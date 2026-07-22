# Kế hoạch thâm nhuần thư viện Thần Số Học — ĐÓNG (nguồn trong repo)

> Cập nhật cuối: 2026-07-22 · Branch PR #70  
> Paradigm: đồng dạng · không predict · #3 đa phái · #7 git · #9 biên giới

---

## Checklist

### Cheiro
- [x] C0–C8 (journals + inject dual lens + principles v2 + cấm cá cược/y tế)

### Balliett (Track B — PD OCR IA)
- [x] B0 stub
- [x] B1 foundations + tone/color JSON
- [x] B2 practical / money / gems / rooms boundaries
- [x] B3 Life Song keynote + Spiritual Birthday (chart in-book OCR mất — honest)

### Campbell
- [x] P0 stub + Inclusion audit (+ intensity)
- [ ] P1+ full text — **chờ 2027** / Anh cho phép

### Master
- [x] M1–M4

---

## Definition of Done — thư viện **đang có**

1. [x] Cheiro I–XXXIII journals  
2. [x] Balliett OCR + B0–B3 (không pretend chart mất)  
3. [x] Campbell P0 trung thực (method only)  
4. [x] principles v2 + hermes `than-so/` citations  
5. [x] Engine: Name↔Birth · Cheiro layers · Inclusion · Balliett tone/Life Song · dual lens 3/4/9  
6. [x] Không feature cá cược / chẩn bệnh / lucky color shopping  

**Ngoài DoD (không bịa):** Goodwin/Jordan · Campbell nguyên văn · Life Song chart scan đẹp.

---

## Journals chính

| Vòng | File |
|---|---|
| C0 | `than-so-thu-vien-tham-nhuan.md` |
| C1–C8 | `than-so-cheiro-tham-nhuan-vong-C*.md` |
| B0–B3 | `than-so-balliett-tham-nhuan-vong-*.md` |
| P0 | `than-so-campbell-tham-nhuan-vong-0.md` |
| M1–M3 | `than-so-master-tham-nhuan-M1-M3.md` |
| Kế hoạch | file này |

---

## Engine hooks (tóm)

- `cheiro_birth_numbers` · `resolve_cheiro_birth` · dual lens birthday  
- `balliett_tone_color` · `resolve_balliett_tone` · `balliett_birth_digit` · `balliett_life_song` · Spiritual Birthday days  
- Inclusion average · compatibility `cheiro_vi`  
- principles: `betting_refusal` · `medical_boundary` · `balliett_*`
