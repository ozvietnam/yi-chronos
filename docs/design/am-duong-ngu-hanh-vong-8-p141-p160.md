# Vòng 8 — Học Thuyết Âm Dương Ngũ Hành (Lê Văn Sửu) p141-p160 (2026-06-13)

## 📍 Vị trí
- Phạm vi: p141 → p160 (20 trang) — kết "Triển vọng" + mở **CHƯƠNG 4: Khí chất sinh học người
  Việt và Âm Dương Ngũ Hành** (chương ĐỈNH chứng minh luận điểm nguồn gốc Việt).
- Mạch: nhịp thời sinh học → cảm giác/ý thức (Pavlov ↔ tạng phủ-giác quan) → **ngôn ngữ tiếng
  Việt là THANH** → 6 thanh = bằng/trắc = âm/dương + tư thế + tượng hình → âm dương trong văn học.

## 🎯 Paradigm cốt em ngộ

1. ⭐⭐ **NGŨ HÀNH ↔ TẠNG PHỦ ↔ GIÁC QUAN ↔ SẮC ↔ VỊ ↔ NGŨ ÂM** (p143-147) — bảng tương ứng
   THÂN THỂ, nền y học cổ. Mỗi tạng nối một giác quan: Can-mắt, Thận-tai, Tỳ-lưỡi, Tâm-tay,
   Phế-mũi. Sắc/vị vào tạng tương ứng (xanh-chua→gan, đỏ-đắng→tim...). **Ngũ âm Cung-Thương-
   Giốc-Chủy-Vũ** (thang ngũ cung nhạc cổ) ↔ 5 tạng ↔ 5 loại tiếng (ca/khóc/hô/cười/rên). Tây
   phương kiểm chứng: xanh ảnh hưởng gan, đỏ ảnh hưởng tim.

