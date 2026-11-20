# Nghien-cuu — Nolane-x

Kho lưu trữ dài hạn cho các nghiên cứu khoa học, kỹ thuật và kiến trúc AI của dự án Nolane-x.

> **Nguyên tắc quan trọng:** GitHub là bản lưu chuẩn. Mọi nghiên cứu mới, kết quả thử nghiệm, mã nguồn, dữ liệu có thể phân phối và hướng tiếp tục phải được ghi vào kho này ngay trong phiên làm việc tạo ra chúng. Không dựa vào lịch sử hội thoại làm nơi lưu duy nhất.

## Bắt đầu từ đây

1. **[HANDOFF.md](HANDOFF.md)** — bàn giao đầy đủ cho AI/phiên làm việc mới: mục tiêu, trạng thái thật, phát hiện, giới hạn, việc cần làm và quy trình tiếp tục.
2. **[research/AMSN_RESEARCH_DOSSIER.md](research/AMSN_RESEARCH_DOSSIER.md)** — hồ sơ nghiên cứu AMSN: neuron tháp vỏ não người, công cụ mô phỏng, kiến trúc đa thang, lỗ hổng, kế hoạch kiểm chứng và benchmark AI.
3. **[research/RESEARCH_LOG.md](research/RESEARCH_LOG.md)** — nhật ký nghiên cứu theo ngày.
4. **[research/AMSN_RECOVERY_STATUS_2026-11-20.md](research/AMSN_RECOVERY_STATUS_2026-11-20.md)** — đối chiếu những gì còn tồn tại và những gì chưa thể xác minh trong bản Alpha cũ.

## Các nguyên tắc lưu trữ không được phá vỡ

- **Ưu tiên append-only:** thêm file phiên bản/ngày mới; không xóa, không ghi đè tài liệu cũ nếu không thực sự cần.
- Trước khi sửa một file đã có, phải đọc lại file và SHA hiện tại; ghi nhận lý do sửa. Khi có thể, tạo file mới như `HANDOFF_YYYY-MM-DD.md` hoặc `experiment_name_v2.md`.
- Không force-push, không reset lịch sử, không xóa nhánh/commit để “dọn repo”.
- Mỗi kết quả phải ghi: câu hỏi, giả thuyết, nguồn, phiên bản phần mềm, cấu hình, seed, lệnh chạy, kết quả, giới hạn và kết luận.
- Phân biệt rõ **đã đọc nguồn**, **đã chạy thử**, **đã kiểm chứng**, **giả thuyết**, **chưa xác minh**. Không biến kế hoạch thành kết quả.
- Không ghi API key, token, mật khẩu, dữ liệu cá nhân hoặc dữ liệu bệnh nhân có thể định danh vào repo.
- Dữ liệu ngoài phải có provenance và điều khoản sử dụng. Không commit dữ liệu/morphology khi chưa xác minh license.
- Với nghiên cứu nhiều bước, cập nhật checkpoint vào GitHub ngay sau từng mốc có giá trị; không chờ đến cuối phiên.
- Sau mỗi lần ghi, kiểm tra URL/path và commit SHA trả về. Không nói “đã lưu” nếu thao tác GitHub thất bại.

## Nghiên cứu hiện được ưu tiên

**AMSN — Adaptive Multi-Scale Neuron:** nghiên cứu mô hình số đa thang có kiểm chứng cho neuron sinh học, khởi đầu bằng neuron tháp lớp 2/3 vỏ não người. Mục tiêu xa hơn là tìm và kiểm tra các nguyên lý tính toán sinh học có thể chuyển hóa thành kiến trúc AI mới. Chưa có bằng chứng rằng một neuron mô phỏng sẽ vượt Transformer; mọi kết luận như vậy phải dựa trên benchmark công bằng.

## Trạng thái khởi tạo

Kho này được kiểm tra ngày **20/11/2026** và GitHub báo repository rỗng trước khi lưu tài liệu nền. Các file khởi tạo trong commit đầu tiên chỉ là tài liệu nghiên cứu/handoff, không phải mã mô phỏng đã chạy.

