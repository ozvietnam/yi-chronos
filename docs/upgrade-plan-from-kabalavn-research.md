# Kế hoạch nâng cấp YI-CHRONOS — học hỏi từ tiền bối

**Ngày lập:** 2026-05-11
**Cập nhật:** 2026-05-11 (thêm research 9 repos quốc tế về Zhouyi/I Ching)
**Nguồn nghiên cứu:**
- VN: https://github.com/kabalavn (8 repos) + https://kabala.vn
- Quốc tế: 9 repos Python/JS/C++ chuyên sâu Zhouyi (xem Phase 6-7 dưới)

**Báo cáo gốc:** xem 2 agent research outputs trong session 2026-05-11.

---

## Tinh thần

Kabala.vn là tiền bối VN làm divination web ~10+ năm. Engine họ closed-source, chỉ public README marketing — nhưng **content taxonomy, URL convention, content framing, pricing model** của họ là chuẩn thị trường VN. YI-CHRONOS học những thứ đó, đồng thời giữ lợi thế **engine mở + có thể audit + có Liên Hoa Độn Pháp với luận sự đầy đủ** (Kabala không có).

**Nguyên tắc làm dần:**
- Làm tuần tự, không gộp.
- Mỗi mục có: scope rõ, file ảnh hưởng, tiêu chí Done.
- Sau mỗi mục → test pass + dùng được trên UI → mới qua mục kế.

---

## Phase 1 — Hoàn thiện Liên Hoa (current focus)

### ✅ Đã xong (2026-05-11)
- Engine `engine/lien_hoa/` package
- Luận sự layer (6 lĩnh vực: vận đời, tài lộc, hôn nhân, nhà cửa, sức khỏe, xuất hành)
- UI panel với expand KTS + luận sự cards
- 44/44 tests pass

### 🟡 Mục 1.1 — Onboarding drawer cho Liên Hoa
**Nguồn cảm hứng:** `kabalavn/The-64-Hexagrams-of-the-I-Ching` — pedagogy chain Thái Cực → Lưỡng Nghi → Tứ Tượng → Bát Quái → 64 Quẻ.

**Scope:**
- Thêm component `LienHoaOnboardingDrawer.vue` (collapsible).
- 5 step cards (1 ngắn 2-3 câu mỗi step), kèm icon symbol.
- Mặc định collapsed; nút "📖 Liên Hoa hoạt động thế nào?" để mở.
- Step cuối link đến "vì sao 2 số tay tạo Bản Quái Kiện 5/9/13".

**File ảnh hưởng:**
- `client/webapp/src/components/LienHoaOnboardingDrawer.vue` (NEW)
- `client/webapp/src/components/LienHoaPanel.vue` (import + render)

**Done khi:**
- Drawer toggle hoạt động
- 5 bước hiển thị đầy đủ
- Mobile responsive (test < 768px width)

**Ước lượng:** 1.5h

---

### 🟡 Mục 1.2 — 64 hexagram image convention
**Nguồn cảm hứng:** kabala.vn — `sodep.kabala.vn/que/01.png`...`64.png` (zero-padded 2-digit).

**Scope:**
- Tạo `client/webapp/public/que-images/` chứa 64 PNG (placeholder SVG OK cho v1).
- Naming chuẩn: `01.png` ... `64.png`.
- Trong `LienHoaPanel.vue` (và các panel khác dùng hexagram): hiển thị image bên cạnh tên quẻ.
- Helper Vue: `<HexagramImage :king-wen="3" />` → `<img src="/que-images/03.png" />`.

**File ảnh hưởng:**
- `client/webapp/src/components/HexagramImage.vue` (NEW)
- `client/webapp/public/que-images/*.svg` hoặc `*.png` (NEW — 64 file)
- LienHoaPanel.vue, MaiHoaPanel.vue, LucHaoPanel.vue update để dùng

**Done khi:**
- 64 image hiển thị đúng cho tất cả quẻ
- Fallback gracefully nếu thiếu file
- File size hợp lý (<50KB mỗi SVG)

**Ước lượng:** 2-3h (SVG sinh từ binary code 6 bit)

---

### 🟡 Mục 1.3 — Slug routes cho 64 quẻ
**Nguồn cảm hứng:** kabala.vn — `que-3-thuy-loi-truan` style.

