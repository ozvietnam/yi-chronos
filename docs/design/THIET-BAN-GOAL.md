# THIẾT BẢN THẦN SỐ — GOAL & Cách Đọc Đúng Đạo

> La-bàn cho mọi việc về Thiết Bản (铁板神数). Có GOAL này rồi thì **tự chạy**, không hỏi vặt.
> Lập 2026-06-16 theo yêu cầu founder ("phải có GOAL thì không phải hỏi nhiều").

---

## GOAL — một câu

**Làm sáng tỏ những điều ĐÃ ĐỊNH của một đời — theo TỪNG TUỔI — để người đọc HIỂU cái nền mình được trao (bàn tay được chia), KHÔNG phải để sợ một số phận đóng đinh.**

## Sách là gì

- **铁板神数** — hệ số "chắc như tấm sắt" (铁板 = không lay chuyển). Là hệ phán **chi tiết, cụ thể nhất** trong nhà Thiệu Khang Tiết.
- **~12.000 điều văn (条文)** đánh số, **mỗi điều gắn một TUỔI**; tổ chức theo **tập (集)**. Nội dung: số anh em, song thân còn/mất, vợ chồng con cái, thọ yểu, biến cố từng năm tuổi.
- **Cách dùng**: bát tự + **考刻 (khảo khắc)** — neo chính xác KHẮC giờ sinh bằng **sự kiện đời thật** (số anh em, năm cha/mẹ mất…) — ra một dãy SỐ → tra điều văn đánh số. Càng neo đúng khắc, càng trúng.

## Vị trí trong 4 hệ Tổ sư (độ phân giải)

| Hệ | Đọc gì | Độ phân giải |
|---|---|---|
| Hoàng Cực | mùa của thời | vĩ mô — vạn năm |
| Mai Hoa | một khoảnh khắc | tức thời |
| Tử Vi *(Trần Đoàn)* | cấu trúc tâm-thiên-thân | một đời, theo cung |
| **Thiết Bản** | **chi tiết TỪNG TUỔI** | **vi mô nhất, cụ thể nhất** |

## Đọc ĐÚNG ĐẠO (quan trọng nhất — paradigm)

Thiết Bản là hệ **"bói" nhất** → **căng nhất** với đạo đọc-đồng-dạng (Iron Rule #4/#6/#8). Quy tắc bắt buộc:

1. **Đọc cái ĐÃ ĐỊNH (THỂ) — bàn tay được chia**: gia cảnh, thân, hoàn cảnh khởi, các mốc đã rồi. **KHÔNG phán cái DỤNG** (mình SỐNG ra sao) — vì **mệnh là dịch**, người là cái BIẾN (founder ngộ 16/6, [[founder_menh_la_dich]]).
2. **Dùng để HIỂU mình + hoà giải quá khứ**, KHÔNG để sợ tương lai.
3. Điều văn về tương lai/thọ yểu → trình bày như **cấu trúc/điều kiện**, luôn kèm: *"đây là cái NỀN, không phải bản án; người là cái biến."* **Không hù doạ.**
4. Kế thừa Mai Hoa: **không nghi không bói · một việc bói một lần** (Iron Rule #4).
5. **Attribution rõ**: Thiết Bản **tương truyền** Thiệu Khang Tiết (gán truyền thống; văn bản thực có lẽ biên soạn Minh/Thanh mượn danh). KHÔNG nhận nhầm công tổ.

## Output contract (feature cho user)

- ✅ Tra điều văn theo số / khoảng / chữ / tập.
- ⏳ **Tính số từ ngày sinh** (cần OCR 起数 + phép 考刻) — bước biến Thiết Bản từ "tra cứu" thành "công cụ trọn".
- Mỗi lần hiện điều văn → **kèm 1 dòng đúng-đạo** (cái nền, không phải bản án).

## Trạng thái & roadmap (tự chạy theo thứ tự này)

- **STORE (quan trọng)**: canonical = **DB `data/yi_wiki/wiki.sqlite3` bảng `tabular_verses`** (corpus `thiet-ban-than-so`, **10.907 điều, 8.217 có vi ~75%**). File `data/tabular_verses_v1_*.json` là **bản OCR cũ STALE (5.7k vi)** — KHÔNG ingest đè DB. Dịch mới → ghi thẳng vào DB (UPDATE ... WHERE vi IS NULL), rồi sync.
- **ĐÃ CÓ**: `engine/thiet_ban` + `api/thiet_ban` (verse/range/search/volume/stats) + web (HoangCucPanel ô "🔢 Tra điều văn" + khung đúng-đạo). OCR bảng điều văn tr.106–587 (qwen-VL).
- **KEYSTONE 起数 — ĐÃ HIỂU PHÉP** (16/6): phương pháp nằm ở Càn Tập (restored p0006–0013), tài liệu hoá ở **`docs/design/THIET-BAN-KHOI-SO.md`**; nền số = Hà Đồ-Lạc Thư (Chương 9) → `engine/thiet_ban/khoi_so.py` (phần kiểm-được). Bonus: front matter sách có Tử Vi an-sao + tứ hóa, **kiểm chéo khớp Đồ Năm**. CHƯA ship engine tính-số vì: 八卦加则 OCR mờ/khẩu quyết + 考刻 cần cha-mẹ-bát-tự & sự kiện + **thiếu cặp kiểm** (không bịa số đóng đinh). Chờ: OCR sạch Lệ + 1-2 cặp kiểm.
- **GAP khác**: ~2.690 điều DB chưa có vi (gồm cả mảnh OCR vỡ).
- **LIVE**: DB → VPS qua `scripts/sync-atoms-to-vps.sh` (đẩy cả wiki.sqlite3; chỉ chạy khi gom đủ thay đổi, tránh đè state vì 1 nhúm điều).
- **PATH** (làm không cần hỏi): ① thêm khung GOAL+đúng-đạo vào web Thiết Bản → ② dịch nốt ~1.690 điều → ③ OCR 起数+考刻 → ④ engine tính-số-từ-ngày-sinh → ⑤ trang/sách Thiết Bản hoàn chỉnh.

---

*Nguyên tắc vận hành: bám GOAL này, chạy trọn từng bước của PATH, chỉ hỏi khi thật sự bị chặn (thiếu quyết định không suy được từ GOAL).*
