from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


MANIFEST_NAME = "honyx.json"
SCHEMA_VERSION = "0.1"
COMPARISON_TYPES = {"exists", "exact", "json"}


@dataclass(frozen=True)
class ValidationIssue:
    location: str
    message: str

    def render(self) -> str:
        return f"{self.location}: {self.message}"


class ContractError(ValueError):
    pass


def load_manifest(package_root: Path) -> dict[str, Any]:
    manifest_path = package_root / MANIFEST_NAME
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"missing {MANIFEST_NAME}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(
            f"invalid JSON in {MANIFEST_NAME} at line {exc.lineno}, column {exc.colno}"
        ) from exc
    if not isinstance(value, dict):
        raise ContractError(f"{MANIFEST_NAME} must contain a JSON object")
    return value


def validate_package(package_root: Path) -> list[ValidationIssue]:
    root = package_root.resolve()
    issues: list[ValidationIssue] = []
    if not root.is_dir():
        return [ValidationIssue("package", "package root is not a directory")]

    try:
        manifest = load_manifest(root)
    except ContractError as exc:
        return [ValidationIssue("honyx.json", str(exc))]

    if manifest.get("schema_version") != SCHEMA_VERSION:
        issues.append(
            ValidationIssue(
                "schema_version", f"must equal {SCHEMA_VERSION!r}"
            )
        )

    method = _object(manifest, "method", issues)
    for field in ("id", "version", "title", "question", "document"):
        _nonempty_string(method, field, f"method.{field}", issues)

    document = method.get("document")
    if isinstance(document, str) and _safe_relative_path(
        document, "method.document", issues
    ):
        if not _path_stays_in_package(root, document, "method.document", issues):
            pass
        elif not (root / document).is_file():
            issues.append(
                ValidationIssue("method.document", "declared document does not exist")
            )

    run = _object(manifest, "run", issues)
    entrypoint = run.get("entrypoint")
    if not (
        isinstance(entrypoint, list)
        and entrypoint
        and all(isinstance(part, str) and part for part in entrypoint)
    ):
        issues.append(
            ValidationIssue(
                "run.entrypoint", "must be a non-empty array of non-empty strings"
            )
        )

    inputs = _declarations(run, "inputs", required=True, issues=issues)
    resources = _declarations(run, "resources", required=False, issues=issues)
    outputs = _declarations(run, "outputs", required=True, issues=issues)

    readable_paths: set[str] = set()
    for group_name, declarations in (("inputs", inputs), ("resources", resources)):
        for index, declaration in enumerate(declarations):
            location = f"run.{group_name}[{index}]"
            path = declaration.get("path")
            if isinstance(path, str) and _safe_relative_path(
                path, f"{location}.path", issues
            ):
                readable_paths.add(path)
                if not _path_stays_in_package(
                    root, path, f"{location}.path", issues
                ):
                    continue
                if not (root / path).exists():
                    issues.append(
                        ValidationIssue(f"{location}.path", "declared path does not exist")
                    )

    output_paths: set[str] = set()
    for index, declaration in enumerate(outputs):
        location = f"run.outputs[{index}]"
        path = declaration.get("path")
        if isinstance(path, str) and _safe_relative_path(
            path, f"{location}.path", issues
        ):
            output_paths.add(path)
            if not _path_stays_in_package(root, path, f"{location}.path", issues):
                continue
            comparison = declaration.get("comparison")
            if not isinstance(comparison, dict):
                issues.append(
                    ValidationIssue(
                        f"{location}.comparison", "must be an object"
                    )
                )
            else:
                comparison_type = comparison.get("type")
                if comparison_type not in COMPARISON_TYPES:
                    issues.append(
                        ValidationIssue(
                            f"{location}.comparison.type",
                            "must be one of " + ", ".join(sorted(COMPARISON_TYPES)),
                        )
                    )
                elif comparison_type != "exists" and not (root / path).is_file():
                    issues.append(
                        ValidationIssue(
                            f"{location}.path",
                            "reference output must exist for this comparison",
                        )
                    )

    for output in sorted(output_paths):
        for readable in sorted(readable_paths):
            if _paths_overlap(output, readable):
                issues.append(
                    ValidationIssue(
                        "run.outputs",
                        f"output {output!r} overlaps declared input/resource {readable!r}",
                    )
                )

    verification = manifest.get("verification", {})
    if not isinstance(verification, dict):
        issues.append(ValidationIssue("verification", "must be an object"))
    else:
        timeout = verification.get("timeout_seconds", 300)
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
            issues.append(
                ValidationIssue(
                    "verification.timeout_seconds", "must be a positive integer"
                )
            )

    return issues


def _object(
    parent: dict[str, Any], key: str, issues: list[ValidationIssue]
) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        issues.append(ValidationIssue(key, "must be an object"))
        return {}
    return value


def _nonempty_string(
    parent: dict[str, Any], key: str, location: str, issues: list[ValidationIssue]
) -> None:
    value = parent.get(key)
    if not isinstance(value, str) or not value.strip():
        issues.append(ValidationIssue(location, "must be a non-empty string"))


def _declarations(
    run: dict[str, Any],
    key: str,
    *,
    required: bool,
    issues: list[ValidationIssue],
) -> list[dict[str, Any]]:
    value = run.get(key, [] if not required else None)
    if not isinstance(value, list) or (required and not value):
        qualifier = "a non-empty array" if required else "an array"
        issues.append(ValidationIssue(f"run.{key}", f"must be {qualifier}"))
        return []

    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, declaration in enumerate(value):
        location = f"run.{key}[{index}]"
        if not isinstance(declaration, dict):
            issues.append(ValidationIssue(location, "must be an object"))
            continue
        result.append(declaration)
        for field in ("path", "role"):
            _nonempty_string(declaration, field, f"{location}.{field}", issues)
        if key != "resources":
            _nonempty_string(declaration, "id", f"{location}.id", issues)
            identifier = declaration.get("id")
            if isinstance(identifier, str):
                if identifier in seen_ids:
                    issues.append(
                        ValidationIssue(f"{location}.id", "must be unique in its group")
                    )
                seen_ids.add(identifier)
    return result


def _safe_relative_path(
    raw_path: str, location: str, issues: list[ValidationIssue]
) -> bool:
    path = PurePosixPath(raw_path)
    if (
        not raw_path
        or "\\" in raw_path
        or path.is_absolute()
        or ".." in path.parts
        or "." == raw_path
    ):
        issues.append(
            ValidationIssue(location, "must be a safe package-relative path")
        )
        return False
    return True


def _path_stays_in_package(
    root: Path, raw_path: str, location: str, issues: list[ValidationIssue]
) -> bool:
    candidate = root / raw_path
    current = root
    for part in PurePosixPath(raw_path).parts:
        current = current / part
        if current.is_symlink():
            issues.append(
                ValidationIssue(location, "must not contain symbolic links")
            )
            return False
    try:
        candidate.resolve(strict=False).relative_to(root)
    except ValueError:
        issues.append(ValidationIssue(location, "resolves outside the package root"))
        return False
    return True


def _paths_overlap(left: str, right: str) -> bool:
    left_parts = PurePosixPath(left).parts
    right_parts = PurePosixPath(right).parts
    shared = min(len(left_parts), len(right_parts))
    return left_parts[:shared] == right_parts[:shared]