**Scope:**
- Vue Router add route `/quẻ/:slug` với slug format `{king_wen}-{upper_trigram_vi}-{lower_trigram_vi}-{name_vi_slug}`.
- Page hiển thị: image + tên + Thoán từ + Hào từ + diễn giải.
- Backend endpoint `/api/hexagram-by-slug/:slug` (hoặc reuse `/api/hexagram-interpretation-v2/:id` + map slug → id).
- Sitemap include 64 URL cho SEO sau này.

**File ảnh hưởng:**
- `client/webapp/src/router/index.js` hoặc tương đương
- `client/webapp/src/views/HexagramDetailView.vue` (NEW)
- `api/main.py` — add slug→id resolver
- `data/hexagram_slugs.json` (NEW) — bảng tra slug

**Done khi:**
- 64 URL truy cập được
- Link từ LienHoaPanel KTS → mở chi tiết quẻ
- Slug encoding chuẩn (không dấu, dash-separated)

**Ước lượng:** 3-4h

---

## Phase 2 — Tử Vi Bắc Phái nâng cấp

### 🟡 Mục 2.1 — Schema `chinh_tinh.json` 14 sao
**Nguồn cảm hứng:** `kabalavn/La-So-Tu-Vi` — bảng 14 chính tinh với cột chuẩn.

**Scope:**
- File `data/tu_vi/chinh_tinh.json` với 14 sao, mỗi sao có:
  ```json
  {
    "id": "tu_vi",
    "ten_vi": "Tử Vi",
    "ten_zh": "紫微",
    "ngu_hanh": "thổ",
    "am_duong": "âm",
    "hoa_khi": "quý",
    "chu_ve": ["lãnh đạo", "uy quyền", "địa vị"],
    "dac_dia": ["Ngọ", "Mùi", "Tý"]
  }
  ```
- Tương tự cho: Thiên Cơ, Thái Dương, Vũ Khúc, Thiên Đồng, Liêm Trinh, Thiên Phủ, Thái Âm, Tham Lang, Cự Môn, Thiên Tướng, Thiên Lương, Thất Sát, Phá Quân.
- Loader Python `engine/tu_vi/data_loader.py` → cache.

**Done khi:**
- 14 sao đầy đủ trong JSON
- Schema validation pass (pydantic model)
- Test load + truy cập đúng

**Ước lượng:** 2h (data entry chủ yếu)

---

### 🟡 Mục 2.2 — Template diễn giải `{Keywords, Tích cực, Tiêu cực}`
**Nguồn cảm hứng:** `kabalavn/Destiny-Matrix` — mỗi archetype có 3 section cố định.

**Scope:**
- Extend `chinh_tinh.json` mỗi sao thêm:
  ```json
  {
    "keywords": ["uy quyền", "trách nhiệm", "cô đơn ở đỉnh"],
    "tich_cuc": "Lãnh đạo bẩm sinh, thu hút quý nhân, hợp công việc đòi hỏi quyết đoán.",
    "tieu_cuc": "Dễ kiêu ngạo, cô độc, áp lực cao, khó hài lòng với cộng sự."
  }
  ```
- Vue component `ChinhTinhCard.vue` render đẹp 3 section.

**Done khi:**
- 14 sao đều có {keywords, tich_cuc, tieu_cuc}
- UI hiển thị balanced (không thiên vị)

**Ước lượng:** 3h (writing chính)

---

## Phase 3 — Convention chia sẻ chart

### 🟡 Mục 3.1 — URL contract `?birth=YYYY-MM-DD-HH-{nam|nu}`
**Nguồn cảm hứng:** kabala.vn — share link chuẩn VN.

**Scope:**
- Parse `?birth=1995-08-15-10-nam` → auto-fill profile form.
- Áp dụng cho: Tử Vi, Bát Tự, Western astrology panels.
- Nút "🔗 Sao chép link chia sẻ" trên mỗi chart.
- Backward compat: nếu profile store có active person, vẫn ưu tiên local.

**File ảnh hưởng:**
- `client/webapp/src/router/index.js` — query param parser
- `client/webapp/src/composables/useShareableUrl.js` (NEW)
- Mỗi panel: import + wire

**Done khi:**
- Dán URL Kabala vào → form tự fill
- Copy link → mở tab mới → chart đúng
- Test với 3-4 birth profiles

**Ước lượng:** 2-3h

---

## Phase 4 — Bát Tự engine (chưa build)

### 🟡 Mục 4.1 — Schema 7 tầng Bát Tự
**Nguồn cảm hứng:** `kabalavn/La-So-Bat-Tu` — 7-layer component list.

