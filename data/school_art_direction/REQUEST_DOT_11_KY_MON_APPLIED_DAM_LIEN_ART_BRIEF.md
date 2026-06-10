# Yêu cầu vẽ Dot 11: Kỳ Môn ứng dụng Đàm Liên

Mục tiêu: bổ sung bộ ảnh minh họa tầng **luận đoán ứng dụng** cho trang **Kỳ Môn Độn Giáp**. Dot 01 đã có nền bàn 9 cung + icon 8 Môn + 9 Tinh + 8 Thần. Dot 11 không vẽ lại các icon đó; chỉ vẽ ảnh lớn/card để giúp user hiểu các khối luận theo Đàm Liên.

Đọc trước:

- `data/school_art_direction/SCHOOL_VISUAL_IDENTITY_WIKI.md`
- `data/school_art_direction/bat_tu_ky_mon_dot01/README.md`
- UI hiện tại: `client/webapp/src/components/KyMonPanel.vue`
- Journal học thuật: `docs/design/ky-mon-don-giap-restoration-journal.md`

## Tinh thần học thuật

Theo Đàm Liên, Kỳ Môn không phải một "bảng cát hung chung". Kỳ Môn là bản đồ **thời-không + việc hỏi + cách cục + phương vị**. Một bàn có thể tốt cho việc này nhưng không hợp việc khác.

Dot 11 cần làm rõ 5 tầng:

1. **Task-oriented reading**: user hỏi việc gì thì cách đọc thay đổi.
2. **Cách cục cát/hung**: cách cục là mạch luận chính, không chỉ nhìn từng Môn/Tinh/Thần rời rạc.
3. **Phương vị tương đối**: hướng trong Kỳ Môn phụ thuộc trung tâm người hỏi/ngữ cảnh.
4. **Thiên - Địa - Nhân**: nhiều lớp bàn chồng lên nhau.
5. **Trị Phù - Trị Sử**: trục chỉ huy của bàn.
6. **Đàm Liên personal reading**: đọc lá số sinh theo Kỳ Môn, không phải chỉ gieo việc tức thời.

## Ngôn ngữ mỹ thuật

Hình ảnh đúng:

- Bàn lệnh chiến lược, bản đồ quân cơ, đồng cổ, gỗ sơn đen, dây phương vị, trục chỉ huy.
- Cửu cung/Lạc Thư là cấu trúc nền, nhưng không cần vẽ lại icon 8 Môn/9 Tinh/8 Thần.
- Cảm giác quyết sách: quan sát thời-không, chọn hướng, chọn việc, nhận diện cách cục.
- Màu: đen sơn, đồng cổ, xanh sâu, đỏ son tiết chế, vàng lệnh điểm nhấn.

Hình ảnh sai:

- Không vẽ thành tarot/oracle nhân vật.
- Không vẽ thần tướng full-body fantasy.
- Không dùng cung điện Tử Vi hoặc chân dung sao.
- Không làm infographic hiện đại.
- Không render chữ Hán/Vietnamese nhỏ; UI sẽ overlay chữ chuẩn.

## Chuẩn xuất file

- Ảnh gốc: PNG hoặc JPG, cạnh dài tối thiểu 2200px.
- Web-ready: WebP, cạnh dài 1200-1600px.
- Hero/banner: dưới 450KB.
- Card minh họa: dưới 300KB.
- Chừa 25-35% vùng tối/thoáng cho UI overlay.
- Mobile crop phải giữ ý chính ở trung tâm.
- File nguồn đặt tại: `data/school_art_direction/ky_mon_dot11_applied_dam_lien/source/`
- File web đặt tại: `data/school_art_direction/ky_mon_dot11_applied_dam_lien/web_ready/`
- Prompt đặt tại: `data/school_art_direction/ky_mon_dot11_applied_dam_lien/prompts/`

## Asset 01 - bắt buộc

### `ky-mon-05-task-decision-gate`

Loại ảnh: hero/card ngang 16:9.

Vị trí UI dự kiến: khối **Task-oriented analysis / Hero insight card** sau khi user an cục và chọn loại việc.

