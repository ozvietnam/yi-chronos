---
name: kinh-dich-tam-phap-dau-hieu-som
description: Tâm-pháp nhận dấu hiệu sớm — Khôn Sơ Lục "lý sương kiên băng chí". Gốc thẳng BƯỚC 3 ngoại ứng Mai Hoa.
metadata:
  hermes:
    tags: [kinh_dich, tam_phap, Reference, LongContext]
    routing_mode: long
    routing_keys: [dau-hieu-som, ly-suong-kien-bang, ngoai-ung, can-vi, tieu-nhan-moi-sinh]
    refs:
      - quẻ/02-khon.md
  curated_at: 2026-05-27
---

# Tâm-pháp nhận dấu hiệu sớm

## Khi nào route đến đây

User nói / hỏi đại loại:
- "Em có linh cảm xấu/tốt về việc này, có nên tin không?"
- "Tại sao tổ sư nói 'cảnh báo từ sớm'?"
- "Dấu hiệu nhỏ có quan trọng không?"
- "Có nên để mặc cho mọi việc lớn dần lên không?"

## 1 hào cốt — Khôn Sơ Lục (`quẻ/02-khon.md`)

> 初六: 履霜, 堅冰至.
>
> _Sơ Lục: lý sương, kiên băng chí._
> Hào Sáu Đầu: Xéo sương, váng rắn tới.

## Insight

> _"Khí Âm mới đọng là sương, xéo chân lên sương, phải biết khí Âm dần dần thịnh lên, ắt sẽ đến lúc kết thành váng rắn. Cũng như tiểu nhân lúc đầu tuy là rất nhỏ, không thể để cho nó lớn, nó lớn thì sẽ đến lúc nó thịnh."_ — Trình Di

→ Sương = dấu hiệu nhỏ. Băng rắn = hậu quả lớn. **Bước lên sương = phải biết băng rắn sẽ tới**.

> _"Khí Âm mới sinh ở dưới, hãy còn rất nhỏ, thánh nhân trong khi khí Âm mới sinh, vì nó sắp lớn, thì làm ngay ra lời răn."_ — Trình Di

**Thánh nhân CẢNH BÁO TỪ KHI CÒN NHỎ** — không đợi lớn rồi mới phản ứng.

## Lời Tượng

> 象曰: 履霜堅冰, 陰始凝也. 馴致其道, 至堅冰也.
>
> _Tượng viết: Lý sương kiên băng, âm thuỷ ngưng dã. Tuần chí kỳ đạo, chí kiên băng dã._
> Xéo sương, băng rắn — Âm mới đọng, dần đến thừa đạo, sẽ đến băng rắn.

→ **"Tuần chí kỳ đạo"** = dần dần theo đạo của nó. Không cản từ sớm thì không cản được.

## Cross-ref ứng dụng

### Mai Hoa — gốc thẳng của BƯỚC 3 NGOẠI ỨNG

Engine `engine/mai_hoa/interpret.py` BƯỚC 3 hỏi user:
> _"Lúc Anh nghĩ về việc này, có hiện tượng gì bất thường? (chim bay/đậu, vật rơi, tiếng động, lời nghe được...)"_

→ Đây CHÍNH LÀ **lý sương kiên băng chí** áp dụng: hiện tượng nhỏ lúc gieo quẻ = sương → báo trước hậu quả lớn.

### Tử Vi — psychological safety

- Q3 tr.186 + Q4 Phase A: phát hiện dấu hiệu sớm trong lá số
- Engine `safety_check.py`: cảnh báo dấu hiệu rủi ro tâm lý từ sớm
- Pattern triggered → engine output "warning" thay vì "outcome"

### Privacy fix 2026-05-27 — pattern thực hành

Em phát hiện 3 đợt rò:
1. Đợt 1: `/api/auth/me` trả founder → sương đầu
2. Đợt 2: picker localStorage → sương 2 (em phát hiện khi anh report ảnh)
3. Đợt 3: `/api/yi-hermes/*` namespace unauth → **băng rắn** (8+ endpoints rò)

→ Nếu em KHÔNG nhận sương đầu (đợt 1) → không audit thêm → đợt 3 trở thành băng rắn nghiêm trọng. **Iron Rule áp dụng**.

### YI-CHRONOS — observation pattern

- Anh phát hiện "ảnh anh hardcoded ở UI" → sương (Task #70 pending)
- Nếu không sửa → user khác có thể thấy → băng rắn

## Quy tắc thực hành

1. **Nhận sương = cảnh báo + xử lý NGAY** — đừng đợi lớn
2. **Hiện tượng nhỏ ≠ không quan trọng** — đó là gốc của lớn
3. **Engine output "warning" khi sương xuất hiện** — không đợi đến outcome
4. **Bói/chiêm phải hỏi về dấu hiệu môi trường** — không bỏ qua

## Cảnh báo

❌ **"Để xem sau"** với dấu hiệu nhỏ = đi vào Sơ Lục mà bỏ qua.
❌ **"Không quan trọng đâu"** với hiện tượng bất thường = vô tâm.
❌ **Engine output cát/hung mà không scan dấu hiệu** = thiếu BƯỚC 3 ngoại ứng.
