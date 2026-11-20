"""Electrotonic and physical-length refinement for SWC cable morphologies.

The electrotonic criterion follows the high-frequency AC length-constant
approximation used by the NEURON d_lambda rule. It is a meshing heuristic,
not a substitute for spatial-convergence validation or a full 3-D model.
"""
from __future__ import annotations

from dataclasses import replace
from math import ceil, isfinite, pi, sqrt

from .morphology import SWCMorphology, SWCNode


def _positive_finite(name: str, value: float) -> float:
    value = float(value)
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def ac_length_constant_um(
    diameter_um: float,
    reference_frequency_hz: float = 100.0,
    axial_resistivity_ohm_m: float = 0.7,
    specific_capacitance_f_m2: float = 0.01,
) -> float:
    """Return the passive high-frequency AC length constant in micrometres.

    Parameters use SI except ``diameter_um``. The expression is
    ``lambda = sqrt(diameter / (4*pi*f*Ri*Cm))`` in metres, converted to µm.
    Defaults match AMSN's generic passive cable defaults (70 ohm*cm and
    1 µF/cm²); they are not fitted human-neuron parameters.
    """
    diameter_um = _positive_finite("diameter_um", diameter_um)
    frequency = _positive_finite("reference_frequency_hz", reference_frequency_hz)
    ri = _positive_finite("axial_resistivity_ohm_m", axial_resistivity_ohm_m)
    cm = _positive_finite("specific_capacitance_f_m2", specific_capacitance_f_m2)
    denominator = 4.0 * pi * frequency * ri * cm
    return 1_000.0 * sqrt(diameter_um / denominator)


def electrotonic_length_um(
    length_um: float,
    diameter_prox_um: float,
    diameter_dist_um: float,
    reference_frequency_hz: float = 100.0,
    axial_resistivity_ohm_m: float = 0.7,
    specific_capacitance_f_m2: float = 0.01,
) -> float:
    """Integrate ``dx/lambda_f`` along a linearly tapered cylindrical edge.

    Diameter is assumed to vary linearly with physical distance between the
    supplied endpoints. The integral is analytic; no numerical quadrature is
    used. The result is dimensionless (electrotonic lengths).
    """
    length = _positive_finite("length_um", length_um)
    d0 = _positive_finite("diameter_prox_um", diameter_prox_um)
    d1 = _positive_finite("diameter_dist_um", diameter_dist_um)
    frequency = _positive_finite("reference_frequency_hz", reference_frequency_hz)
    ri = _positive_finite("axial_resistivity_ohm_m", axial_resistivity_ohm_m)
    cm = _positive_finite("specific_capacitance_f_m2", specific_capacitance_f_m2)
    scale = sqrt(4.0 * pi * frequency * ri * cm) / 1_000.0
    return length * scale * (2.0 / (sqrt(d0) + sqrt(d1)))


def edge_subdivision_fractions(
    length_um: float,
    diameter_prox_um: float,
    diameter_dist_um: float,
    *,
    max_segment_length_um: float | None = None,
    max_electrotonic_length: float | None = 0.1,
    reference_frequency_hz: float = 100.0,
    axial_resistivity_ohm_m: float = 0.7,
    specific_capacitance_f_m2: float = 0.01,
) -> tuple[float, ...]:
    """Return sorted edge fractions satisfying both requested mesh limits.

    The output includes 0 and 1. Electrotonic cuts are placed at equal
    increments of the exact integrated ``dx/lambda`` coordinate; physical
    extent cuts are added and the two cut sets are unioned. Thus inserting
    either policy cannot invalidate the other policy's maximum bound.
    """
    length = _positive_finite("length_um", length_um)
    d0 = _positive_finite("diameter_prox_um", diameter_prox_um)
    d1 = _positive_finite("diameter_dist_um", diameter_dist_um)
    cuts = {0.0, 1.0}

    if max_segment_length_um is not None:
        max_length = _positive_finite("max_segment_length_um", max_segment_length_um)
        n_physical = max(1, ceil(length / max_length))
        cuts.update(i / n_physical for i in range(1, n_physical))

    if max_electrotonic_length is not None:
        max_electro = _positive_finite("max_electrotonic_length", max_electrotonic_length)
        total_electro = electrotonic_length_um(
            length, d0, d1, reference_frequency_hz,
            axial_resistivity_ohm_m, specific_capacitance_f_m2,
        )
        n_electro = max(1, ceil(total_electro / max_electro))
        delta_d = d1 - d0
        root0, root1 = sqrt(d0), sqrt(d1)
        denominator = root0 + root1
        for i in range(1, n_electro):
            q = i / n_electro
            if delta_d == 0.0:
                fraction = q
            else:
                root_at_q = root0 + q * delta_d / denominator
                diameter_at_q = root_at_q * root_at_q
                fraction = (diameter_at_q - d0) / delta_d
            # Guard against round-off at either endpoint.
            cuts.add(min(1.0, max(0.0, fraction)))

    return tuple(sorted(cuts))


