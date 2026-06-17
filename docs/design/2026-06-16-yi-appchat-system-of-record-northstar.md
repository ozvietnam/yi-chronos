# YI ↔ AppChat — Sổ cái mệnh lý & Mặt phẳng tính năng (NORTH-STAR)

> **Ngày:** 2026-06-16 · **Người chốt:** Anh (CEO).
> **Mục đích:** chốt 1 lần cho đúng — để mọi tính năng tương lai (gieo duyên, công việc,
> luận đoán 1 việc theo Kinh Dịch, luận sâu DeepSeek, thông báo theo tuần, Hermes) có
> **chỗ ngồi đúng** trong kiến trúc, và **mọi tương tác của user được lưu thành lịch sử**.
> **Nền:** kế thừa `docs/design/2026-06-16-user-data-architecture-research.md` (tầng lưu trữ
> + PDPL) + `prvchat/docs/superpowers/plans/2026-06-14-tuvi-gieoduyen-profile-matching-spec.md`
> (§5bis hợp đồng nguồn-sự-thật).

---

## 0. Tuyên ngôn kiến trúc (1 câu)

**YI = SỔ CÁI (system of record)** của toàn bộ mệnh lý + lịch sử + trí nhớ user.
**AppChat = CỬA SỔ (window)** — đăng nhập, nhập liệu, đẩy thông báo, hiển thị tóm tắt.
**Web YI = PHÒNG TRƯNG BÀY (rich view)** — luận giải dài, ảnh minh họa đẹp, lịch sử đầy đủ.

> Hệ quả bất biến: AppChat **không bao giờ** tự sinh / tự đông cứng diễn giải mệnh lý.
> Nó *gọi* YI và *hiển thị*. Mọi diễn giải mang `algoVersion` (xem §5bis spec gieo duyên) →
> YI nâng cấp data giữa tuần → user thấy bản mới. "Mỗi tuần một khám phá" là **tính năng**, không phải bug.

---

## 1. Tin tốt — bộ xương đã có sẵn trong YI (không build lại)

Theo Iron Rule #1, đây là kiểm kê cái đã tồn tại, KHÔNG dựng mới:

| Nhu cầu Anh nêu | Đã có | Vị trí |
|---|---|---|
| Lưu **mọi lần hỏi / lá số / quẻ** thành lịch sử | bảng `user_castings` (method, question, input_json, result_json, verdict, tags, note, created_at) + API `/my/castings` (save/list/delete) | `api/auth.py` |
| Lưu **lá số đã so khớp** (gieo duyên) | bảng `user_favorites` kind=`couple_match` + API `/my/favorites` | `api/auth.py` |
| **Gói trả phí** + **DeepSeek luận sâu rất dài** | bảng `user_subscriptions` + `FEATURE_CATALOG` (`tu_vi_phe_menh_sau` = DeepSeek Pro ~30-40k chữ; `tu_vi_cdk_luan_cung`) + `check_access`/`consume_use`/`grant` | `engine/subscriptions.py` |
| **Hermes ngầm** hiểu user, trả lời, phản biện | memory layer: `user_facts` + `chat_summaries` (FTS5) + `glossary_views` + `build_memory_context()` | `engine/yi_hermes/memory.py` |
| Tài khoản AppChat ⇄ YI **đồng bộ** | khoá `firebase_uid` + `/api/sync/upsert-from-firebase` + `/resolve` | `api/sync.py` |
| Đẩy thông báo về máy user | Cloud Function `notifyUser` (HTTP, `X-API-Key`) → FCM `userDevices` | `prvchat` PR #23 |

→ Việc còn lại **không phải xây mới**, mà là **NỐI** các mảnh này qua cầu, **chuẩn hoá lịch sử**, và **bịt khoảng trống** (§4).

---

## 2. Mặt phẳng tính năng (feature surface) — tất cả chảy về 1 mô hình

Mỗi tính năng = một **"reading"** (một lần YI luận cho user). Tất cả dùng CHUNG:
lưu vào `user_castings`/`user_favorites`, gắn `yi_user_id` (↔ `firebase_uid`), mang `algo_version`.

