# H6 — HERMES PHỤC VỤ NHIỀU NGƯỜI: Nghiên cứu + Thiết kế (Phương án A)

> Ngày: 2026-06-17 · Trạng thái: **THIẾT KẾ (chờ anh duyệt từng phần)** · Tiền đề: nền P0 (Postgres+RLS+Celery+llm_spend) đã merged vào main (`9af10cc1`).
> Đây là ADR + plan. **Chưa code.** Mỗi mục có chỗ anh duyệt.

---

## 0. Vì sao có tài liệu này

Hermes là linh hồn dự án nhưng **chưa hoạt động đúng vai**. Nghiên cứu (2026-06-17) phát hiện gốc rễ + chốt hướng xử lý cho mục tiêu **phục vụ nhiều END-USER** (không phải multi-tenant nhiều tổ chức).

---

## 1. HIỆN TRẠNG (kết quả nghiên cứu)

### 1.1 Có HAI Hermes, cái mạnh KHÔNG phục vụ user
| | Hermes Agent CLI (NousResearch) | YI-Hermes concierge |
|---|---|---|
| Vị trí | `vendor/hermes-agent/` (KHÔNG commit — chỉ máy anh) | `engine/yi_hermes/` (in-app web) |
| Năng lực | tự xây skill, tự hành, cron, kanban, council, distill | mỏng: ý định → glossary/council/LLM |
| Phục vụ | **một operator (anh), local** | end-user, đa người |

→ "Hermes tự xây skill/tự hành" anh trải nghiệm = **CLI operator-side**. End-user chỉ chạm concierge mỏng. Cầu nối CLI↔web (Phase 2 trong `docs/hermes-agent-setup.md`) **chưa làm**.

### 1.2 Trí tuệ bị "nhốt" trên máy anh
`data/hermes_yi/` gitignore → container cloud (cái users hit) **thiếu**: 3/7 sage, **arbiter** (người tổng hợp council), `vendor/` CLI, `project_manifest` (rỗng), `founder_profile`. ⇒ **Cái deploy ≠ Hermes thật.** Đây là chặn lớn nhất cho đa-user.

### 1.3 Các bộ phận (đã kiểm code)
- **Concierge** `chat.py`: đồng bộ, chặn worker.
- **Council** `kanban_council.py`: đa-sage, nhưng **daemon local spawn process** → đơn-operator.
- **Sage SOUL** `profiles/*/SOUL.md`: khế ước nhận thức (đồng dạng, engine-tính-sage-luận). Công phu.
- **Skill** `data/hermes_yi/skills/`: markdown tĩnh + `feed_sages.py` bơm từ wiki. KHÔNG sinh lúc chạy.
- **Memory** `memory.py`: per-user facts/summaries/glossary — **đã RLS** (P0). **Soul per-user** `soul.py`: tự tiến hoá giọng/sở thích ✓.
- **Research** `yi_research/`: bọc GPT Researcher, **chưa nối chat**.
- Phôi thai tiến hoá đã có: `critique_store`, `feedback_store`, `distill_from_council`.

---

## 2. QUYẾT ĐỊNH KIẾN TRÚC (Phương án A — anh đã chốt)

**A: Nâng concierge thành agent đa-user (tool-loop + memory + wiki + council) chạy như dịch vụ stateless qua Celery `q_hermes`. Hermes Agent CLI giữ vai "bộ não backend" đọc sách/distill offline.**

Nguyên tắc nền: **worker phi-trạng-thái, state ở Postgres/Redis, chạy async**. (Worker stateless ≠ agent stateless — agent vẫn "nhớ mọi thứ" vì state ở DB.)

→ Mô hình tổng: **MỘT bộ não chung (code+skill+tri thức) + HỒ SƠ RIÊNG mỗi user (cô lập RLS) + nhiều worker song song.** Không có "1 Hermes / N user" — scale theo worker/GPU (= tiền), sizing theo **đỉnh đồng thời** (không phải tổng user).

---

## 3. HAI VÒNG LẶP

### 🟦 Vòng 1 — Ô chat mỗi user (agent có rào)
Stateless agent qua `q_hermes`, nạp hồ sơ riêng mỗi lượt.

| Đầu việc | Cơ chế | Tái dùng |
|---|---|---|
| Hỏi đáp lá số | tool-loop tự gọi engine → *facts* → RAG sách → luận. **Fact từ engine, KHÔNG bịa** | tool-loop + pgvector |
| Giải thích khái niệm | đường nhanh glossary/wiki (model rẻ / không LLM) | `glossary.py` |
| Tư vấn phản biện đa chiều | council đa-sage, **đa-user qua `q_hermes`** (bỏ daemon local), async+stream | `kanban_council` |
| Bám 1 việc → nhiều phương án | giữ đúng việc user nêu; **phương án + lý lẽ, KHÔNG quyết thay** | paradigm dự án |
| **Giới hạn phạm vi (không làm hộ)** | rào 3 lớp: (1) chặn ngoài-miền; (2) vòng "nghĩ–nói–phản tỉnh"; (3) post-filter cấm tiên tri | **SocraticAI pattern** |
| Báo chủ động khi có trường phái mới | Beat/event → fan-out tới user liên quan (gói trả phí) | Celery Beat |