def refine_swc_morphology(
    morphology: SWCMorphology,
    *,
    max_segment_length_um: float | None = None,
    max_electrotonic_length: float | None = 0.1,
    reference_frequency_hz: float = 100.0,
    axial_resistivity_ohm_m: float = 0.7,
    specific_capacitance_f_m2: float = 0.01,
) -> SWCMorphology:
    """Create a refined SWC tree without mutating the original reconstruction.

    Every original node ID is preserved. New IDs are allocated above the
    original maximum. Inserted coordinates and radii are linearly interpolated
    along each original edge, and original branch topology/type labels remain.
    """
    if max_segment_length_um is not None:
        _positive_finite("max_segment_length_um", max_segment_length_um)
    if max_electrotonic_length is not None:
        _positive_finite("max_electrotonic_length", max_electrotonic_length)
    # Validate the frequency and passive parameters even for a morphology
    # with no edges, so invalid configurations cannot silently pass.
    if max_electrotonic_length is not None:
        _positive_finite("reference_frequency_hz", reference_frequency_hz)
        _positive_finite("axial_resistivity_ohm_m", axial_resistivity_ohm_m)
        _positive_finite("specific_capacitance_f_m2", specific_capacitance_f_m2)

    root_id = morphology.root_id
    root = morphology.nodes[root_id]
    new_nodes: list[SWCNode] = [root]
    next_id = max(morphology.nodes) + 1
    stack = [root_id]

    while stack:
        parent_id = stack.pop()
        parent = morphology.nodes[parent_id]
        for child_id in morphology.children[parent_id]:
            child = morphology.nodes[child_id]
            dx = child.x_um - parent.x_um
            dy = child.y_um - parent.y_um
            dz = child.z_um - parent.z_um
            length = sqrt(dx * dx + dy * dy + dz * dz)
            if length <= 0.0:
                raise ValueError(
                    f"zero-length SWC edge between nodes {parent_id} and {child_id}"
                )
            fractions = edge_subdivision_fractions(
                length,
                2.0 * parent.radius_um,
                2.0 * child.radius_um,
                max_segment_length_um=max_segment_length_um,
                max_electrotonic_length=max_electrotonic_length,
                reference_frequency_hz=reference_frequency_hz,
                axial_resistivity_ohm_m=axial_resistivity_ohm_m,
                specific_capacitance_f_m2=specific_capacitance_f_m2,
            )
            previous_id = parent_id
            for fraction in fractions[1:-1]:
                new_nodes.append(SWCNode(
                    node_id=next_id,
                    neurite_type=child.neurite_type,
                    x_um=parent.x_um + dx * fraction,
                    y_um=parent.y_um + dy * fraction,
                    z_um=parent.z_um + dz * fraction,
                    radius_um=parent.radius_um
                    + (child.radius_um - parent.radius_um) * fraction,
                    parent_id=previous_id,
                ))
                previous_id = next_id
                next_id += 1
            new_nodes.append(replace(child, parent_id=previous_id))
            stack.append(child_id)

    return SWCMorphology(new_nodes)


def to_electrotonic_cable_tree(
    morphology: SWCMorphology,
    *,
    max_segment_length_um: float | None = None,
    max_electrotonic_length: float | None = 0.1,
    reference_frequency_hz: float = 100.0,
    axial_resistivity_ohm_m: float = 0.7,
    specific_capacitance_f_m2: float = 0.01,
    root_soma_area_um2: float | None = None,
):
    """Refine an SWC morphology and convert it to AMSN's passive cable tree."""
    refined = refine_swc_morphology(
        morphology,
        max_segment_length_um=max_segment_length_um,
        max_electrotonic_length=max_electrotonic_length,
        reference_frequency_hz=reference_frequency_hz,
        axial_resistivity_ohm_m=axial_resistivity_ohm_m,
        specific_capacitance_f_m2=specific_capacitance_f_m2,
    )
    return refined.to_cable_tree(root_soma_area_um2=root_soma_area_um2)
