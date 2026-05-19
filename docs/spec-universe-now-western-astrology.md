# Spec: Universe Now — Nâng cấp lớp Chiêm tinh phương Tây

- **Tên ngắn:** `western-astro-v1`
- **Trạng thái:** spec đang mở, sẵn sàng triển khai
- **Tuần triển khai:** 2026-05-16 → 2026-05-22 (Day 5–6)
- **Owner kỹ thuật:** chưa gán (xem mục Handoff bên dưới)
- **Liên quan:** [weekly-plan-2026-05-16-to-2026-05-22.md](weekly-plan-2026-05-16-to-2026-05-22.md)

---

## 0) Cho người mới vào dự án — đọc trước

Spec này là một lớp **bổ sung** cho Trang 1 (Universe Now), không thay thế.
Nếu bạn lần đầu tham gia, đọc theo thứ tự:

1. [README.md](../README.md) — chạy được app cục bộ.
2. [deep-research-report.md](../deep-research-report.md) — bản sắc dự án (đặc biệt mục **"Physics first, symbolism later"**).
3. [docs/rulesets/bac_phai_v1.md](rulesets/bac_phai_v1.md) — ruleset Đông phương đang chạy.
4. **Spec này** — lớp Tây phương đang thêm.

**Không được hiểu sai:** dự án rõ ràng cấm **"app bói toán"**. Lớp chiêm tinh
phương Tây ở đây chỉ là **state mapping** (mô tả trạng thái bầu trời),
**không** dự đoán may rủi, tài lộc, sức khỏe, cái chết, v.v.

---

## 1) Mục tiêu

Trang 1 (Universe Now) đang chỉ hiển thị Kp + pha trăng + tiết khí. Nâng cấp
để hiển thị **toàn bộ trạng thái bầu trời theo trường phái chiêm tinh phương Tây**:

- Vị trí 10 thiên thể chính trong 12 cung Hoàng đạo (tropical zodiac).
- Aspect (góc) quan trọng giữa các thiên thể.
- Trạng thái retrograde.
- Phẩm vị (dignity) cơ bản của hành tinh trong cung.
- (Optional) Ascendant / Midheaven nếu người dùng cấp tọa độ + giờ.

Tất cả tính toán phải **deterministic 100%** từ thời gian UTC và tọa độ
quan sát.

---

## 2) Non-goals (rõ ràng)

- **Không** có "tử vi hôm nay", "lá số tốt xấu", lời khuyên cá nhân.
- **Không** dự đoán sự kiện (sẽ chết, sẽ giàu, sẽ bệnh...).
- **Không** kết hợp lớp này với personal layer ở phiên bản v1 (giữ tách biệt).
- **Không** hỗ trợ sidereal zodiac (Vedic) ở v1 — chỉ tropical.
- **Không** tính progression / solar return / synastry ở v1.

Lý do: tránh trượt thành "app bói toán", giữ ranh giới đã chốt trong blueprint.

---

## 3) Quyết định kỹ thuật (đã chốt sơ bộ — cần xác nhận)

| Quyết định | Lựa chọn | Lý do | Ai cần xác nhận |
|---|---|---|---|
| Thư viện ephemeris | `skyfield` (MIT) | License sạch, JPL DE440 chất lượng cao, không phụ thuộc network | Tech lead |
| Thư viện astrology phụ trợ | **Tự viết thin layer** (sign/aspect math đơn giản) | Tránh AGPL của Swiss Ephemeris | Tech lead, Legal |
| Zodiac system | Tropical (0° Aries = vernal equinox) | Chuẩn phổ biến nhất phương Tây | Đồng thuận |
| House system | Placidus (cho v1, optional feature) | Thông dụng nhất, nhưng chỉ tính khi có location + giờ | Tech lead |
| Aspect orbs | Conjunction 8°, Opposition 8°, Trine 6°, Square 6°, Sextile 4° | Convention phổ biến | Đồng thuận |
| Bodies in v1 | Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto + North/South Node | 10 hành tinh + nodes | Đồng thuận |
| Bodies bỏ qua v1 | Chiron, asteroids, Lilith, Arabic parts | Giảm phạm vi | Có thể thêm v2 |

