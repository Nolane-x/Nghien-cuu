# Nghien-cuu — Nolane-x

Kho lưu trữ dài hạn cho các nghiên cứu khoa học, kỹ thuật và kiến trúc AI của Nolane-x.

> **GitHub là bản lưu chuẩn.** Mọi mã nguồn, dữ liệu, kết quả và handoff quan trọng phải được lưu tại đây; không để kết quả chỉ tồn tại trong hội thoại.

## Bắt đầu từ đây

1. [AGENTS.md](AGENTS.md) — quy tắc làm việc, bảo toàn dữ liệu và tính trung thực khoa học cho AI agent.
2. [HANDOFF.md](HANDOFF.md) — mục tiêu nghiên cứu tổng thể và lịch sử khôi phục.
3. [HANDOFF_2026-11-20_AMPA-SYNAPTIC-NUMERICS.md](HANDOFF_2026-11-20_AMPA-SYNAPTIC-NUMERICS.md) — checkpoint mới nhất: sửa quy ước lấy mẫu synapse, alpha-function limit, tham chiếu AMPA/NMDA người và trạng thái CI cần kiểm tra.
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
21. [AMPA numerical audit log](research/RESEARCH_LOG_2026-11-20_AMPA-NUMERICS.md) — sai số baseline, code change và validation pending.

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

- AMSN Core có SWC parser, passive cable/Hines solver, HH1952 numerical smoke test, electrotonic discretizer, section-based resampler và conductance-based synaptic integration (double-exponential/alpha-limit).
- Một morphology người thật đã được nhập với provenance CC BY 4.0; mẫu có soma + dendrite, không có axon, dendrite completeness moderate và metadata ghi mesiotemporal sclerosis.
- Section-based resampling giảm cable còn 690 compartments (92,24% ít hơn), với sai số DC tối đa dưới 0,69% so với NEURON 9.0.2 trong protocol thử nghiệm này. Diện tích điện học giữa hai simulator khớp trong 0,000001%. Đây là cross-simulator numerical validation cho một cell/thụ động, chưa phải xác thực sinh học hoặc mô hình neuron hoàn chỉnh.
