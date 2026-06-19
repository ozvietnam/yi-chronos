# SPEC — Đồng bộ ví Xu AppChat ↔ YI (YI = nguồn chân lý) + kế hoạch chuyển đổi

> Ngày: 2026-06-19 · Trạng thái: **CHỐT (Anh duyệt)** · Repo: YI-Chronos (canonical) + prvchat (tiêu thụ).
> Nền: ADR `2026-06-19-ADR-vi-xu-trung-tam.md` (quyết định) + PR yi-chronos#54 (engine `xu_wallet` + gating + API).
> Doc này là **bản đồng bộ trọn vẹn**: hợp đồng dữ liệu, luồng, **kế hoạch migration cắt-chuyển**, idempotency,
> đối soát, ca biên, checklist go-live. Mục tiêu tối thượng: **một nguồn chân lý, không trừ trùng, không cộng trùng,
> không mất số dư cũ.**

---

## 1. Nguyên tắc (không được vi phạm)
1. **YI là nguồn chân lý** của số dư xu (`xu_wallet` + sổ cái `xu_ledger`). AppChat Firestore `users/{uid}.xu` xuống cấp thành **bản mirror chỉ-đọc/hiển thị**.
2. **Trừ xu CHỈ xảy ra ở YI**, trong luồng Hermes (`hermes_service._gate` → `xu_wallet.spend`). Không có nơi nào khác trừ. AppChat **bỏ** `spendXu`.
3. **Cộng xu (nạp/tặng) idempotent theo `ref`** — webhook RevenueCat retry / migration chạy lại không cộng trùng.
4. **Fail-closed**: YI lỗi/không với tới → AppChat KHÔNG được tự trừ/tự cộng cục bộ (sẽ lệch). Báo "thử lại", không serve.
5. **Cache "một việc một lần" (Iron #4)** không tính phí lần hỏi lại; **hoàn xu** nếu trừ rồi mà không serve được (budget/LLM lỗi).
6. **Tiền là dữ liệu nghiêm**: mọi cộng/trừ ghi `xu_ledger` (append-only) để đối soát + audit; lỗi spend KHÔNG nuốt.

## 2. Hiện trạng 2 phía (2026-06-19)
| | AppChat (prvchat) | YI-Chronos |
|---|---|---|
| Ví | `users/{uid}.xu` Firestore + `grantXu/spendXu/claimDailyXu` (đã ship) | `xu_wallet` + `xu_ledger` (PR #54) — **canonical** |
| Hằng số | quick 1 / council 5 / deep 99 · +10 xu/30 ngày | **KHỚP**; free/ngày do YI quản (quick 10 / council 3 — Anh chốt giữ nguyên §9.1) |
| Charging | `XU_ENFORCED` flag (đang wire) | `_gate`: VIP → free → **xu** → denied(insufficient_xu) |
| Nạp | (chưa) RevenueCat/IAP | `POST /api/sync/wallet/grant` (idempotent ref) |

## 3. Mô hình đồng bộ (sau cắt-chuyển)
```
RevenueCat/IAP (verified ở AppChat Functions)
        │ grant(ref=txn_id)               ┌─────────────────────────────┐
        ▼                                 │  YI xu_wallet (CANONICAL)    │
AppChat Cloud Function ───X-API-Key────▶  │  balance + xu_ledger (audit) │
   (cầm secret, uid=context.auth.uid)     └──────────────┬──────────────┘
        ▲  mirror balance để hiển thị                     │ spend trong luồng Hermes
        │  (Firestore.xu = cache, KHÔNG tin để trừ)        │ (quick/council/deep)
   Flutter (hiển thị số dư, nút nạp, nhận xu hằng ngày)    ▼
                                              user_castings + ledger
```
- **Đọc số dư**: AppChat gọi `GET /api/sync/wallet/{uid}` (hoặc lấy `xu_balance` trả về trong kết quả Hermes `done`) → cập nhật Firestore mirror để UI nhanh.
- **Spend**: KHÔNG có call spend riêng. Khi user hỏi Hermes, YI tự trừ; kết quả `done` trả `xu_cost` + `xu_balance` → AppChat cập nhật mirror.

## 4. Kế hoạch CHUYỂN ĐỔI (4 pha — không mất số dư, không trừ/cộng trùng)
> Việc lớn ⇒ làm theo pha, mỗi pha kiểm chứng trước khi sang pha sau. Không big-bang.

**Pha 0 — YI sẵn sàng (XONG, PR #54):** engine + API + gating live nhưng AppChat **chưa** trỏ sang. `grant` idempotent theo `ref`.

**Pha 1 — Di trú số dư (một lần, idempotent):**
- AppChat chạy script đọc mỗi `users/{uid}` có `xu>0` → gọi `POST /api/sync/wallet/grant {firebase_uid, amount=xu, reason:"migration", ref:"migrate:{uid}"}`.
  - `ref="migrate:{uid}"` ⇒ chạy lại script an toàn (idempotent — không cộng đôi).
- Di trú kèm trạng thái phụ để không lệch hành vi ngày đầu:
  - `xuDailyLast` (Firestore) → YI `xu_wallet.daily_last_claim` (tránh **double daily bonus** đúng ngày cắt). *(YI bổ sung endpoint set-daily khi migrate, hoặc gộp tham số vào `/grant` — xem §9 mục mở.)*
  - **Mốc welcome window**: YI tính theo `users.created_at`. User AppChat provision qua `upsert-from-firebase` có `created_at` = lần sync đầu (KHÔNG phải ngày tạo TK) → phải truyền `account_created_at` thật khi upsert/migrate để cửa sổ 30 ngày khớp AppChat.
- Trong cửa sổ migrate: tốt nhất **freeze** spend/claim phía AppChat (maintenance ngắn) HOẶC chấp nhận drift nhỏ rồi đối soát ở Pha 1.5.

**Pha 1.5 — Đối soát:** so `Σ balance YI` vs `Σ Firestore.xu` (chỉ user đã migrate). Lệch → tra `xu_ledger` theo `ref`. YI thắng. Ghi báo cáo.

**Pha 2 — Lật công tắc (AppChat trỏ YI):**
- Bật cờ AppChat (vd `XU_SOURCE=yi`): `spendXu`/`grantXu`/`claimDailyXu` Firestore **ngừng là nguồn chân lý**.
  - Spend: bỏ hẳn — để YI trừ trong luồng Hermes; client đọc `xu_balance` trả về.
  - Nạp: RevenueCat webhook (đã verify) → `POST /api/sync/wallet/grant {ref: rc_txn_id}` → cập nhật mirror.
  - Daily: `claimDailyXu` → `POST /api/sync/wallet/claim-daily`.
- Hết xu: callable Hermes nhận `denied/insufficient_xu` từ YI → `failed-precondition(insufficient_xu)` → màn nạp (UX đã có).

**Pha 3 — Dọn:** gỡ code trừ/cộng Firestore chết; `users/{uid}.xu` chỉ còn mirror; xoá cờ.

## 5. Hợp đồng endpoint (YI — đã có ở PR #54)
| Endpoint | Kênh | Việc |
|---|---|---|
| `GET /api/sync/wallet/{firebase_uid}` | AppChat (X-API-Key) | balance + `xu_cost` + `free_quick_remaining` |
| `POST /api/sync/wallet/grant {firebase_uid, amount, reason, ref}` | AppChat | nạp/tặng — **idempotent theo `ref`** |
| `POST /api/sync/wallet/claim-daily {firebase_uid}` | AppChat | login bonus (idempotent theo ngày) |
| `GET /api/wallet` · `POST /api/wallet/claim-daily` | YI-web (authed) | parity |
| (spend) | — | KHÔNG có endpoint rời — chỉ trong luồng Hermes |

Kết quả Hermes `done` (quick/council) trả thêm `tier`, và khi `tier="xu"`: `xu_cost`, `xu_balance` → client cập nhật mirror.

## 6. Idempotency + đối soát
- **grant**: dedup theo `(user_id, ref, delta>0)` trong `xu_ledger`. RevenueCat **phải** truyền `ref = transaction id` (toàn-cục-duy-nhất). Migration dùng `ref="migrate:{uid}"`.
- **claim-daily**: idempotent theo `daily_last_claim == today(VN)` — gọi nhiều lần/ngày chỉ tặng 1.
- **spend**: không idempotent theo bản chất (mỗi câu hỏi 1 lần tính) — nhưng **cache Iron #4** chặn tính lại cùng câu/ngày; client KHÔNG retry spend (YI là người trừ, client chỉ đọc kết quả).
- **Đối soát định kỳ** (cron, follow-up): `Σ ledger delta == balance` mỗi user (bất biến sổ cái); cảnh báo nếu lệch.

## 7. Ca biên (đã chốt cách xử)
| Ca | Xử |
|---|---|
| YI down lúc user hỏi | callable trả lỗi → client "thử lại"; **KHÔNG** trừ Firestore cục bộ |
| Trừ xu rồi LLM lỗi / quá ngân sách | `_refund_xu` (grant hoàn) — số dư về nguyên |
| Hỏi lại cùng câu trong ngày | cache hit TRƯỚC `_gate` → **không trừ** |
| RevenueCat gửi webhook 2 lần | `grant` idempotent theo `ref` → cộng 1 |
| Migration script chạy 2 lần | `ref="migrate:{uid}"` → cộng 1 |
| Double daily bonus ngày cắt | migrate `daily_last_claim` ở Pha 1 |
| Cửa sổ welcome lệch | truyền `account_created_at` thật khi upsert/migrate |
| User chưa sync (404) / thiếu giờ sinh (422) | giữ guard hiện có (client điều hướng sync giờ sinh) |

## 8. Bảo mật / PDPL
- `grant` chỉ qua Cloud Function cầm `YI_SYNC_API_KEY` (Secret Manager) — **không lộ client**; uid = `context.auth.uid` (không tin body).
- Nạp chỉ sau khi AppChat **verify** biên lai RevenueCat/IAP (chống giả mạo cộng xu).
- `xu_ledger` không chứa PII (chỉ user_id nội bộ + ref giao dịch) — số dư cô lập theo user; YI-web đọc qua authed self.

## 9. Việc còn mở (đã ghi, chờ làm/Anh chốt)
1. **Free numbers**: **CHỐT (Anh duyệt 2026-06-19): GIỮ NGUYÊN** YI `FREE_DAILY_QUICK=10`, `FREE_DAILY_COUNCIL=3` — rộng tay giai đoạn đầu để hút người dùng, KHÔNG ép parity 3/0. Vì YI là nguồn chân lý, đây là con số hiệu lực cho **cả kênh AppChat** (free quick 3 cũ của AppChat không còn áp). Không đổi code.
2. **Migrate daily_last_claim + account_created_at**: bổ sung tham số cho `/wallet/grant` (hoặc endpoint `/wallet/migrate` riêng) để set `daily_last_claim` + `created_at` chuẩn lúc di trú.
3. **deep-reading spend 99 xu**: wire `engine/deep_reading` qua cùng cơ chế `_gate`/`spend` (hiện mới quick + council).
4. **YI-web UI ví (Vue)**: số dư + nhận xu hằng ngày + luồng nạp — parity AppChat.
5. **Cron đối soát** `Σ ledger == balance` + cảnh báo.
6. **(AppChat)** adapter Pha 2: cờ `XU_SOURCE=yi`, gỡ trừ Firestore, RevenueCat→`/grant(ref)`, claim→`/claim-daily`.

## 10. Acceptance (cắt-chuyển coi như xong khi)
- [ ] Pha 1: tổng số dư YI sau migrate == tổng Firestore (đối soát khớp); chạy script 2 lần không đổi tổng.
- [ ] Pha 2: user hỏi Hermes → YI trừ đúng (quick 1/council 5), Firestore mirror khớp `xu_balance` trả về.
- [ ] RevenueCat retry → cộng 1 lần (kiểm `xu_ledger` theo ref).
- [ ] YI down → client KHÔNG trừ cục bộ (không có call spend Firestore nào).
- [ ] `Σ xu_ledger.delta == xu_wallet.balance` mọi user (bất biến sổ cái).

## 11. Test (PR #54)
`tests/test_xu_wallet.py` (13, gồm idempotent-by-ref) · `tests/test_hermes_xu_gating.py` (4) · `tests/test_wallet_api.py` (6). PASS dual-driver.