**Thư viện thay thế nếu skyfield không phù hợp:**
- `astropy` (BSD) — heavy hơn nhưng đầy đủ.
- `pymeeus` (LGPL) — nhẹ, thuần Python.
- KHÔNG dùng `pyswisseph` / `flatlib-swisseph` vì AGPL.

---

## 4) Data model

### 4.1) `SkyBody`

```python
@dataclass
class SkyBody:
    name: str                    # "sun", "moon", "mercury", ...
    ecliptic_longitude: float    # 0–360°, geocentric apparent
    ecliptic_latitude: float     # ±, geocentric apparent
    sign: str                    # "aries", "taurus", ...
    sign_degree: float           # 0–30° within sign
    is_retrograde: bool
    speed_deg_per_day: float
    dignity: str | None          # "rulership"|"exaltation"|"detriment"|"fall"|None
```

### 4.2) `SkyAspect`

```python
@dataclass
class SkyAspect:
    body_a: str
    body_b: str
    aspect_type: str             # "conjunction"|"opposition"|"trine"|"square"|"sextile"
    angle_deg: float             # actual angular separation
    orb_deg: float               # difference from exact aspect
    applying: bool               # True nếu aspect đang siết (gần dần)
```

### 4.3) `SkyChart` (response chính)

```python
@dataclass
class SkyChart:
    timestamp_utc: str           # ISO 8601
    bodies: list[SkyBody]
    aspects: list[SkyAspect]
    moon_phase_name: str         # tái dùng từ chronos
    sun_sign: str                # rút gọn cho UI
    dominant_element: str        # "fire"|"earth"|"air"|"water" — đếm signs
    ascendant: SkyBody | None    # chỉ khi có location + time
    midheaven: SkyBody | None
```

---

## 5) API contract

### 5.1) Endpoint mới

```
GET /api/sky-now
```

**Query params:**
- `lat` (optional, float) — vĩ độ quan sát, để tính Ascendant/MC.
- `lon` (optional, float) — kinh độ quan sát.
- `at` (optional, ISO 8601 UTC) — mặc định = now.

**Response:** `SkyChart` JSON.

### 5.2) Mở rộng `/api/universe-now`

Thêm field mới (giữ nguyên fields cũ):

```json
{
  "...": "...",
  "sky": { ...SkyChart... }
}
```

**Backward compatibility:** clients cũ bỏ qua field `sky` vẫn hoạt động.

---

## 6) UI plan

### 6.1) Component mới

`client/webapp/src/components/SkyChartPanel.vue`

- Vẽ vòng tròn 12 cung (SVG đơn giản, không 3D).
- Đặt 10 hành tinh ở vị trí ecliptic longitude tương ứng.
- Vẽ đường aspect giữa các hành tinh (màu theo loại: hài hòa/căng).
- Hover hành tinh → tooltip: cung, độ, retrograde, dignity.
- Hover aspect → tooltip: loại + orb.

### 6.2) Vị trí trên Trang 1

```
[ Energy Weather Panel (cũ) ]
[ Hexagram Ring (cũ)        ]
[ Sky Chart Panel (MỚI)     ]   ← thêm
[ Stats summary             ]
```

### 6.3) Copy rules — bắt buộc tuân thủ

- Mô tả **trạng thái**, không mô tả **hệ quả**.
  - ✅ "Hỏa tinh vuông Thổ tinh — căng thẳng cấu trúc."
  - ❌ "Cẩn thận tai nạn hôm nay."
- Không dùng từ "may", "rủi", "xui", "hên", "tốt", "xấu".
- Cho người mới không biết chiêm tinh: nhãn nhỏ "đây là mô hình trạng thái".

