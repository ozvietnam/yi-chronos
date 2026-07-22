# Thần Số — Campbell thâm nhuần Vòng P0 (stub + audit Inclusion)

> Nguồn trong repo: `data/restored_books/campbell-your-days-are-numbered/content.md` (~43 dòng method)  
> ⚠️ Bản quyền tới **2027-01-01** — chỉ method facts; **không** restore/publish nguyên văn.  
> Ngày: 2026-07-22 · Kế hoạch: `than-so-thu-vien-KE-HOACH-THAM-NHUAN.md`

---

## 1. Trung thực về độ sâu

Stub mô tả: Inclusion Table → Hidden Passion (trội) / Karmic Lessons (thiếu); procedural “lập kế hoạch theo số”.  
**Không** có chữ chương trong repo → P0 = audit engine khớp method facts công khai + stub, không thâm nhuần nguyên văn.

---

## 2. Audit engine (2026-07-22) — PASS

Hàm: `extended.inclusion_table` · `karmic_lessons` · `hidden_passion` · `subconscious_self`

| Kiểm | Kết quả |
|---|---|
| `inclusion.missing` ≡ `karmic_lessons.values` | ✅ mọi fixture thử |
| `inclusion.dominant` ≡ `hidden_passion.values` (tie = nhiều số) | ✅ kể cả `John` (4 số cùng max) |
| `sum(frequency) == letter_count` | ✅ |
| VN strip dấu: `Nguyễn Văn An` → NGUYENVANAN | ✅ (11 chữ; thiếu 2,6,8,9; passion 5) |
| `Mary Ann Smith` → thiếu 3,6; passion 1 | ✅ |
| Subconscious = 9 − |lessons| | ✅ (Decoz standard; stub Campbell không phủ nhận) |
| Tone deep_reading | ✅ “chưa tập / đam mê” — không dọa nghiệp |

### Gap đã vá ở P0

1. **Intensity average** — Inclusion hiện đại đọc theo trung bình `letter_count/9` (above/below). Engine trước chỉ missing/dominant → thêm `average`, `above_average`, `below_average` (method fact, không copy sách).
2. Tests siết: đồng bộ lessons↔inclusion; case tie passion; empty name.

### Gap còn mở (P1+ / chờ 2027 hoặc method-only sâu hơn nếu Anh OK)

- Ngưỡng “Secret Desire = average+1” (trường phái Intensity Table hiện đại) — chưa wire như số riêng (tránh phình SKU).
- Personal cycles trong Campbell textbook vs Decoz Personal Y/M/D — giữ Decoz trong `cycles.json`; ghi M2.
- Không publish PDF nguyên văn trước 2027.

---

## 3. Đừng nhầm (giữ cứng)

| Campbell Lessons | Karmic Debt 13/14/16/19 |
|---|---|
| Số 1–9 **thiếu** trong tên | Bước trung gian khi rút |
| Phẩm chất chưa tập | Mất cân bằng cần quan-sát |

---

## 4. Insights P0

1. Inclusion = **bản đồ luyện**, không điểm tốt/xấu.
2. Passion tie (nhiều số cùng max) hợp lệ — đừng ép 1 số.
3. Tên ngắn → nhiều lessons + nhiều passion tie — đọc “ít chữ = ít mẫu” chứ không “số phận mỏng”.
4. Procedural grimoire: Campbell “plan by number” ↔ YI IMPROVE theo khí năm/tháng Decoz — cùng tinh thần, khác công thức (#3).

---

## 5. Hệ quả inject

- [x] Journal P0
- [x] Enrich `inclusion_table` average bands
- [x] Tests consistency
- [x] Skill campbell.md link P0
- [ ] P1+ sau PD / Anh cho phép method sâu hơn
