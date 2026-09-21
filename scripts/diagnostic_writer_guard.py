#!/usr/bin/env python3
"""Fail-closed static contract for the one diagnostic export writer module.

I27/I28 permit only one narrow Linux no-clobber writer shape. The guard does
not prove runtime correctness; it rejects source forms that are broader than
the reviewed contract.
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
READ_FILE_FLAGS = {"os.O_RDONLY", "os.O_CLOEXEC", "os.O_NOFOLLOW"}
DIRECTORY_FLAGS = {
    "os.O_RDONLY", "os.O_DIRECTORY", "os.O_CLOEXEC", "os.O_NOFOLLOW",
}
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


def _is_role(node: ast.AST, role: str) -> bool:
    name = _role_name(node)
    if not name:
        return False
    accepted = {
        role,
        f"{role}_path",
        f"{role}_name",
        f"{role}_dir",
        f"{role}_dir_fd",
    }
    return name in accepted or any(name.endswith("_" + value) for value in accepted)


def _keyword_name(call: ast.Call, keyword_name: str) -> str | None:
    for keyword in call.keywords:
        if keyword.arg == keyword_name and isinstance(keyword.value, ast.Name):
            return keyword.value.id
    return None


def _classify_directory_open(
    call: ast.Call,
    aliases: dict[str, str],
) -> tuple[bool, str | None]:
    if len(call.args) < 2:
        return False, "Directory-os.open braucht Pfad und statische Flags"
    if any(keyword.arg == "dir_fd" for keyword in call.keywords):
        return False, "Directory-os.open darf nicht selbst relativ zu dir_fd erfolgen"
    if not _is_role(call.args[0], "target"):
        return False, "Directory-os.open ist nur für target_dir zulässig"
    flags, static = _flag_names(call.args[1], aliases)
    if not static or not flags:
        return False, "Directory-os.open-Flags müssen vollständig statisch sein"
    if flags != DIRECTORY_FLAGS:
        return False, (
            "target_dir_fd braucht exakt O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW"
        )
    return True, None


def _directory_fds(tree: ast.AST, aliases: dict[str, str]) -> set[str]:
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
        flags, static = _flag_names(value.args[1], aliases) if len(value.args) >= 2 else (set(), False)
        if "os.O_DIRECTORY" not in flags:
            continue
        allowed, _ = _classify_directory_open(value, aliases)
        if allowed and _is_role(target, "target"):
            names.add(target.id)
    return names


def _classify_partial_open(
    call: ast.Call,
    aliases: dict[str, str],
    safe_dir_fds: set[str],
) -> tuple[bool, str | None]:
    if len(call.args) < 2:
        return False, "Partial-os.open braucht Pfad und statische Flags"
    if not _is_role(call.args[0], "partial"):
        return False, "schreibendes os.open ist nur für partial_name/partial_path zulässig"

    flags, static = _flag_names(call.args[1], aliases)
    if not static or not flags:
        return False, "os.open-Flags müssen vollständig statisch als os.O_* belegbar sein"
    if flags & DANGEROUS_OPEN_FLAGS:
        bad = ", ".join(sorted(flags & DANGEROUS_OPEN_FLAGS))
        return False, f"os.open enthält verbotene Flags: {bad}"
    unknown = flags - CREATE_OPEN_FLAGS
    if unknown:
        return False, f"unerlaubte Create-Flags: {', '.join(sorted(unknown))}"
    if not CREATE_REQUIRED <= flags:
        return False, "schreibendes os.open braucht O_CREAT|O_EXCL"
    access = flags & WRITE_ACCESS
    if len(access) != 1:
        return False, "schreibendes os.open braucht genau O_WRONLY oder O_RDWR"

    dir_fd = _keyword_name(call, "dir_fd")
    if dir_fd is None or dir_fd not in safe_dir_fds:
        return False, "Partial-os.open braucht den nachweislich sicheren target_dir_fd"
    return True, None


def _exclusive_writer_fds(
    tree: ast.AST,
    aliases: dict[str, str],
    safe_dir_fds: set[str],
) -> set[str]:
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
        allowed, _ = _classify_partial_open(value, aliases, safe_dir_fds)
        if allowed and _is_role(target, "partial"):
            names.add(target.id)
    return names


def analyze_writer_source(
    source: str,
    *,
    filename: str = WRITER_RELATIVE,
) -> tuple[str, ...]:
    tree = ast.parse(source, filename=filename)
    aliases = _import_aliases(tree)
    safe_dir_fds = _directory_fds(tree, aliases)
    safe_writer_fds = _exclusive_writer_fds(tree, aliases, safe_dir_fds)
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif node.module:
                modules = [node.module]
            for module in modules:
                if any(
                    module == prefix or module.startswith(prefix + ".")
                    for prefix in BLOCKED_IMPORT_PREFIXES
                ):
                    violations.append(
                        f"{filename}:{getattr(node, 'lineno', '?')}: "
                        f"Import im Writer verboten: {module}"
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
                f"{filename}:{line}: pathlib-/Objekt-Schreib-API verboten: "
                f".{node.func.attr}()"
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
            flags, static = _flag_names(node.args[1], aliases) if len(node.args) >= 2 else (set(), False)
            if static and "os.O_DIRECTORY" in flags:
                allowed, reason = _classify_directory_open(node, aliases)
            elif static and not (flags & (CREATE_REQUIRED | WRITE_ACCESS)):
                unknown = flags - READ_FILE_FLAGS
                allowed = not unknown and not any(keyword.arg == "dir_fd" for keyword in node.keywords)
                reason = None if allowed else "freies read-only os.open ist im Writer nicht zulässig"
            else:
                allowed, reason = _classify_partial_open(node, aliases, safe_dir_fds)
            if not allowed:
                violations.append(f"{filename}:{line}: {reason}")
            continue

        if name == "os.write":
            fd = node.args[0] if node.args else None
            if not isinstance(fd, ast.Name) or fd.id not in safe_writer_fds:
                violations.append(
                    f"{filename}:{line}: os.write nur auf exklusiv erzeugtem Partial-FD zulässig"
                )
            continue

        if name == "os.link":
            if len(node.args) < 2:
                violations.append(f"{filename}:{line}: os.link braucht Partial- und Finalnamen")
                continue
            if not _is_role(node.args[0], "partial"):
                violations.append(
                    f"{filename}:{line}: os.link-Quelle muss partial_name/partial_path sein"
                )
            if not _is_role(node.args[1], "final"):
                violations.append(
                    f"{filename}:{line}: os.link-Ziel muss final_name/final_path sein"
                )
            src_fd = _keyword_name(node, "src_dir_fd")
            dst_fd = _keyword_name(node, "dst_dir_fd")
            if (
                src_fd is None
                or dst_fd is None
                or src_fd != dst_fd
                or src_fd not in safe_dir_fds
            ):
                violations.append(
                    f"{filename}:{line}: os.link muss denselben sicheren target_dir_fd "
                    "für Quelle und Ziel verwenden"
                )
            follow = None
            for keyword in node.keywords:
                if keyword.arg == "follow_symlinks" and isinstance(keyword.value, ast.Constant):
                    follow = keyword.value.value
            if follow is not False:
                violations.append(
                    f"{filename}:{line}: os.link muss follow_symlinks=False setzen"
                )
            continue

        if name == "os.unlink":
            target = node.args[0] if node.args else None
            if target is None or not _is_role(target, "partial"):
                violations.append(
                    f"{filename}:{line}: os.unlink ist nur für partial_name/partial_path zulässig"
                )
            dir_fd = _keyword_name(node, "dir_fd")
            if dir_fd is None or dir_fd not in safe_dir_fds:
                violations.append(
                    f"{filename}:{line}: os.unlink braucht den sicheren target_dir_fd"
                )
            continue

    return tuple(violations)


def main() -> int:
    print(
        "diagnostic_writer_guard ist ein statischer Library-Gate; "
        "Ausführung erfolgt über read_only_guard/tests."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
