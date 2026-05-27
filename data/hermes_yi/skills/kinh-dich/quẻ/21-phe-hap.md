---
name: kinh-dich-21-phe-hap
description: Quẻ Phệ Hạp 噬嗑 — cắn để hợp. Trong miệng có vật ngăn cách → phải cắn mới hợp. Lợi dùng hình ngục.
metadata:
  hermes:
    tags: [kinh_dich, quẻ, Reference, LongContext]
    routing_mode: long
    routing_keys: [can-de-hop, hinh-nguc, tru-cuong-nganh-sam-ta, sang-soi-oai-nhuc]
    cross_ref:
      mai_hoa: [chiem-quan-tung]
      tu_vi: [cung-quan-loc]
      bookflow: [refactor-tru-code-rac]
  source:
    pages_orig_raw_ocr: "382-396"
    note: "Bypass content.md bug (Phệ Hạp bị thiếu — task #73). Đọc raw_ocr trực tiếp."
  curated_at: 2026-05-27 cuối ngày (sửa từ stub)
---

# Quẻ 21 — Phệ Hạp 噬嗑 · ☲☳ (Ly trên, Chấn dưới — chớp trên sấm)

## Tóm cốt

**Phệ = cắn, Hạp = hợp**. Trong miệng có vật ngăn cách → phải cắn vật ấy đi mới hợp lại được. Tượng quẻ: trên dưới 2 hào cứng (mép), giữa rỗng (khoang miệng), 1 hào Dương ở giữa (Cửu Tứ — vật ngăn).

Tiếp sau Quán (đáng xem rồi mới có kẻ đến hợp). Lý dòng từ Quán → Phệ Hạp: muốn hợp thì phải trừ cái ngăn cách.

## Lời Kinh

> 噬嗑亨, 利用獄.
>
> _Phệ hạp hanh, lợi dụng ngục._
> Phệ hạp hanh, lợi dùng việc ngục.

## Lời Thoán

> _"Dị trung hữu vật, viết Phệ hạp."_ (Khoang giữa có vật, gọi là Phệ hạp.)

## Trình Di Truyện — paradigm thiên hạ

> _"Việc trong thiên hạ sở dĩ không hanh thông là vì có chỗ ngăn cách; cắn mà hợp lại thì hanh thông rồi... Trong thiên hạ thì có kẻ cường ngạnh, hoặc kẻ sàm tà, ngăn cách ở giữa, cho nên việc trong thiên hạ không thể hợp được; phải dùng hình pháp — nhỏ thì trừng giới, lớn thì giết chóc, để trừ bỏ đi, rồi sau cuộc trị thiên hạ mới thành."_

→ **Paradigm cốt**: Sự không hanh thông luôn có **NGUYÊN NHÂN cụ thể** (vật ngăn). Không phải tự nhiên. Tìm + trừ vật ngăn = hanh.

## Chu Hy Bản nghĩa — vì sao "lợi dụng ngục" mà không "lợi dụng hình"

> _"Không nói 'lợi dùng việc hình' mà nói 'lợi dùng việc ngục', là vì trong quẻ có tượng sáng soi, lợi về sự xét ngục vậy. Ngục là để xét trị sự thật sự dối."_

→ **Insight**: Phệ Hạp KHÔNG phải đập kẻ cường — mà là **XÉT cho ra sự thật** rồi mới dùng hình. _"Biết được tình thật, thì biết cái đạo làm cho ngăn cách, rồi mới có thể đặt ngăn ngừa và dùng hình phạt."_

## 2 thể quẻ — sáng soi + oai nhức

- Ly (chớp) trên = sáng soi
- Chấn (sấm) dưới = oai nhức

→ Tượng tốt cho **xét ngục công bằng**: vừa sáng soi sự thật vừa có oai nhức trừ ác.

## 6 hào — 5 cấp dùng hình (skim)

| Hào | Lời | Tâm pháp |
|---|---|---|
| Sơ Cửu | Lý hiệu diệt chỉ | Mang gông cùm hủy ngón chân — răn nhỏ trừ to |
| Lục Nhị | Phệ phu diệt tỵ | Cắn da mềm đến lút mũi — hình phạt người cương cường |
| Lục Tam | Phệ tích nhục, ngộ độc | Cắn thịt khô gặp độc — ngôi không đáng, có hối nhỏ |
| Cửu Tứ | Phệ can chí, đắc kim thỉ | Cắn xương khô, được tên vàng — gặp việc khó, lợi gian trinh |
| Lục Ngũ | Phệ can nhục, đắc hoàng kim | Cắn thịt khô, được vàng — vua xét ngục, trinh lệ vô cữu |
| Thượng Cửu | Hà giáo diệt nhĩ | Mang gông cùm đến nỗi mất tai — không nghe răn → hung |

## Cross-ref

### Engine output cảnh báo

- Phệ Hạp paradigm: trước khi cảnh báo user → phải **XÉT** (như xét ngục): tình huống có thật không? Có vật ngăn cụ thể nào? KHÔNG cảnh báo lung tung.
- Engine `safety_check.py` Tử Vi = Phệ Hạp ở scale nhỏ: phát hiện pattern hung → xét hoàn cảnh user → cảnh báo có sáng soi.

### Bookflow refactor

- Code legacy có "vật ngăn cách" → phải cắn (refactor). Q3 v1.12 NOT-FINAL = Phệ Hạp paradigm.
- Privacy audit 2026-05-27: phát hiện rò founder = vật ngăn cách giữa user và an toàn → xét + cắn (vá) → hanh.

### Multi-school respect

- Khi 2 trường phái mâu thuẫn → có "vật ngăn cách" → phải xét (như Tụng paradigm) + có thể cắn 1 phía nếu phái đó sai (Phệ Hạp) hoặc kept_all (Tụng trung cát).

## Cảnh báo

❌ **Cắn lung tung**: dùng hình không xét = mất công bằng. _"Hà giáo diệt nhĩ"_ (mang gông đến mất tai) = không nghe răn từ đầu → hung.
✅ **Sáng soi + oai nhức**: xét cho ra sự thật trước, rồi mới hình. Mai Hoa Sage paradigm cùng cốt với Phệ Hạp ở chỗ này.
