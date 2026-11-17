---
day: "D07"
title: "Day 07 Lab — Guideline, Taxonomy & QC"
description: "Xây dựng guideline gán nhãn đủ dùng, chuẩn hóa taxonomy theo JSON Schema, gán bounding box độc lập bằng mã thành viên trên CVAT, đo IAA, calibration có truy vết phiên bản và bàn giao lô nhãn với quyết định Release / Chưa đủ điều kiện / Rework."
outcomes:
  - "Viết được guideline cá nhân (`guideline_<mã>.md`) từ bản khởi đầu v0 và hợp nhất thành `guideline_v1.0_agreed.md` kèm mã quy tắc `R-01`, `R-02`… và `submission/taxonomy.json` hợp lệ theo `schemas/taxonomy.schema.json`."
  - "Chia ảnh gán mù đôi K=2 (hoặc K=3 với nhóm 5 người) theo mã thành viên 3 chữ số và xuất đủ nhãn COCO 1.0 từ CVAT vượt qua `python scripts/validate_labels.py --all`."
  - "Đo độ đồng thuận IAA bằng `qc_compare.py`, trực quan hóa ca lệch bằng `viz_disagreement.py`, hoàn thiện bảng 9 cột `calibration_decisions.csv`, `submission/guideline_change.json` và tạo `labels_calibrated.json` kèm `batch_manifest.json`."
  - "Thực hiện duyệt QC toàn lô theo vòng (`qc_sample.py --round 1`, `qc_report.py --round 1`), hoàn thiện `submission/qc/QC_REPORT.md` đủ 10 trường bắt buộc với quyết định Release / Chưa đủ điều kiện / Rework và vượt qua `python scripts/check_submission.py --round 1` với 0 lỗi."
prerequisites:
  - "Đã làm quen thao tác tạo Project, Task, vẽ Rectangle và xuất COCO 1.0 trên CVAT."
  - "Có Python 3.9+, Git và mã thành viên ba chữ số (ví dụ `101`, `102`, `103`)."
  - "Có tài khoản CVAT của lớp hoặc CVAT local (`v2.74.1`)."
requiredTools:
  - "Python 3.9+ với `pillow>=10.0` và `jsonschema>=4.23,<5`"
  - "CVAT (`http://localhost:8080` bản local hoặc instance CVAT của lớp)"
  - "Git và trình duyệt web"
commonErrors:
  - "`validate_labels.py` báo tên lớp lạ → Project CVAT còn dùng bộ nhãn cũ; tạo lại Project từ `cvat/labels_generated.json` (hoặc `cvat/labels_final.json` nếu đổi schema)."
  - "Thiếu hoặc thừa ảnh trong file nhãn → Kiểm tra Task CVAT để bảo đảm chứa đúng ảnh trong `submission/qc/assignments/<mã>.txt`."
  - "Thiếu thuộc tính sau khi export COCO 1.0 → Kiểm tra cấu hình Project, lưu lại box rồi export lại."
  - "`build_final.py` báo IAA đã đổi → Lưu bảng `calibration_decisions.csv` cũ ra nơi khác, xóa file cũ để script tạo lại bảng khớp `calibration_context.json` mới."
  - "`qc_report.py` báo lệch phiên bản hoặc Chưa đủ điều kiện → Chạy `qc_sample.py --round <số mới>` mỗi khi thay đổi nhãn cuối, giữ nguyên vòng cũ để truy vết."
requiresSubmission: true
workMode: "team"
---

# Day 07 Lab — Guideline, Taxonomy & QC

Bài lab này thực hành quy trình chuẩn bị dữ liệu và kiểm soát chất lượng (QC) theo nhóm **2–5 người** trong **4 giờ** trên toàn bộ **40 ảnh đường phố** (`data/images/img_001.jpg` đến `img_040.jpg`). Bạn nhận bản [guideline/guideline_v0_starter.md](guideline/guideline_v0_starter.md) cố ý sơ sài để nhóm tự phát hiện tình huống biên, viết lại đặc tả đủ dùng, gán nhãn độc lập trên CVAT theo **mã thành viên ba chữ số**, đo độ đồng thuận giữa người gán (IAA), họp calibration có truy vết phiên bản và duyệt toàn lô để ra quyết định **Release / Chưa đủ điều kiện / Rework**.

:::image{src="docs/assets/sample_grid.jpg" alt="Lưới 6 ảnh mẫu trong bộ dữ liệu đường phố gồm tuk-tuk, xe chở ô tô, tượng đồng, xe diễu hành, tượng bán tải và ma-nơ-canh" caption="Những tình huống thực tế trong 40 ảnh mà guideline v0 chưa xử lý: tuk-tuk, xe chở ô tô, tượng, xe diễu hành, ma-nơ-canh và phản chiếu gương."}
:::

## Pha 0 — Chuẩn bị repository, mã thành viên và môi trường

Trước khi đọc ảnh hay mở CVAT, cả nhóm clone repository của lab, cài các gói phụ thuộc Python và nhận **mã thành viên ba chữ số** (ví dụ `101`, `102`, `103`). Quy ước của bài yêu cầu dùng mã thành viên xuyên suốt trong tên file, tên Task CVAT và phiếu duyệt; **tránh** đưa họ tên, MSHV, email hay tài khoản cá nhân vào tên file, Task hoặc tiêu đề `README.md` (coach giữ bảng đối chiếu mã ở kênh riêng của lớp).

