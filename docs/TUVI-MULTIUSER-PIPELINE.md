# Đường dẫn DeepSeek chính chủ → Multi-user Tử Vi pipeline

> **Vấn đề user báo cáo (2026-05-19)**: User mới đăng ký không xem được Cách cục / Đại vận / Lưu niên / Lưu nguyệt — panel toàn báo "Chưa có dữ liệu".

## 🔍 3 vấn đề cộng dồn (đã fix)

### Vấn đề 1: Cache collision giữa các user
Trước: `data/yi_publishing/analysis_cache/{person_key}/` — KHÔNG có user namespace.
→ User A signup, setup profile → cache vào `analysis_cache/self/`
→ User B signup → ghi đè cùng path `analysis_cache/self/` (vì cùng `person_key='self'`)
→ User B vô tình đọc data của A; A re-run sẽ xoá data của B.

### Vấn đề 2: Chưa auto-run
User mới setup profile xong → vào panel thấy "Chưa có ... Nhấn 'Phân tích ngay'" → phải tự click 4 nút (Cách cục + Đại vận + Lưu niên + Lưu nguyệt) — UX kém, không phải ai cũng biết.

### Vấn đề 3: Bug an_sao.py (off-by-one)
`dau_quan()` validator yêu cầu `hour_index ∈ 0..11` nhưng được truyền `H = B[hour_branch] + 1 ∈ 1..12`.
→ User sinh giờ Hợi (H=12) crash với `ValueError: hour_index must be 0..11, got 12`.
→ Founder (giờ Tý, H=1) không trigger, nên bug ngủ yên cho đến khi user thứ N sinh giờ Hợi.

---

## 🛤 Đường dẫn dùng DeepSeek chính chủ

```
User mới đăng ký
    │
    ▼
POST /api/auth/signup           (api/auth.py)
    │   → INSERT users, auto-login + cookie
    │
    ▼
OnboardingModal.vue             (frontend)
    │   → POST /api/auth/setup-profile {birth, gender}
    │
    ▼
setup_profile()                 (api/auth.py)
    │   → UPSERT user_persons(person_key='self')
    │   → threading.Thread(_bg_runall).start()    ← AUTO-TRIGGER
    │       │
    │       ▼
    │   TuViAnalyzer(Person(person_key='self', user_id=N))
    │       │
    │       ▼
    │   engine.yi_publishing.translator.get_deepseek_client()
    │       │
    │       ▼
    │   client = OpenAI(
    │       base_url="https://api.deepseek.com/v1",   ← CHÍNH CHỦ
    │       api_key=<from data/ai_keys.json["deepseek"]>
    │   )
    │       │
    │       ▼
    │   4 calls DeepSeek (model="deepseek-chat", ~25s total, ~$0.02):
    │       │  • discover_cach_cuc()    →  cach_cuc.json
    │       │  • dai_van_annotate()     →  dai_van.json
    │       │  • luu_nien(2026, 2030)   →  luu_nien_2026_2030.json
    │       │  • luu_nguyet(2026)       →  luu_nguyet_2026.json
    │       │
    │       ▼
    │   Cache scoped per-user:
    │       data/yi_publishing/analysis_cache/u{N}/self/*.json
    │
    ▼
User vào panel Tử Vi
    │
    ▼
GET /api/tu-vi/analyze/self/<kind>
    │   → _cache_load("self", kind, user_id=N)
    │   → load u{N}/self/{kind}.json
    │
    ▼
Panel render đầy đủ Cách cục / Đại vận / Lưu niên / Lưu nguyệt
```

### Tại sao "chính chủ" quan trọng

| Route | Vấn đề |
|---|---|
| ❌ `openrouter.ai/api/v1` `deepseek/deepseek-chat` | Ambiguous model ID, đôi khi route sang model khác; thêm fee 5-10% |
| ❌ Bypass providers (mock) | Không real analysis |
| ✅ **`api.deepseek.com/v1`** `deepseek-chat` | Native API, giá gốc $0.27/M in + $1.10/M out, JSON mode chuẩn |

Code: `engine/yi_publishing/translator.py:88-103` — `get_deepseek_client()` lazy-init, raise nếu thiếu key.

Key lưu ở `data/ai_keys.json["deepseek"]` (chmod 600, gitignored). Owner config qua tab **⚙️ Cài đặt** → section "🔑 AI Providers" → DeepSeek → paste key → Lưu. **Mọi user dùng chung key này** (founder pays for everyone — đúng intent).

---

## ✅ Fix summary

### 1. Cache namespace per-user (`engine/tu_vi/analyzer.py`)

```python
@dataclass
class Person:
    person_key: str
    ...
    user_id: Optional[int] = None   # NEW

def _scoped_key(person_key: str, user_id: Optional[int] = None) -> str:
    if user_id is None:
        return person_key                    # legacy/founder fallback
    if user_id == 1 and person_key == "_founder":
        return person_key                    # founder backward compat
    return f"u{user_id}/{person_key}"        # all other users
```

