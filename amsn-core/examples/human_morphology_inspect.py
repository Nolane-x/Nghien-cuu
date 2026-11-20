"""Inspect the attributed NeuroMorpho human L2-3 morphology fixture."""
from pathlib import Path

from amsn.morphology import SWCMorphology
from amsn.morphometrics import distal_cylinder_morphometrics


if __name__ == "__main__":
    path = Path(__file__).parents[1] / "data" / "human" / "1094_Mohan_etal_2015.CNG.swc"
    morphology = SWCMorphology.from_file(path)
    summary = morphology.summary()
    metrics = distal_cylinder_morphometrics(morphology)
    print("NeuroMorpho.Org NMO_290988 / 1094_Mohan_etal_2015")
    print("Human temporal cortex, middle temporal gyrus, BA21, layer 2-3")
    print("Soma + basal/apical dendrites; no axon; dendritic integrity: moderate")
    print(f"SWC points: {summary.node_count}")
    print(f"Neurite length: {metrics.neurite_length_um:.3f} um")
    print(f"Neurite surface (distal-cylinder): {metrics.neurite_surface_area_um2:.3f} um^2")
    print(f"Neurite volume (distal-cylinder): {metrics.neurite_volume_um3:.3f} um^3")
    print(f"Soma area (type-1 frusta): {metrics.soma_surface_area_um2:.3f} um^2")
    print(f"Bifurcations / stems: {metrics.bifurcation_count} / {metrics.stem_count}")
