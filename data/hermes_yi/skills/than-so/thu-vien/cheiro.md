# Cheiro — Sách Về Những Con Số

> Cheiro / Louis Hamon (1926) · Public domain · `data/restored_books/cheiro-book-of-numbers/`
> OCR: `source/cheiro-book-of-numbers-ocr.txt` · PDF publish core v0.2

## Cống hiến đã wire vào engine

1. Bảng Chaldean (9 linh thiêng, không gán chữ) → `letter_maps.json`
2. Số kép **10–52** (Ch.XIII OCR) → `chaldean_compound_numbers.json` + `library.resolve_compound`
3. Hành tinh số đơn → `cross_bind` cheiro_planet
4. Cast `cross_reference.name_compound_flat` — cộng tràn tên Chaldean + tra kép

## Alias quan trọng (OCR)

- 33→24, 34→25, 35→26, 36→27, 38→29… 52→43
- **Lực riêng**: 37 (tình thân/hợp tác), 43 (đảo loạn), 51 (chiến binh)

## Paradigm

Cheiro viết may/cảnh báo → YI đọc thành **sắc thái cấu trúc cần quan-sát**, không predict.

## File

- restored content + OCR + published PDF
- `library_provenance.json`
