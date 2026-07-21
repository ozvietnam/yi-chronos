# Thần Số Học (Numerology) — Master Data Index

Knowledge base **Pythagoras (Decoz)** cho YI-Chronos. Tính mệnh từ **TÊN + NGÀY SINH**.
Paradigm: **đọc đồng dạng, KHÔNG predict**.

## Files

| File | Nội dung |
|---|---|
| **`library_provenance.json`** | Map sách thư viện ↔ engine hooks |
| **`compatibility_matrix.json`** | Ma trận tương hợp 1–9 |
| **`pythagorean_spec.json`** | **SPEC ĐÓNG BĂNG v1** — Decoz Method A, inventory P0, golden fixtures |
| `letter_maps.json` | Bảng chữ cái Pythagoras (+ Chaldean đối chiếu) + bản địa hóa VN |
| `core_numbers.json` | Định nghĩa 6 số cốt lõi + mở rộng |
| `number_meanings.json` | Ý nghĩa 1-9 + master 11/22/33 |
| `karmic_debt.json` | Nợ nghiệp 13/14/16/19 |
| `cycles.json` | Pinnacle / Challenge / Period / Personal YMD |
| `sources_catalog.json` | Danh mục nguồn |
| `cross_bind_dong_phuong.json` | (opt-in) đối chiếu Đông phương — không thuộc pipeline P0 |

## Engine

`engine/than_so/` — schema **v2**:
- Core: per-name-part Expression/Soul/Personality (Decoz)
- Extended: Attitude, Balance, Rational Thought, Lessons, Passion, Subconscious, Cornerstone/Capstone, Bridges, Planes, Minor
- Cycles: Challenges bỏ Master; Period timing 27 năm; Personal M/D; Transit/Essence/Duality/Age Digit

## Journal

`docs/design/than-sohoc-pythagoras-tham-nhuan.md`

## Trạng thái

- v1–v4: data + E2E tối thiểu + UI + cross-bind
- **v5 (2026-07-21)**: Decoz P0 complete chart — golden fixtures + extended + cycles đầy đủ
- **v6 (2026-07-21)**: deep reading + PDF + lịch 24 tháng + UI một nguồn API
- **v7–v8 (2026-07-21)**: transit timeline, method audit, năm/ngày window, glossary UI, sage SOUL v2
- **v9 (2026-07-21)**: Expression name-audit (per-part vs flat), PDF đủ timeline/deep, xoá PytagoEnergyPage
- **v10 (2026-07-21)**: SKU tương hợp multi-aspect + WeasyPrint PDF (fpdf2 fallback)
- **v11 (2026-07-21)**: thư viện Balliett/Campbell/Cheiro → compound 10–52, Inclusion Table, skills
- **v12 (2026-07-21)**: thâm nhuần nguyên lý → deep_reading Name↔Birth + Cheiro layers + synthesis
