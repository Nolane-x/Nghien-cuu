from pathlib import Path

import pytest

from amsn.morphology import MorphologyError
from amsn.provenance import validate_swc_morphology


VALID_SWC = """\
1 1 0 0 0 4 -1
2 1 -4 0 0 4 1
3 1 4 0 0 4 1
4 2 0 0 10 0.1 1
5 2 0 0 20 0.1 4
6 3 10 0 0 1 1
7 3 20 0 0 0.8 6
8 4 -10 0 0 1 1
9 4 -20 0 0 0.8 8
10 3 30 0 0 0.7 7
"""


def write_swc(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "fixture.swc"
    path.write_text(text, encoding="utf-8")
    return path


def test_validate_swc_checks_types_topology_and_three_point_soma(tmp_path):
    result = validate_swc_morphology(
        write_swc(tmp_path, VALID_SWC),
        expected_node_count=10,
    )
    assert result.summary.node_count == 10
    assert result.summary.root_count == 1
    assert result.three_point_soma_detected is True
    assert result.neurite_type_counts == {1: 3, 2: 2, 3: 3, 4: 2}


def test_validate_swc_rejects_wrong_expected_node_count(tmp_path):
    with pytest.raises(MorphologyError, match="record count"):
        validate_swc_morphology(
            write_swc(tmp_path, VALID_SWC),
            expected_node_count=11,
        )


def test_validate_swc_rejects_missing_apical_type(tmp_path):
    no_apical = "\n".join(
        line for line in VALID_SWC.splitlines()
        if not line.startswith(("8 ", "9 "))
    )
    with pytest.raises(MorphologyError, match="missing required neurite types"):
        validate_swc_morphology(
            write_swc(tmp_path, no_apical),
            expected_node_count=8,
        )


def test_validate_swc_rejects_missing_three_point_soma(tmp_path):
    one_point_soma = """\
1 1 0 0 0 4 -1
2 2 0 0 10 0.1 1
3 2 0 0 20 0.1 2
4 3 10 0 0 1 1
5 3 20 0 0 0.8 4
6 4 -10 0 0 1 1
7 4 -20 0 0 0.8 6
"""
    with pytest.raises(MorphologyError, match="three-point soma"):
        validate_swc_morphology(
            write_swc(tmp_path, one_point_soma),
            expected_node_count=7,
        )
