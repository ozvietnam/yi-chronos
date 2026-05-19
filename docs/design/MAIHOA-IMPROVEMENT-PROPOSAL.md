# Đề xuất cải tiến trang Mai Hoa hệ thống cũ

**Ngày**: 2026-05-15
**Người viết**: Em (Claude) — dựa trên 45 trang sách Mai Hoa VN đã đọc + wiki v0.1
**Trạng thái wiki tham chiếu**: 196 concepts + 29 methods + 23 passages

---

## 1. State hiện tại của trang Mai Hoa (App.vue line 474-488)

```
Tab "Mai Hoa"
├── TabIntro            — mô tả thuần text
├── YiTimelineNarrativePanel  — 6 quẻ narrative theo timeline
├── YiDiepPanel         — chia 1 giờ thành 5 "diệp" (12 phút)
└── PersonalQuaiPanel   — quẻ bản mệnh + 30 ngày dự báo

Lõi tính toán: utils/maiHoaTime.js
  computeMaiHoaState(date, timeZone) → {upper, lower, moving}
  Công thức: (Y+M+D) mod 8, (Y+M+D+H) mod 8, (Y+M+D+H) mod 6
  ✅ ĐÚNG VỚI SÁCH MAI HOA TRANG 43-45
```

**Đánh giá**: Lõi toán chuẩn. UI chuẩn ở mức **trình bày**. Thiếu ở mức **diễn giải truyền thống Thiệu Khang Tiết**.

---

## 2. 8 GAP phát hiện được sau 45 trang

| # | Gap | Mức độ | Cần đọc thêm? |
|---|---|---|---|
| G1 | TabIntro nói "5 quẻ phái sinh (Hỗ, Biến, Giao, Phục, Bao)" — sách Mai Hoa Thiệu cổ chỉ có **Chính + Hỗ + Biến** (3 quẻ) | 🔴 Cao | Không — fix ngay |
| G2 | Không phân biệt **Thể-Dụng** — đây là trụ cột Quyển 3 | 🔴 Cao | **CÓ — Quyển 3 (~trang 150+)** |
| G3 | Không có **Quái Khí Vượng/Suy** theo mùa | 🟡 Vừa | Không — đã có ở trang 24-27 |
| G4 | Không cross-ref tới Wiki Tổ sư (link Author/Concept/Method) | 🟡 Vừa | Không |
| G5 | Không tracking **Prediction** (anh gieo xong → chỗ nào? review ra sao?) | 🔴 Cao | Không — schema đã có |
| G6 | TabIntro thiếu link tới Master entry trong Wiki | 🟢 Thấp | Không |
| G7 | Không hiện triết lý **Ngoạn Pháp** ("Nhân ư tâm thượng khởi kinh luận") | 🟡 Vừa | Không — đã có ở trang 36-38 |
| G8 | Không hiện mnemonic 8 quẻ (Càn tam liên, Khôn lục đoạn…) | 🟢 Thấp | Không — đã có ở trang 32 |

---

## 3. Roadmap cải tiến — 3 phase

### 🟢 PHASE A — Làm ngay (data đã có trong wiki)

#### A1. Fix TabIntro — phân biệt "Mai Hoa Thiệu cổ" vs "Mai Hoa mở rộng"
**Sửa**: Mô tả chính xác hơn:
> Mai Hoa Dịch Số (Thiệu Khang Tiết, 1011-1077): từ thời điểm Năm-Tháng-Ngày-Giờ → 3 quẻ chuẩn (**Chính + Hỗ + Biến**) qua thuật toán mod 8 + mod 6. Hệ thống mở rộng thêm 3 góc phái sinh (Giao, Phục, Bao) để đọc đa chiều.

