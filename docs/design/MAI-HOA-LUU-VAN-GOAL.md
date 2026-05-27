# GOAL — Mai Hoa Lưu Vận + Nhật Ký Trải Nghiệm Cá Nhân

> **🔒 IRON RULE — KHÔNG QUÊN**
> Anh giao cho em (Claude) 2026-05-27 đêm.
> File này là **mục tiêu dài hạn** — em đọc lại đầu mỗi phiên có liên quan.

---

## 🎯 Vision dài hạn (CỐT)

Xây dựng **hệ thống Mai Hoa Lưu Vận + Nhật Ký** đúng paradigm Khang Tiết, để Anh có thể:

1. **Ghi lại** các việc lớn-nhỏ trong đời thực (deals, decisions, sự kiện gia đình, etc.)
2. **Đối chiếu** với 7 vòng quẻ Mai Hoa tại thời điểm tương ứng
3. Sau **1 tháng / 6 tháng / 1 năm / nhiều năm** → **tìm ra mối liên hệ thực**:
   - Việc loại X có ứng với cấu trúc quẻ Y không?
   - Cùng quẻ Lưu Nguyệt → trải nghiệm cùng pattern?
   - Thể-Dụng tỉ hoà → ngày bình; Thể bị khắc → ngày trở ngại thực?
4. **Giải nghĩa trải nghiệm Anh qua quẻ** — chứng minh hoặc bác bỏ paradigm Tổ sư bằng **DỮ LIỆU THỰC** của 1 đời người.

→ Đây là **khoa học nhỏ trong nhà** — không phải fortune-telling. Tổ sư cũng muốn thế (Q3 "lý chỉ dị minh, sát kỳ cơ").

---

## 📐 ĐỊNH NGHĨA — "7 vòng quẻ" cho cá nhân

Mỗi vòng = 1 lớp paradigm theo Tam Tài + chu kỳ thời gian.

| # | Vòng | Input | Đổi mới khi | Phạm vi |
|---|---|---|---|---|
| **1** | **Quẻ Khởi Sinh** (cố định) | Năm + Tháng + Ngày + Giờ SINH | Không bao giờ đổi | "Tượng" khoảnh khắc Anh sinh ra |
| **2** | **Lưu Niên** (năm hiện tại) | Năm hiện tại + Tháng + Ngày + Giờ SINH | Đầu năm âm | Tượng năm hiện tại Anh đi qua |
| **3** | **Lưu Nguyệt** | Năm hiện tại + Tháng hiện tại + Ngày + Giờ SINH | Đầu tháng âm | Tượng tháng |
| **4** | **Lưu Nhật** | Năm + Tháng + Ngày HIỆN TẠI + Giờ SINH | 23:00 (giờ Tý) đầu ngày mới | Tượng ngày |
| **5** | **Lưu Thời** | Năm + Tháng + Ngày + Giờ HIỆN TẠI (12 chi giờ) | Mỗi 2 tiếng | Tượng thời điểm vũ trụ chiếu vào Anh |
| **6** | **Quẻ Vũ trụ hiện tại** | Năm + Tháng + Ngày + Giờ HIỆN TẠI (KHÔNG có sinh thần) | Mỗi 2 tiếng | Tượng vũ trụ "đang rung" — chung cho mọi người |
| **7** | **Quẻ Cộng hưởng Tam Tài** | Cộng số gieo của vòng 1 (Khởi Sinh) + vòng 6 (Vũ trụ) | Mỗi 2 tiếng | Tượng giao thoa Anh × vũ trụ |

→ **Vòng 1**: "tượng" — KHÔNG dùng để predict đời, chỉ tham chiếu cấu trúc gốc.
→ **Vòng 2-5**: paradigm cá nhân theo chu kỳ — đổi theo thời gian.
→ **Vòng 6**: paradigm vũ trụ thuần — KHÔNG cá nhân hóa.
→ **Vòng 7**: paradigm Tam Tài = Anh × Vũ trụ.

---

## 🎯 GOAL CẤP 1 — Engine + API + UI (foundation)

**Em làm phase này TRƯỚC. Anh duyệt rồi mới phase tiếp.**

### G1.1 — Engine `engine/yi_wiki/luu_van.py`

7 hàm tương ứng 7 vòng:

```python
cast_que_khoi_sinh(birth) -> CastResult
cast_luu_nien(birth, year_chi_current) -> CastResult
cast_luu_nguyet(birth, year_chi_current, month_current) -> CastResult
cast_luu_nhat(birth, date_current) -> CastResult
cast_luu_thoi(birth, date_current, hour_chi_current) -> CastResult
cast_que_vu_tru(date_current, hour_chi_current) -> CastResult
cast_que_cong_huong(birth, date_current, hour_chi_current) -> CastResult
```

+ 1 hàm tổng hợp:
```python
quan_sat_luu_van(birth, datetime_current) -> dict[7 quẻ + Thể-Dụng + giao thoa]
```

