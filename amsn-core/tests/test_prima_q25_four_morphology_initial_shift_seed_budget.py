import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "research" / "audit_prima_q25_four_morphology_initial_shift_seed_budget.py"
SPEC = importlib.util.spec_from_file_location("q25_initial_seed_budget", MODULE_PATH)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit)

MORPHOLOGIES = (
    "NMO_03524_JacobsControl",
    "NMO_107159_Tamas_human_pyramidal_Control",
    "NMO_162186_AllenL23",
    "NMO_163775_Peng_mouse_Control",
)
LAYOUT_PORTS = {
    "seven": 7,
    "eight_basal_q25": 8,
    "eight_apical_q25": 8,
    "nine_both_q25": 9,
}
SHIFTS = (0.0, 100.0, 1000.0, 3000.0, 6000.0, 10000.0)


def synthetic_seed_rows():
    rows = []
    for morphology in MORPHOLOGIES:
        for scenario in range(9):
            for layout_id, port_count in LAYOUT_PORTS.items():
                cumulative = 0
                for shift in SHIFTS:
                    cumulative += port_count
                    rows.append({
                        "morphology": morphology,
                        "parameter_scenario": f"scenario_{scenario}",
                        "layout_id": layout_id,
                        "port_count": port_count,
                        "seed_shift_hz": shift,
                        "independent_seed_columns": port_count,
                        "cumulative_seed_columns": cumulative,
                        "remaining_order_after_seed": audit.MAX_ORDER - cumulative,
                    })
    return rows


class TestQ25InitialShiftSeedBudget(unittest.TestCase):
    def test_exact_seed_coverage_and_order_budgets(self):
        model_rows, morphology_rows = audit.summarize_seed_rows(
            synthetic_seed_rows(), shifts_hz=SHIFTS
        )
        self.assertEqual(len(model_rows), 144)
        self.assertEqual(len(morphology_rows), 16)
        for row in model_rows:
            expected_seed_columns = row["port_count"] * len(SHIFTS)
            self.assertEqual(row["initial_seed_columns_total"], expected_seed_columns)
            self.assertEqual(
                row["order_112_remaining_after_initial_seeds"],
                112 - expected_seed_columns,
            )
            self.assertEqual(
                row["order_168_remaining_after_initial_seeds"],
                168 - expected_seed_columns,
            )
            self.assertEqual(
                row["order_224_remaining_after_initial_seeds"],
                224 - expected_seed_columns,
            )

    def test_q25_layouts_consume_more_initial_seed_columns(self):
        model_rows, _ = audit.summarize_seed_rows(
            synthetic_seed_rows(), shifts_hz=SHIFTS
        )
        by_layout = {
            layout: next(row for row in model_rows if row["layout_id"] == layout)
            for layout in LAYOUT_PORTS
        }
        self.assertEqual(by_layout["seven"]["initial_seed_columns_total"], 42)
        self.assertEqual(by_layout["eight_basal_q25"]["initial_seed_columns_total"], 48)
        self.assertEqual(by_layout["eight_apical_q25"]["initial_seed_columns_total"], 48)
        self.assertEqual(by_layout["nine_both_q25"]["initial_seed_columns_total"], 54)

    def test_duplicate_shift_rows_are_rejected(self):
        rows = synthetic_seed_rows()
        rows.append(dict(rows[0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit.summarize_seed_rows(rows, shifts_hz=SHIFTS)

    def test_incomplete_shift_coverage_is_rejected(self):
        rows = synthetic_seed_rows()[:-1]
        with self.assertRaisesRegex(ValueError, "incomplete expansion-shift"):
            audit.summarize_seed_rows(rows, shifts_hz=SHIFTS)

    def test_inconsistent_cumulative_rank_is_rejected(self):
        rows = synthetic_seed_rows()
        rows[1]["cumulative_seed_columns"] = 999
        with self.assertRaisesRegex(ValueError, "cumulative seed rank"):
            audit.summarize_seed_rows(rows, shifts_hz=SHIFTS)

    def test_seed_rank_exceeding_a_requested_basis_order_is_rejected(self):
        rows = synthetic_seed_rows()
        with self.assertRaisesRegex(ValueError, "exceeds basis order 32"):
            audit.summarize_seed_rows(
                rows, shifts_hz=SHIFTS, orders=(32, 168, 224)
            )

    def test_per_shift_seed_rank_cannot_exceed_retained_port_count(self):
        rows = synthetic_seed_rows()
        rows[0]["independent_seed_columns"] = 8
        rows[0]["cumulative_seed_columns"] = 8
        with self.assertRaisesRegex(ValueError, "exceeds retained port count"):
            audit.summarize_seed_rows(rows, shifts_hz=SHIFTS)

    def test_unsorted_or_duplicate_orders_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            audit.summarize_seed_rows(
                synthetic_seed_rows(), shifts_hz=SHIFTS, orders=(112, 112, 224)
            )
        with self.assertRaisesRegex(ValueError, "ascending"):
            audit.summarize_seed_rows(
                synthetic_seed_rows(), shifts_hz=SHIFTS, orders=(224, 112)
            )


if __name__ == "__main__":
    unittest.main()
