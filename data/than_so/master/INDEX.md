# Thần Số Học (Numerology) — Master Data Index

Knowledge base trường phái **Thần Số Học** cho YI-Chronos. Tính mệnh từ **TÊN + NGÀY SINH**.
Phái dẫn đầu: **Pythagoras**; đối chiếu: **Chaldean** (Iron Rule #3).
Paradigm: **đọc đồng dạng, KHÔNG predict** (Iron Rule #4/#6 — "Vạn vật là số").

## Files

| File | Nội dung |
|---|---|
| `letter_maps.json` | Bảng chữ cái → số (Pythagoras + Chaldean) + quy tắc Y nguyên/phụ âm + **bản địa hóa tiếng Việt** (bỏ dấu, Đ→D, không tách ghép phụ âm) |
| `core_numbers.json` | 6 số cốt lõi (Life Path, Expression, Soul Urge, Personality, Birthday, Maturity) + số mở rộng + **công thức** |
| `number_meanings.json` | Ý nghĩa 1-9 + master 11/22/33 (2 lớp: kinh điển Pythagoras + đồng dạng YI) |
| `karmic_debt.json` | Số nợ nghiệp 13/14/16/19 |
| `cycles.json` | Lớp BIẾN: Pinnacle / Challenge / Period Cycle / Personal Year-Month-Day + công thức |
| `sources_catalog.json` | Danh mục nguồn uy tín + cái còn thiếu cần đi tìm (bookflow v2.0) |

## Journal
`docs/design/than-sohoc-pythagoras-tham-nhuan.md` — thâm nhuần đầy đủ + khảo nguồn.

## Trạng thái
- v1 = data nghiên cứu (CƠ) ✅
- v2 = E2E ✅: engine `engine/than_so/`, API `/api/than-so/*`, sage `than-so-sage/SOUL.md`,
  wiki seed `scripts/wiki_seed_than_so.py`, tests `tests/test_than_so.py` (14 PASS).
- Chưa làm: UI Vue + restore sách gốc (chờ Anh).
