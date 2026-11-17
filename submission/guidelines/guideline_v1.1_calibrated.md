# Guideline gán nhãn nhóm — v1.1

- Ngày: 2026-11-17
- Trạng thái: **Calibration — chờ xác nhận**
- Định dạng: bounding box trên ảnh, CVAT, xuất COCO 1.0
- Kế thừa quy tắc v1.0, trừ thay đổi ngữ nghĩa R-02 dưới đây.
- Taxonomy tương ứng: `submission/taxonomy_v1.1.json`.

> Tài liệu ghi lại phương án calibration đang chờ xác nhận; các dòng người chốt chưa phải biên bản họp hoặc xác nhận đã hoàn tất. Chỉ khóa v1.1 sau khi người review nhóm xác nhận quyết định và nhãn đã được sửa/kiểm lại.

## 1. Mục tiêu

Gán từng người và phương tiện có thật, nhìn thấy trong ảnh đường phố để huấn luyện mô hình phát hiện đối tượng. Chỉ gán thông tin có căn cứ trực quan; không đoán phần khuất, không ép vật ngoài taxonomy vào lớp gần giống và không dùng `can_review` như nhãn mục tiêu của mô hình.

## 2. Lớp và thuộc tính

| Lớp | Định nghĩa | Ví dụ | Không thuộc lớp |
|---|---|---|---|
| `car` | Ô tô chở người kiểu sedan, hatchback, coupe hoặc SUV. | Sedan/SUV đang lưu thông. | Xe tải, pickup, van thân kín cỡ nhỏ. |
| `truck` | Xe tải chở hàng, xe chuyên chở (kể cả xe chở ô tô), hoặc pickup có khoang chở hàng; pickup gắn camper/canopy che thùng vẫn là `truck` khi nhận diện rõ cấu trúc pickup. | Xe chở ô tô trong `img_002`; pickup/camper trong `img_037` nếu xác nhận được cấu trúc pickup. | Ô tô chở người, van thân kín cỡ nhỏ không phải pickup. |
| `van` | Xe cơ giới cỡ nhỏ có thân/khoang kín kiểu van, dùng chở người hoặc hàng; chỉ chọn khi dấu hiệu thân xe đủ rõ. | Van thân hộp cỡ nhỏ. | SUV, pickup, xe tải lớn. |
| `motorcycle` | Xe máy/mô tô có động cơ và hai bánh. | Xe máy trong `img_005`, `img_026`. | Xe đạp, tuk-tuk/cyclo, phương tiện ba bánh. |
| `person` | Người thật trong cảnh, gồm người đi bộ, người lái và hành khách. | Người đi bộ hoặc người ngồi trên xe. | Tượng, ma-nơ-canh, hình in/vẽ, nội dung màn hình, ảnh phản chiếu. |
| `ignore_region` | Vùng ngoài taxonomy hoặc không thể gán riêng nhất quán; không phải lớp vật thể. | Tuk-tuk; cụm người không thể tách. | Không dùng cho đối tượng hợp lệ chỉ vì chưa chắc lớp/box. |

Giữ nguyên thuộc tính của v1.0: `occluded_level` 0–3 theo các ngưỡng đã thống nhất; `truncated=yes` khi vật tiếp tục qua biên ảnh; `can_review` chỉ là cờ quy trình. Khi đã chốt nhãn calibration, tắt `can_review`.

## 3. Quy tắc gán nhãn

**R-01 — Đối tượng mục tiêu.** Chỉ gán người thật và phương tiện thuộc lớp trong taxonomy; không gán tượng, ma-nơ-canh, hình vẽ/in, nội dung màn hình hoặc ảnh phản chiếu như đối tượng thật.

**R-02 — Chọn lớp theo cấu trúc nhìn thấy (thay đổi ngữ nghĩa v1.1).** Xe tải chở hàng và xe chuyên chở là `truck`. Pickup được xếp `truck` khi nhận diện được cấu trúc pickup, kể cả khi có camper/canopy gắn trên thùng che kín khoang hàng. Không xếp thành `van` chỉ vì khoang sau bị che kín. Van thân kín cỡ nhỏ là `van` khi nhận diện rõ; ô tô chở người kiểu sedan/hatchback/coupe/SUV là `car`. Nếu dấu hiệu không đủ để chọn lớp, không đoán; ghi vấn đề để reviewer xử lý.

