# Nghien-cuu — Nolane-x

Kho lưu trữ dài hạn cho các nghiên cứu khoa học, kỹ thuật và kiến trúc AI của dự án Nolane-x.

> **GitHub là bản lưu chuẩn.** Không để kết quả, mã nguồn hay handoff quan trọng chỉ nằm trong hội thoại.

## Bắt đầu từ đây

1. **[AGENTS.md](AGENTS.md)** — quy tắc bắt buộc cho mọi AI agent làm việc trong repo.
2. **[HANDOFF.md](HANDOFF.md)** — hồ sơ nghiên cứu nền và lịch sử recovery.
3. **[HANDOFF_2026-11-20_AMSN-CORE.md](HANDOFF_2026-11-20_AMSN-CORE.md)** — checkpoint mới nhất cho AMSN Neuron Core v0.1.0, lệnh chạy, kiểm thử, giới hạn và việc tiếp theo.
4. **[AMSN Neuron Core](amsn-core/README.md)** — mã nguồn Python đã chạy được, unit tests và ví dụ.
5. **[SWC-to-cable discretization note](research/SWC_TO_CABLE_DISCRETIZATION_2026-11-20.md)** — công thức hình học, cách phân bổ diện tích/điện trở và kiểm chứng giải tích.
6. **[Human L2–3 evidence update](research/HUMAN_L23_EVIDENCE_UPDATE_2026-11-20.md)** — cập nhật nghiên cứu người từ 2025–2026.
7. **[AMSN research dossier](research/AMSN_RESEARCH_DOSSIER.md)** — tổng hợp nghiên cứu AMSN ban đầu.
8. **[Recovery status](research/AMSN_RECOVERY_STATUS_2026-11-20.md)** — trạng thái thực tế của Alpha cũ.
9. **[Research log](research/RESEARCH_LOG.md)** — nhật ký khởi tạo; các log mới được thêm theo ngày.

## Quy tắc bảo toàn dữ liệu

- Ưu tiên append-only: thêm file phiên bản/ngày mới; không xóa hoặc ghi đè tùy tiện.
- Trước khi sửa tệp có sẵn, đọc lại nội dung và blob SHA hiện tại.
- Không force-push, reset lịch sử, xóa nhánh hoặc xóa commit.
- Mọi kết quả phải có nguồn, phiên bản, cấu hình, seed, lệnh chạy, kết quả, giới hạn và commit SHA.
- Phân biệt literature observation, simulation run, validated result, hypothesis và unverified historical claim.
- Không commit credentials, secrets, dữ liệu cá nhân hoặc dữ liệu bệnh nhân định danh.
- Không commit dữ liệu/morphology khi chưa kiểm tra license/terms.
- Mỗi mốc quan trọng phải được lưu lên GitHub ngay trong phiên tạo ra nó.

## Nghiên cứu đang ưu tiên

**AMSN — Adaptive Multi-Scale Neuron:** xây dựng mô hình số đa thang có kiểm chứng cho neuron sinh học; khởi đầu bằng neuron tháp L2–3 vỏ não người, giữ rõ subtype, độ sâu, điều kiện thí nghiệm và uncertainty. Mục tiêu xa hơn là khảo sát nguyên lý tính toán sinh học để thiết kế và kiểm thử kiến trúc AI mới. Không tuyên bố mô hình sinh học vượt Transformer nếu chưa có benchmark công bằng.

## Trạng thái mã nguồn

`amsn-core/` là implementation mới v0.1.0, khác với AMSN Alpha README cũ. Local test suite đạt 21 tests tại checkpoint 20/11/2026 (Python 3.13.5, NumPy 2.3.5, pytest 9.0.2). Đây mới là numerical foundation (SWC parsing/conversion, passive cable tree, HH1952 smoke test), **chưa** phải mô hình neuron người đã hiệu chuẩn và chưa reproduce Eyal 2018.
