# Guideline gán nhãn cá nhân — v0.2 — 888

- Ngày: 2026-11-16
- Người viết: thành viên 888, có AI hỗ trợ biên tập
- Trạng thái: đề xuất cá nhân; chưa thay thế guideline nhóm đã thống nhất
- Định dạng: bounding box trên ảnh, CVAT, xuất COCO 1.0
- Phạm vi ví dụ: đã đối chiếu trực tiếp `img_001`, `img_002`, `img_005`, `img_017`, `img_026`; tài liệu này không khẳng định đã rà soát đủ 40 ảnh.

## 1. Mục tiêu và thứ tự ra quyết định

Gán box cho người và phương tiện có thật, nhìn thấy trong ảnh đường phố. Mục tiêu là để hai người gán độc lập quyết định giống nhau về **có gán hay không, lớp nào, box nào và thuộc tính nào**. Không suy diễn hình dạng bị khuất, không biến vật mô phỏng thành đối tượng thật và không tự thêm lớp ngoài taxonomy.

Áp dụng các bước theo đúng thứ tự dưới đây. Dừng ở nhánh có kết luận; không dùng `ignore_region` để thay cho một đối tượng thuộc lớp hợp lệ chỉ vì lớp hoặc box còn chưa chắc.

1. **Đây có phải người/phương tiện thật trong cảnh không?** Nếu là tượng, ma-nơ-canh, hình vẽ/in, nội dung màn hình hoặc ảnh phản chiếu: không gán đối tượng. Chỉ thêm `ignore_region` nếu vùng đó dễ gây nhầm khi QC.
2. **Đối tượng có thuộc một lớp trong taxonomy không?** Nếu xác định rõ là vật ngoài phạm vi, xử lý theo nhánh `ignore_region`. Nếu có thể thuộc lớp hợp lệ nhưng ảnh không đủ căn cứ chọn lớp, bật `can_review` và ghi vấn đề.
3. **Có đạt điều kiện gán riêng không?** Đối tượng cao dưới 20 px theo ảnh gốc không tạo box riêng. Với đám đông không tách được cá thể, không tạo box gộp.
4. **Nếu gán được:** vẽ box cho phần nhìn thấy của từng đối tượng, chọn lớp và thuộc tính theo các quy tắc bên dưới.

## 2. Lớp và thuộc tính

### Lớp

| Lớp | Định nghĩa thao tác | Ví dụ | Không gán lớp này khi |
|---|---|---|---|
| `car` | Ô tô chở người có thân xe kiểu sedan, hatchback, coupe hoặc SUV; không có khoang chở hàng hở kiểu pickup. | Ô tô con đang lưu thông; SUV. | Là xe tải, pickup có thùng hở hoặc van thân kín cỡ nhỏ. |
| `truck` | Xe tải chở hàng, xe chuyên dụng/chở ô tô, hoặc pickup có khoang chở hàng hở. Phân loại theo cấu trúc xe nhìn thấy, không theo việc xe đang chở hàng hay không. | Xe chở ô tô và pickup ở `img_001`–`img_002`. | Là ô tô con/SUV hoặc van thân kín cỡ nhỏ. |
| `van` | Xe cơ giới cỡ nhỏ có thân/khoang kín kiểu van, dùng chở người hoặc hàng; chỉ chọn khi hình dáng đủ rõ để phân biệt với `car` và `truck`. | Van thân hộp cỡ nhỏ. | Là SUV, xe tải lớn hoặc pickup có thùng hở. |
| `motorcycle` | Xe máy/mô tô có động cơ và hai bánh, đang chạy hoặc đỗ. | Xe máy ở `img_005` và `img_026`. | Là xe đạp không động cơ hoặc phương tiện ba bánh. |
| `person` | Người thật đang hiện diện trong cảnh, gồm người đi bộ, người lái và hành khách. | Người đi bộ hoặc người ngồi trên xe máy. | Là tượng, ma-nơ-canh, người trong tranh/ảnh hoặc ảnh phản chiếu. |
| `ignore_region` | Vùng bỏ qua, không phải lớp đối tượng mục tiêu; dùng cho vật rõ ràng ngoài taxonomy hoặc vùng quá nhỏ/không thể tách nhất quán theo quy tắc. | Tuk-tuk/cyclo, tượng dễ bị nhầm, cụm người không thể phân ranh. | Không dùng chỉ vì chưa chắc một vật có thuộc lớp hợp lệ hay không. |

