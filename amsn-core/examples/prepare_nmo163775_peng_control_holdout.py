#!/usr/bin/env python3
"""Pin and preflight the NeuroMorpho NMO_163775 Peng mouse control morphology."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[1]
SWC = ROOT / "data" / "mouse" / "neuromorpho_peng" / "NMO_163775_18453_5766_x31719_y6139_semi_r.CNG.swc"
EXPECTED_NODE_COUNT = 4209
EXPECTED_TYPE_COUNTS = {1: 3, 2: 3602, 3: 306, 4: 298}
EXPECTED_SWC_SHA256 = "94eb448c2d70b6dfa78322df8a18013d0899e0908cd203b79c4a7a9a954dd00f"
EXPECTED_SEVEN_PORT_IDS = {1, 40, 144, 4180, 3926, 4104, 3948}
LABEL = "NMO_163775_PengControl"
SOURCE_URL = "https://neuromorpho.org/dableFiles/peng/CNG%20version/18453_5766_x31719_y6139-semi_r.CNG.swc"
METADATA_URL = "https://neuromorpho.org/neuron_info.jsp?neuron_name=18453_5766_x31719_y6139-semi_r"


def parse_swc_text(text: str) -> tuple[list[dict], dict[int, int]]:
    rows: list[dict] = []
    counts: Counter[int] = Counter()
    seen: set[int] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) != 7:
            raise ValueError(f"SWC line {line_number} has {len(parts)} fields, expected 7")
        try:
            node_id = int(parts[0])
            node_type = int(parts[1])
            x, y, z, radius = (float(value) for value in parts[2:6])
            parent = int(parts[6])
        except ValueError as exc:
            raise ValueError(f"SWC line {line_number} contains an invalid numeric field") from exc
        if node_id in seen:
            raise ValueError(f"duplicate SWC node ID {node_id}")
        if not np.isfinite([x, y, z, radius]).all() or radius <= 0:
            raise ValueError(f"SWC line {line_number} has a non-finite coordinate or invalid radius")
        seen.add(node_id)
        counts[node_type] += 1
        rows.append({
            "id": node_id, "type": node_type, "x": x, "y": y,
            "z": z, "radius": radius, "parent": parent,
        })
    if not rows:
        raise ValueError("SWC contains no numeric records")
    roots = [row for row in rows if row["parent"] == -1]
    if len(roots) != 1 or roots[0]["type"] != 1:
        raise ValueError(f"expected one soma root, observed {len(roots)} roots")
    missing = [row["id"] for row in rows if row["parent"] != -1 and row["parent"] not in seen]
    if missing:
        raise ValueError(f"SWC contains missing parent references: {missing[:10]}")
    observed = dict(sorted(counts.items()))
    return rows, observed


def parse_swc_records(text: str) -> tuple[list[dict], dict[int, int]]:
    """Parse and enforce the immutable NeuroMorpho source record/type counts."""
    rows, observed = parse_swc_text(text)
    if len(rows) != EXPECTED_NODE_COUNT:
        raise ValueError(f"SWC record count {len(rows)} != pinned {EXPECTED_NODE_COUNT}")
    if observed != EXPECTED_TYPE_COUNTS:
        raise ValueError(f"SWC neurite type counts {observed} != pinned {EXPECTED_TYPE_COUNTS}")
    return rows, observed


def parse_swc_records_for_test(text: str) -> tuple[list[dict], dict[int, int]]:
    """Expose generic structural parsing for small unit-test fixtures."""
    return parse_swc_text(text)


def main() -> None:
    if not SWC.is_file():
        raise FileNotFoundError(f"downloaded source SWC not found: {SWC}")
    payload = SWC.read_bytes()
    if len(payload) < 1000:
        raise RuntimeError(f"source SWC is unexpectedly small: {len(payload)} bytes")
    text = payload.decode("utf-8-sig")
    rows, type_counts = parse_swc_records(text)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SWC_SHA256:
        raise RuntimeError(f"SWC SHA-256 mismatch: {digest}")

    from amsn.provenance import validate_swc_morphology
    morphology_validation = validate_swc_morphology(
        SWC,
        expected_node_count=EXPECTED_NODE_COUNT,
        required_neurite_types=(1, 2, 3, 4),
        require_three_point_soma=True,
    )
    morphology = morphology_validation.morphology

    import neuron_cross_validation as reference
    import human_fine_mesh_passive_dc_audit as fine_audit
    import neuron
    reference.DATA = SWC
    reference.MAX_NEURON_SEGMENT_UM = 0.5
    reader, sections = reference.import_swc_with_neuron()
    injections, probes, mapped_sites = fine_audit.build_sites(morphology, reader, sections)
    port_node_ids = list(dict.fromkeys(node_id for _, node_id in injections + probes))
    if set(port_node_ids) != EXPECTED_SEVEN_PORT_IDS:
        raise RuntimeError(f"canonical seven-port IDs changed: {port_node_ids}")
    if len(port_node_ids) != 7:
        raise RuntimeError(f"expected seven unique retained ports, got {len(port_node_ids)}")

    source_ids = {name: node_id for name, node_id in injections}
    import human_prima_port_enrichment as port_enrichment
    _, _, q25_mapped = port_enrichment.build_sites(
        morphology, reader, sections, extra_probe_quantiles=(0.25,)
    )
    q25_ids = tuple(sorted(set(q25_mapped) - set(mapped_sites)))
    if len(q25_ids) != 2 or set(q25_ids).intersection(port_node_ids):
        raise RuntimeError(f"expected two distinct q25-only nodes, observed {q25_ids}")
    if set(source_ids) != {"soma", "basal_q75", "apical_q75"}:
        raise RuntimeError(f"unexpected source site set: {source_ids}")
    electrical_mapping = morphology.electrical_node_mapping()
    base = morphology.to_cable_tree()
    port_names = {
        node_id: f"swc_{electrical_mapping[node_id]}" for node_id in port_node_ids
    }
    ports = [base.index[port_names[node_id]] for node_id in port_node_ids]

    roles_by_node: dict[int, list[str]] = {node_id: [] for node_id in port_node_ids}
    for role, node_id in injections + probes:
        if role not in roles_by_node[node_id]:
            roles_by_node[node_id].append(role)
    neuron_segments = sum(int(section.nseg) for section in sections)
    max_segment_um = max(float(section.L) / int(section.nseg) for section in sections)
    if max_segment_um > 0.5 * 1.000001:
        raise RuntimeError(f"NEURON mesh cap exceeded: {max_segment_um} um")

    source_current = np.zeros(base.n_compartments, dtype=np.complex128)
    soma_node = source_ids["soma"]
    soma_electrical_name = f"swc_{electrical_mapping[soma_node]}"
    source_current[base.index[soma_electrical_name]] = 1.0 + 0.0j
    response = base.solve_passive_frequency_response(1000.0, source_current)
    if not np.isfinite(np.asarray(response)).all():
        raise RuntimeError("non-finite 1 kHz full-Hines passive response")

    output = ROOT / "results" / "NMO_163775_PengControl_holdout"
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "PASS",
        "label": LABEL,
        "source": {
            "neuromorpho_id": "NMO_163775",
            "cell_name": "18453_5766_x31719_y6139-semi_r",
            "archive": "Peng",
            "species": "mouse",
            "age_days": 56,
            "sex": "Male/Female",
            "experimental_condition": "Control",
            "primary_region": "neocortex",
            "secondary_region": "somatosensory",
            "tertiary_region": "layer 2-3",
            "cell_class": "principal cell, pyramidal, projection, Intratelencephalic (IT)",
            "structural_domains": ["dendrites", "soma", "axon"],
            "physical_integrity": "Dendrites & Axon Complete; morphological attributes: No Diameter",
            "protocol": "in vitro; whole mount",
            "staining": "green fluorescent protein",
            "slice_thickness_um": None,
            "reference_article": "Brain-wide single neuron reconstruction reveals morphological diversity in molecularly defined striatal, thalamic, cortical and claustral neuron types",
            "source_url": SOURCE_URL,
            "metadata_url": METADATA_URL,
            "source_sha256": digest,
            "source_bytes": len(payload),
        },
        "swc": {
            "record_count": len(rows),
            "type_counts": {str(key): value for key, value in sorted(type_counts.items())},
            "root_count": 1,
            "missing_parent_references": 0,
            "branch_point_count": morphology_validation.summary.branch_point_count,
            "total_path_length_um": morphology_validation.summary.total_path_length_um,
            "three_point_soma_detected": morphology_validation.three_point_soma_detected,
        },
        "neuron": {
            "version": neuron.__version__,
            "section_count": len(sections),
            "segment_count": neuron_segments,
            "maximum_segment_length_um": max_segment_um,
            "maximum_segment_length_cap_um": 0.5,
        },
        "amsn": {
            "electrical_compartment_count": base.n_compartments,
            "seven_unique_port_node_ids": port_node_ids,
            "q25_only_swc_node_ids": list(q25_ids),
            "source_node_ids": source_ids,
            "roles_by_node": {str(node): roles_by_node[node] for node in port_node_ids},
            "finite_1khz_passive_response": True,
            "port_mapping_rows": [
                {
                    "swc_node_id": int(node_id),
                    "section_name": site["section_name"],
                    "normalized_x": float(site["normalized_x"]),
                    "nearest_centre_offset_um": float(site["nearest_centre_offset_um"]),
                    "geometry_offset_um": float(site["geometry_offset_um"]),
                    "interpolation_lower_x": float(site["lower_x"]),
                    "interpolation_upper_x": float(site["upper_x"]),
                    "interpolation_upper_weight": float(site["interpolation_upper_weight"]),
                    "interpolation_endpoint_fallback": site.get("interpolation_endpoint_fallback"),
                }
                for node_id, site in sorted(mapped_sites.items())
            ],
        },
        "scientific_limits": [
            "The specimen is a mouse control morphology from the Peng archive, but it is a single cell and does not constitute a population.",
            "NeuroMorpho metadata marks dendrites and axon complete, but marks Morphological Attributes as No Diameter.",
            "This is a passive linear-RC numerical morphology holdout, not active-neuron or biological validation; stored SWC radii must not be interpreted as measured biological diameters.",
            "No active-channel mechanism, conductance fit or production default is changed.",
        ],
    }
    (output / "preflight.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    mapping_rows = []
    for node_id in port_node_ids:
        mapping_rows.append({
            "swc_node_id": node_id,
            "electrical_node_name": port_names[node_id],
            "electrical_index": base.index[port_names[node_id]],
            "roles": ";".join(roles_by_node[node_id]),
        })
    with (output / "port_mapping.csv").open("w", newline="", encoding="utf-8") as handle:
        import csv
        writer = csv.DictWriter(handle, fieldnames=list(mapping_rows[0]))
        writer.writeheader()
        writer.writerows(mapping_rows)
    print(json.dumps({
        "status": report["status"],
        "neuromorpho_id": "NMO_163775",
        "sha256": digest,
        "source_bytes": len(payload),
        "records": len(rows),
        "type_counts": type_counts,
        "electrical_compartments": base.n_compartments,
        "neuron_sections": len(sections),
        "neuron_segments": neuron_segments,
        "unique_ports": len(port_node_ids),
        "max_segment_um": max_segment_um,
        "preflight_json": str(output / "preflight.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
