import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "research" / "audit_prima_q25_cpu_dispatch_rerun.py"
SPEC = importlib.util.spec_from_file_location("q25_dispatch_audit", MODULE_PATH)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit)


def synthetic_case_rows():
    rows = []
    morphologies = tuple(audit.MORPHOLOGY_NAMES)
    scenarios = ("nominal", "Rm_minus20", "Rm_plus20", "Cm_minus20", "Cm_plus20",
                 "Ra_minus20", "Ra_plus20", "all_minus20", "all_plus20")
    sources = ("soma", "basal_q75", "apical_q75")
    for morphology in morphologies:
        for scenario in scenarios:
            for source in sources:
                for output in range(1, 8):
                    for pulse in ("2.0", "10.0"):
                        for window in ("20.0", "40.0"):
                            for layout in audit.LAYOUTS:
                                rows.append({
                                    "morphology": morphology,
                                    "parameter_scenario": scenario,
                                    "source_name": source,
                                    "output_swc_id": str(output),
                                    "pulse_width_ms": pulse,
                                    "window_ms": window,
                                    "layout_id": layout,
                                })
    return rows


class TestQ25DispatchAudit(unittest.TestCase):
    def test_case_key_places_window_before_layout(self):
        row = {
            "morphology": "NMO_03524_JacobsControl",
            "parameter_scenario": "nominal",
            "source_name": "soma",
            "output_swc_id": "1",
            "pulse_width_ms": "2.0",
            "window_ms": "40.0",
            "layout_id": "nine_both_q25",
        }
        self.assertEqual(audit.key(row), (
            "NMO_03524_JacobsControl", "nominal", "soma", "1",
            "2.0", "40.0", "nine_both_q25",
        ))

    def test_full_four_layout_matrix_has_exact_case_count(self):
        rows = synthetic_case_rows()
        indexed = audit.index_rows(rows, "synthetic")
        self.assertEqual(len(indexed), 12096)
        self.assertEqual(len({k[:6] for k in indexed}), 3024)

    def test_baseline_case_keys_retain_each_morphology_and_window(self):
        indexed = audit.index_rows(synthetic_case_rows(), "synthetic")
        baseline = audit.baseline_case_keys(indexed)
        self.assertEqual(len(baseline), 3024)
        for morphology in audit.MORPHOLOGY_NAMES:
            for window in ("20.0", "40.0"):
                group = [
                    key for key in baseline
                    if key[0] == morphology and key[5] == window
                ]
                self.assertEqual(len(group), 378)

    def test_duplicate_or_missing_layout_is_rejected(self):
        rows = synthetic_case_rows()
        rows[-1] = dict(rows[0])
        with self.assertRaisesRegex(ValueError, "duplicate paired key"):
            audit.index_rows(rows, "duplicate")
        rows = synthetic_case_rows()[:-1]
        with self.assertRaisesRegex(ValueError, "row count"):
            audit.index_rows(rows, "missing")

    def test_percentile_uses_linear_interpolation(self):
        self.assertAlmostEqual(audit.percentile([0.0, 10.0, 20.0], 0.90), 18.0)
        self.assertEqual(audit.median([2.0, 4.0, 8.0]), 4.0)

    def test_basis_hash_comparison_counts_each_projection(self):
        rows = []
        for morphology in audit.MORPHOLOGY_NAMES:
            for scenario in ("a", "b", "c", "d", "e", "f", "g", "h", "i"):
                for layout in audit.LAYOUTS:
                    rows.append({
                        "morphology": morphology,
                        "parameter_scenario": scenario,
                        "layout_id": layout,
                        "basis_sha256": f"basis-{len(rows)}",
                        "conductance_sha256": f"g-{len(rows)}",
                        "capacitance_sha256": f"c-{len(rows)}",
                        "input_sha256": f"b-{len(rows)}",
                    })
        report_a = {"reproducibility_diagnostics": {"basis_models": rows}}
        report_b = {"reproducibility_diagnostics": {"basis_models": [dict(x) for x in rows]}}
        result = audit.compare_basis_hashes(report_a, report_b)
        self.assertEqual(result["basis_sha256"], {"equal": 144, "different": 0, "total": 144})
        report_b["reproducibility_diagnostics"]["basis_models"][0]["basis_sha256"] = "different"
        result = audit.compare_basis_hashes(report_a, report_b)
        self.assertEqual(result["basis_sha256"], {"equal": 143, "different": 1, "total": 144})

    def test_trace_hash_comparison_requires_216_pairs(self):
        rows = []
        for morphology in audit.MORPHOLOGY_NAMES:
            for scenario in range(9):
                for trace_kind in range(6):
                    rows.append({
                        "morphology": morphology,
                        "parameter_scenario": str(scenario),
                        "trace_kind": str(trace_kind),
                        "trace_sha256": f"trace-{len(rows)}",
                    })
        report_a = {"reproducibility_diagnostics": {"trace_outputs": rows}}
        report_b = {"reproducibility_diagnostics": {"trace_outputs": [dict(x) for x in rows]}}
        self.assertEqual(
            audit.compare_trace_hashes(report_a, report_b),
            {"equal": 216, "different": 0, "total": 216},
        )


if __name__ == "__main__":
    unittest.main()
