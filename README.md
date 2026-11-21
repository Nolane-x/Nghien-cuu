# Nghien-cuu — Nolane-x

Kho lưu trữ dài hạn cho các nghiên cứu khoa học, kỹ thuật và kiến trúc AI của Nolane-x.

> **GitHub là bản lưu chuẩn.** Mọi mã nguồn, dữ liệu, kết quả và handoff quan trọng phải được lưu tại đây; không để kết quả chỉ tồn tại trong hội thoại.

## Bắt đầu từ đây

1. [AGENTS.md](AGENTS.md) — quy tắc làm việc, bảo toàn dữ liệu và tính trung thực khoa học cho AI agent.
2. [HANDOFF.md](HANDOFF.md) — mục tiêu nghiên cứu tổng thể và lịch sử khôi phục.
3. [HANDOFF_2026-11-21_FINE-MESH-PASSIVE-DC.md](HANDOFF_2026-11-21_FINE-MESH-PASSIVE-DC.md) — checkpoint mới nhất: passive DC cross-validation trên NEURON 0,5 µm, 25.233 segment, 15 cặp source–probe.
   - [Handoff axial conductance matrix](HANDOFF_2026-11-21_FULL-TREE-AXIAL-MATRIX.md) — audit trước đó: 8.893 nút / 8.892 cạnh, ma trận axial sai khác L2 tối đa 6,675e-6.
   - [Handoff full-tree axial network](HANDOFF_2026-11-21_FULL-TREE-AXIAL-NETWORK.md) — audit nền: 8.892/8.892 active SWC edges mapped, 58/58 branchpoints khớp topology.
   - [Handoff AMPA synaptic timing — 20/11](HANDOFF_2026-11-20_AMPA-SYNAPTIC-TIMING-FINAL.md) — baseline lịch sử: 65 test trên Python 3.12/3.13, NEURON 9.0.2 cross-validation và Exp2Syn timing audit.
   - [Handoff AMPA audit ban đầu](HANDOFF_2026-11-20_AMPA-SYNAPTIC-NUMERICS.md) — lịch sử nghiên cứu trước khi hoàn tất kernel timing.
   - [Handoff transient lịch sử](HANDOFF_2026-11-20-HUMAN-TRANSIENT.md) — pulse/step passive cross-validation với NEURON 9.0.2.
