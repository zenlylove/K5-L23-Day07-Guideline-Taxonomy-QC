# Guideline gán nhãn cá nhân — v0.1 — 666

- Ngày: 2026-11-16
- Người viết: thành viên 666
- Trạng thái: bản cá nhân đề xuất; chưa phải guideline nhóm đã thống nhất
- Định dạng: bounding box trên ảnh, xuất COCO 1.0 từ CVAT

## 1. Mục tiêu

Gán nhãn người và phương tiện nhìn thấy trong ảnh đường phố để xây dựng dữ liệu huấn luyện mô hình phát hiện đối tượng. Ưu tiên tính nhất quán giữa ảnh và giữa người gán: chỉ gán những gì ảnh cho phép nhận diện, không suy đoán phần bị che hoặc đối tượng chỉ xuất hiện trong tranh, ảnh phản chiếu hay tượng.

## 2. Lớp và thuộc tính

### Lớp

| Lớp | Định nghĩa dùng trong bản cá nhân | Ví dụ | Phản ví dụ / dễ nhầm |
|---|---|---|---|
| `car` | Ô tô chở người có thân xe kiểu sedan, hatchback, coupe hoặc SUV. | Ô tô con đang lưu thông; SUV. | Xe tải có thùng hàng; xe van thân kín rõ ràng. |
| `truck` | Xe tải chở hàng, xe đầu kéo/xe chuyên chở xe và pickup có khoang chở hàng hở. | Xe tải chở các ô tô ở `img_002`; pickup ở `img_001`. | Ô tô con/SUV; van thân kín cỡ nhỏ. |
| `van` | Xe cơ giới thân kín cỡ nhỏ, có khoang chở hàng hoặc chở người kiểu van. Chỉ dùng khi hình dáng thân xe đủ rõ để phân biệt với `car` và `truck`. | Van thân hộp cỡ nhỏ. | SUV gán `car`; xe tải lớn hoặc pickup gán `truck`. |
| `motorcycle` | Xe cơ giới hai bánh dạng xe máy/mô tô; gán riêng với người ngồi trên xe nếu nhìn thấy. | Xe máy ở `img_005` và `img_026`. | Xe đạp không động cơ; xe con. |
| `person` | Người thật đang hiện diện trong cảnh, gồm người đi bộ, người lái và hành khách. | Người đi bộ hoặc người ngồi trên xe máy. | Tượng, ma-nơ-canh, hình người in/vẽ hoặc phản chiếu. |
| `ignore_region` | Vùng có đối tượng/vật thể không thuộc phạm vi taxonomy hoặc quá nhỏ để gán riêng theo quy tắc dưới đây; đây là vùng bỏ qua, không phải lớp đối tượng. | Tượng lớn ngoài phạm vi hoặc vùng đám đông không thể tách cá thể. | Không dùng thay cho một lớp hợp lệ chỉ vì chưa chắc; bật `can_review` và hỏi reviewer. |

Xe ba bánh chở khách (ví dụ tuk-tuk/cyclo) không khớp rõ với các định nghĩa lớp trên. Trong bản cá nhân này, tôi đề xuất đánh dấu vùng đó bằng `ignore_region`, không tự ép vào `motorcycle`, `car` hay `truck`. Cần đưa trường hợp này ra họp để nhóm chốt cách xử lý chung trước khi khóa taxonomy.

### Thuộc tính

