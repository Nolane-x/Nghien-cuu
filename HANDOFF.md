## Latest active-channel checkpoint — K fit-snapshot sensitivity rejected (23/11/2026)

Continue from [HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md](HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md) on branch `research/wilbers-human-active-channel-baseline-2026-11-22`.

- Dataverse source reconciliation [45128132847](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45128132847): Na final-fit 13/13 parameters match MOD; K only 5/11 match.
- K-human terminal fit snapshot, replayed as runtime-only sensitivity [45128589224](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45128589224), worsens 200-AP MAE by 7.49% and RMSE by 7.49%. All 200 amplitudes finite; canonical MOD unchanged.
- Do not promote archived snapshot. Next focus is controlled kinetic/density identifiability rather than copying the terminal fit dictionary.

---

## Latest active-channel checkpoint — 200-AP AP-clamp validated (23/11/2026)

Continue from [HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md](HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md) on branch `research/wilbers-human-active-channel-baseline-2026-11-22`.

- 200-AP workflow [45126687672](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45126687672): success, 9/9 tests; artifact [14796251799](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45126687672/artifacts/14796251799).
- Four original human/mouse Na/K models produced 200/200 finite amplitudes on the verified H_wide trace. Optimized current collector matched the original np.append output exactly on the 5-AP reference for all four models.
- Per-recording workbook comparison: model AP200 is above experimental mean in all six groups. Largest gap: mouse K 0.6284 model vs 0.2736 experiment. Keep Na Hnarrow/Hwide separate.
- Report/JSON/CSV committed; next is controlled sensitivity/identifiability, without changing runtime channel defaults.

---

## Latest active-channel research checkpoint — Figure 2 inferential statistics reproduced (23/11/2026)

Continue from [HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md](HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md) on branch `research/wilbers-human-active-channel-baseline-2026-11-22`.

- Original `stats_fig2.py` executed unchanged after SHA-1/SHA-256 verification; workflow [45117497613](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45117497613) passed 18/18 tests.
- OLS/Type-II interaction p-values reproduce all four article values: Na AP1–200 underflow <1e-323; Na AP1–5 1.41e-54; K AP1–200 3.19e-46; K AP1–5 0.0721.
- Cluster-robust sensitivity by recording: Na AP1–200 8.50e-11 / AP1–5 5.80e-9; K AP1–200 0.00373; K AP1–5 0.0759. Interpret separately from original OLS.
- Raw AP-clamp H_wide.csv trace replay remains pending. No runtime channel mechanism or production default changed.

---

## Latest active-channel research checkpoint — Figure 2 AP-clamp raw data verified (23/11/2026)

Continue from [HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md](HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md) on branch `research/wilbers-human-active-channel-baseline-2026-11-22`.

- Figure 2 Na/K workbook and original plot/stat scripts SHA-1/SHA-256 verified; data workflow [45116703439](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45116703439) passed.
- Na 49 recordings (16 H, 33 M), main Hnarrow AP200 mean normalized current: 0.7487 H, 0.5167 M.
- K 25 recordings (14 H, 11 M), AP200 normalized current: H cells 0.4275 (H input)/0.4063 (M input); M cells 0.2736/0.2693.
- Exact source stats script inspected; OLS/Type-II ANOVA reproduction not yet run. Na workbook has unresolved Mwide/Hwide description duplication. 15.1 MB AP-clamp time-series matrix not yet replayed.
- NMODL source-vs-stable probe remains successful on NEURON 9.0.2; no runtime mechanism or production default changed.

---

## Latest research checkpoint — Wilbers Dataverse v3 / NMODL source audit (22/11/2026)

Continue from [HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md](HANDOFF_2026-11-22-HUMAN-SOMATIC-NAV-KV-BASELINE.md) on branch `research/wilbers-human-active-channel-baseline-2026-11-22`.

- DataverseNL DOI 10.34894/L5J0SD: released version 3.0, CC0-1.0, 65 files.
- Selected Na/K mechanisms and fitting source files were downloaded/read and SHA-256 hashed; see the [curated manifest](amsn-core/research/references/wilbers2023_dataverse_source_manifest_2026-11-22.json).
- The source audit found a possible `trap0` branch/limit mismatch, an unresolved K fitting snapshot mismatch, and current-clamp gbar fitting against a 50:50 human/mouse target. These are reproduction blockers, not confirmed runtime failures.
- Raw spreadsheets/AP-clamp traces remain undownloaded. Original mechanisms not compiled or reproduced. No runtime active-channel code or default changed.
- PR #8 remains draft/open, unmerged and unchanged.

---

## Latest research checkpoint — human somatic NaV/KV evidence baseline (22/11/2026)

Continue from [HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md](HANDOFF_2026-11-22_HUMAN-SOMATIC-NAV-KV-BASELINE.md). Separate evidence branch: `research/wilbers-human-active-channel-baseline-2026-11-22`, based on `7655389b9d95dc85a54f81185a037ab026e32300`.

- Added a provenance-aware evidence registry for Wilbers et al. 2023 direct somatic nucleated-patch measurements, its separate single-compartment HH model fit, and Eyal et al. 2018 compartment-specific model estimates.
- Added a report and data-integrity tests. Values are **not** AMSN runtime defaults; the tests have not yet been run.
- Wilbers dataset DOI 10.34894/L5J0SD is verified at the VU Research Portal, but the raw Dataverse files have not been downloaded or hashed.
- Do not use somatic patch densities as AIS/axon densities. Keep the human dendritic channel distribution unresolved until direct evidence exists.
- This is a separate research branch; PR #8 remains draft/open and unchanged.

---

# HANDOFF — Nolane-x Research


---

## Latest implementation checkpoint — PRIMA phase profiler (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-PHASE-PROFILER.md](HANDOFF_2026-11-22_PRIMA-PHASE-PROFILER.md). Active branch: `research/allen-human-morphology-heldout-preflight-2026-11-22`; profiler code checkpoint: `9050c6a075c12af564fa86c0e5c2b1ce1564eac4`.