4. [Human transient cross-validation report](amsn-core/research/HUMAN_TRANSIENT_CROSS_VALIDATION_2026-11-20.md) — 270 phép đo theo thời gian, sai lệch điện thế probe tối đa 1,48%.
5. [Human transient raw CSV](amsn-core/results/human_transient_cross_validation_2026-11-20.csv).
6. [NEURON temporal/spatial convergence report](amsn-core/research/NEURON_TEMPORAL_SPATIAL_CONVERGENCE_2026-11-20.md) — 540 phép đo, tách sai số thời gian và không gian.
7. [NEURON convergence raw CSV](amsn-core/results/neuron_passive_convergence_2026-11-20.csv).
8. [NEURON passive cross-validation report](amsn-core/research/NEURON_PASSIVE_CROSS_VALIDATION_2026-11-20.md) — diện tích sai khác <0,000001%; sai số điện học tối đa <0,69%.
9. [NEURON raw 15-row CSV](amsn-core/results/neuron_passive_cross_validation_2026-11-20.csv) — các phép đo cross-simulator thô.
10. [HANDOFF_2026-11-20_HUMAN-SECTIONED-MESH.md](HANDOFF_2026-11-20_HUMAN-SECTIONED-MESH.md) — resampler 690 compartment trên morphology người.
11. [Sectioned mesh report](amsn-core/research/SECTIONED_HUMAN_MORPHOLOGY_2026-11-20.md) — số compartment, sai số DC, công thức tích phân và giới hạn.
12. [Raw 60-row CSV](amsn-core/results/human_sectioned_mesh_sensitivity_2026-11-20.csv) — dữ liệu đo thô so với cable 8.903 compartment.
13. [AMSN Neuron Core](amsn-core/README.md) — mã Python, API, test và ví dụ.
14. [Human morphology provenance](amsn-core/data/human/README.md) — nguồn NeuroMorpho, CC BY 4.0, metadata và giới hạn mẫu.
15. [Handoff: human passive DC](HANDOFF_2026-11-20_HUMAN-PASSIVE-DC.md) — 60 phép đo truyền DC.
16. [Handoff: human morphology CI](HANDOFF_2026-11-20_HUMAN-MORPHOLOGY-CI.md) — import morphology người, sửa soma nhiều điểm, CI.
17. [Handoff: electrotonic discretization](HANDOFF_2026-11-20_ELECTROTONIC.md) — refinement theo chiều dài vật lý và điện học.
18. [AMSN research dossier](research/AMSN_RESEARCH_DOSSIER.md) — tổng hợp nền nghiên cứu.
19. [Recovery status](research/AMSN_RECOVERY_STATUS_2026-11-20.md) — trạng thái mã Alpha cũ và những gì còn lại.
20. [Human excitatory-synapse reference](amsn-core/research/HUMAN_EXCITATORY_SYNAPSE_REFERENCE_2026-11-20.md) — tham số AMPA/NMDA L2–3 người, độ biến thiên và giới hạn áp dụng.
21. [AMPA numerical audit log](research/RESEARCH_LOG_2026-11-20_AMPA-NUMERICS.md) — baseline, thất bại kiểm thử được lưu lại, phép thử timing, kết quả cuối và giới hạn.
22. [Exp2Syn kernel timing audit](amsn-core/examples/exp2syn_kernel_timing_audit.py) — cô lập waveform và event timing của NEURON 9.0.2, không trộn với morphology/cable.
23. [Handoff — AMPA temporal convergence](HANDOFF_2026-11-20_AMPA-TEMPORAL-CONVERGENCE.md) — checkpoint mới nhất: audit 5 timestep trên NEURON 0,5 µm và AMSN 2.000 Hz.
24. [Human AMPA temporal convergence report](amsn-core/research/HUMAN_AMPA_TEMPORAL_CONVERGENCE_2026-11-20.md) — sai số tự hội tụ giảm theo timestep; sai số chéo hai engine tiến tới floor gần 0,00385 mV RMS ở basal q90.
25. [Human AMPA temporal raw CSV](amsn-core/results/human_ampa_temporal_convergence_2026-11-20.csv) — 18.615 mẫu voltage/conductance tại 5 timestep, 3 vị trí ghi.
26. [Temporal convergence workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787) — NEURON 9.0.2, 1/1 job thành công.
27. [Handoff — AMPA spatial-floor audit](HANDOFF_2026-11-20_AMPA-SPATIAL-FLOOR.md) — checkpoint mới nhất: sai số dư tại basal q90 và kế hoạch kiểm tra interpolation/area-lumping.
28. [Human AMPA spatial-floor report](amsn-core/research/HUMAN_AMPA_SPATIAL_FLOOR_2026-11-20.md) — sweep 2.000–6.000 Hz ở timestep 1,5625 µs, so với NEURON 0,5 µm.
29. [Spatial-floor raw traces — 2.000 Hz](amsn-core/results/human_ampa_spatial_floor_2026-11-20_2000Hz.csv).
30. [Spatial-floor raw traces — 3.000 Hz](amsn-core/results/human_ampa_spatial_floor_2026-11-20_3000Hz.csv).
31. [Spatial-floor raw traces — 4.000 Hz](amsn-core/results/human_ampa_spatial_floor_2026-11-20_4000Hz.csv).
32. [Spatial-floor raw traces — 6.000 Hz](amsn-core/results/human_ampa_spatial_floor_2026-11-20_6000Hz.csv).
33. [Spatial-floor workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734) — NEURON 9.0.2, 1/1 job thành công.
34. [Handoff — probe interpolation & matched area](HANDOFF_2026-11-20_AMPA-PROBE-INTERPOLATION-AREA.md) — checkpoint mới nhất: tách sai số đọc vị trí và diện tích control-volume.
35. [Probe interpolation report](amsn-core/research/HUMAN_AMPA_PROBE_INTERPOLATION_AUDIT_2026-11-20.md) — interpolation NEURON ảnh hưởng khác nhau ở q75 và q90.
36. [Matched-support area report](amsn-core/research/HUMAN_AMPA_MATCHED_SUPPORT_AREA_AUDIT_2026-11-20.md) — diện tích AMSN/NEURON khớp khi tích phân trên cùng miền hỗ trợ.
37. [Probe interpolation raw — 2.000 Hz](amsn-core/results/human_ampa_probe_interpolation_2026-11-20_2000Hz.csv).
38. [Probe interpolation raw — 4.000 Hz](amsn-core/results/human_ampa_probe_interpolation_2026-11-20_4000Hz.csv).
39. [Probe interpolation raw — 6.000 Hz](amsn-core/results/human_ampa_probe_interpolation_2026-11-20_6000Hz.csv).
40. [Matched-support area raw CSV](amsn-core/results/human_ampa_matched_support_area_2026-11-20.csv).
41. [Probe interpolation workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648) — 1/1 job thành công.
42. [Matched-support area workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776) — 1/1 job thành công.