| Thuộc tính | Giá trị | Quy tắc chọn |
|---|---|---|
| `occluded_level` | `0` | Không bị vật khác che, hoặc phần bị che ước tính không quá 10% diện tích/hình dáng đối tượng. |
| `occluded_level` | `1` | Bị che trên 10% đến 30%; vẫn thấy phần lớn đối tượng. |
| `occluded_level` | `2` | Bị che trên 30% đến 60%; vẫn nhận diện được lớp và xác định được box phần nhìn thấy. |
| `occluded_level` | `3` | Bị che trên 60%, nhưng phần còn thấy vẫn đủ để xác định chắc chắn lớp. Nếu không đủ căn cứ xác định lớp, không đoán lớp: bật `can_review` hoặc dùng `ignore_region` theo quyết định của reviewer. |
| `truncated` | `no` | Đối tượng không bị cắt bởi biên ảnh. Bị vật khác che không làm thuộc tính này thành `yes`. |
| `truncated` | `yes` | Đối tượng giao với biên ảnh và hình dáng cho thấy nó tiếp tục ra ngoài khung hình. |
| `can_review` | bật | Có bất định thực sự về lớp, ranh giới box, hoặc quy tắc áp dụng; ghi thêm vấn đề để reviewer biết cần xem gì. |
| `can_review` | tắt | Quyết định rõ theo guideline, kể cả khi đối tượng bị che/cắt nhưng vẫn nhận diện được. |

Các ngưỡng phần trăm che khuất trên là quy ước thao tác ước lượng bằng mắt để tăng nhất quán, không phải số đo pixel chính xác. Không đổi danh sách giá trị thuộc tính trong taxonomy khi chưa được nhóm thống nhất.

## 3. Quy tắc vẽ box

**P-01 — Box ôm phần nhìn thấy.** Vẽ hình chữ nhật sát biên ngoài của phần đối tượng nhìn thấy trong ảnh. Không mở rộng box qua vật che khuất để đoán hình dáng bị khuất; không đưa người/vật khác vào box. Với đối tượng bị cắt mép ảnh, box dừng tại mép ảnh và đặt `truncated=yes`.

**P-02 — Mỗi đối tượng là một box riêng.** Không gộp nhiều người hoặc nhiều phương tiện vào một box. Trong cảnh đông, chỉ gán từng cá thể khi có thể xác định ranh giới hợp lý; nếu một cụm người quá dày không thể tách nhất quán, dùng `ignore_region` cho đúng vùng cụm đó và ghi chú để reviewer kiểm tra.

**P-03 — Người và xe là hai đối tượng.** Khi thấy người lái/ngồi trên xe, gán một box `person` và một box riêng cho xe `motorcycle` (hoặc lớp xe phù hợp). Hai box có thể chồng lấn. Không gán người nếu chỉ thấy quần áo/vật thể mà không đủ căn cứ nhận ra người.

**P-04 — Xe chở xe.** Gán box cho xe chuyên chở (`truck`) và cho từng ô tô (`car`) được chở nếu từng xe nhìn thấy đủ rõ để nhận diện độc lập. Box của mỗi xe chỉ bao phần nhìn thấy của chính xe đó; không gộp xe chở và xe được chở. Áp dụng cho `img_002`.

**P-05 — Phân biệt vật thật với hình ảnh/đồ vật mô phỏng.** Chỉ gán người và phương tiện thật trong cảnh. Không gán tượng người/động vật, ma-nơ-canh, hình in, hình vẽ, nội dung trên màn hình hoặc phản chiếu như đối tượng thật. Nếu vùng mô phỏng nổi bật và có nguy cơ bị hiểu nhầm là đối tượng mục tiêu, đánh dấu `ignore_region`; ví dụ tượng người cưỡi ngựa ở `img_017`.

**P-06 — Vật nhỏ.** Nếu chiều cao box đối tượng dưới 20 px theo ảnh gốc, không tạo box riêng; dùng `ignore_region` cho vùng chứa vật nhỏ khi cần thể hiện rõ vùng bị loại khỏi gán nhãn. Từ 20 px trở lên, gán nếu đủ căn cứ nhận diện lớp. Không thay đổi ngưỡng 20 px đã đặt trong taxonomy.

**P-07 — Lớp không chắc.** Nếu đối tượng thuộc phạm vi nhưng chưa phân biệt được lớp, không tự chọn lớp gần giống và không dùng `ignore_region` để che bất đồng. Bật `can_review`, ghi ảnh/vùng/lý do; khi có quy trình nhóm thì đưa vào danh sách calibration.

**P-08 — Vùng bỏ qua.** Box `ignore_region` chỉ bao vùng cần bỏ qua, không dùng thay cho box hợp lệ bị che một phần. Không phủ rộng cả ảnh hoặc các đối tượng hợp lệ lân cận. Nếu có thể khoanh từng vùng không thuộc phạm vi, dùng các vùng riêng để reviewer thấy rõ quyết định.

