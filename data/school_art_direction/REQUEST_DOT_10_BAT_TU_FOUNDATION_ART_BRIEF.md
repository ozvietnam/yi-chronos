# Yêu cầu vẽ Dot 10: Bát Tự Foundation

Mục tiêu: tạo bộ ảnh nền và ảnh minh họa riêng cho trang **Bát Tự & Hà Lạc Lý Số**. Bộ này thay phần Bát Tự còn treo từ Dot 01; Dot 01 đã nhận phần Kỳ Môn, còn Bát Tự cần một brief riêng để không lẫn phong cách.

Đọc trước:

- `data/school_art_direction/SCHOOL_VISUAL_IDENTITY_WIKI.md`
- UI hiện tại: `client/webapp/src/components/BatTuPanel.vue`

## Tinh thần mỹ thuật

Bát Tự trong Yi không phải thẻ sao, không phải oracle nhân vật. Đây là hệ **Tứ Trụ - Nhật Chủ - Ngũ Hành - Thập Thần - Đại Vận - Hà Lạc**.

Hình ảnh đúng:

- Trụ/seal/cột can chi, ấn triện, giấy xuyến chỉ, bàn gỗ tối, mực đen.
- Vật liệu ngũ hành thật: gỗ, lửa/chu sa, đất, kim loại, nước/mực.
- Dòng vận động theo mùa, theo đại vận 10 năm.
- Cảm giác thư phòng mệnh lý cổ, sang, trầm, có cấu trúc.

Hình ảnh sai:

- Không vẽ chân dung thần sao kiểu Tử Vi.
- Không dùng khung thẻ vàng/dọc 2:3 của Tử Vi Bắc Phái.
- Không dùng bàn lệnh chiến lược/la bàn cửu cung kiểu Kỳ Môn.
- Không render nhiều chữ Hán/Vietnamese nhỏ trong ảnh; chữ chuẩn sẽ overlay bằng UI.
- Không vẽ giàu/nghèo/tốt/xấu tuyệt đối. Bát Tự ở Yi đọc theo hướng **tri mệnh, cân bằng, bổ khí**.

## Chuẩn xuất file

- Ảnh gốc: PNG hoặc JPG, cạnh dài tối thiểu 2200px.
- Web-ready: WebP, cạnh dài 1200-1600px.
- Dung lượng web mục tiêu:
  - Hero/banner: dưới 450KB.
  - Card minh họa: dưới 300KB.
  - Texture/icon nhỏ nếu có: dưới 120KB.
- Chừa 25-35% vùng tối/thoáng để UI overlay tiêu đề, chip, số liệu.
- Mobile crop phải giữ được ý chính ở vùng trung tâm.
- File nguồn đặt tại: `data/school_art_direction/bat_tu_dot10_foundation/source/`
- File web đặt tại: `data/school_art_direction/bat_tu_dot10_foundation/web_ready/`
- Prompt đặt tại: `data/school_art_direction/bat_tu_dot10_foundation/prompts/`

## Asset 01 - bắt buộc

### `bat-tu-01-four-pillars-command-table`

Loại ảnh: hero/banner ngang 16:9.

Vị trí UI dự kiến: đầu trang Bát Tự hoặc ngay sau khi user bấm **Luận Bát Tự + Hà Lạc**.

Mô tả:

Một bàn thư phòng cổ nhìn hơi từ trên xuống. Trên bàn có bốn trụ/seal dựng hoặc bốn phiến lệnh đặt song song, tượng trưng **Năm - Tháng - Ngày - Giờ**. Nhật trụ ở gần trung tâm, sáng hơn ba trụ còn lại nhưng không thành ngai vua. Nền có giấy xuyến chỉ, mực đen, ấn đỏ, thước thiên can địa chi mờ, vài đường chỉ nối bốn trụ thành một mệnh cục.

Ý nghĩa cần truyền:

> Bát Tự là bốn trụ khí tại thời điểm sinh. Nhật Chủ là điểm quy chiếu để đọc toàn bộ quan hệ khí.