**Thứ tự phân loại xe:** pickup có thùng hở → `truck`; xe tải/chuyên chở → `truck`; van thân kín cỡ nhỏ, nhận diện rõ → `van`; ô tô chở người còn lại, gồm SUV → `car`. Nếu ảnh che mất dấu hiệu phân biệt `car`/`van`/`truck`, không đoán theo kích thước tương đối; bật `can_review`.

**Phương tiện ba bánh:** taxonomy không có lớp riêng cho tuk-tuk, cyclo hoặc xe ba bánh tương tự. Không ép chúng vào `motorcycle`, `car` hay `truck`; dùng `ignore_region` cho chính phương tiện đó. Người ngồi trên xe vẫn là `person` riêng nếu nhìn thấy và nhận diện được.

### Thuộc tính

| Thuộc tính | Giá trị | Quy tắc chọn |
|---|---|---|
| `occluded_level` | `0` | Không bị vật khác che, hoặc ước tính phần bị che không quá 10%. |
| `occluded_level` | `1` | Bị che trên 10% đến 30%. |
| `occluded_level` | `2` | Bị che trên 30% đến 60%; vẫn nhận diện được lớp và phần thấy đủ để vẽ box. |
| `occluded_level` | `3` | Bị che trên 60%, nhưng phần còn thấy vẫn đủ căn cứ xác định lớp. Nếu không đủ căn cứ, bật `can_review`, không đoán. |
| `truncated` | `no` | Đối tượng không bị cắt bởi biên ảnh. Bị đối tượng khác che không làm giá trị này thành `yes`. |
| `truncated` | `yes` | Đối tượng chạm/cắt biên ảnh và dấu hiệu nhìn thấy cho thấy nó tiếp tục ra ngoài ảnh. |
| `can_review` | bật | Có bất định đáng kể về lớp, ranh giới box hoặc cách áp dụng quy tắc; ghi ảnh, vùng và câu hỏi cần reviewer trả lời. |
| `can_review` | tắt | Quyết định đã rõ theo guideline, kể cả khi đối tượng bị che/cắt nhưng vẫn nhận diện được. |

Mức che khuất là ước lượng trực quan để tăng tính nhất quán, không phải phép đo pixel chính xác. Chỉ dùng các giá trị đã có trong taxonomy; không tự thêm thuộc tính hoặc mức mới.

## 3. Quy tắc vẽ box và các nhánh xử lý

### Cây quyết định nhanh

```text
Vật nhìn thấy trong ảnh
├─ Không phải người/phương tiện thật
│  ├─ Không dễ bị nhầm với mục tiêu → không tạo annotation
│  └─ Dễ bị nhầm khi QC → ignore_region đúng vùng đó
└─ Là người/phương tiện thật
   ├─ Rõ ràng ngoài taxonomy → ignore_region; vẫn gán người thật đi cùng nếu đủ điều kiện
   ├─ Có thể thuộc taxonomy nhưng chưa phân lớp được → can_review + ghi vấn đề
   └─ Thuộc lớp đã biết
      ├─ Cao < 20 px → không tạo box đối tượng; ignore_region nếu cần thể hiện vùng loại
      ├─ Cá thể tách được → box riêng theo phần nhìn thấy
      └─ Không thể tách nhất quán → ignore_region đúng cụm, không vẽ box gộp
```

### Quy tắc

**R-01 — Box phần thấy.** Vẽ hình chữ nhật sát biên ngoài của phần đối tượng nhìn thấy. Không mở rộng qua vật che để phỏng đoán phần khuất; không đưa đối tượng bên cạnh vào box. Box chữ nhật có thể chứa nền nằm giữa các phần của cùng đối tượng.