#### A2. Save Prediction mỗi lần gieo
Khi anh xem quẻ trang Mai Hoa → tạo entry `predictions` qua `/api/yi-wiki/predictions` (chưa có endpoint — phải thêm):
- `timestamp`, `user_intent` (anh ghi câu hỏi)
- `interaction_log` (em capture mouse + thời gian xem)
- `tam_note` (textarea cho anh nhập tâm thái)
- `review_reminder_at` (mặc định +7 ngày)

#### A3. Cross-ref Wiki — overlay
Quẻ Ly trên Chấn dưới → tooltip:
- Quẻ Ly: ☲ Trung hư | Hoả | Trung nữ | Tiên Thiên Đông / Hậu Thiên Nam
- Quẻ Chấn: ☳ Ngưỡng vu | Mộc | Trưởng nam | Tiên Thiên Đông Bắc / Hậu Thiên Đông
- Link → `/wiki?concept=Quẻ Ly`

#### A4. Hiển thị Quái Khí Vượng/Suy theo mùa
Pull dữ liệu từ trang 24-27 đã extract:
- Mùa hạ (tháng 5) → **Ly Hoả vượng**, Càn Đoài Kim suy, Chấn Mộc hưu (đã sinh ra Hoả)
- Render badge ngay cạnh quẻ: 🟢 VƯỢNG / 🔴 SUY / ⚪ HƯU

#### A5. Ngoạn Pháp note
Block nhỏ phía trên UI:
> 💎 Ngoạn Pháp (玩法): "**Nhân ư tâm thượng khởi kinh luân**" —
> Con người từ tâm Thái Cực mà khởi nên tài năng. Quẻ chỉ là gương —
> tâm anh là gốc. (Mai Hoa Dịch Số, trang 38)

#### A6. 8 Quẻ Mnemonic
Mỗi quẻ trên UI có icon ☰ ☷ ☳ ☴ ☵ ☲ ☶ ☱ + tooltip 1 câu:
- Càn tam liên (3 vạch liền) · Khôn lục đoạn (6 đoạn)
- Chấn ngưỡng vu · Cấn phúc uyển · Ly trung hư · Khảm trung mãn
- Đoài thượng khuyết · Tốn hạ đoạn

#### A7. Replace cast logic backend → dùng wiki cast.py
`utils/maiHoaTime.js` đang duplicate logic với `engine/yi_wiki/cast.py`.
Đề xuất: tạo endpoint `/api/yi-wiki/cast` gọi `cast_by_time()` → frontend chỉ call API.
Lợi: 1 source of truth + tự động save Prediction.

---

### 🟡 PHASE B — Sau khi đọc 60-150 trang (Quyển 3 Thể-Dụng)

#### B1. Thể-Dụng phân tích — CORE differentiator
Khi gieo quẻ, hiện đầy đủ:
- Quẻ **THỂ** (chủ thể, anh) — quẻ chứa hào không động
- Quẻ **DỤNG** (việc hỏi, ngoại cảnh) — quẻ chứa hào động
- **Quan hệ ngũ hành Thể-Dụng**:
  - Thể khắc Dụng → tốt (ta thắng)
  - Dụng khắc Thể → xấu
  - Thể sinh Dụng → mất sức
  - Dụng sinh Thể → được hưởng
  - Tỉ hoà → bình
- Apply quy tắc Quái Khí mùa: Thể vượng → mạnh, Thể suy → yếu

#### B2. Thể-Dụng Hỗ Biến chi quyết
Khi xem cùng 3 quẻ (Chính + Hỗ + Biến):
- Hỗ quái = **diễn biến giữa đường**
- Biến quái = **kết quả tương lai**
- Đánh giá tổng: tốt / xấu / bình

#### B3. Cải tiến PersonalQuaiPanel
Mỗi ngày trong 30 ngày tới:
- Lấy quẻ ngày đó
- Xét Thể-Dụng với quẻ bản mệnh anh
- Chấm điểm sinh-khắc → hài hoà

---

### 🟣 PHASE C — Sau khi đọc 100+ trang (Case studies + alternative methods)

