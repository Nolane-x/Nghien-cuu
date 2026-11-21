# Nghien-cuu — Nolane-x

Kho lưu trữ dài hạn cho các nghiên cứu khoa học, kỹ thuật và kiến trúc AI của Nolane-x.

> **GitHub là bản lưu chuẩn.** Mọi mã nguồn, dữ liệu, kết quả và handoff quan trọng phải được lưu tại đây; không để kết quả chỉ tồn tại trong hội thoại.

## Bắt đầu từ đây

1. [AGENTS.md](AGENTS.md) — quy tắc làm việc, bảo toàn dữ liệu và tính trung thực khoa học cho AI agent.
2. [HANDOFF.md](HANDOFF.md) — mục tiêu nghiên cứu tổng thể và lịch sử khôi phục.
3. [HANDOFF_2026-11-20_AMPA-SYNAPTIC-TIMING-FINAL.md](HANDOFF_2026-11-20_AMPA-SYNAPTIC-TIMING-FINAL.md) — checkpoint mới nhất đã xác minh: 65 test trên Python 3.12/3.13, NEURON 9.0.2 cross-validation và Exp2Syn timing audit đều xanh.
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
- Bước tiếp theo là kiểm chứng axial-resistance integrals trên chính các nửa cạnh q75/q90 và mở rộng sang nhánh basal/apical khác; chưa chọn mesh mặc định và chưa tuyên bố biological validation.


### Bổ sung trạng thái — 21/11/2026

- Đã thêm matched-support axial-resistance audit và workflow vào commit `56a731c156db32f6beb35b813e177039d739a850`.
- Audit chuyên biệt đã thành công: 15/15 hàng đo, 5 vị trí trên basal/apical, 3 tần số lưới; sai khác axial geometry factor AMSN/NEURON tối đa 0,000239676%.
- Kết quả loại trừ một sai khác lớn trong tích phân axial cục bộ tại các điểm unbranched đã khảo sát; chưa bao phủ branchpoint, soma, section join, terminal hay toàn bộ cable matrix.
- Xem handoff mới nhất để biết thí nghiệm toàn cây tiếp theo. Không xem đây là biological validation.


- Comprehensive Core CI for code commit `56a731c156db32f6beb35b813e177039d739a850` is now confirmed successful: 65 tests on each of Python 3.12/3.13, module compilation/examples and both NEURON cross-validation jobs all green ([run 44870476392](https://github.com/Nolane-x/Nghien-cuu/actions/runs/44870476392)).