:::repository{url="https://github.com/VinUni-AI20k/K5-L23-Day07-Guideline-Taxonomy-QC" label="Repo gốc Day 07 — K5-L23-Day07-Guideline-Taxonomy-QC"}
- [Repository gốc](https://github.com/VinUni-AI20k/K5-L23-Day07-Guideline-Taxonomy-QC)
:::

Từ thư mục gốc repository, chọn tab phù hợp với hệ điều hành để tạo môi trường ảo Python 3.9+ và cài đủ hai thư viện bắt buộc trong `requirements.txt` (`pillow>=10.0` cho vẽ overlay và `jsonschema>=4.23,<5` cho kiểm tra schema `taxonomy.json`).

:::code-tabs{title="Cài đặt môi trường từ thư mục gốc repository"}
```powershell {title="Windows (PowerShell)"}
git clone https://github.com/VinUni-AI20k/K5-L23-Day07-Guideline-Taxonomy-QC.git
cd K5-L23-Day07-Guideline-Taxonomy-QC
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
```bash {title="macOS / Ubuntu (Bash)"}
git clone https://github.com/VinUni-AI20k/K5-L23-Day07-Guideline-Taxonomy-QC.git
cd K5-L23-Day07-Guideline-Taxonomy-QC
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```
:::

Sau khi cài đặt, hãy điền tên nhóm, danh sách mã thành viên ba chữ số, người điều phối và người review bản cuối vào [TEAM.md](TEAM.md), đồng thời xác nhận bộ kiểm thử tự động chạy thông suốt trước khi bắt đầu.

1. Chạy `python -m unittest discover -s tests -v` từ thư mục gốc để xác nhận môi trường Python đã sẵn sàng (tất cả `20` test trong `tests/test_workflow.py` đều phải trả về `OK`).
2. Điền mã thành viên ba chữ số của 2–5 người vào [TEAM.md](TEAM.md) và hỏi coach kênh nộp riêng của từng pha.
3. Mở trình duyệt tới instance CVAT của lớp (hoặc `http://localhost:8080` khi chạy Docker local), đăng nhập và kiểm tra trang Projects tải bình thường.

:::image{src="walkthrough_images/01_cvat_projects.png" alt="Giao diện trang Projects của CVAT sau khi đăng nhập thành công" caption="Trang Projects trên CVAT v2.74.1 sẵn sàng trước khi bước vào các pha gán nhãn."}
:::

:::checklist{title="Tín hiệu sẵn sàng trước Pha 1" tone="info"}
- [ ] `python -m pip install -r requirements.txt` cài đủ `pillow` và `jsonschema`.
- [ ] `python -m unittest discover -s tests -v` chạy qua `20/20` test `OK`.
- [ ] Đã điền danh sách mã thành viên ba chữ số vào `TEAM.md`.
- [ ] Đăng nhập được CVAT và mở xem được ảnh trong `data/images/`.
:::

## Pha 1 — Soi 40 ảnh và viết guideline cá nhân độc lập

### Bản chất vấn đề: vì sao phải khảo sát cả 40 ảnh trước khi vẽ box?

Nếu cả nhóm mở CVAT lên và vẽ box ngay dựa trên [guideline/guideline_v0_starter.md](guideline/guideline_v0_starter.md), hai thành viên nhìn cùng một bức ảnh chắc chắn sẽ đưa ra hai cách gán khác nhau. Bản v0 chỉ định nghĩa sơ lược năm lớp (`car`, `truck`, `van`, `motorcycle`, `person`) và mô tả thuộc tính `occluded_level` bằng các cụm từ định tính như "che ít", "che nhiều", "không rõ". Trong khi đó, 40 ảnh của bài lab chứa hàng loạt tình huống biên trên đường phố: xe ba bánh tuk-tuk (`img_004.jpg`, `img_035.jpg`), xe tải chở 8 ô tô con trên hai sàn (`img_002.jpg`), xe buýt (`img_009.jpg`, `img_037.jpg`), tượng đồng và tượng đá (`img_011.jpg`, `img_017.jpg`, `img_027.jpg`), ma-nơ-canh và đồ chơi trong tủ kính (`img_033.jpg`, `img_038.jpg`), chân dung trên biển quảng cáo (`img_018.jpg`), phản chiếu qua gương chiếu hậu (`img_020.jpg`), cùng xe đạp và xích lô không động cơ (`img_006.jpg`, `img_029.jpg`, `img_039.jpg`).

Mục tiêu của Pha 1 là để mỗi thành viên **tự đọc hết 40 ảnh một mình** và ghi lại toàn bộ các chỗ v0 chưa trả lời được trước khi họp nhóm. Việc khảo sát độc lập giúp nhóm phát hiện những cách hiểu trái chiều tự nhiên giữa hai người gán; nếu bàn bạc trước rồi mới viết, nhóm sẽ mất đi cơ hội kiểm chứng độ mơ hồ thực tế của đặc tả ban đầu.

### Giải nghĩa các khái niệm quyết định thao tác

Khi chuyển bản nháp v0 sang khung [guideline/TEMPLATE_guideline.md](guideline/TEMPLATE_guideline.md), bạn cần phân biệt ba yếu tố bắt buộc. Thứ nhất, **ngưỡng đo được** là ranh giới định lượng giúp hai người chấm giống nhau một thuộc tính — thay vì "che ít/nhiều", bạn chốt `occluded_level = 1` khi vật bị che 1–30% diện tích, `2` khi che 31–70%, và `3` khi che trên 70% nhưng vẫn nhận dạng chắc chắn. Thứ hai, **phản ví dụ** là vật trông giống một lớp nhưng bị loại khỏi lớp đó (như tượng xe bán tải ở `img_027.jpg` hay xe mô hình đồ chơi ở `img_038.jpg`). Thứ ba, bạn cần tách bạch **ca loại theo quy tắc** (tình huống bạn tự tin loại bỏ bằng định nghĩa lớp) với **ca cần hỏi reviewer** (tình huống biên như bán tải gắn nắp thùng cao `Master 75` ở `img_037.jpg` cần đưa ra họp Pha 2). Với cặp **người đi xe máy**, hãy tự quyết định trước số box, lớp và phạm vi ôm của từng box rồi thử áp dụng lại đúng quy tắc đó trên một ảnh khác để tự kiểm tính nhất quán.

### Lựa chọn thiết kế: tách file theo mã thành viên và gửi riêng

Mỗi thành viên sao chép khung guideline thành `submission/guidelines/individual/guideline_<mã>.md` (ví dụ `guideline_101.md`). Dùng mã ba chữ số giúp tách bạch đóng góp cá nhân mà không làm lộ thông tin định danh trong gói nộp. Sau khi gửi riêng cho coach/nhóm trưởng ở cuối Pha 1, bạn **giữ nguyên bản cá nhân** để đối chiếu với quyết định chung của nhóm ở Pha 2; `check_submission.py` sẽ kiểm tra mã băm SHA-256 để bảo đảm không có file cá nhân nào giống nguyên bản v0.

:::callout{tone="warning" title="Quy tắc độc lập và sử dụng AI ở Pha 1"}
Trong Pha 1, không xem guideline của thành viên khác và không hỏi nhau cách gán từng ảnh cho tới khi mọi người đều đã nộp riêng bản cá nhân. Day 07 yêu cầu **người thật** quyết định và vẽ box; không dùng mô hình hay AI nhìn ảnh để chọn lớp hoặc gán box thay bạn.
:::

### Các bước thực hiện Pha 1

1. Mở thư mục `data/images/` và xem lần lượt toàn bộ `img_001.jpg` đến `img_040.jpg` (chưa vẽ box nào).
2. Sao chép [guideline/TEMPLATE_guideline.md](guideline/TEMPLATE_guideline.md) thành `submission/guidelines/individual/guideline_<mã>.md`.
3. Điền đủ 5 mục trong bản cá nhân: Mục tiêu mô hình 2D; Bảng định nghĩa lớp kèm ví dụ và phản ví dụ; Thuộc tính với ngưỡng đo được (`occluded_level`, `truncated`, `can_review`); Quy tắc cho người đi xe máy, xe chở xe, vật bị che, vật nhỏ `< 20 px`, tượng, phản chiếu; và Bảng ca khó nêu rõ tên ảnh `img_0xx.jpg`, quyết định và lý do.
4. Khởi tạo trước `submission/individual_notes/<mã>.md` theo mẫu [docs/INDIVIDUAL_NOTE_TEMPLATE.md](docs/INDIVIDUAL_NOTE_TEMPLATE.md) và điền ngay Mục 1 (ba ca khó vừa tìm ra).
5. Gửi riêng file `guideline_<mã>.md` theo hướng dẫn của coach; chỉ mở xem bản của bạn khác khi cả nhóm đã nộp xong để chuẩn bị cho buổi họp Pha 2.

### Checkpoint Pha 1 và bước tiếp theo

Bạn đạt mốc Pha 1 khi người đọc bất kỳ mở `submission/guidelines/individual/guideline_<mã>.md` có thể tìm lại đúng bức ảnh `img_0xx.jpg` cho từng ví dụ, hiểu lý do quyết định ban đầu của bạn và kiểm chứng được ngưỡng phần trăm của từng thuộc tính. Khi mọi thành viên đều đã nộp riêng, cả nhóm mở chéo các bản cá nhân để bước vào buổi họp chốt đặc tả ở Pha 2.

## Pha 2 — Họp thống nhất guideline v1.0 và kiểm schema taxonomy

### Bản chất vấn đề: khóa đặc tả 2D bằng mã quy tắc `R-01`, `R-02`…

Khi đối chiếu chéo các bản cá nhân từ Pha 1, những bất đồng cốt lõi lập tức lộ diện: trên `img_002.jpg`, một bạn chỉ muốn gán một box `truck` cho xe chở ô tô trong khi bạn khác gán thêm từng box `car` trên hai sàn; trên `img_004.jpg`, `img_016.jpg` và `img_035.jpg`, xe tuk-tuk 3 bánh chưa có lớp phù hợp; trên `img_009.jpg`, `img_031.jpg`, `img_037.jpg` và `img_040.jpg`, xe buýt cỡ lớn chưa xuất hiện trong v0; còn trên `img_037.jpg`, bán tải gắn nắp thùng cao gây tranh cãi giữa `van` và `truck`. Nếu không giải quyết dứt điểm và khóa chặt những quyết định này trước khi gán nhãn, phép đo IAA ở Pha 4 sẽ thất bại do mỗi người làm theo một quy tắc riêng.

### Giải nghĩa phép thử lớp vs thuộc tính và mã quy tắc `R-xx`

Khi hiệu chỉnh `submission/taxonomy.json`, bạn áp dụng phép thử trong [GUIDE.md](GUIDE.md): **"Mô hình phát hiện vật 2D có phải đoán ra thông tin này khi suy luận không?"**. Nếu **có** (như phân biệt `bus`, `tuk_tuk` với `car`, `motorcycle`), thông tin đó thuộc về danh sách `classes`. Nếu **không** — chỉ dùng để lọc mẫu khó hoặc kiểm QC như `occluded_level`, `truncated`, `can_review` — thì xếp vào `attributes`. Riêng `ignore_region` đánh dấu vùng đám đông dày đặc hoặc cụm vật cao `< 20 px`. Đồng thời, với các quy tắc hay được dẫn lại khi tranh luận (như không gán tượng/phản chiếu, không gán xe chủ, cách vẽ xe chở xe, cách ôm sát phần nhìn thấy), hãy gắn mã **`R-01`**, **`R-02`**, **`R-03`**… trong `guideline_v1.0_agreed.md` để sang Pha 5 và Pha 6 cả nhóm dẫn chiếu chính xác mã quy tắc vào phiếu quyết định và phiếu QC.

### Lựa chọn thiết kế: xác thực `schemas/taxonomy.schema.json` và giữ nguyên `rules`

Script `scripts/make_cvat_labels.py` không chỉ xuất tệp JSON cho CVAT mà còn kiểm tra `submission/taxonomy.json` dựa trên `schemas/taxonomy.schema.json` (yêu cầu tên lớp/thuộc tính viết `snake_case` chữ thường, `checkbox` có `values` rỗng và `default` là `"true"`/`"false"`, và khóa cứng toàn bộ 8 ngưỡng trong mục `"rules"`). Nếu sửa nhầm ngưỡng trong `"rules"`, script sẽ từ chối chạy ngay lập tức. Khi cập nhật v1.0 (ví dụ bổ sung `bus` và `tuk_tuk`), bạn phải tăng `"version": "v1.0"` rồi chạy `make_cvat_labels.py` để đồng bộ nhãn sang CVAT.

### Các bước thực hiện Pha 2

1. Cả nhóm họp đối chiếu các bản `guideline_<mã>.md`, thảo luận trên ảnh gốc để chốt một quy tắc duy nhất cho từng bất đồng (phần nhìn thấy, che khuất, cắt mép, người đi xe máy, xe chở xe, ca ngoài phạm vi) và gắn mã `R-01`, `R-02`… cho các quy tắc trọng tâm.
2. Lưu bản thống nhất tại `submission/guidelines/guideline_v1.0_agreed.md` (đủ 5 phần và bảng lịch sử `v0 → v1.0`).
3. Cập nhật `submission/taxonomy.json`: đặt `"version": "v1.0"`, chỉnh `"classes"` và `"attributes"` khớp `guideline_v1.0_agreed.md`, **giữ nguyên mục `"rules"`**.
4. Chạy lệnh kiểm schema và sinh bộ nhãn cho CVAT:

```bash
python scripts/make_cvat_labels.py
```

   Nếu schema hợp lệ, terminal in toàn bộ mảng JSON 8 nhãn kèm dòng `# Đã ghi cvat\labels_generated.json (taxonomy v1.0). Dán nội dung vào CVAT: Project -> Labels -> Raw -> Done.`. Nếu báo lỗi ở trường nào, sửa đúng trường đó trong `submission/taxonomy.json` rồi chạy lại.

5. Mở CVAT, vào **Projects → Create new project**, chọn tab **Labels → Raw**, dán toàn bộ `cvat/labels_generated.json`, bấm **Done** rồi **Submit & Open** và kiểm tra đủ thuộc tính cho từng lớp. Sau bước này, **khóa cứng** `guideline_v1.0_agreed.md` và `taxonomy.json` cho toàn bộ lượt gán độc lập ở Pha 3.

:::image{src="walkthrough_images/02_cvat_project_labels.png" alt="Trang Project trên CVAT hiển thị đủ 8 nhãn màu sinh từ make_cvat_labels.py" caption="Project trên CVAT sau khi dán JSON từ cvat/labels_generated.json: đủ 8 lớp (car, truck, van, bus, tuk_tuk, motorcycle, person, ignore_region)."}
:::

### Checkpoint Pha 2 và bước tiếp theo

Pha 2 đạt chuẩn khi trên cùng một bức ảnh người đi xe máy, mọi thành viên giải thích cùng một mã quy tắc và dự đoán cùng số lượng box. Với `cvat/labels_generated.json` đã tạo và bộ đặc tả v1.0 đã khóa, nhóm chuyển sang Pha 3 để chia ảnh và gán độc lập.

## Pha 3 — Chia ảnh cân bằng và gán nhãn độc lập trên CVAT

### Bản chất vấn đề: gán mù đôi và thu thập vấn đề cấp ảnh

Phép đo đồng thuận IAA chỉ có giá trị khi mỗi ảnh được `K=2` người (hoặc `K=3` với nhóm 5 người) gán hoàn toàn độc lập. Nếu trong lúc gán bạn hỏi đồng đội về một ca lưỡng lự, độ đồng thuận ở Pha 4 sẽ cao giả tạo. Mọi băn khoăn phát sinh trong Pha 3 đều được ghi nhận bằng hai cơ chế chuẩn thay vì tự đoán: tick cờ `can_review` trên box đã vẽ, hoặc ghi nhận vấn đề cấp ảnh vào `submission/qc/image_issues.csv` (với 4 cột `image,annotator,region,note`) cho những đối tượng bạn **chưa vẽ được box** để nhóm chốt sau khi khóa nhãn.

### Giải nghĩa quy tắc thao tác CVAT và thuộc tính

Khi làm việc trên giao diện CVAT ([docs/CVAT_SETUP.md](docs/CVAT_SETUP.md)), có ba điểm kỹ thuật dễ mất điểm nếu thao tác sai:
- **`occluded_level` vs cờ `Q` của CVAT**: Script chỉ đọc thuộc tính `occluded_level` (`0`, `1`, `2`, `3`) trong panel **Objects**; cờ `occluded` mặc định của CVAT (phím `Q`) bị bỏ qua.
- **Ảnh không có đối tượng**: Các ảnh chỉ chứa tượng, ma-nơ-canh, đồ chơi hay phản chiếu (`img_017.jpg`, `img_020.jpg`, `img_027.jpg`, `img_033.jpg`, `img_038.jpg`) vẫn phải giữ nguyên trong Task CVAT và xuất bình thường trong COCO 1.0 (0 annotation).
- **Ranh giới từ khóa `submission/labels/<mã>.json`**: File xuất ra phải đặt tên đúng mã ba chữ số (ví dụ `101.json`, `102.json`, `103.json`), không gắn họ tên hay MSHV.

### Lựa chọn thiết kế: `split_assign.py` an toàn và kiểm cấu trúc từng người

Script `scripts/split_assign.py` kiểm tra nghiêm ngặt định dạng mã 3 chữ số, chặn ghi vào đường dẫn symlink hoặc thư mục ảnh chứa file lạ ngoài `data/images/`, và dùng chung `--seed 42` để mọi thành viên tạo ra cùng một `submission/qc/assignment.csv` (trong chạy thử nhóm 3 người `101,102,103`, tải chia là `26`, `27`, `27` ảnh, mỗi ảnh 2 người gán). Sau khi export từ CVAT, mỗi người tự kiểm file của mình bằng `python scripts/validate_labels.py submission/labels/<mã>.json`. Script này kiểm tra cấu trúc COCO, kích thước ảnh, tọa độ bbox không vượt biên ảnh, lớp/thuộc tính thuộc taxonomy và đối chiếu khớp hoàn toàn danh sách ảnh được giao, nhưng **không tự biết** box có ôm sát vật thật hay có bỏ sót vật hay không.

### Các bước thực hiện Pha 3

1. Một thành viên chạy lệnh chia ảnh từ thư mục gốc (thay bằng mã ba chữ số của nhóm) và chia sẻ `submission/qc/assignment.csv`:

```bash
python scripts/split_assign.py --members 101,102,103 --copy-images
```

   Mỗi thành viên nhận danh sách ảnh tại `submission/qc/assignments/<mã>.txt` và bộ ảnh sao chép sẵn trong `work/<mã>/images/` (nhóm 3 người: `101` có `26` ảnh, `102` có `27` ảnh, `103` có `27` ảnh).

2. Trên CVAT, tạo Task riêng `task-<mã>` thuộc Project đã tạo ở Pha 2, tải lên **toàn bộ** ảnh trong `work/<mã>/images/` (số frame phải khớp số dòng trong `assignments/<mã>.txt`).

:::image{src="walkthrough_images/03_cvat_task_created.png" alt="Trang chi tiết Task trên CVAT hiển thị đủ số khung hình được giao" caption="Trang chi tiết Task trên CVAT xác nhận số lượng frame khớp với danh sách phân công."}
:::

3. Mở Job và vẽ box bằng phím `N` (Rectangle) theo đúng `guideline_v1.0_agreed.md`, chọn `occluded_level`, `truncated` và `can_review` ở panel **Objects** bên phải, dùng `F`/`D` chuyển ảnh và `Ctrl+S` lưu thường xuyên.

:::image{src="walkthrough_images/04_cvat_annotation_workspace.png" alt="Không gian gán nhãn CVAT trên ảnh img_001.jpg hiển thị box truck và person cùng thuộc tính occluded_level=1 và truncated=yes" caption="Thao tác vẽ Rectangle và chọn thuộc tính occluded_level, truncated trên CVAT cho img_001.jpg."}
:::

4. Vào **Actions → Export task dataset**, chọn **COCO 1.0**, **tắt Save images**, bấm **OK**; sang trang **Requests** tải file `.zip`, lấy `annotations/instances_default.json` lưu thành `submission/labels/<mã>.json`.

:::image{src="walkthrough_images/05_cvat_export_coco.png" alt="Trang Requests trên CVAT báo Export Annotations định dạng COCO 1.0 đạt trạng thái Finished 100%" caption="Trang Requests trên CVAT xác nhận hoàn tất xuất COCO 1.0 (Save images tắt)."}
:::

5. Kiểm tra cấu trúc và phạm vi ảnh được giao trước khi nộp riêng cho người điều phối:

```bash
python scripts/validate_labels.py submission/labels/101.json
```

   Output đạt chuẩn báo rõ `submission\labels\101.json: hợp lệ về cấu trúc, 26 ảnh.` (và lưu ý reviewer kiểm nội dung box bằng mắt). Nếu thấy cảnh báo `[WARN] ... rà lại quy tắc vật nhỏ`, kiểm tra lại các box có chiều cao `< 20 px`.

:::callout{tone="info" title="Giữ tính độc lập khi nộp nhãn Pha 3"}
Mỗi thành viên nộp riêng file `submission/labels/<mã>.json` cho người điều phối hoặc kênh riêng của lớp. Chỉ tập hợp toàn bộ nhãn vào cùng thư mục `submission/labels/` sau khi mọi thành viên đã hoàn thành và khóa bản độc lập.
:::

### Checkpoint Pha 3 và bước tiếp theo

Pha 3 hoàn tất khi cả nhóm đủ `80/80` lượt gán (`26 + 27 + 27` cho 3 người `K=2`), mọi file `<mã>.json` đều vượt qua `validate_labels.py` và các ảnh 0 đối tượng vẫn có mặt đầy đủ trong COCO JSON. Nếu có ca chưa vẽ được box, nhóm tổng hợp vào `submission/qc/image_issues.csv` trước khi chạy so sánh chéo ở Pha 4.

## Pha 4 — Đo độ đồng thuận IAA và trực quan hóa bất đồng

### Bản chất vấn đề: kiểm độ phủ 100%, mẫu số và lỗi hai người cùng sai

Lệnh `python scripts/qc_compare.py` là cổng kiểm tra định lượng của đặc tả v1.0. Trên phiên bản script hiện hành, `qc_compare.py` **dừng ngay nếu chưa đủ 100% lượt gán** so với `assignment.csv`, đồng thời ghi nhận SHA-256 của toàn bộ đầu vào (`assignment.csv`, `taxonomy.json`, `labels/*.json`, `image_issues.csv`) vào `iaa_summary.json` để chống việc sửa lén đầu vào sau khi đã họp calibration.

Bạn cần nhớ hai nguyên tắc đọc số liệu IAA: thứ nhất, IoU trung bình (ngưỡng `>= 0.85`) và % cùng lớp (ngưỡng `>= 95%`) **chỉ tính trên các cặp box ghép 1–1** (IoU `>= 0.5`), không có cặp ghép thì ghi N/A — do đó box bị bỏ sót hẳn không kéo tụt IoU trung bình mà nằm riêng ở các ca `bo_sot_thua`. Thứ hai, ngay cả khi IoU cao và ít bất đồng, hai người vẫn có thể **giống nhau nhưng cùng sai** quy tắc (ví dụ cả hai cùng vẽ `person` lên tượng đồng ở `img_017.jpg`); vì vậy sau khi khóa bản độc lập, nhóm phải đối chiếu thêm ca tham chiếu của coach để bắt các lỗi đồng thuận sai.

### Giải nghĩa 7 loại ca cần xem trong `calibration_candidates.csv`

Ngoài 5 loại bất đồng đối tượng quen thuộc (`bo_sot_thua`, `sai_lop`, `iou_thap`, `sai_thuoc_tinh`, `co_can_review`), `qc_compare.py` hiện kiểm tra thêm hai tín hiệu quan trọng:
- **`bat_dong_ignore`**: Xuất hiện khi vùng `ignore_region` của hai người không ghép được với nhau, hoặc khi chỉ một người đặt vùng `ignore_region` phủ lên box của người kia (tránh việc một vùng ignore tự ý che khuất lỗi bỏ sót).
- **`can_review_anh`**: Đọc tự động từ `submission/qc/image_issues.csv` cho những ca cấp ảnh chưa vẽ được box ở Pha 3.

### Lựa chọn thiết kế: tách nguyên nhân trên ảnh chồng nhãn `work/viz/`

Khi xem ảnh trong `work/viz/` (mỗi người gán một màu) đối chiếu với [docs/QC_CHEATSHEET.md](docs/QC_CHEATSHEET.md), nhóm phân loại nguyên nhân thành ba nhóm để định hướng Pha 5: (1) cả hai lệch trên cùng dạng tình huống (như ranh giới hàng hóa chất cao trên tuk-tuk ở `img_035.jpg` hay bán tải nắp thùng cao ở `img_037.jpg`) → quy tắc mơ hồ, phải sửa guideline; (2) chỉ một người lệch trên quy tắc đã chốt rõ (như `102` quên gán 8 ô tô con trên sàn xe chở ô tô ở `img_002.jpg`) → người gán chưa nắm chắc quy tắc; (3) giống nhau nhưng cùng sai khi đối chiếu ca tham chiếu → cùng hiểu sai khái niệm, phải rà soát lại cả lô.

### Các bước thực hiện Pha 4

1. Khi đủ nhãn của cả nhóm trong `submission/labels/`, chạy kiểm tra đồng loạt rồi đo IAA:

```bash
python scripts/validate_labels.py --all
python scripts/qc_compare.py
```

   Trong lần chạy mẫu với 3 mã `101`, `102`, `103` trên 40 ảnh, script xác nhận lượt gán **`80/80`**, **`177` cặp box ghép**, IoU trung bình **`0.913`** (ngưỡng `0.85`), đồng thuận lớp **`98.9%`** (ngưỡng `95%`) → **ĐẠT**, đồng thời phát hiện **`45` ca cần xem trên `21` ảnh bị cờ** (`iou_thap: 25`, `bo_sot_thua: 12`, `co_can_review: 5`, `sai_lop: 2`, `sai_thuoc_tinh: 1`).

2. Vẽ ảnh chồng nhãn cho toàn bộ các ảnh bị cờ:

```bash
python scripts/viz_disagreement.py --images flagged
```

3. Mở `work/viz/_overview.png` và các ảnh cụ thể như `work/viz/img_002.png`, `work/viz/img_035.png` để đối chiếu từng dòng trong `submission/qc/calibration_candidates.csv` và bảng trong `submission/qc/iaa_summary.md`.

:::image{src="walkthrough_images/06_viz_disagreement_overview.png" alt="Bảng tổng quan 21 ảnh bị cờ trong work/viz/_overview.png" caption="Bảng tổng quan work/viz/_overview.png hiển thị toàn bộ 21 ảnh có ca bất thường cần họp calibration."}
:::

:::image{src="walkthrough_images/08_viz_disagreement_img002.png" alt="Ảnh img_002.jpg chồng box đỏ và xanh dương cho thấy một người gán đủ 8 xe con trên sàn và một người bỏ sót" caption="Bất đồng bo_sot_thua trên img_002.jpg: thành viên 103 (xanh) gán đủ 8 xe con trên 2 tầng, thành viên 102 (đỏ) bỏ sót toàn bộ xe trên sàn."}
:::

:::image{src="walkthrough_images/07_viz_disagreement_img035.png" alt="Ảnh img_035.jpg chồng box cho thấy một người chỉ ôm khung tuk-tuk và người kia bao cả khối bao tải trên nóc" caption="Bất đồng kích thước trên img_035.jpg: thành viên 101 (đỏ) chỉ ôm thân tuk-tuk, còn 103 (xanh) kéo box bao cả khối bao tải phía trên."}
:::

### Checkpoint Pha 4 và bước tiếp theo

Bạn hoàn thành Pha 4 khi đọc rõ mẫu số `177` cặp box ghép trong `iaa_summary.md`, giải thích được lý do bất đồng trên `work/viz/` và chỉ ra được điều mà số đo IAA tự động không tự xác nhận được (lỗi hai người cùng sai). Giờ đây `iaa_summary.json`, `calibration_candidates.csv`, `flagged_images.txt` và `consensus_draft.json` là cơ sở đầu vào bị khóa hash cho quy trình calibration ở Pha 5.

## Pha 5 — Chốt ca calibration, nâng cấp v1.1 và tạo nhãn cuối

### Bản chất vấn đề: ràng buộc quyết định, thay đổi ngữ nghĩa và checksum bàn giao

Trong quy trình mới, calibration không dừng ở việc sửa vài file ảnh rồi ghi đè nhãn: mọi quyết định, mức độ thay đổi guideline và đường dẫn COCO sau sửa đều được liên kết bằng mã băm SHA-256 (`calibration_context.json` và `batch_manifest.json`). Nếu nhóm thay đổi quy tắc chọn vật, phân lớp, ranh giới box hoặc thuộc tính (`kind: "semantic"`), quyết định đó không chỉ ảnh hưởng riêng vài ảnh bị cờ mà buộc phải **kiểm lại toàn bộ lô 40 ảnh** để bảo đảm không sót các ảnh trước đó chưa bị gắn cờ.

### Giải nghĩa `calibration_decisions.csv` (9 cột) và `guideline_change.json`

Khi chạy `python scripts/build_final.py` lần đầu, script tạo `submission/qc/calibration_context.json` và sinh bảng mẫu `submission/qc/calibration_decisions.csv` gồm **9 cột**:
- `case_id`, `image`: điền sẵn theo `calibration_candidates.csv`.
- `quyet_dinh`, `quy_tac_ghi_vao_guideline` (mã `R-01`, `R-07`…), `phien_ban_guideline` (`v1.1`), `nguoi_chot` (mã thành viên): quyết định và cơ sở quy tắc.
- `phieu_sua`, `kiem_lai`: vết chỉnh sửa (ảnh/box nào đã sửa) và kết quả người kiểm lại.
- `pham_vi`: `anh` (chỉ ảnh đó) hoặc `lo` (quy tắc đổi nghĩa, phải kiểm cả lô).

Song song với `submission/guidelines/guideline_v1.1_calibrated.md`, nhóm bắt buộc tạo `submission/guideline_change.json` với trường `"kind"` là `"editorial"` (chỉ sửa câu chữ, giữ nguyên quy tắc) hoặc `"semantic"` (đổi cách chọn vật, lớp, box, thuộc tính — đòi hỏi ít nhất một dòng `pham_vi=lo` và mở rộng phạm vi sửa lên toàn bộ 40 ảnh). Nếu có đổi lớp/thuộc tính của taxonomy, lưu thêm `submission/taxonomy_v1.1.json` (tăng version) và chạy `python scripts/make_cvat_labels.py --final` để sinh `cvat/labels_final.json`.

### Lựa chọn thiết kế: đường dẫn export gắn hash và `batch_manifest.json`

Script `scripts/prepare_calibration.py` sao chép đúng tập ảnh thuộc phạm vi sửa vào `work/calib/images/` và in ra đường dẫn đích chính xác có chứa 16 ký tự hash của toàn bộ tổ hợp đầu vào (ví dụ `submission/qc/labels_calibrated_6bc09dcda5c64450.json`). Thiết kế này ngăn chặn lỗi dùng nhầm file COCO export cũ sau khi quyết định hoặc guideline vừa được chỉnh sửa. Khi chạy lại `build_final.py`, script xác thực file COCO đúng tên phiên bản đó, rồi ghi đồng thời `labels_calibrated.json`, `labels_calibrated.csv` và `batch_manifest.json` (chứa mục đích sử dụng, giới hạn, SHA-256 của nhãn cuối, từng file đầu vào và từng ảnh kèm thông tin `data/ATTRIBUTION.csv`).

### Các bước thực hiện Pha 5

1. Chạy `python scripts/build_final.py` một lần để script khởi tạo `submission/qc/calibration_decisions.csv` và `submission/qc/calibration_context.json`.
2. Họp nhóm giải quyết toàn bộ các dòng trong `calibration_candidates.csv`, điền đủ 9 cột vào `submission/qc/calibration_decisions.csv` (trong lượt chạy thử với 45 ca, các quy tắc mới như không bao hàng hóa quá khổ `img_035.jpg` được gắn `R-07` và `pham_vi=lo`, bỏ thân vỏ xe trên nóc `img_024.jpg` gắn `R-08` và `pham_vi=lo`, bán tải nắp thùng cao `img_016.jpg`/`img_037.jpg` và motion blur `img_014.jpg`/`img_015.jpg` gắn `R-09` và `pham_vi=lo`).
3. Lưu `submission/guidelines/guideline_v1.1_calibrated.md` và `submission/guideline_change.json` (ví dụ `{"kind": "semantic", "summary": "..."}`), rồi chạy lệnh chuẩn bị gói sửa cho CVAT:

```bash
python scripts/prepare_calibration.py
```

   Ghi nhận chính xác đường dẫn mà lệnh in ra ở dòng `COCO sau sửa: submission\qc\labels_calibrated_<hash>.json` (ở lần chạy thử với phạm vi `lo`: `40` ảnh tại `work/calib/images/`, đường dẫn đích là `submission\qc\labels_calibrated_6bc09dcda5c64450.json`).

4. Mở CVAT tạo Task calibration mới từ `work/calib/images/`, nạp nhãn nháp từ `work/calib/consensus_flagged.json` (qua **Actions → Upload annotations → COCO 1.0**), sửa lại đúng theo quyết định và tắt toàn bộ cờ `can_review`, rồi xuất **COCO 1.0 (tắt Save images)** lưu đúng vào đường dẫn hash mà bước 3 vừa in ra.

:::image{src="walkthrough_images/09_cvat_calibration_task.png" alt="Giao diện Task calibration trên CVAT hiển thị khung hình img_002.jpg đã sửa đầy đủ 1 truck và 8 car trên 2 tầng" caption="Task calibration trên CVAT (img_002.jpg) sau khi nạp nhãn nháp và hiệu chỉnh đầy đủ theo quyết định v1.1."}
:::

5. Chạy lệnh gộp nhãn cuối để kiểm tra toàn bộ biên ảnh, lớp, thuộc tính và sinh `batch_manifest.json`:

```bash
python scripts/build_final.py
```

   (Khi chạy thử, `build_final.py` tự động bắt được một lỗi bbox vượt biên trên `img_026.jpg` có kích thước `784x1024`; sau khi chỉnh lại và xuất lại từ CVAT, lệnh in `Đã gộp 40 ảnh, 196 annotation. Bước tiếp: python scripts/qc_sample.py.`).

### Checkpoint Pha 5 và bước tiếp theo

Pha 5 hoàn tất khi mọi ca bất thường đều có người chốt, vết sửa, kết quả kiểm lại và mỗi ảnh trong 40 ảnh xuất hiện đúng một lần trong `submission/qc/labels_calibrated.json` và `labels_calibrated.csv` kèm `batch_manifest.json`. Tuy nhiên, tập nhãn này chỉ sẵn sàng bàn giao sau khi được một reviewer độc lập duyệt vòng QC toàn lô ở Pha 6.

## Pha 6 — Duyệt QC toàn lô, lập báo cáo và kiểm tra bàn giao

### Bản chất và cây quyết định Chưa đủ điều kiện → Rework → Release

Khác với cách chỉ lấy mẫu 20 ảnh minh họa, quy trình chuẩn của Pha 6 mặc định **duyệt toàn bộ lô 40/40 ảnh** (`python scripts/qc_sample.py --round 1`). Toàn bộ ảnh overlay có gắn sẵn ID vật (`#174 tuk_tuk`…) được xuất vào `work/review/round-01/`, đi kèm bản chụp nhãn và phiếu kiểm 7 cột `submission/qc/reviews/round-01/qc_review.csv` (`image, object_id, error_type, reviewer, rule_id, region, note`). Lưu ý rằng tùy chọn `--n` (ví dụ `qc_sample.py --round 99 --n 5 --seed 42`) chỉ dùng để demo lấy mẫu ngẫu nhiên và **luôn giữ trạng thái Chưa đủ điều kiện** khi bàn giao.

:::image{src="walkthrough_images/10_qc_review_sample.png" alt="Ảnh img_035.png trong thư mục duyệt QC vẽ sẵn ID đối tượng (#174 tuk_tuk)" caption="Ảnh overlay trong thư mục duyệt QC (img_035.png): hiển thị sẵn ID từng vật (#174 tuk_tuk) để reviewer đối chiếu vào qc_review.csv."}
:::

Khi tổng hợp số liệu bằng `python scripts/qc_report.py --round 1`, quyết định đi theo cây **Chưa đủ điều kiện → Rework → Release**:
- **Chưa đủ điều kiện**: thiếu bằng chứng, guideline/dữ liệu có vấn đề (`--guideline-gap N` hoặc `--data-problem N`), còn box bật `can_review`, hoặc vòng đó chỉ là demo lấy mẫu (`--n`).
- **Rework**: tỉ lệ ảnh có lỗi `> 2%` (với lô 40 ảnh, chỉ cần `1/40 = 2.5%` ảnh lỗi là vượt ngưỡng), hoặc có lỗi lặp lại (`>= 3` lỗi và chiếm `>= 50%` tổng lỗi). Khi Rework, nhóm cập nhật lại quyết định/nhãn từ Pha 5 và mở vòng mới `--round 2` (giữ nguyên toàn bộ thư mục `round-01` để truy vết).
- **Release**: chỉ khi reviewer xác nhận lô duyệt toàn bộ đạt `<= 2%` ảnh lỗi, không lỗi lặp lại và đủ bằng chứng hợp lệ.

### Các bước thực hiện Pha 6

1. Tạo vòng duyệt toàn lô đầu tiên:

```bash
python scripts/qc_sample.py --round 1
```

2. Mở tất cả 40 ảnh trong `work/review/round-01/` (người duyệt nên khác người sửa; nhóm 2 người thì đổi vai và ghi rõ) rồi điền `submission/qc/reviews/round-01/qc_review.csv`:
   - Ảnh sạch: ghi `error_type = khong`, điền `reviewer` là mã 3 chữ số (để trống `object_id`, `rule_id`, `region`).
   - Lỗi trên box hiện có (`thua`, `sai_lop`, `sai_vi_tri_kich_thuoc`, `sai_thuoc_tinh`): điền `object_id` trên ảnh overlay, `reviewer`, `rule_id` và `note`.
   - Lỗi bỏ sót (`bo_sot`): **để trống** `object_id`, ghi mô tả vị trí cụ thể vào `region` kèm `reviewer`, `rule_id`, `note`.
3. Chạy lệnh tính số đo và ghi `qc_result.json` + `qc_report_auto.md`:

```bash
python scripts/qc_report.py --round 1
```

   Trong lần chạy mẫu (duyệt `40/40` ảnh `full`, `186` đối tượng), script xuất kết quả: `RELEASE`, `Ảnh có lỗi trên ảnh đã duyệt: 0/40 = 0.0%`, `Annotation đối tượng hiện có bị lỗi: 0/186 = 0.0%`, `Vật bỏ sót ghi riêng: 0`.

4. Sao chép [docs/QC_REPORT_TEMPLATE.md](docs/QC_REPORT_TEMPLATE.md) thành `submission/qc/QC_REPORT.md`, điền đầy đủ mọi mục `<<...>>` và giữ nguyên tên trường ở **10 dòng gạch đầu dòng bắt buộc** (`Mục đích và giới hạn sử dụng`, `Manifest và checksum nhãn cuối`, `Guideline và taxonomy khi gán / khi bàn giao`, `Lượt hoàn thành / được giao`, `Vòng QC`, `Người review và ngày`, `Đã duyệt / cả lô`, `Quyết định`, `Lý do, người nhận và phạm vi sử dụng`, `Kiểm ngược từ báo cáo tới ảnh, rule và nhãn`).
5. Hoàn thiện `submission/individual_notes/<mã>.md` cho từng thành viên và điền mục "Kết quả tóm tắt" ở [TEAM.md](TEAM.md).
6. Chạy kiểm tra tự động cuối cùng trước khi bàn giao:

```bash
python scripts/check_submission.py --round 1
```

   Kết quả đạt chuẩn phải báo **`Tổng kết: 0 lỗi.`**. Trước khi nộp, hãy nhờ một người ngoài nhóm thử lần ngược một `case_id` từ `QC_REPORT.md` tới ảnh, mã quy tắc và box trong `labels_calibrated.json`.

### Quy cách gói bàn giao và kênh nộp

Nhóm nộp **một link repository riêng tư có quyền cho coach** hoặc **một gói nén qua LMS (`https://aithucchien.vinuni.edu.vn`)** theo kênh coach công bố, đặt tên repo/gói là `K5-L23-DAY07-<TenNhom>-GuidelineQC`. Nếu đóng gói theo cấu trúc thư mục nộp chuẩn của lớp `K5-DAY07-TenNhom/` (`KX-DAYXX-TenNhom/`), giữ `TEAM.md` tại gốc (và chỉ giữ bảng đối chiếu mã thành viên `TEAMMATES.md` ở kênh bảo mật của coach nếu lớp yêu cầu tách danh tính), tuyệt đối **không** đưa thư mục `work/` hay thông tin đăng nhập vào gói nộp.

```text
K5-L23-DAY07-TenNhom-GuidelineQC/   # (hoặc gói nộp KX-DAYXX-TenNhom/)
├── TEAM.md                         # thông tin nhóm dùng mã 3 chữ số + kết quả tóm tắt
├── data/ATTRIBUTION.csv            # giữ nguyên gốc
└── submission/
    ├── taxonomy.json               # khớp v1.0, giữ nguyên mục rules (kèm taxonomy_v1.1.json nếu đổi schema)
    ├── guideline_change.json       # {"kind": "editorial"|"semantic", "summary": "..."}
    ├── guidelines/
    │   ├── individual/             # guideline_<mã>.md (mỗi thành viên 1 file)
    │   ├── guideline_v1.0_agreed.md
    │   └── guideline_v1.1_calibrated.md
    ├── labels/                     # <mã>.json (COCO 1.0 từng thành viên)
    ├── individual_notes/           # <mã>.md (ghi chú cá nhân từng thành viên)
    └── qc/                         # assignment.csv, iaa_summary.*, calibration_*, labels_calibrated.*, batch_manifest.json, reviews/round-*/, QC_REPORT.md
```

:::checklist{title="Checklist bàn giao cuối cùng" tone="success"}
- [ ] Mọi thành viên có `guideline_<mã>.md`, `<mã>.json` và `individual_notes/<mã>.md` dùng đúng mã ba chữ số (không ghi họ tên, MSHV, email vào tên file/Task).
- [ ] `submission/taxonomy.json` khớp guideline và giữ nguyên mục `rules`.
- [ ] Có đủ `calibration_decisions.csv` (9 cột), `calibration_context.json`, `guideline_change.json` và `guideline_v1.1_calibrated.md`.
- [ ] `submission/qc/labels_calibrated.json`, `labels_calibrated.csv`, `batch_manifest.json` và thư mục `submission/qc/reviews/round-*/` đầy đủ theo vòng nộp.
- [ ] `QC_REPORT.md` điền đủ 10 trường bắt buộc, số liệu kèm mẫu số và khớp quyết định của vòng QC.
- [ ] `python scripts/check_submission.py --round <vòng-cuối>` trả về `0 lỗi` và không chứa `work/` hay mật khẩu/token.
:::
