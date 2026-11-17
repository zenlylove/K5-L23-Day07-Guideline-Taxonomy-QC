# Lệnh và bằng chứng Day 07

Chạy từ thư mục gốc sau khi cài `requirements.txt`. [GUIDE.md](../GUIDE.md) giải thích thời điểm chạy từng lệnh. Mọi script có `--help`.

## Thứ tự chạy

| Pha | Lệnh | Đầu ra chính |
|---|---|---|
| 2 | `python scripts/make_cvat_labels.py` | kiểm JSON Schema, sinh `cvat/labels_generated.json`; `--final` dùng taxonomy sau calibration |
| 3 | `python scripts/split_assign.py --members 101,102 --copy-images` | `assignment.csv`, danh sách từng mã, ảnh trong `work/<mã>/images/` |
| 3 | `python scripts/validate_labels.py submission/labels/101.json` | đối chiếu COCO, hình học, lớp, thuộc tính, đúng tập ảnh của thành viên |
| 4 | `python scripts/qc_compare.py` | độ phủ, IAA, ca cần xem, ảnh bị cờ, nháp đồng thuận; dừng nếu thiếu lượt gán |
| 4 | `python scripts/viz_disagreement.py --images flagged` | ảnh chồng nhãn từng người trong `work/viz/` |
| 5 | `python scripts/build_final.py` | lần đầu: mẫu quyết định; sau đó: COCO/CSV nhãn cuối và manifest |
| 5 | `python scripts/prepare_calibration.py` | ảnh cần sửa, COCO nháp, đường dẫn export có mã phiên bản |
| 6 | `python scripts/qc_sample.py --round 1` | mẫu, phiếu, ảnh overlay, bản chụp nhãn và manifest của vòng |
| 6 | `python scripts/qc_report.py --round 1` | số đo, `qc_result.json`, gợi ý quyết định |
| 6 | `python scripts/check_submission.py --round 1` | kiểm trường bắt buộc của báo cáo; đối chiếu quyết định với nhãn và phiếu hiện hành |

Ghi chú:
- Chia ảnh: K = 2 người/ảnh; nhóm 5 người K = 3. Cùng mã và `--seed` thì ra cùng bảng chia.
- `viz_disagreement.py` cũng nhận `--images all`, tên ảnh cụ thể, `--source consensus|final`.
- `qc_sample.py` mặc định duyệt **toàn lô**. `--n` chỉ để demo (kết quả là Chưa đủ điều kiện). Vòng đã có thì dùng số vòng mới.
- `qc_report.py` nhận thêm `--guideline-gap N`, `--data-problem N` (dẫn tới Chưa đủ điều kiện). Quyết định chỉ là **gợi ý**.

## Phiếu QC

File `submission/qc/reviews/round-NN/qc_review.csv`, cột: `image, object_id, error_type, reviewer, rule_id, region, note`.

| Tình huống | Cách ghi |
|---|---|
| Ảnh sạch | một dòng: `image`, `error_type=khong`, `reviewer` |
| Lỗi trên box | một dòng mỗi loại lỗi: `object_id` (in trên ảnh QC), `rule_id`, `note`; `error_type` là `thua`, `sai_lop`, `sai_vi_tri_kich_thuoc` hoặc `sai_thuoc_tinh` |
| Vật bỏ sót | `error_type=bo_sot`, **để trống** `object_id`, ghi `region` đủ cụ thể để tìm vật, kèm `rule_id`, `note`. Nhiều vật gần nhau: mỗi vật một mô tả vùng |

- `reviewer` là mã ba chữ số trên **mọi** dòng.
- Cần sửa nhãn: cập nhật quyết định, lưu COCO theo phiên bản do `prepare_calibration.py` in ra, chạy `build_final.py`, rồi mở vòng mới. Phiếu vòng trước đi cùng bản chụp nhãn cũ.

## Script kiểm được gì, không kiểm được gì

- **Kiểm được:** tên file / mã, lớp và thuộc tính trong taxonomy, box trong ảnh, box quá nhỏ, đủ lượt gán, độ lệch giữa người gán (IoU, lớp, thuộc tính, bỏ sót / thừa), phiên bản bằng chứng, các số đo QC.
- **Không kiểm được:** box có ôm sát vật thật không; lớp có đúng thực tế không; vật mà **cả nhóm cùng bỏ sót**; mọi người **cùng hiểu sai** quy tắc. Cần mắt người đối chiếu guideline và ảnh gốc.

## Lưu ý định dạng CVAT

Script map lớp theo **tên** và ảnh theo **tên file** (bỏ tiền tố thư mục). Thuộc tính `occluded_level`, `truncated`, `can_review` được chuẩn hoá. Cờ `occluded` sẵn của CVAT bị bỏ qua. Ảnh có trong `images` nhưng không có annotation được hiểu là "đã gán, không có vật".

## Kiểm thử

`python -m unittest discover -s tests -v` (xem [ma trận kiểm thử](../docs/TEST_MATRIX.md)).
