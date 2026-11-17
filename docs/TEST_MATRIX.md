# Kiểm thử Day 07

Chạy `python -m unittest discover -s tests -v` sau khi cài `requirements.txt`.

| Bằng chứng | Cách kiểm |
|---|---|
| Đủ ảnh và lượt gán độc lập | Fixture thiếu ảnh hoặc người thứ ba bị dừng trước IAA. Vùng ignore bất đồng được gắn cờ, kể cả khi hai vùng ghép được nhưng chỉ một vùng phủ box. |
| Schema và phạm vi ảnh | Kiểm taxonomy, kích thước ảnh, bbox, thuộc tính và đúng ảnh trong phân công. |
| Đổi guideline/taxonomy | Nhãn cũ chưa xử lý và export sửa chỉ một phần lô bị chặn khi quy tắc đổi nghĩa. Bảng quyết định cũ bị chặn nếu đầu vào IAA thay đổi. Export cũ bị chặn khi quyết định hoặc guideline đổi dù phạm vi ảnh giữ nguyên. |
| Nghiệm thu lô | Phiếu trống, thiếu IAA, vòng demo hoặc bằng chứng lệch phiên bản dẫn đến Chưa đủ điều kiện, kể cả khi bản chụp quyết định calibration đã đổi. Vòng đầy đủ và QC sạch có thể Release. JPEG bị cắt dữ liệu bị chặn. Lỗi tạo ảnh chồng box cho phép chạy lại cùng số vòng. |
| Rework và truy vết | Sửa ảnh ban đầu không bị cờ, sinh lại cả COCO/CSV, giữ phiếu và nhãn vòng cũ. Lỗi bỏ sót có số đếm riêng. Báo cáo bàn giao thiếu trường bắt buộc bị từ chối. |
| Chạy thử trên CVAT của lớp | Coach kiểm export/import, thuộc tính, ảnh rỗng, quyền Review và thời gian qua [hướng dẫn chuẩn bị](COACH_GUIDE.md). |