### G1.2 — Engine `engine/yi_wiki/giao_thoa.py` (quan hệ 2 quẻ)

```python
giao_thoa(quẻ_A, quẻ_B) -> dict:
    {
        "the_A_vs_the_B": "tỉ hoà | A sinh B | A khắc B | B sinh A | B khắc A",
        "ngu_hanh_summary": "Thổ-Thổ tỉ hoà — bình thuận",
        "paradigm_note": "đọc đồng dạng, KHÔNG nói cát/hung tĩnh"
    }
```

Đặc biệt cần:
- Giao thoa Khởi Sinh × Lưu Niên (paradigm năm cộng hưởng với Anh)
- Giao thoa Khởi Sinh × Lưu Nguyệt
- Giao thoa Khởi Sinh × Vũ Trụ hiện tại
- Giao thoa Lưu Niên × Lưu Nguyệt (paradigm trong năm)

### G1.3 — API endpoints

```
GET /api/yi-wiki/luu-van/snapshot?birth=YYYY-MM-DD-HH:MM&at=<now>
  → 7 quẻ + giao thoa
GET /api/yi-wiki/luu-van/vu-tru-now
  → Quẻ Vũ trụ giờ hiện tại (không cần birth)
GET /api/yi-wiki/luu-van/timeline?birth=...&from=...&to=...&grain=day|week|month
  → Series của Lưu Nhật/Nguyệt qua thời gian (cho đồ thị)
```

### G1.4 — UI Dashboard `LuuVanDashboard.vue`

3 view:

**View A — Snapshot bây giờ**: 7 quẻ ngang hàng + giao thoa lưới
- KHÔNG có "điểm cát/hung"
- HIỂN THỊ: tên quẻ, cấu trúc, Thể-Dụng, hành Ngũ hành, mùa
- Tooltip: link sang HexagramBrowser detail của quẻ đó

**View B — Đồ thị 12 tháng** (Lưu Nguyệt × 12 tháng âm năm hiện tại):
- Y-axis: 8 trigram (Càn → Khôn) — KHÔNG phải điểm số
- Mỗi tháng = 1 cột thể hiện: Thượng quái + Hạ quái + Thể-Dụng vs Khởi Sinh
- Hiển thị **quan hệ Ngũ hành** (tỉ hoà / sinh / khắc) với màu đặc trưng (KHÔNG đỏ/xanh fortune)

**View C — Nhật ký** (G2 dưới — phase sau):
- Anh gắn việc thực vào timestamp
- Hiển thị quẻ Lưu Nhật/Thời tương ứng

---

## 🎯 GOAL CẤP 2 — Nhật ký việc thực + tag

**Sau khi G1 xong, Anh duyệt, mới làm G2.**

### G2.1 — Schema nhật ký

```sql
CREATE TABLE nhat_ky_van (
    id INTEGER PRIMARY KEY,
    user_id TEXT,             -- founder hoặc shared user
    happened_at INTEGER,      -- unix timestamp
    title TEXT,               -- "Ký deal X", "Họp gia đình", "Privacy incident"
    body TEXT,                -- nội dung dài
    tags TEXT,                -- JSON: ["deal", "thuan", "tieu_su_kien"]
    importance INTEGER,       -- 1-5 (việc nhỏ → việc lớn)
    sentiment TEXT,           -- "thuan", "nghich", "binh", "kho_phan_loai"
    outcome TEXT,             -- ghi sau khi việc đã xong
    luu_van_snapshot_json TEXT,  -- snapshot 7 quẻ tại thời điểm happened_at
    created_at INTEGER,
    updated_at INTEGER
);
```

→ Mỗi entry **TỰ ĐỘNG snapshot 7 quẻ** vào thời điểm `happened_at`.
→ Sau khi việc xong, Anh update `outcome` + `sentiment` (manual).

### G2.2 — UI nhật ký

- Form ghi: title + time + tags + importance
- Hiển thị quẻ snapshot ngay khi save (User thấy paradigm tại đó)
- Sau đó user quay lại update `outcome` khi việc xong

### G2.3 — Tag preset (paradigm-correct, KHÔNG cát/hung)

```
Loại việc: deal | gia_đình | sức_khỏe | sang_tao | quyết_định_lớn | crisis | hằng_ngày
Sentiment outcome (Anh tự gán SAU): thuan | nghich | bình | chưa rõ
Importance: 1 (nhỏ) → 5 (định mệnh)
```

❌ KHÔNG dùng tag "cát" / "hung" — đó là kết luận, không phải dữ liệu.

---

## 🎯 GOAL CẤP 3 — Pattern mining + Giải nghĩa

**Đây là việc KHÓ NHẤT. Cần ≥ 6 tháng dữ liệu mới làm được.**

### G3.1 — Mỗi entry nhật ký được match với 7 quẻ tại thời điểm đó

Sau N tháng tích lũy → có DataFrame:

| happened_at | việc | importance | outcome_sentiment | Khởi Sinh | Lưu Niên | Lưu Nguyệt | Lưu Nhật | Lưu Thời | Vũ trụ | Cộng hưởng |
|---|---|---|---|---|---|---|---|---|---|---|

