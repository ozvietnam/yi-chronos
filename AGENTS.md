<claude-mem-context>
# Memory Context

# [yi] recent context, 2026-05-12 5:45pm GMT+7

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (17,528t read) | 1,208,334t work | 99% savings

### May 11, 2026
S1309 Hội Đồng Tư Vấn Trí Tuệ (Sages Council) — complete backend AI layer with FastAPI endpoints, tests, and live verification (May 11 at 6:31 PM)
S1311 User asked about embedding autonomous self-improving agents (Hermes for skill dev, MeiCurry for memory) into the yi project to run 24/7 — primary session responded with full backend status recap (May 11 at 6:37 PM)
S1312 User asked about embedding autonomous self-improving agents (Hermes for skill dev, MeiCurry for memory) into yi project — primary session designed a 3-tier autonomous agent architecture called YI-CHRONOS Observer (May 11 at 6:49 PM)
S1314 User asked about installing a Hermes agent for user reception, profiling, module mapping, Vietnamese glossary, and Socratic questioning — primary session designed 3-tier autonomous agent architecture (Observer/Self-correcting/Self-improving) and awaits user decisions (May 11 at 6:50 PM)
S1313 User proposed a dedicated Hermes agent for yi project (user reception, profiling, module mapping, Vietnamese glossary, Socratic questioning) — primary session evaluated feasibility and designed a 3-tier autonomous agent architecture (May 11 at 8:11 PM)
S1315 User confirmed Hermes agent concept — primary session delivered full architectural design for a 5-role meta-layer agent (Concierge + Profile Builder + Module Librarian + Vietnamese Glossary + Blind Spot Skill Generator) with 3-phase build plan (May 11 at 8:20 PM)
S1316 User asked whether to use Hermes (custom agent) or Trae AI — primary session clarified these serve completely different roles and are not mutually exclusive (May 11 at 8:21 PM)
S1317 User confirmed Hermes as in-app agent, asked about API key requirements and whether to build parallel UX (self-service + bot) — primary session delivered full UX design with auto-mode-decision and 3-phase build plan (May 11 at 8:26 PM)
S1318 YI-Hermes chat engine glossary lookup improvements + intent detection fixes + full verification sweep (May 11 at 8:35 PM)
2360 8:41p 🟣 yi_hermes Module Librarian Implemented — Anti-Hallucination Knowledge Index for 7 Schools
2361 8:44p 🟣 Vietnamese Divination Glossary Seed — 46 Hand-Curated Terms Across 7 Schools
2362 8:45p 🟣 GlossaryStore SQLite Backend Implemented — Full CRUD + Fuzzy Search for Vietnamese Divination Terms
2363 " 🟣 yi_hermes Concierge System Prompt Written — Vietnamese-First Persona with Anti-Hallucination Rules
2364 8:52p 🔴 Intent detection greeting false-positive on Vietnamese terms containing "hi"
2365 " 🔴 Glossary lookup extended to "question" intent for short messages
2366 " 🔴 Vietnamese question suffix ordering fixed to longest-first in glossary lookup
2367 9:39p 🔵 NousResearch/hermes-agent identified as top GitHub result for "hermes agent"
2368 " 🔵 Existing Hermes Agent installation found: v0.12.0, 604 commits behind main
2369 " ✅ Created vendor/ and data/hermes_yi/ directories in yi project for Hermes integration
2370 " ✅ NousResearch/hermes-agent cloned into vendor/hermes-agent at HEAD (includes v0.13.0)
2371 " 🔵 Hermes Agent v0.13.0 "Tenacity Release" — major upgrade from installed v0.12.0
2372 9:40p ✅ Isolated Python venv created inside vendor/hermes-agent for Hermes v0.13.0 install
2373 " ✅ Hermes Agent v0.13.0 installed successfully in vendor venv (editable mode)
2374 " 🟣 Hermes Agent v0.13.0 running isolated inside yi project with project-local HERMES_HOME
2375 9:41p 🟣 Dual Hermes isolation confirmed — Mac v0.12.0 and YI v0.13.0 run independently with separate project paths
2376 " 🟣 Created scripts/hermes-yi — wrapper script for YI-CHRONOS isolated Hermes Agent
2377 " 🟣 scripts/hermes-yi wrapper verified working — full v0.13.0 command surface available
2378 " 🔵 Hermes doctor reveals YI Hermes needs .env config and provider auth to be functional
2379 9:42p ✅ Created docs/hermes-agent-setup.md — full setup guide for YI-CHRONOS isolated Hermes Agent
2380 " 🔵 vendor/ directory NOT in .gitignore — vendored Hermes venv would be committed to git
2381 " ✅ Updated .gitignore to exclude Hermes venv, pyc files, and sensitive data/hermes_yi/ contents
S1319 User asked to find latest Hermes on GitHub and install it — completed: NousResearch/hermes-agent v0.13.0 installed isolated in vendor/ alongside existing Mac Hermes v0.12.0 (May 11 at 9:42 PM)
### May 12, 2026
2482 5:17p 🔵 Yi Project Structure — Vietnamese Astrology Web App
2483 " 🔵 Yi-Chronos Frontend is Minimal Vue/Vite SPA with Only Two Source Files
2484 5:18p 🔵 Yi-Chronos Frontend is Actually a Rich Multi-Panel Vue App with Three.js and 25+ Components
2485 " 🔵 Full UI Asset Map: HexagramImage Expects SVG Files from /que-images/, Two Three.js Canvases, Multiple Inline SVG Charts
2486 " 🔵 Dev Stack Is Live; Hexagram SVGs Exist Only in dist/, Not in public/ — HexagramImage May 404 in Dev Mode
2487 " 🔵 All 64 Hexagram SVGs Are Correctly in public/que-images/ — Prior 404 Concern Was Unfounded
2488 5:19p 🔵 Playwright ESM Named Import Fails — Must Use Default Import Destructuring on Node v22
2493 " ⚖️ Upgrade Task Prioritization: Tasks 1 & 2 First
2496 5:26p 🔵 Yi App: Vue.js Divination Platform with Multi-Tab Architecture
2497 " ⚖️ Yi App UI Upgrade Plan: 4-Step Mobile-First Refactor
2499 " 🔵 lucide-vue-next v0.468.0 Already Installed; Icons Bundled in Single CJS File
2500 " 🔵 Yi Project docs/ Contains Active Roadmap and Upgrade Planning Documents
2502 5:27p 🔵 All 15 Planned Lucide Replacement Icons Confirmed Available in Bundle
2504 5:28p 🟣 SchoolIcon Component Created; Emoji Tabs Replaced with Lucide Icons; Mobile Responsive CSS Fixed
2505 5:29p 🟣 Yi App Production Build Passes After Icon + Responsive CSS Upgrade
2506 " 🟣 Playwright QA: Desktop and Mobile Pass — No Horizontal Overflow, Tab Navigation Functional
2507 5:30p ⚖️ Kế hoạch nâng cấp: Ưu tiên làm nhiệm vụ 1 và 2 trước
2508 " 🔵 Yi App mobile UI kiểm tra bố cục - không có tràn ngang, tab scroll rộng hơn viewport
2509 5:31p ⚖️ Upgrade Task Ordering: Tasks 1 & 2 Prioritized First
2510 5:32p ⚖️ Ưu tiên thực hiện nhiệm vụ 1 và 2 trước, ghi kế hoạch nâng cấp theo thứ tự
2512 " ✅ Icon Selection Rejected by User — Previous Version Preferred
2511 5:34p 🟣 UI visual upgrade: responsive topbar, icon tabs, và Playwright screenshot kiểm tra
2513 5:39p ⚖️ User Feedback: Icon Selection Regression
2514 5:40p 🔵 Yi App UI State: Tab Icon Uses Clipboard Emoji After Icon Change
2515 " 🔵 Yi App Vite Build: Large JS Bundle Warning
2516 " 🔴 Tab icon alignment fix in yi webapp main navigation
2517 5:42p 🔴 Tab alignment fix verified — no horizontal overflow at 1600px viewport
2518 " 🔵 Yi webapp tab bar visual state confirmed post-CSS fix

Access 1208k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>

## Runtime Execution Policy (User Preference)

- Prefer external model APIs first for heavy processing and large-batch workloads.
- Reserve Cursor model/token usage for hard reasoning, architecture decisions, and complex problem solving.
- Keep API keys in `.env.local` only (never commit secrets into repository files).