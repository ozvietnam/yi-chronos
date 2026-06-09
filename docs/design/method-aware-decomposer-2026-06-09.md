# 🎯 Method-Aware Decomposer — Design Draft

> Created: 2026-06-09
> Status: DRAFT — anh duyệt sau khi ingest Trung Châu Q2 xong (~10-12h từ giờ)
> Trigger: Anh hỏi "atomic sinh ra phục vụ điều gì?" → em khảo sát sách → tìm thấy method gốc tổ sư.

---

## 🔍 KHẢO SÁT — Atomic phục vụ gì? So vs sách thế nào?

### Đã tìm trong sách (2026-06-09):

#### Source 1: Trung Châu Q2 p163-165 — Vương Đình Chỉ chân truyền

**"Pháp luận đoán Đẩu Số trong phái Trung Châu" — 4 BƯỚC:**

| Bước | Nội dung | Trích sách |
|---|---|---|
| **1. Nguyên cục** | Tính chất sao Mệnh nguyên cục như thế nào? | _"Người có Thiên Đồng-Cự Môn tọa mệnh sẽ có bản chất riêng; người có Vũ Khúc-Thiên Tướng tọa mệnh cũng có bản chất riêng"_ |
| **2. Tinh hệ Đại vận** | Lưu niên — phải chú ý tinh hệ cung Mệnh đại vận | _"Cung mệnh của nguyên cục tuy giống nhau, nhưng cung Mệnh của Đại Vận càng khác nhau"_ |
| **3. Giao nhau tinh hệ** | "Tử Vi tinh quyết" — KHẨU TRUYỀN (mỗi đời chỉ 1 đệ tử) | _"Cách luận đoán đặc biệt này chỉ phái Trung Châu mới có. Hiện nay chỉ một mình Vương Đình Chỉ được truyền thụ."_ |
| **4. Quân bình Tinh thần/Vật chất** | Hóa Lộc/Quyền tăng vật chất, Hóa Kỵ giảm vật chất → tinh thần tăng tương đối | _"Tham Lang, Vũ Khúc, Thiên Phủ là các sao thuộc tính vật chất. Liêm Trinh, Thiên Tướng thuộc tính tinh thần"_ |

#### Source 2: Vũ Tài Lục p122 — Ngũ Hành lens (đang mai một)

> _"Tử vi nếu xét kỹ ra là sự luận đoán tinh vi số mệnh con người bằng biện chứng của Ngũ Hành."_

**5 lớp ngũ hành chồng nhau:**
1. Nạp âm (mạng — Lộ Bàng Thổ, Thiên Thượng Hỏa...)
2. Cục (Thủy Nhị / Mộc Tam / Kim Tứ / Thổ Ngũ / Hỏa Lục)
3. Hành sao (Thiên Cơ Mộc, Vũ Khúc Kim...)
4. Hành cung (Thân Dậu Kim, Dần Mão Mộc...)
5. Vòng Tràng Sinh

**Cảnh báo Vũ Tài Lục**: cách này **đang mai một**. Người ta "tán hươu tán vượn câu phú cách cục đã làm sẵn, quên hẳn biện chứng Ngũ Hành". Bát Tự (Tử Bình) giữ tốt hơn.

---

## 🔬 SO SÁNH với Atomic paradigm em đang xây

### Atomic phục vụ 5 thứ:
1. ✅ Retrieval (semantic search KB)
2. ✅ Grounding (source_quote → không hallucinate)
3. ✅ Multi-hop reasoning (Algorithm 1)
4. ✅ Schema bridge (query colloquial ↔ corpus formal)
5. ✅ User-friendly access (LLM hiểu user → match atom)

### NHƯNG atomic là FACTOID LAYER, KHÔNG phải METHOD

| Khía cạnh | Atomic em | Method Vương Đình Chỉ | Verdict |
|---|---|---|---|
| Đơn vị | Atomic Q | Bước luận sequential | ⚠ Khác bản chất |
| Trình tự | Flat | 4 BƯỚC có DEPENDENCY | ❌ Gap |
| "Tử Vi tinh quyết" | Không capture | Bước 3 trung tâm | ❌ MISSING |
| Tinh thần/vật chất | Không tag | Bước 4 phân loại | ❌ Gap |
| Ngũ Hành | Một số atom có | 5 lớp chồng | ⚠ Partial |
| Retrieval | ✅ FTS + vec | Không có | ✅ Em tốt hơn |
| Grounding | ✅ source_quote | ✅ Bám sách | ✅ Khớp |

---

