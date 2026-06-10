# 🏗️ Design — Engine Hoàng Cực & Thiết Bản (khớp kiến trúc YI-Chronos)

> 2026-06-10 · Trạng thái: DRAFT chờ Anh duyệt · Người soạn: em
> Tiền đề: 2 cuốn đã dịch 100%; bảng tra điều văn v1 8.014 điều (v2 ~12k đang ghép từ qwen-VL);
> atoms Hoàng Cực đang đúc (~3.1k lúc soạn). Đọc sâu vòng 1 Quan Vật Nội Thiên đã xong.

---

## 0. Research existing solutions (Iron Rule #1 — đã làm)

| Nguồn | Kết quả | Dùng gì |
|---|---|---|
| [xaminxan/tiebanshenshu](https://github.com/xaminxan/tiebanshenshu) | Calculator Thiết Bản 1 phái (819 dòng Python + CSV bảng số): bát tự → tiên thiên mệnh số → ngũ âm → nhật mệnh/thời vận → khảo khắc → bản mệnh số → quẻ → điều văn bản mệnh + lưu niên 1–108 tuổi | **Tham chiếu FLOW + kiến trúc**, KHÔNG copy bảng số (phái khác, điều văn DB khác). Engine mình bám LỆ TRONG SÁCH MÌNH |
| [Nguyên-Hội-Vận-Thế (wiki + khảo cứu)](https://zh.wikipedia.org/zh-hans/%E5%85%83%E4%BC%9A%E8%BF%90%E4%B8%96) | Quy tắc chuẩn hóa: 1 nguyên = 12 hội = 360 vận = 4.320 thế = 129.600 năm; hội = 10.800 năm; vận = 360 năm; thế = 30 năm; phối 60 quẻ (trừ Càn Khôn Khảm Ly) + can chi + 24 tiết khí | Phép thuần số học → tự viết ~100 dòng. **Mốc lịch + bảng phối quẻ lấy từ chính sách 今说** (sẽ trích khi đọc sâu tới phần đó — KHÔNG bịa) |
| GitHub Hoàng Cực calculator | Không có repo hoàn chỉnh | Tự build (nhẹ) |

---

## 1. Engine `engine/hoang_cuc/` — tầng THỜI CUỘC (đề xuất làm TRƯỚC)

**Vì sao trước**: phép tính chuẩn hóa, rủi ro thấp, lấp đúng khoảng trống dự án — mọi engine hiện có (mai_hoa, tu_vi, bat_tu, ha_lac, ky_mon, luc_hao, than_so) đều là tầng CÁ NHÂN; chưa có tầng THỜI ĐẠI/QUỐC VẬN. Hoàng Cực chính là tầng đó — đặt việc cá nhân vào dòng lớn.

```
engine/hoang_cuc/
├── __init__.py
├── constants.py          # 12 hội (Tý..Hợi), bảng 60 quẻ phối vận/thế (TRÍCH TỪ SÁCH),
│                         # mốc lịch quy chiếu (từ 今说 — đối chiếu 2 thuyết nếu sách nêu)
├── nguyen_hoi_van_the.py # year ↔ (nguyên, hội, vận, thế, năm-trong-thế) + can chi năm
├── que_van.py            # quẻ ứng vận/thế hiện tại + lời quẻ (nối wiki hexagrams_64)
├── cast.py               # cast_hoang_cuc(year=2026) → JSON: vị trí vũ trụ học + quẻ
│                         # + atoms/citations liên quan (gọi atomization retriever)
└── interpret.py          # luận giải paradigm-safe (đọc đồng dạng — Iron Rule #4/#6)
```

- **API**: `POST /api/hoang-cuc/the-cuc` (year → vị trí + quẻ + citations), `GET /api/hoang-cuc/timeline?from=&to=` (dải năm cho UI vẽ trục)
- **METHOD_ID** `hoang_cuc_v1` · **SOURCE_REF** "皇极经世书今说 — Diêm Tu Triện (2007), nguyên trứ Thiệu Khang Tiết"
- **Paradigm guard**: output là "năm X nằm ở hội/vận/thế nào, quẻ gì — phản chiếu cấu trúc thời đoạn", TUYỆT ĐỐI không "năm X sẽ tốt/xấu"
- **Phụ thuộc đọc sâu**: bảng phối quẻ vận-thế + mốc lịch nằm phần sau sách (chương Nguyên-Hội-Vận-Thế) — em đọc vòng 2-3 sẽ trích chính xác; TRƯỚC ĐÓ chỉ code khung + phép chia thời gian (phần chuẩn hóa không cần sách)

## 2. Engine `engine/thiet_ban/` — 2 tầng

### Tầng A — TRA CỨU (ship ngay được, không chờ gì)
```
engine/thiet_ban/
├── __init__.py
├── verses.py             # lookup: theo số điều / tập / dải số; search FTS (VI) + LIKE (ZH)
└── cast.py (tầng B sau)
```
- **API**: `GET /api/thiet-ban/verse/{seq_no}` · `GET /api/thiet-ban/search?q=` · `GET /api/thiet-ban/volume/{tap}`
- Data: `tabular_verses` (v2 sau merge qwen-VL ~12k điều, confidence từng điều)
- UI: panel tra số đơn giản (nhập số → điều văn ZH-VI + trang gốc + ảnh trang)

### Tầng B — PHÉP TÍNH SỐ (CHỜ đọc sâu phần lệ, KHÔNG bịa)
- Phần lệ sách mình (PDF tr.9–105): an Thân Mệnh, ngũ hổ độn, nạp âm, **bảng địa chi phối số Hà Đồ/Lạc Thư**, thiên can/địa chi/nhật chủ phối quẻ, và cả hệ an sao Tử Vi (Xương Khúc, Tả Hữu, Khôi Việt, Tứ Hóa, đại tiểu hạn) → bản này là "quảng bản" kết hợp tinh bàn
- Flow tham chiếu (đã xác minh qua repo + truyền thống): bát tự → số trung gian → **bản mệnh số** → tra điều bản mệnh → **khảo nghiệm lục thân** (điều văn dạng "huynh đệ X người" dùng để xác cục — founder xác nhận đúng/sai, hệ hiệu chỉnh) → dãy điều lưu niên
- **Điều kiện code**: em đọc sâu phần lệ + trích công thức từng bước có số trang; công thức nào sách không nói rõ → flag founder, không suy đoán
- UI tầng B: wizard khảo nghiệm tương tác (hỏi lục thân từng bước — rất hợp UX webapp)

## 3. Khớp hệ sinh thái hiện có

| Mảnh | Nối vào |
|---|---|
| Wiki | concepts trích khi đọc sâu (school `thieu-khang-tiet`); quẻ vận nối `hexagrams_64` |
| Atomization | atoms Hoàng Cực (đang đúc ~6k dự kiến) làm citations cho `cast`; Thiết Bản KHÔNG atomize điều văn (đã chốt — bảng tra) |
| Sage | profile mới `hoang-cuc-sage` theo pattern v0.14 (SOUL = WHO+HOW ~6k, kiến thức route về skill/INDEX) — đợi đọc sâu đủ vòng mới viết SOUL |
| Bookflow | 2 sách tiếp tục vòng đời: thâm nhuần → wiki → (sau) biên soạn PDF publish theo Iron Rule #5 |
| Auth/UI | endpoints công khai đọc, phép cast owner-gated như các engine khác |

## 4. Thứ tự thi công đề xuất (sau khi Anh duyệt)

1. `engine/hoang_cuc` khung + nguyen_hoi_van_the (phần chuẩn hóa) + API + panel timeline — **~1 buổi**
2. `engine/thiet_ban` tầng A tra cứu + panel — **~nửa buổi** (data đã có)
3. Đọc sâu tiếp Hoàng Cực (vòng 2-3) → trích bảng phối quẻ + mốc lịch → hoàn thiện `que_van` — theo nhịp đọc của Anh
4. Đọc sâu phần lệ Thiết Bản → design chi tiết tầng B trình Anh → code
5. Sage profiles + PDF publish — cuối chuỗi

## 5. Câu hỏi mở cho Anh

1. Thứ tự 1→2 (Hoàng Cực trước, Thiết Bản tra cứu sau) ổn không, hay Anh muốn ngược?
2. Panel Hoàng Cực: Anh muốn trục thời gian nhìn được cả đời mình đặt trong vận/thế (overlay năm sinh→nay) không? (Em thấy đây là điểm "chạm" nhất.)
3. Tầng B Thiết Bản cần wizard khảo nghiệm tương tác — Anh có muốn em ưu tiên sớm hơn để Anh tự nghiệm trên bát tự mình?