**Scope:**
- Build `engine/bat_tu/` package với output structure:
  1. `tu_tru` — 4 trụ Thiên Can / Địa Chi (năm, tháng, ngày, giờ)
  2. `ngu_hanh_balance` — Kim/Mộc/Thủy/Hỏa/Thổ counts
  3. `vong_truong_sinh` — 12 vòng
  4. `thap_than` — 10 thần (Tỷ Kiên, Kiếp Tài, Thực Thần, Thương Quan, Chính Tài, Thiên Tài, Chính Quan, Thất Sát, Chính Ấn, Kiêu Thần)
  5. `than_sat` — Quý nhân, Văn Xương, Đào Hoa, etc.
  6. `dung_than_hy_than` — element TA cần
  7. `dai_van_tieu_van` — 10-year cycles

- Engine cần: lunar calendar conversion, can-chi table lookup.

**File ảnh hưởng:**
- `engine/bat_tu/` (NEW package — constants.py, tu_tru.py, ngu_hanh.py, thap_than.py, dai_van.py, cast.py)
- `api/main.py` — endpoint `/api/bat-tu/cast`
- `tests/test_bat_tu.py` (NEW)

**Done khi:**
- Cast 1 lá Bát Tự return 7 layers
- Test với 3 ví dụ celeb đã biết kết quả (so sánh kabala.vn)
- Tests pass

**Ước lượng:** 8-12h (lớn nhất)

---

### 🟡 Mục 4.2 — Bảng `ngu_hanh_colors.json` reusable
**Nguồn cảm hứng:** `kabalavn/La-So-Bat-Tu` color tables.

**Scope:**
- File `data/ngu_hanh_colors.json`:
  ```json
  {
    "kim": {
      "tuong_sinh": ["thổ"],
      "hoa_hop": ["kim"],
      "bi_khac": ["hỏa"],
      "khac_che": ["mộc"],
      "colors_recommend": ["#c0a878", "#d4af37", "#ffffff"],
      "colors_avoid": ["#d65a4a", "#ff4500"]
    },
    "moc": { ... }, "thuy": ..., "hoa": ..., "tho": ...
  }
  ```
- Vue widget `<PhongThuyColorPalette :element="kim" />` dùng được trên mọi panel.

**Done khi:**
- 5 element đầy đủ
- Widget hoạt động trên Bát Tự, Tử Vi, Liên Hoa, Western (sun sign element)

**Ước lượng:** 2h

---

## Phase 5 — Differentiator chiến lược

### 🟡 Mục 5.1 — Bát Tự Hà Lạc cross-module
**Nguồn cảm hứng:** `kabalavn/The-64-Hexagrams` README nhắc đến nhưng KHÔNG ship.

**Scope:**
- Endpoint `/api/bat-tu-ha-lac/cast` nhận birth datetime.
- Logic: từ Bát Tự (Thiên Can ngày + Địa Chi giờ) → suy ra **Quẻ Tiên thiên** (Hà Đồ) + **Quẻ Hậu thiên** (Lạc Thư) cho cá nhân.
- Output: 2 hexagram + giải thích "đời này anh mang quẻ X, vận hành theo quẻ Y".

**Yêu cầu:** Mục 4.1 (Bát Tự engine) phải xong trước.

**Done khi:**
- 2 hexagram output có cơ sở thuật toán (không random)
- Cross-reference với 1-2 sách Hà Lạc để verify
- Test 3 case

**Ước lượng:** 6-8h

**⭐ ĐÂY LÀ MOAT** — Kabala không có, mình ship được = unique value.

---

### 🟡 Mục 5.2 — Pricing/Paywall strategy
**Nguồn cảm hứng:** Kabala "lá số miễn phí + interpretation report trả phí".

**Scope:**
- Document `docs/pricing-strategy.md`:
  - Free tier: cast tất cả chart, basic interpretation
  - Premium tier: full luận sự PDF report, cross-school synthesis, historical chart save
  - Đặt cụ thể giá VND (so sánh kabala)
- Chưa build payment ngay, chỉ design tier.

**Done khi:**
- Doc strategy clear
- Identify được 3 premium features
- Quyết định khi nào enable (timeline)

**Ước lượng:** 2h (chỉ doc)

---

---

## Phase 6 — Học từ ichingshifa & cộng đồng Zhouyi quốc tế

