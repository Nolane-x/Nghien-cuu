"""Preflight one independent Allen Cell Types human morphology through AMSN/NEURON.

This is a provenance, SWC topology, port-mapping and passive-RC smoke test.
It does not certify a complete axon or biological population generalization.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from amsn.provenance import validate_swc_morphology

ROOT = Path(__file__).parents[1]
SWC = ROOT / "data" / "human" / "allen_cell_types" / "770307286_transformed.CNG.swc"
EXPECTED_NODE_COUNT = 7287
MAX_NEURON_SEGMENT_UM = 0.125
SOURCE_NAMES = ("soma", "basal_q75", "apical_q75")
PROBE_NAMES = ("soma", "basal_q50", "basal_q90", "apical_q50", "apical_q90")
METADATA = {
    "neuromorpho_id": "NMO_162186",
    "cell_name": "770307286_transformed",
    "archive": "Allen Cell Types",
    "species": "human",
    "region": "right middle temporal gyrus, neocortex, layer 2-3",
    "cell_class": "pyramidal, excitatory intratelencephalic (IT)",
    "experimental_condition": "epilepsy",
    "dendrites_complete": True,
    "axon_complete": False,
    "source_url": (
        "https://neuromorpho.org/dableFiles/allen%20cell%20types/CNG%20version/"
        "770307286_transformed.CNG.swc"
    ),
    "metadata_url": "https://neuromorpho.org/neuron_info.jsp?neuron_name=770307286_transformed",
    "license": "CC BY 4.0 (NeuroMorpho.Org terms of use)",
    "neuromorpho_rrid": "SCR_002145",
    "published_paper_doi": "10.1038/s41586-021-03813-8",
    "dataset_collection_doi": "10.35077/g.19",
    "neuromorpho_citation_doi": "10.1096/fba.2024-00048",
}


def main() -> None:
    if not SWC.is_file():
        raise FileNotFoundError(
            f"Expected downloaded source SWC at {SWC}; run the workflow download step first"
        )
    source_bytes = SWC.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()

    validated = validate_swc_morphology(
        SWC,
        expected_node_count=EXPECTED_NODE_COUNT,
        required_neurite_types=(1, 2, 3, 4),
        require_three_point_soma=True,
    )
    morphology = validated.morphology
    summary = validated.summary
    if validated.neurite_type_counts.get(2, 0) == 0:
        raise RuntimeError("expected at least one partial axon (SWC type 2) point")

    examples_dir = str(Path(__file__).parent)
    if examples_dir not in sys.path:
        sys.path.insert(0, examples_dir)
    import neuron_cross_validation as reference
    import human_fine_mesh_passive_dc_audit as fine_audit
    import neuron

    reference.DATA = SWC
    reference.MAX_NEURON_SEGMENT_UM = MAX_NEURON_SEGMENT_UM
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, mapped = fine_audit.build_sites(morphology, reader, sections)

    injection_by_name = dict(injections)
    probe_by_name = dict(probes)
    if set(injection_by_name) != set(SOURCE_NAMES):
        raise RuntimeError(f"source placement coverage mismatch: {sorted(injection_by_name)}")
    if set(probe_by_name) != set(PROBE_NAMES):
        raise RuntimeError(f"probe placement coverage mismatch: {sorted(probe_by_name)}")

    site_ids = sorted(set(injection_by_name.values()) | set(probe_by_name.values()))
    if len(site_ids) != 7:
        raise RuntimeError(f"expected seven unique SWC ports, got {len(site_ids)}")
    if set(site_ids) - set(mapped):
        raise RuntimeError("one or more selected SWC ports were not mapped by Import3D")

    electrical_map = morphology.electrical_node_mapping()
    cable = morphology.to_cable_tree()
    cable_mapping = {
        node_id: f"swc_{electrical_map[node_id]}" for node_id in morphology.nodes
    }
    port_indices = [cable.index[cable_mapping[node_id]] for node_id in site_ids]
    if len(set(port_indices)) != 7:
        raise RuntimeError("SWC-to-AMSN electrical mapping collapsed one or more retained ports")

    mapping_rows = []
    site_roles = defaultdict(list)
    for name, node_id in injections + probes:
        site_roles[node_id].append(name)
    for node_id in site_ids:
        row = mapped[node_id]
        mapping_error = float(row["total_mapping_offset_um"])
        if not math.isfinite(mapping_error):
            raise RuntimeError(f"non-finite Import3D mapping error for SWC node {node_id}")
        mapping_rows.append({
            "swc_node_id": node_id,
            "roles": ";".join(site_roles[node_id]),
            "section_name": row["section_name"],
            "normalized_x": float(row["normalized_x"]),
            "mapping_error_um": mapping_error,
            "geometry_offset_um": float(row["geometry_offset_um"]),
            "segment_centre_offset_um": float(row["nearest_centre_offset_um"]),
        })

    amsn_source_results = []
    for source_name in SOURCE_NAMES:
        source_id = injection_by_name[source_name]
        input_r, rows = reference.solve_amsn(
            cable, cable_mapping, source_id, list(probe_by_name.values())
        )
        amsn_source_results.append({
            "source": source_name,
            "source_swc_id": source_id,
            "input_resistance_mohm": float(input_r),
            "probe_responses": {
                probe_name: {
                    "swc_id": probe_by_name[probe_name],
                    "transfer_resistance_mohm": float(rows[probe_by_name[probe_name]][1]),
                    "voltage_ratio": float(rows[probe_by_name[probe_name]][2]),
                }
                for probe_name in PROBE_NAMES
            },
        })

    soma_source_id = injection_by_name["soma"]
    neuron_probe_segments = {
        node_id: mapped[node_id]["nearest_segment"]
        for node_id in set(probe_by_name.values()) | {soma_source_id}
    }
    neuron_voltage, steady_residual, _ = reference.solve_neuron(
        mapped[soma_source_id]["nearest_segment"],
        neuron_probe_segments,
        [],
    )
    source_delta = neuron_voltage[soma_source_id] - reference.ELEAK_MV
    neuron_input_r = source_delta / reference.INJECTED_P_A * 1e3
    amsn_soma = next(row for row in amsn_source_results if row["source"] == "soma")
    neuron_comparison = []
    for probe_name in PROBE_NAMES:
        probe_id = probe_by_name[probe_name]
        neuron_delta = neuron_voltage[probe_id] - reference.ELEAK_MV
        neuron_ratio = neuron_delta / source_delta
        amsn_ratio = amsn_soma["probe_responses"][probe_name]["voltage_ratio"]
        relative_error = 100.0 * abs(amsn_ratio - neuron_ratio) / max(abs(neuron_ratio), 1e-30)
        neuron_comparison.append({
            "probe": probe_name,
            "probe_swc_id": probe_id,
            "neuron_voltage_mv": float(neuron_voltage[probe_id]),
            "neuron_voltage_ratio": float(neuron_ratio),
            "amsn_voltage_ratio": float(amsn_ratio),
            "ratio_relative_error_pct": float(relative_error),
        })

    current = [0j] * cable.n_compartments
    current[cable.index[cable_mapping[soma_source_id]]] = 1.0 + 0j
    ac_response = cable.solve_passive_frequency_response(1000.0, current)
    if not all(
        math.isfinite(float(value.real)) and math.isfinite(float(value.imag))
        for value in ac_response
    ):
        raise RuntimeError("non-finite 1 kHz AMSN passive frequency response")

    neuron_segment_count = sum(int(section.nseg) for section in sections)
    max_section_segment_um = max(float(section.L) / int(section.nseg) for section in sections)
    if max_section_segment_um > MAX_NEURON_SEGMENT_UM * 1.000001:
        raise RuntimeError(
            f"NEURON segment cap failed: {max_section_segment_um} um > {MAX_NEURON_SEGMENT_UM} um"
        )

    result = {
        "metadata": METADATA,
        "source_sha256": digest,
        "swc_record_count": summary.node_count,
        "swc_neurite_type_counts": {str(k): v for k, v in validated.neurite_type_counts.items()},
        "swc_branch_point_count": summary.branch_point_count,
        "swc_path_length_um": summary.total_path_length_um,
        "swc_estimated_membrane_area_um2": summary.estimated_membrane_area_um2,
        "three_point_soma_detected": validated.three_point_soma_detected,
        "amsn_full_node_compartments": cable.n_compartments,
        "amsn_unique_port_count": len(site_ids),
        "neuron_version": neuron.__version__,
        "neuron_section_count": len(sections),
        "neuron_segment_count": neuron_segment_count,
        "neuron_max_section_segment_um": max_section_segment_um,
        "neuron_steady_residual_mv": float(steady_residual),
        "neuron_soma_input_resistance_mohm": float(neuron_input_r),
        "source_placements": [
            {"name": name, "swc_id": node_id} for name, node_id in injections
        ],
        "probe_placements": [
            {"name": name, "swc_id": node_id} for name, node_id in probes
        ],
        "mapping": mapping_rows,
        "amsn_passive_dc": amsn_source_results,
        "soma_source_neuron_comparison": neuron_comparison,
        "ac_frequency_hz": 1000.0,
        "ac_response_is_finite": True,
        "scope": "passive linear RC only; not a complete axon reconstruction or population validation",
    }

    output = ROOT / "results" / "NMO_162186_holdout_preflight"
    output.mkdir(parents=True, exist_ok=True)
    (output / "preflight.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (output / "port_mapping.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(mapping_rows[0]))
        writer.writeheader()
        writer.writerows(mapping_rows)

    print(json.dumps({
        "neuromorpho_id": METADATA["neuromorpho_id"],
        "sha256": digest,
        "records": summary.node_count,
        "type_counts": validated.neurite_type_counts,
        "branches": summary.branch_point_count,
        "amsn_compartments": cable.n_compartments,
        "neuron_sections": len(sections),
        "neuron_segments": neuron_segment_count,
        "unique_ports": len(site_ids),
        "max_import3d_mapping_error_um": max(row["mapping_error_um"] for row in mapping_rows),
        "neuron_steady_residual_mv": float(steady_residual),
        "status": "PASS",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
