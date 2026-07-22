# Cheiro — Sách Về Những Con Số

> Cheiro / Louis Hamon (1926) · Public domain · `data/restored_books/cheiro-book-of-numbers/`
> OCR: `source/cheiro-book-of-numbers-ocr.txt` · PDF publish core v0.2

## Cống hiến đã wire vào engine

1. Bảng Chaldean (9 linh thiêng, không gán chữ) → `letter_maps.json`
2. Số kép **10–52** (Ch.XIII OCR) → `chaldean_compound_numbers.json` + `library.resolve_compound`
3. Hành tinh số đơn → `cross_bind` cheiro_planet
4. Cast `cross_reference.name_compound_flat` — cộng tràn tên Chaldean + tra kép
5. **Birth Day 1–9** (Ch.III–XI) → `cheiro_birth_numbers.json` + dual lens trong `deep_reading` (không ghi đè Decoz)
6. Nguyên lý C0–C8 → `interpretation_principles.json` **v2**

## Vòng thâm nhuần (citation)

| Vòng | Journal | Phạm vi |
|---|---|---|
| C0 | `docs/design/than-so-thu-vien-tham-nhuan.md` | I–II, XII–XV, XVII, XXIV |
| C1 | `docs/design/than-so-cheiro-tham-nhuan-vong-C1.md` | III–VII số 1–5 |
| C2 | `docs/design/than-so-cheiro-tham-nhuan-vong-C2.md` | VIII–XI số 6–9 |
| C3 | `docs/design/than-so-cheiro-tham-nhuan-vong-C3.md` | XII–XIII compound audit |
| C4 | `docs/design/than-so-cheiro-tham-nhuan-vong-C4.md` | XIV–XVI Name↔Birth |
| C5 | `docs/design/than-so-cheiro-tham-nhuan-vong-C5.md` | XVII–XXI recurrence |
| C6–C8 | `docs/design/than-so-cheiro-tham-nhuan-vong-C6-C8.md` | XXII–XXXIII + biên giới XXX |

## Alias quan trọng (OCR)

- 33→24, 34→25, 35→26, 36→27, 38→29… 52→43
- **Lực riêng**: 37 (tình thân/hợp tác), 43 (đảo loạn), 51 (chiến binh)

## Conflict đa phái (#3)

Birth Day Cheiro **3 / 4 / 9** lệch Decoz → `cheiro_birth_numbers.conflict_digits` — present BOTH.

## Biên giới cứng

- Ch.XXVIII disease → **không** chẩn bệnh / kê thuốc theo số
- Ch.XXX horse-racing → **tuyệt đối từ chối** SKU cá cược / xổ số (*A little knowledge is a dangerous thing*)

## Paradigm

Cheiro viết may/cảnh báo → YI đọc thành **sắc thái cấu trúc cần quan-sát**, không predict.

## File

- restored content + OCR + published PDF
- `library_provenance.json`
- `data/than_so/master/cheiro_birth_numbers.json`
