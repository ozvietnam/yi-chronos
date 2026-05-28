# Yêu cầu vẽ đợt 01: Bát Tự + Kỳ Môn

Mục tiêu đợt này: tạo nền mỹ thuật riêng cho hai trang còn khô nhất là **Bát Tự** và **Kỳ Môn Độn Giáp**, đồng thời tránh nhầm với bộ thẻ Tử Vi Bắc Phái và Chiếu Đởm Kinh.

Đọc trước file wiki: `data/school_art_direction/SCHOOL_VISUAL_IDENTITY_WIKI.md`.

## Chuẩn xuất file

- Ảnh gốc: PNG hoặc JPG chất lượng cao, cạnh dài tối thiểu 2200px.
- Bản web: WebP tối ưu, cạnh dài 1200-1600px, dung lượng mục tiêu dưới 450KB/ảnh nền, dưới 120KB/icon.
- Không render chữ Hán/Vietnamese nhỏ trực tiếp trong ảnh. Chữ sẽ overlay bằng giao diện để tránh sai chữ.
- Chừa vùng trống đủ cho text UI: ảnh nền cần có 25-35% vùng tối/thoáng.
- Không dùng lại khung thẻ vàng của Tử Vi.

## Batch A: Bát Tự

### `bat-tu-01-tu-tru-hero`

Loại ảnh: hero background ngang 16:9.

Mô tả: thư phòng cổ, mặt bàn gỗ tối, bốn trụ/seal dựng thẳng tượng trưng Năm-Tháng-Ngày-Giờ. Nhật trụ ở gần giữa sáng hơn ba trụ còn lại. Có giấy xuyến chỉ, mực đen, ấn đỏ, ánh sáng ấm thấp.

Dùng trên UI: nền đầu trang Bát Tự và panel sau khi an số.

Tránh: không vẽ nhân vật, không vẽ thần sao, không để chữ giả chi chít.

### `bat-tu-02-day-master-core`

Loại ảnh: square 1:1 hoặc 4:3.

Mô tả: một ấn triện trung tâm đại diện Nhật Chủ, xung quanh là năm lớp vật liệu ngũ hành. Cảm giác "bản mệnh ở giữa", không phải ngai vàng.

Dùng trên UI: khối Nhật Chủ/Day Master.

Tránh: không biến Nhật Chủ thành hoàng đế hay đạo sĩ.

### `bat-tu-03-five-elements-material-wheel`

Loại ảnh: diagram background 1:1.

Mô tả: vòng ngũ hành bằng vật liệu thật: Mộc là vân gỗ/mầm xanh, Hỏa là chu sa/lửa, Thổ là đất vàng/đá, Kim là đồng/thép, Thủy là nước mực. Vòng sinh-khắc có đường mảnh, đủ sang nhưng không rối.

Dùng trên UI: panel Ngũ Hành phân bố.

Tránh: không dùng icon phẳng kiểu game; không dùng màu quá neon.

### `bat-tu-04-thap-than-ledger`

Loại ảnh: background ngang 4:3.

Mô tả: sổ quan hệ Thập Thần như bảng sớ/ledger cổ, các ô quan hệ quanh Nhật Chủ. Có dấu triện, dây chỉ đỏ, bút lông. Tinh thần là "quan hệ khí với bản thân", không phải 10 vị thần.

Dùng trên UI: Cách Cục, Thập Thần, Dụng/Hỷ/Kỵ thần.

Tránh: không vẽ 10 nhân vật.

### `bat-tu-05-luck-pillars-river`

Loại ảnh: panoramic 21:9.

Mô tả: dòng sông hoặc đường núi chia thành các bậc 10 năm, khí đổi màu theo mùa/ngũ hành. Cảm giác đời người đi qua vận, không phán tốt xấu tuyệt đối.

Dùng trên UI: Đại Vận timeline.

Tránh: không vẽ đường đời kiểu infographic hiện đại.

### `bat-tu-06-ha-lac-two-hexagrams`

Loại ảnh: ngang 16:9.

Mô tả: hai quẻ Tiên thiên và Hậu thiên đặt như hai bản đồ cổ đối diện, giữa là dòng sinh mệnh mảnh. Phong cách sáng hơn Bát Tự một chút, có lưỡng nghi/quẻ nhưng không lấn sang Mai Hoa.

Dùng trên UI: phần Hà Lạc Lý Số.

Tránh: không vẽ quẻ sai nét; quẻ chuẩn sẽ overlay bằng UI nếu cần.

