#!/usr/bin/env python3
"""Pin q25-aware port identities and Import3D mappings on two independent holdouts.

This is a preflight only. It does not run PRIMA transient sweeps or alter
production defaults. The two specimens retain separate metadata and limits.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = Path(__file__).resolve().parent
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

import neuron_cross_validation as reference
import replay_nmo03524_prima_7v9port as jacobs
import replay_nmo162186_prima_7v9port as allen
from amsn.morphology import SWCMorphology

MAX_NEURON_SEGMENT_UM = 0.5
EXPECTED_MORPHOLOGIES = (
    {
        "key": "NMO_03524_JacobsControl",
        "module": jacobs,
        "swc": ROOT / "data/human/neuromorpho_jacobs/1-5-3.CNG.swc",
        "records": 869,
        "sha256": "6850378b0c451fdcb4a2649c8d93999973a4a7078dcd032037887b4b39160748",
        "shared_ids": (1, 367, 583, 751, 866, 867, 868),
        "q25_ids": {"basal_q25": 272, "apical_q25": 864},
        "source_ids": {"soma": 1, "basal_q75": 583, "apical_q75": 867},
        "species": "human",
        "condition": "Control",
        "cell_class": "principal cell, pyramidal",
        "region": "occipital neocortex, Brodmann area 18",
        "dendrites_complete": False,
        "axon_complete": False,
        "integrity_note": "NeuroMorpho rates dendrites moderate and axon incomplete.",
        "source_url": "https://neuromorpho.org/dableFiles/jacobs/CNG%20version/1-5-3.CNG.swc",
        "metadata_url": "https://neuromorpho.org/neuron_info.jsp?neuron_name=1-5-3",
    },
    {
        "key": "NMO_162186_AllenL23",
        "module": allen,
        "swc": ROOT / "data/human/allen_cell_types/770307286_transformed.CNG.swc",
        "records": 7287,
        "sha256": "a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc",
        "shared_ids": (1, 515, 2261, 2304, 4180, 4262, 6608),
        "q25_ids": {"basal_q25": 2713, "apical_q25": 4488},
        "source_ids": {"soma": 1, "basal_q75": 2304, "apical_q75": 4262},
        "species": "human",
        "condition": "epilepsy surgical specimen",
        "cell_class": "principal / pyramidal, excitatory intratelencephalic (IT)",
        "region": "right middle temporal gyrus, neocortex, layer 2–3",
        "dendrites_complete": True,
        "axon_complete": False,
        "integrity_note": "NeuroMorpho marks dendrites complete and axon incomplete; do not label this a healthy-control cell.",
        "source_url": (
            "https://neuromorpho.org/dableFiles/allen%20cell%20types/CNG%20version/"
            "770307286_transformed.CNG.swc"
        ),
        "metadata_url": "https://neuromorpho.org/neuron_info.jsp?neuron_name=770307286_transformed",
    },
)
RESULT_STEM = "prima_q25_cross_morphology_boundary_preflight_2026-11-25"
RESULTS = ROOT / "results"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_port_manifest(
    morphology_key: str,
    common_ids: list[int] | tuple[int, ...],
    nine_ids: list[int] | tuple[int, ...],
    roles_by_node: dict[int, list[str]],
    source_ids: dict[str, int],
    expected_shared_ids: tuple[int, ...],
    expected_q25_ids: dict[str, int],
    expected_source_ids: dict[str, int],
    maximum_segment_um: float,
    segment_cap_um: float = MAX_NEURON_SEGMENT_UM,
) -> dict[str, int]:
    """Fail closed if shared ports, q25 identities, sources or mesh drift."""
    shared = set(int(x) for x in common_ids)
    nine = set(int(x) for x in nine_ids)
    require(len(shared) == 7, f"{morphology_key}: expected seven shared ports")
    require(shared == set(expected_shared_ids),
            f"{morphology_key}: shared SWC node IDs differ from the pinned map")
    require(len(nine) == 9 and shared.issubset(nine),
            f"{morphology_key}: nine-port layout does not contain the seven shared ports")
    extras = nine - shared
    require(len(extras) == 2, f"{morphology_key}: expected exactly two q25-only IDs")
    observed_q25: dict[str, int] = {}
    for node_id in extras:
        roles = roles_by_node.get(int(node_id), [])
        for role in roles:
            if role in ("basal_q25", "apical_q25"):
                require(role not in observed_q25,
                        f"{morphology_key}: duplicate role {role}")
                observed_q25[role] = int(node_id)
    require(observed_q25 == expected_q25_ids,
            f"{morphology_key}: q25 node identities differ: {observed_q25}")
    require(source_ids == expected_source_ids,
            f"{morphology_key}: source SWC node identities changed")
    require(math.isfinite(maximum_segment_um) and maximum_segment_um > 0.0,
            f"{morphology_key}: invalid maximum segment length")
    require(maximum_segment_um <= segment_cap_um + 1e-9,
            f"{morphology_key}: maximum segment length exceeds the common cap")
    return observed_q25


def _mapping_row(
    morphology_key: str,
    layout_name: str,
    layout: dict[str, Any],
    node_id: int,
) -> dict[str, Any]:
    mapping = layout["mapping"].get(int(node_id))
    require(mapping is not None, f"{morphology_key}: missing Import3D mapping for SWC node {node_id}")
    roles = layout["roles"].get(int(node_id), [])
    def number(name: str):
        value = mapping.get(name)
        return None if value is None else float(value)
    return {
        "morphology": morphology_key,
        "layout": layout_name,
        "port_count": int(layout["port_count"]),
        "swc_node_id": int(node_id),
        "roles": ";".join(roles),
        "section_name": mapping.get("section_name"),
        "normalized_x": number("normalized_x"),
        "mapping_offset_um": number("total_mapping_offset_um"),
        "geometry_offset_um": number("geometry_offset_um"),
        "nearest_segment_centre_offset_um": number("nearest_centre_offset_um"),
        "interpolation_lower_x": number("lower_x"),
        "interpolation_upper_x": number("upper_x"),
        "interpolation_upper_weight": number("interpolation_upper_weight"),
        "endpoint_fallback": mapping.get("interpolation_endpoint_fallback"),
    }


def _clear_neuron_sections() -> None:
    """Keep the two Import3D preflights isolated within one Python process."""
    for section in list(reference.h.allsec()):
        reference.h.delete_section(sec=section)


def _preflight_one(spec: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    swc = Path(spec["swc"])
    require(swc.is_file(), f"{spec['key']}: missing source SWC at {swc}")
    payload = swc.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    require(digest == spec["sha256"],
            f"{spec['key']}: SWC SHA-256 mismatch: {digest}")

    morphology = SWCMorphology.from_file(swc)
    require(len(morphology.nodes) == spec["records"],
            f"{spec['key']}: SWC record count mismatch")
    require(morphology.detect_neuromorpho_three_point_soma() is not None,
            f"{spec['key']}: expected recognized three-point soma")

    reference.DATA = swc
    reference.MAX_NEURON_SEGMENT_UM = MAX_NEURON_SEGMENT_UM
    reference.h.load_file("stdrun.hoc")
    reference.h.load_file("import3d.hoc")
    reader, sections = reference.import_swc_with_neuron()
    segment_count = sum(int(section.nseg) for section in sections)
    maximum_segment_um = max(float(section.L) / int(section.nseg) for section in sections)
    require(segment_count > 0 and maximum_segment_um <= MAX_NEURON_SEGMENT_UM + 1e-9,
            f"{spec['key']}: Import3D mesh does not respect the common cap")

    base_tree = morphology.to_cable_tree()
    layouts, common_ids, q25_extra_ids = spec["module"].build_port_layouts(
        morphology, reader, sections, base_tree
    )
    seven = layouts[7]
    nine = layouts[9]
    observed_q25 = validate_port_manifest(
        spec["key"],
        common_ids,
        nine["node_ids"],
        nine["roles"],
        nine["source_ids"],
        spec["shared_ids"],
        spec["q25_ids"],
        spec["source_ids"],
        maximum_segment_um,
    )
    require(set(int(x) for x in q25_extra_ids) == set(observed_q25.values()),
            f"{spec['key']}: q25 mapper return IDs do not match role map")

    # Verify each fixed injection site still produces a finite passive AC response.
    electrical_map = morphology.electrical_node_mapping()
    passive_checks = []
    for source_name in ("soma", "basal_q75", "apical_q75"):
        source_node = int(seven["source_ids"][source_name])
        source_name_in_tree = f"swc_{electrical_map[source_node]}"
        current = [0.0] * base_tree.n_compartments
        current[base_tree.index[source_name_in_tree]] = 1.0
        response = base_tree.solve_passive_frequency_response(1000.0, current)
        require(all(math.isfinite(float(value.real)) and math.isfinite(float(value.imag))
                    for value in response),
                f"{spec['key']}: non-finite 1-kHz passive response for {source_name}")
        passive_checks.append({"source": source_name, "source_swc_id": source_node,
                               "frequency_hz": 1000.0, "finite_response": True})

    mapping_rows = []
    for node_id in seven["node_ids"]:
        mapping_rows.append(_mapping_row(spec["key"], "seven_shared", seven, int(node_id)))
    for node_id in nine["node_ids"]:
        mapping_rows.append(_mapping_row(spec["key"], "nine_q25", nine, int(node_id)))

    port_roles = {
        str(int(node_id)): list(nine["roles"].get(int(node_id), []))
        for node_id in nine["node_ids"]
    }
    report = {
        "morphology": spec["key"],
        "neuromorpho_id": spec["key"].split("_")[0] + "_" + spec["key"].split("_")[1],
        "source_url": spec["source_url"],
        "metadata_url": spec["metadata_url"],
        "species": spec["species"],
        "experimental_condition": spec["condition"],
        "cell_class": spec["cell_class"],
        "region": spec["region"],
        "dendrites_complete": spec["dendrites_complete"],
        "axon_complete": spec["axon_complete"],
        "integrity_note": spec["integrity_note"],
        "swc_path": str(swc.relative_to(ROOT)),
        "swc_records": len(morphology.nodes),
        "swc_sha256": digest,
        "amsn_electrical_compartments": base_tree.n_compartments,
        "neuron_version": str(reference.neuron.__version__),
        "neuron_sections": len(sections),
        "neuron_segments": segment_count,
        "maximum_segment_length_um": maximum_segment_um,
        "segment_cap_um": MAX_NEURON_SEGMENT_UM,
        "shared_output_swc_node_ids": [int(x) for x in common_ids],
        "q25_only_swc_node_ids": observed_q25,
        "source_swc_node_ids": {k: int(v) for k, v in seven["source_ids"].items()},
        "nine_port_roles_by_swc_node_id": port_roles,
        "finite_passive_ac_checks": passive_checks,
        "status": "PASS",
    }
    return report, mapping_rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with path.open("r", newline="", encoding="utf-8") as handle:
        readback = list(csv.DictReader(handle))
    require(len(readback) == len(rows), f"CSV read-back row mismatch for {path}")


def main() -> None:
    morphology_reports = []
    all_mapping_rows = []
    for spec in EXPECTED_MORPHOLOGIES:
        _clear_neuron_sections()
        report, rows = _preflight_one(spec)
        morphology_reports.append(report)
        all_mapping_rows.extend(rows)

    require(len(morphology_reports) == 2 and all(x["status"] == "PASS" for x in morphology_reports),
            "both morphology preflights must pass")
    require(len(all_mapping_rows) == 32,
            f"mapping CSV rows {len(all_mapping_rows)} != expected 32")

    result = {
        "schema_version": 1,
        "status": "prima_q25_cross_morphology_boundary_preflight_passed",
        "common_mesh_cap_um": MAX_NEURON_SEGMENT_UM,
        "morphologies": morphology_reports,
        "exact_coverage": {
            "morphologies": len(morphology_reports),
            "q25_probe_mappings": 4,
            "mapping_csv_rows": len(all_mapping_rows),
            "shared_output_nodes": 14,
            "source_sites": 6,
            "finite_passive_ac_checks": 6,
        },
        "scientific_limits": [
            "This is a source, morphology, port-identity and Import3D mapping preflight; it does not run the finite-window decomposition.",
            "NMO_03524 is one human Control morphology with moderate dendritic integrity and incomplete axon.",
            "NMO_162186 is one human epilepsy surgical-specimen morphology with complete dendrites and incomplete axon; it is not a healthy-control cell.",
            "The two specimens are independent individual reconstructions, not a representative population.",
            "A common 0.5-um NEURON segment cap harmonizes this preflight's discretization setting only; it does not make the biological source conditions or morphologies interchangeable.",
            "No active-neuron or biological validation is claimed; full Hines remains canonical and no production defaults are changed.",
        ],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS / f"{RESULT_STEM}_report.json"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
                         encoding="utf-8")
    csv_path = RESULTS / f"{RESULT_STEM}_mapping.csv"
    write_csv(csv_path, all_mapping_rows)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
