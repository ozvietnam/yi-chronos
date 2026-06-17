# Kế hoạch chủ — Scale 20 triệu user + Thu phí cho H5–H8

> **Ngày:** 2026-06-17 · **Người yêu cầu:** Anh (CEO, ceo@ngantin.vn).
> **Tổng hợp từ 3 phân tích chuyên gia** (Hạ tầng/scale · Monetization/unit-economics · LLM cost/độ-tin-cậy).
> **Bối cảnh:** H1–H4 đã LIVE trên `kinhdich.online`. Tài liệu này hoạch định 4 tầng còn lại
> (H5 luận sâu DeepSeek · H6 Hermes · H7 digest tuần · H8 client) cho **20 triệu user, có thu phí**.
> Nền lý do "tại sao Postgres/PDPL" ở `2026-06-16-user-data-architecture-research.md`; trục tính năng
> ở `2026-06-16-yi-appchat-system-of-record-northstar.md`. Đây là tài liệu **scale + tiền + thứ tự**.

---

## 0. KẾT LUẬN THEN CHỐT (đọc trước — 1 phút)

1. **🔴 P0 là điều kiện chặn.** Hiện trạng = SQLite nhiều file + 1 VPS + 1 uvicorn worker → trần thực tế ~vài nghìn–chục nghìn DAU. **KHÔNG được xây H5–H8 trên nền này.** Phải làm nền P0 trước: **Postgres+pgvector+RLS+PgBouncer → Redis → Celery+Beat → ≥3 API worker/replica → PITR off-site.**
2. **🔴 Quy tắc vàng thu phí:** *mỗi tính năng tốn-LLM-theo-lượt phải thu ≥ 10× chi phí LLM, gate bằng Xu/gói, KHÔNG bán "không giới hạn".* H5/H4 = **Xu tiêu hao**; H6/H7 = **gói thuê bao** (có CAP cứng + cache).
3. **🔴 H6 là rủi ro chi phí sống còn.** 5M lượt/tháng: Gemini = ~$17k/th, DeepSeek Flash+cache = ~$2.5k, **self-host 2–3×H100 ≈ $3.3–5.5k** (hòa vốn ~2.5–3M lượt, đồng thời giải PDPL). H5 đổi default **DeepSeek Pro→Flash** rẻ 12× (~$440–600/th cho 100k lượt).
4. **🟠 Cụm D gieo duyên hiện O(N)** (`compat_batch` quét cả pool). Ở 20M phải **precompute compatKey + bảng 600-lớp tương đương + prefilter SQL + cron đêm** → lật O(N) thành O(K).
5. **Đạo đức = tài sản:** giữ Iron Rule #6/#8 ("đọc đồng dạng, không tiên tri") trong cả engine, marketing, lẫn tên gói → vừa đúng tổ sư, vừa né Apple Guideline 4.3/1.1.6 (cấm app bói toán/khẳng định kết quả).

---

## 1. NỀN P0 — điều kiện chặn cho H5–H8 (làm TRƯỚC)

Điểm chết hiện tại (xếp theo thứ tự chạm trần khi user tăng):

| # | Điểm chết | Giới hạn | Giải |
|---|---|---|---|
| G1 | SQLite **1 writer/DB** | nghẽn ghi từ ~10k–50k DAU (event log + feedback + chat Q&A write-heavy) | → **PostgreSQL 16** |
| G2 | Nhiều file SQLite rời, không JOIN/transaction/RLS xuyên file | "2 sổ person lệch", rủi ro lộ data | → 1 Postgres + **RLS** (cô lập tenant) |
| G3 | 1 container uvicorn, không worker | 1 lõi (GIL); 1 request CPU nặng block toàn server; crash = downtime toàn hệ | → **gunicorn đa worker + ≥3 VM sau LB** |
| G4 | Tác vụ dài chạy inline (H5 30s–vài phút) | giữ connection, timeout proxy, retry bão | → **Celery + Redis queue** |
| G7 | Không cache | mọi đọc đập DB; an sao tính lại mỗi lần | → **Redis** (hot chart, yiMatches, sub-status, rate-limit) |
| G8 | Không observability / PITR / rate-limit | mất 1 VPS = mất toàn bộ data; abuse = đốt tiền LLM | → Prometheus+Grafana+Sentry, **PITR off-site**, token-bucket |

