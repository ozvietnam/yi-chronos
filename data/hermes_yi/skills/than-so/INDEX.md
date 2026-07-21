---
name: than-so-index
description: Master index Thần Số Học — route intent → sách thư viện + data master. Load trước khi luận sâu có citation.
metadata:
  hermes:
    tags: [than_so, numerology, Index, AlwaysAvailable]
    routing_mode: short
  curated_at: 2026-07-21
---

# Thần Số Học — Master Index (thư viện dự án)

Cấu trúc:
- **Tier 1 (file này)** — luôn load khi cần Thần Số.
- **Tier 2** `thu-vien/*.md` — citation từ sách đã restore.
- **Data** `data/than_so/master/` — bảng máy (engine).

## Sách CÓ trong thư viện

| Intent | Route |
|---|---|
| Hòa / lệch Name↔Birth; 5 bước luận | `nguyen-ly.md` |
| Provenance bảng Pythagoras / nguyên âm / master 11/22 | `thu-vien/balliett.md` |
| Inclusion Table / Karmic Lessons / Hidden Passion | `thu-vien/campbell.md` |
| Chaldean / số kép 10–52 / hành tinh | `thu-vien/cheiro.md` |
| Công thức Decoz Method A (engine) | `data/than_so/master/pythagorean_spec.json` |
| Tương hợp multi-aspect | `data/than_so/master/compatibility_matrix.json` |

## Sách CHƯA có (đừng bịa nguyên văn)

- Juno Jordan — *Romance in Your Name* (1965, còn bản quyền)
- Matthew Goodwin — *Complete Guide* (1981, còn bản quyền)

→ Dùng Balliett (PD) làm provenance Jordan; Decoz web + spec cho công thức hiện đại.

## Engine hooks

- `engine/than_so/library.py` — tra compound Cheiro, provenance
- `extended.inclusion_table` — Campbell
- `cast.cross_reference` — Chaldean + số kép tên
