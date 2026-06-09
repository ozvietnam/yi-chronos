# KẾ HOẠCH ATOMIZE v2 — STRICT BÁM SÁCH

**2026-06-09 — sau khi Anh nói "ẩu"**

---

## 🎯 GOAL CUỐI

Build kho **168 atom-section** (12 cung × 14 sao) cho Trung Châu Q2 Chương 5 — atoms **bám TEXT 100%**, không Claude general knowledge.

### Vì sao cần kho này:
1. **3-Layer output cho user**: atom là nguyên liệu để `output_filler.py` compose 3 lớp ("Chuyện về anh / Vì sao / Sách cổ nói")
2. **Section-priority retrieval**: khi user hỏi "Sao X ở cung Y", retriever lấy atoms section tương ứng FIRST
3. **Founder verify dễ**: mỗi atom 1 source_quote — anh tick ✅/⚠/❌

---

## 🚫 ANTI-PATTERN (lesson "ẩu" 2026-06-09)

| Đã làm sai | Sửa từ giờ |
|---|---|
| viet_thuan + nguyen_ly + ví dụ bằng Claude knowledge | PARAPHRASE TEXT — KHÔNG diễn rộng |
| Compress 4 trang → 7-8 atoms | Atom dày — mỗi paradigm con 1 atom riêng |
| confidence 0.95 — tự tick ✅ | confidence 0.85 — chờ founder verify |
| Hardcode commentary từ chat | Sub-agent parse text → output JSON |
| 1 process tự làm tất cả | Sub-agent parallel — 1 sub-agent / 1 section |

---

## 📐 SCHEMA BÁM SÁCH

```json
{
  "question_id": "tcq2-5.1.X-Q01",
  "question": "Sao X ở cung Y, gặp [điều kiện] thì sao?",
  "answer_atom": "[paraphrase text]",
  "source_quote": "[trích nguyên văn từ text]",
  "source_page": 521,
  "section_id": "5.1.6",
  "tags": ["star:X", "palace:menh", "condition:..."],
  "commentary": {
    "han_viet_explain": "[NULL hoặc giải nghĩa thuật ngữ Hán-Việt CÓ trong source_quote]",
    "viet_thuan": "[PARAPHRASE text Việt thuần — KHÔNG thêm gì]",
    "nguyen_ly": "[NULL nếu text không nói nguyên lý]",
    "vi_du_doi_song": "[NULL trừ khi sách có ví dụ]",
    "iron_rule_warning": "[NULL trừ khi sách có cảnh báo paradigm]"
  },
  "confidence": 0.85,
  "extracted_by": "sub-agent-bam-sach"
}
```

---

## 🏗️ PHASE BREAKDOWN

### Phase A — Setup (NOW, ~5 phút)
- [x] A.1: Write plan này
- [ ] A.2: Sub-agent prompt template
- [ ] A.3: Insert script

### Phase B — Cung Mệnh 5.1.6 → 5.1.14 (~30 phút)
Spawn 9 sub-agents parallel:
- 5.1.6 Liêm Trinh (p521-524, 4 trang)
- 5.1.7 Thiên Phủ (p525-527, 3 trang)
- 5.1.8 Thái Âm (p528-532, 5 trang)
- 5.1.9 Tham Lang (manifest skip — em check riêng)
- 5.1.10 Cự Môn (p533-535, 3 trang)
- 5.1.11 Thiên Tướng (p536-538, 3 trang)
- 5.1.12 Thiên Lương (p539-546, 8 trang)
- 5.1.13 Thất Sát (manifest skip — em check riêng)
- 5.1.14 Phá Quân (p547-549, 3 trang)

### Phase C — Re-do 5.1.1 → 5.1.5 (~15 phút)
Spawn 5 sub-agents replace atoms ẨU cũ với output bám sách 100%.

### Phase D-L — 11 cung còn lại (~4h, chia nhiều phiên)
5.2 Huynh Đệ → 5.3 Phu Thê → ... → 5.12 Phụ Mẫu. Mỗi cung ~25 phút.

### Phase Z — Verify với anh
- Export MD review per cung
- Anh tick ✅/⚠/❌
- Atoms ✅ → upgrade confidence 0.95 + founder_verified=1
- Atoms ❌ → mark obsolete

---

## ⏱ THỜI GIAN PHIÊN NÀY

Phase A + B + C trong phiên hôm nay (~1h).
Phase D+ — sau khi anh confirm quality Phase B+C OK.

---

## 🔒 NGUYÊN TẮC EM CAM KẾT

1. **KHÔNG sinh content general** — chỉ paraphrase text
2. **NULL hơn diễn bừa** — nếu text không nói, để NULL
3. **Atom dày hơn** — không compress trang sách
4. **confidence 0.85 cho atom draft** — chờ verify
5. **founder_verified=0** — anh là người tick cuối
6. **Sub-agent đọc text độc lập** — em không inject Claude knowledge vào prompt
