"""Source, topology and metadata guardrails for the Jacobs control holdout."""
from __future__ import annotations

import sys
from pathlib import Path

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import prepare_jacobs_control_holdout as MODULE


def test_pinned_neuromorpho_record_identity():
    assert MODULE.EXPECTED_NODE_COUNT == 869
    assert MODULE.EXPECTED_TYPE_COUNTS == {1: 3, 2: 42, 3: 816, 4: 8}
    assert MODULE.LABEL == "NMO_03524_JacobsControl"


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


def test_metadata_remains_control_and_partial_axon():
    assert MODULE.SOURCE_URL.endswith("/1-5-3.CNG.swc")
    assert "Jacobs" in MODULE.LABEL
    assert MODULE.EXPECTED_TYPE_COUNTS[2] > 0