### Checkpoint mới nhất — 21/11/2026

- [Handoff axial-resistance audit](HANDOFF_2026-11-21_AMPA-AXIAL-RESISTANCE.md) — checkpoint mới nhất, đã chạy CI thành công.
- [Matched-support axial-resistance report](amsn-core/research/HUMAN_AMPA_AXIAL_RESISTANCE_AUDIT_2026-11-21.md) — 15 phép đo trên 5 vị trí basal/apical và 3 mật độ lưới; sai khác axial factor lớn nhất 0,00024%.
- [Raw axial-resistance CSV](amsn-core/results/human_ampa_axial_resistance_2026-11-21.csv) — toàn bộ 15 dòng đo thô.
- [Research log 21/11](research/RESEARCH_LOG_2026-11-21_AMPA-AXIAL-RESISTANCE.md).
- [Axial-resistance audit workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391) — NEURON 9.0.2, 1/1 job thành công.

### Checkpoint mới nhất — full-tree axial audit (21/11/2026)

- [Handoff toàn cây](HANDOFF_2026-11-21_FULL-TREE-AXIAL-NETWORK.md) — tiếp tục từ đây.
- [Báo cáo full-tree axial network](amsn-core/research/HUMAN_FULL_TREE_AXIAL_NETWORK_AUDIT_2026-11-21.md) — 8.892/8.892 cạnh hoạt động được ánh xạ; 58/58 branchpoint khớp child count; 25.233 phép kiểm tra NEURON ri().
- [CSV tóm tắt toàn cây](amsn-core/results/human_full_tree_axial_summary_2026-11-21.csv) — các metric chính để đọc nhanh.
- [Raw artifact gồm 4 CSV](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854/artifacts/14693349082) — edge-level, segment-ri, branchpoint và section-connections.
- [Full-tree workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993854) — NEURON 9.0.2, 1/1 job thành công.
- [Mã audit](amsn-core/examples/human_full_tree_axial_network_audit.py) và [workflow YAML](.github/workflows/amsn-full-tree-axial-network-audit.yml).

### Checkpoint mới nhất — full-tree axial conductance matrix (21/11/2026)

- [Handoff axial matrix](HANDOFF_2026-11-21_FULL-TREE-AXIAL-MATRIX.md).
- [Báo cáo so sánh ma trận axial](amsn-core/research/HUMAN_FULL_TREE_AXIAL_MATRIX_AUDIT_2026-11-21.md) — 8.893 nút / 8.892 cạnh; mean relative operator error 3,53e-6 trên 32 vector kiểm tra.
- [CSV summary](amsn-core/results/human_full_tree_axial_matrix_summary_2026-11-21.csv).
- [Raw edge matrix + vector probes artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672/artifacts/14694905509).
- [Matrix audit workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44872853672) — 1/1 job thành công.
- [Mã audit](amsn-core/examples/human_full_tree_axial_matrix_audit.py) và [workflow](.github/workflows/amsn-full-tree-axial-matrix-audit.yml).

### Checkpoint mới nhất — fine-mesh passive DC (21/11/2026)

