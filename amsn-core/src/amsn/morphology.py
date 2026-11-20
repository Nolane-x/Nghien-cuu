"""Strict SWC parsing, geometry summaries and vertex-centred cable conversion.

SWC edges are interpreted as tapered conical frusta. The converter partitions
frustum membrane area between endpoint control volumes, optionally subdivides
long edges, and supplies the exact axial-resistance integral for a linearly
tapered circular segment. The result is a one-dimensional cable approximation,
not a three-dimensional soma, branch-junction or spine mesh.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from math import pi, sqrt
from typing import Iterable


@dataclass(frozen=True, slots=True)
class SWCNode:
    node_id: int
    neurite_type: int
    x_um: float
    y_um: float
    z_um: float
    radius_um: float
    parent_id: int


class MorphologyError(ValueError):
    """Raised when an SWC file is structurally invalid."""


@dataclass(frozen=True, slots=True)
class NeuroMorphoSomaNormalization:
    """Detected NeuroMorpho three-point soma and Import3D wire attachments."""

    root_id: int
    soma_node_ids: tuple[int, ...]
    wire_attachment_node_ids: tuple[int, ...]
    wire_attachment_lengths_um: dict[int, float]
    root_soma_area_um2: float


@dataclass(frozen=True)
class MorphologySummary:
    node_count: int
    edge_count: int
    root_count: int
    branch_point_count: int
    total_path_length_um: float
    estimated_membrane_area_um2: float
    neurite_length_by_type_um: dict[int, float]


class SWCMorphology:
    def __init__(self, nodes: Iterable[SWCNode]):
        rows = list(nodes)
        if not rows:
            raise MorphologyError("SWC morphology is empty")
        ids = [n.node_id for n in rows]
        if len(ids) != len(set(ids)):
            raise MorphologyError("SWC contains duplicate node IDs")
        self.nodes = {n.node_id: n for n in rows}
        self.children: dict[int, list[int]] = {n.node_id: [] for n in rows}
        roots: list[int] = []
        for node in rows:
            if node.radius_um <= 0:
                raise MorphologyError(f"node {node.node_id}: radius must be > 0")
            if not all(map(lambda x: x == x and abs(x) != float("inf"),
                           (node.x_um, node.y_um, node.z_um, node.radius_um))):
                raise MorphologyError(f"node {node.node_id}: coordinates/radius must be finite")
            if node.parent_id == -1:
                roots.append(node.node_id)
            else:
                if node.parent_id not in self.nodes:
                    raise MorphologyError(
                        f"node {node.node_id}: missing parent {node.parent_id}"
                    )
                if node.parent_id == node.node_id:
                    raise MorphologyError(f"node {node.node_id}: self-parent cycle")
                self.children[node.parent_id].append(node.node_id)
        if len(roots) != 1:
            raise MorphologyError(f"expected exactly one root, found {len(roots)}")
        self.root_id = roots[0]
        self._validate_connected_acyclic()

    @classmethod
    def from_file(cls, path: str | Path) -> "SWCMorphology":
        return cls.from_text(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_text(cls, text: str) -> "SWCMorphology":
        nodes: list[SWCNode] = []
        for line_number, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) != 7:
                raise MorphologyError(
                    f"line {line_number}: expected 7 fields, got {len(fields)}"
                )
            try:
                node_id = int(fields[0])
                neurite_type = int(fields[1])
                x, y, z, radius = map(float, fields[2:6])
                parent_id = int(fields[6])
            except ValueError as exc:
                raise MorphologyError(f"line {line_number}: invalid numeric field") from exc
            if node_id < 0:
                raise MorphologyError(f"line {line_number}: node ID must be non-negative")
            nodes.append(SWCNode(node_id, neurite_type, x, y, z, radius, parent_id))
        return cls(nodes)

    def _validate_connected_acyclic(self) -> None:
        # Use an explicit stack: real reconstructions can contain many
        # thousands of SWC points, so recursive DFS can hit Python's recursion
        # limit even when the morphology is a valid simple chain.
        visited: set[int] = set()
        stack = [self.root_id]
        while stack:
            node_id = stack.pop()
            if node_id in visited:
                raise MorphologyError(f"cycle or repeated traversal detected at node {node_id}")
            visited.add(node_id)
            stack.extend(self.children[node_id])

        if len(visited) != len(self.nodes):
            disconnected = sorted(set(self.nodes) - visited)
            raise MorphologyError(f"disconnected nodes or cycles: {disconnected[:8]}")


    def detect_neuromorpho_three_point_soma(
        self, *, length_tolerance: float = 0.01
    ) -> NeuroMorphoSomaNormalization | None:
        """Detect the exact three-point spherical soma convention used by Import3D.

        The three soma points must be the first three SWC rows; the two
        non-root points must be direct root children without children of their
        own; their diameters must match; and the sum of their distances from
        the root must be within 1% of the soma diameter. Long, unbranched
        same-type neurite roots attached to this soma are identified as
        zero-resistance wire attachments, mirroring Import3D's section.first
        rule. All source SWC data remain unchanged.
        """
        if not (0.0 < length_tolerance < 1.0):
            raise ValueError("length_tolerance must be between 0 and 1")
        ordered_ids = list(self.nodes)
        soma_ids = [
            node_id for node_id in ordered_ids
            if self.nodes[node_id].neurite_type == 1
        ]
        if len(soma_ids) != 3 or ordered_ids[:3] != soma_ids:
            return None

        root_id = self.root_id
        if soma_ids[0] != root_id:
            return None
        root = self.nodes[root_id]
        other_soma_ids = soma_ids[1:]
        if any(
            self.nodes[node_id].parent_id != root_id
            or self.children[node_id]
            for node_id in other_soma_ids
        ):
            return None

        radii = [self.nodes[node_id].radius_um for node_id in soma_ids]
        if max(radii) - min(radii) > max(radii) * 1e-12:
            return None

        outline_length_um = 0.0
        for node_id in other_soma_ids:
            node = self.nodes[node_id]
            outline_length_um += sqrt(
                (node.x_um-root.x_um)**2
                + (node.y_um-root.y_um)**2
                + (node.z_um-root.z_um)**2
            )
        diameter_um = 2.0 * root.radius_um
        if abs(outline_length_um / diameter_um - 1.0) >= length_tolerance:
            return None

        wire_ids: list[int] = []
        wire_lengths: dict[int, float] = {}
        for soma_id in soma_ids:
            parent = self.nodes[soma_id]
            for child_id in self.children[soma_id]:
                child = self.nodes[child_id]
                if child.neurite_type == 1:
                    continue

                # Import3D marks a soma-connected section as a wire when its
                # same-type unbranched section extends for more than one edge.
                current_id = child_id
                same_type_edges = 0
                while len(self.children[current_id]) == 1:
                    next_id = self.children[current_id][0]
                    next_node = self.nodes[next_id]
                    if next_node.neurite_type != child.neurite_type:
                        break
                    same_type_edges += 1
                    current_id = next_id

                if same_type_edges > 1:
                    wire_ids.append(child_id)
                    wire_lengths[child_id] = sqrt(
                        (child.x_um-parent.x_um)**2
                        + (child.y_um-parent.y_um)**2
                        + (child.z_um-parent.z_um)**2
                    )

        return NeuroMorphoSomaNormalization(
            root_id=root_id,
            soma_node_ids=tuple(soma_ids),
            wire_attachment_node_ids=tuple(wire_ids),
            wire_attachment_lengths_um=wire_lengths,
            root_soma_area_um2=4.0 * pi * root.radius_um**2,
        )

    def electrical_node_mapping(
        self, *, normalize_neuromorpho_soma: bool = True
    ) -> dict[int, int]:
        """Map SWC IDs to electrical vertices while preserving source geometry."""
        mapping = {node_id: node_id for node_id in self.nodes}
        if normalize_neuromorpho_soma:
            info = self.detect_neuromorpho_three_point_soma()
            if info is not None:
                for node_id in info.soma_node_ids:
                    mapping[node_id] = info.root_id
                for node_id in info.wire_attachment_node_ids:
                    mapping[node_id] = info.root_id
        return mapping

    def to_cable_tree(self, max_segment_length_um: float | None = None,
                      root_soma_area_um2: float | None = None,
                      normalize_neuromorpho_soma: bool = True):
        """Convert an SWC tree into a node-centred passive cable tree.

        Each SWC edge is optionally split into shorter straight frusta. Every
        generated point becomes an electrical node. Frustum surface area is
        partitioned between its endpoint nodes; the root receives a spherical
        soma-area estimate unless an explicit area is supplied. Axial
        resistance uses the exact integral for a linearly tapered frustum,
        R = rho * L / (pi * r0 * r1).

        This is an explicit 1-D cable approximation, not a 3-D soma/branch
        junction mesh. SWC coordinates are assumed to be micrometres and
        radii are assumed to be micrometres as specified by SWC convention.
        """
        from math import ceil
        from .cable import CableCompartment, CableTree
        from .units import um_to_m

        if max_segment_length_um is not None and (
                not (max_segment_length_um > 0)
                or not (max_segment_length_um < float("inf"))):
            raise ValueError("max_segment_length_um must be finite and positive")
        root = self.nodes[self.root_id]
        has_multi_point_soma = any(
            node_id != self.root_id and node.neurite_type == 1
            for node_id, node in self.nodes.items()
        )
        soma_info = (
            self.detect_neuromorpho_three_point_soma()
            if normalize_neuromorpho_soma else None
        )
        if root_soma_area_um2 is not None and has_multi_point_soma:
            raise ValueError(
                "root_soma_area_um2 cannot be supplied with a multi-point soma; "
                "the source soma geometry already defines its surface"
            )
        if root_soma_area_um2 is not None and (
                not (root_soma_area_um2 > 0)
                or not (root_soma_area_um2 < float("inf"))):
            raise ValueError("root_soma_area_um2 must be finite and positive")

        electrical_map = self.electrical_node_mapping(
            normalize_neuromorpho_soma=normalize_neuromorpho_soma
        )
        # Collapse soma outline points and zero-resistance stem connectors
        # into the single spherical soma electrical vertex.
        points: dict[int, tuple[float, float, float, float, int | None]] = {}
        for node_id, node in self.nodes.items():
            electrical_id = electrical_map[node_id]
            if electrical_id == self.root_id and node_id != self.root_id:
                continue
            parent_id = (
                None if node.parent_id == -1
                else electrical_map[node.parent_id]
            )
            points[electrical_id] = (
                node.x_um, node.y_um, node.z_um, node.radius_um, parent_id
            )

        edge_rows: list[tuple[int, int, float, float, float]] = []
        next_id = max(self.nodes) + 1
        stack = [self.root_id]
        while stack:
            parent_id = stack.pop()
            parent = self.nodes[parent_id]
            children = self.children[parent_id]
            for child_id in children:
                child = self.nodes[child_id]
                electrical_parent_id = electrical_map[parent_id]
                electrical_child_id = electrical_map[child_id]
                if electrical_parent_id == electrical_child_id:
                    stack.append(child_id)
                    continue
                dx, dy, dz = (child.x_um - parent.x_um,
                              child.y_um - parent.y_um,
                              child.z_um - parent.z_um)
                edge_length = sqrt(dx * dx + dy * dy + dz * dz)
                if edge_length <= 0:
                    raise MorphologyError(
                        f"zero-length edge between SWC nodes {parent_id} and {child_id}"
                    )
                n_parts = (1 if max_segment_length_um is None else
                           max(1, ceil(edge_length / max_segment_length_um)))
                previous_id = electrical_parent_id
                previous_radius = parent.radius_um
                for part in range(1, n_parts + 1):
                    fraction = part / n_parts
                    current_radius = (parent.radius_um
                                      + (child.radius_um - parent.radius_um) * fraction)
                    if part == n_parts:
                        current_id = child_id
                    else:
                        current_id = next_id
                        next_id += 1
                        points[current_id] = (
                            parent.x_um + dx * fraction,
                            parent.y_um + dy * fraction,
                            parent.z_um + dz * fraction,
                            current_radius,
                            previous_id,
                        )
                    part_length = edge_length / n_parts
                    edge_rows.append((previous_id, current_id, part_length,
                                      previous_radius, current_radius))
                    # Keep the original child's true parent; its electrical
                    # parent is the final synthetic point on this edge.
                    if current_id == child_id:
                        points[current_id] = (
                            child.x_um, child.y_um, child.z_um,
                            child.radius_um, previous_id,
                        )
                    previous_id = current_id
                    previous_radius = current_radius
                stack.append(child_id)

        membrane_area_um2 = {node_id: 0.0 for node_id in points}
        local_length_um = {node_id: 0.0 for node_id in points}
        axial_factor_m_inv: dict[int, float] = {}
        for parent_id, child_id, length_um, r0_um, r1_um in edge_rows:
            r_mid = 0.5 * (r0_um + r1_um)
            half_length = 0.5 * length_um
            proximal_area = pi * (r0_um + r_mid) * sqrt(
                half_length * half_length + (r_mid - r0_um) ** 2
            )
            distal_area = pi * (r_mid + r1_um) * sqrt(
                half_length * half_length + (r1_um - r_mid) ** 2
            )
            membrane_area_um2[parent_id] += proximal_area
            membrane_area_um2[child_id] += distal_area
            local_length_um[parent_id] += half_length
            local_length_um[child_id] += half_length
            # Integral ds / A(s) for a linearly tapered circular frustum.
            r0_m, r1_m, length_m = map(um_to_m, (r0_um, r1_um, length_um))
            axial_factor_m_inv[child_id] = length_m / (pi * r0_m * r1_m)

        if soma_info is not None:
            membrane_area_um2[self.root_id] += soma_info.root_soma_area_um2
        elif root_soma_area_um2 is not None:
            membrane_area_um2[self.root_id] += root_soma_area_um2
        elif root.neurite_type == 1 and not has_multi_point_soma:
            membrane_area_um2[self.root_id] += 4.0 * pi * root.radius_um**2

        compartments = []
        for node_id, (x, y, z, radius, parent_id) in points.items():
            effective_length = local_length_um[node_id]
            if effective_length <= 0:
                # A morphology containing only the root still needs a valid
                # representative control-volume length for CableCompartment.
                effective_length = 2.0 * radius
            compartments.append(CableCompartment(
                name=f"swc_{node_id}",
                length_m=um_to_m(effective_length),
                diameter_m=um_to_m(2.0 * radius),
                parent=None if parent_id is None else f"swc_{parent_id}",
                membrane_area_m2=um_to_m(1.0) ** 2 * membrane_area_um2[node_id],
                axial_geometry_factor_m_inv=axial_factor_m_inv.get(node_id),
            ))
        return CableTree(compartments)

    def summary(self) -> MorphologySummary:
        total_length = 0.0
        root = self.nodes[self.root_id]
        has_multi_point_soma = any(
            node_id != self.root_id and node.neurite_type == 1
            for node_id, node in self.nodes.items()
        )
        area = (
            4.0 * pi * root.radius_um**2
            if root.neurite_type == 1 and not has_multi_point_soma else 0.0
        )
        by_type: dict[int, float] = {}
        for node in self.nodes.values():
            if node.node_id == self.root_id:
                continue
            parent = self.nodes[node.parent_id]
            dx = node.x_um - parent.x_um
            dy = node.y_um - parent.y_um
            dz = node.z_um - parent.z_um
            length = sqrt(dx * dx + dy * dy + dz * dz)
            total_length += length
            by_type[node.neurite_type] = by_type.get(node.neurite_type, 0.0) + length
            r1, r2 = parent.radius_um, node.radius_um
            slant = sqrt(length * length + (r2 - r1) ** 2)
            area += pi * (r1 + r2) * slant
        # Soma stems are not neurite bifurcations.
        branch_points = sum(
            1 for node_id, kids in self.children.items()
            if self.nodes[node_id].neurite_type != 1 and len(kids) >= 2
        )
        return MorphologySummary(
            node_count=len(self.nodes),
            edge_count=len(self.nodes) - 1,
            root_count=1,
            branch_point_count=branch_points,
            total_path_length_um=total_length,
            estimated_membrane_area_um2=area,
            neurite_length_by_type_um=dict(sorted(by_type.items())),
        )
