import math
import pytest

from amsn.units import (
    ohm_cm_to_ohm_m, ohm_cm2_to_ohm_m2, uf_cm2_to_f_m2,
    ms_cm2_to_s_m2, pa_to_a, um_to_m,
)
from amsn.morphology import MorphologyError, SWCMorphology


def test_unit_conversions_are_consistent():
    assert ohm_cm_to_ohm_m(100) == pytest.approx(1.0)
    assert ohm_cm2_to_ohm_m2(10_000) == pytest.approx(1.0)
    assert uf_cm2_to_f_m2(1.0) == pytest.approx(0.01)
    assert ms_cm2_to_s_m2(1.0) == pytest.approx(10.0)
    assert pa_to_a(3.0) == pytest.approx(3e-12)
    assert um_to_m(12) == pytest.approx(12e-6)


def test_swc_summary_handles_branch_and_frustum_area():
    morph = SWCMorphology.from_text("""
    # id type x y z radius parent
    1 1 0 0 0 2 -1
    2 3 0 0 10 1 1
    3 3 10 0 10 1 2
    4 4 -10 0 10 1 2
    """)
    summary = morph.summary()
    assert summary.node_count == 4
    assert summary.edge_count == 3
    assert summary.branch_point_count == 1
    assert summary.total_path_length_um == pytest.approx(10 + 10 + 10)
    expected_area = 4 * math.pi * 2**2 + math.pi * (2 + 1) * math.sqrt(10**2 + 1**2) + 2 * (2 * math.pi * 1 * 10)
    assert summary.estimated_membrane_area_um2 == pytest.approx(expected_area)
    assert summary.neurite_length_by_type_um == {3: 20.0, 4: 10.0}


@pytest.mark.parametrize("text", [
    "1 1 0 0 0 1 -1\n1 3 0 0 1 1 1",  # duplicate ID
    "1 1 0 0 0 1 -1\n2 3 0 0 1 1 9",  # missing parent
    "1 1 0 0 0 -1 -1",                  # invalid radius
    "1 1 0 0 0 1 -1\n2 3 0 0 1 1 3\n3 3 0 0 2 1 2",  # disconnected cycle
    "1 1 0 0 0 1 -1\n2 3 0 0 1 1 2", # self-parent
])
def test_invalid_swc_is_rejected(text):
    with pytest.raises(MorphologyError):
        SWCMorphology.from_text(text)


def test_swc_file_example_is_explicitly_synthetic_and_parseable():
    from pathlib import Path
    sample = Path(__file__).parents[1] / "examples" / "synthetic_branching.swc"
    morph = SWCMorphology.from_file(sample)
    summary = morph.summary()
    assert summary.node_count == 7
    # The root is the synthetic soma and is not counted as a neurite bifurcation.
    assert summary.branch_point_count == 1


def test_swc_long_chain_is_stack_safe():
    # A realistic SWC may contain thousands of points in a single branch.
    # Parsing must not depend on Python's recursion limit.
    count = 5_000
    rows = ["1 1 0 0 0 2 -1"]
    rows.extend(f"{i} 3 0 0 {i - 1} 0.5 {i - 1}" for i in range(2, count + 1))
    morph = SWCMorphology.from_text("\n".join(rows))
    summary = morph.summary()
    assert summary.node_count == count
    assert summary.edge_count == count - 1
    assert summary.branch_point_count == 0
    assert summary.total_path_length_um == pytest.approx(count - 1)
