# Nộp bài Day 07

## Cách nộp

- Một nhóm nộp **một link repo riêng tư có quyền cho coach**, hoặc **một gói nén qua LMS**, theo kênh coach công bố.
- Tên repo / gói: `K5-L23-DAY07-<TenNhom>-GuidelineQC`.
- Dùng **mã thành viên** (ví dụ `101`). **Tránh** họ tên, MSHV, email, tài khoản trong tên file, Task hay tiêu đề README. Coach giữ bảng đối chiếu mã ở kênh lớp có giới hạn quyền.
- Thời hạn do coach công bố.

## Gói bàn giao

| Nhóm | Gồm có |
|---|---|
| Nhóm và nguồn | `TEAM.md`, `data/ATTRIBUTION.csv` |
| Đặc tả | `submission/guidelines/individual/guideline_<mã>.md`; `guideline_v1.0_agreed.md`, `guideline_v1.1_calibrated.md`; `submission/guideline_change.json`; `submission/taxonomy.json` (và `taxonomy_v1.1.json` nếu đổi schema) |
| Gán độc lập | `submission/labels/<mã>.json`; `submission/qc/assignment.csv`; `image_issues.csv` nếu có ca chưa có box |
| Calibration | `iaa_summary.json/.md`, `calibration_candidates.csv`, `flagged_images.txt`, `consensus_draft.json`, `calibration_decisions.csv`, `calibration_context.json`; COCO phạm vi đã sửa nếu có |
| Nhãn cuối | `labels_calibrated.json`, `labels_calibrated.csv`, `batch_manifest.json` |
| QC và học cá nhân | `submission/qc/reviews/round-*/` (giữ cả vòng cũ), `QC_REPORT.md`, `submission/individual_notes/<mã>.md` |

Giữ đường dẫn tương đối để reviewer chạy lại lệnh. Thư mục `work/` chỉ dùng cục bộ, **không nộp**.
Nếu nộp gói nén: kèm starter repo và dữ liệu, hoặc ghi đúng commit và cách lấy lại dữ liệu.

## Checklist

- [ ] Mọi thành viên có guideline cá nhân, COCO và ghi chú cá nhân (tên file dùng mã).
- [ ] Mỗi ảnh được ≥ 2 người gán (nhóm 5 người: 3); `validate_labels.py --all` sạch.
- [ ] `taxonomy.json` khớp guideline; mục `rules` không đổi.
- [ ] Mỗi ca IAA có một dòng trong `calibration_decisions.csv`; có `guideline_v1.1_calibrated.md` và `guideline_change.json`.
- [ ] `QC_REPORT.md` điền đủ, tỉ lệ kèm mẫu số, có quyết định.
- [ ] `python scripts/check_submission.py --round <vòng-cuối>` không còn lỗi.
- [ ] Không có `work/`, thông tin cá nhân hay thông tin đăng nhập; giữ ghi công ảnh.