- Added `amsn-core/examples/prima_phase_profile.py`, targeted tests in `amsn-core/tests/test_prima_phase_profile.py`, and `.github/workflows/amsn-prima-kernel-phase-profile.yml`.
- Profile scope: existing PRIMA shifted Hines solves, orthogonalization, congruence projection, orchestration; separate Python/native self-time; same-order unprofiled build reference; reduced frequency/transient solvers; full-Hines baseline in an independent process.
- The matrix is three morphology fixtures × orders84/112/168 × two profiled repeats, with a separate Hines process for each morphology.
- **Validation pending:** Actions [45034830634](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45034830634) was queued at the last check. The targeted pytest command has not yet been observed passing; no profiler measurements have been accepted. See the new handoff for exact parameters and next actions.
- No production defaults or canonical Hines equations were changed. PR #8 remains draft/open.

---

## Latest implementation checkpoint — PRIMA phase profiler (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-PHASE-PROFILER.md](HANDOFF_2026-11-22_PRIMA-PHASE-PROFILER.md). Latest implementation commit: `fb642cce096a1fb2920c5b30bbaf471c1dd2d3a0`.

- Added phase timing for the real PRIMA builder, unprofiled build reference, reduced solver timing and a separate full-Hines process baseline.
- Files: `amsn-core/examples/prima_phase_profile.py`, `amsn-core/tests/test_prima_phase_profile.py`, `.github/workflows/amsn-prima-kernel-phase-profile.yml`.
- Targeted workflow [45035222028](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45035222028) and Core CI [45035222163](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45035222163) were **queued** at the last inspection. No tests or profile results have been accepted as passing yet.
- Keep full Hines canonical and production defaults unchanged. PR #8 remains draft/open.

---

## Latest validated checkpoint — complete PRIMA resource benchmark (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-RESOURCE-BENCHMARK.md](HANDOFF_2026-11-22_PRIMA-RESOURCE-BENCHMARK.md). Active branch: `research/allen-human-morphology-heldout-preflight-2026-11-22`. Resource benchmark code head tested: `e556625b9f0b1f31f9c822e603cf0ae220eefe0f`.

- [Completed GitHub Actions run 45016243390](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45016243390): 37/37 jobs passed (one validator + 36 resource jobs); validator log: 16 tests passed.
- 36/36 artifact ZIPs downloaded; 36/36 SHA-256 digests match GitHub metadata. Matrix coverage 3 morphologies × 2 mesh caps × orders84/112/168 × 2 repeats = 36 unique conditions.
- 7,560 sweep rows checked: 1,080 frequency, 5,832 per-port transient, 648 aggregate transient; each artifact has 210 rows and exit status 0.
- Median process user CPU / peak RSS: order84 = 141.45 s / 268.16 MiB; order112 = 205.96 s / 277.29 MiB; order168 = 278.31 s / 300.76 MiB. State reductions: 99.3225%, 99.0967%, 98.6451%.
- Whole audit-process measurements only, not isolated PRIMA kernels. Seven runner CPU models mean wall time is not a controlled speed comparison. Full Hines remains canonical; production defaults unchanged.
- Complete report: [HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_2026-11-22.md](amsn-core/research/HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_2026-11-22.md). Raw per-run data, summaries, manifest, validation JSON and reproducer are linked in that report.

The preceding 12/36 resource note remains in the history below, but is superseded for resource status by this 36/36 verified run. PR #8 remains draft/open; do not merge or mark ready without explicit authorization.

---

## Previous validated checkpoint — PRIMA held-out morphology and port/order study (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-HELDOUT-AND-PORT-ORDER.md](HANDOFF_2026-11-22_PRIMA-HELDOUT-AND-PORT-ORDER.md). Active branch: `research/allen-human-morphology-heldout-preflight-2026-11-22`; validated code head: `5180f0bc72dbfad0a460b0870ca80fec772db0e3`.