- [Handoff fine-mesh passive DC](HANDOFF_2026-11-21_FINE-MESH-PASSIVE-DC.md).
- [Báo cáo passive DC](amsn-core/research/HUMAN_FINE_MESH_PASSIVE_DC_AUDIT_2026-11-21.md) — NEURON 0,5 µm, 15 source–probe pairs, interpolation đọc tại đúng arc SWC.
- [Raw CSV 15 dòng](amsn-core/results/human_fine_mesh_passive_dc_2026-11-21.csv) và [summary metrics](amsn-core/results/human_fine_mesh_passive_dc_summary_2026-11-21.csv).
- [Workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889) — 1/1 job thành công; [artifact](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44873368889/artifacts/14694533497).
- [Mã audit](amsn-core/examples/human_fine_mesh_passive_dc_audit.py).

## Bảo toàn dữ liệu

- Ưu tiên append-only: thêm checkpoint mới; không xóa hoặc ghi đè lịch sử nghiên cứu.
- Đọc nội dung và blob SHA trước khi sửa file có sẵn.
- Không force-push, reset lịch sử hoặc xóa nhánh.
- Mọi kết quả phải có nguồn, dữ liệu, đơn vị, cấu hình, lệnh chạy, log, giới hạn và commit SHA.
- Phân biệt giả thuyết, kết quả tái lập, kết quả đã kiểm chứng và suy luận chưa xác minh.
- Không tuyên bố test hay thí nghiệm thành công nếu chưa có log chạy thực tế.
- Không commit secrets, credentials hoặc dữ liệu cá nhân định danh.
- Kiểm tra license trước khi lưu dữ liệu bên ngoài; giữ nguyên attribution.

## Hướng nghiên cứu ưu tiên

**AMSN — Adaptive Multi-Scale Neuron:** xây dựng mô hình neuron sinh học đa thang có thể kiểm chứng, bắt đầu từ morphology và điện học thụ động của neuron tháp L2–3 vỏ não người. Sau khi xác thực với simulator và dữ liệu thực nghiệm mới mở rộng sang kênh ion chủ động, synapse, calcium, plasticity, gene expression, metabolism và astrocyte coupling. Mục tiêu AI xa hơn cần benchmark công bằng; không suy diễn trí thông minh từ một neuron đơn lẻ.

## Trạng thái hiện tại

- AMSN Core có SWC parser, passive cable/Hines solver, HH1952 numerical smoke test, electrotonic discretizer, section-based resampler và conductance-based synaptic integration (double-exponential/alpha-limit). Synapse được lấy mẫu ở đầu bước theo kết quả kernel audit fixed-step với NEURON 9.0.2.
- Một morphology người thật đã được nhập với provenance CC BY 4.0; mẫu có soma + dendrite, không có axon, dendrite completeness moderate và metadata ghi mesiotemporal sclerosis.
- Section-based resampling giảm cable còn 690 compartments (92,24% ít hơn), với sai số DC tối đa dưới 0,69% so với NEURON 9.0.2 trong protocol thử nghiệm này. Diện tích điện học giữa hai simulator khớp trong 0,000001%. Đây là cross-simulator numerical validation cho một cell/thụ động, chưa phải xác thực sinh học hoặc mô hình neuron hoàn chỉnh.
- Synaptic timing audit: với fixed-step dt=0,025 ms, NetStim start=0 và Exp2Syn 0,2/2,0 ms, conductance NEURON tại t khớp kernel AMSN tại t-dt trong 199/199 mẫu (sai số bằng 0 ở độ chính xác log). Left-edge sampling được giữ trong production solver; AMPA probe relative error hiện 7,41%, chưa có ngưỡng nghiệm thu khoa học.
- [CI run 44754148879](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44754148879) đã xanh ở 4/4 job, gồm 65 test mỗi Python 3.12/3.13 và 2 job NEURON cross-validation.
- Single-compartment voltage/current audit [run 44757208267](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44757208267) đã xanh 2/2 job trên Python 3.12/3.13; voltage sai khác cỡ 10^-15 V trong cấu hình một ngăn được kiểm soát.
- Spatial mesh và NEURON segment refinement [run 44758746509](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44758746509) đã xanh; với NEURON 0,5 µm, q90 RMS mismatch khoảng 0,00384 mV ở dt=0,00625 ms.
- Fast-AMPA temporal convergence [run 44760319787](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44760319787) đã xanh; 5 timestep từ 0,025 đến 0,0015625 ms cho thấy sai số tự hội tụ giảm, trong khi sai số chéo hai engine gần như ổn định quanh 0,00385 mV RMS ở basal q90. Đây là kết quả số học cho một morphology và protocol, không phải xác thực sinh học.
- Fast-AMPA spatial-floor sweep [run 44761379734](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44761379734) đã xanh; tăng AMSN 2.000→6.000 Hz (2.541→4.287 compartment) giảm q90 RMS từ 0,003851 xuống 0,003670 mV nhưng không cải thiện source/soma cùng hướng. Chưa chọn mesh mặc định; bước kế tiếp là kiểm tra interpolation vị trí NEURON và area-lumping quanh protected control points.
- Probe interpolation [run 44762715648](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44762715648) cho thấy nội suy NEURON tới tọa độ SWC giúp q90 ở mesh 2k/4k nhưng không phải 6k, và làm xấu q75; đây là hiệu ứng phụ thuộc vị trí.
- Matched-support area [run 44763720776](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44763720776) cho thấy diện tích control-volume AMSN khớp NEURON trong cùng miền hỗ trợ: q90 sai khác khoảng 0,0000018%, q75 khoảng 0,04–0,05%. So một segment đơn lẻ với cả node trước đó là không cùng miền đo.
- Matched-support axial-resistance audit [run 44870476391](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476391) đã xanh; 15 phép đo trên 5 điểm basal/apical cho thấy sai khác axial geometry factor AMSN/NEURON tối đa 0,000239676%. Chỉ xác nhận các điểm unbranched đã khảo sát, chưa phải biological validation.