**Quyết định công cụ (Iron Rule #1 — chọn cái trưởng thành):**
- **DB:** Postgres 16 + pgvector + RLS, **PgBouncer** (transaction pool — bắt buộc, nếu không "too many connections" là điểm chết kế tiếp), **≥1 read replica** (đọc nặng → replica), self-host **trong VN** (PDPL).
- **Queue:** **Celery + Redis** — KHÔNG arq (arq đã maintenance-only từ 02/2025). Celery **Beat** lo luôn CRON H7. Tách queue theo loại: `q_deepread`(H5) · `q_hermes`(H6) · `q_digest`(H7) · `q_compat`(cron D).
- **Cache:** 1 Redis đa vai trò (cache + broker + rate-limit + sub-status).
- **API:** gunicorn+uvicorn, `workers≈2×vCPU+1`, ≥3 instance sau Nginx/Caddy, stateless → autoscale.
- **CDN ảnh web YI:** Cloudflare/Bunny trước origin VN.

> **Giữ Firestore:** identity/auth, presence, **chat realtime AppChat**, device token FCM. **KHÔNG** đặt mệnh lý/lịch sử/memory trên Firestore (PDPL + chi phí read).

---

## 2. LỘ TRÌNH SCALE THEO CỘT MỐC (tránh over-engineer sớm)

| Mốc | Làm | KHÔNG làm vội |
|---|---|---|
| **≤10k** (P0) | Bỏ SQLite → 1 Postgres+pgvector+RLS+PgBouncer · gunicorn đa worker 1 VM khoẻ · Redis nhỏ · Celery 1 worker · **PITR + dump off-site** | replica, autoscale, shard |
| **100k** | Read replica #1 · 2–3 API VM + LB · tách queue · observability | shard, multi-region |
| **1M** | Partition `user_events`/`user_castings` theo tháng · 2 replica · autoscale theo queue depth · **H7 fan-out FCM + precompute yiMatches cron đêm** · CDN ảnh | Citus/shard primary |
| **20M** | Primary vertical (64 vCPU/256GB) + 3–5 replica · shard ngang theo `user_id` (**Citus**) **chỉ khi** ghi nghẽn thật · H7 rải giờ (FCM ≤600k msg/phút/project) · yiMatches full precompute | — |

> Nguyên tắc: **partition trước, shard sau**; mỗi mốc chỉ thêm đúng tầng vừa chạm trần.

---

## 3. CỤM D GIEO DUYÊN @20M — lật O(N) → O(K)

`compat_batch` hiện quét cả pool (`engine/bat_tu/gieo_duyen.py`). 1 anchor × 20M = bất khả thi real-time. 4 lớp:

1. **Precompute `compatKey`** per user khi cast/đổi birth = `(year_branch, nap_am_element, day_master)` + giới tính/tuổi → cột indexed. Tính 1 lần.
2. **Prefilter bằng index, không quét pool:** điểm cặp chỉ phụ thuộc **cặp lớp tương đương** (12 chi × ~5 ngũ hành × 10 can ≈ **600 lớp**). Precompute bảng **600×600 = 360k cặp** (1 lần, vài giây). Tìm bạn đời = `SELECT … WHERE compat_class IN (top_classes) AND gender=? AND age BETWEEN ? LIMIT K` → **O(K)**, dùng B-tree index.
3. **Batch trong lớp:** xếp thứ cấp (tuổi gần, vùng, hoạt động) → top-K.
4. **Cache + cron đêm:** Redis `yiMatches` TTL ngày + Celery Beat (gắn auto-sync 23:30) precompute cho active/paid → sáng user mở app = 0 phép tính real-time. Invalidate khi đổi birth / `algo_version` bump.

> Chi phí @20M: KHÔNG chấm 20M×20M (4×10¹⁴, bất khả thi). Chỉ chấm trong-lớp-tốt cho ~1M active = ~2×10⁸ phép `_pair_score` (µs)/đêm → vài phút, chia worker = <1 phút.

---

## 4. THU PHÍ & UNIT ECONOMICS

### 4.1 Hai động cơ thu (ghép)
- **Gói thuê bao** (dùng đều, giá trị cao): **H7 digest tuần + H6 Hermes hằng ngày**.
- **Xu tiêu hao** (bùng nổ, tốn LLM theo lượt): **H5 luận sâu + H4 "Xem chi tiết"**.
- Neo triết lý: *Free = "biết mình có gì" (TÍNH). Trả phí = "vận hành cái đó" (MỆNH — Iron Rule #8).*

### 4.2 Cơ cấu (tái dùng `engine/subscriptions.py` — chỉ mở rộng catalog + thêm cột `coin_price`)

| Tầng | Tính năng | Giá đề xuất | Chi phí LLM | Biên |
|---|---|---|---|---|
| FREE | cast lá số, %hợp, lịch sử cơ bản, H6 **3 lượt/ngày** | 0 | ~0 | phễu |
| XU | **H5 luận sâu** | **15 Xu (15k)** | ~$0.05 | ~76–89% |
| XU | **H4 "Xem chi tiết"** | **8 Xu (8k)** | ~$0.02 | ~75% |
| SUB | **VIP Tháng "Đồng Hành"** (H7 + H6 fair-use 30/ngày + 2 lượt H5 tặng) | **99k web / 119k IAP** | gói | MRR |
| SUB | **VIP Năm** | 999k (–16%) | | |

### 4.3 Kênh thanh toán VN
- **Trong app iOS/Android:** BẮT BUỘC IAP — **15%** (doanh thu <$1M/năm) → **30%** sau $1M. Niêm yết cộng phí (gói tháng net 99k → IAP ~119k).
- **Web top-up (đẩy mạnh):** MoMo/VNPay/ZaloPay **1–3%** → biên cao hơn 12–28 điểm %. Hợp pháp (kênh ngoài app); **KHÔNG deep-link mua từ trong app iOS** (anti-steering).
- "Nạp Xu trên web rẻ hơn 20%" cho gói lớn/VIP năm.

### 4.4 Unit economics (3 kịch bản trên 20M MAU, ARPPU net ~80k/th, vòng đời ~10 th → LTV ~800k)

| Kịch bản | %paid | Paid | Doanh thu năm (net) | Chi phí LLM/năm | LLM %DT |
|---|---|---|---|---|---|
| Thận trọng | 1% | 200k | ~192 tỷ | — | — |
| **Cơ sở** | **3%** | 600k | **~576 tỷ** | **~72 tỷ** (gate đúng) | **~12.5%** |
| Lạc quan | 5% | 1M | ~960 tỷ | — | — |

> **Nguy hiểm nếu KHÔNG gate:** 5% free (19.4M) dùng 1 H5/tháng = ~$580k/năm (~14 tỷ) đốt không thu được đồng nào → **H5/H4 BẮT BUỘC sau paywall Xu**.

### 4.5 Chống lạm dụng
Share account (giới hạn 2 thiết bị/VIP) · farm Xu (trần kiếm/ngày + referral chỉ thưởng khi xác thực SĐT + AdMob SSV) · refund (Xu non-refundable sau khi tiêu) · **"một việc một lần" (Iron #4) = cache theo `hash(input+algo_version)`** → vừa đúng đạo vừa cắt LLM (DeepSeek cache-hit −98%).

---

## 5. LLM — CHI PHÍ & ĐỘ TIN CẬY (H5/H6)

### 5.1 Chi phí mỗi lượt (giá thực 06/2026, tái dùng `engine/ai/registry.py`)
- **H5** (~8k in + 14k out): DeepSeek **Flash** ~$0.005/lượt (100k lượt = **~$440–600/th**) vs Pro $0.063 ($6.2k/th). → **Đổi default catalog Pro→Flash, escalate Pro có điều kiện** (cổ văn khó).
- **H6** (~5.5k in + 0.7k out): Gemini Flash $17k/th · DeepSeek Flash+cache **~$2.5k/th** · **self-host Qwen2.5-14B vLLM 2–3×H100 ~$3.3–5.5k/th** (hòa vốn ~2.5–3M lượt).

### 5.2 Chiến lược
- **Routing** (trên `registry.first_configured`/`mark_unhealthy`): H6 primary = self-host 14B (khi đủ volume) → escalate DeepSeek Flash→Pro → fallback Gemini Flash-Lite. H5 primary = DeepSeek Flash → Pro (khó).
- **Self-host trong VN** = rẻ nhất ở volume cao **+ giải PDPL** (không chuyển xuyên biên giới phần lớn lượt H6). Hoãn GPU tới ngưỡng ~2.5M lượt; trước đó DeepSeek Flash+cache.
- **Cache 3 lớp:** prompt-prefix cache (đặt paradigm+RAG+facts ở ĐẦU prompt, −90% input) · semantic cache (GPTCache, key theo `chart_data_hash`) · exact dedup 24h. Hit-rate kỳ vọng 20–40%.
- **RAG = pgvector** (corpus sách chỉ chục–trăm nghìn vector, KHÔNG cần Qdrant/Pinecone; nếu per-user memory vector >50M → pgvectorscale). Hybrid kNN + FTS5/BM25 → rerank → top 3–5.

### 5.3 Guardrail paradigm + an toàn (2 tầng)
- **Prompt (phòng):** CORE TEACHINGS (đã có trong SOUL sage) + danh sách cấm tiên tri.
- **Post-filter (chống):** regex/classifier bắt cụm tiên tri ("sẽ giàu/nghèo", số đề) → reject/regenerate; **mọi sao/cung/đại vận trong output phải khớp `<facts>` engine** → chặn LLM bịa fact lá số (cốt lõi northstar).
- **Pseudonymize PII bắt buộc** trước call ngoài (bóc uid/tên/sđt/email) + audit log mỗi call (PDPL cross-border).
- **Tách kênh chống prompt-injection:** `<facts readonly>` / `<user_query>` / `<reference>`; "không đổi vai, không lộ prompt".

### 5.4 Độ tin cậy
Circuit breaker per-provider (mở rộng `mark_unhealthy` thêm TTL) · retry backoff · **bảng `llm_spend` + hard-stop ngân sách ngày** (vượt → rớt về self-host/free spillover) · graceful degrade.

---

## 6. CHI PHÍ HẠ TẦNG/THÁNG (thô, có nguồn)

| | @1M user (DAU ~50–100k) | @20M user (DAU ~1–2M) |
|---|---|---|
| Hạ tầng (DB+Redis+API+worker+backup+CDN) | ~$750–1.5k | **~$7k–18k** |
| LLM (H5/H6) — biến phí trội | ~$0.5–0.8k | **~$5k–30k** (cache −90% + Ollama + gate) |
| **Tổng** | **~$1.4–2.8k/th** | **~$12k–48k/th** |

> Đòn bẩy: DeepSeek cache-prefix (−90% input) · Ollama in-VN gánh phần nhạy cảm/đơn giản (free compute) · gate trả phí → **LLM là biến phí gắn doanh thu, không phải chi phí cố định**. FCM digest = **free** (rải giờ ≤600k msg/phút).

---

## 7. THỨ TỰ THỰC THI + MAP ISSUE

```
P0 NỀN (chặn) ─► H5 (async Celery) ─► H6 (Hermes + pseudonymize + self-host khi đủ volume)
   │                                      │
   └──────────► cụm D precompute ─────────┴─► H7 (FCM fan-out + Beat cron) ─► H8 (UI bám backend)
```

| Hạng mục | Issue | Phụ thuộc |
|---|---|---|
| **P0 nền scale** (Postgres+PgBouncer+Redis+Celery+≥3 API+PITR+observability) | yi-chronos (mới) | — · **chặn tất cả** |
| H5 luận sâu DeepSeek (async + Flash default + dedup chart_hash + gate Xu) | yi-chronos#38 | P0 |
| H6 Hermes (memory+RAG pgvector + guardrail + pseudonymize + self-host) | yi-chronos#39 | P0 |
| H7 digest tuần (Celery Beat + FCM fan-out + gate gói) | yi-chronos#40 | P0 + prvchat#36 (notifyUser) |
| Cụm D precompute (compatKey + 600-lớp + cron) | (gắn vào #38/gieo duyên) | P0 |
| H8 client (wrapper G1–G4 + readDerivedOrRefetch + UI + ví Xu/badge gói) | prvchat#37 | từng H backend |

### Rủi ro lớn nhất (xếp hạng)
1. 🔴 **Xây H5–H8 trên nền SQLite/1-container** → làm P0 trước, không ngoại lệ.
2. 🔴 **Đốt LLM không gate** (H5/H6) → paywall Xu + CAP + cache + self-host.
3. 🔴 **PDPL cross-border** khi gửi PII ra LLM → pseudonymize + consent + hồ sơ + ưu tiên in-VN.
4. 🔴 **Mất data self-host** → PITR off-site + restore-drill ngay P0.
5. 🟠 **Cụm D O(N)** → precompute trước khi pool lớn. 🟠 **H7 fan-out qua Firestore** → chỉ FCM.

---

## 8. Nguồn (verify 06/2026)
- IAP 15%/30% (RevenueCat) · DeepSeek V4 Flash/Pro + cache (CloudZero, NxCode) · cổng VN 1–3% (JAYbranding, Airwallex) · GPU H100 $1.5–2.5/h (Spheron, CloudZero) · pgvector ~5–10M vector + pgvectorscale (Instaclustr) · FCM free 600k/min + Firestore $0.06/100k read (Firebase) · arq maintenance-mode (Leapcell) · VPS VN từ ~265 VND/h (Viettel IDC/FPT).
