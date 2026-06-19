# THIẾT BẢN THẦN SỐ — GOAL & La-bàn (v2, theo sách 图解)

> La-bàn cho mọi việc Thiết Bản. Có GOAL này thì **tự chạy, validated từng bước, ít hỏi**.
> v1 lập 2026-06-16; **v2 viết lại 2026-06-19** sau khi founder add sách thẩm quyền 《图解铁版神数》.

---

## GOAL — một câu

**Dựng engine Thiết Bản: bát tự → (nhiều phép 取数) → số → tra điều văn (kho sạch) → đọc cái
ĐÃ ĐỊNH của một đời (mạnh nhất: LỤC THÂN), để HIỂU cái nền — KHÔNG bói, KHÔNG hù.**
Độ chính xác đỉnh cao đến từ **考刻 (neo khắc/phân bằng lục thân đã biết)** — đặt ở trang Gia Đạo.

## Nguồn THẨM QUYỀN (xếp hạng)

1. **《图解易经象数学·铁版神数》** (陕西师大, `thư viện sách/thieukhangtiet/757915970-...pdf`, 347tr) —
   bản hiện đại tổng hợp各派, CÓ 图表 + **举例 (cặp kiểm)** + 密码本 + **13000 条文 sạch**. ⭐ Chuẩn để validate.
2. Bản gốc 《邵康节说易（乙）》(origin.pdf) — bản khắc CŨ, có **lỗi in** (天干配卦 lệch 纳甲, 7艮8兑) → chỉ dùng đối chiếu, KHÔNG làm chuẩn tính.
3. Repo open-source `xaminxan/tiebanshenshu` — cặp kiểm máy (đã khớp 108/108 流年). Không LICENSE → chỉ học số.
4. DB `wiki.sqlite3` bảng `tabular_verses` (corpus thiet-ban-than-so) — kho điều văn của ta (lấp lỗ từ nguồn #1).

## Cấu trúc sách 图解 (bản đồ)

- **上篇**: 18 取数法 (tr.67-109).
- **中篇**: 乾集 19 歌诀 (tr.112-128) + 坤集 密码集 21 mục (tr.130-141: 各宫流度/斗宫密数/纳卦表甲乙丙/师徒爻/升仙年月爻).
- **下篇**: 13000 条文 (子1001→亥13000, tr.144-553).

## 18 取数法 — mỗi phép sinh điều văn theo một góc (trạng thái validate)

| # | Phép | Cho ra | Trạng thái |
|---|---|---|---|
| 五音/十二辟卦 (repo) | 本命 + 流年 | 本命条文 + 流年 từng tuổi | ✅ engine `lap_so.py`, 流年 khớp 108/108 |
| 12. 卦中取数法 (太玄) | 4 điều (年月+日时+互卦) | birth-only | ✅ `quai_trung_so_tu_tru`, khớp 4/4 cặp kiểm sách |
| 13. 八卦滚法 | 48 điều (toàn diện) | birth-only | ◑ geometry + 配数表 xong; base 后天 odd/even + full roll CHƯA validate |
| 4. 考时定刻 + 17/18 考刻论lục thân | neo khắc/phân | cần lục thân | ⏳ tr.69/118/121 (cặp kiểm) — CHƯA đọc kỹ |
| 7. 元堂取数 | 先天/后天卦 | birth | ✅ có sẵn `engine/ha_lac` (河洛真数) |
| 14/15/16. 元会运世/大运/流年 | vĩ mô + năm | | ◑ 元会运世 ↔ engine Hoàng Cực; 流年 đã wire |
| 8-11. 八卦加则/前后卦/六爻和数 | điều bổ sung | | ⏳ chưa làm |

→ **"N种算法"**: Thiết Bản đầy đủ = NHIỀU phép, mỗi phép góp điều văn (lục thân, tính cách, tài, lưu niên, thọ). Một quẻ đọc tổng hợp nhiều phép.

## 考刻 = đỉnh cao (đặt ở GIA ĐẠO)

Sách 乾集: *"从本人**父母本身八字**... 每一时推八刻, 每刻推十五分, 推到准时, 全数悉合."* →
考刻 = dùng **lục thân đã biết** (số anh em, cha/mẹ tuổi gì còn-mất...) + **bát tự cha mẹ** để neo đúng
KHẮC/PHÂN sinh (8 khắc × 15 phân). Đây là máy **trắc nghiệm giờ sinh** + làm bản luận "chuẩn đóng đinh".
→ Đặt ở trang Gia Đạo (`docs/design/GIA-DAO.md`). 考刻论父母兄弟 (tr.118) + 考分论夫妻子女 (tr.121) có ví dụ.

## Paradigm (Iron Rule #4/#6/#8 — căng nhất vì là hệ "bói" nhất)

- Đọc cái **ĐÃ ĐỊNH (THỂ)** — lục thân, gia cảnh, thân, cái nền — KHÔNG phán cái **DỤNG** (mình sống ra sao). Mệnh là động từ.
- CHỈ theo **giờ SINH** (founder chốt: bỏ "giờ hỏi", quá mơ hồ).
- Để **HIỂU + hoà giải**, KHÔNG để sợ. Không hù thọ yểu. Attribution rõ (tương truyền Thiệu Khang Tiết).

## KỶ LUẬT VALIDATE (bắt buộc — "vào việc cẩn thận")

**Mỗi phép TRƯỚC khi ship: phải khớp ví dụ mẫu của sách (cặp kiểm) + ra verse thật trong DB.**
Thiếu cặp kiểm / thiếu 密码 → KHÔNG bịa số. Ghi rõ chỗ partial. (Đã giữ kỷ luật này xuyên suốt.)

## Trạng thái hiện tại (2026-06-19)

- ✅ Engine `lap_so.py` (五音/辟卦): 本命 + 流年 từng tuổi, validate 108/108. UI live local (tab Hoàng Cực → 🎴 Lập số).
- ✅ `bat_quai_lan.py`: geometry 互/变/倒, 八卦基本配数表 (`so_tu_co_ban`), 卦中取数法 (`quai_trung_so_tu_tru`, khớp 4/4).
- ✅ 天干配卦 sửa về 纳甲 chuẩn (xác nhận bởi sách 图解). 元堂/大限 có ở `engine/ha_lac`.
- ◑ 八卦滚 full · 考刻 lục thân · 条文 lấp lỗ từ sách 图解 — chưa xong.

## PATH (làm theo thứ tự, validated)

1. **Hoàn tất 八卦滚**: sửa base → 后天 odd/even; validate full roll vs ví dụ 图解 (女2006 丙戌庚寅丁亥辛亥 → 地天泰 → 雷泽归妹 → 8 quẻ → 48 điều). Đọc tr.97-98.
2. **考刻论父母兄弟 + 考分论夫妻子女** (tr.118-121): đọc + dựng phép lục thân (cặp kiểm) → nối Gia Đạo (bát tự cha mẹ).
3. **坤集 密码集** (tr.130-141): số hoá các 流度/密数/纳卦表 (数序 cho các phép cần).
4. **条文 sạch**: lấp lỗ hổng DB (vd 9356) + sửa OCR từ 下篇 sách 图解 (13000 bản in đẹp).
5. **Web**: gộp đa-phép vào panel (本命 + lục thân + lưu niên + 八卦滚), nối 考刻 ở Gia Đạo.

---

*Nguyên tắc: bám GOAL, chạy trọn PATH, mỗi bước VALIDATE bằng cặp kiểm sách + DB, KHÔNG bịa. Chỉ hỏi khi thật sự bị chặn.*
