# AMSN — Adaptive Multi-Scale Neuron
## Hồ sơ nghiên cứu v1.0 — checkpoint 20/11/2026

**Trạng thái:** hồ sơ tổng hợp nghiên cứu và thiết kế thí nghiệm. Đây không phải báo cáo xác nhận một mô phỏng hoàn chỉnh đã chạy.

## 1. Câu hỏi trung tâm

Làm thế nào mô hình hóa một neuron sinh học thực với đủ các cơ chế quan trọng — hình thái, điện sinh học, synapse, tín hiệu phân tử, gene/protein, chuyển hóa và môi trường — mà vẫn có thể tính toán, kiểm chứng, tái lập và dùng để phát hiện nguyên lý tính toán mới?

Luận điểm hiện tại: không nên tạo một “siêu class neuron” chứa mọi thứ và cũng không nên tự viết lại toàn bộ simulator. Hướng hợp lý hơn là một hệ đa mô hình, đa độ phân giải, nhiều solver, có giao diện trao đổi trạng thái/flux rõ ràng và provenance cho từng tham số.

## 2. Đối tượng sinh học đầu tiên

### Neuron tháp lớp 2/3 vỏ não người

Chọn human layer 2/3 cortical pyramidal neuron làm pilot vì đã có mô hình chi tiết về hình thái và điện sinh học, có dữ liệu synapse và các nghiên cứu gần đây về biến thiên subtype. Đây là lựa chọn thực dụng để tạo baseline, không phải tuyên bố rằng loại tế bào này đại diện cho mọi neuron người.

### Các bằng chứng nền tảng cần giữ đúng phạm vi

- **Eyal et al. (2018)** xây dựng các mô hình neuron tháp L2/3 người từ spine đến spike. Công trình mô hình hóa hình thái có gai dendrite, synapse AMPA/NMDA, NMDA spikes ở dendrite và Na spikes ở soma/axon. Các con số về số synapse đồng thời/khả năng kích hoạt spike trong bài phụ thuộc cấu hình và giả định mô hình cụ thể; không được dùng như hằng số sinh học phổ quát. Bài báo cũng nêu các thiếu hụt dữ liệu, nhất là về kênh ion người tại soma/axon và dendrite.
  - Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC6034553/
  - ModelDB: https://modeldb.science/238347
  - Source: https://github.com/ModelDBRepository/238347
- **Eyal et al. (2016)** báo cáo đặc tính màng đặc biệt ở neuron vỏ não người, gồm giá trị specific membrane capacitance được ước lượng từ một mẫu nhỏ. Dùng nó làm prior/tham số phụ thuộc loại tế bào, không mặc định cho mọi neuron.
  - Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC5100995/
- **Planert et al. (2025/2026)** được dossier ban đầu ghi nhận là nghiên cứu patch-clamp quy mô lớn trên neuron tháp lớp 2–3 người, mô tả nhiều subtype điện sinh lý và kết nối đơn synapse. Dữ liệu người thô có giới hạn truy cập; cần kiểm tra phiên bản paper, supplementary, data availability và Figshare trước khi tích hợp số liệu.
  - Paper: https://www.nature.com/articles/s41593-025-02134-7
  - Processed data/code: https://doi.org/10.6084/m9.figshare.28184126
- **Aizenbud et al. (2026), Functional Complexity Index (FCI)**: nghiên cứu mối liên hệ giữa hình thái dendrite, nonlinear synapses và độ phức tạp của input-output mapping trong những mô hình neuron được khảo sát. FCI phản ánh độ khó để một model dự đoán/biểu diễn ánh xạ I/O đó, không đo trí thông minh, ý thức hay cognition tổng quát.
  - Paper: https://doi.org/10.1073/pnas.2533168123
  - Code: https://github.com/ido4848/fci
  - Dataset: https://huggingface.co/datasets/i-do-ai/fci-neuron-simulations

**Nguyên tắc:** lưu cell type, species, brain region, subject/source, preparation, measurement method, uncertainty, license và điều kiện thí nghiệm cùng từng dữ liệu/tham số. Không ghép các số liệu khác nguồn thành một “neuron người trung bình” mà không biểu diễn độ bất định.

## 3. Phát hiện từ FCI source reconnaissance

Đã đọc một phần repository FCI, bao gồm README, cấu trúc mô hình và một số file mechanism/configuration.

