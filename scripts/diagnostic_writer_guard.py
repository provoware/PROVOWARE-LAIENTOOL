#!/usr/bin/env python3
"""Fail-closed static contract for the one diagnostic export writer module.

I27 does not implement a writer. It defines the exact low-level primitives a
future writer may use and rejects ambiguous/dynamic write paths.
"""

from __future__ import annotations

import ast

WRITER_RELATIVE = "src/provoware_laientool/diagnostic_export.py"

BLOCKED_IMPORT_PREFIXES = (
    "socket", "urllib", "http", "ftplib", "smtplib", "requests", "httpx",
    "subprocess", "tempfile", "ctypes", "mmap", "shutil", "io", "gzip",
    "bz2", "lzma", "zipfile", "tarfile",
)

FORBIDDEN_CALLS = {
    "os.rename", "os.replace", "os.remove", "os.rmdir", "os.removedirs",
    "os.mkdir", "os.makedirs", "os.chmod", "os.chown", "os.lchown",
    "os.symlink", "os.truncate", "os.ftruncate", "os.mknod", "os.mkfifo",
    "os.creat", "os.pwrite", "os.writev", "os.sendfile",
    "os.copy_file_range", "os.splice", "os.fdopen", "os.system", "os.popen",
    "shutil.copy", "shutil.copy2", "shutil.copyfile", "shutil.copytree",
    "shutil.move", "shutil.rmtree", "eval", "exec", "compile", "__import__",
    "builtins.eval", "builtins.exec", "builtins.compile", "builtins.__import__",
}

FORBIDDEN_ATTRS = {
    "write_text", "write_bytes", "rename", "replace", "mkdir", "touch",
    "chmod", "symlink_to", "hardlink_to", "link_to",
}

WRITE_MODE_MARKERS = {"w", "a", "x", "+"}
READ_OPEN_FLAGS = {"os.O_RDONLY", "os.O_CLOEXEC", "os.O_NOFOLLOW", "os.O_DIRECTORY"}
CREATE_OPEN_FLAGS = {
    "os.O_CREAT", "os.O_EXCL", "os.O_WRONLY", "os.O_RDWR",
    "os.O_CLOEXEC", "os.O_NOFOLLOW",
}
CREATE_REQUIRED = {"os.O_CREAT", "os.O_EXCL"}
WRITE_ACCESS = {"os.O_WRONLY", "os.O_RDWR"}
DANGEROUS_OPEN_FLAGS = {"os.O_TRUNC", "os.O_APPEND", "os.O_TMPFILE"}


def _import_aliases(tree: ast.AST) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".", 1)[0]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name != "*":
                    aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return aliases


def _qualified_name(node: ast.AST, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value, aliases)
        if parent:
            return f"{parent}.{node.attr}"
    return None


def _flag_names(node: ast.AST, aliases: dict[str, str]) -> tuple[set[str], bool]:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left, left_static = _flag_names(node.left, aliases)
        right, right_static = _flag_names(node.right, aliases)
        return left | right, left_static and right_static
    name = _qualified_name(node, aliases)
    if name and name.startswith("os.O_"):
        return {name}, True
    return set(), False


def _role_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_role_path(node: ast.AST, role: str) -> bool:
    name = _role_name(node)
    return bool(name and (name == f"{role}_path" or name.endswith(f"_{role}_path")))


def _classify_os_open(call: ast.Call, aliases: dict[str, str]) -> tuple[str, str | None]:
    if len(call.args) < 2:
        return "invalid", "os.open braucht statisch prüfbare Pfad- und Flag-Argumente"
    if any(keyword.arg == "dir_fd" for keyword in call.keywords):
        return "invalid", "os.open mit dir_fd ist im Writer verboten"

    flags, static = _flag_names(call.args[1], aliases)
    if not static or not flags:
        return "invalid", "os.open-Flags müssen vollständig statisch als os.O_* belegbar sein"

    if flags & DANGEROUS_OPEN_FLAGS:
        bad = ", ".join(sorted(flags & DANGEROUS_OPEN_FLAGS))
        return "invalid", f"os.open enthält verbotene Flags: {bad}"

    write_intent = bool(flags & (CREATE_REQUIRED | WRITE_ACCESS))
    if not write_intent:
        unknown = flags - READ_OPEN_FLAGS
        if unknown:
            return "invalid", f"unbekannte/unerlaubte Read-Flags: {', '.join(sorted(unknown))}"
        return "read", None

    unknown = flags - CREATE_OPEN_FLAGS
    if unknown:
        return "invalid", f"unerlaubte Create-Flags: {', '.join(sorted(unknown))}"
    if not CREATE_REQUIRED <= flags:
        return "invalid", "schreibendes os.open braucht O_CREAT|O_EXCL"
    access = flags & WRITE_ACCESS
    if len(access) != 1:
        return "invalid", "schreibendes os.open braucht genau O_WRONLY oder O_RDWR"
    if not _is_role_path(call.args[0], "partial"):
        return "invalid", "schreibendes os.open ist nur für expliziten partial_path zulässig"
    return "exclusive-write", None


