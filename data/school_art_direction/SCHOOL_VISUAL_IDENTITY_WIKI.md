# Wiki mỹ thuật đa trường phái

Mục tiêu: mỗi trường phái trong Yi phải có ngôn ngữ hình ảnh riêng, đúng logic học thuật và đúng vị trí hiển thị trên website. Không gom mọi thứ thành cùng kiểu thẻ bài Tử Vi.

## Nguyên tắc chung

- Tử Vi Bắc Phái: dùng ngôn ngữ **thẻ sao / chân dung / cung vị đời người**. Đây là hệ nhân tượng rõ nhất, phù hợp oracle card dọc 2:3.
- Chiếu Đởm Kinh: dùng ngôn ngữ **phi tinh / phù tượng / đồng hồ địa chi**. Có thể dùng thẻ dọc, nhưng thẻ phải chìm vào thiên bàn, khác 14 chính tinh.
- Bát Tự: dùng ngôn ngữ **trụ, can chi, vật liệu ngũ hành, nhật chủ, dòng đại vận**. Không ưu tiên chân dung thần sao.
- Kỳ Môn Độn Giáp: dùng ngôn ngữ **bàn lệnh chiến lược, Lạc Thư cửu cung, môn-tinh-thần, la bàn phương vị**. Không biến thành bộ tarot nhân vật.
- Mai Hoa: nên dùng **ảnh điềm tượng khoảnh khắc**: hoa, chim, mưa, tiếng động, vật rơi, phương vị ngoài đời. Hình phải giống quan sát hiện trường.
- Lục Hào: nên dùng **hào tuyến, mai rùa, đồng tiền, sổ phán đoán**. Trọng tâm là 6 dòng biến động, không phải nhân vật.
- Liên Hoa: nên dùng **mandala sen, tầng tâm thức, vòng sáng, thủy diện**. Hình mềm và thiền hơn các hệ thuật số.

## Kiểm tra UX hiện tại

### Bát Tự & Hà Lạc

File giao diện: `client/webapp/src/components/BatTuPanel.vue`.

Hiện trạng:
- Trang đang mạnh về dữ liệu: form sinh thần, Tứ Trụ, Nhật Chủ, Ngũ Hành, Cách Cục, Dụng/Hỷ/Kỵ thần, Trường Sinh, Thần Sát, Đại Vận, Hà Lạc.
- Hình ảnh hiện có chủ yếu là `HexagramImage` cho Hà Lạc. Bát Tự chưa có hệ ảnh riêng.
- Các khối quan trọng đều đang là card text/number. Mobile có thể đọc được, nhưng cảm giác mỹ thuật chưa tách khỏi dashboard.

Kết luận:
- Bát Tự cần vẽ, nhưng không nên vẽ theo kiểu thẻ sao Tử Vi.
- Bộ ảnh Bát Tự nên là **bộ nền cấu trúc** và **biểu tượng học vật liệu**, dùng để làm rõ 4 tầng: Tứ Trụ, Nhật Chủ, Ngũ Hành, Đại Vận.

Ngôn ngữ mỹ thuật đề xuất:
- Nền: thư phòng cổ, bàn gỗ tối, giấy xuyến chỉ, ấn triện đỏ, mực đen, kim loại đã xước.
- Tứ Trụ: 4 cột/seal đứng, mỗi cột gồm thiên can trên, địa chi dưới.
- Nhật Chủ: một ấn chính giữa, sáng nhất, không phải chân dung.
- Ngũ Hành: 5 chất liệu thật: gỗ sống, lửa chu sa, đất hoàng thổ, kim loại rèn, nước mực.
- Đại Vận: sông/thềm ruộng/đường núi 10 năm một bậc, thể hiện lưu biến chứ không phán định cát hung.
- Hà Lạc: hai quẻ như hai bản đồ đời người, Tiên thiên và Hậu thiên, tách khỏi Bát Tự bằng hình lưỡng nghi/quẻ.

Vị trí dùng trên UI:
- Hero nền mỏng phía sau tiêu đề Bát Tự.
- Sau khi an số: ảnh/diagram lớn cho Tứ Trụ + Nhật Chủ.
- Panel Ngũ Hành: dùng texture/ngũ hành thay màu phẳng.
- Đại Vận: dùng timeline ngang có nền cảnh dòng thời gian.
- Hà Lạc: dùng ảnh song quẻ, không trộn vào Tứ Trụ.

