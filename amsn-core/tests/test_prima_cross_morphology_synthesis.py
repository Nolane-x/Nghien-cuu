"""Regression tests for the four-morphology PRIMA synthesis."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESEARCH_DIR = REPO_ROOT / "amsn-core" / "research"
if str(RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(RESEARCH_DIR))

import synthesize_prima_cross_morphology as synthesis


class PrimaCrossMorphologySynthesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = synthesis.load_dataset(REPO_ROOT)
        cls.rows = synthesis.build_rows(cls.cases)

    def test_four_independent_holdouts_have_exact_coverage(self) -> None:
        self.assertEqual(
            [case["id"] for case in self.cases],
            ["NMO_162186", "NMO_03524", "NMO_163775", "NMO_107159"],
        )
        for case in self.cases:
            self.assertEqual(case["coverage"], synthesis.EXPECTED_COVERAGE)

    def test_all_shared_hines_checks_are_exact(self) -> None:
        self.assertEqual(sum(case["hines_checks"] for case in self.cases), 1512)
        for case in self.cases:
            self.assertEqual(case["hines_max_abs"], 0.0)
            self.assertEqual(case["hines_max_rel"], 0.0)

    def test_protocol_is_matched_except_for_recorded_mesh_cap(self) -> None:
        signatures = {
            synthesis.protocol_signature(case["protocol"]) for case in self.cases
        }
        self.assertEqual(len(signatures), 1)
        self.assertEqual(
            sorted(case["protocol"]["mesh_max_segment_um"] for case in self.cases),
            [0.125, 0.125, 0.5, 0.5],
        )

    def test_order_112_penalty_is_morphology_dependent(self) -> None:
        rows = [row for row in self.rows if row["basis_order"] == 112]
        ratios = {row["morphology_id"]: row["median_error_ratio_nine_over_seven"] for row in rows}
        self.assertTrue(0.99 <= ratios["NMO_03524"] <= 1.01)
        self.assertGreater(ratios["NMO_162186"], 8.0)
        self.assertGreater(ratios["NMO_163775"], 70.0)
        self.assertGreater(ratios["NMO_107159"], 40.0)

    def test_order_168_is_near_parity_on_three_of_four_holdouts(self) -> None:
        rows = [row for row in self.rows if row["basis_order"] == 168]
        near_parity = [
            row for row in rows
            if 0.99 <= row["median_error_ratio_nine_over_seven"] <= 1.01
        ]
        self.assertEqual(len(near_parity), 3)
        peng = next(row for row in rows if row["morphology_id"] == "NMO_163775")
        self.assertAlmostEqual(peng["median_error_ratio_nine_over_seven"], 14.50136293587607)
        self.assertLess(peng["max_nine_port_nrmse_pct"], 1e-6)

    def test_generated_summary_has_two_rows_per_morphology(self) -> None:
        self.assertEqual(len(self.rows), 8)
        self.assertEqual(
            sum(row["matched_shared_output_pairs"] for row in self.rows),
            3024,
        )
        self.assertEqual(
            sum(row["q25_observations"] for row in self.rows),
            864,
        )

    def test_bad_coverage_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            synthesis.validate_exact_coverage(
                {"models": 35, **{k: v for k, v in synthesis.EXPECTED_COVERAGE.items() if k != "models"}},
                "fixture",
            )


if __name__ == "__main__":
    unittest.main()