**Triết lý rào (anh chốt #1):** theo **MỆNH LÀ ĐỘNG TỪ** (Iron #8) — agent **soi tính → gợi cách vận hành**, KHÔNG bói, KHÔNG quyết thay, KHÔNG làm bài hộ. Vừa đúng đạo vừa chặn chi phí.

### 🟩 Vòng 2 — Bộ não hệ thống (đọc sách, tự tiến hoá)
Pipeline tự-chủ-có-duyệt, chạy **nền/offline** (model rẻ local + Celery Beat). **1 lần distill → cả triệu user hưởng** (chi phí chia đều ~0/user).

| Đầu việc | Cơ chế | Phôi thai sẵn |
|---|---|---|
| Đọc sách → trường phái mới | bookflow → distill → wiki/lexicon → skill pack + sage + engine module | bookflow + `feed_sages` |
| Tự phát hiện vấn đề | mining hội thoại ẩn danh + feedback + câu trả lời độ-tin-thấp | `feedback_store`, `critique_store` |
| Tự bổ sung data / tự tìm | research agent + đọc nguồn → đề xuất | `yi_research/` |
| Tự tiến hoá tri thức/tính năng | skill-library tiến hoá + **propose(sage)→solve→judge(arbiter)** → ExpeL-style insight | council = sẵn pattern |

**Adopt từ thế giới (Iron #1):** AutoSkill/SkillFoundry (skill self-evolution), ExpeL (chắt trajectory→insight sửa được), Multi-Agent Evolve (Proposer/Solver/Judge ≈ council mình). SocraticAI (rào phạm vi). Letta/Mem0 (tầng ký-ức-hội-thoại). → **mượn pattern, ghép lên phôi thai**, không phát minh.

### 🔗 Cầu nối "cập nhật lẫn nhau"
```
Vòng 2 ──(cổng duyệt)──► NÃO CHUNG có version ──► Vòng 1 nạp NGAY ──► báo user liên quan
Hồ sơ RIÊNG ◄── chỉ chảy vào chính user đó (RLS, kín)
```

---

## 3B. ROSTER SAGE — mỗi trường phái một Hermes, tranh luận chuẩn nghiên cứu (anh chốt)

**Có**: mỗi trường phái = một sage riêng, độc lập, rồi tranh luận để ra kết luận chuẩn. Khớp Iron #3 (đa phái độc lập, `kept_all` hợp lệ). ~**10-15 trường phái** trên thế giới → roster ~10-15 sage.

### Nguyên tắc sống còn: THUẦN-KHIẾT + tranh-luận-ở-ARBITER
> Giữ mỗi sage TINH KHIẾT (một thầy, một thế giới quan). **KHÔNG trộn phái vào trong một sage** (trộn = nhão, mất nhất quán). **Va chạm để ra chân lý là việc của arbiter**, không phải nhồi nhiều phái vào một đầu.

- Sage Tử Vi chỉ sống trong thế giới Trần Đoàn; Mai Hoa chỉ trong Thiệu Khang Tiết… → chuyên sâu + nhất quán cao.
- Đọc **độc lập** (sage không thấy bài nhau → không nhiễm → giữ thuần).

### Quy mô (quan trọng cho chi phí)
1. **Roster CHUNG, KHÔNG nhân theo user**: ~10-15 chuyên gia dùng chung cho cả triệu user (trong "não chung"), không phải 15 × số user.
2. **Một câu hỏi KHÔNG gọi cả 15**: router chọn 2-5 phái liên quan (định tuyến rẻ từ khoá/embedding). **Council đầy đủ = tính năng cao cấp / trả phí** (tốn + chậm). Free = một sage giỏi nhất hoặc concierge.

### Bảo chứng "nhất quán cao độ"
- SOUL = khế ước nhận thức (paradigm + format + điều cấm) — đã có.
- Một thầy gốc (master-apprentice, author-worldview-first) — không LLM chung chung.
- Fact từ engine (sage luận, không tự tính) → input nhất quán.
- Skill pack riêng mỗi phái — đã có.
- **Buộc trích dẫn** (sách/điều) = chuẩn nghiên cứu.
- **Bộ test nhất quán** (golden Q → paradigm kỳ vọng) cho mỗi sage = bắt "trôi giọng" như test hồi quy. *(cần thêm)*
- *(xa, H6.3)* fine-tune model self-host riêng từng phái.

### Quy trình tranh luận chuẩn (= Proposer→Solver→Judge)
1. Sage đọc độc lập.
2. **Arbiter** đối chiếu: đánh dấu **đồng thuận / mâu thuẫn / thiểu số** — KHÔNG ép đồng ý.
3. Mâu thuẫn → trình user dạng "đa phái, mỗi cái đúng trong ngữ cảnh" (`kept_all`), hoặc đẩy lên cổng duyệt anh nếu là tri thức mới.
4. Mọi luận điểm **truy được nguồn** + khớp facts engine (post-filter chống bịa).
→ Cần **khôi phục arbiter** (đang thiếu) + thêm tầng đánh dấu đồng thuận/mâu thuẫn.

### Trường phái mới
Vòng 2 đọc sách → đề xuất **sage mới + skill pack** → cổng duyệt theo độ tự tin (trường phái mới = tác-động-lớn → anh duyệt) → vào roster chung. Roster lớn dần *có chủ đích*.

**Lưu ý kinh tế:** roster nhiều (10-15) nhưng mỗi lượt chỉ triệu tập subset liên quan; council-đầy-đủ chỉ cho câu hỏi sâu/trả phí.

---

## 4. CỔNG DUYỆT THEO ĐỘ TỰ TIN (anh chốt #2)

Mọi đề xuất Vòng-2 vào **não chung** đều: **em (AI) rà Iron Rules + chấm độ tự tin TRƯỚC**, rồi:

| Độ tự tin | Tác động | Ai duyệt |
|---|---|---|
| CAO | NHỎ (trích dẫn, atom lẻ) | em duyệt + auto-merge · anh được báo (rollback được) |
| CAO | LỚN (trường phái mới, đụng paradigm) | em phân tích+chấm → **anh duyệt** bắt buộc |
| THẤP / mơ hồ | bất kỳ | em trình cái chưa chắc → **anh quyết** |

- **Em = vòng duyệt đầu** (lọc + chấm điểm + gắn cờ rủi ro paradigm) → anh chỉ nhìn hàng đợi đã lọc.
- **Anh = quyền tối hậu**, đặc biệt với tác-động-lớn / paradigm.
- Dữ liệu RIÊNG user: **tuyệt đối cô lập, không qua cổng chung** (RLS đã khoá).

---

## 5. CHI PHÍ & PHÂN TẦNG (quy tắc vàng ≥10× chi phí LLM)

| Gói | Memory | Tiến hoá | Tự hành |
|---|---|---|---|
| FREE | cửa sổ ngắn, 3 lượt/ngày | — | — |
| Đồng Hành (VIP) | nhớ mọi thứ (cold log+RAG) | soul tiến hoá + digest | proactive + tool-agent đầy đủ |

- Vòng 1: tốn theo câu hỏi → cache 3 lớp + routing (Flash→Pro→Gemini) + `llm_spend` hard-stop (P0-5 ✓) + gói/CAP.
- Vòng 2: theo mẻ → rẻ, đòn bẩy lớn.
- Self-host Qwen2.5-14B vLLM trong VN khi ~2.5–3M lượt/tháng (rẻ nhất + giải PDPL).

---

## 6. KHOẢNG CÁCH PHẢI VÁ (để đúng vai + đa-user)
1. **Đưa não ra khỏi máy Mac**: sage/arbiter/manifest/founder-context phải **deploy được** (DB/được track), không kẹt local gitignore.
2. **arbiter** (người tổng hợp council) — bổ sung/khôi phục.
3. **Council đa-user**: thay subprocess+daemon local → Celery `q_hermes` + stateless.
4. **Bỏ `_founder` cứng** → `center = current user`; per-user context từ DB (P0 RLS sẵn).
5. **Nối wiki query** (mode HIỂU/DÙNG) + **nối research** vào chat.
6. Thêm **rào phạm vi Socratic** + **pseudonymize PDPL** + **post-filter paradigm**.

---

## 7. LỘ TRÌNH (mỗi nhịp 1 PR, test thật)
- **H6.0 — nền đa-user + agent tối thiểu**: stateless + `q_hermes` async/SSE · tổng quát `_founder`→user · tool-loop cơ bản (engine=tools) · **rào phạm vi** · khôi phục arbiter · gate gói. *(gỡ blocker, rủi ro thấp)*
- **H6.1 — nhớ mọi thứ + chi phí**: memory hot/warm/cold + pgvector retrieval + consolidation (cân nhắc Letta/Mem0) · cache 3 lớp · pseudonymize · post-filter.
- **H6.2 — Vòng 2 tiến hoá + tự hành**: pipeline distill có **cổng duyệt theo độ tự tin** · Beat triggers (Đại Vận/biến cố) → proactive (VIP) · pattern-mining.
- **H6.3 — self-host (+ tùy chọn fine-tune)**: Qwen14B vLLM VN khi đủ volume.

---

## 8. CẦN ANH DUYỆT (đánh dấu khi đồng ý)
- [ ] Mục 2: Phương án A + mô hình "não chung + hồ sơ riêng" ✅(đã đồng ý miệng)
- [ ] Mục 3: rào phạm vi theo *mệnh-là-động-từ* ✅(đã đồng ý #1)
- [ ] Mục 3B: roster ~10-15 sage thuần-khiết + tranh luận ở arbiter ✅(đã đồng ý)
- [ ] Mục 4: cổng duyệt theo độ tự tin, AI đồng-duyệt + anh tối hậu ✅(đã đồng ý #2)
- [ ] Mục 7: bắt đầu từ **H6.0** sau khi duyệt thiết kế
- [ ] Xác minh trên máy Mac: `vendor/hermes-agent/` + 7 sage + arbiter có thật không (để biết "vá" hay "khôi phục")