Mô tả:

Một bàn lệnh Kỳ Môn đặt giữa phòng chỉ huy tối. Trên bàn có nhiều thẻ việc khác nhau đặt quanh cửu cung: xuất hành, gặp người, ký kết, khai trương, học tập, trị bệnh, kiện tụng. Từ trung cung tỏa ra một đường lệnh sáng tới đúng một thẻ việc được chọn. Cảm giác: cùng một bàn nhưng cách đọc đổi theo nhiệm vụ.

Ý nghĩa cần truyền:

> Kỳ Môn đọc theo việc hỏi. Không có một kết luận cát/hung chung cho mọi việc.

Tránh:

- Không vẽ người ra quyết định.
- Không biến thành dashboard hiện đại.
- Không viết tên task trong ảnh.

## Asset 02 - bắt buộc

### `ky-mon-06-cach-cuc-detection`

Loại ảnh: card ngang 4:3 hoặc 3:2.

Vị trí UI dự kiến: khối **Cách cục phát hiện**.

Mô tả:

Trên bàn cửu cung, một vài đường sáng nối Thiên bàn - Địa bàn - Môn - Tinh tạo thành hình cách cục. Có hai vùng đối lập: một cách cục cát sáng bằng vàng/lam, một cách cục hung tối bằng đỏ sẫm/đen. Nhưng không phán tuyệt đối; cảm giác là engine đang nhận diện pattern cổ điển.

Ý nghĩa cần truyền:

> Cách cục là mạch luận chính của Kỳ Môn Độn Giáp. User cần thấy pattern được phát hiện, không chỉ xem từng ô rời rạc.

Tránh:

- Không vẽ biểu đồ dây quá rối.
- Không tạo cảm giác "đỏ = xấu tuyệt đối"; chỉ là cảnh báo theo việc.
- Không nhồi chữ tên cách cục.

## Asset 03 - bắt buộc

### `ky-mon-07-relative-direction-center`

Loại ảnh: card ngang 4:3.

Vị trí UI dự kiến: phần giải thích **phương vị Kỳ Môn là tương đối, tùy trung tâm**.

Mô tả:

Một la bàn Kỳ Môn đặt trên bản đồ mờ. Ở trung tâm có một điểm sáng "người hỏi/trung tâm". Tám phương mở ra như các tia đường; khi trung tâm dịch chuyển, các tia phương vị được vẽ lại bằng lớp mờ thứ hai. Cảm giác: hướng không phải tọa độ cứng trên trời, mà là quan hệ giữa người hỏi và không gian thực.

Ý nghĩa cần truyền:

> Phương vị Kỳ Môn là tương đối theo trung tâm và bối cảnh, không phải hướng tuyệt đối bất biến.

Tránh:

- Không dùng bản đồ Google/hiện đại.
- Không viết Đông Tây Nam Bắc trong ảnh.
- Không làm giống la bàn phong thủy thông thường quá mức.

## Asset 04 - ưu tiên cao

### `ky-mon-08-heaven-earth-human-layers`

Loại ảnh: card ngang 4:3 hoặc square 1:1.

Vị trí UI dự kiến: phần **bàn 3x3 chi tiết / 9 cung + 4 tầng**.

Mô tả:

Ba lớp trong suốt chồng lên nhau phía trên một bàn cửu cung: Thiên bàn như lớp trời/tinh tượng, Địa bàn như nền cung/đất, Nhân sự như lớp Môn/Tinh/Thần hoạt động. Các lớp lệch nhẹ để user thấy cùng một cung có nhiều tầng thông tin.

Ý nghĩa cần truyền:

> Một cung Kỳ Môn không chỉ có một nhãn; nó là nhiều lớp Thiên - Địa - Nhân đang chồng nhau.

Tránh:

- Không vẽ thành sơ đồ kỹ thuật khô.
- Không nhồi icon Môn/Tinh/Thần vì Dot 01 đã có.
- Không dùng màu neon hologram.

## Asset 05 - ưu tiên cao

### `ky-mon-09-duty-seal-tri-phu-tri-su`

