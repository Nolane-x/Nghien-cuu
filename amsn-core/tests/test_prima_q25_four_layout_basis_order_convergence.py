import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "research" / "run_prima_q25_four_layout_basis_order_convergence.py"
SPEC = importlib.util.spec_from_file_location("q25_order_sweep_driver", MODULE_PATH)
driver = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(driver)


class TestQ25BasisOrderSweepDriver(unittest.TestCase):
    def test_declared_order_grid_includes_existing_reference_once(self):
        self.assertEqual(
            driver.validate_order_grid(),
            (112, 168, 224),
        )

    def test_reference_order_reuses_completed_result_stem(self):
        self.assertEqual(
            driver.result_stem_for_order(168),
            driver.BASE_RESULT_STEM,
        )

    def test_new_orders_have_distinct_deterministic_stems(self):
        stems = [driver.result_stem_for_order(order) for order in (112, 224)]
        self.assertEqual(len(stems), len(set(stems)))
        self.assertTrue(all(f"order_{order}" in stem for order, stem in zip((112, 224, 280), stems)))

    def test_invalid_and_unplanned_orders_are_rejected(self):
        for order in (0, -1, True, 84, 1680, 280):
            with self.subTest(order=order):
                with self.assertRaises(ValueError):
                    driver.result_stem_for_order(order)

    def test_duplicate_or_unsorted_order_grids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            driver.validate_order_grid((112, 112, 224))
        with self.assertRaisesRegex(ValueError, "ascending"):
            driver.validate_order_grid((224, 112, 280))
        with self.assertRaisesRegex(ValueError, "must not be recomputed"):
            driver.validate_order_grid((112, 168, 224))

    def test_coverage_constants_match_four_layout_case_design(self):
        self.assertEqual(driver.EXPECTED_CASE_ROWS, 4 * 9 * 4 * 3 * 2 * 7 * 2)
        self.assertEqual(driver.EXPECTED_COMPARISON_ROWS, 4 * 9 * 3 * 3 * 2 * 7 * 2)
        self.assertEqual(driver.EXPECTED_SOURCE_POSTHOC_ROWS, 4 * 3 * 3 * 2 * 2 * 7)
        self.assertEqual(driver.EXPECTED_MORPHOLOGY_POSTHOC_ROWS, 4 * 3 * 2 * 7)
        self.assertEqual(driver.EXPECTED_INTERACTION_POSTHOC_ROWS, 4 * 3 * 2 * 2 * 7)


if __name__ == "__main__":
    unittest.main()
