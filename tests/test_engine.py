import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from minimize import ddmin

from classify_mismatches import classify
from analyze_diagnostics import analyze


class TestMismatchClassification(unittest.TestCase):

    def test_identical_results(self):
        reference = {
            "file": {"id": "file", "success": True, "attributes": 32}
        }

        self.assertEqual(classify(reference, reference), [])

    def test_error_code_mismatch(self):
        reference = {
            "file": {"id": "file", "success": False, "error_code": 2}
        }

        target = {
            "file": {"id": "file", "success": False, "error_code": 3}
        }

        result = classify(reference, target)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["category"], "ERROR_CODE_MISMATCH")

    def test_success_failure_mismatch(self):
        reference = {
            "file": {"id": "file", "success": True, "attributes": 32}
        }

        target = {
            "file": {"id": "file", "success": False, "error_code": 5}
        }

        result = classify(reference, target)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["category"],
            "SUCCESS_FAILURE_MISMATCH",
        )

    def test_missing_case(self):
        reference = {
            "file": {"id": "file", "success": True, "attributes": 32}
        }

        result = classify(reference, {})

        self.assertEqual(result[0]["category"], "MISSING_TEST_CASE")


class TestDiagnosticAnalysis(unittest.TestCase):

    def test_consistent_paths(self):
        results = [
            {
                "source_case": "file",
                "variant": "absolute_path",
                "success": True,
                "attributes": 32,
            },
            {
                "source_case": "file",
                "variant": "relative_path",
                "success": True,
                "attributes": 32,
            },
        ]

        findings = analyze(results)

        self.assertTrue(findings[0]["consistent_behavior"])
        self.assertFalse(findings[0]["path_representation_sensitive"])

    def test_inconsistent_paths(self):
        results = [
            {
                "source_case": "file",
                "variant": "absolute_path",
                "success": True,
                "attributes": 32,
            },
            {
                "source_case": "file",
                "variant": "relative_path",
                "success": False,
                "error_code": 3,
            },
        ]

        findings = analyze(results)

        self.assertFalse(findings[0]["consistent_behavior"])
        self.assertTrue(findings[0]["path_representation_sensitive"])


class TestMinimization(unittest.TestCase):

    def test_minimizes_trigger(self):
        result = ddmin(
            "folder/nested/invalid<>.txt",
            lambda value: "<>" in value,
        )

        self.assertEqual(result, "<>")

    def test_rejects_non_reproducing_input(self):
        with self.assertRaises(ValueError):
            ddmin("valid.txt", lambda value: "<>" in value)

    def test_preserves_failure(self):
        predicate = lambda value: "ABC" in value

        result = ddmin("123ABC456", predicate)

        self.assertTrue(predicate(result))
        self.assertEqual(result, "ABC")



if __name__ == "__main__":
    unittest.main()