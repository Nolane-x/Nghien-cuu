"""Optional apical/basal quantile probe enrichment for the human PRIMA audit.

The established seven-port mapper remains the default. This module adds only
named output probes at additional path-distance quantiles and maps them to
Import3D segment coordinates without changing the original source locations.
"""
from __future__ import annotations

import numpy as np

import human_fine_mesh_passive_dc_audit as fine_audit
import neuron_cross_validation as reference
from amsn.ports import path_distances_um, quantile_node


def build_sites(
    morphology,
    reader,
    sections,
    *,
    extra_probe_quantiles: tuple[float, ...] = (0.25, 0.75),
):
    """Extend the canonical matched port set, preserving shared q75 sources."""
    quantiles = tuple(float(value) for value in extra_probe_quantiles)
    if not quantiles:
        return fine_audit.build_sites(morphology, reader, sections)
    if any(not np.isfinite(q) or not 0.0 < q < 1.0 for q in quantiles):
        raise ValueError("extra probe quantiles must be finite and strictly between 0 and 1")
    labels = [f"q{round(q * 100):02d}" for q in quantiles]
    if len(set(labels)) != len(labels) or {"q50", "q90"}.intersection(labels):
        raise ValueError("extra probe quantiles collide with existing probe labels")

    injections, probes, mapped = fine_audit.build_sites(morphology, reader, sections)
    distances = path_distances_um(morphology)
    source_ids = dict(injections)
    if (
        quantile_node(morphology, distances, 3, 0.75) != source_ids["basal_q75"]
        or quantile_node(morphology, distances, 4, 0.75) != source_ids["apical_q75"]
    ):
        raise RuntimeError("quantile helper disagrees with the canonical q75 source nodes")

    extra_probes = []
    for quantile, label in zip(quantiles, labels):
        extra_probes.extend((
            (f"basal_{label}", quantile_node(morphology, distances, 3, quantile)),
            (f"apical_{label}", quantile_node(morphology, distances, 4, quantile)),
        ))

    section_by_name = {section.name(): section for section in sections}
    for node_id in sorted({node_id for _, node_id in extra_probes} - set(mapped)):
        nearest, total, geometry, centre, section_name, normalized = (
            reference.locate_neuron_segment(
                reader, section_by_name, morphology.nodes[node_id]
            )
        )
        section = section_by_name[section_name]
        segments = list(section)
        xs = np.array([float(segment.x) for segment in segments])
        insertion = int(np.searchsorted(xs, normalized))
        lower, upper = insertion - 1, insertion
        if lower < 0 or upper >= len(segments):
            raise RuntimeError(
                f"SWC node {node_id} at x={normalized:.9f} is outside "
                "the segment-centre interpolation interval"
            )
        x0, x1 = float(xs[lower]), float(xs[upper])
        if not (x0 <= normalized <= x1) or x1 <= x0:
            raise RuntimeError(
                f"invalid interpolation bracket for SWC node {node_id}: "
                f"{x0} <= {normalized} <= {x1}"
            )
        mapped[node_id] = {
            "nearest_segment": nearest,
            "section": section,
            "section_name": section_name,
            "normalized_x": float(normalized),
            "lower_segment": segments[lower],
            "upper_segment": segments[upper],
            "lower_x": x0,
            "upper_x": x1,
            "interpolation_upper_weight": float((normalized - x0) / (x1 - x0)),
            "total_mapping_offset_um": float(total),
            "geometry_offset_um": float(geometry),
            "nearest_centre_offset_um": float(centre),
        }

    return injections, probes + extra_probes, mapped