### Bổ sung trạng thái — 21/11/2026

- Đã thêm matched-support axial-resistance audit và workflow vào commit `56a731c156db32f6beb35b813e177039d739a850`.
- Audit chuyên biệt đã thành công: 15/15 hàng đo, 5 vị trí trên basal/apical, 3 tần số lưới; sai khác axial geometry factor AMSN/NEURON tối đa 0,000239676%.
- Kết quả loại trừ một sai khác lớn trong tích phân axial cục bộ tại các điểm unbranched đã khảo sát; chưa bao phủ branchpoint, soma, section join, terminal hay toàn bộ cable matrix.
- Bước tiếp theo: đối chiếu toàn bộ axial edge/junction matrix, bao gồm branchpoint, soma, section join và terminal; sau đó reproduce published Eyal 2018 / ModelDB 238347 bằng morphology/mechanism gốc. Không thêm NMDA/calcium/plasticity trước khi baseline điện học được khóa.


- Comprehensive Core CI for code commit `56a731c156db32f6beb35b813e177039d739a850` is now confirmed successful: 65 tests on each of Python 3.12/3.13, module compilation/examples and both NEURON cross-validation jobs all green ([run 44870476392](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476392)).


### Bổ sung kết quả — full-tree axial audit 21/11/2026

- 8.892/8.892 active SWC edges được ánh xạ với NEURON Import3D pt3d; 0 edge không ánh xạ.
- Sai khác axial geometry factor SWC/pt3d có median 0,0001638%, p99 0,0036173%, maximum 0,0152884%; lớn nhất trên một cạnh apical rất ngắn 0,1565 µm, phù hợp với ảnh hưởng precision của pt3d nhưng chưa quy nguyên nhân tuyệt đối.
- 25.233/25.233 NEURON ri records được kiểm tra; sai khác nội bộ cực đại 2,28e-11%.
- 58/58 branchpoints có đúng số child sections; 116 section endpoint bình thường có gap bằng 0; 8 soma wire attachments được báo riêng, không suy diễn chúng có zero biological resistance.
- Kết quả là numerical/topology audit trên một partial morphology, chưa phải biological validation hay bằng chứng tương đương toàn bộ voltage solver.
- Bước tiếp theo: so sánh toàn bộ effective AMSN axial conductance matrix với NEURON, rồi tái tạo ModelDB 238347 bằng morphology/mechanism gốc sau khi xác minh archive/license.