> **Bối cảnh:** Sau khi quét 9 repos chuyên sâu (kentang2017/ichingshifa, muyen/decoding-iching, xiangzhang1015/Zhou_Yi_Zhan_Bu_in_Python, bollwarm/ZHOUYI, Ovilia/biangua, verifier-studio/yi, obiscr/yijing, wuyr/HexagramDecoder, niubideren111/I-Ching-Divination-System), phát hiện chính:
> - **kentang2017/ichingshifa (MIT)** là "át chủ bài" — Najia + 伏神 + 28-tú + 京房易 đầy đủ. Engine Lục Hào của ta còn thiếu mảng này.
> - **muyen/decoding-iching** có labeled dataset 384 hào với `ji_rate` + `yaoci_class ∈ {吉/中/凶}` — chuyển Kinh Dịch thành decision tool, đúng triết lý dự án ta.
> - **Ovilia/biangua** + **verifier-studio/yi** có UI patterns đỉnh: click-to-flip yao, Tiên Thiên ↔ Hậu Thiên morph.

### 🟡 Mục 6.1 — Najia / 伏神 / 28-tú cho Lục Hào engine ⭐ **GAP LỚN NHẤT**
**Nguồn:** `kentang2017/ichingshifa/src/ichingshifa/ichingshifa.py` (MIT — safe port). Hàm `Iching.dc_gua()` + `Iching.decode_gua()`.

**Scope:**
- Engine `engine/luc_hao/` hiện tại có: 6 hào + lục thân + dụng thần. THIẾU:
  - **伏神 (Hidden lines)** — hào ẩn từ 純卦 cha của 8 cung
  - **28-tú position** — mỗi hào ứng 1 tinh tú trong 28 chòm
  - **Najia 納甲** — gán Thiên Can + Địa Chi cho từng hào theo cung
  - **月建, 積算** — chỉ số thời gian Kinh Phòng (Jīng Fáng)
- Thêm các trường trên vào output JSON `luc_hao_state`.
- UI hiển thị thêm 1 collapsed section "Tầng sâu Kinh Phòng".

**File ảnh hưởng:**
- `engine/luc_hao/najia.py` (NEW)
- `engine/luc_hao/hidden_lines.py` (NEW)
- `engine/luc_hao/twenty_eight_xiu.py` (NEW)
- `data/luc_hao/najia_table.json` (NEW — bảng tra 64 quẻ × 6 hào)
- `engine/luc_hao/cast.py` — wire vào output
- `tests/test_luc_hao_najia.py` (NEW)

**Done khi:**
- Cast 1 quẻ Lục Hào trả về đầy đủ 4 trường mới
- Compare với output `ichingshifa` của Trung Quốc cho 5 case quẻ → khớp
- Tests pass

**Ước lượng:** 10-15h (lớn — cần ingest bảng dữ liệu)

---

### 🟡 Mục 6.2 — Da-Yan probability cross-validation
**Nguồn:** `xiangzhang1015/Zhou_Yi_Zhan_Bu_in_Python/Zhan_Bu.py` (MIT) — Da-Yan stalk simulation chuẩn.

**Scope:**
- Nếu sau này build "rút thẻ Đại Diễn" cho người không có 2 số tay Liên Hoa.
- Test 100,000 cast → so distribution với phân bố cổ điển (1/16 老陰, 5/16 少陽, 7/16 少陰, 3/16 老陽).
- Đây là sanity test, không phải feature chính.

**File ảnh hưởng:**
- `engine/yi_classic/da_yan.py` (NEW — optional)
- `tests/test_da_yan_distribution.py` (NEW)

**Done khi:**
- 100k samples → distribution lệch < 0.5% khỏi phân bố cổ điển

**Ước lượng:** 3h

---

### 🟡 Mục 6.3 — Hồ quái similarity layer cho Luận sự
**Nguồn:** `muyen/decoding-iching/data/analysis/iching_algorithm.json` — 互卦 similarity ~0.73 vs baseline 0.19.
**License:** NOASSERTION → reimplement, không copy.

**Scope:**
- Trong `engine/lien_hoa/luan_su.py`, khi domain reading verdict là "凶" hoặc "Bất thành":
  - Tính Hồ quái của Tiên đề (đã có trong cast).
  - Tra "bản chất bên trong" của Hồ quái từ data 64-hex của ta.
  - Trả thêm `inner_nature_note: str` cho domain reading.
- Thuật toán: text similarity giữa 卦辭 chánh và 卦辭 hồ → nếu similarity cao thì "bản chất tương đồng, dù vẻ ngoài xấu", thấp thì "bên trong khác biệt".