Tất cả `_cache_load` / `_cache_save` call sites (16 chỗ trong analyzer.py + 5 chỗ trong report_pdf.py) đã pass `user_id`.

Backward compat: nếu cache scoped path không tồn tại, fallback sang legacy unscoped path (cho founder migrate cũ).

### 2. Auto-run pipeline (`api/auth.py:setup_profile`)

```python
# Sau khi save user_persons row 'self':
def _bg_runall():
    analyzer = TuViAnalyzer(Person(person_key="self", user_id=user["user_id"], ...))
    analyzer.discover_cach_cuc()
    analyzer.dai_van_annotate()
    analyzer.luu_nien(2026, 2030)
    analyzer.luu_nguyet(2026)
threading.Thread(target=_bg_runall, daemon=True).start()
```

Response trả `auto_pipeline_started: true` → frontend hiển thị banner "⏳ Đang phân tích lá số của bạn bằng DeepSeek (~30s)..."

### 3. Fix `an_sao.py` `dau_quan` H off-by-one

```diff
- dau_quan_idx = dau_quan(lunar_month, H)
+ # H uses 1..12 convention (Tý=1). dau_quan() expects 0..11 (Tý=0).
+ dau_quan_idx = dau_quan(lunar_month, H - 1)
```

### 4. API routes scope theo `user_id`

- `POST /api/tu-vi/analyze/{kind}` — `_resolve_person_from_request` set `user_id` từ `get_current_user(request)`
- `GET /api/tu-vi/analyze/{person_key}/{kind}` — `_cache_load(person_key, kind, uid)`
- `POST /api/tu-vi/run-all/{person_key}` — Person có user_id
- `GET /api/tu-vi/report-pdf/{person_key}` — `generate_pdf(person_key, user_id=uid)`

---

## 🧪 Multi-user E2E test (verified 2026-05-19)

```
Alice signup → uid=10 → setup birth 1990-04-15T07:30 (nữ)
Bob   signup → uid=11 → setup birth 1985-12-20T22:15 (nam, GIỜ HỢI — triggers an_sao bug)

Background pipelines (parallel):
    Alice → data/.../u10/self/{cach_cuc,dai_van,luu_nien_2026_2030,luu_nguyet_2026}.json
    Bob   → data/.../u11/self/{cach_cuc,dai_van,luu_nien_2026_2030,luu_nguyet_2026}.json

Verify isolation:
    Alice GET /api/tu-vi/analyze/self/dai_van → birth: 1990-04-15T07:30:00 ✓
    Bob   GET /api/tu-vi/analyze/self/dai_van → birth: 1985-12-20T22:15:00 ✓
    Alice ≠ Bob ✓

PDF per-user:
    Alice PDF 291,765 bytes  ≠  Bob PDF 283,538 bytes ✓
```

---

## 📁 Files thay đổi

```
engine/tu_vi/analyzer.py     +30 -16   (Person.user_id + _scoped_key + 16 call sites)
engine/tu_vi/an_sao.py       +2 -1     (dau_quan H-1 off-by-one fix)
engine/tu_vi/report_pdf.py   +8 -7     (user_id propagate through build_html/generate_pdf)
api/auth.py                  +30       (auto-run pipeline thread in setup_profile)
api/main.py                  +12 -2    (4 endpoints: pass user_id to TuViAnalyzer)
client/webapp/src/components/OnboardingModal.vue  +12  (autoPipelineMsg banner)
```

---

## 🔮 Workflow cho user mới (sau fix)

1. Truy cập `https://yi-chronos` → bấm "Đăng nhập" → tab "✨ Đăng ký"
2. Nhập email + tên + password → "Tạo tài khoản" → tự đăng nhập
3. **OnboardingModal popup** → nhập tên + giới tính + ngày-giờ sinh dương lịch → "Lưu & bắt đầu"
4. **Banner** "⏳ Đang phân tích lá số của bạn bằng DeepSeek (~30s)..." hiện ra
5. Modal đóng. Background thread chạy 4 analyses (~25s).
6. User click tab **🌟 Tử Vi Lá Số** → ngay 4 panel có data đầy đủ:
   - 🪐 Cách cục (6-8 cách)
   - 🌗 12 Đại Vận
   - 📅 Lưu Niên 2026-2030
   - 📆 Lưu Nguyệt 12 tháng 2026
7. Click "📄 Xuất PDF" → tải báo cáo PDF chỉ chứa data của họ.

**Lần đăng nhập sau**: KHÔNG có modal, panel có sẵn data từ cache `u{N}/self/`. Zero friction.

**Cost**: ~$0.02 × số user (founder chịu — như Anh đã chọn).
