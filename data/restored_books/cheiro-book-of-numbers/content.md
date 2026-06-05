# Sách Về Những Con Số — Cheiro

> _Cheiro's Book of Numbers_ (1926) · Cheiro (Count Louis Hamon, 1866-1936)
> Bản phục dựng EN→VI — phần cốt lõi hệ **Chaldean**. Public domain.
> Nguồn gốc: https://archive.org/details/cheirosbookofnumbers
>
> ⚠️ **Phục dựng Phase 1** (Iron Rule #2): phần này restore nội dung CỐT LÕI (bảng chữ cái
> Chaldean + số đơn 1-9 + số kép 10-32). Bản PDF nguyên tác đính kèm sau. Sắc thái đầy đủ
> các số kép 33-52: tra bản gốc.
>
> 🪷 **Paradigm YI-Chronos**: Cheiro dùng tone "may mắn / cảnh báo". Em phục dựng trung thực
> nguyên văn, NHƯNG khi luận giải cho người dùng → đọc theo paradigm **đồng dạng** (Iron Rule
> #4/#6): mỗi số là **sắc thái cấu trúc cần quan-sát**, KHÔNG phải lời tiên tri định mệnh.

---

## I. Hệ Chaldean — nền tảng

Cheiro phân biệt hai lớp số:
- **Số đơn 1-9** — thuộc mặt **VẬT CHẤT** của sự vật; ứng với hành tinh.
- **Số kép từ 10 trở lên** — thuộc mặt **HUYỀN / TINH THẦN** của đời sống và sự kiện.

Khác hệ Pythagoras (gán tuần tự A=1…), Chaldean gán chữ cái theo **rung động âm thanh**, và
**số 9 linh thiêng — không gán cho chữ cái nào**. Khi tính tên, Chaldean **giữ số kép** (vd 23)
rồi mới xét tổng rút gọn — số kép mang lớp nghĩa riêng.

### Bảng chữ cái Chaldean
(chi tiết: `data/than_so/master/letter_maps.json` → `chaldean`)

| Số | Chữ cái |
|---|---|
| 1 | A I J Q Y |
| 2 | B K R |
| 3 | C G L S |
| 4 | D M T |
| 5 | E H N X |
| 6 | U V W |
| 7 | O Z |
| 8 | F P |
| 9 | _(không gán — linh thiêng)_ |

---

## II. Số đơn 1-9 & hành tinh

| Số | Hành tinh (Cheiro) |
|---|---|
| 1 | Mặt Trời |
| 2 | Mặt Trăng |
| 3 | Mộc tinh |
| 4 | Thiên Vương (nhóm Mặt Trời) |
| 5 | Thủy tinh |
| 6 | Kim tinh |
| 7 | Hải Vương (nhóm Mặt Trăng) |
| 8 | Thổ tinh |
| 9 | Hỏa tinh |

(Ý nghĩa tính cách từng số 1-9 đối chiếu với `number_meanings.json`.)

---

## III. Số kép 10-32 (cốt lõi)

> Phục dựng từ nguyên tác Cheiro. Dữ liệu máy: `data/than_so/master/chaldean_compound_numbers.json`.

- **10 — Bánh Xe Số Phận**: danh dự, niềm tin, tự tin; thăng-trầm; tên tuổi được biết đến; kế hoạch dễ thành.
- **11 — Bàn tay nắm chặt / sư tử bị bịt mõm**: cảnh báo hiểm họa ngầm, thử thách, phản trắc.
- **12 — Hy Sinh / Nạn Nhân**: khổ tâm, lo âu; dễ bị hy sinh cho mưu đồ người khác.
- **13 — Biến động** _(không phải 'xui')_: đổi kế hoạch/nơi chốn, xáo trộn, hiểm bất ngờ. Quyền lực để thay đổi nếu dùng đúng.
- **14 — Chuyển động & kết hợp**: vận động, phối hợp; hiểm từ thiên nhiên; may về tiền nhưng đừng phó mặc phán đoán cho người khác.
- **15 — Ma thuật / sức hút**: hùng biện, nghệ thuật, từ tính mạnh; huyền học — ích kỷ thì nguy.
- **16 — Tháp bị Sét đánh**: cảnh báo định mệnh lạ, tai nạn, kế hoạch sụp.
- **17 — Ngôi Sao của Pháp Sư**: số tâm linh cao, Bình an & Tình yêu; vượt lên thử thách; tên tuổi bất tử. May.
- **18 — Vật chất lấn tinh thần**: tranh chấp, mâu thuẫn, biến động; cảnh báo lừa dối. Giữ tinh thần trên vật chất.
- **19 — Hoàng Tử Thiên Đường**: thành công, hạnh phúc, được trọng vọng. Rất may.
- **20 — Thức Tỉnh / Phán Xét**: lời gọi hành động vì mục đích mới; thức tỉnh tinh thần.
- **21 — Vương Miện của Pháp Sư**: thăng tiến, vinh quang, chiến thắng sau gian nan. May.
- **22 — Người tốt bị lừa**: cảnh báo ảo tưởng & lầm lạc; sống trong "thiên đường của kẻ khờ".
- **23 — Vương Tinh của Sư Tử**: thành công, được cấp trên giúp, người quyền cao che chở. Rất may.
- **24 — May mắn / quý nhân**: được người có địa vị trợ giúp; lợi từ tình yêu.
- **25 — Sức mạnh qua trải nghiệm**: thành công qua thử thách thời đầu; thuận cho tương lai.
- **26 — Cảnh báo nặng**: thảm họa do hùn hạp/đầu cơ/lời khuyên sai. Cân nhắc kỹ đường đi.
- **27 — Vương Trượng**: quyền uy, sức mạnh; phần thưởng từ trí tuệ; nên tự thực thi ý tưởng. Tốt.
- **28 — Mâu thuẫn**: nhiều hứa hẹn nhưng dễ mất trắng nếu không lo xa; có thể phải làm lại nhiều lần.
- **29 — Bất trắc lòng người**: dễ bị phản bội/lừa; phiền muộn từ người khác giới.
- **30 — Suy tưởng**: ưu thế trí tuệ, thiên suy tư; tùy quyết định của trí — "được tất cả hoặc không gì".
- **31 — Cô lập**: như 30 nhưng khép kín, cô đơn, tách biệt đời.
- **32 — Sức mạnh huyền** (như 14/23): thuận nếu giữ phán đoán riêng; nghe theo cố chấp người khác thì đổ vỡ.

### Số kép 33-52
Cheiro: phần lớn **lặp lại** sắc thái theo tổng chữ số → tra số kép thấp tương ứng
(33≈24, 34≈25, 35≈26, 36≈27, 40≈31…). **37** đặc biệt tốt cho hợp tác/tình thân.
Sắc thái đầy đủ: xem bản PDF nguyên tác.

---

## IV. Còn lại (Stage 6 — chờ Anh)
- [ ] Đính kèm PDF nguyên tác (Stage 1 hoàn tất)
- [ ] Dịch trọn các chương ứng dụng (tên + ngày sinh, tương hợp, dự cảm)
- [ ] Biên soạn → PDF publish (Stage 6) + vào `data/published/` + LEDGER
