"""Fail-closed policy for the pinned Linux x86_64 PySide6 wheelhouse."""

from __future__ import annotations

from pathlib import Path

EXPECTED_VERSION = "6.11.2"
EXPECTED_DISTRIBUTIONS = {
    "pyside6",
    "pyside6_addons",
    "pyside6_essentials",
    "shiboken6",
}


def normalize_distribution(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(".", "_")


def parse_wheel_filename(filename: str) -> tuple[str, str, str]:
    name = Path(filename).name
    if not name.endswith(".whl"):
        raise ValueError(f"Keine Wheel-Datei: {name}")
    parts = name[:-4].split("-")
    if len(parts) < 5:
        raise ValueError(f"Wheel-Dateiname unvollständig: {name}")
    distribution = normalize_distribution(parts[0])
    version = parts[1]
    platform_tag = parts[-1].lower()
    return distribution, version, platform_tag


def validate_wheel_names(names: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    failures: list[str] = []
    parsed: dict[str, tuple[str, str]] = {}

    for name in sorted(names):
        try:
            distribution, version, platform_tag = parse_wheel_filename(name)
        except ValueError as exc:
            failures.append(str(exc))
            continue

        if distribution in parsed:
            failures.append(f"Doppelte Wheel-Distribution: {distribution}")
            continue
        parsed[distribution] = (version, platform_tag)

        if version != EXPECTED_VERSION:
            failures.append(
                f"Wheel-Version falsch für {distribution}: {version}; erwartet {EXPECTED_VERSION}"
            )
        if "manylinux" not in platform_tag or "x86_64" not in platform_tag:
            failures.append(
                f"Wheel-Plattform nicht Linux-x86_64 für {distribution}: {platform_tag}"
            )

    present = set(parsed)
    missing = sorted(EXPECTED_DISTRIBUTIONS - present)
    unexpected = sorted(present - EXPECTED_DISTRIBUTIONS)
    if missing:
        failures.append(f"Wheelhouse unvollständig; fehlt: {missing}")
    if unexpected:
        failures.append(f"Unerwartete Wheels im Wheelhouse: {unexpected}")
    if len(names) != len(EXPECTED_DISTRIBUTIONS):
        failures.append(
            f"Wheelhouse muss exakt {len(EXPECTED_DISTRIBUTIONS)} Wheels enthalten; gefunden: {len(names)}"
        )

    return tuple(failures)


def validate_wheelhouse_dir(path: Path) -> tuple[tuple[Path, ...], tuple[str, ...]]:
    if not path.is_dir():
        return (), (f"Wheelhouse fehlt: {path}",)
    wheels = tuple(sorted(path.glob("*.whl"), key=lambda item: item.name))
    return wheels, validate_wheel_names(tuple(item.name for item in wheels))
