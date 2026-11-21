# HANDOFF — Nolane-x Research

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
