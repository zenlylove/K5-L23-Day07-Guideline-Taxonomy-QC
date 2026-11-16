# Guideline gán nhãn nhóm — v1.0

- Ngày: 2026-11-16
- Trạng thái: **KHÓA cho lượt gán độc lập Pha 3**
- Định dạng: bounding box trên ảnh, CVAT, xuất COCO 1.0
- Tài liệu cá nhân được đối chiếu: `individual/guideline_666.md` và `individual/guideline_888.md`
- Cơ sở rà ca ảnh gốc: `img_001`, `img_002`, `img_005`, `img_017`, `img_026`

> Đây là đặc tả vận hành hợp nhất để mọi lượt gán Pha 3 dùng cùng một cách hiểu. Quyết định dưới đây không ghi nhận danh sách người dự họp. `TEAM.md` hiện liệt kê `666,999`, trong khi thư mục guideline có `666,888`; cần xác nhận mã thành viên trước khi lập phân công, nhưng không tự đổi các mã này trong guideline.

## 1. Mục tiêu

Gán từng người và phương tiện có thật, nhìn thấy trong ảnh đường phố để huấn luyện mô hình phát hiện đối tượng. Chỉ gán thông tin có căn cứ trực quan trong ảnh; không đoán phần khuất, không ép vật ngoài taxonomy vào một lớp gần giống và không dùng cờ quy trình `can_review` như một nhãn mục tiêu của mô hình.

## 2. Bảng đối chiếu bất đồng và quyết định

| Chủ đề | Bản 666 | Bản 888 | Quyết định v1.0 |
|---|---|---|---|
| Định nghĩa `car`, `truck`, `van` | Đã nêu các kiểu thân xe; pickup thùng hở và xe chở ô tô thuộc `truck`. | Nêu thêm thứ tự phân lớp và không phân loại theo hàng đang chở. | Dùng cấu trúc nhìn thấy: pickup thùng hở/xe tải/xe chuyên chở → `truck`; van thân kín cỡ nhỏ rõ ràng → `van`; ô tô chở người kiểu sedan/hatchback/coupe/SUV → `car`. Không suy từ hàng hóa hoặc kích thước tương đối. |
| `motorcycle` và xe ba bánh | Định nghĩa hai bánh; đề xuất không ép tuk-tuk/cyclo vào lớp hiện có. | Xác định rõ xe máy có động cơ hai bánh; ba bánh ngoài taxonomy. | `motorcycle` chỉ xe cơ giới hai bánh. Tuk-tuk/cyclo/xe ba bánh không được gán lớp phương tiện. |
| Ngưỡng `occluded_level` | 0–10%, >10–30%, >30–60%, >60% nếu vẫn nhận diện được. | Cùng các ngưỡng. | Giữ đúng bốn mức và các ngưỡng chung; ước lượng trực quan, không đo pixel chính xác. |
| `truncated` | Đặt `yes` khi vật tiếp tục qua biên ảnh; che bởi vật khác không phải truncation. | Cùng nguyên tắc. | Giữ cùng nguyên tắc; box dừng ở biên ảnh. |
| `ignore_region` | Mô tả rộng gồm vật ngoài phạm vi hoặc vật quá nhỏ; có thể dùng cho tượng/cụm đông. | Chỉ khoanh vùng cần bỏ qua; không dùng để che đối tượng hợp lệ chưa rõ lớp. | Chỉ khoanh vùng cụ thể ngoài taxonomy hoặc vùng không thể gán riêng theo quy tắc; không thay cho box hợp lệ và không dùng để xử lý bất định lớp. |
| Bất định lớp | Có chỗ viết “`can_review` hoặc `ignore_region` theo quyết định reviewer”. | Tách rõ: đối tượng có thể hợp lệ nhưng chưa rõ lớp thì `can_review`. | Không đoán lớp. Chỉ gắn `can_review` khi tạo được box với một lớp tạm có căn cứ trực quan; nếu chưa thể chọn lớp nào thì không tạo box gán nhãn, ghi vấn đề cấp ảnh để reviewer xử lý. Không gán `ignore_region`. |
| Box phần thấy | Box sát phần nhìn thấy, không đoán phần khuất. | Cùng nguyên tắc, thêm box chữ nhật có thể chứa nền nằm giữa các phần của cùng vật. | Box chữ nhật ôm sát biên ngoài của phần thấy; không nội suy phần khuất, không lấy vật khác vào box. |
| Người đi xe máy | Người và xe là hai box, có thể chồng lấn. | Cùng nguyên tắc cho người lái/hành khách và xe. | Gán riêng từng người `person` và xe `motorcycle` nếu đủ điều kiện; không bỏ người vì đang ngồi trên xe. |
| Xe chở xe | Gán `truck` và từng `car` nhận diện độc lập, không gộp. | Cùng nguyên tắc, nêu rõ ngưỡng 20 px. | Gán xe chuyên chở `truck`; gán riêng từng ô tô được chở khi nhận diện được và cao ít nhất 20 px. |
| Vật nhỏ/đám đông | Dưới 20 px không gán riêng; vùng người không tách được có thể ignore. | Cùng ngưỡng, nhấn mạnh không tạo box gộp và khoanh đúng vùng. | Dưới 20 px không tạo box đối tượng; người tách được vẫn gán riêng; cụm không thể tách không có box `person` gộp. Chỉ thêm `ignore_region` khi cần ghi nhận đúng vùng bị loại. |