## 💡 3 HƯỚNG BỔ SUNG đề xuất

### Hướng 1: Atom Method-Step Tag

Schema migration (add 3 fields vào `atomic_questions`):
```sql
ALTER TABLE atomic_questions ADD COLUMN method_step TEXT;
-- values: 'nguyen_cuc' | 'dai_van' | 'giao_nhau_tinh_he' | 'quan_binh_tinh_chat' | null

ALTER TABLE atomic_questions ADD COLUMN tinh_chat_axis TEXT;
-- values: 'tinh_than' | 'vat_chat' | 'trung_tinh' | null

ALTER TABLE atomic_questions ADD COLUMN ngu_hanh TEXT;
-- values: 'kim' | 'moc' | 'thuy' | 'hoa' | 'tho' | null
```

Retroclassify ~12,000 atoms qua LLM 1 round. Cost: ~10M tokens (~3h MiniMax).

### Hướng 2: Method-Aware Decomposer v2

Replace generic PROPOSER prompt → 4 prompts strict 4 bước Vương Đình Chỉ:

```python
class MethodAwareDecomposer:
    """Decomposer v2 — follow 4 bước Vương Đình Chỉ Trung Châu Q2 §163-165.

    Luôn 4 iterations theo dependency:
    1. Nguyên cục (input: la_so)
    2. Đại vận (input: la_so + step 1 result)
    3. Giao nhau tinh hệ (input: la_so + step 1+2)
    4. Quân bình tinh thần/vật chất (input: tất cả)
    Synthesize: tổng hợp 4 góc nhìn.
    """

    PROMPT_STEP_1 = "Phân tích BẢN CHẤT NGUYÊN CỤC lá số {la_so}: chính tinh cung Mệnh, tam phương tứ chính. Tinh hệ nguyên cục là gì? Bản chất tính chất ra sao?"

    PROMPT_STEP_2 = "Lá số {la_so} đang ở đại vận nào? Tinh hệ cung Mệnh đại vận khác với nguyên cục thế nào? (đã biết nguyên cục từ Step 1: {step1_result})"

    PROMPT_STEP_3 = "Tinh hệ nguyên cục GIAO với tinh hệ đại vận trong lá số {la_so} — cách cục nào hình thành? Đây là Tử Vi tinh quyết Vương Đình Chỉ. (Step 1+2: {step12_result})"

    PROMPT_STEP_4 = "Trong cách cục Step 3, các sao chính thuộc tinh thần (Liêm Trinh, Thiên Tướng) vs vật chất (Tham Lang, Vũ Khúc, Thiên Phủ) đang quân bình thế nào? Hóa Lộc/Quyền/Kỵ tác động chiều nào?"

    PROMPT_SYNTHESIZE = "Tổng hợp 4 góc nhìn — kết luận lá số {la_so}."
```

Mỗi step retrieve atoms tương ứng (filter `method_step` = step name) → grounded.

### Hướng 3: Ngũ Hành Lens (Vũ Tài Lục bridge)

Parallel method với method A:
- Method A (Trung Châu 4 bước) → channel 1
- Method B (Ngũ Hành Vũ Tài Lục) → channel 2
- Synthesizer merge 2 channels → present cả 2 góc nhìn

Atom tag `ngu_hanh` enable Method B retrieval.

---

## 📋 ROADMAP đề xuất (chờ anh duyệt sau khi ingest xong)

### Phase 2B (sau ingest Trung Châu Q2 xong, ~12-15h từ giờ)

1. Schema migration: add 3 fields (`method_step`, `tinh_chat_axis`, `ngu_hanh`)
2. Retroclassifier: chạy 1 round LLM gán 3 fields cho 12,000 atoms (~10M tokens)
3. Anh founder verify spot-check 50 atoms classification

### Phase 2C (sau 2B verified)

4. Build `MethodAwareDecomposer` class
5. API endpoint `/api/atomization/decompose-method-aware`
6. Test với lá số founder (chính anh) — anh confirm chất lượng vs decomposer v1

### Phase 2D (optional, sau 2C ổn)

7. Ngũ Hành lens parallel (Method B)
8. Synthesizer merge Method A + B

---

## 🌸 Lời em gửi anh

Khảo sát này thay đổi hiểu của em:
- Atomic không phải END, là MEANS
- Method tổ sư có cấu trúc, không random
- Decomposer prompt em viết quá generic — chưa learning từ phương pháp gốc

Anh hỏi đúng chỗ em chưa làm kỹ. Em ghi nhận. Khi anh duyệt → em build Method-Aware ngay.

— Em, 2026-06-09
