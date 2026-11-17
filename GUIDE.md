# Hướng dẫn làm lab

Bài nhóm 2–5 người, **4 giờ**, làm trên **cả 40 ảnh**. Chạy lệnh từ thư mục gốc. Mốc tự kiểm tra: [CHECKPOINTS.md](CHECKPOINTS.md). Chấm điểm: [RUBRIC.md](RUBRIC.md). Quy tắc: [RULES.md](RULES.md).

## Tóm tắt một trang

| Pha | Việc | Lệnh chính | Sản phẩm |
|---|---|---|---|
| 0 (15') | Cài đặt, nhận mã | `pip install -r requirements.txt` | `TEAM.md` |
| 1 (35') | Mỗi người sửa guideline v0 | (đọc 40 ảnh) | `individual/guideline_<mã>.md` |
| 2 (30') | Họp, thống nhất | `make_cvat_labels.py` | `guideline_v1.0_agreed.md`, `taxonomy.json` |
| nghỉ (10') | | | |
| 3 (60') | Chia ảnh, gán độc lập | `split_assign.py`, `validate_labels.py` | `labels/<mã>.json` |
| 4 (20') | So sánh, đo IAA | `qc_compare.py`, `viz_disagreement.py` | `iaa_summary.md`, `calibration_candidates.csv` |
| 5 (40') | Calibration, nhãn cuối | `prepare_calibration.py`, `build_final.py` | `calibration_decisions.csv`, `labels_calibrated.json` |
| 6 (30') | Duyệt QC, bàn giao | `qc_sample.py`, `qc_report.py`, `check_submission.py` | `QC_REPORT.md` |

Mã thành viên có ba chữ số (ví dụ `101`, `102`) và dùng trong tên file. Không dùng họ tên, MSHV hay email.

## Pha 0 — Chuẩn bị

1. `python -m pip install -r requirements.txt`.
2. Đăng nhập CVAT của lớp, mở được ảnh trong `data/images/`.
3. Cả nhóm điền mã vào [TEAM.md](TEAM.md). Hỏi coach kênh nộp riêng.

## Pha 1 — Tìm chỗ guideline còn mơ hồ (độc lập)

1. Mở [guideline v0](guideline/guideline_v0_starter.md) và xem **cả 40 ảnh** (chưa vẽ gì).
2. Với ảnh có **người đi xe máy**: tự quyết định lớp, số box, phần được bao trong từng box. Thử quy tắc ấy trên một ảnh khác.
3. Với xe chở xe, người bị che, vật quá nhỏ, tượng, phản chiếu: ghi ảnh (`img_0xx`), quyết định và lý do. Phân biệt ca **loại theo quy tắc** với ca **cần hỏi reviewer**.
4. Copy [khung guideline](guideline/TEMPLATE_guideline.md) thành `submission/guidelines/individual/guideline_<mã>.md` và viết.
5. **Gửi riêng** theo hướng dẫn coach. Khi cả nhóm đã nộp, mở các bản của nhau để chuẩn bị họp. Giữ bản cá nhân để so với quyết định nhóm.

**Tự kiểm:** người đọc tìm lại được ảnh cho từng ví dụ và biết quyết định ban đầu của bạn.

## Pha 2 — Chốt đặc tả của nhóm (họp)

1. So các bản cá nhân. Chốt quy tắc cho mô hình phát hiện vật trên ảnh 2D: định nghĩa lớp, thuộc tính, phần nhìn thấy, che khuất, cắt mép, ca ngoài phạm vi. Gắn mã `R-01`, `R-02`… cho quy tắc hay được dẫn lại.
2. Lưu `submission/guidelines/guideline_v1.0_agreed.md`.
3. Sửa `submission/taxonomy.json` cho khớp: đặt `version` là `v1.0`, **giữ nguyên mục `rules`** (các ngưỡng).
4. Chạy `python scripts/make_cvat_labels.py` (kiểm schema và sinh `cvat/labels_generated.json`). Báo sai ở trường nào thì sửa đúng trường đó.
5. **Khóa** guideline và taxonomy v1.0 cho lượt gán độc lập.

**Tự kiểm:** cùng một ảnh người đi xe máy, mọi người giải thích cùng quy tắc và dự đoán cùng số box.

## Pha 3 — Chia ảnh và gán độc lập

Một người chạy (thay bằng mã của nhóm), cả nhóm dùng chung `assignment.csv`:

```bash
python scripts/split_assign.py --members 101,102 --copy-images
```

- Nhóm 2–4 người: mỗi ảnh 2 người gán độc lập. Nhóm 5 người: 3 người.
- Ảnh của bạn nằm trong `work/<mã>/images/`; danh sách ở `submission/qc/assignments/<mã>.txt`.

Việc của mỗi người:

1. Tạo Task riêng trong CVAT ([docs/CVAT_SETUP.md](docs/CVAT_SETUP.md)), tải đúng ảnh của mình, gán theo v1.0.
2. Box chưa chắc: tick `can_review`. Chưa vẽ được box: ghi ảnh, vùng, lý do để nhóm thu vào `submission/qc/image_issues.csv` (cột `image,annotator,region,note`) **sau khi khóa nhãn**.
3. Export COCO 1.0, lưu `submission/labels/<mã>.json`, rồi kiểm:
   ```bash
   python scripts/validate_labels.py submission/labels/101.json
   ```
4. **Gửi riêng.** Chỉ tập hợp nhãn của cả nhóm khi tất cả đã nộp.

**Tự kiểm:** số ảnh khớp phân công. Ảnh không có vật vẫn phải có mặt trong COCO.

## Pha 4 — Đọc kết quả đồng thuận

```bash
python scripts/validate_labels.py --all
python scripts/qc_compare.py
python scripts/viz_disagreement.py --images flagged
```

Đọc `submission/qc/iaa_summary.md`:
- Đủ lượt gán chưa? IoU và đồng thuận lớp tính trên **các cặp box ghép được**; không có cặp thì là N/A.
- Mở ảnh chồng nhãn (`work/viz/`): xem box chưa ghép và bất đồng ở vùng `ignore_region`.
- Với mỗi nhóm bất thường: **cả hai cùng lệch** (guideline mơ hồ) hay **một người lệch** (chưa nắm quy tắc)?

Sau khi khóa bản độc lập, đối chiếu ca tham chiếu coach cung cấp: tìm một tình huống hai người làm giống nhau nhưng vẫn **sai** quy tắc.

**Tự kiểm:** bạn giải thích được mẫu số và chỉ ra một điều IAA chưa xác nhận.

## Pha 5 — Chốt ca và tạo nhãn cuối

1. **Quyết định.** Chạy `python scripts/build_final.py` để sinh mẫu `submission/qc/calibration_decisions.csv`. Mỗi ca bất thường **một dòng**:

   | Cột | Ý nghĩa |
   |---|---|
   | `case_id`, `image` | đã điền sẵn |
   | `quyet_dinh` | quyết định của nhóm |
   | `quy_tac_ghi_vao_guideline` | mã quy tắc, ví dụ `R-03` |
   | `phien_ban_guideline` | ví dụ `v1.1` |
   | `nguoi_chot` | mã người chốt |
   | `phieu_sua` | chỗ đã sửa (ảnh, box) |
   | `kiem_lai` | ai kiểm lại và kết quả |
   | `pham_vi` | `anh` (chỉ ảnh đó) hoặc `lo` (quy tắc đổi nghĩa, phải kiểm cả lô) |

   Không có ca nào thì giữ bảng chỉ có header. Nếu phải chạy lại IAA với đầu vào khác, lưu bảng cũ riêng rồi để script tạo lại.
2. **Guideline v1.1.** Lưu `guideline_v1.1_calibrated.md` và `submission/guideline_change.json`:
   ```json
   {"kind": "editorial", "summary": "Sửa câu chữ, giữ nguyên quy tắc"}
   ```
   `kind` là `editorial` (đính chính câu chữ) hoặc `semantic` (đổi cách chọn vật, lớp, box, thuộc tính). `semantic` cần ít nhất một quyết định `pham_vi=lo` và kiểm lại cả lô. Nếu đổi taxonomy: lưu `submission/taxonomy_v1.1.json` (tăng version, ghi cách rà lại) rồi `python scripts/make_cvat_labels.py --final`.
3. **Sửa nhãn.** Chạy `python scripts/prepare_calibration.py`, sửa đúng tập ảnh được chuẩn bị trong CVAT, lưu COCO theo đúng đường dẫn `labels_calibrated_<phiên-bản>.json` mà lệnh in ra. Quyết định hoặc guideline đổi thì chạy lại bước này và lưu vào đường dẫn mới. Không có ảnh cần sửa thì dùng luôn bản đồng thuận.
4. **Nhãn cuối.** Chạy lại `python scripts/build_final.py` → `labels_calibrated.json`, `labels_calibrated.csv`, `batch_manifest.json`.

**Tự kiểm:** mỗi ca có người chốt, dấu vết bản sửa và kết quả kiểm lại; mỗi ảnh xuất hiện đúng một lần ở bản cuối.

## Pha 6 — Duyệt và bàn giao

```bash
python scripts/qc_sample.py --round 1
python scripts/qc_report.py --round 1
```

Giữa hai lệnh: mở ảnh trong `work/review/round-01/`, điền `submission/qc/reviews/round-01/qc_review.csv` (cách điền: [scripts/README.md](scripts/README.md#phiếu-qc)).
Mặc định **duyệt toàn bộ lô**. Người kiểm nên khác người sửa; nhóm 2 người thì đổi vai và ghi rõ.

Kết quả gợi ý, người kiểm xác nhận:

| Quyết định | Khi nào | Làm gì tiếp |
|---|---|---|
| **Chưa đủ điều kiện** | thiếu bằng chứng, guideline chưa chốt, dữ liệu có vấn đề | ghi phần còn thiếu; có thể thêm `--guideline-gap N` / `--data-problem N` |
| **Rework** | > 2% ảnh lỗi hoặc lỗi lặp | thêm ca vào nhật ký (ID `Q01`…), làm lại Pha 5 cho phạm vi cần sửa, rồi `--round 2` (giữ vòng 1) |
| **Release** | số liệu đạt, người kiểm xác nhận | bàn giao kèm báo cáo |

Cuối cùng:
1. Điền [mẫu báo cáo](docs/QC_REPORT_TEMPLATE.md) và [ghi chú cá nhân](docs/INDIVIDUAL_NOTE_TEMPLATE.md).
2. `python scripts/check_submission.py --round 1` (hoặc vòng cuối của nhóm).
3. Nhờ một người ngoài nhóm lần theo một ca từ báo cáo tới ảnh, quy tắc và nhãn.
4. Nộp theo [SUBMISSION.md](SUBMISSION.md).

**Mở rộng:** `python scripts/qc_sample.py --round 99 --n 5 --seed 42` minh họa chọn mẫu ngẫu nhiên. Vòng demo luôn giữ trạng thái **Chưa đủ điều kiện** khi bàn giao.

## Lỗi hay gặp

| Triệu chứng | Cách xử lý |
|---|---|
| `validate_labels` báo lớp lạ | Project CVAT còn bộ nhãn cũ: tạo lại từ `cvat/labels_generated.json`. |
| Thiếu / thừa ảnh | Task phải chứa đúng ảnh trong `assignments/<mã>.txt`. |
| Thiếu thuộc tính sau khi export | Kiểm cấu hình Project, lưu lại box rồi export lại. |
| `build_final` báo IAA đã đổi | Lưu bảng quyết định cũ riêng, để script tạo bảng theo các ca mới. |
