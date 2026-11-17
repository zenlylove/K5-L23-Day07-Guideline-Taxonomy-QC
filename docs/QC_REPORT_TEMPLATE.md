# Báo cáo QC — <<TÊN NHÓM>>

Copy vào `submission/qc/QC_REPORT.md`. Giữ tên trường trong các dòng gạch đầu dòng. Thay các chỗ `<<...>>` và điền vòng QC của bản nhãn muốn bàn giao.

## 1. Mục đích, dữ liệu và phiên bản

- Mục đích và giới hạn sử dụng: <<đặc tả và QC nhãn 2D, giới hạn độ đại diện>>
- Nguồn và phép sử dụng dữ liệu: <<xem ATTRIBUTION.csv và lưu ý nếu có>>
- Manifest và checksum nhãn cuối: <<batch_manifest.json và SHA-256>>
- Guideline và taxonomy khi gán / khi bàn giao: <<phiên bản, quyết định đổi hay giữ>>

## 2. Phân công và đồng thuận trước calibration

- Lượt hoàn thành / được giao: <<>>
- Số cặp box ghép, IoU TB, đồng thuận lớp và mẫu số: <<>>
- Box chưa ghép, loại do ignore, bất đồng vùng ignore: <<>>
- Ca hai người có thể cùng sai sau khi đối chiếu tham chiếu: <<ảnh, điều khoản, cách kiểm>>

## 3. Calibration và kiểm lại

- Ca đã xử lý, rule ID, bản sửa và người xác nhận: <<dẫn calibration_decisions.csv>>
- Tác động v1.1 lên nhãn và ảnh: <<phạm vi, mapping nếu cần>>
- Tham chiếu bằng chứng khi Rework: <<vòng cũ, vùng sửa, vòng mới>>

## 4. Kết quả duyệt

- Vòng QC: <<số nguyên, ví dụ 1>>
- Người review và ngày: <<mã, ngày>>
- Đã duyệt / cả lô: <<>>
- Ảnh lỗi / ảnh đã duyệt: <<>>
- Annotation đối tượng hiện có bị lỗi / annotation đối tượng đã duyệt: <<>>
- Vật bỏ sót, ảnh và vùng: <<>>
- Ca khó / phần còn lại, lỗi lặp và ví dụ: <<dẫn phiếu của vòng>>
- Một lỗi máy chặn được và một lỗi cần người đọc ảnh: <<>>

## 5. Quyết định bàn giao

- Quyết định: <<Release hoặc Chưa đủ điều kiện hoặc Rework>>
- Lý do, người nhận và phạm vi sử dụng: <<>>
- Nếu còn việc: <<việc, người xử lý, bằng chứng cần kiểm lại>>
- Kiểm ngược từ báo cáo tới ảnh, rule và nhãn: <<mã ca, đường dẫn, kết quả>>
