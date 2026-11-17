# Tóm tắt QC

## Ngưỡng và cách đếm

| Đại lượng | Công thức / quy tắc | Ngưỡng của lab |
|---|---|---|
| IoU | giao / hợp của hai box | box cao ≥ 50 px: 0.85; nhỏ hơn: 0.7 |
| IAA | IoU trung bình và % cùng lớp, **chỉ trên cặp box ghép 1–1** (không phân biệt lớp, IoU ghép ≥ 0.5) | IoU TB ≥ 0.85, cùng lớp ≥ 95% |
| Độ phủ | lượt gán hợp lệ / tổng lượt trong `assignment.csv` | đủ 100% mới đo IAA |
| Vật nhỏ | cao < 20 px | `ignore_region`, đối chiếu quy tắc vật nhỏ |
| Lỗi theo **ảnh** | ảnh có ≥ 1 lỗi / ảnh đã duyệt | **≤ 2%** mới Release |
| Lỗi theo **đối tượng** | annotation đối tượng bị lỗi / annotation đã duyệt | báo kèm mẫu số |

- Số đo luôn ghi dạng `tử số/mẫu số`. Không có cặp box thì ghi N/A.
- Với ba người, một ảnh đóng góp ba cặp người.
- Box chưa ghép được đếm riêng. Chỉ một người đặt vùng `ignore_region` phủ box thì đưa ca vào calibration.
- Release của lab yêu cầu **duyệt toàn bộ lô**. Lô 40 ảnh: một ảnh lỗi (2,5%) đã vượt ngưỡng.
- Vòng demo chỉ lấy mẫu: luôn là **Chưa đủ điều kiện** khi bàn giao.
- Giữ IAA **trước** calibration trong hồ sơ.

## Năm loại lỗi (trong `qc_review.csv`)

| `error_type` | Loại | Ví dụ |
|---|---|---|
| `bo_sot` | Bỏ sót | vật thật không có box (để trống `object_id`, ghi `region`) |
| `thua` | Thừa | box trên tượng / phản chiếu / hình in |
| `sai_lop` | Sai lớp | xe con gán `truck` |
| `sai_vi_tri_kich_thuoc` | Sai vị trí, kích thước | box lỏng, thiếu đuôi xe |
| `sai_thuoc_tinh` | Sai thuộc tính | `occluded_level` sai mức |
| `khong` | Không lỗi | ảnh đã duyệt, sạch |

Một ảnh có thể có nhiều lỗi (mỗi lỗi một dòng). Quy định từng dòng: [scripts/README.md](../scripts/README.md#phiếu-qc).

## Cây quyết định: Chưa đủ điều kiện → Rework → Release

1. **Chưa đủ điều kiện** nếu thiếu bằng chứng, guideline / dữ liệu còn vấn đề, review lệch phiên bản, hoặc mới chỉ lấy mẫu.
2. **Rework** nếu > 2% ảnh lỗi hoặc có **lỗi lặp** theo quy tắc của lab. Ghi nguyên nhân, người sửa, kết quả kiểm lại.
3. **Release** khi reviewer xác nhận bằng chứng đạt yêu cầu bàn giao lô thực hành.

Lỗi ít nhưng lặp cùng một kiểu vẫn là Rework: đó là lỗi hệ thống.

## IAA thấp thì sửa gì?

| Dấu hiệu | Nguyên nhân | Xử lý |
|---|---|---|
| Cả hai lệch cùng loại ca | quy tắc mơ hồ | sửa guideline |
| Chỉ một người lệch | chưa nắm quy tắc | hướng dẫn lại |
| Giống nhau nhưng cùng sai | cùng hiểu sai | đối chiếu ca tham chiếu |

Muốn hiểu thêm về lấy mẫu nghiệm thu: [NIST](https://itl.nist.gov/div898/handbook/pmc/section2/pmc21.htm) · [ISO 2859-1:2026](https://www.iso.org/standard/85464.html).
