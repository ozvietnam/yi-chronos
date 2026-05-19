# TuViAnalyzer — Công thức phân tích lá số tự vận hành

> _"Có gì đào được thì em đào hết đi, rồi viết công thức cho những người khác.
> Hoặc chuẩn bị data để hệ thống tự vận hành được nhé."_ — Anh, 2026-05-19

Hệ thống Tử Vi của YI giờ là **engine generic**: thêm bất kỳ ai vào → chạy
được 8 phép phân tích, cache vào đĩa, đọc lại không tốn $.

---

## 1. Kiến trúc

```
                   ┌──────────────────────────────────────────┐
                   │  TuViAnalyzer(person, force=False)       │
                   │  engine/tu_vi/analyzer.py                │
                   └──────────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
  cast_la_so()              DeepSeek (deepseek-chat)         cache JSON
  engine/tu_vi/an_sao.py    api.deepseek.com/v1              data/yi_publishing/
                                                              analysis_cache/
                                                                {person_key}/
                                                                  cach_cuc.json
                                                                  dai_van.json
                                                                  luu_nien_*.json
                                                                  luu_nguyet_*.json
                                                                  synastry_*.json
                                                                  phu_match.json
                                                                  phu_reading.json
                                                                  cach_deep_*.json
```

**Mỗi phép phân tích** = method trên class `TuViAnalyzer`. Mỗi method:
1. Check cache → trả về nếu có và `force=False`
2. Lấy `chart_summary` (human-readable rendering của lá số)
3. Gọi DeepSeek (JSON output) với system prompt + chart context
4. Lưu kết quả vào `analysis_cache/{person_key}/<kind>.json`
5. Trả dict đầy đủ kèm `generated_at`, `cost_usd`, `person_key`

---

## 2. 8 phép phân tích

| Kind | Method | Cost/lần (DeepSeek) | Output |
|---|---|---|---|
| `cach_cuc` | `discover_cach_cuc()` | ~$0.0015 | 6-8 cách cục kinh điển + bằng chứng |
| `dai_van` | `dai_van_annotate()` | ~$0.008 | 12 đại vận × (tổng quan + cơ hội + thách thức + lời khuyên) |
| `luu_nien` | `luu_nien(2026, 2030)` | ~$0.004 (5 năm) | Vận năm + tiểu hạn + đại vận đan xen |
| `luu_nguyet` | `luu_nguyet(2026)` | ~$0.007 | 12 tháng âm với tính chất + việc nên / tránh |
| `synastry` | `synastry(other_analyzer)` | ~$0.003 | Đối chiếu 2 chart (vợ chồng, partner) |
| `phu_match` | `phu_match()` | $0 (manual scoring) | Top passages Phú Thái Vi match chart |
| `phu_reading` | `phu_reading(top_n=5)` | ~$0.005 | DeepSeek personalize top N passages |
| `cach_cuc_deep` | `cach_cuc_deep(cach_id)` | ~$0.002 | Đào sâu 1 cách cụ thể |

**Total full pipeline 1 người: ~$0.03**. Cache thì chỉ tốn 1 lần.

---

## 3. API endpoints

### Generic (recommended)

```bash
# POST: chạy phân tích (cast → DeepSeek → cache → return)
POST /api/tu-vi/analyze/{kind}
{
  "person_key": "wife",                      # cache namespace (required if no auth person)
  "birth_datetime_local": "1990-03-01T05:45:00",
  "gender": "nữ",                            # "nam" / "nữ"
  "name": "Vợ Anh",                          # optional display name
  "timezone": "Asia/Ho_Chi_Minh",            # default
  "luu_nien_start": 2026,                    # cho kind=luu_nien
  "luu_nien_end": 2030,
  "luu_nguyet_year": 2026,                   # cho kind=luu_nguyet
  "phu_top_n": 5,                            # cho kind=phu_reading
  "force": false                             # bypass cache
}

# Nếu có session đăng nhập + đã add person vào /api/auth/my/persons:
# truyền person_key (snake-case của tên) → engine tự load birth_datetime + gender từ DB.

# GET: chỉ đọc cache (KHÔNG chạy nếu chưa có)
GET /api/tu-vi/analyze/{person_key}/{kind}
```