Hai bản thống nhất về người/phương tiện thật, box phần thấy, ngưỡng thuộc tính, cắt mép, người đi xe, xe chở xe và giữ ảnh rỗng. Các điểm cần chốt là phạm vi `ignore_region`, nhánh chưa chắc lớp, chi tiết phân lớp xe và ngưỡng cho xe được chở; các quyết định đã chốt ở bảng trên.

## 3. Lớp và thuộc tính

### Lớp

| Lớp | Định nghĩa | Ví dụ | Không thuộc lớp |
|---|---|---|---|
| `car` | Ô tô chở người có kiểu thân sedan, hatchback, coupe hoặc SUV. | Sedan/SUV đang lưu thông. | Xe tải, pickup thùng hở, van thân kín cỡ nhỏ. |
| `truck` | Xe tải chở hàng, xe chuyên chở (kể cả xe chở ô tô), hoặc pickup có khoang hàng hở. | Xe chở ô tô trong `img_002`; pickup trong `img_001`. | Ô tô chở người, van thân kín cỡ nhỏ. |
| `van` | Xe cơ giới cỡ nhỏ có thân/khoang kín kiểu van, dùng chở người hoặc hàng; chỉ chọn khi dấu hiệu thân xe đủ rõ. | Van thân hộp cỡ nhỏ. | SUV, pickup thùng hở, xe tải lớn. |
| `motorcycle` | Xe máy/mô tô có động cơ và hai bánh. | Xe máy trong `img_005`, `img_026`. | Xe đạp, tuk-tuk/cyclo, phương tiện ba bánh. |
| `person` | Người thật đang hiện diện trong cảnh, gồm người đi bộ, người lái và hành khách. | Người đi bộ hoặc người ngồi trên xe. | Tượng, ma-nơ-canh, hình in/vẽ, nội dung màn hình, ảnh phản chiếu. |
| `ignore_region` | Vùng đánh dấu không đưa vào đối tượng mục tiêu; không phải một loại vật thể cần dự đoán. Chỉ dùng cho vùng ngoài taxonomy hoặc không thể gán riêng nhất quán theo quy tắc. | Tuk-tuk; tượng dễ bị nhầm; cụm người không thể tách. | Không dùng cho đối tượng hợp lệ chỉ vì chưa chắc lớp hoặc box. |

### Thuộc tính

Giữ nguyên ba thuộc tính đã định nghĩa trong `submission/taxonomy.json`:

| Thuộc tính | Giá trị | Tiêu chí quan sát |
|---|---|---|
| `occluded_level` | `0` | Không bị che hoặc phần bị che ước tính không quá 10%. |
| `occluded_level` | `1` | Bị che trên 10% đến 30%. |
| `occluded_level` | `2` | Bị che trên 30% đến 60%, vẫn nhận diện được đối tượng. |
| `occluded_level` | `3` | Bị che trên 60%, nhưng phần còn thấy vẫn đủ căn cứ nhận diện lớp. Nếu không đủ, `can_review`; không đoán. |
| `truncated` | `no` | Không bị cắt bởi biên ảnh. |
| `truncated` | `yes` | Đối tượng tiếp tục ra ngoài biên ảnh. |
| `can_review` | `false` | Không còn bất định cần reviewer giải quyết. |
| `can_review` | `true` | Người gán cần reviewer giải quyết bất định về lớp, box hoặc quy tắc; kèm ghi chú/vấn đề cấp ảnh. |

