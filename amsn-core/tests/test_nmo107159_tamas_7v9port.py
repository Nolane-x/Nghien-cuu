"""Coverage and exact-port matching tests for NMO_107159 Tamas human pyramidal Control 7-vs-9-port PRIMA."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import replay_nmo107159_tamas_7v9port as MODULE


def test_matrix_row_counts_are_exact():
    assert MODULE.expected_counts() == {
        "models": 36,
        "frequency": 324,
        "transient": 1728,
        "matched_shared": 756,
        "q25_only": 216,
        "hines_shared": 378,
    }


def test_tamas_human_pyramidal_source_hash_is_pinned():
    assert MODULE.EXPECTED_SWC_RECORDS == 7228
    assert MODULE.EXPECTED_SWC_SHA256 == "6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023"


def test_seven_and_nine_port_sets_share_exactly_seven_swc_nodes():
    seven = [1, 5564, 6363, 7023, 4301, 4735, 4623]
    nine = seven + [6609, 4404]
    roles = {
        6609: ["basal_q25"],
        4404: ["apical_q25"],
    }
    common, extra = MODULE.validate_port_node_sets(seven, nine, roles)
    assert common == sorted(seven)
    assert extra == [4404, 6609]


@pytest.mark.parametrize(
    "seven,nine,roles",
    [
        ([1, 2, 3], [1, 2, 3, 4, 5], {4:["basal_q25"],5:["apical_q25"]}),
        ([1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 8, 9, 10, 11],
         {10:["basal_q25"],11:["apical_q25"]}),
        ([1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 6, 7, 8, 9],
         {8:["basal_q25"],9:["basal_q25"]}),
    ],
)
def test_invalid_port_set_mappings_fail_closed(seven, nine, roles):
    with pytest.raises(ValueError):
        MODULE.validate_port_node_sets(seven, nine, roles)


def test_matched_shared_rows_pair_by_exact_swc_id_and_protocol():
    rows = []
    for port_count, values in (
        (7, {1:0.1,5564:0.2}),
        (9, {1:0.11,5564:0.18,6609:0.01}),
    ):
        for node_id, value in values.items():
            rows.append({
                "port_count":port_count,
                "basis_order":112,
                "parameter_scenario":"nominal",
                "source_name":"soma",
                "pulse_width_ms":2.0,
                "port_swc_id":node_id,
                "port_roles":"probe",
                "port_nrmse_pct":value,
            })
    result = MODULE.build_matched_shared_rows(rows, [1,5564], expected_count=2)
    assert len(result) == 2
    assert result[0]["port_swc_id"] == 1
    assert result[0]["error_ratio_nine_over_seven"] == pytest.approx(1.1)
    assert result[1]["port_swc_id"] == 5564
    assert result[1]["error_ratio_nine_over_seven"] == pytest.approx(0.9)


def test_matched_shared_requires_complete_pair_coverage():
    rows = [{
        "port_count":7,"basis_order":112,"parameter_scenario":"nominal",
        "source_name":"soma","pulse_width_ms":2.0,"port_swc_id":1,
        "port_roles":"probe","port_nrmse_pct":0.1,
    }]
    with pytest.raises(ValueError, match="coverage mismatch"):
        MODULE.build_matched_shared_rows(rows, [1], expected_count=2)


def test_peng_source_and_complete_axon_holdout_metadata_are_pinned():
    assert MODULE.EXPECTED_SWC_RECORDS == 7228
    assert MODULE.EXPECTED_SWC_SHA256 == "6b3b00905fe3659132dbda67ad4f0f30287984e75d5bde41ba79f61b6d479023"