`{kind}` ∈ `cach_cuc | dai_van | luu_nien | luu_nguyet | synastry | phu_match | phu_reading`

### Legacy (founder-only — vẫn giữ để Vue panels cũ chạy được)

| Path | Tương đương generic |
|---|---|
| `GET /api/yi-publishing/dai-van/founder` | `GET /api/tu-vi/analyze/_founder/dai_van` |
| `GET /api/yi-publishing/luu-nien/founder` | `GET /api/tu-vi/analyze/_founder/luu_nien` |
| `GET /api/yi-publishing/luu-nguyet-2026/founder` | `GET /api/tu-vi/analyze/_founder/luu_nguyet` |
| `GET /api/yi-publishing/phu/founder-reading` | `GET /api/tu-vi/analyze/_founder/phu_reading` |
| `GET /api/yi-publishing/anh-deep-analysis` | `GET /api/tu-vi/analyze/_founder/deep_analysis` |

Tất cả legacy endpoints **đã refactor đọc cache mới** (`analysis_cache/_founder/<kind>.json`)
với fallback sang đường cũ nếu chưa migrate. Nghĩa là `DaiVanPanel.vue`, `LuuNienPanel.vue`
chạy bình thường, không cần đổi gì.

---

## 4. Công thức thêm 1 người mới

### 4.1 Qua UI (khuyến nghị)

1. Login → tab **👨‍👩 Người thân**
2. Add person: nhập tên + ngày sinh + giờ + giới tính
3. (Future) Click **"Phân tích đầy đủ"** → trigger `analyzer.run_all()` background

### 4.2 Qua API (ad-hoc, không cần login)

```bash
# 1. Cách cục
curl -X POST http://localhost:8000/api/tu-vi/analyze/cach_cuc \
  -H 'Content-Type: application/json' \
  -d '{"birth_datetime_local":"1990-03-01T05:45:00","gender":"nữ","person_key":"wife","name":"Vợ Anh"}'

# 2. Đại vận
curl -X POST http://localhost:8000/api/tu-vi/analyze/dai_van \
  -H 'Content-Type: application/json' \
  -d '{"birth_datetime_local":"1990-03-01T05:45:00","gender":"nữ","person_key":"wife"}'

# 3. Lưu niên 5 năm
curl -X POST http://localhost:8000/api/tu-vi/analyze/luu_nien \
  -H 'Content-Type: application/json' \
  -d '{"birth_datetime_local":"1990-03-01T05:45:00","gender":"nữ","person_key":"wife","luu_nien_start":2026,"luu_nien_end":2030}'

# 4. Lưu nguyệt 12 tháng
curl -X POST http://localhost:8000/api/tu-vi/analyze/luu_nguyet \
  -H 'Content-Type: application/json' \
  -d '{"birth_datetime_local":"1990-03-01T05:45:00","gender":"nữ","person_key":"wife","luu_nguyet_year":2026}'

# 5. Đọc lại bất kỳ (GET, không tốn $)
curl http://localhost:8000/api/tu-vi/analyze/wife/cach_cuc
curl http://localhost:8000/api/tu-vi/analyze/wife/dai_van
curl http://localhost:8000/api/tu-vi/analyze/wife/luu_nien_2026_2030
curl http://localhost:8000/api/tu-vi/analyze/wife/luu_nguyet_2026
```

### 4.3 Qua Python REPL

```python
from engine.tu_vi.analyzer import TuViAnalyzer, Person

wife = TuViAnalyzer(Person(
    person_key="wife",
    name="Vợ Anh",
    birth_datetime_local="1990-03-01T05:45:00",
    gender="nữ",
))

# Chạy lẻ
wife.discover_cach_cuc()      # 6-8 cách
wife.dai_van_annotate()        # 12 đại vận
wife.luu_nien(2026, 2030)
wife.luu_nguyet(2026)

# Hoặc chạy hết
result = wife.run_all(
    luu_nien_start=2026, luu_nien_end=2030,
    luu_nguyet_year=2026,
    phu_top_n=5,
)
print(result.keys())
# dict_keys(['cach_cuc', 'dai_van', 'luu_nien_2026_2030', 'luu_nguyet_2026', 'phu_match', 'phu_reading'])

# Synastry với chồng
husband = TuViAnalyzer(Person(
    person_key="_founder",
    name="Anh Founder",
    birth_datetime_local="1988-06-05T23:30:00",
    gender="nam",
))
syn = husband.synastry(wife)
```