`occluded_level` và `truncated` mô tả dấu hiệu có thể đánh giá từ ảnh. `can_review` là cờ quy trình do người gán đặt, không phải thuộc tính ngoại quan để dùng làm nhãn học của mô hình; vẫn giữ trong CVAT để kiểm soát QC. Ba thuộc tính được cấu hình trên các lớp đối tượng, không cấu hình trên `ignore_region`.

## 4. Quy tắc gán nhãn

**R-01 — Đối tượng mục tiêu.** Chỉ gán người thật và phương tiện thuộc lớp trong taxonomy. Không gán tượng, ma-nơ-canh, hình vẽ/in, nội dung màn hình hoặc ảnh phản chiếu như đối tượng thật.

**R-02 — Chọn lớp theo dấu hiệu nhìn thấy.** Dùng định nghĩa lớp ở mục 3. Pickup có thùng hở là `truck`; van thân kín cỡ nhỏ chỉ là `van` khi nhận diện rõ; SUV là `car`. Không suy đoán lớp. Chỉ tạo box có lớp tạm và bật `can_review` nếu lớp tạm có căn cứ trực quan; nếu không thể chọn lớp nào có căn cứ, không tạo box gán nhãn và ghi vấn đề cấp ảnh để reviewer xử lý.

**R-03 — Một đối tượng, một box.** Mỗi người/phương tiện được gán một box riêng. Không gộp người, xe hoặc nhiều cá thể; box của các đối tượng có thể chồng lấn khi chúng chồng lấn trong ảnh.

**R-04 — Box phần nhìn thấy.** Vẽ hình chữ nhật sát biên ngoài phần nhìn thấy của đối tượng. Không đoán hoặc mở rộng box qua vật che; không lấy phần của đối tượng khác vào box.

**R-05 — Che khuất.** Gán `occluded_level` cho từng đối tượng theo phần trăm ước lượng ở mục 3. Dùng box phần thấy theo R-04. Chỉ gán mức 3 khi phần còn thấy vẫn đủ để nhận diện lớp; nếu không thì `can_review`.

**R-06 — Cắt mép ảnh.** Nếu đối tượng tiếp tục qua biên ảnh, vẽ phần nằm trong ảnh, dừng box tại mép và đặt `truncated=yes`. Che bởi đối tượng khác không phải truncation.

**R-07 — Người đi xe.** Khi nhìn thấy và nhận diện được, gán người là `person`, xe là lớp xe riêng; áp dụng cả người lái lẫn hành khách. Hai box có thể chồng lấn.

**R-08 — Xe chở xe.** Gán xe chuyên chở là `truck`. Gán từng ô tô được chở là `car` riêng nếu hình xe nhận diện độc lập và box cao ít nhất 20 px. Không gộp các xe với nhau; đánh giá che khuất trên từng xe.

**R-09 — Đối tượng nhỏ.** Box đối tượng cao dưới 20 px trên ảnh gốc không được tạo. Từ 20 px trở lên, gán nếu đủ căn cứ nhận diện lớp. Chỉ tạo `ignore_region` cho vùng nhỏ khi cần thể hiện rõ vùng bị loại; không phủ vật hợp lệ lân cận.

**R-10 — Đám đông.** Gán từng người nếu cá thể và ranh giới có thể xác định. Nếu cụm dày đến mức không thể tách nhất quán, không tạo box `person` gộp; dùng `ignore_region` đúng vùng cụm khi cần.

**R-11 — Ngoài taxonomy và chưa chắc lớp.** Vật rõ ràng ngoài taxonomy (ví dụ tuk-tuk/cyclo) có thể được khoanh bằng `ignore_region`; người thật trên xe vẫn gán riêng nếu đủ điều kiện. `can_review` chỉ gắn trên box có lớp tạm đủ căn cứ trực quan nhưng còn điểm cần reviewer kiểm tra. Nếu không thể chọn lớp nào có căn cứ, không tạo box với lớp đoán; ghi `image,annotator,region,note` vào `submission/qc/image_issues.csv` để reviewer chốt trước khi chấp nhận nhãn. Không dùng `ignore_region` để né quyết định đó.

