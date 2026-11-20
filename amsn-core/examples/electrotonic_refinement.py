"""Demonstrate physical + d_lambda-like refinement on a synthetic SWC."""
from pathlib import Path

from amsn.discretization import refine_swc_morphology
from amsn.morphology import SWCMorphology


if __name__ == "__main__":
    swc_path = Path(__file__).parents[1] / "examples" / "synthetic_branching.swc"
    morphology = SWCMorphology.from_file(swc_path)
    refined = refine_swc_morphology(
        morphology,
        max_segment_length_um=20.0,
        max_electrotonic_length=0.1,
        reference_frequency_hz=100.0,
        axial_resistivity_ohm_m=0.7,
        specific_capacitance_f_m2=0.01,
    )
    cable = refined.to_cable_tree()

    original_summary = morphology.summary()
    refined_summary = refined.summary()
    print(f"original SWC nodes: {original_summary.node_count}")
    print(f"refined SWC nodes:  {refined_summary.node_count}")
    print(f"cable compartments: {cable.n_compartments}")
    print(f"path length before/after: {original_summary.total_path_length_um:.6f} / "
          f"{refined_summary.total_path_length_um:.6f} um")
    print("estimated membrane area before/after: "
          f"{original_summary.estimated_membrane_area_um2:.6f} / "
          f"{refined_summary.estimated_membrane_area_um2:.6f} um^2")
