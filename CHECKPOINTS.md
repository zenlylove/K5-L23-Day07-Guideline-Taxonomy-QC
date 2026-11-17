# Checkpoints — Day 07

Bài **nhóm 2–5 người**, 240 phút. Mốc tính từ lúc bắt đầu, là điểm tự kiểm tra tại lớp, **không phải hạn nộp**.

| Mốc | Mục tiêu | Tự kiểm tra |
|---|---|---|
| 0:15 | **CP0** Chuẩn bị | Mở được ảnh, đăng nhập CVAT, mỗi người có mã và biết kênh nộp riêng. |
| 0:50 | **CP1** Guideline cá nhân | Mỗi người có guideline riêng và giải thích được một ảnh ca khó. |
| 1:20 | **CP2** Guideline thống nhất | v1.0 và `taxonomy.json` đã khóa; `make_cvat_labels.py` chạy được. |
| 1:30 | Nghỉ | |
| 2:30 | **CP3** Gán độc lập | Mỗi người đã export COCO và `validate_labels.py` sạch; đã nộp riêng trước khi tập hợp. |
| 2:50 | **CP4** IAA | Đủ lượt gán; đọc được mẫu số IAA; đã xem một ca tham chiếu. |
| 3:30 | **CP5** Calibration | Có quyết định mỗi ca, guideline v1.1, nhãn cuối và `batch_manifest.json`. |
| 4:00 | **CP6** QC và nộp | Đã ghi số ảnh duyệt, quyết định, lý do; người khác mở được gói đúng vòng QC. |

## Cần hiểu ở mỗi mốc

- **CP1:** chỗ nào v0 làm hai người hiểu khác nhau? Mức thuộc tính của bạn có ngưỡng đo được chưa?
- **CP2:** phép thử lớp / thuộc tính: *"mô hình có phải đoán ra điều này không?"* Ca ngoài taxonomy xử lý thế nào, và cả nhóm có **cùng một** cách không?
- **CP3:** vì sao phải gán độc lập? Script kiểm được gì và **không** kiểm được gì (box có ôm sát vật không)?
- **CP4:** IAA thấp thì sửa guideline hay sửa người gán? Dấu hiệu nào phân biệt?
- **CP5:** quyết định nào là quy tắc mới phải vào guideline? Thiếu dòng ghi quyết định thì sau này nhóm tranh luận lại đúng ca đó.
- **CP6:** tỉ lệ lỗi **theo ảnh** khác **theo đối tượng** thế nào, vì sao luôn ghi mẫu số? Cây quyết định đi theo thứ tự Chưa đủ điều kiện → Rework → Release.

Nếu CVAT chậm hoặc thiếu quyền Review, báo coach. Dùng ảnh chồng box và phiếu CSV để tiếp tục xem ca. Chi tiết lệnh: [GUIDE.md](GUIDE.md).