**R-12 — Vùng ignore có giới hạn.** Khoanh đúng vùng cần loại; không phủ cả ảnh, không che đối tượng hợp lệ. Không tạo ignore chỉ vì vật là tượng/hình ảnh nếu vùng đó không có nguy cơ gây nhầm trong QC.

**R-13 — Ảnh không có đối tượng.** Giữ ảnh trong Task/COCO với không annotation; không xóa hoặc bỏ ảnh khỏi phân công.

## 5. Ca tham chiếu đã đối chiếu trên ảnh gốc

| Ảnh | Quyết định v1.0 | Rule | Lý do |
|---|---|---|---|
| `img_001.jpg` | Pickup thùng hở là `truck`; người thật là `person` riêng. | R-02, R-07 | Hình dạng khoang hàng nhìn thấy; người và xe là hai đối tượng. |
| `img_002.jpg` | Xe chuyên chở là `truck`; mỗi ô tô nhìn thấy đủ rõ và cao ≥20 px là `car` riêng. | R-04, R-08 | Không gộp xe chở với các xe được chở; mức che xét theo từng xe. |
| `img_005.jpg` | Gán riêng người và từng xe máy nhận diện được; không gộp thành box đám đông. | R-03, R-05, R-07, R-10 | Chồng lấn không làm người và xe thành một đối tượng; cụm không tách được mới dùng ignore. |
| `img_017.jpg` | Không gán tượng thành `person`; `ignore_region` chỉ khi vùng dễ bị nhầm và cần đánh dấu. | R-01, R-12 | Tượng/ngựa không phải người/phương tiện thuộc taxonomy. |
| `img_026.jpg` | Gán người/xe thật; không gán vật thể chỉ xuất hiện trong hình nền. | R-01, R-07 | Phân biệt đối tượng trong cảnh với hình ảnh hai chiều. |

## 6. QC, khóa phiên bản và lịch sử

- Dùng đúng các ngưỡng trong `submission/taxonomy.json`: box cao dưới 50 px dùng IoU `0.70`, từ 50 px dùng `0.85`; ngưỡng ghép box `0.50`; IAA mục tiêu IoU `0.85`, đồng thuận lớp `0.95`; tỷ lệ ảnh lỗi tối đa `0.02`.
- Ghi số liệu kèm tử số/mẫu số; IAA chỉ tính trên cặp box ghép 1–1. Không có cặp thì báo N/A. Báo riêng box chưa ghép và bất đồng liên quan `ignore_region`.
- Script kiểm cấu trúc, lớp, thuộc tính, kích thước/vị trí và độ lệch; reviewer vẫn phải đối chiếu ảnh gốc để tìm box không sát, vật bỏ sót hoặc lỗi cùng hiểu sai.
- Lượt gán độc lập Pha 3 phải dùng đúng taxonomy v1.0 và guideline này. Không đổi nghĩa quy tắc giữa lượt gán; mọi thay đổi sau khi khóa phải theo quy trình calibration và tăng phiên bản.
- Hold nếu thiếu bằng chứng hoặc mới duyệt mẫu; Rework nếu vượt ngưỡng ảnh lỗi hoặc lỗi hệ thống lặp lại; chỉ Release theo điều kiện nghiệm thu của lab.

| Phiên bản | Thay đổi | Căn cứ |
|---|---|---|
| v0 | Guideline khởi đầu yêu cầu gán người/phương tiện và vẽ box ôm sát, nhưng chưa định nghĩa đủ lớp, ngưỡng thuộc tính, phần bị che/cắt, ngoài taxonomy, người đi xe, xe chở xe và ca khó. | `guideline/guideline_v0_starter.md`. |
| v1.0 | Hợp nhất hai bản cá nhân; chốt định nghĩa lớp, mức thuộc tính, box phần thấy, che khuất, truncation, vật ngoài taxonomy, người đi xe máy, xe chở xe, vật nhỏ, đám đông và cờ review; gắn mã R-01–R-13. | Đối chiếu `guideline_666.md`, `guideline_888.md`, taxonomy hiện tại và các ảnh gốc nêu ở mục 5. |