**File ảnh hưởng:**
- `engine/lien_hoa/luan_su.py` — add helper `inner_nature_hint()`
- `data/yi64/hexagram_text_vectors.json` (NEW — precomputed TF-IDF nếu cần)

**Done khi:**
- 6 domain readings có inner_nature_note khi verdict tiêu cực
- UI hiển thị note nhỏ dưới explanation
- Test với 3-4 case khẳng định note có nghĩa

**Ước lượng:** 5-7h

---

### 🟡 Mục 6.4 — Schema 64-hex enriched với 384 hào labels
**Nguồn:** `muyen/decoding-iching/data/structure/hexagrams_structure.json` + `biangua_384.json`.
**License:** NOASSERTION → ingest schema, label tự derive từ sách Việt.

**Scope:**
- Mở rộng `data/yi64/*.json` mỗi quẻ thêm:
  ```json
  {
    "king_wen_number": 1,
    "binary_bottom_first": "111111",
    "fuxi_position": 64,
    "is_symmetric": true,
    "inverse_king_wen": 1,
    "complement_king_wen": 2,
    "nuclear_upper": "Càn",
    "nuclear_lower": "Càn",
    "yaoci_classes": ["吉", "中", "中", "中", "中", "凶"],
    "ji_rates": [0.85, 0.6, 0.55, 0.5, 0.55, 0.15]
  }
  ```
- Label `yaoci_class` + `ji_rate` derive từ Ngô Tất Tố + Tam Thiên Dịch Số đã có.
- Loader Python wrap thành dataclass.

**File ảnh hưởng:**
- `data/yi64/enriched/*.json` (NEW)
- `core/yi64/model.py` — extend dataclass
- `tests/test_yi64_enriched.py` (NEW)

**Done khi:**
- 64 hex + 384 hào đầy đủ
- Mỗi field có nguồn (từ sách nào) note kèm
- Test load + truy cập

**Ước lượng:** 8-10h (data labeling chính)

---

### 🟡 Mục 6.5 — Chu Hi 0-to-6 moving line policy
**Nguồn:** `kentang2017/ichingshifa.mget_bookgua_details()` — explicit branch table cho 0/1/2/3/4/5/6 hào động.

**Scope:**
- File `core/yi64/moving_line_policy.py`:
  - 0 hào động → chỉ đọc Thoán từ
  - 1 hào động → đọc Hào từ ấy
  - 2 hào động → đọc 2 Hào từ, ưu tiên hào trên
  - 3 hào động → đọc Thoán Chánh + Thoán Biến
  - 4 hào động → đọc 2 Hào từ không động trong Biến
  - 5 hào động → đọc Hào từ không động trong Biến
  - 6 hào động → 用九 (Càn) / 用六 (Khôn) hoặc Thoán Biến
- Plug vào Lục Hào engine để chọn text hiển thị đúng.

**File ảnh hưởng:**
- `core/yi64/moving_line_policy.py` (NEW)
- `engine/luc_hao/cast.py` — wire

**Done khi:**
- 7 branch test pass
- UI Lục Hào hiển thị đúng text theo số hào động

**Ước lượng:** 3-4h

---

## Phase 7 — UI patterns từ Ovilia/biangua + verifier-studio/yi

### 🟡 Mục 7.1 — Click-to-flip yao (biến hào tương tác)
**Nguồn:** `Ovilia/biangua` — click 1 hào → tự động flip → load quẻ mới + URL hash `#111010`.

**Scope:**
- Component `<HexagramInteractive>` Vue 3:
  - 6 div hào dọc, click bất kỳ → toggle bit → emit new binary string
  - URL `?gua=111010` shareable
  - Hover hào → tooltip hiển thị hào từ
- Áp dụng trên trang chi tiết quẻ (mục 1.3).

**File ảnh hưởng:**
- `client/webapp/src/components/HexagramInteractive.vue` (NEW)
- `client/webapp/src/views/HexagramDetailView.vue` — embed
- Router add `?gua=` query param

**Done khi:**
- Click flip hoạt động smooth
- URL update khi flip
- Tooltip hiển thị hào từ đúng
- Mobile tap-friendly

**Ước lượng:** 4-5h

---

### 🟡 Mục 7.2 — Tiên Thiên ↔ Hậu Thiên Bát Quái morph animation
**Nguồn:** `verifier-studio/yi/static/js/yi.js` — CSS class toggle morph.

