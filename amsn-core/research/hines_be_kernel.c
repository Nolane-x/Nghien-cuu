#include <stdint.h>

/*
 * Exact-order vectorized wrapper for CableTree.step_linear.
 *
 * Arrays use row-major (compartment, RHS-column) layout.  For each RHS the
 * arithmetic and compartment traversal follow the Python Hines implementation:
 * RHS assembly, descending child elimination, root solve, ascending backsolve.
 * Compile without fast-math/FMA contraction so tiny residual parity is retained.
 */
void amsn_hines_be_step(
    int64_t n,
    int64_t columns,
    const double *pivot,
    const double *multiplier,
    const int64_t *parent,
    const double *axial_g,
    const double *c_over_dt,
    const double *leak_source,
    const double *previous,
    const double *current,
    double *following,
    double *work
) {
    int64_t i, column;
    for (i = 0; i < n; ++i) {
        const int64_t base = i * columns;
        for (column = 0; column < columns; ++column) {
            const int64_t k = base + column;
            work[k] = c_over_dt[i] * previous[k] + leak_source[i] + current[k];
        }
    }

    for (i = n - 1; i > 0; --i) {
        const int64_t p = parent[i];
        const int64_t child_base = i * columns;
        const int64_t parent_base = p * columns;
        const double m = multiplier[i];
        for (column = 0; column < columns; ++column) {
            work[parent_base + column] += m * work[child_base + column];
        }
    }

    for (column = 0; column < columns; ++column) {
        following[column] = work[column] / pivot[0];
    }

    for (i = 1; i < n; ++i) {
        const int64_t p = parent[i];
        const int64_t child_base = i * columns;
        const int64_t parent_base = p * columns;
        const double g = axial_g[i];
        const double d = pivot[i];
        for (column = 0; column < columns; ++column) {
            following[child_base + column] =
                (work[child_base + column] + g * following[parent_base + column]) / d;
        }
    }
}
