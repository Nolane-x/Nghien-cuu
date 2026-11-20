"""Non-rigorous scaling smoke check for the tree solver (not a benchmark suite)."""
from time import perf_counter
import numpy as np

from amsn.cable import CableCompartment, CableTree

for count in (1_000, 5_000, 10_000):
    compartments = [
        CableCompartment(str(i), 100e-6, 2e-6, None if i == 0 else str(i - 1))
        for i in range(count)
    ]
    start = perf_counter()
    tree = CableTree(compartments)
    built = perf_counter()
    voltage = np.full(count, -0.065)
    result = tree.step_passive(voltage, 1e-5)
    finished = perf_counter()
    print(
        f"n={count:>5} build={built - start:.4f}s "
        f"one_step={finished - built:.4f}s finite={np.isfinite(result).all()}"
    )
