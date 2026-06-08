# Yêu cầu vẽ đợt 09: Cung Phu Thê Bắc Phái Trung Châu

Mục tiêu: tạo bộ ảnh minh họa cho feature **Cung Phu Thê — Bắc Phái Trung Châu · Vương Đình Chỉ** trong trang Tử Vi. Ảnh dùng để làm đẹp và làm rõ tầng nghĩa khi user bấm luận cung Phu Thê, không phải để phơi thành gallery đại trà.

## Bối cảnh học thuật

Feature hiện nằm tại:

- UI: `client/webapp/src/components/CungPhuTheBacPhaiPanel.vue`
- API: `POST /api/tu-vi/cung-phu-the/bac-phai`
- Nguồn: `Trung Châu Tử Vi Đẩu Số 2`, section 5.3, Vương Đình Chỉ.

Lá số đang test của anh:

- Mệnh Tỵ: Thiên Tướng.
- Mệnh chủ: Vũ Khúc.
- Cung Phu Thê Mão: Tử Vi + Tham Lang.
- Tứ Hóa: Tham Lang Hóa Lộc tại Phu Thê.
- Kết luận trọng tâm theo Trung Châu: **Tử Vi + Tham Lang Hóa Lộc nghiêng về chí tiến thủ, vật chất, quan hệ cùng xây sự nghiệp**, không được vẽ thành đào hoa/dục tình đơn giản.
- Điểm cát: Tả Phụ + Hữu Bật hội chiếu từ Phúc Đức, Hữu Bật Hóa Khoa.
- Điểm cần cân bằng: Thiên Di có Vũ Khúc + Phá Quân + Không/Kiếp, nên hôn nhân có yếu tố đi xa, biến động, sự nghiệp và quan hệ gắn chặt.
- Đối cung Quan Lộc Dậu vô chính diệu, mượn Tử-Tham từ Phu Thê: **sự nghiệp và hôn nhân chia sẻ cùng tinh hệ**.

## Ngôn ngữ mỹ thuật

Đây vẫn thuộc **Tử Vi Bắc Phái**, nhưng là tầng **luận cung/quan hệ**, không phải chân dung 14 chính tinh thuần.

Hướng đúng:

- Cảm giác: sang, sâu, có trí tuệ, có hợp đồng/khế ước, có đồng hành xây dựng sự nghiệp.
- Không khí Trung Châu: cổ thư, bàn luận số, cung điện trầm, giấy khế, ấn triện, trục cung vị.
- Tử Vi: khí chủ, quyền uy mềm, trung tâm ổn định.
- Tham Lang Hóa Lộc: hoa/lộc/tiệc/nguồn lực, nhưng tiết chế, nghiêng về tài nguyên và sức hút xã hội.
- Phu Thê: hai lực đồng hành, không nhất thiết vẽ cảnh tình yêu trực diện.

Tránh tuyệt đối:

- Không vẽ romance sến, cưới hỏi hiện đại, trái tim, đôi nam nữ ôm nhau.
- Không vẽ Tham Lang thành dục tình lộ liễu.
- Không vẽ Tử Vi như hoàng đế một mình chiếm toàn ảnh.
- Không nhồi chữ Hán nhỏ trong ảnh; chữ chuẩn sẽ overlay bằng UI.
- Không dùng phong cách Chiếu Đởm Kinh 18 Phi Tinh.

## Quy chuẩn file

- Ảnh gốc: PNG, cạnh dài tối thiểu 2200px.
- Web: WebP, cạnh dài 1200-1600px, dung lượng mục tiêu dưới 450KB với ảnh nền, dưới 160KB với ảnh nhỏ.
- Tỷ lệ ưu tiên:
  - Hero/UI banner: 16:9 hoặc 21:9.
  - Card minh họa: 4:3 hoặc 3:2.
  - Không dùng thẻ dọc 2:3 cho phần này trừ khi được yêu cầu sau.
- Đặt nguồn tại: `data/tu_vi/oracle_cards/tu_vi_bac_phai/generated_cards/`
- Đặt WebP tại: `data/tu_vi/oracle_cards/tu_vi_bac_phai/web_ready/`

## Asset A — bắt buộc

### `82-phu-the-tu-tham-hoa-loc-trung-chau`

Loại ảnh: hero/banner ngang 16:9.

Vị trí UI dự kiến: đầu kết quả trong `CungPhuTheBacPhaiPanel.vue`, chỉ hiện sau khi user bấm luận và API trả kết quả có Phu Thê = Tử Vi + Tham Lang / Tham Lang Hóa Lộc.

Mô tả ảnh:

Một bàn cổ Trung Châu trong phòng sách sơn mài tối. Ở trung tâm là một khế ước hôn nhân/sự nghiệp đặt trên thiên bàn 12 cung. Hai luồng khí đối xứng gặp nhau tại cung Mão: một luồng tím-vàng đại diện Tử Vi, một luồng lục-đỏ rượu đại diện Tham Lang Hóa Lộc. Trên bàn có ấn triện, chén ngọc, dây đỏ rất mảnh, hoa đào tiết chế, tiền/khế lộc đặt kín đáo. Cảm giác là hai người cùng lập nghiệp, cùng xây nền tài nguyên, có chủ kiến và tiến thủ.

