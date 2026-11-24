"""Data-integrity and interpretation guardrails for PRIMA residual localization."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESEARCH_DIR = REPO_ROOT / "amsn-core" / "research"
if str(RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(RESEARCH_DIR))

import analyze_prima_matched_residuals as analysis


class PrimaMatchedResidualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = analysis.load_all_rows(REPO_ROOT)
        cls.output_rows = analysis.build_source_output_rows(cls.rows)

    def test_all_four_holdouts_have_exact_paired_coverage(self) -> None:
        self.assertEqual(len(self.rows), 4 * 2 * 378)
        for morphology_id in ("NMO_162186", "NMO_03524", "NMO_163775", "NMO_107159"):
            for order in (112, 168):
                subset = [
                    row for row in self.rows
                    if row["morphology_id"] == morphology_id and row["basis_order"] == order
                ]
                self.assertEqual(len(subset), 378)

    def test_every_source_output_group_has_complete_factorial_coverage(self) -> None:
        self.assertEqual(len(self.output_rows), 4 * 2 * 3 * 7)
        self.assertTrue(all(row["paired_observations"] == 18 for row in self.output_rows))

    def test_peng_order168_source_and_output_interaction_is_reproduced(self) -> None:
        def get(source: str, port: str):
            return next(
                row for row in self.output_rows
                if row["morphology_id"] == "NMO_163775"
                and row["basis_order"] == 168
                and row["source_name"] == source
                and row["port_role"] == port
            )
        soma_to_soma = get("soma", "soma")
        apical_to_apical = get("apical_q75", "apical_q75")
        self.assertAlmostEqual(
            soma_to_soma["median_error_ratio_nine_over_seven"],
            113.55773944106028,
            places=8,
        )
        self.assertAlmostEqual(
            apical_to_apical["median_error_ratio_nine_over_seven"],
            1.0045970417171743,
            places=8,
        )
        self.assertGreater(
            soma_to_soma["median_error_ratio_nine_over_seven"],
            apical_to_apical["median_error_ratio_nine_over_seven"] * 50,
        )

    def test_peng_large_relative_ratio_is_reported_with_absolute_error(self) -> None:
        subset = [
            row for row in self.rows
            if row["morphology_id"] == "NMO_163775" and row["basis_order"] == 168
        ]
        result = analysis.summarize(subset)
        self.assertAlmostEqual(result["median_error_ratio_nine_over_seven"],
                               14.50136293587607, places=10)
        self.assertAlmostEqual(result["max_nine_port_nrmse_pct"],
                               6.065666321938609e-7, places=14)
        self.assertLess(result["max_nine_port_nrmse_pct"], 1e-6)

    def test_stored_ratio_and_delta_are_recomputed(self) -> None:
        sample = self.rows[0]
        self.assertTrue(analysis.close_enough(
            sample["error_ratio_nine_over_seven"],
            sample["nine_port_nrmse_pct"] / sample["seven_port_nrmse_pct"],
        ))
        self.assertTrue(analysis.close_enough(
            sample["delta_pct_points"],
            sample["nine_port_nrmse_pct"] - sample["seven_port_nrmse_pct"],
        ))

    def test_csv_output_has_stable_research_grain(self) -> None:
        self.assertEqual(set(self.output_rows[0]), set(analysis.OUTPUT_FIELDS))
        self.assertEqual(self.output_rows[0]["paired_observations"], 18)

    def test_bad_quantile_input_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            analysis.nearest_rank([], 0.9)


if __name__ == "__main__":
    unittest.main()
