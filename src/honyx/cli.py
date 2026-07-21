from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .contract import ContractError, validate_package
from .scaffold import initialize_package
from .verifier import verify_package


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="honyx", description="Build and verify reproducible analysis packages."
    )
    parser.add_argument("--version", action="version", version="honyx 0.1.0")
    commands = parser.add_subparsers(dest="command", required=True)

    init_parser = commands.add_parser("init", help="create a valid example package")
    init_parser.add_argument("package", nargs="?", default=".")

    validate_parser = commands.add_parser("validate", help="validate a package contract")
    validate_parser.add_argument("package", nargs="?", default=".")
    validate_parser.add_argument("--json", action="store_true", dest="as_json")

    verify_parser = commands.add_parser(
        "verify", help="regenerate declared outputs in an allowlisted workspace"
    )
    verify_parser.add_argument("package", nargs="?", default=".")
    verify_parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        try:
            created = initialize_package(Path(args.package))
        except (OSError, FileExistsError) as exc:
            print(f"honyx init failed: {exc}", file=sys.stderr)
            return 1
        print(f"Created Honyx package with {len(created)} files in {args.package}")
        return 0

    if args.command == "validate":
        issues = validate_package(Path(args.package))
        if args.as_json:
            print(
                json.dumps(
                    {
                        "valid": not issues,
                        "issues": [
                            {"location": issue.location, "message": issue.message}
                            for issue in issues
                        ],
                    },
                    indent=2,
                )
            )
        elif issues:
            print("Package is invalid:", file=sys.stderr)
            for issue in issues:
                print(f"- {issue.render()}", file=sys.stderr)
        else:
            print("Package contract is valid.")
        return 0 if not issues else 1

    if args.command == "verify":
        try:
            result = verify_package(Path(args.package))
        except ContractError as exc:
            print(f"Verification could not start: {exc}", file=sys.stderr)
            return 1
        if args.as_json:
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        else:
            marker = "PASS" if result.passed else "FAIL"
            print(f"[{marker}] {result.verification_id}")
            print(f"Entrypoint exit code: {result.exit_code}")
            for check in result.output_checks:
                check_marker = "PASS" if check.passed else "FAIL"
                print(f"[{check_marker}] {check.path}: {check.detail}")
            print(f"Evidence: {result.report_path}")
            if result.limitations:
                print("Limitations:")
                for limitation in result.limitations:
                    print(f"- {limitation}")
            if not result.passed and result.stderr:
                print("Entrypoint stderr:", file=sys.stderr)
                print(result.stderr.rstrip(), file=sys.stderr)
        return 0 if result.passed else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

