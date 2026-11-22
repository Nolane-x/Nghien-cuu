import sys
from pathlib import Path

import numpy as np
import pytest

from amsn.cable import CableCompartment, CableTree

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

from prima_phase_profile import (  # noqa: E402
    measure_reduced_frequency,
    measure_reduced_transient,
    profile_prima_build,
)


def _small_tree():
    return CableTree([
        CableCompartment("soma", 20e-6, 20e-6, None),
        CableCompartment("basal", 100e-6, 2e-6, "soma"),
        CableCompartment("apical", 120e-6, 1.5e-6, "soma"),
        CableCompartment("branch", 80e-6, 1.0e-6, "basal"),
    ])


def test_profiled_prima_build_reports_each_actual_builder_phase():
    tree = _small_tree()
    model, summary = profile_prima_build(
        tree,
        retained_indices=(0, 2),
        max_order=3,
        expansion_frequencies_hz=(0.0, 1000.0),
    )

    assert model.order == 3
    assert set(summary["phases"]) == {
        "shifted_hines_solve",
        "orthogonalization",
        "congruence_projection",
        "multishift_orchestration",
        "other_python_self",
    }
    phases = summary["phases"]
    assert phases["shifted_hines_solve"]["calls"] > 0
    assert phases["orthogonalization"]["calls"] > 0
    assert phases["congruence_projection"]["calls"] == 1
    assert phases["multishift_orchestration"]["calls"] == 1
    assert all(item["self_seconds"] >= 0 for item in phases.values())
    assert summary["build_wall_seconds"] > 0
    assert summary["profiled_python_self_seconds"] > 0
    assert phases["other_python_self"]["self_seconds"] >= 0
    np.linalg.cholesky(model.conductance_matrix_s)
    np.linalg.cholesky(model.capacitance_matrix_f)


def test_reduced_frequency_and_transient_profile_are_finite():
    tree = _small_tree()
    model, _ = profile_prima_build(
        tree,
        retained_indices=(0, 2),
        max_order=3,
        expansion_frequencies_hz=(0.0, 1000.0),
    )

    frequency = measure_reduced_frequency(model, frequencies_hz=(0.0, 100.0))
    transient = measure_reduced_transient(model, source_port=0)

    assert frequency["solve_calls"] == 2
    assert frequency["wall_seconds"] > 0
    assert frequency["cpu_seconds"] >= 0
    assert frequency["finite_checksum"] is True
    assert transient["steps"] == 100
    assert transient["wall_seconds"] > 0
    assert transient["cpu_seconds"] >= 0
    assert transient["seconds_per_step"] > 0
    assert np.isfinite(transient["peak_port_perturbation_v"])


@pytest.mark.parametrize("source_port", [-1, 2])
def test_reduced_transient_rejects_invalid_source_port(source_port):
    tree = _small_tree()
    model, _ = profile_prima_build(
        tree,
        retained_indices=(0, 2),
        max_order=3,
        expansion_frequencies_hz=(0.0, 1000.0),
    )
    with pytest.raises(ValueError):
        measure_reduced_transient(model, source_port=source_port)