- Held-out human L2–3 dendritic morphology NMO_162186: [workflow 45012282648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282648), 2/2 jobs pass. Exact SWC SHA-256 `a05ad0770e857676b6be415f6f81a7548d69ccf74f62c7418756429c6a4105cc`; 7,287 records; dendrites complete and axon incomplete; epilepsy surgical specimen. PRIMA coverage 81/729/3,402 rows and all 81 G/C Cholesky checks passed.
- Equal-order 7-port/9-port: [workflow 45012282737](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282737), 12/12 pass. At order56/112, all 252 common-output pairs worsened when nine ports were retained. At order168, 138/252 worsened and 114/252 improved, median ratio 1.000001: practical parity, not a systematic improvement.
- Nine-port order capacity: [workflow 45012282650](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282650), 6/6 pass. Maximum transient NRMSE falls from 12.10% (order28) to 0.5231% (56), 0.001775% (84), 3.447e-5% (112), 3.450e-6% (168). Order168's incremental value varies by morphology.
- Core CI [45012282476](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282476) 4/4 pass; enrichment [45012282496] 6/6; parameter robustness [45012282485] 3/3.
- Resource/RSS matrix [45012282723](https://github.com/Nolane-x/Nghien-cuu/actions/runs/45012282723): validator preflight passed; 12/36 resource artifacts for NMO_68174 have now been independently verified (two mesh caps × orders84/112/168 × two replicates, all SHA-256 matched and exit0). Other morphology jobs remain; full matrix incomplete. See [partial report](amsn-core/research/HUMAN_PASSIVE_PRIMA_RESOURCE_BENCHMARK_PARTIAL_2026-11-22.md).

Full Hines remains canonical. No production defaults changed. All claims are limited to passive linear RC; ±20% parameter scenarios are deterministic stress tests, not biological distributions. PR #8 remains draft/open.

**Ngày checkpoint ban đầu:** 2026-11-20  
**Kho chuẩn:** https://github.com/Nolane-x/Nghien-cuu  
**Nghiên cứu đang bàn giao:** AMSN — Adaptive Multi-Scale Neuron  
**Phạm vi:** tài liệu này phản ánh snapshot ban đầu, không phải trạng thái repo mới nhất. Ở thời điểm snapshot, các thư mục nguồn AMSN Alpha cũ trống; sau đó AMSN Neuron Core đã được xây dựng lại từ đầu và có mã nguồn/test thật trong `amsn-core/`. Xem `HANDOFF_2026-11-20_MESH.md` để biết trạng thái mới nhất. Không coi code mới là recovery của Alpha cũ.

---

## 0. Chỉ dẫn bắt buộc cho AI/phiên mới

Trước khi làm bất cứ việc gì:

1. Đọc toàn bộ file này và checkpoint `HANDOFF_*.md` mới nhất.
2. Kiểm tra trạng thái branch/commit mới nhất; các mục lịch sử phía dưới có thể đã được supersede bởi handoff mới hơn.
3. Đọc `research/AMSN_RESEARCH_DOSSIER.md`.
3. Đọc `research/AMSN_RECOVERY_STATUS_2026-11-20.md` và phần mới nhất trong `research/RESEARCH_LOG.md`.
4. Kiểm tra trạng thái GitHub hiện tại (nhánh, commit mới nhất, files) trước khi ghi. Không giả định repo vẫn giống checkpoint.
5. Tiếp tục nghiên cứu và thực hiện thí nghiệm; không chỉ lặp lại kế hoạch cho người dùng. Sau mỗi phát hiện có giá trị, ghi lại vào repo trước khi kết thúc phiên.

**Không yêu cầu người dùng lặp lại mục tiêu đã ghi ở đây.** Người dùng muốn tiến hành nghiên cứu thật, không dừng ở lời hứa hay báo cáo kế hoạch. Khi có thể thực hiện một bước an toàn và hữu ích thì hãy làm luôn.

## 1. Mục tiêu dài hạn

Xây dựng và kiểm chứng một mô hình tính toán có độ trung thực sinh học cao cho một neuron thực, sau đó dùng các nguyên lý tính toán rút ra để thiết kế và đánh giá những kiến trúc AI mới.

Mục tiêu không phải tạo một mô hình “trông giống neuron”, cũng không phải nhồi mọi cơ chế vào một class Python. Mục tiêu là một **digital twin đa thang, có provenance, uncertainty, coupling đúng đơn vị và validation độc lập**.

Các lớp sinh học cần được nghiên cứu theo mức độ có bằng chứng:

- Hình thái: soma, axon initial segment, axon, basal/apical dendrite, branch, spine, synaptic bouton; về sau mới thêm ER, mitochondria, nucleus và extracellular geometry.
- Điện sinh học: cable equation, màng, điện dung, điện trở trục, Na/K/Ca/Cl, leak, HCN, Ca-activated K, pump/exchanger.
- Synapse: vesicle pools, release probability, glutamate/GABA, uptake/clearance, AMPA/NMDA/GABA receptors, Markov kinetics.
- Tính toán dendrite: branch-specific integration, NMDA/Na/Ca local events, spine neck resistance, tương tác dendrite–soma–AIS.
- Calcium/signaling: diffusion, buffering, pumps, ER, mitochondria, CaM/CaMKII, calcineurin/PP1, PKA/PKC, ERK/CREB khi có dữ liệu.
- Plasticity: STDP, LTP/LTD, homeostasis, receptor trafficking, intrinsic excitability.
- Gene/protein: synapse-to-nucleus, CREB/IEGs, mRNA, translation, protein turnover; không mô phỏng toàn bộ genome nếu chưa có câu hỏi và dữ liệu.
- Năng lượng: Na/K pump, calcium handling, vesicle cycling, ATP/ADP, mitochondria/oxidative phosphorylation.
- Môi trường/glia: extracellular ions, glutamate, astrocytic uptake/buffering và neuromodulation.
- Cấu trúc dài hạn: remodeling và thay đổi hình thái khi có cơ chế và dữ liệu thích hợp.

Không cần đưa tất cả vào phiên bản đầu tiên. Mỗi cơ chế phải có lý do, nguồn tham số, kiểm tra và tiêu chí loại bỏ.

## 2. Đối tượng khởi đầu

Ưu tiên **human layer 2/3 cortical pyramidal neuron** vì đã có mô hình hình thái/điện sinh học người và nghiên cứu quần thể L2–3.

Các nguồn nền tảng đã được ghi trong dossier:

- Eyal et al. 2018 — mô hình neuron tháp vỏ não người từ gai dendrite đến spike: https://pmc.ncbi.nlm.nih.gov/articles/PMC6034553/
- ModelDB 238347: https://modeldb.science/238347
- Aizenbud et al. 2026 / FCI: https://doi.org/10.1073/pnas.2533168123
- FCI source: https://github.com/ido4848/fci
- Planert et al. human L2–3 electrophysiological subtypes: https://www.nature.com/articles/s41593-025-02134-7
- Allen Cell Types: https://celltypes.brain-map.org/
- NeuroMorpho: https://neuromorpho.org/

Thông số từ paper/model cụ thể không được biến thành “hằng số phổ quát của neuron người”. Ghi rõ loài, vùng não, cell type, phương pháp, cỡ mẫu, điều kiện và nguồn.

## 3. Nền tảng/phát hiện kỹ thuật đã khảo sát

### FCI repository

Đã đọc một phần source/README/model files của https://github.com/ido4848/fci.

- Có các mô hình compartmental người/chuột dùng trong phân tích functional complexity.
- Cấu hình được xem xét có dendrite thụ động, soma/axon phát spike, AMPA/NMDA, GABA-A và cơ chế phát xung Na/K.
- Đây là baseline có giá trị cho hình thái + tích hợp synapse + NMDA nonlinearity, **không phải** mô phỏng toàn bộ kênh ion hoạt động trên dendrite, calcium signaling, gene expression hay metabolism.
- FCI đo độ phức tạp của ánh xạ input-output trong protocol/mô hình cụ thể; không phải phép đo trí thông minh, ý thức hoặc cognition của con người.
- Dùng FCI làm metric phụ; phải match firing rate, input statistics, dataset, training budget.

### BRAINCELL

Đã khảo sát source tree và một số mechanism files của https://github.com/RusakovLab/BRAINCELL.

- Nền tảng NEURON-based tập trung vào neuron, astrocyte, synapse và extracellular dynamics; README đề cập nanoscale spine/stalk geometry và ion diffusion.
- Đã thấy các module thuộc calcium diffusion/handling, receptor states, glutamate transporter và một số ion/pump mechanisms.
- Không được tuyên bố đã audit đầy đủ mọi module. Trước khi tự xây mechanism tương tự, đọc source đúng path, xác định license từng thành phần và benchmark khả năng mở rộng.
- Khuyến nghị: tận dụng/đối chiếu BRAINCELL thay vì viết lại những gì nó đã cung cấp.

### Bộ công cụ cần benchmark

- **MOOSE**: ứng viên tích hợp đa ngăn + hóa sinh/reaction-diffusion; phải kiểm tra thực nghiệm trước khi chọn làm core. License cần xét.
- **NEURON + RxD**: baseline quan trọng cho cable electrophysiology và reaction-diffusion.
- **STEPS / MCell**: subdomain stochastic 3D cho spine, nanodomain, vesicle/receptor.
- **Jaxley**: differentiable biophysical modeling, parameter fitting và sensitivity ở phần phù hợp.
- **Arbor**: hiệu năng neuron/network.
- **COPASI**: reaction network, ODE/SDE/SSA và parameter estimation.
- **NeuroML / SBML / NWB**: định dạng trao đổi mô hình/dữ liệu, không phải simulator thay thế.

Nguồn chính thức được liệt kê trong dossier. Phiên bản hiện hành cần kiểm tra lại ở mỗi phiên dùng phần mềm.

## 4. Trạng thái lưu trữ và sự thật về mã nguồn (20/11/2026)

Đã kiểm tra filesystem của phiên làm việc:

- `/mnt/data/AMSN_research_dossier_v1.md`: có hồ sơ nghiên cứu Markdown, khoảng 32.586 byte, 340 dòng.
- `/mnt/data/amsn_alpha/README.md`: có README mô tả AMSN Alpha 0.2.0a2, khoảng 9.341 byte.
- Các thư mục `amsn/`, `tests/`, `scripts/`, `docs/`, `results/`, `data/` trong `/mnt/data/amsn_alpha/` có tồn tại nhưng rỗng tại lần kiểm tra.
- Vì vậy, các module Python, test suite, scripts và output dữ liệu không còn trong thư mục được kiểm tra.
- README cũ **tuyên bố** có SWC import, Hines solver, HH/Mainen-like channels, AMPA/NMDA/GABA, stochastic release, STDP, calcium/plasticity, metabolism/ATP, chloride homeostasis, astrocyte coupling và “69 passing tests”. Nhưng khi code/tests trống, không thể xác minh các chức năng hay con số test đó.
- Ba PNG còn thấy trong vùng mount tạm của phiên: `astrocyte_eaat_sweep.png`, `amsn_astrocyte_closed_loop.png`, `amsn_alpha_integrated.png`. Chúng không nằm trong thư mục `/mnt/data/amsn_alpha/results/` chuẩn ở thời điểm kiểm tra; chưa có nguồn dữ liệu/mã tái tạo đủ để coi hình là kết quả có thể tái lập.
- Một mô hình SWC 10.660 node tên `790872626_raw.swc` từng được xem trong nghiên cứu trước, nhưng license/provenance và việc có còn file nguồn không phải kiểm tra lại trước khi dùng. Không commit/redistribute nếu chưa kiểm tra license.

**Điểm sửa quan trọng:** không lặp lại tuyên bố “69 tests passed” hoặc tuyên bố alpha đã chạy được cho đến khi mã nguồn thật được khôi phục/tái dựng và toàn bộ test được chạy lại. Dossier hiện là hồ sơ nghiên cứu, không phải bằng chứng code hoạt động.

## 5. Thiết kế nghiên cứu

AMSN nên là một hệ nhiều solver, nhiều thang thời gian, nhiều độ phân giải, với sổ cái provenance.

Mỗi subsystem phải khai báo:

- state variables và đơn vị;
- spatial domain/compartment mapping;
- solver/integrator, deterministic hay stochastic;
- timestep hoặc tolerance;
- inputs/outputs/fluxes và quy ước dấu;
- cách coupling và độ trễ đồng bộ;
- conservation checks phù hợp;
- nguồn và uncertainty của mọi parameter.

Không kết nối subsystem bằng cách cập nhật các biến tùy tiện. Đặc biệt phải kiểm tra đơn vị (m, cm, µm; s, ms; mol/L, mM; A, nA; F, µF), area/volume conversion và flux direction. Kiểm tra numerical convergence và seed reproducibility trước khi tin hình vẽ.

### Pipeline validation

- V0 Morphology: import/branch topology, lengths, diameters, area, volume.
- V1 Passive cable: input resistance, membrane time constant, attenuation/transfer impedance.
- V2 Action potential: threshold, amplitude, width, AHP, adaptation.
- V3 Synapse: EPSP/IPSP rise/decay, paired-pulse, receptor kinetics.
- V4 Dendritic nonlinearities: branch-local voltage/calcium, NMDA/Na/Ca events, soma coupling.
- V5 Calcium/signaling: transient, spatial profile, time course, perturbation.
- V6 Plasticity: STDP window, LTP/LTD magnitude/time course, receptor/kinase dependence.
- V7 Gene/protein: transcript/protein dynamics and perturbations.
- V8 Metabolism: ATP demand/recovery, pump cost, mitochondrial calcium.
- V9 Generalization: protocols withheld from fit; uncertainty/calibration.
- V10 Computational utility: FCI, task accuracy, data efficiency, continual learning, energy/computation.

Chia train/calibration/holdout theo cell/subject/experiment nếu có thể; không chỉ chia ngẫu nhiên các time window của cùng một trace.

## 6. Lộ trình có thứ tự ưu tiên

### P0 — Khôi phục và khóa provenance

1. Lưu các tài liệu nghiên cứu này lên GitHub.
2. Không giả định source code cũ có thể khôi phục từ README.
3. Tìm lại artifacts/source từ GitHub Actions, commit history hoặc backup chỉ khi người dùng chỉ rõ vị trí/repo; không tự bịa đường dẫn hay ghi đè.
4. Tạo project Python tối thiểu mới trong branch riêng khi đến lúc code; mỗi module/test phải được lưu ngay sau khi tạo.
5. Ghi SHA commit, package lock, Python version, OS và lệnh tái tạo.

### P1 — Reproduce baseline

1. Chạy nguyên bản Eyal/ModelDB NEURON model (không thay mechanism).
2. Chọn một morphology có license rõ ràng và metadata đầy đủ.
3. Lưu protocol, voltage traces và test output.
4. Đối chiếu một baseline bằng NEURON; chỉ thử MOOSE sau khi có reference outputs.
5. Không bắt đầu bằng full gene/metabolism; điện sinh học chưa vững thì chemistry chỉ làm tăng sai số khó truy tìm.

### P2 — Dendrite/spine benchmark

- Single synapse, same-branch coincident cluster, distributed multi-branch inputs, jitter, inhibitory veto.
- Ghi spine head/neck, dendrite local, soma và AIS.
- Ablation: passive vs NMDA vs active channel variants.
- Match rate/input distribution trước khi so sánh FCI.

### P3 — Causal calcium-to-plasticity loop

- NMDAR/CaV → Ca²⁺/CaM → CaMKII/phosphatase → AMPAR state/trafficking.
- Block từng mắt xích và dự đoán đầu ra nhiều tầng.
- So ODE/continuum với STEPS/MCell stochastic ở một microdomain.

### P4 — Synapse-to-nucleus / gene & protein

- Ca²⁺/ERK/CREB → immediate early genes → mRNA/protein → receptor trafficking.
- Phân biệt local translation và nuclear transcription.
- Mở rộng theo time course và perturbation, không mô phỏng whole genome trước.

### P5 — Metabolic constraint

- Nối Na/K pumping, calcium handling, vesicle recycling với ATP cost/recovery.
- Dùng cùng tổng spike nhưng khác temporal patterns để đánh giá lịch sử hoạt động.

### P6 — AI architecture translation

- Trích cơ chế có bằng chứng, xây abstraction nhỏ và kiểm thử độc lập với biological simulator.
- Baselines: MLP, RNN/GRU/LSTM, TCN, SNN và Transformer phù hợp.
- Match parameter count, data, training steps, compute/energy budget và evaluation protocol.
- Metrics: data efficiency, continual learning/forgetting, temporal memory, robustness, compositional generalization, energy, interpretability.
- Không kết luận vượt Transformer dựa trên một task nhỏ, một plot hoặc FCI.

## 7. Giả thuyết nghiên cứu mở

Các ý sau là giả thuyết, không phải kết quả:

1. **Adaptive Biological Resolution:** tăng chi tiết ở spine/branch đang hoạt động mạnh, giảm chi tiết ở nơi ít liên quan, có error bound và flux conservation.
2. **Causal Cell Twin:** dự đoán hậu quả perturbation chứ không chỉ fit waveform baseline.
3. **Energetically Constrained Computation:** đo lợi ích tính toán trên mỗi chi phí năng lượng sinh học.
4. **Hybrid differentiable + stochastic inference:** Jaxley/gradient cho subsystem khả vi; Bayesian/SBI cho subsystem stochastic; kiểm tra identifiability.
5. **Population digital twins:** sau cell đơn đã validation, dùng distributions của morphology/subtype/synapse thay vì một neuron trung bình.

## 8. Quy tắc khoa học và an toàn dữ liệu

- Không tự đặt thông số sinh học để làm demo rồi gọi là human-calibrated.
- Không dùng một trace phù hợp làm bằng chứng toàn cục.
- Báo cáo negative results, failure cases, confidence/credible intervals và seed variance.
- Mọi bảng so sánh công cụ phải gắn phiên bản/ngày kiểm tra.
- License phải được kiểm tra trước khi vendoring mã và dữ liệu; giữ nguyên license của từng nguồn.
- Không commit dữ liệu người/bệnh nhân có thông tin định danh hoặc dữ liệu bị hạn chế.
- Không tuyên bố “mô phỏng hoàn chỉnh neuron người”, “AGI”, hay “vượt Transformer” khi chưa có bằng chứng được kiểm định độc lập.

## 9. Quy trình bắt buộc khi tiếp tục nghiên cứu

Mỗi phiên AI phải:

1. Kiểm tra branch và commit mới nhất trên GitHub.
2. Đọc checkpoint gần nhất, không sửa dựa trên bản nhớ cũ.
3. Làm một bước nghiên cứu/thực nghiệm cụ thể, lưu log command và output.
4. Tạo file log theo ngày, ví dụ `research/log/2026-11-21-<topic>.md`.
5. Với kết quả mới, cập nhật dossier bằng file version mới thay vì xóa lịch sử, ví dụ `AMSN_RESEARCH_DOSSIER_v1.1.md`.
6. Cập nhật handoff checkpoint mới (có thể tạo `HANDOFF_YYYY-MM-DD.md`), chỉ ra điểm khác so với bản trước.
7. Đẩy file lên repo, kiểm tra commit SHA/URL và xác nhận đúng path.
8. Khi hết phiên, ghi rõ: đã làm gì, file nào được tạo, test nào đã chạy, test nào chưa chạy, next action cụ thể.

**Ưu tiên tiếp theo ngay sau checkpoint này:** dựng một reproduction tối thiểu của Eyal 2018 bằng NEURON/ModelDB ở một môi trường có thể chạy; thu output baseline; khóa source version; rồi xây test đối chiếu đầu tiên. Không thêm các lớp gene/ATP/astrocyte vào trước khi baseline điện học qua kiểm chứng.

## 10. Cách ghi kết quả

Mỗi báo cáo thực nghiệm phải có:

- Research question
- Hypothesis (và điều kiện bác bỏ)
- Biological scope and cell type
- Data/source/license/provenance
- Model equations and parameter table
- Software/OS/package versions
- Run command/configuration/random seed
- Outputs and plots with source data
- Validation metrics and uncertainty
- Limitations and failed cases
- Commit SHA that contains code/data/report

Nếu thiếu một thành phần, phải ghi rõ “not collected/not validated”, không được tự điền bằng suy đoán.

---

**Trạng thái handoff:** Đây là checkpoint tài liệu để tiếp tục từ dữ liệu còn xác minh được. Nó không khẳng định có sẵn mã AMSN Alpha chạy được.


---

## Latest dated checkpoint — FCI derivatives and Segev morphologies (21/11/2026)

Read `HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md` before continuing. Two direct NeuroMorpho human L2/3 morphologies have been added with CC BY 4.0 attribution. The FCI `human/eyal` configurations are reduced derivatives, with passive dendrites and active soma/synthetic axon; their Na/Kv scaling is based on a rat Hay L5b exemplar. No FCI code was copied. The original Eyal 2018 ModelDB archive remains unavailable/unintegrated. Keep configurations separate.


---

## Latest dated checkpoint — FCI derivative / Segev morphologies (21/11/2026)

Continue from [HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md](HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md). The commit adds two direct NeuroMorpho human L2/3 morphologies, CC BY 4.0 attribution, parser/soma/cable tests, an FCI read-only provenance/parameter audit, and a four-job passive AC matrix. Do not claim results until that workflow passes. FCI is a reduced derivative, not original Eyal 2018; no FCI code is copied.


## Segev morphology investigation — 21/11/2026

The four-job AC matrix [44885009077](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44885009077) passed but shows NMO_68175 residuals (~0.94% low-frequency input, ~5.7% transfer maximum) that do not reduce on mesh refinement. Do not claim multi-cell validation is complete. Follow [HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md](HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md) and compare geometry/area/import mapping before changing parameters.



---

## Latest dated checkpoint — Segev AC source and probe coordinate audits (21/11/2026)

- Three-reference source audit [workflow 44899442076](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899442076) passed both NMO_68174/68175 morphology jobs on NEURON 9.0.2; Core CI [44899349672](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44899349672) passed.
- Source-reference results and limitations are recorded in [triplet handoff](HANDOFF_2026-11-21_SEGEV-AC-SOURCE-TRIPLET.md) and [research log](research/RESEARCH_LOG_2026-11-21_SEGEV-AC-SOURCE-TRIPLET.md). The measured legacy-to-exact transfer effect reached 0.021954% for cell1125 and 0.228926% for cell1204; exact-to-refined centre changes were zero at exported precision for those identifiable source sites.
- Next active experiment: [AC probe-coordinate audit](HANDOFF_2026-11-21_SEGEV-AC-PROBE-COORDINATE.md), comparing exact SWC readout, nearest segment centre and complex interpolation with source fixed at exact SWC arc. Do not infer results until raw CSVs and both CI jobs pass.



## Verified Segev AC probe-coordinate checkpoint — 21/11/2026

Probe audit [44901688035](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901688035) passed both human Segev morphologies on NEURON 9.0.2 (120 rows each); Core CI [44901673896](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44901673896) passed. Exact-SWC and nearest-centre probe readouts were identical at exported precision. Complex-linear interpolation altered cross-simulator residuals non-uniformly: for cell1125 median/p95/max 0.001555/0.049634/0.130599% → 0.000670/0.046984/0.132786%; for cell1204 0.002297/0.073495/0.169222% → 0.001105/0.059094/0.125637%. It must remain a diagnostic option, not a new default. Continue from [probe mesh sweep handoff](HANDOFF_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md) to test 0.25/0.125/0.0625 µm convergence.




## Verified Segev AC probe mesh-convergence checkpoint — 21/11/2026

The six-job matrix [44902130621](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130621) passed 6/6; Core CI [44902130609](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44902130609) passed 4/4. Exact-SWC and nearest-centre transfer readouts were identical at exported precision for all 720 rows. Complex-interpolation readout sensitivity shrank with mesh refinement, but its effect on the cross-simulator residual did not converge to a universal benefit: at 0.0625 µm it improved the NMO_68174 aggregate and worsened all three NMO_68175 aggregate metrics. Keep exact-SWC canonical and interpolation diagnostic-only. See [report](amsn-core/research/HUMAN_SEGEV_AC_PROBE_MESH_SWEEP_2026-11-21.md), [summary CSV](amsn-core/results/human_segev_ac_probe_mesh_sweep_summary_2026-11-21.csv) and [mesh-sweep handoff](HANDOFF_2026-11-21_SEGEV-AC-PROBE-MESH-SWEEP.md).


## Verified Segev axial operator checkpoint — 21/11/2026

The Segev full-tree axial matrix [44903533060](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903533060) passed 2/2 jobs; original NMO_290988 regression [44903453372](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44903453372) passed. The 32-vector sampled axial-operator relative L2 max is 0.0106860% (NMO_68174) and 0.0032929% (NMO_68175). This is axial-only and not a formal operator-norm or biological validation. Next, establish matched membrane-area/control-volume support before adding leak and capacitance. See [matrix report](amsn-core/research/HUMAN_SEGEV_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md) and [handoff](HANDOFF_2026-11-21_SEGEV-FULL-TREE-AXIAL-MATRIX.md).


## Verified Segev membrane-area support checkpoint — 21/11/2026

Matched-support membrane-area workflow [44904138720](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904138720) passed both Segev cells. Total area mismatch is below 1.2e-6%; maximum per-node difference is 0.0256% (NMO_68174) and 0.00908% (NMO_68175); every NEURON segment area was allocated with section coverage closure below 2.3e-14%. Next: combine this validated per-node area support with the locked axial graph to compare the passive leak+capacitance operator. See [report](amsn-core/research/HUMAN_SEGEV_MEMBRANE_AREA_SUPPORT_AUDIT_2026-11-21.md) and [handoff](HANDOFF_2026-11-21_SEGEV-MEMBRANE-AREA-SUPPORT.md).


## Verified Segev matched-support passive operator checkpoint — 21/11/2026

Matched-support passive admittance workflow [44904475571](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475571) passed 2/2 cells, and Core CI [44904475559](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44904475559) passed 4/4 jobs. The maximum sampled relative L2 error across DC–3 kHz was 0.0078381% for NMO_68174 and 0.0025449% for NMO_68175. Leak/capacitance diagonal errors were below 0.00025%. This is a matched-support finite-volume projection, not a native fine-grid Schur complement or biological validation. See [report](amsn-core/research/HUMAN_SEGEV_PASSIVE_ADMITTANCE_OPERATOR_AUDIT_2026-11-21.md) and [handoff](HANDOFF_2026-11-21_SEGEV-PASSIVE-ADMITTANCE-OPERATOR.md).


## Verified Segev native passive transient checkpoint — 21/11/2026

Native transient validation [44907890895](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890895) passed 2/2 cells; Core CI [44907890934](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44907890934) passed 4/4 jobs. Maximum waveform NRMSE was 0.001641% (NMO_68174) and 0.002370% (NMO_68175); absolute waveform errors stayed below 5.2e-6 mV. This directly compared native NEURON segment trees against AMSN's SWC node-centred trees with backward Euler and recorded nonzero source/probe mapping offsets. See [report](amsn-core/research/HUMAN_SEGEV_PASSIVE_TRANSIENT_AUDIT_2026-11-21.md) and [handoff](HANDOFF_2026-11-21_SEGEV-PASSIVE-TRANSIENT.md). Next: time-step/spatial mesh factorial convergence.

## Verified Segev transient time/space convergence — 21/11/2026

The 12-job matrix [44908381318](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381318) passed 12/12; Core CI [44908381336](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44908381336) passed 4/4. It produced 126,180 time-series rows and 360 summaries.

Backward-Euler temporal refinement is first-order (pairwise maximum-NRMSE ratios 1.985/1.984 as dt is halved). Cross-simulator residuals barely change with dt at fixed mesh. Spatial refinement is cell-specific: it improves NMO_68174 but worsens NMO_68175, where interpolation is no longer better at 0.0625 µm. Do not choose a universal finer mesh or probe rule from these two morphologies.

See [full convergence report](amsn-core/research/HUMAN_SEGEV_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md), [configuration summary](amsn-core/results/human_segev_passive_transient_convergence_summary_2026-11-21.csv), and [pairwise measurements](amsn-core/results/human_segev_passive_transient_pairwise_convergence_2026-11-21.csv).

Next: test source placement by comparing nearest-centre IClamp with a charge-conserving two-centre weighted current split at the exact SWC arc.


## Verified Segev transient source-placement checkpoint — 21/11/2026

Source-placement audit [44910070325](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070325) passed 4/4; Core CI [44910070326](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910070326) passed 4/4. The weighted two-centre IClamp split conserves total 10 pA at every sample, but its benefit is morphology-/mesh-dependent: it strongly improves NMO_68175 and is mixed/worse for NMO_68174 at the finer mesh. Keep it optional, not the default. Full report: [HUMAN_SEGEV_TRANSIENT_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md](amsn-core/research/HUMAN_SEGEV_TRANSIENT_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md). Next: direct AC source-placement comparison.


## Verified Segev AC source-placement checkpoint — 21/11/2026

AC source placement [44910754764](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754764) passed 4/4, Core CI [44910754810](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44910754810) passed 4/4. Weighted adjacent-centre source superposition strongly improves NMO_68175 at both meshes, but is mixed/worse on NMO_68174 at the finer mesh. Keep it optional, not the default. See [AC report](amsn-core/research/HUMAN_SEGEV_AC_SOURCE_ALIGNMENT_AUDIT_2026-11-21.md), [summary](amsn-core/results/human_segev_ac_source_alignment_summary_2026-11-21.csv), and [comparison](amsn-core/results/human_segev_ac_source_alignment_comparison_2026-11-21.csv).


## AC source-placement worst-path localization — 21/11/2026

The four raw AC matrices peak at 3 kHz and are concentrated in apical transfer paths. NMO_68174's worst path remains basal q75→apical q90; NMO_68175's worst path changes with mesh, and weighted source moves the remaining worst path to basal q75→apical q90 at both meshes. See [AC worst-pair table](amsn-core/results/human_segev_ac_source_alignment_worst_pairs_2026-11-21.csv).


## Third-morphology source-alignment replication — 21/11/2026

A six-job independent morphology matrix has been added: NMO_68174, NMO_68175 and NMO_290988 / 1094_Mohan_etal_2015 at mesh caps 0.125 and 0.0625 µm. The third morphology is a distinct NeuroMorpho.Org/DeKock record but is a partial dendritic reconstruction (no axon, moderate completeness) with mesiotemporal sclerosis context; do not label it a healthy control. Each job runs all AMSN tests, validates source/probe mapping and produces both transient and AC raw measurements.


## Completed three-morphology source-placement replication — 21/11/2026

Workflow [44914135217](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44914135217) passed 6/6; every job ran the full 81-test suite. The matrix covers NMO_68174, NMO_68175 and NMO_290988 at 0.125/0.0625 µm, with transient and AC comparisons. NMO_68175 benefits consistently, NMO_68174 is mixed, and NMO_290988 shows strong transient improvement but slight AC degradation at the finer mesh. Keep exact-SWC canonical and weighted source optional. See the [replication report](amsn-core/research/HUMAN_MORPHOLOGY_SOURCE_ALIGNMENT_REPLICATION_2026-11-21.md) and [summary CSV](amsn-core/results/human_morphology_source_alignment_summary_2026-11-21.csv).


## NMO_290988 transient time/space convergence — in progress

A six-job factorial run now varies dt=0.1/0.05/0.025 ms and NEURON mesh cap=0.125/0.0625 µm on the independent 8,903-record NMO_290988 morphology. Each job runs the complete AMSN test suite and preserves raw transients. Do not infer convergence until all six artifacts have been reviewed.


## NMO_290988 transient time/space convergence — completed 21/11/2026

Workflow [44915125555](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44915125555) passed 6/6. At fixed mesh, AMSN–NEURON mismatch barely changes with dt; refining the NEURON mesh from 0.125 to 0.0625 µm reduces maximum interpolated NRMSE by about 90.4%. Direct NEURON temporal pairwise error halves with dt as expected for backward Euler. See [convergence report](amsn-core/research/HUMAN_NMO_290988_PASSIVE_TRANSIENT_CONVERGENCE_2026-11-21.md) and [pairwise data](amsn-core/results/human_nmo290988_passive_transient_pairwise_convergence_2026-11-21.csv).


## Exact passive Schur port reduction — in progress

Core API amsn.schur_reduce_passive_admittance eliminates non-retained passive cable vertices and returns the frequency-dependent complex admittance on retained ports. Unit tests compare it with dense Schur and full Hines results. The six-job human audit compares seven-port AMSN and NEURON operators over eight frequencies.


## Exact passive Schur port-matrix audit — completed 21/11/2026

The new exact frequency-dependent Schur reduction is validated against an independent full-tree AMSN port impedance inverse to 9.40e-11% maximum error. The six-job human audit [44916411567](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411567) passed 6/6, and Core CI [44916411432](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411432) passed 4/4. Seven-port admittance matrix errors remain below 0.0262% and impedance errors below 0.0895%; maxima occur at 3 kHz, with off-diagonal couplings more sensitive than diagonal ports. See [report](amsn-core/research/HUMAN_PASSIVE_SCHUR_PORT_MATRIX_AUDIT_2026-11-21.md).


The six Schur audit jobs each passed 90 tests; Core CI [44916411432](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44916411432) passed all 90 tests on Python 3.12 and 3.13 and both NEURON jobs.


## Schur port error localization extension — in progress

The Schur audit now records per-frequency, per-port row-norm and diagonal/off-diagonal errors so the high-frequency residual can be localized without unstable relative percentages on near-zero matrix entries. Each configuration will upload 56 port-localization rows in addition to the 392 raw matrix entries and eight frequency summaries.


## Schur port-resolved residual localization — completed

The rerun [44917323461](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44917323461) passed 6/6 and adds a 56-row per-configuration port-localization CSV. Dominant 3 kHz rows: NMO_68174 apical q50; NMO_68175 basal q50/apical q50 depending on mesh; NMO_290988 apical q90 with off-diagonal coupling error dominating its diagonal. See [localization data](amsn-core/results/human_schur_port_matrix_port_localization_2026-11-21.csv).


## PRIMA passive reduced-order model — completed 21/11/2026

A structure-preserving passive state-space reduction has been added after the exact Schur port audit. Human audit [44918896972](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918896972) passed 6/6; Core CI [44918897010](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44918897010) passed 4/4. The reduced order is 56 for full models of 8,893–13,747 compartments (99.37–99.59% fewer states). Worst 3 kHz impedance/admittance errors are 1.9661%/2.3601%; worst individual-port transient NRMSE is 0.00015662%. This validates the passive numerical subsystem, not active or biological behavior. Read [PRIMA handoff](HANDOFF_2026-11-21_PRIMA-PASSIVE-REDUCTION.md), [research report](amsn-core/research/HUMAN_PASSIVE_PRIMA_REDUCTION_AUDIT_2026-11-21.md) and [summary CSV](amsn-core/results/human_passive_prima_reduction_summary_2026-11-21.csv).

Next: multi-shift/frequency-aware PRIMA order sweep, retaining passivity and measuring the high-frequency error trade-off.


## Multi-shift passive PRIMA and order sweep — completed 21/11/2026

Added positive-real multi-shift Krylov expansion at 0/100/1,000/3,000 Hz and a human order sweep at 28/56/84 states. Across three morphologies and six NEURON reference-mesh configurations, order 56 gives maximum 3 kHz Z/Y errors below 0.0201%/0.0237%; order 84 lowers them below 0.000094%/0.000183%, with more than 99.05% state reduction. Six human jobs and four Core CI jobs passed; 99 tests passed on Python 3.12 and 3.13. Read [multi-shift/order-sweep handoff](HANDOFF_2026-11-21_PRIMA-PASSIVE-REDUCTION.md), [report](amsn-core/research/HUMAN_PASSIVE_PRIMA_MULTISHIFT_ORDER_SWEEP_2026-11-21.md) and [summary CSV](amsn-core/results/human_passive_prima_multishift_order_sweep_summary_2026-11-21.csv).


## Direct PRIMA-to-NEURON comparison — completed 21/11/2026

Added a three-layer validation: exact Schur vs Hines, PRIMA vs full Hines, and PRIMA vs NEURON. Human audit [44921474635](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474635) passed 6/6; Core CI [44921474632](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44921474632) passed 4/4 with 99 tests on both Python versions. At order 84, direct PRIMA–NEURON errors (0.08943% Z and 0.02611% Y) are essentially at the full-model cross-simulator discrepancy floor. Detailed [report](amsn-core/research/HUMAN_PASSIVE_PRIMA_NEURON_DIRECT_COMPARISON_2026-11-21.md) and [summary CSV](amsn-core/results/human_passive_prima_neuron_direct_comparison_summary_2026-11-21.csv).


## Human passive PRIMA parameter robustness — completed 21/11/2026

The basis-reprojection API has been tested on three human morphologies with nine parameter scenarios each (Rm/Cm/Ra ±20%, plus joint corners). Human workflow [44922676384](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44922676384) passed 3/3; Core CI [44922676436](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44922676436) passed 4/4 with 108 tests on Python 3.12 and 3.13. All 54 reduced models (27 frozen and 27 fresh) passed Cholesky passivity checks. Across the scenarios, the frozen order-56 basis stayed below 0.995% Z / 0.977% Y error at the 10 kHz stress point and below 0.000627% worst individual-port transient NRMSE. A fresh order-56 basis improved the global high-frequency error envelope, but not uniformly scenario-by-scenario. See [parameter robustness report](amsn-core/research/HUMAN_PASSIVE_PRIMA_PARAMETER_ROBUSTNESS_2026-11-21.md) and [morphology summary CSV](amsn-core/results/human_passive_prima_parameter_robustness_morphology_summary_2026-11-21.csv).


---

## Latest checkpoint — PRIMA nine-port result (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-NINE-PORT-RESULTS.md](HANDOFF_2026-11-22_PRIMA-NINE-PORT-RESULTS.md), not the older initial snapshot above. PR #3 merged as `9e646563f04d2682c32b6ccec5da8c4ae1bebb84`. The nine-port workflow passed 6/6 jobs, Core CI 4/4 and the seven-port control 6/6. The full report is [HUMAN_PASSIVE_PRIMA_NINE_PORT_ENRICHMENT_2026-11-22.md](amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_ENRICHMENT_2026-11-22.md). Key negative result: all 144 matched apical-q90 comparisons worsened after expanding seven to nine ports at the same tested reduction orders. Keep seven-port as the reference and full Hines canonical; next test basis capacity/order 112 and 168 or a block-Krylov/source-probe weighted basis. See the new dated research log for exact metrics and limits.


---

## Current validated state — PRIMA nine-port high-order basis (22/11/2026)

Continue from [HANDOFF_2026-11-22_PRIMA-NINE-PORT-HIGH-ORDER.md](HANDOFF_2026-11-22_PRIMA-NINE-PORT-HIGH-ORDER.md) and [the full result](amsn-core/research/HUMAN_PASSIVE_PRIMA_NINE_PORT_HIGH_ORDER_2026-11-22.md). PR #4 merged at `af88ffa12a3b00f274716d2f7c1229bfa4be2abc`. High-order workflow 44979673244 (6/6), Core CI 44979673250 (4/4), nine-port control 44979673251 (6/6) and seven-port Schur control 44979673239 (6/6) all passed. Orders 112/168 beat seven-port and nine-port order84 apical-q90 in all 36 matched pairs each and had no regression in 252 shared-port comparisons each. Do not promote defaults: retain default 28/56/84 and full Hines canonical until CPU/peak-RSS and held-out morphology benchmarks finish.