**P-09 — Không có đối tượng.** Ảnh không có đối tượng thuộc phạm vi vẫn phải được giữ trong tập ảnh/COCO với trạng thái không có annotation; không tự xóa ảnh.

## 4. Ca khó đã xem

| Ảnh | Tình huống | Rule ID | Quyết định cá nhân | Lý do |
|---|---|---|---|---|
| `img_002.jpg` | Xe tải chở nhiều ô tô; các xe che khuất lẫn nhau. | P-01, P-04 | Gán `truck` cho xe chở và từng `car` nhìn thấy đủ rõ; box theo phần thấy được, đặt mức che khuất cho từng xe. | Mỗi phương tiện là một đối tượng độc lập; không coi toàn bộ đoàn xe là một box. |
| `img_005.jpg` | Nhiều người đi xe máy, chồng lấn và có người bị che. | P-01, P-02, P-03 | Tách từng người và xe máy nhận diện được; box chặt trên phần thấy được. Bật `can_review` nếu không xác định được cá thể/lớp. | Không bỏ người chỉ vì đang ngồi trên xe; tránh box gộp trong cảnh đông. |
| `img_017.jpg` | Tượng người cưỡi ngựa có hình dáng giống người/động vật thật. | P-05, P-08 | Không gán `person`; đề xuất khoanh tượng bằng `ignore_region`. | Đây là tượng, không phải người đang hiện diện; giữ dấu vết vùng dễ gây nhầm. |
| `img_026.jpg` | Người và xe thật ở trước hình vẽ/phong cảnh trên tường. | P-03, P-05 | Gán người và xe thật; không gán người/xe trong hình vẽ. | Phân biệt đối tượng trong cảnh với nội dung in/vẽ phía sau. |
| `img_001.jpg` | Pickup chở hàng; có người thật gần xe. | P-01, P-03 | Pickup vào `truck`; gán riêng người thật nhìn thấy được. | Khoang chở hàng hở giúp phân biệt pickup với ô tô con; người và xe là hai box. |

Các quyết định trên là đề xuất cá nhân. Đặc biệt, cách xử lý tuk-tuk/cyclo và phạm vi dùng `ignore_region` cần được nhóm thảo luận, thống nhất trước khi áp dụng cho lượt gán chính thức.

## 5. QC và phiên bản

- Dùng các ngưỡng cố định trong `submission/taxonomy.json`: box nhỏ có chiều cao dưới 50 px dùng IoU threshold 0.70, box từ 50 px trở lên dùng 0.85; IAA mục tiêu IoU trung bình ít nhất 0.85 và cùng lớp ít nhất 95%; ghép box ở IoU ít nhất 0.50; tỷ lệ ảnh lỗi tối đa 2%.
- IAA chỉ tính trên các cặp box ghép được; luôn ghi tử số/mẫu số và không diễn giải N/A thành 0.
- Script có thể kiểm cấu trúc COCO, lớp/thuộc tính, kích thước/vị trí và độ lệch; người review vẫn phải xem ảnh gốc để phát hiện box lỏng, vật bỏ sót hoặc hiểu sai chung.
- Ca chưa chắc được ghi kèm mã ảnh, vùng, rule ID và lý do. Reviewer/nhóm quyết định; mọi sửa đổi ảnh hưởng nhãn phải được ghi lại và làm tăng phiên bản guideline.
- Bản này chưa thay thế `guideline_v1.0_agreed.md`; chỉ dùng sau khi nhóm chốt quy tắc chung.

| Phiên bản | Thay đổi | Lý do |
|---|---|---|
| v0.1 | Viết guideline cá nhân; đề xuất quy tắc cho box, lớp, thuộc tính và các ca khó. | Bổ sung các trường hợp chưa được quy định trong guideline khởi đầu; dùng `img_001`, `img_002`, `img_005`, `img_017`, `img_026` làm ví dụ. |