Không được làm:
- Không vẽ các sao Bát Tự như thần tiên hoặc nhân vật giống 14 chính tinh.
- Không dùng cùng khung vàng oracle của Tử Vi.
- Không để ảnh quá nhiều chi tiết chữ Hán do model sinh chữ dễ sai; chữ chuẩn nên overlay bằng UI.

### Kỳ Môn Độn Giáp

File giao diện: `client/webapp/src/components/KyMonPanel.vue`.

Hiện trạng:
- Trang đã có logic đúng: Đàm Liên, an cục, task analysis, hướng tốt/tránh, cách cục, Trị Phù-Trị Sử, bàn 3x3 Lạc Thư.
- Phần 3x3 hiện chủ yếu là ô text. Đúng kỹ thuật nhưng chưa có cảm giác "đế vương chi học" hay bàn lệnh chiến lược.
- Kỳ Môn có hệ cấu trúc riêng: 9 cung x 8 môn x 9 tinh x 8 thần. Cần modular art, không cần thẻ bài dọc như Tử Vi.

Kết luận:
- Kỳ Môn rất cần vẽ, ưu tiên hơn Bát Tự nếu muốn nâng cảm giác chuyên nghiệp ngay, vì nó đã có bàn 3x3 để lắp ảnh.
- Bộ ảnh nên là **bàn chiến lược và glyph module**, không phải gallery.

Ngôn ngữ mỹ thuật đề xuất:
- Nền: bàn chỉ huy gỗ sơn đen, đồng cổ, la bàn, dây phương vị, bản đồ quân cơ.
- 9 cung: ô vuông/phiến lệnh theo Lạc Thư, có viền phương hướng riêng.
- 8 môn: biểu tượng cửa/lối vào, mỗi môn một hình cổng khác nhau.
- 9 tinh: phù hiệu tinh tú, không vẽ thành nhân vật.
- 8 thần: cờ lệnh hoặc bóng tượng nghi lễ, hạn chế chân dung.
- Trị Phù/Trị Sử: ấn lệnh trung tâm, nổi bật như trục chỉ huy.

Vị trí dùng trên UI:
- Header Kỳ Môn: nền panoramic "bàn lệnh cửu cung".
- Sau khi an cục: dùng ảnh nền board 3x3 dưới các ô text.
- Mỗi ô cung: có icon nhỏ cho Môn/Tinh/Thần, không dùng ảnh dọc lớn.
- Modal cung: có ảnh nền cung theo phương vị, giúp user hiểu vì sao cung đó mang khí đó.

Không được làm:
- Không vẽ "Khai Môn", "Sinh Môn" thành người cầm cửa như tarot.
- Không dùng phong cách cung điện Tử Vi.
- Không lạm dụng vàng tím huyền ảo; Kỳ Môn phải có cảm giác chiến lược, phương vị, lệnh bàn.

### Mai Hoa Dịch Số

File giao diện: `client/webapp/src/components/wiki/MaiHoaCastPanel.vue` và `client/webapp/src/components/MaiHoaClock3D.vue`.

Hiện trạng:
- Trang đã có đồng hồ Mai Hoa 3D và form Niên-Nguyệt-Nhật-Thời.
- Có tầng "Ngoạn Pháp", ngoại ứng, tư thế thân thể, 8 quẻ mnemonic và focus mode khi gieo.
- Mỹ thuật hiện đã có tính động hơn Bát Tự/Kỳ Môn, nên chưa cần vẽ đại trà.

Kết luận:
- Mai Hoa cần ảnh theo kiểu **điềm tượng đang xảy ra**, không phải sao, không phải bàn chiến lược.
- Khi đặt vẽ sau này, nên làm bộ "omen scenes": hoa mai rung, chim đậu, tiếng chuông, vật rơi, mưa gõ mái, bóng người ngoài cửa.

Vị trí dùng trên UI:
- Focus Mode: nền dịu theo khoảnh khắc đang gieo.
- Ngoại ứng: icon/thumbnail cho nhóm omen.
- 8 quẻ mnemonic: có thể nâng từ ký hiệu text thành icon quẻ rất nhỏ, cùng nét mực.

Không được làm:
- Không vẽ chart kỹ thuật kiểu Bát Tự.
- Không vẽ thẻ nhân vật như Tử Vi.
- Không làm quá thiền/mandala vì đó là vùng của Liên Hoa.

### Lục Hào

File giao diện: `client/webapp/src/components/MaiHoaClock3D.vue` và `client/webapp/src/components/LucHaoResultPage.vue`.

