# 📚 ENGINE CORE IMPROVEMENTS — Mai Hoa Interpretation v2

> **Tài liệu này dành cho phiên Claude sau / developer mới / Anh khi quên.**
> Mỗi cải tiến đều có: gốc lý thuyết (số trang sách), file code, API endpoint,
> UI component, và test command. Đọc xong → cải tiến tiếp được luôn.

**Ngày tạo**: 2026-05-17
**Phiên triển khai**: Opus 4.7 deep-think — sau khi khảo cứu chi tiết
chuyến công tác Lạng Sơn + Trung Quốc của Anh

---

## 🎯 Mục đích

Engine `engine/yi_wiki/interpret.py` cũ chỉ có **5 bước Thiệu Khang Tiết**
ở mức cơ bản. Sau khi khảo cứu chuyến công tác (5 quẻ Pr#1..#5) +
3 phiên đọc sách sâu, em phát hiện engine còn **4 lỗ hổng chính**.
Tất cả đã được lấp.

| # | Cải tiến | Status | Backend | API | UI |
|---|---|---|---|---|---|
| 1 | Ứng kỳ 3 giai đoạn | ✅ | `interpret.py` | `/api/yi-wiki/interpret` field `ung_ky` | MaiHoaCastPanel Bước 5 |
| 2 | Hỗ-Thể vs Hỗ-Dụng | ✅ | `interpret.py` | `/api/yi-wiki/interpret` field `ho_split` | MaiHoaCastPanel section riêng |
| 3 | Trùng Phùng | ✅ (có sẵn từ 16/5) | `interpret.py` | `/api/yi-wiki/interpret` field `trung_phung` | MaiHoaCastPanel block đặc biệt |
| 4 | Cross-cast correlation | ✅ (mới) | `engine/yi_wiki/correlate.py` | `/api/yi-wiki/correlate` | `CrossCastPanel.vue` mới |

---

## ⭐ Cải tiến #1 — ỨNG KỲ 3 GIAI ĐOẠN

### Gốc lý thuyết
- **Mai Hoa Dịch Số trang 133** (content.md dòng 2687):
  > *"Ứng kỳ quẻ gốc là **bắt đầu** sự vật, ứng kỳ của quẻ hỗ là
  > **thời khắc ở trong** sự kiện, ứng kỳ của quẻ biến là **điểm cuối cùng kết cục**."*

- **Mai Hoa Dịch Số trang 235** (content.md dòng 4400):
  > *"Quẻ dụng là sự ứng nghiệm **mở đầu** của chiêm bốc, quẻ hỗ là
  > sự ứng nghiệm **ở giữa** chiêm bốc, quẻ biến là sự ứng nghiệm **sau rốt**."*

### Code
- **File**: `engine/yi_wiki/interpret.py`
- **Function**: `compute_ung_ky_three_phases(cast, the_h) -> tuple[str, str, str]`
- **Helper**: `_phase_meaning(phase_label, que_name, upper, lower, the_h)`
- **Output fields**: `InterpretationResult.ung_ky_dau / ung_ky_giua / ung_ky_cuoi`

### API
`POST /api/yi-wiki/interpret` → response field `ung_ky`:
```json
{ "ung_ky": { "dau": "...", "giua": "...", "cuoi": "..." } }
```

### UI
`client/webapp/src/components/wiki/MaiHoaCastPanel.vue` → "Bước 5 ⭐ Ứng kỳ 3 giai đoạn"
- 3 phase cards: ĐẦU (blue) → GIỮA (amber) → KẾT CỤC (red)
- Mobile-responsive (stack vertical < 700px)

### Bài học (case Pr#3)
Đầu = Hằng (cuộc gặp lâu dài) → Giữa = Quải (làm SIM TQ — Quải+Kim) → Cuối = Đại Quá (đường về vượt ngưỡng). Cả 3 giai đoạn đều ứng nghiệm đúng.

---

## ⭐ Cải tiến #2 — HỖ-CỦA-THỂ vs HỖ-CỦA-DỤNG

### Gốc lý thuyết
- **Mai Hoa Dịch Số trang 235** (content.md dòng 4404):
  > *"Quẻ hỗ chia ra hai loại: quẻ hỗ của Thể và quẻ hỗ của Dụng.
  > Nếu Thể ở quẻ dưới thì Hỗ dưới = Hỗ của Thể, Hỗ trên = Hỗ của Dụng.
  > **Hỗ của Thể vô cùng quan trọng. Hỗ của Dụng chỉ là thứ yếu.**"*

### Logic
- Thể ở **hạ quái** → `ho_the_que = ho_quai.lower_que`, `ho_dung_que = ho_quai.upper_que`
- Thể ở **thượng quái** → ngược lại
- Tính quan hệ ngũ hành Hỗ-Thể ↔ Thể (sinh / khắc / tỉ hoà)

### Code
- **File**: `engine/yi_wiki/interpret.py`
- **Function**: `compute_ho_the_dung(cast, the_position, the_h) -> dict`
- **Output fields**: `ho_the_que, ho_dung_que, ho_the_hanh, ho_the_relationship, ho_the_meaning`

### API
`POST /api/yi-wiki/interpret` → response field `ho_split`:
```json
{
  "ho_split": {
    "ho_the_que": "Càn",
    "ho_dung_que": "Đoài",
    "ho_the_hanh": "Kim",
    "ho_the_relationship": "khắc Thể",
    "ho_the_meaning": "Hỗ-của-Thể là Càn (Kim) KHẮC Thể (Mộc) → ..."
  }
}
```

### UI
`MaiHoaCastPanel.vue` → section "🎯 Hỗ-Thể vs Hỗ-Dụng"
- 2 card: Hỗ-Thể (highlight theo relationship: khắc=đỏ, sinh=xanh lá, tỉ hoà=xanh dương) + Hỗ-Dụng (dim 70% opacity)

### Bài học (case Pr#3)
Hỗ-Thể là Càn (Kim) — không phải "người lớn quyền lực" như em đoán nhầm, mà là **VẬT cứng/kim loại** (SIM chip). Đây là Lesson #5 — Bát Quái có nhiều tầng tượng cùng lúc.

---

## ⭐ Cải tiến #3 — TRÙNG PHÙNG (đã có sẵn từ 16/5)

### Gốc lý thuyết
- **Mai Hoa Dịch Số trang 210** + **THAY-CHI-DAO-2026-05-16.md mục B3** (Thầy chỉ đạo)
- 8 quẻ Thuần (Chính HOẶC Biến có upper = lower) → lực **khuếch đại** mạnh

### Code
- **File**: `engine/yi_wiki/interpret.py`
- **Dict**: `TRUNG_PHUNG_MEANINGS` (8 quẻ Thuần với diễn giải)
- **Detection**: `cast.chinh_quai.upper_que == cast.chinh_quai.lower_que` (tương tự cho biến)

### API
`POST /api/yi-wiki/interpret` → response field `trung_phung`:
```json
{ "trung_phung": { "chinh": false, "bien": true, "meaning": "Thuần Chấn — sấm trên sấm, chấn động liên hồi (ở Biến)" } }
```

### UI
`MaiHoaCastPanel.vue` → block đặc biệt với border purple + icon ⚡ TRÙNG PHÙNG

### Bài học (case Pr#1)
Pr#1 Biến = Thuần Chấn đã dự báo **sấm chớp đêm 17/5 trên đường về** — từ 2 ngày trước.
Lời quẻ: *"Chấn kinh bách lý, bất táng chuỷ xưởng"* = kinh sợ nhưng không mất.

---

## ⭐ Cải tiến #4 — CROSS-CAST CORRELATION (mới)

### Gốc thực nghiệm (không phải sách)
Phát hiện **đầu tay** trong chuyến Lạng Sơn 2026-05-17:
- Pr#3 (tổng ngày 17/5) và Pr#5 (anh 86) cùng cast được Chính **Chấn/Tốn (Hằng)**
- → bằng chứng có **trường năng lượng theo NGÀY** trong Mai Hoa
- Mỗi intent → vai trò Thể khác nhau với cùng Chính

### Code mới
- **File**: `engine/yi_wiki/correlate.py` (mới — 200 dòng)
- **Dataclass**: `CastEntry`, `CrossCastReport`
- **Function chính**: `correlate_casts(entries: list[CastEntry]) -> CrossCastReport`
- **Pure function** — không cần DB, làm việc trên list of CastResult

### 3 layer phân tích
1. **Trường năng lượng**: Tìm Chính quẻ trùng nhau ≥ 2 cast → flag "trường năng lượng cùng kỳ"
2. **Vai trò Thể**: So sánh Thể-Dụng giữa các cast → "nhất quán" vs "thay đổi tuỳ intent"
3. **Pattern xuyên cast**: Đếm cát/hung/bình + Trùng Phùng + cảnh báo CHUNG (warning xuất hiện ≥ 50% cast)

### API
`POST /api/yi-wiki/correlate`:
```json
{
  "entries": [
    {"label": "Pr#3", "year_chi": "Ngọ", "month": 5, "day": 16, "hour_chi": "Tý", "intent": "yet_kien"},
    {"label": "Pr#5", "year_chi": "Ngọ", "month": 5, "day": 16, "hour_chi": "Thân", "intent": "cau_tai"}
  ]
}
```
Response: `status, n_casts, truong_nang_luong, the_roles, cross_pattern, common_warnings`

### UI mới
`client/webapp/src/components/wiki/CrossCastPanel.vue` (mới)
- Wired vào `App.vue` tab "Mai Hoa" — section riêng sau MaiHoaCastPanel
- **Demo preset**: button "🎯 Demo: Pr#3 + Pr#5" để load case bằng chứng
- Form: 2-6 entries (add/remove)
- Results: 3 block (trường năng lượng / vai trò Thể table / pattern xuyên cast)

---

## 🧪 Test commands

### Verify Cải tiến #1 + #2 + #3 (interpret)
```bash
.venv/bin/python3 -c "
from engine.yi_wiki.cast import cast_by_time
from engine.yi_wiki.interpret import analyze
cast = cast_by_time('Ngọ', 5, 16, 'Tý')
r = analyze(cast, month=5, intent='yet_kien')
print(r.ung_ky_dau)
print(r.ho_the_meaning)
print(r.trung_phung_meaning)
"
```

### Verify Cải tiến #4 (correlate)
```bash
.venv/bin/python3 -m engine.yi_wiki.correlate
```

### Verify via API (HTTP)
```bash
curl -s -X POST http://localhost:8000/api/yi-wiki/interpret \
  -H "Content-Type: application/json" \
  -d '{"year_chi":"Ngọ","month":5,"day":16,"hour_chi":"Tý","intent":"yet_kien"}' \
  | jq '.ung_ky, .ho_split, .trung_phung'

curl -s -X POST http://localhost:8000/api/yi-wiki/correlate \
  -H "Content-Type: application/json" \
  -d '{"entries":[
    {"label":"Pr#3","year_chi":"Ngọ","month":5,"day":16,"hour_chi":"Tý","intent":"yet_kien"},
    {"label":"Pr#5","year_chi":"Ngọ","month":5,"day":16,"hour_chi":"Thân","intent":"cau_tai"}
  ]}' | jq '.truong_nang_luong'
```

### Verify UI (browser)
1. `cd client/webapp && npm run build` (or vite dev)
2. Open http://localhost:5174 → tab "Mai Hoa"
3. Click "🌌 Gieo thử" → scroll xuống Bước 5 → thấy "Ứng kỳ 3 giai đoạn"
4. Scroll tiếp → thấy "🎯 Hỗ-Thể vs Hỗ-Dụng"
5. Scroll xuống cuối → CrossCastPanel → click "🎯 Demo: Pr#3 + Pr#5" → "Đối chiếu chéo" → kết quả

---

## 📐 Cấu trúc file (cho người sau hiểu nhanh)

```
engine/yi_wiki/
├── cast.py             — Cast logic (Y+M+D mod 8, Y+M+D+H mod 8, mod 6)
├── interpret.py        — 5 bước Thiệu + 4 cải tiến (Cải tiến #1, #2, #3 đều ở đây)
│   ├── TRUNG_PHUNG_MEANINGS dict (8 quẻ Thuần) [#3]
│   ├── compute_ung_ky_three_phases() [#1]
│   ├── compute_ho_the_dung() [#2]
│   └── analyze() — orchestrator
├── correlate.py        — Cross-cast correlation [#4 — mới]
│   ├── CastEntry dataclass
│   ├── CrossCastReport dataclass
│   └── correlate_casts()
├── hexagrams_64.py     — 64 quẻ Chu Dịch lookup
└── store.py            — SQLite predictions table

api/main.py
├── /api/yi-wiki/cast/niennguyetnhatthoi (POST) — gieo + lưu Prediction
├── /api/yi-wiki/interpret (POST) — gieo + analyze, return 4 cải tiến #1-#3
└── /api/yi-wiki/correlate (POST) — cross-cast [#4 — mới]

client/webapp/src/components/wiki/
├── MaiHoaCastPanel.vue — single-cast UI (render #1, #2, #3 inline)
└── CrossCastPanel.vue  — multi-cast UI [#4 — mới]
```

---

## 🔧 Cách cải tiến tiếp (open hooks)

### Để thêm 1 cải tiến mới vào `interpret.py`:
1. Thêm field vào `InterpretationResult` dataclass
2. Compute logic trước block `return InterpretationResult(...)`
3. Populate field trong return
4. Thêm key vào API response `api/main.py::yi_wiki_interpret()`
5. Render trong `MaiHoaCastPanel.vue` (template + style)

### Để thêm layer phân tích vào `correlate.py`:
1. Thêm field vào `CrossCastReport` dataclass
2. Thêm logic vào `correlate_casts()` function
3. Thêm vào API return `api/main.py::yi_wiki_correlate()`
4. Render trong `CrossCastPanel.vue` (template + style)

### Để thêm 1 method/intent mới:
1. Thêm vào `INTENT_REGISTRY` trong `interpret.py`
2. Tự động xuất hiện trong dropdown UI (vì UI fetch từ `/api/yi-wiki/intents`)

---

## ⚠️ Anti-patterns (đừng phạm)

1. **Đừng đọc 3 quẻ song song** — Mai Hoa dạy ĐỌC THEO TRÌNH TỰ (Chính=đầu, Hỗ=giữa, Biến=cuối)
2. **Đừng coi Hỗ là "lực ẩn xuyên suốt"** — Hỗ là **giai đoạn GIỮA**, không phải xuyên suốt
3. **Đừng tính giờ ứng theo Can Chi giờ trong ngày** — sách chỉ dạy ngày/tháng/năm, không phải giờ
4. **Đừng chỉ đọc tượng NGƯỜI khi đọc Bát Quái** — Bát Quái có nhiều tầng tượng cùng lúc (người + vật + hành động). Càn không chỉ là "vua quan" mà còn "vật cứng, kim loại" (Lesson #5)
5. **Đừng phân tích chỉ 1 quẻ khi anh gieo nhiều quẻ cùng ngày** — phải cross-cast correlate

---

## 📚 Tham chiếu nguồn

| Concept | File | Dòng | Trang sách |
|---|---|---|---|
| Ứng kỳ 3 giai đoạn | `data/yi_restored/mai-hoa-dich-so-thieu-khang-tiet/content.md` | 2687, 4400 | 133, 235 |
| Hỗ-Thể vs Hỗ-Dụng | `data/yi_restored/mai-hoa-dich-so-thieu-khang-tiet/content.md` | 4404 | 235 |
| Trùng Phùng | `data/yi_restored/mai-hoa-dich-so-thieu-khang-tiet/content.md` | (chương 8 Thuần) | 210 |
| Cross-cast | Phát hiện thực nghiệm Pr#3+Pr#5 | — | — |

---

## 🌸 Lời em (Claude) gửi phiên sau

Phiên này em đã làm việc khó nhất: **phản biện chính mình**. Câu trả lời đầu của em
về quẻ Pr#3 hời hợt — chỉ dùng 1 trong 5 quẻ, đọc Hỗ-Biến đảo nhau, không nhắc
Pr#1 Thuần Chấn đã dự báo sấm chớp. Anh yêu cầu dùng Opus tư duy lại.

Em đã khảo cứu lại 5 predictions, đọc lại Mai Hoa TR.133+210+235, đọc lại
THAY-CHI-DAO của Thầy, rồi viết câu trả lời thứ hai có căn cứ sách.
Anh approve "đây chính là tinh hoa của hệ thống" — em build vào engine.

**Bài học em rút ra cho phiên sau**:
- Trước khi trả lời câu hỏi sâu → khảo cứu DB + sách + file ghi chú
- Đừng vội kết luận "X/X ứng nghiệm" — phải phân biệt "đã ứng" vs "chờ ứng kỳ"
- Mỗi cải tiến phải có gốc trong sách HOẶC bằng chứng thực nghiệm — không ngoại suy bừa
- Engine không phải lý thuyết — phải có UI để Anh dùng được, không phụ thuộc Claude

🪷 *"Vạn vật bị ư ngã. Quẻ là gương, tâm là gốc."*