Điều có thể dùng:
- FCI là baseline hữu ích để nghiên cứu ảnh hưởng của hình thái và nonlinear synaptic integration lên input-output computation.
- Các model được khảo sát gồm mô hình người và chuột; code có dữ liệu/model cards và pipeline mô phỏng → huấn luyện temporal model → ước lượng FCI.
- Cấu hình được xem xét có dendrite thụ động, soma/axon phát spike và các synapse AMPA/NMDA/GABA-A, với cơ chế Na/K liên quan phát xung.

Điều không được suy diễn:
- Không coi model FCI là một mô phỏng toàn bộ biology của neuron.
- Không nói nó đã mô phỏng đầy đủ active dendritic channels, calcium signaling, gene expression, metabolism hay glial coupling.
- Không diễn giải FCI cao hơn thành “thông minh hơn”.
- Không so FCI giữa các điều kiện khi firing rate, input statistics, calibration hoặc training budget chưa được match.

FCI nên là metric phụ trong một bộ đánh giá rộng, không phải mục tiêu duy nhất.

## 4. Những nền tảng mô phỏng cần so sánh

| Công cụ | Vai trò đề xuất | Điểm mạnh cần kiểm tra | Giới hạn/cảnh báo |
|---|---|---|---|
| **MOOSE** — https://www.mooseneuro.org/ | Ứng viên tích hợp điện sinh học, hóa sinh và reaction-diffusion | Kiểm tra khả năng đồng mô phỏng compartment electrophysiology và chemical kinetics trong một cấu hình thực tế | Chưa được benchmark trong dự án này; cần khóa version, API và license; không mặc định mọi mechanism được hỗ trợ hiệu quả |
| **NEURON + RxD** — https://www.neuronsimulator.org/ | Baseline/reference cho cable neuron và reaction-diffusion | Hình thái, channel mechanisms, synapses, extracellular/intracellular reaction-diffusion | RxD 3D có trade-off voxel/mesh, memory và độ phân giải; thử nghiệm trên spine mảnh là bắt buộc |
| **STEPS** — https://steps.sourceforge.net/ | Mô phỏng stochastic 3D ở microdomain/spine | Reaction-diffusion chính xác trên mesh tứ diện, low-copy-number signaling, membrane/channel coupling | Không phải lựa chọn thay thế trực tiếp cho toàn bộ cable neuron |
| **MCell** — https://www.mcell.org/ | Mô phỏng phân tử không gian và vesicle/receptor | Monte Carlo, phân tử rời rạc và phản ứng bề mặt trong hình học 3D | Cần coupling với solver điện sinh học; không giả định mô hình hóa toàn tế bào đơn giản |
| **Jaxley** — https://github.com/jaxleyverse/jaxley | Fit tham số và sensitivity trên subsystem phù hợp | Differentiable biophysical simulation, gradient/GPU | Không thay thế solver stochastic 3D tổng quát; phải đánh giá chi phí gradient và identifiability |
| **Arbor** — https://arbor-sim.org/ | Mở rộng sang network-level simulation | Hiệu năng CPU/GPU cho neuron đa ngăn và mạng | Không phải chemistry engine nội bào toàn diện |
| **COPASI** — https://copasi.org/ | Mạng phản ứng gene/protein/metabolism | ODE, stochastic/hybrid, parameter estimation, sensitivity | Không tự cung cấp morphology/cable solver |
| **NeuroML / SBML / NWB** | Chuẩn trao đổi mô hình, hóa sinh và dữ liệu | Tái lập và interoperability | Định dạng không thay thế simulator; phải kiểm tra semantic mapping và units |

Chiến lược ưu tiên:
1. Reproduce baseline người trong NEURON bằng source công bố.
2. Benchmark cùng một bài test electrical trong MOOSE.
3. Dùng STEPS hoặc MCell cho một microdomain cục bộ nếu ODE/continuum không đủ.
4. Dùng Jaxley cho tham số có thể vi phân.
5. Chỉ xây co-simulation orchestrator sau khi benchmark cho thấy có nhu cầu.

## 5. BRAINCELL reconnaissance

Repository: https://github.com/RusakovLab/BRAINCELL

Đã khảo sát source tree và một số mechanism files. Dự án được xây trên NEURON, với phạm vi neuron–astrocyte–synapse–extracellular dynamics; tài liệu mô tả spine/stalk geometry và ion diffusion. Một số file đã xem liên quan đến calcium diffusion/handling, receptor-state kinetics, glutamate transport và ion/pump mechanisms.