Hiện trạng:
- Lục Hào dùng cùng điểm gieo ở Mai Hoa Clock 3D, có vùng giữ tay/chuột, đo thời lượng, nhịp cảm xúc, năng lượng.
- Trang kết quả riêng có quẻ chủ, quẻ biến, hào động, Thế/Ứng, phân tích hào, Phục Thần/Nạp Giáp.
- Hình ảnh hiện vẫn thiên về text/result card, chưa có ngôn ngữ riêng cho 6 hào.

Kết luận:
- Lục Hào nên vẽ theo **nghi thức gieo và hồ sơ sáu hào**.
- Ưu tiên sau Kỳ Môn/Bát Tự: một bộ nền gieo quẻ và icon sáu hào sẽ giúp trang kết quả bớt khô.

Ngôn ngữ mỹ thuật đề xuất:
- Đồng xu cổ, tay gieo, bàn gỗ, sổ hào, vạch âm dương, mực phê.
- 6 hào là sáu thanh ngang có chất liệu riêng, chuyển động từ dưới lên.
- Thế/Ứng là hai mốc đối thoại, không vẽ thành hai người fantasy.

Không được làm:
- Không nhập nhằng với Mai Hoa 3D clock; Lục Hào là câu hỏi cụ thể và sáu hào nghiệm sự.
- Không dùng ảnh chiến lược/la bàn của Kỳ Môn.

### Liên Hoa Độn Pháp

File giao diện: `client/webapp/src/components/LienHoaPanel.vue` và `client/webapp/src/components/LienHoaOnboardingDrawer.vue`.

Hiện trạng:
- Trang dùng hai số tâm ý tay Phải/tay Trái, sinh chuỗi 5/9/13 không thời sự.
- Có onboarding giải thích riêng, summary quẻ tiên đề, chủ sự, domain cards.
- Hình ảnh đã có `HexagramImage`, nhưng chưa có bản sắc Liên Hoa riêng.

Kết luận:
- Liên Hoa nên đi theo **mandala sen + chuỗi không thời sự**, khác Mai Hoa và Lục Hào.
- Đây có thể là trường phái mới về mặt mỹ thuật: mềm, tâm ý, tuần hoàn, ít chất chiến thuật.

Ngôn ngữ mỹ thuật đề xuất:
- Sen nhìn từ trên, vòng nước, hạt sáng, hai dòng số nhập vào một quẻ tiên đề.
- 5/9/13 không thời sự là các cánh/vòng đồng tâm, không phải timeline Bát Tự.
- Màu nên dịu: ngọc, lam nước, vàng nhạt, hồng sen tiết chế.

Không được làm:
- Không dùng kiểu chiến lược Kỳ Môn.
- Không dùng cảnh omen đời thường của Mai Hoa.
- Không dùng bảng sáu hào Lục Hào.

## Bảng phân biệt nhanh cho thợ vẽ

| Trường phái | Cốt lõi | Hình ảnh đúng | Hình ảnh sai |
| --- | --- | --- | --- |
| Tử Vi Bắc Phái | Sao và cung đời người | chân dung sao, cung vị, thẻ 2:3 | bảng kỹ thuật khô |
| Chiếu Đởm Kinh | 18 phi tinh + địa chi clock | phù tượng, thẻ chìm nền, thiên bàn | sao chính tinh Bắc Phái |
| Bát Tự | 4 trụ + Nhật Chủ + Ngũ Hành | cột can chi, ấn triện, vật liệu | thần sao/chân dung tarot |
| Kỳ Môn | 9 cung + môn/tinh/thần | bàn lệnh, la bàn, glyph module | oracle card nhân vật |
| Mai Hoa | điềm tượng tức thời | cảnh vật ngoài đời, omen moment | chart nặng chữ |
| Lục Hào | 6 hào biến | hào tuyến, đồng tiền, sách phán | nhân vật thần thoại |
| Liên Hoa | tầng tâm thức | sen, mandala, thủy diện | chiến thuật/cung điện |

## Thứ tự nâng cấp đề xuất

1. Kỳ Môn: vẽ board 3x3 + icon Môn/Tinh/Thần vì UI đã có nơi lắp rõ nhất.
2. Bát Tự: vẽ hero Tứ Trụ + Ngũ Hành + Đại Vận để trang bớt khô.
3. Mai Hoa/Lục Hào/Liên Hoa: sau khi kiểm tra kỹ từng tab, lập brief riêng để không lẫn nhau.
4. Tử Vi: tiếp tục hoàn thiện ảnh cung vị còn thiếu, nhưng không để Tử Vi lấn át các phái khác.