Tránh:

- Không vẽ người.
- Không vẽ sao/tinh tú Tử Vi.
- Không viết sẵn tên can chi trong ảnh.

## Asset 02 - bắt buộc

### `bat-tu-02-day-master-forge`

Loại ảnh: card ngang 4:3 hoặc square 1:1.

Vị trí UI dự kiến: khối **Nhật chủ (Day Master)**.

Mô tả:

Một ấn triện/lõi kim loại ở trung tâm đại diện Nhật Chủ. Xung quanh là năm lớp vật liệu ngũ hành bao quanh như lò tôi luyện: Mộc là vân gỗ/mầm sống, Hỏa là chu sa/lửa thấp, Thổ là đá/hoàng thổ, Kim là đồng/thép đã rèn, Thủy là nước mực. Ánh sáng tập trung vào lõi giữa, nhưng cảm giác là “được môi trường tháng mùa tôi luyện”, không phải biểu tượng quyền lực.

Ý nghĩa cần truyền:

> Nhật Chủ không đứng một mình; sức mạnh/yếu của nó phụ thuộc mùa sinh, ngũ hành xung quanh và quan hệ Thập Thần.

Tránh:

- Không vẽ Nhật Chủ thành hoàng đế, đạo sĩ, thần linh.
- Không dùng hiệu ứng fantasy quá mạnh.

## Asset 03 - bắt buộc

### `bat-tu-03-five-elements-balance`

Loại ảnh: diagram background 1:1 hoặc ngang 4:3.

Vị trí UI dự kiến: khối **Ngũ Hành cân bằng**.

Mô tả:

Một bàn cân khí hoặc vòng vật liệu ngũ hành, không phải icon phẳng. Năm hành là năm chất liệu thật đặt quanh một mặt bàn: gỗ non, chu sa/lửa, đất vàng, kim loại, nước mực. Đường sinh-khắc là nét mảnh khắc chìm hoặc dây chỉ rất tinh, đủ để gợi cấu trúc nhưng không rối. Vùng giữa để trống cho UI đặt biểu đồ/số liệu.

Ý nghĩa cần truyền:

> Ngũ Hành trong Bát Tự là tỷ trọng khí và khả năng cân bằng, không phải màu trang trí.

Tránh:

- Không dùng màu neon.
- Không làm thành biểu tượng game.
- Không nhồi vòng mũi tên quá rõ khiến UI bị rối.

## Asset 04 - ưu tiên cao

### `bat-tu-04-ten-gods-court`

Loại ảnh: card ngang 4:3.

Vị trí UI dự kiến: khối **Thập Thần / Cách Cục / Dụng-Hỷ-Kỵ thần**.

Mô tả:

Một sổ quan hệ khí đặt quanh Nhật Chủ như một bàn nghị sự. Có mười ô/ấn nhỏ xung quanh trung tâm, tượng trưng Thập Thần, nhưng không cần chữ trong ảnh. Một vài ô sáng, một vài ô chìm, cho cảm giác mỗi Thập Thần là một kiểu quan hệ với bản thân: đồng loại, sinh xuất, tài, quan sát, ấn.

Ý nghĩa cần truyền:

> Thập Thần không phải 10 vị thần; đó là 10 quan hệ khí xoay quanh Nhật Chủ.

Tránh:

- Không vẽ 10 nhân vật.
- Không biến thành triều đình Tử Vi.
- Không viết tên Thập Thần trong ảnh.

## Asset 05 - ưu tiên cao

### `bat-tu-05-useful-god-remedy`

Loại ảnh: card ngang 4:3 hoặc 3:2.

Vị trí UI dự kiến: khối **Dụng Thần / Bổ khí / Lưu ý paradigm**.

Mô tả:

Một mệnh cục hơi lệch cân bằng, được điều chỉnh bằng một dòng khí/vật liệu bổ sung. Ví dụ: bàn ngũ hành có một vùng khô/nặng, một nét nước mực hoặc ánh mộc/hỏa được thêm vào đúng chỗ. Có cảm giác tinh chỉnh, cân bằng, chữa lệch, không phải “đổi số phận”.