| # | Tính năng | `method` / `kind` | Trạng thái | Đầu vào | Lưu lịch sử ở |
|---|---|---|---|---|---|
| F1 | **Lá số Tử Vi / Bát Tự** | `tu_vi` / `bat_tu` | ✅ cast LIVE (PR #23/#31) | birth | `user_castings` |
| F2 | **Gieo duyên** (so khớp tình duyên) | `couple_match` | 🟡 spec xong, chờ G1–G4 | 2 birth | `user_favorites` |
| F3 | **Công việc / sự nghiệp** | `tu_vi` cung Quan/Tài + lưu vận | 🔜 sau | birth + năm xét | `user_castings` |
| F4 | **Luận đoán 1 việc theo Kinh Dịch** | `luc_hao` / `mai_hoa` | 🔜 sau | câu hỏi + thời điểm/quẻ | `user_castings` |
| F5 | **Luận sâu DeepSeek (rất dài)** | feature `tu_vi_phe_menh_sau` | ✅ engine có, chờ nối bridge | chart đã cast | `user_castings` (kết quả dài) + sub `consume_use` |
| F6 | **Hermes hỏi-đáp / phản biện** | chat session | ✅ memory có, chờ nối bridge | hội thoại + chart + history | `chat_summaries` + `user_facts` |
| F7 | **Thông báo theo tuần** (gói tháng) | digest | 🔜 sau (§3) | toàn bộ history + new discoveries | log gửi |

> **Nguyên tắc "không bỏ sót":** bất kỳ tính năng nào mới thêm về sau (xem ngày tốt, đặt tên,
> phong thuỷ…) **bắt buộc** map vào `user_castings`/`user_favorites` với 1 `method`/`kind` mới —
> KHÔNG được tạo store riêng lẻ. Đó là cách lịch sử user luôn ở 1 nơi.

---

## 3. Vòng đời gói trả phí → thông báo theo tuần (F7)

Đây là chỗ 3 mảnh có sẵn ghép lại thành cái Anh muốn:

```
User mua gói tháng (AppChat IAP / web)
   → grant_subscription(user_id, feature, tier=vipX, expires_at=+30d)   [subscriptions.py — CÓ]
   → user dùng tính năng: check_access() gate + consume_use()           [CÓ]

CRON hằng tuần (server VN, gắn cùng auto-sync 23:30):
   với mỗi user có sub enabled & chưa hết hạn:
     1. Quét cái MỚI tuần này:
        - algo_version của engine có bump? (data YI nâng cấp → diễn giải mới)
        - lưu vận: sang tuần/tháng âm mới → cung lưu niên/lưu nguyệt đổi
        - Hermes phát hiện fact/insight mới từ history
     2. Sinh "digest" ngắn (1-3 ý) — KHÔNG luận đầy ở notdif, chỉ teaser
     3. notifyUser(uid, type="yi", payload={kind:"weekly_digest", deeplink})  [CF — CÓ]
   → user mở AppChat → deep-link → đọc tóm tắt → "Xem đầy đủ trên web YI" (ảnh đẹp + luận dài)
```

Quy tắc: **digest = teaser**, bản đầy đủ (ảnh minh họa, luận dài) sống ở **web YI** (phòng trưng bày).
Free user vẫn cast được cơ bản; **luận sâu + digest tuần là quyền lợi gói trả phí** (gate qua `check_access`).

---

## 4. Khoảng trống cần bịt (việc thực thi, theo thứ tự)

> Mỗi mục theo Iron Rule #1 (tận dụng cái có) + test discipline (`tests/test_*.py`).

| ID | Việc | Repo | Ghi chú |
|---|---|---|---|
| **H1** | ✅ Cast qua bridge **tự lưu** lịch sử + đóng dấu `algo_version` — `POST /api/sync/castings` + `POST /api/sync/favorites` (service-keyed) | yi-chronos | DONE 2026-06-17 (`api/sync.py`); cột `user_castings.algo_version` + migration idempotent |
| **H2** | ✅ API đọc lịch sử hợp nhất cho AppChat: `GET /api/sync/history/{firebase_uid}` (gộp castings + favorites, mới nhất trước, phân trang, lọc `method`/`kind`/`type`) | yi-chronos | DONE 2026-06-17 (`api/sync.py`) |
| **H3** | ✅ `GET /api/version` (algo_version + per-method) + helper `engine/algo_version.py` đóng dấu mọi reading | yi-chronos | DONE 2026-06-17 — trục của §5bis freshness; kế thừa `core.config.ALGORITHM_VERSION` |
| **H4** | ✅ Gieo duyên G1–G4 (nạp âm/cung mệnh Bát Trạch, tuổi hợp, tuổi cưới, compat-batch) — hàm thuần, mỗi response đóng dấu `algo_version` | yi-chronos | DONE 2026-06-17 — `engine/bat_tu/gieo_duyen.py` + 4 endpoint `/api/bat-tu/{profile-derived,compatible-years,marriage-years,compat-batch}`; kết quả lưu qua H1 (`couple_match`) |
| **H5** | Nối **luận sâu DeepSeek** (F5) qua bridge: callable `deepReading` → `check_access` → engine → lưu castings → `consume_use` | cả 2 | job dài → async + trạng thái "đang luận" |
| **H6** | Nối **Hermes** (F6) qua bridge: callable `askHermes` đọc memory + history + chart, trả lời/phản biện; ghi `chat_summaries`+`user_facts` | cả 2 | đây là "vũ khí bí mật" — xem §5 |
| **H7** | CRON digest tuần (F7) + gate gói tháng | yi-chronos | §3 |
| **H8** | AppChat UI: tab **Lịch sử** (đọc H2) + màn **Hermes chat** + badge gói | prvchat | cửa sổ |

---

## 5. Hermes — vũ khí bí mật (không được quên)

Hermes **không phải chatbot trả lời suông**. Nó là agent per-user, đứng TRÊN sổ cái:

- **Đọc** được: chart facts (deterministic từ engine, KHÔNG bịa) + history (`user_castings`) +
  memory (`user_facts`, `chat_summaries`, `glossary_views`) + tri thức sách (wiki → RAG).
- **Làm** được (Anh nêu): luận giải, trả lời, **so sánh & phản biện** (đa trường phái — Iron Rule #3),
  và "rất nhiều thứ khác" → mỗi việc mới = 1 skill route trong `data/hermes_yi/skills/`.
- **Càng dùng càng hiểu user**: mỗi phiên → `add_summary` + chưng cất `add_fact` →
  `build_memory_context()` bơm vào phiên sau. Đây là lý do "lưu hết lịch sử" sống còn —
  **history là nhiên liệu của Hermes**, không phải kho chết.
- **Guardrail bất biến** (Iron Rule #4/#6/#8): đọc đồng dạng, **không tiên tri**; "mệnh là động từ".
  Hermes luận "cấu trúc này VẬN HÀNH tốt nhất khi…", không phán "anh sẽ giàu/nghèo".

> Vì Hermes đọc PII + suy luận đời tư → khi gọi LLM ngoài (DeepSeek/Anthropic) **bắt buộc
> pseudonymize** (gửi facts + chart ẩn danh, KHÔNG uid/tên/sđt) + consent + hồ sơ chuyển dữ liệu
> (PDPL — xem doc research §2). Ưu tiên model in-country khi đủ chất lượng.

---

## 6. Ranh giới dữ liệu (nhắc lại — sống còn)

| Tầng | Bản chất | Ai sinh | Lưu ở | Quy tắc |
|---|---|---|---|---|
| Chart facts (sao/cung/cục, tứ trụ, quẻ) | sự thật deterministic | **engine YI** | `user_castings.result_json` | KHÔNG để LLM bịa |
| Lịch sử tương tác | append-only | app→YI | `user_castings`/`user_favorites` | lưu HẾT, gắn version |
| Memory ("hiểu user") | giả định mềm | LLM chưng cất | `yi_hermes/memory` | có confidence, cho user đính chính |
| Identity (uid/sđt/email) | nhạy cảm | Firebase | `users` (VN) | gate owner/self; pseudonymize khi gọi LLM ngoài |

---

## 7. Sơ đồ tổng

```
 AppChat (cửa sổ)            Cloud Functions (giấu key)         YI (sổ cái, server VN)        Web YI (trưng bày)
 ─────────────────          ──────────────────────────         ──────────────────────        ─────────────────
 đăng nhập ───────────────► syncYiProfile ──────────────────► /api/sync (firebase_uid)
 nhập birth                                                    users + persons
 cast F1/F3/F4 ───────────► castChart ───────────────────────► engine + LƯU user_castings ◄── lịch sử đầy đủ
 gieo duyên F2 ───────────► (G1–G4) ─────────────────────────► engine + LƯU couple_match  ◄── ảnh đẹp, luận dài
 luận sâu F5 ─────────────► deepReading (gate sub) ───────────► DeepSeek + LƯU + consume_use
 hỏi Hermes F6 ───────────► askHermes ──────────────────────► Hermes(memory+history+RAG)
 tab Lịch sử ─────────────► GET /api/my/history ◄─────────────┘
 nhận digest F7 ◄────────── notifyUser ◄───── CRON tuần (gói tháng) ── quét algo_version + lưu vận + insight
```

---

## 8. Việc kế tiếp đề xuất

Thứ tự ưu tiên để có giá trị sớm mà không nợ kỹ thuật:
**H3** (version contract — nền freshness) → **H1+H2** (lịch sử chảy + đọc được) →
**H4** (gieo duyên) → **H5** (luận sâu) → **H6** (Hermes) → **H7** (digest tuần) → **H8** (UI).

> Doc này là **trục**. Khi bắt tay từng H#, tạo plan chi tiết riêng (TDD), cross-ref về đây.