## Batch B: Kỳ Môn Độn Giáp

### `ky-mon-01-nine-palace-command-board`

Loại ảnh: board background vuông 1:1, có thể crop mobile.

Mô tả: bàn lệnh Lạc Thư cửu cung 3x3 trên gỗ sơn đen và đồng cổ. Có vòng la bàn ngoài, dây phương vị, ánh sáng từ trung cung. Các ô để trống đủ để UI đặt text Môn/Tinh/Thần.

Dùng trên UI: nền bàn Kỳ Môn 3x3.

Tránh: không viết chữ cố định vào từng ô; không làm quá sáng khiến text khó đọc.

### `ky-mon-02-eight-gates-icon-set`

Loại ảnh: 8 icon riêng hoặc 1 sprite sheet.

Danh sách: Khai, Hưu, Sinh, Thương, Đỗ, Cảnh, Tử, Kinh.

Mô tả: mỗi Môn là một biểu tượng cửa/cổng/lối vào khác nhau. Cùng hệ nét đồng cổ, đọc rõ ở kích thước 32-48px.

Dùng trên UI: hàng `Môn` trong mỗi cung.

Tránh: không vẽ người đứng trước cổng; không tạo tarot card.

### `ky-mon-03-nine-stars-glyph-set`

Loại ảnh: 9 icon riêng hoặc 1 sprite sheet.

Danh sách: Thiên Bồng, Thiên Nhậm, Thiên Xung, Thiên Phụ, Thiên Cầm, Thiên Tâm, Thiên Trụ, Thiên Anh, Thiên Nhuế.

Mô tả: phù hiệu tinh tú dạng huy chương nhỏ, khác 14 chính tinh Tử Vi. Hình phải là khí/tinh tượng, không phải chân dung sao.

Dùng trên UI: hàng `Tinh` trong mỗi cung.

Tránh: không vẽ thành thần sao nhân vật.

### `ky-mon-04-eight-deities-banner-set`

Loại ảnh: 8 banner/glyph riêng hoặc sprite sheet.

Danh sách: Trị Phù, Đằng Xà, Thái Âm, Lục Hợp, Câu Trần, Chu Tước, Cửu Địa, Cửu Thiên.

Mô tả: mỗi Thần là một cờ lệnh hoặc ấn tượng nghi lễ. Có bóng/tượng trưng nhẹ, nhưng không thành tranh nhân vật lớn.

Dùng trên UI: hàng `Thần` trong mỗi cung và modal cung.

Tránh: không vẽ full-body nhân vật fantasy.

### `ky-mon-05-duty-seal-tri-phu-tri-su`

Loại ảnh: ngang 4:3 hoặc square.

Mô tả: hai ấn lệnh Trị Phù và Trị Sử đặt trên bàn chỉ huy, một ấn thiên, một ấn môn. Có dây đỏ nối tới cung được chọn.

Dùng trên UI: khối Trị Phù - Trị Sử.

Tránh: không vẽ vua/ngai vàng.

### `ky-mon-06-direction-compass-ring`

Loại ảnh: transparent PNG/WebP hoặc background ring.

Mô tả: vòng la bàn 8 phương + trung cung, chất liệu đồng khắc, đường nét rõ. Có thể đặt dưới grid hoặc quanh board.

Dùng trên UI: bọc ngoài bàn 3x3, desktop ưu tiên; mobile có thể ẩn bớt.

Tránh: không thêm chữ nhỏ không đọc được.

## Thứ tự giao ảnh

1. Kỳ Môn: `ky-mon-01`, `ky-mon-02`, `ky-mon-03`, `ky-mon-04`.
2. Bát Tự: `bat-tu-01`, `bat-tu-02`, `bat-tu-03`.
3. Phần bổ sung: `ky-mon-05`, `ky-mon-06`, `bat-tu-04`, `bat-tu-05`, `bat-tu-06`.

## Tiêu chí duyệt

- Nhìn thumbnail vẫn phân biệt được: Bát Tự = trụ/ngũ hành/ấn; Kỳ Môn = bàn lệnh/cửu cung/la bàn.
- Ảnh không bị nhầm với Tử Vi Bắc Phái hoặc Chiếu Đởm Kinh.
- Dễ lắp vào UI: có vùng tối, có khoảng trống, không phụ thuộc chữ trong ảnh.
- Mobile load được: có bản WebP nhẹ và crop vẫn giữ ý chính.