Ý nghĩa cần truyền:

> Dụng Thần là điểm điều khí để cân bằng mệnh cục. Yi đọc Bát Tự theo hướng tri mệnh và bổ khí, không phán định tuyệt đối.

Tránh:

- Không vẽ phép thuật chữa bệnh.
- Không vẽ trước/sau giàu nghèo.
- Không tạo cảm giác mê tín cứu rỗi.

## Asset 06 - ưu tiên vừa

### `bat-tu-06-da-van-river`

Loại ảnh: panoramic 21:9 hoặc 16:9.

Vị trí UI dự kiến: khối **Đại Vận timeline**.

Mô tả:

Một dòng sông hoặc đường núi chia thành nhiều đoạn 10 năm. Mỗi đoạn đổi mùa/khí nhẹ theo ngũ hành. Có các mốc đá hoặc thẻ tre dọc đường, nhưng không cần chữ. Dòng chảy đi từ trái sang phải, thể hiện vận trình là sự lưu biến dài hạn.

Ý nghĩa cần truyền:

> Đại Vận là dòng khí 10 năm một đoạn. Nó cho bối cảnh vận động, không tự nó kết luận tốt/xấu.

Tránh:

- Không làm infographic hiện đại.
- Không dùng icon tuổi tác/đồng hồ kiểu app sức khỏe.
- Không vẽ đường đời lên/xuống quá trực diện.

## Asset 07 - tùy chọn nếu còn thời gian

### `bat-tu-07-ha-lac-two-hexagrams`

Loại ảnh: banner ngang 16:9.

Vị trí UI dự kiến: phần **Hà Lạc Lý Số** trong trang Bát Tự.

Mô tả:

Hai quẻ Tiên Thiên và Hậu Thiên đặt như hai bản đồ cổ đối diện. Giữa hai quẻ là một dòng sinh mệnh mảnh, có các nấc hào vận mờ. Phong cách sáng hơn Bát Tự một chút, nhưng vẫn cùng thư phòng cổ. Nếu có quẻ, chỉ nên gợi bằng vạch âm dương lớn, không render quẻ sai nét; UI sẽ overlay quẻ thật.

Ý nghĩa cần truyền:

> Hà Lạc là tầng quẻ đời người đi cùng Bát Tự, nhưng không lẫn với Mai Hoa gieo quẻ khoảnh khắc.

Tránh:

- Không vẽ quẻ chi chít, dễ sai.
- Không biến thành Mai Hoa ngoại ứng.

## Thứ tự giao ảnh

1. `bat-tu-01-four-pillars-command-table`
2. `bat-tu-02-day-master-forge`
3. `bat-tu-03-five-elements-balance`
4. `bat-tu-04-ten-gods-court`
5. `bat-tu-05-useful-god-remedy`
6. `bat-tu-06-da-van-river`
7. `bat-tu-07-ha-lac-two-hexagrams` nếu còn thời gian

## Cách duyệt ảnh

Ảnh đạt khi:

- Nhìn thumbnail biết ngay là Bát Tự: trụ, can chi, vật liệu ngũ hành, mệnh cục.
- Không nhầm với Tử Vi, Chiếu Đởm Kinh, Kỳ Môn, Mai Hoa.
- Có vùng trống để UI overlay dữ liệu.
- Mobile crop vẫn giữ được Tứ Trụ/Nhật Chủ/Ngũ Hành ở trung tâm.
- Cảm giác sang, trầm, có học thuật, không mê tín rẻ tiền.

Ảnh không đạt khi:

- Có quá nhiều chữ giả.
- Giống tarot/oracle nhân vật.
- Giống bàn lệnh Kỳ Môn.
- Giống thẻ sao Tử Vi.
- Quá sáng/đầy chi tiết khiến text UI khó đọc.