def _exclusive_writer_fds(tree: ast.AST, aliases: dict[str, str]) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        target: ast.AST | None = None
        value: ast.AST | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        if not isinstance(target, ast.Name) or not isinstance(value, ast.Call):
            continue
        if _qualified_name(value.func, aliases) != "os.open":
            continue
        kind, _ = _classify_os_open(value, aliases)
        if kind == "exclusive-write":
            names.add(target.id)
    return names


def analyze_writer_source(source: str, *, filename: str = WRITER_RELATIVE) -> tuple[str, ...]:
    tree = ast.parse(source, filename=filename)
    aliases = _import_aliases(tree)
    safe_fds = _exclusive_writer_fds(tree, aliases)
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif node.module:
                modules = [node.module]
            for module in modules:
                if any(module == prefix or module.startswith(prefix + ".")
                       for prefix in BLOCKED_IMPORT_PREFIXES):
                    violations.append(
                        f"{filename}:{getattr(node, 'lineno', '?')}: Import im Writer verboten: {module}"
                    )

        if not isinstance(node, ast.Call):
            continue
        name = _qualified_name(node.func, aliases)
        line = getattr(node, "lineno", "?")

        if name in FORBIDDEN_CALLS:
            violations.append(f"{filename}:{line}: Writer-/Escape-API verboten: {name}")
            continue

        if isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_ATTRS:
            violations.append(
                f"{filename}:{line}: pathlib-/Objekt-Schreib-API verboten: .{node.func.attr}()"
            )
            continue

        if name in {"open", "builtins.open"} or (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "open"
            and name != "os.open"
        ):
            mode_node = node.args[1] if len(node.args) >= 2 else None
            for keyword in node.keywords:
                if keyword.arg == "mode":
                    mode_node = keyword.value
            if mode_node is None:
                continue
            if not isinstance(mode_node, ast.Constant) or not isinstance(mode_node.value, str):
                violations.append(f"{filename}:{line}: dynamischer open()-Modus verboten")
            elif any(marker in mode_node.value for marker in WRITE_MODE_MARKERS):
                violations.append(
                    f"{filename}:{line}: builtins/path open mit Schreibmodus verboten"
                )
            continue

        if name == "os.open":
            kind, reason = _classify_os_open(node, aliases)
            if kind == "invalid":
                violations.append(f"{filename}:{line}: {reason}")
            continue

        if name == "os.write":
            fd = node.args[0] if node.args else None
            if not isinstance(fd, ast.Name) or fd.id not in safe_fds:
                violations.append(
                    f"{filename}:{line}: os.write nur auf exklusiv erzeugtem Partial-FD zulässig"
                )
            continue

        if name == "os.link":
            if len(node.args) < 2:
                violations.append(f"{filename}:{line}: os.link braucht Partial- und Finalpfad")
                continue
            if not _is_role_path(node.args[0], "partial"):
                violations.append(
                    f"{filename}:{line}: os.link-Quelle muss expliziter partial_path sein"
                )
            if not _is_role_path(node.args[1], "final"):
                violations.append(
                    f"{filename}:{line}: os.link-Ziel muss expliziter final_path sein"
                )
            follow = None
            for keyword in node.keywords:
                if keyword.arg == "follow_symlinks" and isinstance(keyword.value, ast.Constant):
                    follow = keyword.value.value
                if keyword.arg in {"src_dir_fd", "dst_dir_fd"}:
                    violations.append(
                        f"{filename}:{line}: os.link mit *_dir_fd ist im Writer verboten"
                    )
            if follow is not False:
                violations.append(
                    f"{filename}:{line}: os.link muss follow_symlinks=False setzen"
                )
            continue

        if name == "os.unlink":
            target = node.args[0] if node.args else None
            if target is None or not _is_role_path(target, "partial"):
                violations.append(
                    f"{filename}:{line}: os.unlink ist nur für expliziten partial_path zulässig"
                )
            if any(keyword.arg == "dir_fd" for keyword in node.keywords):
                violations.append(
                    f"{filename}:{line}: os.unlink mit dir_fd ist im Writer verboten"
                )
            continue

    return tuple(violations)


def main() -> int:
    print("diagnostic_writer_guard ist ein statischer Library-Gate; Ausführung erfolgt über read_only_guard/tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
