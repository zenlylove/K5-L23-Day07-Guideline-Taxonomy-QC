# Rubric — 100 điểm

Chấm theo **bằng chứng** và cách giải thích. Chưa đủ điều kiện hoặc Rework có căn cứ vẫn có thể được điểm tốt. Phần cá nhân coach xem theo từng mã thành viên.

| # | Hạng mục | Điểm | Bằng chứng |
|---|---|---:|---|
| 1 | Guideline cá nhân | 15 | `individual/guideline_<mã>.md` |
| 2 | Guideline nhóm và taxonomy | 20 | `guideline_v1.0_agreed.md`, `taxonomy.json` |
| 3 | Phân công và gán độc lập | 15 | `assignment.csv`, `labels/<mã>.json` |
| 4 | IAA và calibration | 25 | `iaa_summary.md`, `calibration_decisions.csv`, `guideline_v1.1`, nhãn cuối |
| 5 | QC và báo cáo | 15 | `reviews/round-*/`, `QC_REPORT.md` |
| 6 | Tái lập và hợp tác | 10 | gói bàn giao, `check_submission.py`, `individual_notes/` |

## 1. Guideline cá nhân (15)
- 6: ca thật có ID ảnh và lập luận.
- 5: định nghĩa lớp, ví dụ và phản ví dụ; mức thuộc tính đo được.
- 4: cấu trúc rõ.

## 2. Guideline nhóm và taxonomy (20)
- 5: đặc tả đủ.
- 6: giải quyết bất đồng giữa các bản cá nhân, có lý do.
- 5: quy tắc ca biên (ngoài taxonomy, vật không thật, che / cắt mép, vật nhỏ / đám đông).
- 4: taxonomy khớp guideline và có phiên bản.

## 3. Phân công và gán độc lập (15)
- 5: đủ lượt theo phân công (≥ 2 người/ảnh; nhóm 5 người: 3).
- 5: COCO hợp lệ.
- 5: nhãn theo v1.0, ghi được ca mơ hồ.

## 4. IAA và calibration (25)
- 5: mẫu số đúng.
- 5: giải thích ca lệch hoặc **cùng sai**.
- 7: quyết định truy được tới ca và quy tắc (mỗi ca một dòng).
- 8: bản sửa và guideline v1.1 nhất quán.

## 5. QC và báo cáo (15)
- 4: phạm vi và số liệu (kèm mẫu số, hai cách đếm).
- 4: lỗi và ví dụ.
- 4: quyết định dựa trên bằng chứng.
- 3: giải thích vai trò kiểm bằng script và kiểm bằng mắt.

## 6. Tái lập và hợp tác (10)
- 3: gói mở và kiểm lại được.
- 4: bằng chứng cá nhân và phân công.
- 3: dùng mã thành viên, hồ sơ bàn giao, kênh nộp riêng.

Thiếu bằng chứng tính vào hạng mục liên quan. Số liệu tạo ra khi chưa làm việc tương ứng xử lý theo [RULES.md](RULES.md).
