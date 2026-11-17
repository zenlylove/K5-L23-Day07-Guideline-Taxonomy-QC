# Báo cáo QC — Poseidon

## 1. Mục đích, dữ liệu và phiên bản

- Mục đích và giới hạn sử dụng: Thực hành đặc tả và QC nhãn bounding box 2D; bộ ảnh tuyển chọn, chưa đánh giá tính đại diện cho dữ liệu vận hành.
- Nguồn và phép sử dụng dữ liệu: Theo `data/ATTRIBUTION.csv`; chưa thay đổi phạm vi sử dụng.
- Manifest và checksum nhãn cuối: Chưa có `submission/qc/batch_manifest.json` hoặc nhãn cuối đã hiệu chỉnh; chưa có checksum bàn giao.
- Guideline và taxonomy khi gán / khi bàn giao: Gán độc lập v1.0; v1.1 thay đổi ngữ nghĩa R-02 về pickup có camper/canopy, đang chờ rà toàn bộ lô trước bàn giao.

## 2. Phân công và đồng thuận trước calibration

- Lượt hoàn thành / được giao: 80/80 lượt, 40 ảnh, 2 người gán.
- Số cặp box ghép, IoU TB, đồng thuận lớp và mẫu số: 151 cặp; IoU TB 0.922; cùng lớp 100%; mẫu số 151.
- Box chưa ghép, loại do ignore, bất đồng vùng ignore: 0/0 box chưa ghép; 0 box bỏ qua do ignore; 0 bất đồng vùng ignore.
- Ca hai người có thể cùng sai sau khi đối chiếu tham chiếu: `img_017` không có annotation ở cả hai bộ, phù hợp quy tắc không gán tượng là `person`; `img_021` có nguy cơ bỏ sót chung do chỉ có 7 box trong cảnh đông, cần rà ảnh gốc theo R-03/R-10.

## 3. Calibration và kiểm lại

- Ca đã xử lý, rule ID, bản sửa và người xác nhận: 14 ca trong `submission/qc/calibration_decisions.csv`; phạm vi dự kiến 40/40 do thay đổi R-02. Chưa có bản sửa CVAT hoặc xác nhận hoàn tất.
- Tác động v1.1 lên nhãn và ảnh: Quy tắc phân lớp pickup gắn camper/canopy được làm rõ; cần rà toàn bộ 40 ảnh. Chưa có nhãn cuối v1.1.
- Tham chiếu bằng chứng khi Rework: Chưa có vòng Rework; chưa ghi nhận ca sửa trong vòng QC.

## 4. Kết quả duyệt

- Vòng QC: 1
- Người review và ngày: Chưa có lượt review được ghi nhận; chưa xác định ngày review.
- Đã duyệt / cả lô: 0/40; vòng 1 chưa khởi tạo vì thiếu nhãn cuối và `batch_manifest.json`.
- Ảnh lỗi / ảnh đã duyệt: Chưa đo; 0/0 ảnh đã review.
- Annotation đối tượng hiện có bị lỗi / annotation đối tượng đã duyệt: Chưa đo; 0/0 annotation đã review.
- Vật bỏ sót, ảnh và vùng: Chưa có phiếu review; `img_021` là ca cần kiểm tra độ đầy đủ theo ảnh gốc. Có ghi nhận nhiều nhãn trùng và box đặt trên vùng ảnh mờ; chưa đếm hoặc gắn với object ID/ảnh cụ thể.
- Ca khó / phần còn lại, lỗi lặp và ví dụ: Chưa hoàn tất review calibration. Các ảnh đông và `img_037` cần được kiểm theo `calibration_decisions.csv`. Ghi nhận nhãn trùng/vùng ảnh mờ chưa được xác minh bằng phiếu có ảnh và object ID.
- Một lỗi máy chặn được và một lỗi cần người đọc ảnh: Máy chặn vòng QC khi thiếu manifest; nhãn trùng và box trên vùng mờ cần người đọc ảnh, ghi đúng object ID/vùng và xác nhận trong phiếu.

## 5. Quyết định bàn giao

- Quyết định: Chưa đủ điều kiện
- Lý do, người nhận và phạm vi sử dụng: Chưa có bản nhãn calibration được xuất và xác thực, chưa có manifest, chưa duyệt 40/40 ảnh; không dùng làm nhãn phát hành.
- Nếu còn việc: Hoàn tất rà/sửa 40 ảnh trong CVAT, xuất COCO theo đúng hash, chạy `build_final.py`, tạo vòng QC mới và điền phiếu theo ảnh/rule thực tế. `submission/qc/qc_result_blocked.json` chỉ ghi trạng thái chặn hiện tại, không thay thế kết quả chính thức của `qc_report.py`.
- Kiểm ngược từ báo cáo tới ảnh, rule và nhãn: `img_021` → `work/viz/img_021.png` và R-03/R-10; `img_017` → `work/viz/img_017.png` và R-01/R-12; nhãn cuối chưa tồn tại để kiểm đối chiếu.
