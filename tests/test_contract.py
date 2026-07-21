from __future__ import annotations

import json
import os
import shutil
import sys
import unittest
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from honyx.contract import validate_package
from honyx.scaffold import initialize_package
from honyx.verifier import verify_package


class HonyxContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.work = PROJECT_ROOT / "build" / f"test-{uuid.uuid4().hex}"
        self.work.mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.work, ignore_errors=True)

    def copy_example(self) -> Path:
        package = self.work / "package"
        shutil.copytree(PROJECT_ROOT / "examples" / "group-summary", package)
        return package

    def test_reference_package_is_valid(self) -> None:
        issues = validate_package(PROJECT_ROOT / "examples" / "group-summary")
        self.assertEqual([], issues)

    def test_real_data_package_is_valid_and_regenerates(self) -> None:
        package = PROJECT_ROOT / "examples" / "iris-permutation-test"
        self.assertEqual([], validate_package(package))
        result = verify_package(package)
        self.assertTrue(result.passed)
        output = package / result.workspace / "results" / "analysis.json"
        values = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(150, values["analysis"]["observation_count"])
        self.assertEqual(0, values["permutation_test"]["exceedances"])
        self.assertEqual(1936, values["permutation_test"]["random_seed"])

    def test_clean_verification_regenerates_reference_output(self) -> None:
        package = self.copy_example()
        result = verify_package(package)
        self.assertTrue(result.passed)
        self.assertEqual("passed", result.status)
        self.assertEqual(1, len(result.output_checks))
        self.assertTrue(result.output_checks[0].passed)
        self.assertTrue((package / result.workspace / "results" / "summary.json").is_file())
        self.assertTrue((package / result.report_path).is_file())

    def test_reference_output_mismatch_fails_verification(self) -> None:
        package = self.copy_example()
        reference = package / "results" / "summary.json"
        value = json.loads(reference.read_text(encoding="utf-8"))
        value["total_observations"] = 999
        reference.write_text(json.dumps(value), encoding="utf-8")
        result = verify_package(package)
        self.assertFalse(result.passed)
        self.assertEqual("parsed JSON values differ", result.output_checks[0].detail)

    def test_parent_traversal_is_rejected(self) -> None:
        package = self.copy_example()
        manifest_path = package / "honyx.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["run"]["inputs"][0]["path"] = "../measurements.csv"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        issues = validate_package(package)
        self.assertTrue(any("safe package-relative" in issue.message for issue in issues))

    def test_output_cannot_overlap_input(self) -> None:
        package = self.copy_example()
        manifest_path = package / "honyx.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["run"]["outputs"][0]["path"] = "inputs/measurements.csv"
        manifest["run"]["outputs"][0]["comparison"] = {"type": "exact"}
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        issues = validate_package(package)
        self.assertTrue(any("overlaps" in issue.message for issue in issues))

    def test_declared_symlink_is_rejected(self) -> None:
        package = self.copy_example()
        outside = self.work / "outside.csv"
        outside.write_text("group,value\ncontrol,1\n", encoding="utf-8")
        input_path = package / "inputs" / "measurements.csv"
        input_path.unlink()
        os.symlink(outside, input_path)
        issues = validate_package(package)
        self.assertTrue(any("symbolic links" in issue.message for issue in issues))

    def test_init_creates_a_valid_runnable_package(self) -> None:
        package = self.work / "initialized"
        created = initialize_package(package)
        self.assertGreaterEqual(len(created), 6)
        self.assertEqual([], validate_package(package))
        self.assertTrue(verify_package(package).passed)


if __name__ == "__main__":
    unittest.main()
