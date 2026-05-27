---
name: kinh-dich-06-tung
description: Quẻ Tụng 訟 — kiện tụng, tranh biện. "Trung cát, chung hung" — vừa phải tốt, theo đuổi đến chót xấu.
metadata:
  hermes:
    tags: [kinh_dich, quẻ, Reference, LongContext]
    routing_mode: long
    routing_keys: [kien-tung, tranh-bien, biet-dung-lai, khong-theo-duoi-den-cung]
    cross_ref:
      mai_hoa: [chiem-quan-tung]
      tu_vi: [cung-thien-di-quan-loc]
      bookflow: [tranh-luan-engine-vs-engine]
      multi_school: [iron-rule-3-multi-school-respect]
  source:
    pages_orig: "195-204"
    journal_section: "XV.Quẻ Tụng (đợt 3)"
  curated_at: 2026-05-27
---

# Quẻ 6 — Tụng 訟 · ☰☵ (Kiền trên, Khảm dưới — trời lên, nước xuống)

## Tóm cốt

Tiếp sau Nhu (chờ + ăn uống): cần dùng thì sinh tranh — tụng. **Trên cứng (Kiền) dưới hiểm (Khảm)** = cứng + hiểm gặp nhau → kiện. Trong người: **bên trong hiểm trở, bên ngoài cường cường** → sinh tranh.

## Lời Kinh — "Trung cát, chung hung"

> 訟, 有孚窒惕, 中吉, 終凶, 利見大人, 不利涉大川.
>
> _Tụng, hữu phu chất Dịch, trung cát, chung hung, lợi kiến đại nhân, bất lợi thiệp đại xuyên._
> Kiện: có thật, bị lấp, phải sợ. **Vừa phải, tốt; theo đuổi đến chót, xấu**. Lợi thấy người lớn, không lợi sang sông lớn.

**Insight cốt nhất**: **"Trung cát, chung hung"** — biết dừng vừa phải thì tốt, theo đuổi đến cùng thì xấu. KHÔNG cãi đến cùng dù mình đúng.

## Trình Di Truyện (cốt)

> _"Trung cát nghĩa là vừa phải thì tốt, chung hung nghĩa là theo đuổi công việc tới cùng thì xấu. Kẻ kiện cần để phân biệt cong ngay, cho nên lợi về sự thấy người lớn, vì rằng người lớn dùng đức cương minh trung chính quyết đoán việc kiện của họ. Kiện không phải là việc hòa bình, nên chọn chỗ yên ổn mà ở, không nên hăm vào chốn nguy hiểm."_

→ Có sự thật **bị lấp** → bị oan → biết sợ → tìm người lớn quyết đoán. NHƯNG: không sang sông lớn (không bước vào chốn nguy thêm).

## 3 nguyên tắc rút từ Tụng

1. **Kiện phải có sự thật** — không thật là kiểu "Vô vọng" (đạo hung). Engine output sai sự thật = kiểu Vô vọng.
2. **Trung cát, chung hung** — biết dừng đúng lúc. Tranh luận đến cùng = thua dù thắng.
3. **Lợi kiến đại nhân, bất lợi thiệp đại xuyên** — tìm người trung lập quyết, KHÔNG bước thêm vào nguy hiểm.

## Cross-ref

### Iron Rule #3 — Multi-school respect

Anh đã nói: _"Multi-school respect: mỗi trường phái độc lập, có đối chiếu chéo, KHÔNG ép vào 1 trường phái duy nhất. Conflict mappings → present cho anh duyệt (kept_all hợp lệ — đa phái mỗi cái đúng trong context riêng)."_

→ Đây CHÍNH LÀ **Tụng Trung Cát**. Khi 2 trường phái mâu thuẫn → KHÔNG ép 1 phái thắng (chung hung), giữ cả 2 (trung cát). Anh là "đại nhân" quyết đoán (kept_all).

### Engine vs Engine

- Tử Vi Sage nói A, Mai Hoa Sage nói B → conflict
- KHÔNG ép 1 sage thắng (chung hung)
- Present anh quyết hoặc kept_all (trung cát)

### Bookflow

- Q3 v1.12 vs v1.9: nếu cứ tranh "v1.9 đã publish rồi, không sửa" → chung hung
- Mark v1.12 NOT-FINAL + chờ v3.0 rebuild = trung cát + lợi kiến đại nhân (Bookflow paradigm là "đại nhân")

### Privacy audit

- Em phát hiện rò founder data → tranh luận về paradigm cũ (Sage cũ default founder) → biết dừng + vá ngay (trung cát) thay vì cãi giữ paradigm cũ (chung hung)

## Cảnh báo

❌ **Cãi đến cùng dù mình đúng** = chung hung. Engine output absolute correct nhưng user không cần = chung hung.
❌ **Sang sông lớn** trong khi đang tranh = đi thêm vào nguy hiểm. Đừng ship hot feature giữa tranh luận engine architecture.
✅ **Trung cát** = biết dừng đúng lúc + tìm người ngoài quyết.
