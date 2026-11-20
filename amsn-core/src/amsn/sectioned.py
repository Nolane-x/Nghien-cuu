"""Section-based electrical discretization of piecewise-linear SWC trees.

The anatomical reconstruction remains a dense polyline. Electrical control
volumes are placed on that polyline, preserving branch/type boundaries and
integrating each original edge's path length, frustum area, and axial
resistance instead of replacing a bent chain with a straight chord.
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from math import ceil, hypot, pi, sqrt
from typing import Iterable

from .cable import CableCompartment, CableTree, PassiveParameters
from .discretization import electrotonic_length_um
from .morphology import SWCMorphology


def _positive_finite(name: str, value: float) -> float:
    value = float(value)
    if not (value > 0.0 and value < float("inf")):
        raise ValueError(f"{name} must be finite and positive")
    return value


@dataclass(frozen=True, slots=True)
class SectionedCableResult:
    """Electrical tree plus mappings and exact per-edge geometry integrals."""

    tree: CableTree
    swc_node_to_compartment: dict[int, str]
    swc_node_mapping_error_um: dict[int, float]
    edge_arc_length_m: dict[str, float]
    edge_electrotonic_length: dict[str, float]
    edge_axial_geometry_factor_m_inv: dict[str, float]
    section_count: int


def _section_paths(
    morphology: SWCMorphology,
    preserve_node_ids: set[int] | None = None,
) -> list[list[int]]:
    """Split at branch points, terminals, type transitions, and protected sites."""
    protected = preserve_node_ids or set()
    starts: list[int] = []
    for node_id, node in morphology.nodes.items():
        parent_id = node.parent_id
        parent_type_changes = (
            parent_id != -1
            and morphology.nodes[parent_id].neurite_type != node.neurite_type
        )
        if (
            node_id == morphology.root_id
            or len(morphology.children[node_id]) != 1
            or parent_type_changes
            or node_id in protected
        ):
            starts.append(node_id)

    sections: list[list[int]] = []
    for start_id in starts:
        start_type = morphology.nodes[start_id].neurite_type
        for child_id in morphology.children[start_id]:
            path = [start_id, child_id]
            current_id = child_id
            if (
                morphology.nodes[current_id].neurite_type != start_type
                or current_id in protected
            ):
                sections.append(path)
                continue

            while len(morphology.children[current_id]) == 1 and current_id not in protected:
                next_id = morphology.children[current_id][0]
                path.append(next_id)
                if (
                    morphology.nodes[next_id].neurite_type
                    != morphology.nodes[current_id].neurite_type
                    or next_id in protected
                ):
                    break
                current_id = next_id
            sections.append(path)
    return sections


def _path_geometry(
    morphology: SWCMorphology,
    path: list[int],
    *,
    reference_frequency_hz: float,
    axial_resistivity_ohm_m: float,
    specific_capacitance_f_m2: float,
) -> tuple[list[float], list[float]]:
    """Cumulative physical arc length and passive electrotonic coordinate."""
    cumulative_length = [0.0]
    cumulative_electrotonic = [0.0]
    for parent_id, child_id in zip(path, path[1:]):
        parent = morphology.nodes[parent_id]
        child = morphology.nodes[child_id]
        length = hypot(
            hypot(child.x_um - parent.x_um, child.y_um - parent.y_um),
            child.z_um - parent.z_um,
        )
        if length <= 0.0:
            raise ValueError(
                f"zero-length SWC edge between nodes {parent_id} and {child_id}"
            )
        cumulative_length.append(cumulative_length[-1] + length)
        cumulative_electrotonic.append(
            cumulative_electrotonic[-1]
            + electrotonic_length_um(
                length,
                2.0 * parent.radius_um,
                2.0 * child.radius_um,
                reference_frequency_hz,
                axial_resistivity_ohm_m,
                specific_capacitance_f_m2,
            )
        )
    return cumulative_length, cumulative_electrotonic


def _sample_positions(
    path: list[int],
    cumulative_length: list[float],
    cumulative_electrotonic: list[float],
    morphology: SWCMorphology,
    *,
    max_segment_length_um: float | None,
    max_electrotonic_length: float | None,
) -> list[float]:
    """Return sorted control-point arc positions satisfying both mesh bounds."""
    total_length = cumulative_length[-1]
    positions = [0.0, total_length]

    if max_segment_length_um is not None:
        n_physical = max(1, ceil(total_length / max_segment_length_um))
        positions.extend(
            total_length * i / n_physical for i in range(1, n_physical)
        )

    if max_electrotonic_length is not None:
        total_electrotonic = cumulative_electrotonic[-1]
        n_electrotonic = max(
            1, ceil(total_electrotonic / max_electrotonic_length)
        )
        for i in range(1, n_electrotonic):
            target = total_electrotonic * i / n_electrotonic
            edge_index = min(
                len(path) - 2,
                max(0, bisect_right(cumulative_electrotonic, target) - 1),
            )
            parent = morphology.nodes[path[edge_index]]
            child = morphology.nodes[path[edge_index + 1]]
            edge_e = (
                cumulative_electrotonic[edge_index + 1]
                - cumulative_electrotonic[edge_index]
            )
            q = (target - cumulative_electrotonic[edge_index]) / edge_e
            d0, d1 = 2.0 * parent.radius_um, 2.0 * child.radius_um
            if d0 == d1:
                fraction = q
            else:
                root0, root1 = sqrt(d0), sqrt(d1)
                root_at_q = root0 + q * (d1 - d0) / (root0 + root1)
                fraction = (root_at_q * root_at_q - d0) / (d1 - d0)
            fraction = min(1.0, max(0.0, fraction))
            edge_start = cumulative_length[edge_index]
            edge_length = cumulative_length[edge_index + 1] - edge_start
            positions.append(edge_start + edge_length * fraction)

    unique: list[float] = []
    tolerance = 1e-9
    for position in sorted(positions):
        if not unique or position - unique[-1] > tolerance:
            unique.append(position)
        elif abs(position - total_length) <= tolerance:
            unique[-1] = total_length
    unique[0] = 0.0
    unique[-1] = total_length
    return unique


def _edge_interval_metrics(
    morphology: SWCMorphology,
    path: list[int],
    cumulative_length: list[float],
    start_um: float,
    end_um: float,
    *,
    reference_frequency_hz: float,
    axial_resistivity_ohm_m: float,
    specific_capacitance_f_m2: float,
) -> tuple[float, float, float]:
    """Integrate lateral area, integral(ds/A), and electrotonic distance."""
    area_um2 = 0.0
    axial_factor_m_inv = 0.0
    electrotonic_length = 0.0

    for edge_index, (parent_id, child_id) in enumerate(zip(path, path[1:])):
        edge_start = cumulative_length[edge_index]
        edge_end = cumulative_length[edge_index + 1]
        piece_start = max(start_um, edge_start)
        piece_end = min(end_um, edge_end)
        if piece_end <= piece_start:
            continue

        edge_length = edge_end - edge_start
        parent = morphology.nodes[parent_id]
        child = morphology.nodes[child_id]
        f0 = (piece_start - edge_start) / edge_length
        f1 = (piece_end - edge_start) / edge_length
        radius0 = parent.radius_um + (child.radius_um - parent.radius_um) * f0
        radius1 = parent.radius_um + (child.radius_um - parent.radius_um) * f1
        piece_length = piece_end - piece_start

        area_um2 += pi * (radius0 + radius1) * hypot(
            piece_length, radius1 - radius0
        )
        radius0_m, radius1_m = radius0 * 1e-6, radius1 * 1e-6
        piece_length_m = piece_length * 1e-6
        axial_factor_m_inv += (
            piece_length_m / (pi * radius0_m * radius1_m)
        )
        electrotonic_length += electrotonic_length_um(
            piece_length,
            2.0 * radius0,
            2.0 * radius1,
            reference_frequency_hz,
            axial_resistivity_ohm_m,
            specific_capacitance_f_m2,
        )

    return area_um2, axial_factor_m_inv, electrotonic_length


def to_sectioned_cable_tree(
    morphology: SWCMorphology,
    *,
    max_segment_length_um: float | None = None,
    max_electrotonic_length: float | None = 0.1,
    reference_frequency_hz: float = 100.0,
    passive_parameters: PassiveParameters | None = None,
    preserve_node_ids: Iterable[int] = (),
    root_soma_area_um2: float | None = None,
) -> SectionedCableResult:
    """Convert a detailed SWC polyline into a smaller electrical cable tree.

    Original branch points, terminals, type transitions, and caller-selected
    stimulus/recording nodes are retained exactly. Intermediate unbranched
    SWC samples are merged into section arcs. Each electrical edge preserves
    the underlying polyline arc length and integrates each original tapered
    frustum for surface area and axial resistance. Bent morphology is never
    replaced with a straight chord between distant SWC points.

    The result remains a 1-D passive cable approximation. It does not create a
    3-D soma or branch-junction volume mesh.
    """
    if max_segment_length_um is not None:
        _positive_finite("max_segment_length_um", max_segment_length_um)
    if max_electrotonic_length is not None:
        _positive_finite("max_electrotonic_length", max_electrotonic_length)
    if max_segment_length_um is None and max_electrotonic_length is None:
        raise ValueError("at least one physical or electrotonic mesh limit is required")
    frequency = _positive_finite("reference_frequency_hz", reference_frequency_hz)
    parameters = passive_parameters or PassiveParameters()
    ri = parameters.axial_resistivity_ohm_m
    cm = parameters.specific_capacitance_f_m2

    protected = set(preserve_node_ids)
    unknown = protected - set(morphology.nodes)
    if unknown:
        raise ValueError(f"preserve_node_ids contains unknown SWC IDs: {sorted(unknown)[:8]}")

    root = morphology.nodes[morphology.root_id]
    has_multi_point_soma = any(
        node_id != morphology.root_id and node.neurite_type == 1
        for node_id, node in morphology.nodes.items()
    )
    if root_soma_area_um2 is not None:
        _positive_finite("root_soma_area_um2", root_soma_area_um2)
        if has_multi_point_soma:
            raise ValueError(
                "root_soma_area_um2 cannot be added to a multi-point soma"
            )

    sections = _section_paths(morphology, protected)
    point_meta: dict[str, tuple[float, int]] = {
        f"swc_{morphology.root_id}": (root.radius_um, root.neurite_type)
    }
    local_area_um2: dict[str, float] = {f"swc_{morphology.root_id}": 0.0}
    local_length_um: dict[str, float] = {f"swc_{morphology.root_id}": 0.0}
    parent_by_child: dict[str, str] = {}
    axial_by_child: dict[str, float] = {}
    arc_by_child: dict[str, float] = {}
    electro_by_child: dict[str, float] = {}
    swc_mapping: dict[int, str] = {morphology.root_id: f"swc_{morphology.root_id}"}
    mapping_error: dict[int, float] = {morphology.root_id: 0.0}

    def register(name: str, radius_um: float, neurite_type: int) -> None:
        existing = point_meta.get(name)
        if existing is not None:
            if abs(existing[0] - radius_um) > 1e-8 or existing[1] != neurite_type:
                raise ValueError(f"conflicting geometry for section control point {name}")
            return
        point_meta[name] = (radius_um, neurite_type)
        local_area_um2[name] = 0.0
        local_length_um[name] = 0.0

    for section_number, path in enumerate(sections):
        cumulative_length, cumulative_electrotonic = _path_geometry(
            morphology,
            path,
            reference_frequency_hz=frequency,
            axial_resistivity_ohm_m=ri,
            specific_capacitance_f_m2=cm,
        )
        positions = _sample_positions(
            path,
            cumulative_length,
            cumulative_electrotonic,
            morphology,
            max_segment_length_um=max_segment_length_um,
            max_electrotonic_length=max_electrotonic_length,
        )

        sample_names: list[str] = []
        for sample_index, position in enumerate(positions):
            vertex_index = bisect_left(cumulative_length, position)
            exact_vertex = None
            for candidate in (vertex_index - 1, vertex_index):
                if 0 <= candidate < len(path) and abs(
                    cumulative_length[candidate] - position
                ) <= 1e-8:
                    exact_vertex = candidate
                    break

            if exact_vertex is not None:
                node_id = path[exact_vertex]
                node = morphology.nodes[node_id]
                name = f"swc_{node_id}"
                radius_um = node.radius_um
                neurite_type = node.neurite_type
            else:
                edge_index = min(
                    len(path) - 2,
                    max(0, bisect_right(cumulative_length, position) - 1),
                )
                edge_start = cumulative_length[edge_index]
                edge_length = cumulative_length[edge_index + 1] - edge_start
                fraction = (position - edge_start) / edge_length
                parent = morphology.nodes[path[edge_index]]
                child = morphology.nodes[path[edge_index + 1]]
                radius_um = parent.radius_um + (
                    child.radius_um - parent.radius_um
                ) * fraction
                neurite_type = child.neurite_type
                name = f"section_{section_number}_{sample_index}"

            register(name, radius_um, neurite_type)
            sample_names.append(name)

        # Every original sample maps to its nearest electrical point along
        # this same section arc; protected sites and structural boundaries
        # are exact electrical nodes.
        for vertex_index, node_id in enumerate(path):
            arc_position = cumulative_length[vertex_index]
            insertion = bisect_left(positions, arc_position)
            candidates = [
                j for j in (insertion - 1, insertion)
                if 0 <= j < len(positions)
            ]
            nearest_index = min(
                candidates,
                key=lambda j: (abs(positions[j] - arc_position), positions[j]),
            )
            error = abs(positions[nearest_index] - arc_position)
            swc_mapping.setdefault(node_id, sample_names[nearest_index])
            mapping_error.setdefault(node_id, error)

        for sample_index, (start_um, end_um) in enumerate(
            zip(positions, positions[1:])
        ):
            if end_um <= start_um:
                raise ValueError("section mesh contains a non-positive interval")

            middle_um = 0.5 * (start_um + end_um)
            proximal_area, _, _ = _edge_interval_metrics(
                morphology, path, cumulative_length, start_um, middle_um,
                reference_frequency_hz=frequency,
                axial_resistivity_ohm_m=ri,
                specific_capacitance_f_m2=cm,
            )
            distal_area, _, _ = _edge_interval_metrics(
                morphology, path, cumulative_length, middle_um, end_um,
                reference_frequency_hz=frequency,
                axial_resistivity_ohm_m=ri,
                specific_capacitance_f_m2=cm,
            )
            _, axial_factor, electro_length = _edge_interval_metrics(
                morphology, path, cumulative_length, start_um, end_um,
                reference_frequency_hz=frequency,
                axial_resistivity_ohm_m=ri,
                specific_capacitance_f_m2=cm,
            )

            parent_name = sample_names[sample_index]
            child_name = sample_names[sample_index + 1]
            if child_name in parent_by_child:
                raise ValueError(f"electrical point {child_name} has multiple parents")
            parent_by_child[child_name] = parent_name
            local_area_um2[parent_name] += proximal_area
            local_area_um2[child_name] += distal_area
            half_length = 0.5 * (end_um - start_um)
            local_length_um[parent_name] += half_length
            local_length_um[child_name] += half_length
            axial_by_child[child_name] = axial_factor
            arc_by_child[child_name] = (end_um - start_um) * 1e-6
            electro_by_child[child_name] = electro_length

    if set(swc_mapping) != set(morphology.nodes):
        missing = sorted(set(morphology.nodes) - set(swc_mapping))
        raise ValueError(f"section decomposition did not map all SWC nodes: {missing[:8]}")

    root_name = f"swc_{morphology.root_id}"
    if root_soma_area_um2 is not None:
        local_area_um2[root_name] += root_soma_area_um2
    elif root.neurite_type == 1 and not has_multi_point_soma:
        local_area_um2[root_name] += 4.0 * pi * root.radius_um**2

    compartments: list[CableCompartment] = []
    for name, (radius_um, _neurite_type) in point_meta.items():
        effective_length = local_length_um[name]
        if effective_length <= 0.0:
            effective_length = 2.0 * radius_um
        area = local_area_um2[name]
        if area <= 0.0:
            raise ValueError(f"electrical control point {name} has no membrane area")
        compartments.append(CableCompartment(
            name=name,
            length_m=effective_length * 1e-6,
            diameter_m=2.0 * radius_um * 1e-6,
            parent=parent_by_child.get(name),
            membrane_area_m2=area * 1e-12,
            axial_geometry_factor_m_inv=axial_by_child.get(name),
        ))

    tree = CableTree(compartments, parameters=parameters)
    return SectionedCableResult(
        tree=tree,
        swc_node_to_compartment=swc_mapping,
        swc_node_mapping_error_um=mapping_error,
        edge_arc_length_m=arc_by_child,
        edge_electrotonic_length=electro_by_child,
        edge_axial_geometry_factor_m_inv=axial_by_child,
        section_count=len(sections),
    )
