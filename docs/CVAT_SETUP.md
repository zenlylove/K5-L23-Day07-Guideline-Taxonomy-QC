# CVAT và COCO cho Day 07

Dùng instance CVAT do lớp chỉ định (coach đã kiểm quyền tạo Task và xuất / nhập COCO). Khi chia sẻ artifact, dùng **mã thành viên**.

## 1. Tạo Project

1. `python scripts/make_cvat_labels.py` → `cvat/labels_generated.json`.
2. **Projects → Create new project → Labels → Raw**: dán nội dung file, lưu.
3. Kiểm: mỗi lớp có `occluded_level`, `truncated`, `can_review` (riêng `ignore_region` không cần thuộc tính).

Tên nhãn trong CVAT phải trùng `taxonomy.json`. Dùng nguyên cấu hình do script sinh: mỗi lớp là `rectangle`, checkbox `can_review` có hai giá trị `true`/`false` theo định dạng Raw của CVAT.

## 2. Tạo Task gán độc lập

1. **Create new task**, chọn Project, tải ảnh trong `work/<mã>/images/`.
2. Số frame phải bằng số dòng trong `submission/qc/assignments/<mã>.txt`.

| Phím | Việc |
|---|---|
| `N` | vẽ box (chọn **Rectangle**, lớp, thuộc tính) |
| `F` / `D` | ảnh sau / ảnh trước |
| `Ctrl` + `S` | lưu (có thể khác tuỳ máy) |

- Gán `occluded_level` của nhóm. Cờ occluded có sẵn của CVAT (phím `Q`) là trường **khác**, script bỏ qua.
- Vùng bỏ qua: Rectangle lớp `ignore_region`.
- Box mơ hồ: tick `can_review`.
- Chưa vẽ được box: ghi vấn đề cấp ảnh (ảnh, vùng, lý do) để nhóm thu vào `image_issues.csv`.
- Ảnh không có đối tượng: vẫn nằm trong Task.

## 3. Xuất COCO 1.0

1. **Actions → Export task dataset**: format **COCO 1.0**, **tắt** Save images.
2. Tải file ở trang **Requests**, giải nén, lấy `annotations/instances_<subset>.json` (thường là `instances_default.json`).
3. Lưu thành `submission/labels/<mã>.json` (ví dụ `101.json`).
4. `python scripts/validate_labels.py submission/labels/101.json`. Kiểm kỹ ảnh trống và các trường trong `attributes`.

## 4. Sửa ca calibration

1. Điền `calibration_decisions.csv`, rồi `python scripts/prepare_calibration.py`. Tạo Task từ `work/calib/images/`.
2. Taxonomy đổi: tạo Project từ `cvat/labels_final.json` (do `make_cvat_labels.py --final` sinh).
3. Nếu có `work/calib/consensus_flagged.json`: **Actions → Upload annotations → COCO 1.0**. Nếu schema không còn tương thích, áp dụng mapping hoặc gán lại theo quyết định.
4. Nếu instance có **Review mode**: mở issue trên box hoặc vùng ảnh, ghi mã ca, mã quy tắc, cách sửa, kết quả reviewer kiểm lại. Thiếu quyền Review thì dùng ảnh chồng box và CSV.
5. Xuất COCO 1.0, lưu theo đường dẫn có mã phiên bản mà `prepare_calibration.py` in ra. Giữ nguyên tên ảnh.

## Gỡ rối

- Thiếu thuộc tính trong JSON: kiểm cấu hình Project, lưu lại box rồi export lại.
- Tên file có tiền tố thư mục: bình thường, script bỏ tiền tố.
- Export báo lỗi: chờ vài giây rồi tải lại ở trang Requests.

Tham khảo: [COCO trong CVAT](https://docs.cvat.ai/docs/manual/advanced/formats/format-coco/) · [Manual QA](https://docs.cvat.ai/docs/qa-analytics/manual-qa/)