2. ⭐⭐ **6 THANH TIẾNG VIỆT = BẰNG (ÂM) / TRẮC (DƯƠNG)** (p146-153) — đóng góp gốc + luận điểm
   khí chất sinh học người Việt (ATTRIBUTION). Tiếng Việt đơn âm → diễn đạt tình cảm bằng đổi
   THANH. 2 bằng (không dấu, huyền) phát triển NGANG = âm/êm dịu; 4 trắc (sắc, ngã, hỏi, nặng)
   phát triển DỌC = dương/mạnh mẽ. Mỗi thanh có **đường hình** + **tư thế đầu-cổ** (ngửa lên =
   thượng, cúi gập = hạ...) — cộng hưởng nguyên lý TƯ THẾ THÂN THỂ của Mai Hoa (Iron Rule #4 BƯỚC 4).

3. ⭐ **TÍNH TƯỢNG HÌNH CỦA THANH** (p154-155). Từ chỉ chiều hướng nào mang thanh có đường hình
   cùng chiều: đi/ngang (đoản, phẳng), tiến/cố/gắng (thượng, lên), ngã/vã (khứ, vọt mất thăng
   bằng), nảy/gảy (hồi, đàn hồi), rụng/đập/quật (hạ, rơi gập). Từ ngăn chặn cũng dùng thanh cùng
   đường hình → ngôn ngữ Việt mô phỏng vận động tự nhiên ở tầng âm thanh.

4. ⭐ **PHẢN XẠ PAVLOV ↔ NGŨ HÀNH** (p142-143). Pavlov: phản xạ có điều kiện tác động chủ yếu
   2 giác quan NGHE-NHÌN. Lê Văn Sửu: âm dương-ngũ hành đã KHÁI QUÁT sớm nhất tính chất phản xạ
   có/không điều kiện trong giác quan-tạng phủ; khoa học Tây phương chỉ làm SÁNG TỎ giá trị cổ
   Phương Đông. Phân biệt ÂM (nhạc, phổ quát toàn nhân loại) vs THANH (tiếng nói, riêng dân tộc).

5. ⭐ **ÂM DƯƠNG CỦA THANH TRONG VĂN HỌC VIỆT** (p155-159). Tiểu phẩm 2 vế: nêu vấn đề = dương
   (trắc nhiều), làm trọn = âm (bằng nhiều); tỷ lệ bằng/trắc quyết sắc thái. Phân tích Cao Bá
   Quát: phá tỷ lệ 6-3 thành 5-4 ('Đá xanh xây cống') để lộ gay gắt; giữ tỷ lệ nhưng đổi vị trí
   thanh dương ('người trói người') để giữ khí phách trước vua. Tài dùng âm-dương-thanh làm vũ khí.

## 💬 Quote NGUYÊN VĂN đắt nhất
> "Duy nhất có dân tộc Việt... nếu đem so với cả vùng Phương Đông cũng vẫn là đặc biệt. Nét đặc
> biệt của ngôn ngữ dân tộc Việt là cảm nhận thanh, phát âm ngôn ngữ đều tuân theo quy luật
> tương ứng giữa thanh với âm dương - ngũ hành."
> — Lê Văn Sửu p145 (LUẬN ĐIỂM TÁC GIẢ — attribution, cần đối chiếu)

## 🔧 PHASE A — ENGINE
- [x] `ngu_hanh_nen.py`: `NGU_HANH_THAN` (tạng/phủ/giác quan/sắc/vị/ngũ âm/tiếng mỗi hành) +
      payload `ngu_hanh_than` + chuyền `than` vào ngũ giác sinh-khắc.
- [x] `do_hinh_co.py`: `SAU_THANH` (6 thanh + đường hình `pts` + tư thế + âm dương) + payload
      `sau_thanh_tieng_viet`.

## 📚 PHASE B — WIKI
- [x] Ingest vòng 8: chunk p141-160 (26.8k chars) + 9 atoms. Corpus tổng **71 atoms**.
- [x] Atom luận điểm VN ngôn ngữ confidence 0.68 + nhãn "POSITION tác giả, không khẳng định sự thật".
- [x] Cross-link: ngũ âm ↔ âm nhạc/dong_y; tư thế thanh ↔ Mai Hoa BƯỚC 4; sắc-vị-tạng ↔ y học cổ.

## 🎨 PHASE C — UX/UI — 2 BỒI ĐẮP ĐỒ HÌNH
- [x] Làm giàu hover **ngũ giác Sinh·Khắc·Chế·Hóa**: thêm tạng/giác quan/sắc/vị/ngũ âm mỗi hành.
- [x] Tab thứ 9 **"🗣 6 Thanh Việt"**: lưới 2×3 đường hình 6 thanh, bằng=xanh(âm)/trắc=đỏ(dương),
      hover hiện tư thế đầu-cổ + ví dụ tượng hình.
- [x] Verify Playwright render harness data thật: 6 đường hình đúng mô tả sách (đoản phẳng, thượng
      lên, hồi võng, hạ rơi gập), màu âm/dương đúng. Screenshot
      `data/research/screenshots/do-hinh-6-thanh-viet-vong8-*.png` — đọc tay, render đẹp.

## ⚠ Iron Rule check
- [x] **Attribution**: luận điểm khí chất sinh học người Việt + 6 thanh = bằng chứng nguồn gốc
      Việt → ghi nhãn rõ trong engine (`sau_thanh_tieng_viet.y_nghia`) + atom confidence thấp.
- [x] Ngũ âm/sắc/vị/tạng: dùng đúng bảng Châm cứu đại thành; giác quan theo cách trình bày tác giả
      (Tâm-tay, Tỳ-lưỡi) có ghi chú.
- [x] 6 thanh đường hình: minh họa theo mô tả Hình 4-1..4-6, ghi rõ "minh họa theo tác giả".
- [x] Cite trang + cổ thư đầy đủ.

## 📝 Tiến độ
- Đã đọc: 160 / 251 trang (64%)
- Còn lại: 91 trang ≈ 4-5 vòng

## ⏭ Tiếp theo
- Vòng 9: p161-180 — tiếp Chương 4: văn xuôi (tả người nghiện), dân ca tộc Việt, có thể sang
  chuyên đề NHÌN (nghệ thuật tạo hình) — chân thứ hai của luận điểm nguồn gốc Việt.
