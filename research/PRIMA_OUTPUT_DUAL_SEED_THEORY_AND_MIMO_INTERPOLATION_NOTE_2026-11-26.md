# PRIMA output-dual seeds: theory, MIMO interpolation and experimental limits

**Date:** 26 November 2026  
**Scope:** passive linear-RC cable trees; research-only output-aware basis prototype  
**Status:** derivation and literature synthesis for the q25/edge seed-transfer experiments

## 1. Why output-dual enrichment is mathematically natural

Let the passive cable model be

\[
C\dot v(t)+Gv(t)=Bi(t),\qquad y(t)=L^Tv(t),
\]

with symmetric positive-definite \(G,C\), fixed input selector \(B\) and observation selector \(L\). Its transfer matrix is

\[
H(s)=L^T(G+sC)^{-1}B.
\]

A conventional input-generated PRIMA basis contains input resolvent directions \((G+\sigma C)^{-1}B\). The research prototype keeps \(B\) fixed but optionally adds output-dual directions

\[
V\supseteq \operatorname{range}\big((G+\sigma C)^{-1}L\big).
\]

The prototype's implementation follows this order: all initial input-shift blocks are seeded first; output-dual blocks are then orthogonalized against the existing basis; all input and output blocks share the same round-robin Krylov-growth budget; final \(G_r,C_r,B_r\) are produced by the same congruence projection, while the output map is returned separately as \(L^TV\). See the source file at [experimental_prima_output_aware_basis.py](https://github.com/Nolane-x/Nghien-cuu/blob/research/prima-q25-spatial-heldout-generalization-2026-11-26/amsn-core/research/experimental_prima_output_aware_basis.py).

This changes the state approximation space, not the retained current-input selector. It therefore tests whether selected observation functionals can be approximated more accurately without adding those observation sites as current ports.

## 2. A transfer-row interpolation identity at positive-real shifts

For a real positive shift \(\sigma\ge 0\), define

\[
A_\sigma=G+\sigma C.
\]

Because \(G\) and \(C\) are symmetric, \(A_\sigma\) is symmetric. Assume a column \(\ell\) of \(L\) has its exact resolvent vector in the projection space:

\[
v_\ell=A_\sigma^{-1}\ell\in\operatorname{range}(V).
\]

Then \(v_\ell=Vz\) for some coordinate vector \(z\), and \(A_\sigma Vz=\ell\). The reduced transfer for that output row at \(s=\sigma\) is

\[
\begin{aligned}
H_{r,\ell}(\sigma)
&=\ell^TV(V^TA_\sigma V)^{-1}V^TB\\
&=z^TV^TA_\sigma V(V^TA_\sigma V)^{-1}V^TB\\
&=z^TV^TB\\
&=v_\ell^TB\\
&=\ell^TA_\sigma^{-1}B.
\end{aligned}
\]

Thus, in exact arithmetic, retaining the output-dual resolvent vector for an observation row gives exact interpolation of that input-to-output transfer row at the selected positive-real shift. If a seed vector is already in the existing span, orthogonalization may add no new column, but the vector is still represented by the basis. In finite precision, the result is subject to the configured orthogonalization tolerance and linear-solve accuracy.

This identity is conditional. It does not say that all unseeded rows improve, that errors are uniformly reduced across time windows, or that the reduced model matches the full transfer at every frequency.

## 3. Important shift interpretation

The code maps each declared value \(f\) to

\[
\sigma=2\pi f
\]

and solves \((G+\sigma C)x=r\). This is a **positive-real Laplace shift**. It is not the sinusoidal frequency point \(s=i2\pi f\). Therefore the study's “10K” suffix denotes the numerical value used to construct a positive-real resolvent seed; it must not be described as direct interpolation at a 10-kHz sinusoidal evaluation point.

Actual transient NRMSE and the finite-record DFT identity are evaluated separately by the fixed simulation/reference workflow. They do not change this interpretation of the seed shift.

## 4. Why passivity and the fixed input map matter

PRIMA's congruence projection is important because it preserves passivity for the passive circuit class under the standard assumptions; this is a central reason to keep the existing projection machinery rather than introducing an unrelated output fit. Freund's technical paper reviews PRIMA's passivity property and contrasts it with the additional reciprocity/block-structure preservation offered by SPRIM.

The current experiment preserves:
- the seven canonical current-input ports;
- the full-Hines reference;
- congruence projection of \(G,C\);
- the fixed timestep and source/window grid;
- the same 13 output observation coordinates in every seed schedule.

