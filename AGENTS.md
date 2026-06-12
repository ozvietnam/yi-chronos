<claude-mem-context>
# Memory Context

# [yi] recent context, 2026-06-12 7:48pm GMT+7

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (19,478t read) | 2,483,596t work | 99% savings

### May 19, 2026
3153 10:03p 🔵 AuspiciousDayPanel mounted inside Mai Hoa MasterView tab, not standalone — calls /api/yi-wiki/auspicious-day
3154 " 🔵 AuspiciousDayPanel accessible via "Wiki Tổ sư" tab (🌌), not "Bát Tự" or "Mai Hoa" tab
3158 10:09p 🔵 AuspiciousDayPanel has NO role-based visibility gate — all logged-in users can access it
3159 " 🔵 Wiki Tổ sư tab IS owner-only — hidden inside v-if="isOwner" template block along with Lexicon, Research, Dịch sách, Admin
3160 10:17p ⚖️ Option B chosen: move AuspiciousDayPanel into BatTuPanel tab for user visibility
3161 " 🔵 AuspiciousDayPanel uses hardcoded form inputs — does NOT pull from activePerson store
3162 10:18p 🟣 AuspiciousDayPanel embedded in BatTuPanel — lịch vạn niên + tứ trụ now accessible to all users
S1505 Embed AuspiciousDayPanel into public BatTuPanel (completed) + explore birth_hour_quiz feature for potential improvement to AuspiciousDayPanel's birth hour input (May 19 at 10:18 PM)
S1502 Embed AuspiciousDayPanel (lịch vạn niên + tứ trụ) into public BatTuPanel so regular users can access it (May 19 at 10:18 PM)
S1517 Birth Hour Quiz v2 — Phase E/F completion + live test with founder's birth data (21h-24h, June 5, 1988) (May 19 at 10:22 PM)
3164 10:23p ⚖️ Upgrade birth_hour_quiz — Bát Tự-driven hypothesis comparison approach
3165 " 🟣 Birth Hour Quiz v2 design spec written — Bát Tự hypothesis comparison engine
3166 " ✅ Birth Hour Quiz v2 spec refined — K_PER_ROUND constant and early convergence edge case
3179 10:57p ⚖️ Birth Hour Quiz V2 — Hypothesis-Comparison Architecture Design
3217 11:00p 🟣 Quiz Engine: Strategy Detection + Entropy-Ranked Question Generation
3218 " 🔴 Fix test_value_labels_are_vietnamese: Use ord(ch) > 127 Instead of Narrow Charset
3219 " 🟣 Candidate Pillars Generator Using Real Bát Tự Engine
3220 " 🟣 Phase C Complete: Birth Hour Quiz V2 Engine Layer — 60 Tests All GREEN
3180 11:10p 🟣 Birth Hour Quiz v2 — Full Implementation Plan Written
3221 11:52p 🟣 Phase D–F Task Breakdown Created: Session Store, API Endpoints, Vue Frontend
3222 11:53p 🟣 Full Task Breakdown Complete: 23 Tasks Covering All Phases 0–G
3223 " 🟣 SQLite Session Store for Birth Hour Quiz V2
3224 11:54p 🟣 Task D.1 Complete: SQLite Session Store — 5/5 Tests GREEN, Committed
3225 " 🔵 API Structure: schemas.py Pattern and main.py Import Layout for Phase E
3226 " 🟣 Pydantic Schemas Added to api/schemas.py for Birth Hour Quiz V2
3227 11:55p 🔵 api/main.py Structure: 5323 Lines, SPA Mount at End, Yi-Wiki Endpoints at ~3426
3235 " 🔴 Birth Hour Quiz v2 GET session endpoint response schema fixed
3236 " 🟣 Birth Hour Quiz v2 — 4 FastAPI endpoints shipped (Phase E)
3237 " 🟣 BirthHourQuizV2.vue component created — 4-stage state machine UI
3238 " 🔵 QuickTasksPanel.vue contains v1 birth hour quiz — integration point for v2 upgrade
3239 11:59p 🟣 QuickTasksPanel quiz modal upgraded from v1 to BirthHourQuizV2 component
### May 20, 2026
3242 12:00a 🔴 BirthHourQuizV2 import added to QuickTasksPanel — build verified clean
3249 12:05a 🔄 QuickTasksPanel v1 quiz dead code removed — script cleaned up
S1518 Founder submitting partial quiz answers for Birth Hour Quiz v2 — mapping physical/behavioral traits to Tý vs Hợi candidates (May 20 at 12:05 AM)
3268 12:20a 🟣 Birth Hour Quiz v2 — Live Integration Test with Founder's Real Birth Data
S1519 Founder requests minute-level birth time rectification within giờ Tý — "lập bài test xem kỹ sinh chính xác lúc mấy phút" (May 20 at 12:25 AM)
3269 12:27a 🔵 Birth Hour Quiz v2 — Founder's Real Case Returns Tý (23h-1h) with High Confidence
3270 " 🔵 Bat Tu Pillars Stable Across Full Tý Hour Window (23:00–00:59) for 1988-06-05
3271 " 🔵 Dai Van Engine Returns Data Under Different Key Names Than Expected
S1520 Founder confirms 2 life milestone events (married 2016, graduated 2010) and asks feasibility of minute-level birth time rectification (May 20 at 12:29 AM)
S1521 Birth minute rectifier PoC run + honest feasibility verdict — founder asks if minute-level precision is achievable (May 20 at 12:34 AM)
S1523 Design decision: qualitative early-Tý vs late-Tý contrast questionnaire to refine birth minute within giờ Tý (May 20 at 12:34 AM)
3272 12:34a 🔵 Founder's Full Đại Vận Chain Confirmed — Starts Age 4, 8 Cycles Through Age 83
3279 12:35a ⚖️ Birth Minute Rectification — Paradigm Shift from Math to Qualitative Contrast
S1522 Founder proposes qualitative contrast approach for birth minute refinement — split Tý window and use adjacent cung trait blending instead of math (May 20 at 9:20 AM)
S1524 Qualitative "Tý đầu vs Tý cuối" contrast questionnaire designed and presented to founder for self-identification (May 20 at 9:27 AM)
3290 9:30a ⚖️ Founder Self-Identifies as Early Tý (23h-00h) — Confirms Hợi Residue Profile
3305 9:35a 🟣 Chi Giờ Wiki — All 12 Hour Branches Seeded with Core Data
3306 9:43a 🟣 Chi Giờ Wiki — Full JSON Schema + All 12 Hour Branch Data Files + Loader API Built
### May 22, 2026
3766 11:29a 🟣 Chiếu Đởm Kinh 18 Phi Tinh — 12 image-generation prompt files created for Priority 2 and 3 cards
3767 " 🔵 Codex image generation for Phi Tinh oracle cards — 18 PNG files confirmed in local cache
3768 5:44p 🟣 Book Translation UI Redesign — Task Scoped
3769 " 🔵 YI-CHRONOS Publishing System — Codebase Architecture Mapped
3770 5:45p 🔵 PublishingWorkspace.vue — Current 3-Pane Architecture (2346 lines)
3771 " 🔵 Raw PDF and Restored Book Directories Are Nearly Empty
3772 " 🔵 MinerU Pipeline Data Layout and Book Discovery Mechanism
### May 28, 2026
3781 3:39p 🔵 movis 0.7.1 incompatible with Python 3.14 — numpy 0-d array TypeError
3782 " 🟣 OZSlide Movis template created at shared/oz_slide.py
3783 " 🔴 movis LayerItem has no set_opacity() — use solid layered rectangles instead
3784 " 🔵 Vietnamese TikTok logistics/customs education niche has no existing creator using dark+neon+info-card template

Access 2484k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>

## Runtime Execution Policy (User Preference)

- Prefer external model APIs first for heavy processing and large-batch workloads.
- Reserve Cursor model/token usage for hard reasoning, architecture decisions, and complex problem solving.
- Keep API keys in `.env.local` only (never commit secrets into repository files).