- Comprehensive AMSN Core CI cho code commit `e65a347ef1c51bb44ecbc1deca35c8a4d5712a90` đã xanh 4/4 job: 65 test trên Python 3.12 và 65 test trên Python 3.13; cả hai NEURON 9.0.2 cross-validation đều hoàn tất ([run 44871993797](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44871993797)).


### Kết quả full-tree axial matrix — 21/11/2026

- AMSN và NEURON được quy về cùng đồ thị 8.893 nút điện học và 8.892 cạnh.
- Sai khác conductance tuyệt đối theo cạnh: median 0,0001638%, p95 0,0020371%, p99 0,0036173%, max 0,0152884%.
- 32 vector điện thế với seed cố định cho relative operator L2 error mean 3,531e-6, max 6,675e-6; tổng dòng axial được bảo toàn với residual tối đa 2,396e-21 A.
- Đây là axial-only graph operator, chưa bao gồm leak/capacitance/synapse/active channels và không phải biological validation.
- Thí nghiệm kế tiếp: full-tree passive voltage impact, sau đó source-matched Eyal 2018/ModelDB 238347 nếu archive/license gốc được xác minh.


### Fine-mesh passive DC result — 21/11/2026

- Với NEURON 0,5 µm, total normalized membrane area khớp AMSN ở sai khác −8,426e-7%.
- 15 source–probe pairs: max transfer-ratio error 0,107566% khi đọc nearest segment và 0,093053% khi nội suy probe về SWC arc.
- Source input-response sai khác: soma 0,0000629%, basal q75 0,04324%, apical q75 0,06792%. So với mesh 5 µm, sai khác dendritic giảm khoảng 6–10 lần.
- Source clamp vẫn đặt ở segment gần nhất; sai số vị trí nguồn chưa được loại bỏ. Tiếp theo sweep 0,25/0,125 µm để kiểm tra hội tụ.


### Checkpoint mới — passive frequency-domain impedance (21/11/2026)

- [Handoff frequency-domain impedance](HANDOFF_2026-11-21_PASSIVE-FREQUENCY-RESPONSE.md) — checkpoint tiếp tục mới nhất.
- [Báo cáo frequency-domain](amsn-core/research/HUMAN_PASSIVE_FREQUENCY_RESPONSE_AUDIT_2026-11-21.md) — ma trận 4 lưới đều xanh đến 0,0625 µm; từ 0,5 xuống 0,0625 µm, transfer complex median/p95/max giảm ~20,42×/~6,32×/~6,93×.
- [Mã audit](amsn-core/examples/human_passive_frequency_response_audit.py), [bộ giải complex Hines](amsn-core/src/amsn/cable.py) và [workflow](.github/workflows/amsn-passive-frequency-response-audit.yml).
- [Baseline workflow 0,5 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880205634) và [3-mesh convergence workflow](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858) đều xanh. Raw artifacts: [0,5 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14697044290), [0,25 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14696684877), [0,125 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880470858/artifacts/14697712070), [0,0625 µm](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44880843864/artifacts/14698056883). [Tổng hợp 4 mesh](amsn-core/results/human_passive_frequency_response_mesh_summary_2026-11-21.csv), [số liệu theo tần số](amsn-core/results/human_passive_frequency_response_frequency_summary_2026-11-21.csv). Workflow [0,0625 µm refinement](.github/workflows/amsn-passive-frequency-response-refinement.yml) đã xanh, 74/74 tests pass, 201.021 segment NEURON.


### Checkpoint nguồn mô hình chủ động người — Eyal 2018

