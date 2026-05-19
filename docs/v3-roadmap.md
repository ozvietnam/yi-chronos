# YI-CHRONOS Engine v3 Roadmap

**Status**: Active backlog from kanban council critique queue (2026-05-12)
**Owner**: anh + AI council
**Generated**: 2026-05-12, after applying 17 critiques in v2 cycle

This document tracks engine improvements suggested by sages during kanban council consultations. v2 (2026-05-12) applied 17 critiques covering Dụng Thần climate, Đại Vận pointer, Thần Sát 30+ stars, Tiểu Vận adult, cách cục alias, chronos convention flag, Hà Lạc nguyên đường rationale.

The items below are **deferred to v3** — they require larger engineering effort (corpus building, multi-school cross-references, hourly recasting). Each has open critique queue ID for traceability.

## v3 Priority Buckets

### 🟥 HIGH (do first)

| ID | Module | Effort | Description |
|---|---|---|---|
| #5 | `engine.ha_lac.cast` | 2-3 days | Inject Kinh Dịch text (Hán + Việt) per decade-trajectory stage. Requires building a hexagram-text corpus (64 quẻ × 6 hào). |
| #12 | `engine.lien_hoa.cross` | 1 day | Cross-reference với Bát Tự đại vận hiện tại trong KTS interpretation. |
| #13/#20 | `engine.mai_hoa.cast` | 2 days | Hourly quẻ generation (Quẻ Chánh / Hổ / Biến / hào động per hour). Requires NNTT cast for arbitrary moments + chuẩn hóa I/O. |
| #23 | `engine.lien_hoa.cast` | 1 day | Xung/hình/hại cross-check giữa Bát Tự gốc và ngày-giờ cast (đặc biệt cho Day Master nhược). |
| #28 | `engine.bat_tu.dung_than` | 2-3 days | **Dụng Thần v3** — thông căn (通根 xuyên thấu can-chi) + Tòng Cách + Hóa Khí Cách patterns. |

### 🟨 MEDIUM

| ID | Module | Effort | Description |
|---|---|---|---|
| #11 | `engine.lien_hoa.kts_chain` | 1 day | Cast KTS per hour cho hourly_fortune queries (hiện chỉ cast per event/timestamp). |
| #14 | `engine.mai_hoa.precaster` | 1 day | Lunar mansion (Nhị thập bát tú) + Không Vong per hour. |
| #21 | `engine.mai_hoa.hourly_fortune` | 0.5 day | Add `rationale` field cho hourly Cát/Bình/Hung (giải thích ngắn ngũ hành tương tác). |
| #22 | `engine.lien_hoa.hourly_narrative` | 0.5 day | Same as #21 nhưng cho Liên Hoa hourly. |

### 🟦 LOW

| ID | Module | Effort | Description |
|---|---|---|---|
| #24 | `engine.lien_hoa.hourly_breakdown` | 0.25 day | Thêm `day_pillar_shift_note` gần giờ chuyển Day Pillar. |

## v2 Resolved Summary (2026-05-12)

Critiques applied trong session này:

- **#1, #18**: Trường Sinh climate factor — merged into Dụng Thần v2 Điều Hậu.
- **#2, #8 (renumbered)**: Dụng Thần Điều Hậu — implemented 窮通寶鑑 climate matrix (10 stems × 4 seasons).
- **#3, #7, #16, #26**: Thần Sát expansion 15 → 30+ stars. Added Khôi Cương, Văn Khúc, Quốc Ấn, Kim Dư, Lưu Hà, Thiên La, Địa Võng, Tang Môn, Bạch Hổ, Điếu Khách, Thái Cực Quý Nhân, Phục Ngâm, Phản Ngâm.
- **#4**: tu_vi `cast_la_so` type coercion — fixed via `calculate_chronos_state` proper attribute access.
- **#6**: Hà Lạc nguyên đường rationale — every call now emits explanation note.
- **#9**: Tiểu Vận span 12 → 96 years + `current_tieu_van` field.
- **#10**: Day pillar convention flag — merged with #19.
- **#15**: cach_cuc null bug — added `cach_cuc_label` alias.
- **#17, #27**: `current_dai_van` + `next_dai_van` + `second_next_dai_van` pointer fields.
- **#19**: `chronos.day_pillar_convention = "julian_noon"` field added.
- **#25**: Trường Sinh per pillar — confirmed already exposed.

**Total tests**: 730+ green after all v2 changes.

## Process Notes

- Council queries via `/api/ai/council/kanban/consult` with `birth` param now self-document engine gaps.
- Auto-harvest from `task_runs.summary` parses `### improve_system` items into SQLite `engine_critiques.sqlite3`.
- Each fix manually marked resolved via `cs.resolve_critique(id, resolution=...)`.
- Run `GET /api/ai/council/critiques?status=open&priority=high` to see open backlog.

## v3 Sprint Plan (draft)

**Week 1**: #5 Kinh Dịch text corpus (HIGH, biggest unlocks)
**Week 2**: #28 Dụng Thần v3 (HIGH, depth multiplier)
**Week 3**: #13 Mai Hoa hourly cast (HIGH, unlocks hourly fortune)
**Week 4**: #12, #23, then cleanup MEDIUM items #11, #14, #21, #22

Total: ~10-14 engineering days for v3 cycle. Deliver as 1 major version bump per HIGH item.