**R-03 — Một đối tượng, một box.** Mỗi người/phương tiện có một box riêng; không gộp cá thể. Box được chồng lấn khi đối tượng chồng lấn trong ảnh.

**R-04 — Box phần thấy.** Vẽ sát biên ngoài phần nhìn thấy; không nội suy phần khuất hoặc lấy vật khác vào box.

**R-05 — Che khuất.** Gán `occluded_level` theo phần trăm ước lượng. Chỉ dùng mức 3 khi phần còn thấy đủ nhận diện lớp.

**R-06 — Cắt mép.** Nếu vật tiếp tục qua biên ảnh, box dừng ở biên và đặt `truncated=yes`.

**R-07 — Người đi xe.** Gán riêng người lái/hành khách `person` và xe phù hợp nếu đủ căn cứ.

**R-08 — Xe chở xe.** Gán xe chuyên chở là `truck`; gán riêng từng ô tô được chở nếu nhận diện độc lập và cao ít nhất 20 px.

**R-09 — Đối tượng nhỏ.** Không tạo box đối tượng cao dưới 20 px; từ 20 px trở lên gán nếu đủ căn cứ. Chỉ dùng `ignore_region` khi cần ghi rõ vùng bị loại.

**R-10 — Đám đông.** Gán từng người có thể tách; không tạo box người gộp. Cụm không thể tách nhất quán có thể được khoanh đúng vùng bằng `ignore_region`.

**R-11 — Ngoài taxonomy/chưa chắc lớp.** Vật rõ ràng ngoài taxonomy có thể dùng `ignore_region`. Nếu chưa thể chọn lớp hợp lệ có căn cứ, không tạo box đoán lớp; ghi `image,annotator,region,note`.

**R-12 — Vùng ignore có giới hạn.** Khoanh đúng vùng cần loại; không phủ ảnh hoặc đối tượng hợp lệ.

**R-13 — Ảnh không có đối tượng.** Giữ ảnh trong COCO với không annotation.

## 4. Quyết định calibration

Các ca `C001`–`C014` được ghi trong `submission/qc/calibration_decisions.csv`. Hiện tất cả chỉ là cần xác nhận trước khi khóa phiên bản. Vì R-02 đổi nghĩa lớp, phạm vi calibration là **toàn bộ lô 40 ảnh**, không chỉ 10 ảnh bị cờ. Rà tất cả pickup/camper, lớp, độ đầy đủ, box, thuộc tính và tắt toàn bộ `can_review`.

Các điểm cần soi kỹ:

- `img_005`, `img_008`, `img_010`, `img_021`, `img_030`, `img_034`, `img_035`, `img_039`: kiểm độ đầy đủ cá thể nhìn thấy; đồng thuận box giữa hai người không chứng minh không có bỏ sót chung.
- `img_023`: chỉnh box xe máy theo ảnh gốc; giá trị IoU hiển thị đã làm tròn sát ngưỡng nên cần kiểm trực quan.
- `img_037`: phương án xếp pickup có camper vào `truck` nếu cấu trúc pickup nhìn thấy rõ; kiểm riêng người và thuộc tính.

## 5. QC và lịch sử

- Giữ nguyên ngưỡng taxonomy: IoU ghép 0.50; IAA IoU 0.85; cùng lớp 0.95; IoU box nhỏ 0.70 và box lớn 0.85.
- IAA hiện tại là 151 cặp ghép trên 40 ảnh; báo riêng box chưa ghép và vùng `ignore_region`. Đây không thay thế review bỏ sót chung.
- Do thay đổi ngữ nghĩa R-02, rà toàn bộ 40 ảnh. Không dùng nhãn đồng thuận hiện tại làm bản cuối nếu chưa áp dụng quyết định mới.
- Lịch sử: v1.0 hợp nhất guideline độc lập; v1.1 làm rõ pickup có camper/canopy và yêu cầu rà lại toàn lô. Taxonomy v1.1 giữ nguyên lớp/thuộc tính/ngưỡng, chỉ cập nhật định nghĩa `truck`.