Chi tiết nên có:

- Vòng 12 cung hoặc thiên bàn mờ ở nền.
- Cung Mão/Phu Thê là điểm sáng chính nhưng không cần chữ trong ảnh.
- Một cặp bóng người rất nhỏ hoặc hai chiếc ghế đối diện, không vẽ chân dung tình cảm.
- Ấn triện và giấy khế thể hiện cam kết.
- Ánh sáng tím-vàng + lục bảo + đỏ rượu, nền đen nâu sơn mài.

Ý nghĩa cần truyền:

> Tử-Tham Hóa Lộc ở Phu Thê = quan hệ có sức hút, có chí tiến thủ, có tài nguyên và cùng xây sự nghiệp; không mặc định là đào hoa xấu.

## Asset B — nên vẽ

### `83-phu-the-ta-huu-phuc-duc-hoi-chieu`

Loại ảnh: card ngang 4:3.

Vị trí UI dự kiến: khối `Cross-bind Phúc Đức × Mệnh × Phu Thê` hoặc khu `Tả-Hữu hội chiếu`.

Mô tả ảnh:

Từ một cung Phúc Đức phía sau/tam hợp, hai dải ánh sáng Tả Phụ và Hữu Bật đi vào cung Phu Thê như hai cánh tay nâng đỡ. Có gia phả, đèn tổ, sao Thiên Việt hoặc ấn Khoa mờ. Cảm giác: quan hệ được nâng bởi phúc đức, người bạn đời có học/biết hỗ trợ, hôn nhân không đứng một mình mà có nền phúc.

Tránh:

- Không vẽ ông bà tổ tiên thành nhân vật quá cụ thể.
- Không biến thành ảnh Phúc Đức chung chung; phải thấy luồng chiếu vào Phu Thê.

## Asset C — nên vẽ

### `84-phu-the-quan-loc-doi-cung`

Loại ảnh: card ngang 4:3 hoặc 3:2.

Vị trí UI dự kiến: khối `Đối cung Quan Lộc` hoặc `Toàn cảnh Hôn Nhân`.

Mô tả ảnh:

Một trục đối xứng trên thiên bàn: bên trái là Cung Phu Thê, bên phải là Quan Lộc vô chính diệu đang mượn ánh Tử-Tham. Ở giữa là một con đường/cầu nối giữa hôn nhân và sự nghiệp. Nửa Phu Thê có khế ước, nửa Quan Lộc có công đường/bàn làm việc/ấn sự nghiệp nhưng trống chính tinh, nhận ánh sáng từ Phu Thê.

Ý nghĩa:

> Sự nghiệp và hôn nhân chia sẻ cùng tinh hệ. Người bạn đời không chỉ là tình cảm mà còn là lực ảnh hưởng đường sự nghiệp.

Tránh:

- Không vẽ thành cảnh công sở hiện đại.
- Không vẽ Quan Lộc thành tướng quân chiến trận; đây là trục đối cung luận số.

## Asset D — tùy chọn sau

### `85-phu-the-vu-khuc-menh-chu-can-bang`

Loại ảnh: card ngang 4:3.

Vị trí UI dự kiến: khối `Mệnh chủ Vũ Khúc ảnh hưởng quan hệ`.

Mô tả ảnh:

Một ấn kim loại Vũ Khúc ở phía Mệnh, cứng và sáng lạnh, được làm mềm bởi lụa/ánh đèn từ phía Phu Thê. Trục ý nghĩa: người nam thiên hành động, tài chính, kỷ luật; quan hệ cần mềm hóa bằng lắng nghe và chia sẻ quyền quyết định.

Tránh:

- Không biến thành ảnh Tài Bạch.
- Không vẽ xung đột vợ chồng.

## Thứ tự giao ảnh

1. `82-phu-the-tu-tham-hoa-loc-trung-chau` — bắt buộc trước.
2. `83-phu-the-ta-huu-phuc-duc-hoi-chieu`.
3. `84-phu-the-quan-loc-doi-cung`.
4. `85-phu-the-vu-khuc-menh-chu-can-bang` nếu còn thời gian.

## Cách duyệt ảnh

Ảnh đạt khi:

- Nhìn vào biết ngay là Phu Thê Trung Châu/Bắc Phái, không phải 14 chính tinh thuần.
- Không gây hiểu nhầm "Tử-Tham = đào hoa xấu".
- Có khí chất khế ước, đồng hành, tài nguyên, sự nghiệp và phúc đức.
- Có vùng tối/thoáng để UI overlay title, chip sao, verdict.
- Mobile crop vẫn giữ được thiên bàn/khế ước/trục Phu Thê.

Ảnh không đạt khi:

- Quá tình cảm, quá hôn lễ, quá hiện đại.
- Tham Lang bị vẽ dung tục.
- Tử Vi bị vẽ thành vua ngồi một mình.
- Không có chỗ để gắn vào giao diện.

