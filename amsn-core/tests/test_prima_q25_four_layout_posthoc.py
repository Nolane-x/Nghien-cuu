import importlib.util
import math
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "research" / "summarize_prima_q25_four_layout_interactions.py"
SPEC = importlib.util.spec_from_file_location("q25_posthoc", MODULE_PATH)
q25 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(q25)


def make_case(layout: str, multiplier: float) -> dict[str, str]:
    row = {
        "morphology": "morph_a",
        "parameter_scenario": "nominal",
        "source_name": "soma",
        "output_swc_id": "17",
        "pulse_width_ms": "2.0",
        "window_ms": "20.0",
        "layout_id": layout,
    }
    for _name, (field, _unit, _description) in q25.METRICS.items():
        row[field] = str(10.0 * multiplier)
    return row


def make_comparison(layout: str, multiplier: float) -> dict[str, str]:
    row = {
        "morphology": "morph_a",
        "parameter_scenario": "nominal",
        "source_name": "soma",
        "output_swc_id": "17",
        "pulse_width_ms": "2.0",
        "window_ms": "20.0",
        "candidate_layout": layout,
    }
    for field in q25.COMPARISON_RATIO_FIELDS.values():
        row[field] = str(multiplier)
    return row


class TestQ25Posthoc(unittest.TestCase):
    def test_additive_and_multiplicative_interaction_contrasts(self):
        values = q25.metric_contrasts(10.0, 8.0, 9.0, 6.0)
        self.assertAlmostEqual(values["basal_delta_vs_seven"], -2.0)
        self.assertAlmostEqual(values["apical_delta_vs_seven"], -1.0)
        self.assertAlmostEqual(values["combined_delta_vs_seven"], -4.0)
        self.assertAlmostEqual(values["additive_interaction_delta"], -1.0)
        self.assertAlmostEqual(values["multiplicative_interaction_ratio"], 5.0 / 6.0)
        self.assertAlmostEqual(values["log_multiplicative_interaction"], math.log(5.0 / 6.0))

    def test_zero_error_keeps_additive_contrast_but_disables_log_ratio(self):
        values = q25.metric_contrasts(0.0, 1.0, 1.0, 1.0)
        self.assertEqual(values["additive_interaction_delta"], 1.0)
        self.assertIsNone(values["multiplicative_interaction_ratio"])
        self.assertIsNone(values["log_multiplicative_interaction"])

    def test_percentile_uses_linear_interpolation(self):
        self.assertAlmostEqual(q25.percentile([0.0, 10.0, 20.0], 0.90), 18.0)
        self.assertEqual(q25.percentile([3.0], 0.5), 3.0)

    def test_exact_four_layout_matrix_and_paired_ratios_validate(self):
        multipliers = {
            "seven": 1.0,
            "eight_basal_q25": 0.8,
            "eight_apical_q25": 0.9,
            "nine_both_q25": 0.6,
        }
        metric_rows = [
            make_case(layout, factor) for layout, factor in multipliers.items()
        ]
        comparison_rows = [
            make_comparison(layout, factor)
            for layout, factor in multipliers.items()
            if layout != "seven"
        ]
        index = q25.index_metric_rows(metric_rows, enforce_expected=False)
        q25.validate_comparison_rows(
            comparison_rows, index, enforce_expected=False
        )
        self.assertEqual(len(index), 4)

    def test_missing_layout_is_rejected(self):
        metric_rows = [
            make_case("seven", 1.0),
            make_case("eight_basal_q25", 0.8),
            make_case("eight_apical_q25", 0.9),
        ]
        with self.assertRaisesRegex(ValueError, "exact four-layout set"):
            q25.index_metric_rows(metric_rows, enforce_expected=False)

    def test_duplicate_layout_key_is_rejected(self):
        metric_rows = [
            make_case("seven", 1.0),
            make_case("seven", 1.1),
            make_case("eight_basal_q25", 0.8),
            make_case("eight_apical_q25", 0.9),
            make_case("nine_both_q25", 0.6),
        ]
        with self.assertRaisesRegex(ValueError, "duplicate case-metric key"):
            q25.index_metric_rows(metric_rows, enforce_expected=False)

    def test_comparison_ratio_must_match_case_metrics(self):
        multipliers = {
            "seven": 1.0,
            "eight_basal_q25": 0.8,
            "eight_apical_q25": 0.9,
            "nine_both_q25": 0.6,
        }
        metric_rows = [
            make_case(layout, factor) for layout, factor in multipliers.items()
        ]
        comparison_rows = [
            make_comparison(layout, factor)
            for layout, factor in multipliers.items()
            if layout != "seven"
        ]
        comparison_rows[0]["candidate_over_seven_discrete_be_ratio"] = "999"
        index = q25.index_metric_rows(metric_rows, enforce_expected=False)
        with self.assertRaisesRegex(ValueError, "comparison mismatch"):
            q25.validate_comparison_rows(
                comparison_rows, index, enforce_expected=False
            )

    def test_non_finite_values_are_rejected(self):
        row = make_case("seven", 1.0)
        row[q25.METRICS["continuous_ac_error_pct"][0]] = "nan"
        with self.assertRaisesRegex(ValueError, "finite and non-negative"):
            q25.index_metric_rows([row], enforce_expected=False)


if __name__ == "__main__":
    unittest.main()