---

## 5. Cache structure

```
data/yi_publishing/analysis_cache/
├── _founder/                              # anh (CEO)
│   ├── cach_cuc.json                      # ← cũ: _cach_cu_nhat_founder.json
│   ├── dai_van.json                       # ← cũ: _dai_van_founder.json
│   ├── luu_nien.json                      # ← cũ: _luu_nien_founder.json
│   ├── luu_nguyet.json                    # ← cũ: _luu_nguyet_2026_founder.json
│   ├── phu_matches.json                   # ← cũ: _phu_matches_founder.json
│   ├── phu_reading.json                   # ← cũ: _phu_reading_founder.json
│   └── deep_analysis.json                 # ← cũ: _anh_deep_analysis.json
└── wife/                                  # vợ
    ├── cach_cuc.json
    ├── dai_van.json
    ├── luu_nien_2026_2030.json
    └── luu_nguyet_2026.json
```

Force re-run: pass `force=true` trong POST body hoặc `Person(..., force=True)` trong Python.

---

## 6. Files chính

| File | Vai trò |
|---|---|
| `engine/tu_vi/analyzer.py` | Generic `TuViAnalyzer` class — 8 methods + caching |
| `engine/tu_vi/an_sao.py` | An sao + tính 12 cung + tứ hóa + tiểu hạn |
| `core/chronos.py` | Lunar conversion (dùng cho `_cast_chart`) |
| `engine/yi_publishing/translator.py` | DeepSeek client provider |
| `api/main.py` | `/api/tu-vi/analyze/{kind}` (POST/GET) + legacy founder routes |
| `data/yi_publishing/analysis_cache/{person_key}/` | Cache JSON output |

---

## 7. Smoke test end-to-end (verified 2026-05-19)

```bash
# Restart API
.venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Wife: full pipeline ~25s, total cost $0.020
curl -X POST http://localhost:8000/api/tu-vi/analyze/cach_cuc -H 'Content-Type: application/json' \
  -d '{"birth_datetime_local":"1990-03-01T05:45:00","gender":"nữ","person_key":"wife","name":"Vợ Anh"}'
# → status:ok, 6 cách, $0.0015

curl -X POST http://localhost:8000/api/tu-vi/analyze/dai_van  -d '{"birth_datetime_local":"1990-03-01T05:45:00","gender":"nữ","person_key":"wife"}' -H 'Content-Type: application/json'
# → status:ok, 12 annotations, $0.0079

curl -X POST http://localhost:8000/api/tu-vi/analyze/luu_nien -d '{"birth_datetime_local":"1990-03-01T05:45:00","gender":"nữ","person_key":"wife","luu_nien_start":2026,"luu_nien_end":2030}' -H 'Content-Type: application/json'
# → status:ok, 5 years, $0.0035

curl -X POST http://localhost:8000/api/tu-vi/analyze/luu_nguyet -d '{"birth_datetime_local":"1990-03-01T05:45:00","gender":"nữ","person_key":"wife","luu_nguyet_year":2026}' -H 'Content-Type: application/json'
# → status:ok, 12 months, $0.0067

# Đọc lại — không tốn $
curl http://localhost:8000/api/tu-vi/analyze/wife/luu_nguyet_2026
```

---

## 8. Roadmap kế tiếp

- **UI**: thêm dropdown chọn person trong `UserBadge` → các panel tự load theo `person_key`
- **Auto-run**: khi add person mới → POST background `run_all`
- **Lưu nguyệt nhiều năm**: hiện chỉ 1 năm/lần, cần extend cho timeline N năm
- **PDF export**: 1-click xuất "Báo cáo lá số" PDF (cách cục + đại vận + lưu niên năm hiện tại)
- **Notifications**: gần Hóa Kỵ / cảnh báo lưu niên → email/push

---

_Đồng tác giả engine: Anh + Em, 2026-05-18 → 19._
_Tinh thần: Tử Vi không phải predict — là phản chiếu cấu trúc thân-trời. Mọi chữ DeepSeek viết ra phải đi qua mắt người đọc._