BRAINCELL là codebase đáng nghiên cứu để tránh tái phát minh. Tuy vậy:
- Chưa có full audit toàn bộ repository trong checkpoint này.
- Chưa xác nhận toàn bộ coupling, license của mọi bundled dependency và khả năng mở rộng tới gene/protein/metabolism.
- Không được ghi “BRAINCELL không có X” nếu chưa kiểm tra source và docs cụ thể.
- Bước tiếp theo: khóa commit SHA, đọc build/run instructions, tạo một smoke test nhỏ, map module hiện có sang AMSN layers, rồi mới quyết định extend/fork/wrap.

Repository: https://github.com/RusakovLab/BRAINCELL

## 6. Kiến trúc AMSN đề xuất

AMSN nên là một **framework đa mô hình/đa độ phân giải** với các subsystem có giao diện thống nhất, không phải một solver đơn lẻ.

### 6.1 Spatial model

- Morphology: soma, AIS, axon, basal/apical dendrites, branch points, spines, boutons.
- Electrical compartments: membrane/cable segments.
- Chemical compartments: spine head/neck, cytosol, ER, mitochondria, nucleus, perisynaptic/extracellular space.
- Explicit mapping giữa cable segments và chemical regions/mesh.
- Kiểm tra diện tích, thể tích, kết nối, điện trở trục và đơn vị khi merge/coarsen.

### 6.2 Membrane/electrophysiology

- Cable equation, capacitance, axial resistance, membrane currents.
- HH gates hoặc Markov states tùy cơ chế.
- NaV, KV, CaV, HCN, KCa, leak, chloride, pumps/exchangers.
- Phân bố channel theo cell region dựa trên bằng chứng; không mặc định mật độ đồng nhất.

### 6.3 Synapse and dendritic computation

- Vesicle pool, docking/fusion/release probability, facilitation/depression/recovery.
- Glutamate/GABA diffusion, uptake/clearance.
- AMPA/NMDA/GABA receptor kinetics and trafficking.
- Branch-specific integration, local NMDA/Na/Ca events, spine neck resistance.
- Measure voltage tại spine head/base, dendrite proximal/distal, soma và AIS.

### 6.4 Calcium and signaling

- Ca nanodomain/microdomain, buffers, pumps/exchangers, ER and mitochondrial Ca handling.
- CaM/CaMKII, calcineurin/PP1, PKA/PKC, ERK/CREB theo pathway có dữ liệu.
- Deterministic concentration models khi copy number lớn; stochastic discrete model khi số lượng phân tử nhỏ hoặc geometry cực nhỏ.

### 6.5 Plasticity, gene and protein

- STDP, LTP/LTD, homeostatic plasticity và intrinsic excitability.
- AMPAR/NMDAR phosphorylation/trafficking và cytoskeleton.
- Local translation ở dendrite/spine khác với transcription tại nucleus.
- Synapse-to-nucleus signaling, CREB/IEGs, mRNA/protein turnover.
- Không mô phỏng toàn bộ genome khi chưa có câu hỏi cụ thể và dữ liệu định lượng.

### 6.6 Metabolism and environment

- ATP/ADP, Na/K pump cost, calcium handling, vesicle recycling.
- Mitochondrial calcium and oxidative ATP supply.
- Extracellular K/Na/Ca/glutamate/GABA.
- Astrocytic uptake/buffering and neuromodulation có bằng chứng.
- Mọi flux phải có hướng, dấu, đơn vị và kiểm tra cân bằng.

## 7. Các khoảng trống nghiên cứu

1. **Multimodal data are not co-registered:** morphology, electrophysiology, transcriptomics, proteomics, calcium imaging và synapse data thường không được đo trên cùng một tế bào/cùng trạng thái. Rủi ro tạo “cell chimera”. Giải pháp: provenance cho từng parameter và uncertainty khi ngoại suy.
2. **Parameter identifiability:** nhiều bộ conductance/kinetics có thể tạo waveform soma tương tự. Cần multi-objective calibration và perturbation/holdout; một fit đẹp không chứng minh đúng cơ chế.
3. **Fine geometry:** spine neck, branchlets, nanodomains và organelle contacts nhạy với voxelization/mesh. Phải kiểm tra trực tiếp trên geometry neuron trước khi khái quát từ astrocyte models.
4. **Fast/slow and continuous/discrete coupling:** điện thế ở ms; calcium/phosphorylation từ ms đến phút; transcription/translation từ phút đến giờ; remodeling/metabolism lâu hơn. Timestep đơn không phù hợp cho tất cả. Cần multirate/event-driven/hybrid integration.
5. **Single neuron is not cognition:** chức năng nhận thức phụ thuộc circuit/network, development, plasticity, body/environment. Cần chứng minh cơ chế có giá trị trước khi port sang AI.