**R-02 — Một cá thể, một box.** Tạo box riêng cho từng người và phương tiện. Box được chồng lấn khi hai đối tượng thật chồng lấn; không gộp nhiều người hoặc nhiều xe thành một box.

**R-03 — Người và xe độc lập.** Người lái/hành khách và xe là các đối tượng riêng. Khi cả hai đủ điều kiện, tạo box `person` và box xe tương ứng; không bỏ người chỉ vì đang ngồi trên xe.

**R-04 — Xe chở xe.** Tạo box `truck` cho xe chuyên chở và box `car` riêng cho từng ô tô được chở nếu từng xe nhìn thấy đủ rõ, cao ít nhất 20 px và nhận diện được độc lập. Không gộp xe chở với xe được chở. Phần bị giàn chở/xe khác che chỉ ảnh hưởng box phần thấy và `occluded_level`.

**R-05 — Vật mô phỏng hoặc hình ảnh.** Không gán tượng, ma-nơ-canh, hình in/vẽ, nội dung màn hình hay ảnh phản chiếu thành `person`/phương tiện. Nếu hình dáng nổi bật có thể bị hiểu nhầm là mục tiêu, đặt `ignore_region` vừa đủ bao vùng mô phỏng; không tạo ignore cho cả nền.

**R-06 — Ngưỡng kích thước.** Dùng chiều cao box trên ảnh gốc: dưới 20 px thì không tạo box cho đối tượng đó; từ 20 px trở lên thì gán nếu nhận diện được lớp. Chỉ đặt `ignore_region` quanh vật nhỏ khi cần ghi nhận rõ vùng bị loại, không phủ lên mục tiêu hợp lệ bên cạnh.

**R-07 — Đám đông.** Gán từng người khi có thể nhận ra cá thể và vẽ ranh giới hợp lý. Nếu nhiều người chồng lấn tới mức không thể tách nhất quán, dùng `ignore_region` cho đúng cụm không thể tách; không tạo một box `person` bao cả đám đông. Người ở ngoài cụm vẫn được gán bình thường.

**R-08 — Ngoài taxonomy khác với chưa chắc lớp.** Vật xác định rõ là ngoài taxonomy (ví dụ xe ba bánh) đi theo `ignore_region`. Vật có thể là `car`, `van` hoặc `truck` nhưng bị che/mờ đến mức không phân biệt được đi theo `can_review`. Không dùng ignore để che bất đồng về lớp của một mục tiêu hợp lệ.

**R-09 — Vật bị cắt mép ảnh.** Nếu còn nhận diện được đối tượng, vẽ phần nằm trong ảnh, dừng box tại mép ảnh và đặt `truncated=yes`. Không suy đoán box kéo dài ra ngoài khung. Vật bị che bởi vật khác nhưng không chạm biên ảnh không phải truncated.

**R-10 — Không có đối tượng.** Giữ ảnh trong Task và COCO với danh sách annotation rỗng; không xóa ảnh. Nếu không thể vẽ box nhưng có vấn đề cần nhóm xử lý, ghi ảnh/vùng/lý do vào `submission/qc/image_issues.csv`.

**R-11 — Dùng `can_review` có chủ đích.** Gắn cờ cho đúng box còn bất định và ghi câu hỏi cụ thể. Nếu không có box nào để gắn cờ, ghi vấn đề cấp ảnh theo R-10. Không bật cờ cho mọi đối tượng bị che; chỉ bật khi quy tắc không cho ra một quyết định duy nhất.

## 4. Ca khó tham chiếu