**Scope:**
- Component `<BaguaWheel>` SVG:
  - 8 trigram positioned theo Tiên Thiên (xt) hoặc Hậu Thiên (ht)
  - Button "🌀 Văn Vương diễn Dịch" → CSS transition morph
  - Tooltip mỗi trigram: tên + nguyên tố + Tượng
- Áp dụng trên homepage hoặc onboarding drawer Liên Hoa (mục 1.1).

**File ảnh hưởng:**
- `client/webapp/src/components/BaguaWheel.vue` (NEW)
- CSS animation 600ms cubic-bezier

**Done khi:**
- Morph smooth 60fps
- 8 trigram đúng vị trí ở cả 2 phases
- Storytelling text accompany animation

**Ước lượng:** 4-5h

---

### 🟡 Mục 7.3 — Hexagram glyph share (creative feature)
**Nguồn:** `wuyr/HexagramDecoder` (Apache-2.0) — Base64 ↔ 64 hexagram Unicode glyph (U+4DC0…U+4DFF).

**Scope:**
- Util `core/utils/hexagram_cipher.py`:
  - encode_reading(reading_json) → 16-char glyph string
  - decode_reading(glyph_str) → reading_json
- Share button trên mỗi quẻ: "🜲 Sao chép ấn ký" → clipboard 16 ký tự ☰☱☲...
- Paste vào tool → tự động load lại lá quẻ.

**File ảnh hưởng:**
- `core/utils/hexagram_cipher.py` (NEW)
- `client/webapp/src/composables/useReadingCipher.js` (NEW)
- LienHoaPanel, LucHaoPanel, MaiHoaPanel — add share button

**Done khi:**
- Round-trip encode/decode 100% chính xác
- Share UI works trên 3 panels
- Glyph hiển thị đúng font (cần fallback Noto Sans Symbols)

**Ước lượng:** 3-4h

---

## Cross-validation roadmap (sau khi engine ổn định)

**Mục 8 — Verification test suite** (làm tuần cuối, không vội):
- **Liên Hoa Độn Pháp** ↔ `kentang2017/ichingshifa.datetime_bookgua()`: cùng input lunar → so output.
- **Mai Hoa Dịch Số** ↔ same function trên.
- **Da-Yan distribution** ↔ `xiangzhang1015/Zhan_Bu.py`: 100k cast, χ² test.
- **互卦 / 綜卦 / 錯卦 transforms** ↔ `muyen/decoding-iching/data/structure/transformations.json`: exhaustive 384-edge match.
- **Binary key convention** ↔ `Ovilia/biangua/gua.json` (bottom-first verify).

**Ước lượng:** 5-6h tổng

---

## Tổng quan timeline

| Phase | Mục | Ước lượng | Khi nào |
|-------|-----|-----------|---------|
| 1.1 | Onboarding drawer Liên Hoa | 1.5h | Ngay sau session này |
| 1.2 | 64 hexagram images | 2-3h | Tuần 2026-05-11 |
| 1.3 | Slug routes 64 quẻ | 3-4h | Tuần 2026-05-11 |
| 2.1 | Schema chinh_tinh 14 sao | 2h | Tuần 2026-05-18 |
| 2.2 | Template diễn giải | 3h | Tuần 2026-05-18 |
| 3.1 | URL share contract | 2-3h | Tuần 2026-05-18 |
| 4.1 | Bát Tự engine 7 tầng | 8-12h | Tuần 2026-05-25 (cần spec kỹ trước) |
| 4.2 | Ngũ hành colors | 2h | Cùng tuần 4.1 |
| 5.1 | Bát Tự Hà Lạc | 6-8h | Tuần 2026-06-01 |
| 5.2 | Pricing doc | 2h | Bất cứ lúc rảnh |
| **6.1** | **Najia + 伏神 + 28-tú cho Lục Hào ⭐** | **10-15h** | **Tuần 2026-06-08** |
| 6.2 | Da-Yan probability cross-validation | 3h | Tuần 2026-06-08 |
| 6.3 | Hồ quái similarity layer | 5-7h | Tuần 2026-06-15 |
| 6.4 | Schema 64-hex + 384 hào labels | 8-10h | Tuần 2026-06-15 |
| 6.5 | Chu Hi 0-to-6 moving line policy | 3-4h | Tuần 2026-06-22 |
| 7.1 | Click-to-flip yao tương tác | 4-5h | Tuần 2026-06-22 |
| 7.2 | Tiên Thiên ↔ Hậu Thiên morph | 4-5h | Tuần 2026-06-22 |
| 7.3 | Hexagram glyph share (creative) | 3-4h | Tuần 2026-06-29 |
| 8   | Cross-validation suite | 5-6h | Tuần 2026-06-29 |