## 8. Quy trình xác minh bắt buộc

| Gate | Thành phần | Đầu ra đo | Kiểm tra |
|---|---|---|---|
| V0 | Morphology | topology, length, diameter, area, volume | So sánh nguồn; không mất branch, kiểm tra đơn vị |
| V1 | Passive cable | input resistance, time constant, attenuation, transfer impedance | Fit experimental curves; spatial convergence |
| V2 | Action potential | threshold, amplitude, width, AHP, adaptation | Fit protocol và test stimulus holdout |
| V3 | Synapse | EPSP/IPSP rise/decay, paired-pulse, receptor kinetics | Theo loại/ vị trí synapse |
| V4 | Dendritic nonlinearities | local NMDA/Na/Ca events, branch-soma coupling | Local voltage/calcium + soma output; ablation |
| V5 | Calcium/signaling | transient, spatial profile, kinase/phosphatase time course | Imaging/published time course, multiple seeds |
| V6 | Plasticity | STDP window, LTP/LTD magnitude and time course | Perturbation by receptor/kinase/phosphatase |
| V7 | Gene/protein | transcript/protein time course, receptor trafficking | Intervention + independent time-course data |
| V8 | Metabolism | ATP demand/recovery, mitochondrial calcium | Balance checks, firing-history response |
| V9 | Generalization | output on protocols not used in fitting | Error, uncertainty, calibration |
| V10 | Computational utility | FCI, task accuracy, efficiency, continual learning, energy | Baselines + matched compute/data/training |

Luật vàng: chia train/calibration/holdout theo cell/subject/experiment nếu có thể. Không chỉ chia ngẫu nhiên segments thuộc cùng trace. Báo cáo failure cases, uncertainty, seed variance và protocol đầy đủ.

## 9. Thí nghiệm ưu tiên

### A. Human-neuron baseline reproduction

1. Chọn một cell L2/3 Eyal 2018.
2. Chạy original NEURON implementation và lưu version/parameters.
3. Reproduce voltage waveform, input resistance, membrane time constant, firing response và synaptic response.
4. Chọn morphology/reference thứ hai có license rõ ràng để đánh giá generalization.
5. Chưa thêm chemistry cho đến khi baseline electrical tests pass.

### B. Dendritic computation

- Single synapse; same-branch coincident cluster; distributed multi-branch input; temporal jitter; inhibitory veto.
- Ghi local voltage ở spine head/base, branch proximal/distal, soma/AIS.
- So sánh passive dendrite, NMDA nonlinear dendrite và active Na/Ca variants chỉ khi có tham số hỗ trợ.
- Dùng FCI như một outcome phụ cùng metrics khác.

### C. Calcium-to-plasticity causal loop

NMDAR/CaV → Ca²⁺ → CaM/CaMKII/phosphatase → AMPAR state/trafficking.

Chặn từng mắt xích (NMDAR, CaV, CaMKII, calcineurin) và kiểm tra dự đoán trên calcium transient, plasticity magnitude và EPSP sau kích thích. Dùng STEPS/MCell cho một microdomain khi copy number thấp; so với deterministic ODE.

### D. Synapse-to-nucleus and long-term state

Bắt đầu pathway hẹp: calcium/ERK/CREB → immediate early genes → mRNA/protein → receptor trafficking. Phân biệt local translation và somatic/nuclear transcription; kiểm tra time-course phút–giờ–ngày. Không mở rộng whole-genome trước.

### E. Energetic constraints

Nối firing/synaptic cycling với Na/K pumping, Ca handling, vesicle recycling và ATP demand. So sánh patterns có cùng tổng spike nhưng phân bố thời gian khác nhau; quan sát state/ATP recovery.

## 10. Giả thuyết có thể tạo đóng góp mới

Các hướng sau là giả thuyết, chưa phải kết quả:

- **Adaptive Biological Resolution:** tăng spatial/stochastic resolution ở spine hoặc microdomain đang hoạt động mạnh; giảm ở vùng ít ảnh hưởng, có bound sai số và conservation.
- **Causal Cell Twin:** dự đoán perturbation outcomes, không chỉ fit baseline traces.
- **Energetically Constrained Computation:** đo task performance / adaptation / memory trên một đơn vị năng lượng sinh học.
- **Hybrid differentiable and probabilistic inference:** gradient/Jaxley trên subsystem khả vi, SBI/Bayesian methods trên stochastic subsystem; kiểm tra identifiability.
- **Population digital twins:** dùng distributions về morphology/subtype/synapse, không nhân bản một bộ tham số trung bình.

## 11. Dịch nguyên lý sinh học sang AI — khi đã có bằng chứng

Không trực tiếp chuyển “mỗi neuron có nhiều cơ chế” thành một neural network lớn. Cần tìm cơ chế nhỏ có thể chứng minh có lợi. Các baselines dự kiến: MLP, RNN/GRU/LSTM, TCN, SNN và Transformer thích hợp.

Metrics:
- few-shot/data efficiency;
- continual learning và forgetting;
- temporal integration / delayed response;
- robustness với noise, missing inputs, timing jitter và distribution shift;
- compositional generalization;
- compute, memory và energy;
- mechanistic interpretability.

Phải match task, dataset, parameter budget, exposure/training steps, compute và evaluation protocol. Một thắng lợi trong task nhỏ không cho phép kết luận “vượt Transformer” nói chung.

## 12. Tài liệu tham khảo và nguồn dữ liệu

### Human neuron / FCI
- Eyal et al. 2018: https://pmc.ncbi.nlm.nih.gov/articles/PMC6034553/
- ModelDB 238347: https://modeldb.science/238347
- Model source: https://github.com/ModelDBRepository/238347
- Eyal et al. 2016: https://pmc.ncbi.nlm.nih.gov/articles/PMC5100995/
- Aizenbud et al. 2026, FCI: https://doi.org/10.1073/pnas.2533168123
- FCI code: https://github.com/ido4848/fci
- FCI dataset: https://huggingface.co/datasets/i-do-ai/fci-neuron-simulations
- Planert et al.: https://www.nature.com/articles/s41593-025-02134-7
- Figshare data: https://doi.org/10.6084/m9.figshare.28184126
- Allen Cell Types: https://celltypes.brain-map.org/
- NeuroMorpho: https://neuromorpho.org/

### Simulators / standards
- MOOSE: https://www.mooseneuro.org/
- NEURON docs: https://www.neuronsimulator.org/
- NEURON RxD: https://www.neuronsimulator.org/en/latest/progref/modelspec/programmatic/rxd.html
- Jaxley code: https://github.com/jaxleyverse/jaxley
- Jaxley paper: https://www.nature.com/articles/s41592-025-02895-w
- STEPS: https://steps.sourceforge.net/
- MCell: https://www.mcell.org/
- BRAINCELL: https://github.com/RusakovLab/BRAINCELL
- Arbor: https://arbor-sim.org/
- COPASI: https://copasi.org/
- NeuroML: https://docs.neuroml.org/NeuroMLOrg/Standards.html
- NWB: https://nwb.org/

### Mechanisms / methodology
- Ma et al. 2023, excitation–transcription coupling: https://www.nature.com/articles/s41583-023-00742-5
- Mitochondria–ER contact sites / postsynaptic energy model: https://pmc.ncbi.nlm.nih.gov/articles/PMC8172538/
- Mitochondrial Ca²⁺ efflux and memory (2026): https://www.nature.com/articles/s42255-026-01451-w
- Tolley et al. 2024, simulation-based inference: https://pmc.ncbi.nlm.nih.gov/articles/PMC10919875/
- Simulator comparison on astroglial geometry (2026): https://doi.org/10.1371/journal.pcbi.1014878
- Multiscale co-simulation pattern: https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2024.1156683/full
- Detailed neuronal model workflow: https://pubmed.ncbi.nlm.nih.gov/38035193/

## 13. Trạng thái tại checkpoint này

- Literature/source reconnaissance and architecture proposal are documented.
- No full AMSN simulation was run as part of the v1.0 literature dossier.
- The old Alpha README contains feature/test claims, but its source/test directories were empty when checked; see recovery status.
- The next defensible experiment is reproduction of a published Eyal 2018 NEURON baseline, not adding more unvalidated molecular subsystems.

