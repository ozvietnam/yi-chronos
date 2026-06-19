# ADR — Ví Xu TRUNG TÂM ở YI (single source of truth) + parity YI-web

> Ngày: 2026-06-19 · Trạng thái: **CHỐT (Anh duyệt)** · Phạm vi: YI-Chronos (ví) + AppChat (đổi sang dùng ví YI).
> Bối cảnh: AppChat đã build ví Xu trên Firestore (`functions/src/xu/*`, 1 xu=1.000₫). Anh chốt:
> **YI là ví trung tâm cho CẢ HAI kênh** (AppChat + YI-web), không double-charge, không lệch số dư.

## 1. Quyết định
- **YI = nguồn chân lý** của số dư xu (Postgres/SQLite qua `engine.db`, dual-driver).
- Mọi **cộng/trừ THẬT** nằm ở YI (`engine/xu_wallet.py`). AppChat **không tự trừ ở Firestore nữa** — chỉ hiển thị + mở luồng nạp.
- **YI-web parity:** user web YI dùng đúng một ví đó (endpoint authed).
- Hằng số khớp AppChat: **1 xu = 1.000₫ · quick 1 / council 5 / deep 99 · free quick 3/ngày · login +10 xu/ngày trong cửa sổ 30 ngày**.

## 2. Mô hình thu phí (đã wire vào Hermes)
`engine/hermes_service._gate` (quick + council):
```
gói VIP (subscriptions) → 'paid'  (không trừ xu)
  else còn lượt free/ngày → 'free' (ratelimit)
  else TIÊU XU (atomic, ví trung tâm) → 'xu'
  else → 'denied' reason=insufficient_xu  (client mời nạp)
```
- **Tiêu xu atomic** (`xu_wallet.spend`, advisory-lock per-user như `llm_spend.try_charge`) → nhiều request đồng thời không tiêu quá số dư.
- **Cache "một việc một lần" (Iron #4)**: cache hit xảy ra TRƯỚC `_gate` ⇒ KHÔNG trừ xu lần hỏi lại.
- **Hoàn xu** nếu sau khi trừ mà không serve được: vượt ngân sách LLM (`budget_exceeded`) hoặc LLM lỗi → `xu_wallet.grant(refund)`.
- Response `done` khi tier=`xu` kèm `xu_cost` + `xu_balance`; tier=`free` kèm `free_remaining`.

## 3. Data model (`engine/xu_wallet.py`)
- `xu_wallet(user_id PK, balance, daily_last_claim, created_at, updated_at)` — số dư.
- `xu_ledger(ts, day, user_id, delta, reason, balance_after, ref)` — sổ cái append-only (audit tiền; `ref` = vd RevenueCat txn id). Không PK tự tăng → portable SQLite/PG (như `llm_spend`).
- API engine: `get_balance`, `grant`, `spend` (→`{ok,balance,need,have}`), `daily_bonus_decision` (thuần), `claim_daily`.

## 4. Endpoint
**Kênh AppChat (service-keyed, `X-API-Key`):**
| Endpoint | Việc |
|---|---|
| `GET /api/sync/wallet/{firebase_uid}` | số dư + `xu_cost` + `free_quick_remaining` |
| `POST /api/sync/wallet/grant {firebase_uid, amount, reason, ref}` | nạp/tặng (sau RevenueCat/IAP đã verify ở AppChat) |
| `POST /api/sync/wallet/claim-daily {firebase_uid}` | tặng xu đăng nhập |

**Kênh YI-web (authed user):** `GET /api/wallet` · `POST /api/wallet/claim-daily`.

> KHÔNG có endpoint "spend" rời — spend chỉ xảy ra TRONG luồng Hermes (chống double-charge / gọi lậu).

## 5. Hợp đồng cho AppChat (việc dev prvchat phải đổi)
1. **Bỏ trừ xu cục bộ**: `spendXu` Firestore không còn là nguồn chân lý. Trừ xu do YI làm khi gọi Hermes → đọc `xu_balance`/`xu_cost` trong kết quả `done` để cập nhật UI.
2. **Nạp**: webhook RevenueCat/IAP (đã verify) → gọi `POST /api/sync/wallet/grant` (truyền `ref`=transaction id để idempotency). Cập nhật Firestore.xu = giá trị YI trả về (chỉ để hiển thị/cache).
3. **Login bonus**: `claimDailyXu` gọi `POST /api/sync/wallet/claim-daily` thay vì tự cộng Firestore.
4. **Hết xu**: callable Hermes nhận `denied/insufficient_xu` (YI) → map `failed-precondition(insufficient_xu)` → client mở màn nạp (giữ UX đã build).
5. **Số free quick**: nguồn chân lý là YI (free 3/ngày). AppChat không tự đếm free nữa.

## 6. Còn lại (follow-up)
- **Free numbers**: YI hiện `FREE_DAILY_QUICK=10`, `FREE_DAILY_COUNCIL=3`. Parity AppChat = quick **3**, council **0**. Đổi 2 hằng số (test dùng hằng số động → an toàn) — chờ Anh chốt con số cuối.
- **YI-web UI ví (Vue)**: hiển thị số dư + nút nhận xu hằng ngày + luồng nạp — parity với AppChat (chưa làm, task riêng).
- **deep-reading**: wire spend 99 xu vào `engine/deep_reading` (giống quick/council) — chưa làm trong slice này.

## 7. Test
`tests/test_xu_wallet.py` (12) · `tests/test_hermes_xu_gating.py` (4: free→xu, denied, refund, council 5 xu) · `tests/test_wallet_api.py` (6). Toàn bộ PASS dual-driver (SQLite; PG qua `YI_TEST_PG_DSN`).
