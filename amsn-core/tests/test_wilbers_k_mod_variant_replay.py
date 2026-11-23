"""Protocol and analysis invariants for Wilbers released K-MOD AP-clamp replay."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).parents[1] / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import replay_wilbers_k_mod_variants as MODULE


def test_catalog_contains_all_nine_pinned_released_k_mechanisms():
    MODULE.validate_variant_catalog()
    assert set(MODULE.K_VARIANTS) == {
        "k_human", "k_mouse", "k_human_h1", "k_human_hm12inf",
        "k_hybrid1", "k_hybrid2", "k_hybrid3", "k_hybrid4", "k_hybrid5",
    }
    assert len({item["id"] for item in MODULE.K_VARIANTS.values()}) == 9
    assert MODULE.K_VARIANTS["k_human"]["id"] == 318647
    assert MODULE.K_VARIANTS["k_human_hm12inf"]["id"] == 318604
    assert MODULE.K_VARIANT_PINS["k_human"]["sha1"] == "d299b3430ecda7a94f6d1c37ac76b2878052c7d5"
    assert MODULE.K_VARIANT_PINS["k_hybrid5"]["bytes"] == 4080


def test_hybrid_roles_are_transcribed_from_original_source_audit():
    assert MODULE.SOURCE_ROLES["k_hybrid1"] == "human G/Gmax activation + inactivation"
    assert MODULE.SOURCE_ROLES["k_hybrid2"] == "human G/Gmax activation"
    assert MODULE.SOURCE_ROLES["k_hybrid3"] == "human G/Gmax inactivation"
    assert MODULE.SOURCE_ROLES["k_hybrid4"] == "human activation time constant"
    assert MODULE.SOURCE_ROLES["k_hybrid5"] == "human G/Gmax activation + activation time constant"


def test_source_parser_requires_exact_suffix_and_preserves_gate_structure():
    payload = b"""
NEURON {
    SUFFIX k_human_h1
    USEION k READ ek WRITE ik
    RANGE gbar
}
STATE { m h }
PARAMETER {
    gbar = 1
}
"""
    parsed = MODULE.parse_mod_identity(payload, "k_human_h1")
    assert parsed["suffix"] == "k_human_h1"
    assert parsed["state_names"] == ["m", "h"]
    with pytest.raises(ValueError, match="declares SUFFIX"):
        MODULE.parse_mod_identity(payload, "k_human")


def test_amplitude_validator_requires_full_finite_ap_coverage():
    assert MODULE.validate_amplitudes([1.0, 0.8, 0.6], 3, "synthetic") == [1.0, 0.8, 0.6]
    with pytest.raises(ValueError, match="expected 3"):
        MODULE.validate_amplitudes([1.0, 0.8], 3, "synthetic")
    with pytest.raises(ValueError, match="non-finite"):
        MODULE.validate_amplitudes([1.0, float("nan"), 0.6], 3, "synthetic")


def test_five_ap_source_replay_must_match_full_train_prefix():
    result = MODULE.validate_first_five_consistency(
        [10.0, 8.0, 7.0, 6.0, 5.0],
        [10.0, 8.0, 7.0, 6.0, 5.0] + [4.0] * 195,
        "synthetic",
    )
    assert result["status"] == "identical_within_tolerance"
    assert result["max_absolute_amplitude_difference"] == 0.0
    with pytest.raises(ValueError, match="differs from 200-AP prefix"):
        MODULE.validate_first_five_consistency(
            [10.0, 8.0, 7.0, 6.0, 5.0],
            [10.0, 8.0, 7.0, 6.0, 5.2] + [4.0] * 195,
            "synthetic",
        )


def test_epoch_metrics_separate_early_and_late_adaptation():
    model = [1.0 - 0.001 * i for i in range(200)]
    model[150] += 0.01
    experimental = [
        {
            "ap": i + 1,
            "n_recordings": 14,
            "mean": 1.0 - 0.001 * i,
            "median": 1.0 - 0.001 * i,
            "sd": 0.1,
            "sem": 0.1 / (14 ** 0.5),
            "min": 0.8,
            "max": 1.1,
        }
        for i in range(200)
    ]
    result = MODULE.compare_variant_to_recordings(model, experimental)
    assert result["metrics_vs_recording_mean"]["n"] == 200
    assert result["epoch_metrics"]["ap1_5"]["ap_range"] == [1, 5]
    assert result["epoch_metrics"]["ap1_100"]["ap_range"] == [1, 100]
    assert result["epoch_metrics"]["ap101_200"]["ap_range"] == [101, 200]
    assert result["ap200_delta_model_minus_experiment"] == pytest.approx(0.0)
    assert result["pointwise_sem_overlap_is_descriptive_only"] is True


def test_workbook_requires_all_200_human_input_columns():
    assert MODULE.replay.parse_k_workbook_header("amp_h_n_  1") == ("h", 1)
    assert MODULE.replay.parse_k_workbook_header("amp_m_n_  1") is None
    assert MODULE.EXPECTED_WORKBOOK_COLUMNS == 200


def test_protocol_windows_match_the_previously_validated_source_slices():
    assert MODULE.replay.protocol_end_ms(5) == 307
    assert MODULE.replay.expected_protocol_samples(5) == 13501
    assert MODULE.replay.protocol_end_ms(200) == 5182
    assert MODULE.replay.expected_protocol_samples(200) == 622876


def test_all_source_roles_are_present_and_runtime_promotion_is_not_implicit():
    assert set(MODULE.SOURCE_ROLES) == set(MODULE.K_VARIANT_NAMES)
    assert all("runtime" not in role.lower() for role in MODULE.SOURCE_ROLES.values())
