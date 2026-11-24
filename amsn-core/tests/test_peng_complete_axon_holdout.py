"""Source, topology and metadata guardrails for the Peng complete-axon holdout."""
from __future__ import annotations

import sys
from pathlib import Path

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import prepare_nmo163775_peng_control_holdout as MODULE


def test_pinned_neuromorpho_record_identity():
    assert MODULE.EXPECTED_NODE_COUNT == 4209
    assert MODULE.EXPECTED_TYPE_COUNTS == {1: 3, 2: 3602, 3: 306, 4: 298}
    assert MODULE.LABEL == "NMO_163775_PengControl"


def test_parser_accepts_valid_swc_with_three_point_soma_and_all_domains():
    source = """# fixture
1 1 0 0 0 2 -1
2 1 0 1 0 2 1
3 1 0 -1 0 2 1
4 2 0 0 1 1 1
5 3 1 0 0 1 1
6 4 0 1 1 1 2
"""
    rows, counts = MODULE.parse_swc_text(source)
    assert len(rows) == 6
    assert counts == {1: 3, 2: 1, 3: 1, 4: 1}


def test_parser_rejects_duplicate_node_ids():
    source = """1 1 0 0 0 2 -1
1 3 1 0 0 1 1
"""
    try:
        MODULE.parse_swc_text(source)
    except ValueError as exc:
        assert "duplicate" in str(exc).lower()
    else:
        raise AssertionError("duplicate node IDs must fail closed")


def test_parser_rejects_missing_parent_references():
    source = """1 1 0 0 0 2 -1
2 3 1 0 0 1 99
"""
    try:
        MODULE.parse_swc_text(source)
    except ValueError as exc:
        assert "missing parent" in str(exc).lower()
    else:
        raise AssertionError("missing parent references must fail closed")


def test_parser_rejects_multiple_roots():
    source = """1 1 0 0 0 2 -1
2 1 1 0 0 2 -1
"""
    try:
        MODULE.parse_swc_text(source)
    except ValueError as exc:
        assert "one soma root" in str(exc).lower()
    else:
        raise AssertionError("multiple roots must fail closed")


def test_metadata_remains_control_and_complete_axon():
    assert MODULE.SOURCE_URL.endswith("/18453_5766_x31719_y6139-semi_r.CNG.swc")
    assert "Peng" in MODULE.LABEL
    assert MODULE.EXPECTED_SWC_SHA256 == "94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f"
    assert MODULE.EXPECTED_TYPE_COUNTS[2] > 0
    assert MODULE.EXPECTED_SEVEN_PORT_IDS == {1, 54, 144, 4151, 3886, 3926, 3948}
    assert MODULE.EXPECTED_Q25_NODE_IDS == (224, 4096)



def test_segment_centre_bracket_interpolates_inside_section():
    import human_fine_mesh_passive_dc_audit as FINE

    lower, upper, weight, fallback = FINE.segment_centre_bracket(
        [0.1, 0.3, 0.5, 0.7, 0.9], 0.4
    )
    assert (lower, upper) == (1, 2)
    assert abs(weight - 0.5) < 1e-12
    assert fallback is None


def test_segment_centre_bracket_uses_nearest_segment_at_right_endpoint():
    import human_fine_mesh_passive_dc_audit as FINE

    lower, upper, weight, fallback = FINE.segment_centre_bracket(
        [0.1, 0.3, 0.5, 0.7, 0.9], 1.0
    )
    assert (lower, upper) == (4, 4)
    assert weight == 0.0
    assert fallback == "right_endpoint_nearest_segment"


def test_segment_centre_bracket_uses_nearest_segment_at_left_endpoint():
    import human_fine_mesh_passive_dc_audit as FINE

    lower, upper, weight, fallback = FINE.segment_centre_bracket(
        [0.1, 0.3, 0.5, 0.7, 0.9], 0.0
    )
    assert (lower, upper) == (0, 0)
    assert weight == 0.0
    assert fallback == "left_endpoint_nearest_segment"


def test_segment_centre_bracket_rejects_unsorted_centres():
    import human_fine_mesh_passive_dc_audit as FINE

    try:
        FINE.segment_centre_bracket([0.1, 0.5, 0.4], 0.45)
    except ValueError as exc:
        assert "strictly increasing" in str(exc)
    else:
        raise AssertionError("non-monotonic segment centres must fail closed")
