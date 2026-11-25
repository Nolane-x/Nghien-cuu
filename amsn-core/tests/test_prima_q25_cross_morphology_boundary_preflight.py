"""Tests for q25 cross-morphology finite-window replication preflight."""
from __future__ import annotations

import sys
from pathlib import Path

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import pytest

import prepare_prima_q25_cross_morphology_boundary_holdouts as preflight


@pytest.fixture
def valid_case():
    return {
        "morphology_key": "fixture",
        "common_ids": [1, 2, 3, 4, 5, 6, 7],
        "nine_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "roles": {
            8: ["basal_q25"],
            9: ["apical_q25"],
        },
        "sources": {"soma": 1, "basal_q75": 3, "apical_q75": 6},
        "expected_shared": (1, 2, 3, 4, 5, 6, 7),
        "expected_q25": {"basal_q25": 8, "apical_q25": 9},
        "expected_sources": {"soma": 1, "basal_q75": 3, "apical_q75": 6},
    }


def call(case, *, maximum_segment_um=0.499, cap=0.5):
    return preflight.validate_port_manifest(
        case["morphology_key"],
        case["common_ids"],
        case["nine_ids"],
        case["roles"],
        case["sources"],
        case["expected_shared"],
        case["expected_q25"],
        case["expected_sources"],
        maximum_segment_um,
        cap,
    )


def test_valid_q25_mapping_passes(valid_case):
    assert call(valid_case) == {"basal_q25": 8, "apical_q25": 9}


def test_changed_shared_node_identity_fails(valid_case):
    valid_case["common_ids"] = [1, 2, 3, 4, 5, 6, 70]
    with pytest.raises(ValueError, match="shared SWC node IDs"):
        call(valid_case)


def test_missing_or_swapped_q25_role_fails(valid_case):
    valid_case["roles"][8] = ["apical_q25"]
    valid_case["roles"][9] = ["basal_q25"]
    with pytest.raises(ValueError, match="q25 node identities"):
        call(valid_case)


def test_source_mapping_change_fails(valid_case):
    valid_case["sources"]["basal_q75"] = 30
    with pytest.raises(ValueError, match="source SWC node identities"):
        call(valid_case)


def test_mesh_exceeding_common_cap_fails(valid_case):
    with pytest.raises(ValueError, match="exceeds the common cap"):
        call(valid_case, maximum_segment_um=0.50001)


def test_duplicate_shared_port_fails(valid_case):
    valid_case["common_ids"] = [1, 2, 3, 4, 5, 6, 6]
    with pytest.raises(ValueError, match="expected seven shared"):
        call(valid_case)


def test_q25_port_overlap_fails(valid_case):
    valid_case["nine_ids"] = [1, 2, 3, 4, 5, 6, 7, 8, 8]
    with pytest.raises(ValueError, match="exactly two q25-only IDs"):
        call(valid_case)


def test_each_real_holdout_has_distinct_source_condition_and_q25_ids():
    jacobs, allen = preflight.EXPECTED_MORPHOLOGIES
    assert jacobs["q25_ids"] == {"basal_q25": 272, "apical_q25": 864}
    assert allen["q25_ids"] == {"basal_q25": 2713, "apical_q25": 4488}
    assert jacobs["condition"] == "Control"
    assert allen["condition"] == "epilepsy surgical specimen"
    assert jacobs["axon_complete"] is False
    assert allen["axon_complete"] is False