#### C1. Library of Master Cases
Sách Mai Hoa trang 64+ có loạt case study nổi tiếng:
- Quan Mai Hoa (Thiệu nhìn mai → đoán 2 chim đập gãy cành → đứa trẻ ngã)
- Tây Lâm Tự bài ngạch chiêm (đoán biển treo chùa)
- Người hàng xóm gõ cửa (mượn cuốc / mượn búa)
- Thiếu niên có sắc vui mừng

→ Build component `MasterCasesGallery.vue`:
- Mỗi case: hoàn cảnh → input → quẻ → kết quả Thiệu đoán → kết quả thực
- Anh có thể "thử lại" trên quẻ tương tự

#### C2. Alternative cast modes (trang 46-61)
- Vật số chiêm (gieo qua đếm số vật)
- Thanh âm chiêm (gieo qua âm thanh nghe được)
- Tự chiêm (gieo qua số chữ — 1 chữ, 2 chữ, 4 chữ, 5 chữ, 11 chữ)
- Trượng xích chiêm (gieo qua chiều dài)
- Xem cho người (gieo qua quan sát người khác)

→ Tab phụ "Gieo qua đối tượng khác (ngoài thời gian)"

---

## 4. Đề xuất ĐỌC TIẾP để bổ sung

| Phần sách | Trang | Vai trò cho UI |
|---|---|---|
| Các pp chiêm khác | 46-61 | Cần cho PHASE C (alternative cast) |
| Bát quái phương vị đồ | 62-63 | Có thể visualize Tiên/Hậu Thiên Đồ thật |
| ⭐ **Case studies cổ điển** | 64-90 | **CỰC KỲ QUAN TRỌNG** — base cho Master Cases Library |
| Quyển 3 (Thể-Dụng) | ~150+ | **MUST READ** — base cho PHASE B |
| Quyển 5 (tượng từng quẻ) | ~400+ | Bổ sung tooltip mỗi quẻ |

**Em đề nghị**: Đọc tiếp **đến hết case study của Thiệu (trang 90)** trước khi build PHASE A. Vì:
- Case studies cho phép em **học cách Thiệu giải quẻ thật**
- Anh sẽ thấy template "quẻ → diễn giải" tự nhiên
- Em không phải đoán mò khi viết UI

---

## 5. Quick wins làm ngay (1 commit)

Em có thể trong 1 session làm xong PHASE A (A1-A7) — ước lượng:
- A1 (TabIntro) — 5 phút
- A2 (Save Prediction API + UI) — 30 phút
- A3 (Cross-ref tooltip) — 20 phút
- A4 (Quái Khí badge) — 15 phút
- A5 (Ngoạn Pháp note) — 5 phút
- A6 (Mnemonics) — 10 phút
- A7 (Backend cast endpoint) — 25 phút

**Tổng**: ~2 giờ work. Anh OK em làm luôn?

---

## 6. Nguyên tắc thiết kế (theo paradigm anh)

| Paradigm | Áp dụng vào UI Mai Hoa |
|---|---|
| Author-Worldview-First | TabIntro phải attribute Thiệu Khang Tiết + link Wiki Tổ sư |
| Procedural grimoire | UI nhấn mạnh **CÁCH GIEO + ĐỌC** thật sự, không phải dictionary khô |
| Master-Apprentice | Mỗi quẻ trên UI có "Thiệu sẽ giải sao" (sau khi em đọc case studies) |
| Động tâm | Prediction phải capture moment anh click + tam_note |

---

**Kết luận**:
1. Lõi toán cũ đúng chuẩn Mai Hoa, không phải làm lại
2. Phần diễn giải còn thiếu — 8 gap đã liệt kê
3. Em đề xuất đọc tiếp đến trang 90 (case studies Thiệu) trước khi build PHASE A
4. Sau đó build PHASE A trong ~2 giờ
5. Phase B + C cần thêm 200+ trang
