# Vòng 9 — Học Thuyết Âm Dương Ngũ Hành (Lê Văn Sửu) p161-p180 (2026-06-13)

## 📍 Vị trí
- Phạm vi: p161 → p180 (20 trang) — tiếp CHƯƠNG 4: ngôn ngữ tiếng Việt theo âm dương ngũ hành.
- Mạch: đường hình kết cấu thanh (= giai điệu) → từ láy/hư thanh → giao tiếp → **6 thanh ↔ tâm
  sinh lý ↔ tạng ↔ NGŨ HÀNH (Bảng 4-6/7/8)** → giới hạn cao/trường độ → **giọng vùng miền ↔ hành**.

## 🎯 Paradigm cốt em ngộ

1. ⭐⭐⭐ **6 THANH ÁNH XẠ ĐỦ 5 NGŨ HÀNH** (Bảng 4-6/4-7 p169-170) — cú nối quyết định: 6 thanh
   tiếng Việt không chỉ chia âm/dương (bằng/trắc) mà ánh xạ thẳng vào ngũ hành qua ĐỘ CAO + TÂM
   SINH LÝ + TẠNG PHỦ: Thượng(sắc)=HỎA/thần minh-vui/Tâm; Khứ(ngã)=MỘC/mưu lự-giận/Can; Đoản+
   Trường(không dấu+huyền)=THỔ/bình thản-lo/Tỳ; Hồi(hỏi)=KIM/trị tiết-buồn/Phế; Hạ(nặng)=THỦY/
   kỹ xảo-kinh hãi/Thận. → tiếng Việt mang trọn cấu trúc ngũ hành ở tầng âm thanh.

2. ⭐⭐ **TÂM SINH LÝ GIAO THOA NHƯ NGŨ HÀNH** (p171). 'nghĩ'=Mộc, 'lo/bình thản'=Thổ, 'buồn'=Kim
   → 'lo nghĩ'=Mộc+Thổ, 'lo buồn'=Thổ+Kim. Tổ hợp tâm lý sinh vô vàn sắc thái; từ ngữ phải tổ
   hợp đúng quy luật mới diễn đạt nổi — vì tác động âm thanh là trực tiếp, bản năng. (Cộng hưởng
   nguyên lý tổ hợp sao Tử Vi: mỗi tổ hợp = một sắc thái riêng.)

3. ⭐ **GIỌNG VÙNG MIỀN ↔ NGŨ HÀNH ĐỊA LÝ** (p176-178). Tập quán phát âm theo môi trường sinh học:
   Bắc Bộ (bắc=THỦY, lạnh) nói nhanh dứt khoát; Miền Trung (đông=MỘC, vất vả) nói chậm giằn giọng
   nặng; Nam Bộ (nam=HỎA, vui sung túc) kéo dài trường độ. → ngũ hành địa lý hằn vào cả cách nói.

4. ⭐ **ĐƯỜNG HÌNH KẾT CẤU THANH = GIAI ĐIỆU** (p162). Nối độ cao các thanh trong câu → đường hình
   mà diễn biến trùng tình cảm nội dung. Nhạc viện Hà Nội (1983): coi như 'ghi nhạc không lời'.
   Câu tiếng Việt tự thân là một bản nhạc.

5. ⭐ **TỪ LÁY + HƯ THANH theo âm dương** (p164-166). Giảm nghĩa → tổng âm dương = ÂM (tối tăm,
   làm lụng); tăng → DƯƠNG (khênh khang, oang oang). Hư thanh (i, ới, ì) ở dân ca = chỗ đệm
   CÂN BẰNG ÂM DƯƠNG cả câu. Giao tiếp 2 vế: chào/hỏi=dương (khách), đáp/trả lời=âm (chủ).

## 💬 Quote NGUYÊN VĂN đắt nhất
> "Lo nghĩ là Mộc + Thổ. Lo buồn là Thổ + Kim. Sự giao thoa, tổ hợp giữa các loại tâm sinh lý
> khác nhau đã sản sinh ra những tâm lý vô cùng phong phú, từ ngữ do đó cũng có sự giao thoa,
> tổ hợp mới đáp ứng và biểu đạt nổi."
> — Lê Văn Sửu p171

## 🔧 PHASE A — ENGINE
- [x] `do_hinh_co.py`: làm giàu `SAU_THANH` thêm hành/độ cao/tâm sinh lý/tạng (Bảng 4-6/7) +
      `TIENG_VUNG_MIEN` (Bắc-Thủy/Trung-Mộc/Nam-Hỏa) + payload tieng_vung_mien.
- [x] `ngu_hanh_nen.py`: `NGU_HANH_TAM_SINH_LY` (Bảng 4-8 độ cao↔tình cảm↔tạng↔từ mẫu) + payload.

## 📚 PHASE B — WIKI
- [x] Ingest vòng 9: chunk p161-180 (21.5k chars) + 9 atoms. Corpus tổng **80 atoms**.
- [x] Cross-link: 6 thanh↔ngũ hành; tâm lý giao thoa↔tổ hợp sao Tử Vi; giọng vùng↔hành địa lý.

## 🎨 PHASE C — UX/UI — NÂNG CẤP ĐỒ HÌNH 6 THANH
- [x] Tab **"🗣 6 Thanh Việt"**: tô màu đường hình theo NGŨ HÀNH (thay vì chỉ âm/dương); hover hiện
      hành + độ cao + tâm sinh lý + tạng; thêm details "🗺 Giọng vùng miền ↔ ngũ hành".
- [x] Verify Playwright render harness data thật: 6 đường hình đủ 5 màu hành (Thượng đỏ-hỏa, Khứ
      xanh-mộc, Đoản+Trường tan-thổ, Hồi trắng-kim, Hạ xanh dương-thủy) + 3 vùng miền. Screenshot
      `data/research/screenshots/do-hinh-6-thanh-ngu-hanh-vong9-*.png` — đọc tay, render đẹp.

## ⚠ Iron Rule check
- [x] 6 thanh↔ngũ hành: dùng đúng Bảng 4-6/4-7; vẫn nằm trong luận điểm tác giả (attribution kế thừa).
- [x] Giọng vùng miền: chỉ tag hành nơi tác giả gán rõ (Bắc/Trung/Nam); Hà Nội/Sơn Tây để text.
- [x] Cite trang + bảng đầy đủ.

## 📝 Tiến độ
- Đã đọc: 180 / 251 trang (72%)
- Còn lại: 71 trang ≈ 3-4 vòng

## ⏭ Tiếp theo
- Vòng 10: p181-200 — kỳ vọng sang chuyên đề NHÌN (nghệ thuật tạo hình Phương Đông) — chân thứ
  hai của luận điểm nguồn gốc Việt; hoặc tổng kết chương ngôn ngữ.
