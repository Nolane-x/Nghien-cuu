"""Inspect a synthetic SWC and convert it to a passive cable approximation."""
from pathlib import Path

from amsn.morphology import SWCMorphology

sample = Path(__file__).with_name("synthetic_branching.swc")
morphology = SWCMorphology.from_file(sample)
summary = morphology.summary()
cable = morphology.to_cable_tree(max_segment_length_um=10.0)
print(summary)
print("Cable compartments:", cable.n_compartments)
print("Cable membrane area (um^2):", float(cable.area_m2.sum() * 1e12))
print("Cable axial links:", int((cable.axial_g_s > 0).sum()))