---

## 7) Tests bắt buộc

| Test | Vị trí | Pass condition |
|---|---|---|
| Position spot check | `tests/test_sky_engine.py` | Sun ở 0° Aries lúc vernal equinox 2026 (±0.1°) |
| Retrograde detect | cùng file | Mercury retrograde detect đúng các cửa sổ đã biết của 2026 |
| Aspect orb | cùng file | 2 hành tinh cách nhau 91° → square với orb 1° |
| Determinism | cùng file | Cùng UTC + tọa độ → output bytes identical |
| Endpoint | `tests/test_api_sky.py` | `/api/sky-now` trả 200, schema khớp |
| Backward compat | `tests/test_api.py` | `/api/universe-now` cũ vẫn hoạt động khi không có `sky` |

---

## 8) Provenance & License

| Phụ thuộc | Phiên bản dự kiến | License | Ghi chú |
|---|---|---|---|
| `skyfield` | ≥1.46 | MIT | Cần tải JPL DE440 (~110MB), chứa trong `data/ephemeris/` (gitignore) |
| Math thin layer | tự viết | nội bộ | Thuật toán sign/aspect là kiến thức công cộng |

**Bắt buộc:**
- Thêm `data/ephemeris/` vào `.gitignore`.
- Tạo `scripts/download_ephemeris.sh` để tải DE440 lần đầu.
- Ghi rõ source ephemeris file trong response: `"ephemeris_source": "JPL DE440"`.

---

## 9) Risk matrix

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Trượt thành app bói toán | **Cao** | Copy rule mục 6.3 + code review checklist |
| License contamination (Swiss Eph AGPL) | Trung | Cấm import `pyswisseph`, lint rule |
| Tải DE440 chậm cho người mới | Thấp | Script download riêng, không bắt buộc cho dev test (mock được) |
| Tính toán Ascendant phụ thuộc location → privacy | Trung | Optional, không bắt buộc nhập, không log |
| UI 3D phức tạp khiến trễ tuần | Trung | v1 dùng SVG 2D, 3D để v2 |

---

## 10) Handoff & multi-party notes

**Cấu trúc commits/PR:**
- 1 PR = 1 mục trong section "Tests bắt buộc" hoặc 1 layer (engine / API / UI).
- Branch naming: `western-astro/<scope>` (ví dụ `western-astro/engine-core`).

**Thông tin tối thiểu khi bàn giao giữa thành viên:**
- File cuối cùng đã sửa.
- Test command chạy được pass cuối cùng.
- Quyết định mục 3 nào đã xác nhận (đánh dấu trong bảng).
- Câu hỏi mở (nếu có) ghi xuống mục 11 bên dưới.

**Người mới onboard:**
1. Clone repo, chạy `./scripts/dev-up.sh` xác nhận stack chạy.
2. Đọc spec này từ đầu.
3. Chạy `PYTHONPATH=. pytest tests/test_sky_engine.py -q` (sẽ fail nếu engine chưa làm xong — đó là normal).
4. Hỏi trong handoff doc gần nhất ai đang giữ phần nào.

---

## 11) Câu hỏi mở (cập nhật khi có)

- [ ] House system: Placidus có phải lựa chọn cuối, hay dùng Whole Sign cho v1?
- [ ] Có hiển thị fixed stars (Algol, Regulus...) ở v1 không?
- [ ] Aspect minor (semisextile, quincunx) v1 hay v2?
- [ ] Cách hiển thị độ chính xác trên UI: decimal hay degree-minute?
- [ ] Có thêm transit-to-natal khi user nhập ngày sinh? (Có khả năng vi phạm "no fortune-telling" — cần review carefully.)

---

## 12) Changelog spec

| Ngày | Thay đổi | Người |
|---|---|---|
| 2026-05-10 | Spec v1 khởi tạo | (chưa gán) |
