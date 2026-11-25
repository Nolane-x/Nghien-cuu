import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

MODULE_PATH = Path(__file__).resolve().parents[1] / "research" / "analyze_prima_q25_output_observer_fixed_vs_enriched_basis.py"
SPEC = importlib.util.spec_from_file_location("q25_output_observer", MODULE_PATH)
observer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(observer)


def synthetic_case_rows():
    rows = []
    morphologies = tuple(observer.runner_name for observer.runner_name in (
        "NMO_03524_JacobsControl",
        "NMO_107159_Tamas_human_pyramidal_Control",
        "NMO_162186_AllenL23",
        "NMO_163775_Peng_mouse_Control",
    ))
    layouts = ("seven", "eight_basal_q25", "eight_apical_q25", "nine_both_q25")
    for morphology in morphologies:
        for scenario in range(9):
            for role in ("basal_q25", "apical_q25"):
                for source in ("soma", "basal_q75", "apical_q75"):
                    for pulse in (2.0, 10.0):
                        for window in (20.0, 40.0):
                            for layout in layouts:
                                retained = (
                                    (role == "basal_q25" and layout in ("eight_basal_q25", "nine_both_q25"))
                                    or (role == "apical_q25" and layout in ("eight_apical_q25", "nine_both_q25"))
                                )
                                row = {
                                    "morphology": morphology,
                                    "neuromorpho_id": morphology.split("_")[0],
                                    "parameter_scenario": f"scenario_{scenario}",
                                    "basis_order": 168,
                                    "layout_id": layout,
                                    "q25_role": role,
                                    "output_swc_id": "123" if role == "basal_q25" else "456",
                                    "q25_is_retained_port": retained,
                                    "source_name": source,
                                    "pulse_width_ms": pulse,
                                    "window_ms": window,
                                }
                                factor = {
                                    "seven": 1.0,
                                    "eight_basal_q25": 0.8,
                                    "eight_apical_q25": 0.9,
                                    "nine_both_q25": 0.5,
                                }[layout]
                                for metric_name, field in observer.METRICS.items():
                                    row[field] = 10.0 * factor
                                rows.append(row)
    return rows


class TestQ25OutputObserver(unittest.TestCase):
    def test_case_coverage_contract(self):
        rows = synthetic_case_rows()
        self.assertEqual(len(rows), observer.EXPECTED_CASE_ROWS)
        comparisons = observer.build_comparison_rows(rows)
        self.assertEqual(len(comparisons), observer.EXPECTED_COMPARISON_ROWS)

    def test_q25_readout_paired_ratios_separate_retained_from_observer_only(self):
        rows = synthetic_case_rows()
        comparisons = observer.build_comparison_rows(rows)
        sample = next(
            row for row in comparisons
            if row["morphology"] == "NMO_03524_JacobsControl"
            and row["q25_role"] == "basal_q25"
            and row["candidate_layout"] == "eight_apical_q25"
        )
        self.assertFalse(sample["candidate_q25_is_retained_port"])
        self.assertAlmostEqual(
            sample["candidate_over_seven_perturbation_transient_nrmse_pct_ratio"],
            0.9,
        )
        basal_case = next(
            row for row in comparisons
            if row["q25_role"] == "basal_q25"
            and row["candidate_layout"] == "eight_basal_q25"
        )
        self.assertTrue(basal_case["candidate_q25_is_retained_port"])

    def test_summary_group_row_counts_are_exact(self):
        comparisons = observer.build_comparison_rows(synthetic_case_rows())
        source_rows, morphology_rows = observer.build_summaries(comparisons)
        self.assertEqual(len(source_rows), observer.EXPECTED_SOURCE_SUMMARY_ROWS)
        self.assertEqual(len(morphology_rows), observer.EXPECTED_MORPHOLOGY_SUMMARY_ROWS)
        self.assertTrue(all(row["scenario_count"] == 9 for row in source_rows))
        self.assertTrue(all(row["paired_source_pulse_scenario_count"] == 54 for row in morphology_rows))

    def test_comparison_detects_a_retained_q25_output(self):
        rows = synthetic_case_rows()
        comparisons = observer.build_comparison_rows(rows)
        basal = next(
            row for row in comparisons
            if row["q25_role"] == "basal_q25"
            and row["candidate_layout"] == "eight_basal_q25"
        )
        apical = next(
            row for row in comparisons
            if row["q25_role"] == "basal_q25"
            and row["candidate_layout"] == "eight_apical_q25"
        )
        both = next(
            row for row in comparisons
            if row["q25_role"] == "basal_q25"
            and row["candidate_layout"] == "nine_both_q25"
        )
        self.assertTrue(basal["candidate_q25_is_retained_port"])
        self.assertFalse(apical["candidate_q25_is_retained_port"])
        self.assertTrue(both["candidate_q25_is_retained_port"])

    def test_custom_output_basis_projection_is_correct(self):
        model = SimpleNamespace(
            order=2,
            conductance_matrix_s=np.diag([2.0, 4.0]),
            capacitance_matrix_f=np.diag([1.0, 2.0]),
        )
        shifts = np.asarray([0.0, 1.0])
        rhs = np.asarray([[2.0], [4.0]])
        output_basis = np.asarray([[1.0, 0.0], [0.0, 1.0]])
        response = observer.solve_reduced_with_output_basis(
            model, shifts, rhs, output_basis, chunk_size=1
        )
        expected = np.asarray([[[1.0], [1.0]], [[2.0 / 3.0], [2.0 / 3.0]]])
        np.testing.assert_allclose(response, expected, rtol=1e-14, atol=1e-14)

    def test_basis_index_requires_exact_144_primary_models(self):
        row = {
            "morphology": "m",
            "parameter_scenario": "s",
            "layout_id": "seven",
            "basis_sha256": "a",
            "conductance_sha256": "b",
            "capacitance_sha256": "c",
            "input_sha256": "d",
        }
        with self.assertRaisesRegex(ValueError, "not 144"):
            observer._basis_report_index({"reproducibility_diagnostics": {"basis_models": [row]}})


if __name__ == "__main__":
    unittest.main()