Loại ảnh: card ngang 4:3.

Vị trí UI dự kiến: khối **Trị Phù - Trị Sử (trục bàn)**.

Mô tả:

Hai ấn lệnh đặt trên bàn cửu cung: một ấn đại diện Trị Phù, một ấn đại diện Trị Sử. Một ấn thuộc thiên/tinh, một ấn thuộc môn/sự. Hai dây đỏ hoặc hai luồng đồng sáng nối về cung đang giữ quyền chỉ huy. Cảm giác là trục chủ quản của bàn, không phải vua/ngai.

Ý nghĩa cần truyền:

> Trị Phù - Trị Sử là trục điều khiển, giúp biết nơi nào giữ "quyền lệnh" của bàn Kỳ Môn.

Tránh:

- Không vẽ vua, tướng quân, ngai vàng.
- Không dùng icon thần linh to.
- Không viết chữ trên ấn.

## Asset 06 - ưu tiên cao

### `ky-mon-10-personal-reading-dam-lien`

Loại ảnh: hero/card ngang 16:9.

Vị trí UI dự kiến: khối **Đàm Liên luận lá số sinh anh**.

Mô tả:

Một lá số sinh Kỳ Môn nằm trên bàn gỗ tối, bên cạnh sách cổ Đàm Liên mở mờ, cửu cung ở trung tâm và các đường thời gian sinh thần đi vào bàn. Không phải hỏi việc tức thời; đây là đọc cấu trúc sinh theo Kỳ Môn. Có cảm giác học thuật, đối chiếu sách, không mê tín.

Ý nghĩa cần truyền:

> Personal reading theo Đàm Liên là đọc bàn Kỳ Môn sinh, khác với cast hỏi việc ở thời điểm hiện tại.

Tránh:

- Không vẽ chân dung Đàm Liên.
- Không vẽ người xem bói.
- Không dùng hiệu ứng tiên tri rẻ tiền.

## Asset 07 - tùy chọn

### `ky-mon-11-avoid-and-favor-directions`

Loại ảnh: panoramic 21:9 hoặc 16:9.

Vị trí UI dự kiến: khối **hướng tốt / hướng nên tránh** nếu UI tách riêng sau này.

Mô tả:

Một vòng phương vị bao quanh bàn cửu cung. Một vài hướng mở ra bằng ánh lam-vàng, một vài hướng bị phủ đỏ sẫm/khói. Cần thể hiện "nên/không nên theo việc", không phải cát hung vĩnh viễn.

Ý nghĩa cần truyền:

> Hướng tốt/tránh trong Kỳ Môn là lựa chọn chiến thuật theo việc và thời điểm.

Tránh:

- Không vẽ biển báo giao thông.
- Không vẽ hướng xấu như tai họa tuyệt đối.
- Không viết chữ hướng trong ảnh.

## Thứ tự giao ảnh

1. `ky-mon-05-task-decision-gate`
2. `ky-mon-06-cach-cuc-detection`
3. `ky-mon-07-relative-direction-center`
4. `ky-mon-08-heaven-earth-human-layers`
5. `ky-mon-09-duty-seal-tri-phu-tri-su`
6. `ky-mon-10-personal-reading-dam-lien`
7. `ky-mon-11-avoid-and-favor-directions` nếu còn thời gian

## Cách duyệt ảnh

Ảnh đạt khi:

- Nhìn thumbnail biết là Kỳ Môn: cửu cung, bàn lệnh, phương vị, trục chỉ huy.
- Không vẽ lại style Tử Vi/Bát Tự.
- Có vùng trống để UI overlay title/verdict/task.
- Mobile crop giữ được bàn lệnh hoặc trục ý nghĩa ở trung tâm.
- Không có chữ giả, không có nhân vật fantasy.

Ảnh không đạt khi:

- Giống tarot nhân vật hoặc tranh thần tướng.
- Giống dashboard business hiện đại.
- Dùng quá nhiều la bàn phong thủy chung chung mà mất chất Kỳ Môn.
- Cảnh quá sáng/chi tiết khiến text UI khó đọc.