**Tổng mới:** ~78-100h work, rải 6-8 tuần.

---

## Nguyên tắc thực thi

1. **Một mục tại một thời điểm** — không parallel quá 2 mục.
2. **Test trước khi qua mục kế** — pytest + UI manual test.
3. **Commit nhỏ** — mỗi mục 1-3 commit, message rõ.
4. **Cập nhật doc này** — đánh dấu ✅ khi xong, ghi note nếu scope thay đổi.
5. **Học từ tiền bối, không copy** — đọc cách họ design, viết lại theo style của mình.

---

## Theo dõi tiến độ

- [x] 1.1 Onboarding drawer ✅ 2026-05-11
- [x] 1.2 64 hexagram images ✅ 2026-05-11
- [x] 1.3 Slug routes + modal + ?que= URL share ✅ 2026-05-11
- [x] 2.1 Schema chính tinh ✅ 2026-05-11 (14 sao + tích cực/tiêu cực template, gallery UI, 12 tests)
- [x] 2.2 Template diễn giải ✅ 2026-05-11 (gộp với 2.1, đã có {keywords, tich_cuc, tieu_cuc})
- [x] **2.1.Advanced — Tử Vi advanced layers ✅ 2026-05-11**
  - `engine/tu_vi/interpretation.py` — 12 cung readings, hóa attachments, polarity scoring
  - `engine/tu_vi/luu_tru.py` — transit stars for target year + Đại Hạn intra-cung + Tiểu Hạn
  - API: `target_year` param + `include_interpretation` flag
  - 16 tests pass
- [x] **4.1.γ — Bát Tự cách cục classifier ✅ 2026-05-11**
  - `engine/bat_tu/cach_cuc.py` — 10 classical patterns (Chính Quan, Thất Sát, Chính Tài, Thiên Tài, Thực Thần, Thương Quan, Chính Ấn, Thiên Ấn, Kiến Lộc, Dương Nhận)
  - Wire vào cast.py output
  - 6 tests pass
- [x] **1.x.deeper — Liên Hoa luận sự deeper ✅ 2026-05-11**
  - `engine/lien_hoa/luan_su_deeper.py` — per-KTS narrative (role + phase meaning + transition)
  - 4 extra domains: Con cái, Học vấn, Kiện tụng, Sự nghiệp
  - 3-paragraph composed synthesis (tổng quan + điểm mạnh-yếu + khuyến nghị)
  - Wire vào cast_lien_hoa output
  - 12 tests pass
- [x] **2.1.AnSao — Tử Vi An Sao engine ✅ 2026-05-11**
  - `engine/tu_vi/an_sao.py` — full Bắc Phái algorithm (10 layers)
  - 12 cung + Cục số + Tử Vi anchor + 14 chính tinh + 6 phụ tinh + 7 sát tinh + Tứ Hóa + Đại Vận + Tiểu Hạn
  - API: `POST /api/tu-vi/cast` (datetime hoặc lunar input)
  - UI: `TuViLaSoPanel.vue` lá số 4×4 truyền thống với 12 cung + Đại Vận strip
  - 40 tests pass — verify worked example với iztro canonical
- [x] 3.1 URL share contract `?birth=YYYY-MM-DD-HH-{nam|nu}` ✅ 2026-05-11
  - `composables/useBirthShare.js` parse/encode + 17 tests
  - App banner "Đã đọc sinh thần từ URL" + ephemeral active person
  - `BirthShareButton.vue` (Sao chép link / Ghim URL) trong ProfilesPanel
- [ ] 4.1 Bát Tự engine
- [ ] 4.2 Ngũ hành colors
- [x] 4.1 Bát Tự engine MVP ✅ 2026-05-11 (Tứ Trụ + Thập Thần + Ngũ Hành + Day Master strength, 22 tests)
- [x] **4.1.α Bát Tự deferred layers ✅ 2026-05-11**
  - **Vòng Trường Sinh** (12 trạng thái) — 4-pillar phase against Day Master + strength score
  - **Thần Sát** — 15 sao phụ cốt lõi (Thiên Ất Quý Nhân, Văn Xương, Lộc Thần, Dương Nhận, Đào Hoa, Hồng Loan, Thiên Hỷ, Tướng Tinh, Dịch Mã, Hoa Cái, Kiếp Sát, Cô Thần, Quả Tú, Thiên Đức, Nguyệt Đức)
  - **Đại Vận** 8 cycles + Tiểu Vận 12 yearly (direction Dương Nam Âm Nữ thuận / Âm Nam Dương Nữ nghịch)
  - 22 tests + full BatTuPanel UI sections