| Ảnh | Tình huống quan sát được | Rule ID | Quyết định theo guideline 888 | Lý do / điểm cần kiểm |
|---|---|---|---|---|
| `img_001.jpg` | Pickup có khoang chở hàng hở; người đứng gần và người ở hậu cảnh. | R-02, R-03 | Pickup là `truck`; mỗi người đủ nhìn thấy được gán `person` riêng. | Phân loại theo cấu trúc thùng hở, không theo kích thước xe hay việc đang chở hàng. |
| `img_002.jpg` | Xe chuyên chở nhiều ô tô; giàn xe che một phần các xe được vận chuyển. | R-01, R-04 | Một `truck` cho xe chở và box `car` riêng cho từng ô tô nhận diện được, đủ 20 px. | Không gộp thành một cụm; đánh giá che khuất riêng cho từng ô tô. |
| `img_005.jpg` | Người và nhiều xe máy chồng lấn trong cảnh đông. | R-02, R-03, R-07, R-11 | Tách từng người/xe máy khi nhận ra được cá thể; vùng không thể phân ranh mới dùng `ignore_region`. | Box của người và xe có thể chồng lấn; bất định thật sự mới cần review. |
| `img_017.jpg` | Tượng người cưỡi ngựa có hình dáng gần với người/động vật thật. | R-05, R-08 | Không gán tượng thành `person`; dùng `ignore_region` nếu cần để reviewer nhận ra vùng dễ gây nhầm. | Đây là vật mô phỏng, không phải người đang hiện diện. Ngựa cũng không thuộc taxonomy. |
| `img_026.jpg` | Người và xe máy thật ở trước bức tranh/phông nền có hình ảnh. | R-03, R-05 | Gán người và xe máy thật; không gán người/xe chỉ xuất hiện trong hình vẽ. | Phân biệt vật thể trong cảnh với nội dung hai chiều ở nền. |

Các ví dụ trên là ca tham chiếu cho cách áp dụng quy tắc, không thay thế ghi chú về bất đồng hoặc kết quả calibration của nhóm.

## 5. QC và lịch sử phiên bản

- Giữ nguyên ngưỡng trong `submission/taxonomy.json`: chiều cao box tối thiểu 20 px; box cao dưới 50 px dùng IoU threshold `0.70`, box cao từ 50 px dùng `0.85`; ngưỡng ghép box `0.50`; mục tiêu IAA IoU trung bình `0.85`, đồng thuận lớp `0.95`; tỷ lệ ảnh lỗi tối đa `0.02`.
- IAA tính trên các cặp box ghép 1–1; báo số liệu dạng tử số/mẫu số. Không có cặp thì ghi N/A, không ghi thành 0. Báo riêng box chưa ghép và bất đồng liên quan `ignore_region`.
- Tách lỗi theo ảnh khỏi lỗi theo đối tượng. Một ảnh có thể có nhiều lỗi; ghi từng lỗi theo phiếu QC. Lô 40 ảnh có 1 ảnh lỗi tương ứng 2.5%, vượt ngưỡng ảnh lỗi tối đa 2%.
- Chỉ số tự động không chứng minh box ôm sát vật thật, không đảm bảo cả nhóm không cùng bỏ sót hoặc cùng áp dụng sai quy tắc. Reviewer cần đối chiếu nhãn với ảnh gốc và guideline đúng phiên bản.
- Thiếu bằng chứng, chỉ duyệt mẫu, hoặc nhãn/guideline lệch phiên bản thì Chưa đủ điều kiện. Vượt ngưỡng lỗi hoặc có lỗi lặp theo cùng một quy tắc thì Rework; chỉ Release khi đã duyệt đủ lô và bằng chứng đạt yêu cầu của lab.
- Mỗi ca cần ghi ảnh, vùng, rule ID, quyết định, người chốt và kết quả kiểm lại. Nếu thay đổi làm đổi đối tượng/lớp/box/thuộc tính, tăng phiên bản guideline và xác định phạm vi kiểm lại theo quy trình nhóm.

| Phiên bản | Thay đổi | Căn cứ |
|---|---|---|
| v0.1 | Bản nháp tham khảo về lớp, thuộc tính, box và ví dụ ca biên. | Các quy tắc ban đầu cần được làm rõ thành quyết định thao tác. |
| v0.2 | Bổ sung thứ tự quyết định, nhánh phân biệt ngoài taxonomy với bất định, quy tắc lớp xe và tiêu chí QC; biên tập với hỗ trợ AI. | Đối chiếu taxonomy, quy trình lab và các ví dụ `img_001`, `img_002`, `img_005`, `img_017`, `img_026`. |