- [Eyal 2018 ModelDB source review](amsn-core/research/EYAL_2018_MODELDB_SOURCE_REVIEW_2026-11-21.md) — đã xác minh metadata, 6 tế bào L2/3, AMPA/NMDA, dendritic spines, NMDA spikes và somatic/axonal Na spikes; archive ZIP chính thức 133 MB vẫn đang ở cổng tải và chưa được kiểm tra toàn vẹn.
- [ModelDB 238347](https://modeldb.science/238347), [GitHub source record](https://github.com/ModelDBRepository/238347), [Human Brain Project Human Neurons](https://www.humanbrainproject.eu/en/brain-simulation/human-neurons/).
- Core CI trên baseline `ccde254` đã xanh 4/4 job: [run 44881036875](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44881036875).

- AC solver additional safeguard: 50 Hz fitted sinusoidal transient response is now checked against the phasor solution in the core unit suite (pending the latest CI).

- AC-to-transient invariant is now validated: 50 Hz sinusoidal phasor test passed; latest Core CI [44882886045](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44882886045) green 4/4, 75 tests on Python 3.12 and 3.13.
- Eyal 2018 ModelDB archive: official URL confirmed, but Yale legacy domain timed out; linked GitHub repo tree contains README only. No source archive downloaded or integrated.


### Multi-morphology checkpoint — Segev archive (21/11/2026)

- [FCI Eyal-labelled derivative audit](amsn-core/research/FCI_EYAL_DERIVATIVE_SOURCE_AUDIT_2026-11-21.md): source provenance, SI parameter conversion, reduced HOC, channel scaling, synapse kinetics and licensing caveats.
- [NMO_68174 cell 1125](amsn-core/data/human/segev/2013_03_06_cell11_1125_H41_06.CNG.swc) and [NMO_68175 cell 1204](amsn-core/data/human/segev/2013_03_13_cell03_1204_H42_02.CNG.swc): direct NeuroMorpho CC BY 4.0 morphology fixtures; dendrites moderate and axons incomplete.
- [Source manifest](amsn-core/research/references/FCI_EYAL_SOURCE_MANIFEST_2026-11-21.json) pins third-party source SHA and morphology blob hashes.
- [New dated handoff](HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md).


### Multi-morphology checkpoint — Segev archive (21/11/2026)

- [FCI Eyal-labelled derivative audit](amsn-core/research/FCI_EYAL_DERIVATIVE_SOURCE_AUDIT_2026-11-21.md): provenance, SI parameter conversions, reduced HOC, channel/synapse and license notes.
- [NMO_68174](amsn-core/data/human/segev/2013_03_06_cell11_1125_H41_06.CNG.swc) and [NMO_68175](amsn-core/data/human/segev/2013_03_13_cell03_1204_H42_02.CNG.swc): official NeuroMorpho CNG morphologies, CC BY 4.0, incomplete axons.
- [Four-job 0.25/0.125 µm validation](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44885009077) is running; results not yet accepted.
- New handoff: [HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md](HANDOFF_2026-11-21_FCI-EYAL-DERIVATIVE.md).


### Segev multi-morphology Import3D correction — verified

The NMO_68175 mismatch was traced to the immediately branching axon attachment at SWC node 5851. The final soma normalizer collapses that first-point branch junction while retaining a one-point terminal neurite. Passive parameters were not changed. The follow-up 0.0625 µm workflow also passed both cells with 81 tests each; remaining percentile changes are not fully monotone and are recorded in the final report.

- Four-job matrix [44887065310](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310) passed on NEURON 9.0.2 (two morphologies × two mesh caps).
- Area agreement: NMO_68174 −0.00000112%; NMO_68175 −0.00000080%.
- NMO_68175 at 0.125 µm: max input complex error 0.03774%, max transfer complex error 0.16938%; before fix these maxima were ~5.69% and ~5.70%.
- Raw artifacts: [68174/0.25](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310/artifacts/14699778704), [68175/0.25](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310/artifacts/14699833538), [68174/0.125](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310/artifacts/14699989410), [68175/0.125](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065310/artifacts/14700104294).
- Core CI [44887065325](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44887065325) passed 4/4 jobs; 81 tests on both Python 3.12 and 3.13; full NEURON passive/transient/AMPA/Exp2Syn/single-compartment validation passed.
- See [final multi-morphology audit](amsn-core/research/HUMAN_MULTI_MORPHOLOGY_AUDIT_2026-11-21.md), [summary CSV](amsn-core/results/human_segev_import3d_attachment_fix_summary_2026-11-21.csv) and [handoff](HANDOFF_2026-11-21_SEGEV-MORPHOLOGY-VALIDATION.md).