### G3.2 — Pattern mining (auto + manual review)

Phân tích:
- **Pattern 1 — Sentiment vs Thể-Dụng giao thoa**: Việc có sentiment "thuan" có Thể-Dụng tỉ hoà nhiều hơn không?
- **Pattern 2 — Quẻ Lưu Nguyệt lặp**: Cùng quẻ Lưu Nguyệt qua các năm → trải nghiệm pattern giống nhau?
- **Pattern 3 — Hào động ứng**: Hào Lưu Nhật khi việc to xảy ra — có ý nghĩa gì?
- **Pattern 4 — Cộng hưởng Tam Tài**: Quẻ Cộng hưởng vs Khởi Sinh → tỉ hoà nhiều có chính là "ngày thuận" thực?

### G3.3 — Validation

❌ **CẤM**: kết luận "quẻ X = cát" từ dữ liệu (đó vẫn là fortune-telling).

✅ **PHẢI**: kết luận paradigm **"quan sát thấy pattern Z"** với N data points. Để Anh quyết có dùng hay không.

→ Goal cuối: viết **báo cáo paradigm** sau 1 năm: "Theo 100+ entry nhật ký, em quan sát thấy: X / Y / Z. Tổ sư Khang Tiết Q3 nói... — có khớp / không khớp."

---

## 🛑 CẤM (paradigm Tổ sư)

| Cấm | Vì sao |
|---|---|
| ❌ Daily reading "hôm nay tốt/xấu" | Iron Rule #4 — KHÔNG predict tĩnh |
| ❌ Auto bói cho 1 việc cụ thể mà không có nghi user | "Bất nghi bất bốc" Q3 tr.49 |
| ❌ Điểm số cát/hung trên đồ thị | Không phải dữ liệu, là kết luận sai paradigm |
| ❌ "Quẻ Bản Mệnh quyết định đời Anh" | Khang Tiết Tam Tài — Anh + vũ trụ NGANG NHAU, không bị quyết |
| ❌ Auto-generate quẻ Anh "phải sống theo" | Quan vật trace tính, không phải mệnh lệnh |
| ❌ Chỉ làm UI đẹp mà không giải paradigm trong tooltip/help | User sẽ hiểu sai → thành fortune app |

---

## 📜 Iron Rule references

- **Iron Rule #4** (CLAUDE.md): Mai Hoa = đọc đồng dạng, không predict
- **Iron Rule #5** (CLAUDE.md): Bookflow v2.0 — không "FINAL" → vận hành tốt cho hệ thống live + cập nhật pattern
- **Iron Rule #7** (CLAUDE.md): Privacy — nhật ký việc thực = data nhạy cảm, gate ownerOnly

---

## 🗺️ Roadmap

| Phase | Việc | Effort | Anh duyệt? |
|---|---|---|---|
| **0** | Viết GOAL này (file đang đọc) | ✅ DONE 2026-05-27 đêm | ✅ commit |
| **1A** | Engine luu_van.py + giao_thoa.py | ~3h | chờ |
| **1B** | API endpoints luu-van/* | ~1h | chờ |
| **1C** | UI Dashboard 3 view (Snapshot + 12 tháng + nhật ký skeleton) | ~4h | chờ |
| **1D** | Wire Quẻ Vũ trụ giờ hiện tại + xóa Daily reading cũ (sai paradigm) | ~1h | chờ |
| **2A** | Schema + API nhật ký | ~2h | sau phase 1 |
| **2B** | UI ghi + update outcome | ~3h | sau phase 1 |
| **3** | Pattern mining (sau ≥ 6 tháng dữ liệu) | ~5h (1 lần) | sau ≥ 6 tháng |

→ **Phase 1** (1A + 1B + 1C + 1D) = ~9h. Em làm liền sau khi Anh OK GOAL.

---

## 📌 NHẮC EM — KHÔNG QUÊN

1. Anh CẤM em "ứng vào việc em làm" như em đã sai hôm 27-05.
2. Mọi quẻ phải tham chiếu nguồn Tổ sư (Trình Di / Chu Hy / Khang Tiết Q1-5 / Trần Đoàn / 64 quẻ deep) — KHÔNG bịa.
3. Phải có tooltip paradigm cho mỗi quẻ hiển thị — để user (Anh + người khác) hiểu, không tự áp.
4. Đọc file này lại MỖI PHIÊN có động đến Mai Hoa lưu vận.
5. Anh sẽ kiểm tra: sau khi em làm, Anh thử ghi 1 việc thực + xem quẻ snapshot có đúng paradigm Khang Tiết không.

---

_"Quan vật chí huyền chí vi, lý chỉ dị minh."_ — Trần Đoàn

_"Một việc bói một lần. Không nghi không bói."_ — Khang Tiết Q3

— Em (Claude), 2026-05-27 đêm, ghi nhận trong sổ "không được quên".