- [x] **4.1.β Bát Tự refinement ✅ 2026-05-11**
  - **Dụng Thần / Hỷ Thần / Kỵ Thần** heuristic — strong DM → drain (官/財/食), weak → support (印/比), balanced → month-branch
  - **Starting age tiết khí** chính xác — quy tắc 3-ngày-1-năm với solar longitude crossings (replaces rough default)
  - 14 tests + Dụng Thần card + tiết khí distance hiển thị trong Đại Vận UI
- [x] **5.1 ⭐ Bát Tự Hà Lạc cross-module — MOAT FEATURE LIVE ✅ 2026-05-11**
  - `engine/ha_lac/` package: Học Năng 1974 algorithm + Chen Tuan cross-verified
  - Worked example k366.com verified byte-by-byte (Cấu 44 → Trung Phu 61)
  - Output: Tiên thiên quái + Hậu thiên quái + 12-stage decade trajectory (84-90 năm)
  - API: `POST /api/ha-lac/cast`
  - 18 tests pass
- [ ] 5.2 Pricing doc
- [x] **6.1 (phần A-D-F): Najia + 伏神 + 8 cung + Thế/Ứng/Thân cho Lục Hào ⭐** ✅ 2026-05-11
  - `engine/luc_hao/jingfang.py` — 8 cung classifier, Najia, Lục thân theo cung, 伏神
  - 17 tests pass; wired vào `cast.py` (`jingfang_scaffold` + `transformed_jingfang_scaffold`)
  - UI Tab 4 "京房" trong `LucHaoResultPage.vue` với bảng Nạp Giáp + Phục thần cards
  - **Deferred sang session sau:** 28-tú mapping (6.1E), 月建/積算 (Step 9), cross-validation vs ichingshifa (6.1G)
- [ ] 6.2 Da-Yan probability cross-validation
- [ ] 6.3 Hồ quái similarity layer
- [ ] 6.4 Schema 64-hex + 384 hào labels
- [ ] 6.5 Chu Hi 0-to-6 moving line policy
- [ ] 7.1 Click-to-flip yao tương tác
- [ ] 7.2 Tiên Thiên ↔ Hậu Thiên morph
- [ ] 7.3 Hexagram glyph share (creative)
- [ ] 8 Cross-validation test suite

---

## 🔑 Bài học cốt lõi (đọc trước khi triển khai)

**Tiền bối mạnh nhất:** `kentang2017/ichingshifa` (Trung Quốc, MIT) — engine 京房易 production-grade, ship lên PyPI, có 伏神 + 28-tú + 月建 + 積算 đầy đủ.

**Triết lý đúng:** `muyen/decoding-iching` xem Kinh Dịch là **decision tool**, không phải mê tín. Có dataset labeled 384 hào với `yaoci_class ∈ {吉/中/凶}` và `ji_rate` ∈ [0,1]. Đây đúng hướng dự án ta — đã thể hiện qua câu của anh: "hệ thống hoá quy luật, lồng quẻ, để có lời khuyên gần xa, giúp người dùng dễ xác thực dữ liệu."

**Differentiator của YI-CHRONOS:**
1. **Luận sự engine cho Liên Hoa** (Phase 1) — không repo nào có.
2. **Bát Tự Hà Lạc cross-module** (Phase 5) — Kabala nhắc nhưng không ship.
3. **Multi-school synthesis** (Western + Đông phương) — chưa có ai làm.

**Đừng làm:**
- `niubideren111/I-Ching-Divination-System` — code chất lượng thấp, paywall lẫn logic.
- `bollwarm/ZHOUYI*` Perl — đã có engine Python tốt hơn.
- `muyen` ML formulas v3-v10 — chính họ note "moderate evidence", không robust.

**License an toàn để port:** MIT (ichingshifa, xiangzhang1015) + Apache-2.0 (HexagramDecoder).
**License không rõ → reimplement, không copy:** muyen, Ovilia, verifier-studio, obiscr, bollwarm.
