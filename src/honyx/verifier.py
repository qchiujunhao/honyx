from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .contract import ContractError, load_manifest, validate_package


@dataclass
class OutputCheck:
    output_id: str
    path: str
    comparison: str
    passed: bool
    detail: str


@dataclass
class VerificationResult:
    verification_id: str
    status: str
    command: list[str]
    exit_code: int | None
    duration_seconds: float
    workspace: str
    stdout: str
    stderr: str
    output_checks: list[OutputCheck]
    limitations: list[str]
    report_path: str | None = None

    @property
    def passed(self) -> bool:
        return self.status == "passed"

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["passed"] = self.passed
        return value


def verify_package(package_root: Path) -> VerificationResult:
    root = package_root.resolve()
    issues = validate_package(root)
    if issues:
        raise ContractError("; ".join(issue.render() for issue in issues))

    manifest = load_manifest(root)
    run = manifest["run"]
    verification = manifest.get("verification", {})
    verification_id = _verification_id()
    relative_workspace = Path(".honyx") / "runs" / verification_id / "workspace"
    workspace = root / relative_workspace
    workspace.mkdir(parents=True, exist_ok=False)

    for declaration in [*run.get("resources", []), *run["inputs"]]:
        _copy_declared(root, workspace, declaration["path"])

    command = list(run["entrypoint"])
    timeout = verification.get("timeout_seconds", 300)
    environment = os.environ.copy()
    environment.update(
        {
            "HONYX_VERIFICATION": "1",
            "PYTHONHASHSEED": "0",
            "SOURCE_DATE_EPOCH": "0",
        }
    )

    started = time.monotonic()
    exit_code: int | None
    stdout: str
    stderr: str
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            env=environment,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code = None
        stdout = _as_text(exc.stdout)
        stderr = _as_text(exc.stderr) + f"\nverification timed out after {timeout}s"
    except OSError as exc:
        exit_code = None
        stdout = ""
        stderr = f"failed to start entrypoint: {exc}"
    duration = time.monotonic() - started

    checks = [
        _compare_output(root, workspace, output) for output in run["outputs"]
    ]
    passed = exit_code == 0 and all(check.passed for check in checks)
    result = VerificationResult(
        verification_id=verification_id,
        status="passed" if passed else "failed",
        command=command,
        exit_code=exit_code,
        duration_seconds=round(duration, 6),
        workspace=relative_workspace.as_posix(),
        stdout=stdout,
        stderr=stderr,
        output_checks=checks,
        limitations=[
            "The active software environment was reused rather than reconstructed.",
            "Filesystem and network access were not process-sandboxed in contract version 0.1.",
            "Output equivalence does not establish scientific correctness or method conformance.",
        ],
    )
    result.report_path = _write_report(root, result)
    return result


def _copy_declared(root: Path, workspace: Path, relative_path: str) -> None:
    source = root / relative_path
    destination = workspace / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def _compare_output(
    root: Path, workspace: Path, declaration: dict[str, Any]
) -> OutputCheck:
    relative_path = declaration["path"]
    comparison = declaration["comparison"]["type"]
    generated = workspace / relative_path
    reference = root / relative_path
    if not generated.exists():
        return OutputCheck(
            declaration["id"], relative_path, comparison, False, "output was not generated"
        )
    if comparison == "exists":
        return OutputCheck(
            declaration["id"], relative_path, comparison, True, "output exists"
        )
    if not generated.is_file():
        return OutputCheck(
            declaration["id"], relative_path, comparison, False, "output is not a file"
        )
    if comparison == "exact":
        generated_hash = _sha256(generated)
        reference_hash = _sha256(reference)
        passed = generated_hash == reference_hash
        return OutputCheck(
            declaration["id"],
            relative_path,
            comparison,
            passed,
            "SHA-256 values match"
            if passed
            else f"SHA-256 mismatch: generated {generated_hash}, reference {reference_hash}",
        )
    if comparison == "json":
        try:
            generated_value = json.loads(generated.read_text(encoding="utf-8"))
            reference_value = json.loads(reference.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            return OutputCheck(
                declaration["id"],
                relative_path,
                comparison,
                False,
                f"could not compare JSON: {exc}",
            )
        passed = generated_value == reference_value
        return OutputCheck(
            declaration["id"],
            relative_path,
            comparison,
            passed,
            "parsed JSON values match" if passed else "parsed JSON values differ",
        )
    return OutputCheck(
        declaration["id"], relative_path, comparison, False, "unsupported comparison"
    )


def _write_report(root: Path, result: VerificationResult) -> str:
    relative_path = Path(".honyx") / "reports" / f"{result.verification_id}.json"
    report_path = root / relative_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    result.report_path = relative_path.as_posix()
    report_path.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result.report_path


def _verification_id() -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{uuid.uuid4().hex[:8]}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value