The output-dual vectors are state-space basis enrichments only. They are not new stimulation ports and do not alter the model's physical input matrix.

## 5. Relation to MIMO tangential rational-Krylov literature

The wider model-reduction literature treats multiple inputs and outputs with block or tangential rational-Krylov spaces. Relevant lines of work include adaptive selection of tangential directions and shifts, and structure-preserving interpolation for passive/port-Hamiltonian systems. The present prototype is a deliberately constrained passive-RC experiment: it fixes the primal input basis design and varies a small, predeclared set of output-dual coordinate directions.

It is not claimed to be a new general MIMO interpolation algorithm. The methodological contribution here is an auditable test of how a fixed seven-port, order-224 passive basis reallocates capacity when a small number of q25 or branch-edge observation directions are added.

## 6. Consequences for the q25-versus-edge experiment

The five schedules distinguish location from seed budget:

| Schedule | Requested output-dual coordinates | Role |
|---|---:|---|
| D0_none | 0 | production-basis parity baseline |
| Q25_BOTH_10K | 2 | q25-target enrichment |
| BASAL_EDGES_10K | 2 | basal edge enrichment |
| APICAL_EDGES_10K | 2 | apical edge enrichment |
| BOTH_EDGES_10K | 4 | higher-budget edge coverage |

The primary resource-matched comparisons are the three two-seed schedules. BOTH_EDGES_10K is deliberately retained as a higher-budget condition; an improvement relative to two-seed schedules cannot be attributed to location alone.

A row used to create the output-dual seeds is a seed-target readout for that schedule, not an unseeded transfer validation. Consequently the result analyzer applies a schedule-specific mask:
- q25 seeds: q25 rows are reported as seed-target accuracy; four edge rows are unseeded transfer;
- basal edge seeds: basal edge rows are seed targets; q25 and apical edge rows are unseeded transfer;
- apical edge seeds: apical edge rows are seed targets; q25 and basal edge rows are unseeded transfer;
- four edge seeds: all edge rows are seed targets; q25 rows are unseeded transfer.

The analysis also records requested seed-site count and the actual independent output-dual columns retained after orthogonalization, together with basis-build time and projected G/C condition numbers. This exposes both the approximation effect and the computational/conditioning cost.

## 7. What the experiments cannot establish

Even a fully passing archive establishes only numerical behavior for the declared passive linear-RC model family and four individual morphologies. It does not establish:
- biological population generalization;
- active membrane/channel behavior or action-potential fidelity;
- synaptic integration, plasticity, calcium signalling or metabolism;
- cognition, neural computation or biological equivalence;
- superiority of output-dual seeding at arbitrary untested locations or shifts.

Full Hines remains the canonical reference. The research prototype does not change production solver defaults.

## 8. Selected references

1. Roland W. Freund, **Structure-Preserving Model Order Reduction of RCL Circuit Equations**. Discusses PRIMA and SPRIM, including PRIMA's passivity property for general RCL circuit models. [PDF](https://www.math.ucdavis.edu/~freund/freund07.pdf).
2. V. Druskin, V. Simoncini and M. Zaslavsky, **Adaptive Tangential Interpolation in Rational Krylov Subspaces for MIMO Dynamical Systems**, SIAM Journal on Matrix Analysis and Applications. Develops adaptive direction selection for projection-based MIMO rational-Krylov reduction. [DOI: 10.1137/120898784](https://doi.org/10.1137/120898784).
3. S. Gugercin, R. V. Polyuga, C. Beattie and A. van der Schaft, **Structure-preserving tangential interpolation for model reduction of port-Hamiltonian systems**, Automatica 48(9), 2012, 1963–1974. [DOI: 10.1016/j.automatica.2012.05.052](https://doi.org/10.1016/j.automatica.2012.05.052).
4. G. Fanizza, J. Karlsson, A. Lindquist and R. Nagamune, **Passivity-preserving model reduction by analytic interpolation**, Linear Algebra and its Applications 425(2–3), 2007, 608–633. [DOI: 10.1016/j.laa.2007.03.014](https://doi.org/10.1016/j.laa.2007.03.014).
5. **An adaptive block tangential method for multi-input multi-output dynamical systems**, Journal of Computational and Applied Mathematics 358, 2019, 190–205. [DOI: 10.1016/j.cam.2019.03.014](https://doi.org/10.1016/j.cam.2019.03.014).

The cited papers motivate the structure-preserving MIMO/Krylov framework; the transfer-row identity in Section 2 is the direct derivation for this symmetric passive-RC projection setting.
