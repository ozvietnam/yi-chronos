# THIẾT BẢN — Phép 起数 (tính số điều văn): CƠ MẬT đã thấu

> Keystone của Thiết Bản. Đọc THẲNG ảnh scan bản gốc 《邵康节说易·铁板神数》(Trung Châu Cổ Tịch),
> Càn Tập `..._origin.pdf` tr.9-21 + **kiểm chéo 10 nguồn TQ** (163, sohu 朴易天下, 知乎, baidu).
> Lập 16/6, **đọc lại + thấu cơ mật 18-19/6**.
>
> **Kết luận một câu:** 铁板 **KHÔNG phải hàm ngày-sinh → số**. Số điều văn là số **CÁ NHÂN**,
> chỉ chốt được sau **考刻 (đối chiếu lục thân đã biết)** — đó CHÍNH là cái làm nó "chuẩn",
> và cũng là lý do **không thể tự-động-hoá thuần từ ngày sinh**.

---

## 0. Bản gốc CHỈNH TỀ — đính chính lỗi pipeline

Founder soi bản gốc 18/6: **in rất đẹp, không mờ**. Cái "mờ/đảo" ghi trước là do **pipeline MinerU làm rối bảng** (vỡ ô lưới 干支 dày), KHÔNG phải sách. Đã đọc lại bằng mắt; mọi luật dưới đây là bản ĐÚNG.

## 1. Toàn cảnh phép — 6 BƯỚC (kiểm chéo 朴易天下 / 163 / baidu)

```
① 八字排盘        Lập tứ trụ
② 八卦取数        Can-chi → SỐ (太玄数 + 先天八卦数)         ← TẤT ĐỊNH (lớp A)
③ 皇极起数        Ráp 千百十个 → 先天命数 (元会运世)          ← TẤT ĐỊNH (lớp A)
④ 考刻定分        DÒ 调整数 bằng lục thân đã biết            ← CALIBRATE (lớp B = GIA ĐẠO)
⑤ 加减秘数        基数 ± 秘数 → số điều văn theo loại việc    ← GIẤU (lớp C)
⑥ 查阅条文        Tra bảng 纳卦 8 集 → điều văn               ← bảng CÓ trong sách, chưa số hoá
```

**3 LỚP — đây là cơ mật cốt lõi:**

| Lớp | Là gì | Trạng thái |
|---|---|---|
| **A — Số học tất định** | 太玄数, 先天八卦数, 序数, 安身命, base 时×30+日 | ✅ Đã code + KIỂM (engine `khoi_so.py`) |
| **B — 考刻 (dò, không tính)** | 调整数 "đối ra" bằng lục thân (cha mẹ, anh em) | ✅ Khung đã code = **gia đạo** (cần bát tự bố mẹ) |
| **C — Giấu** | 秘数 từng loại + cách index bảng 纳卦 | ⛔ Mọi nguồn GIẤU + thiếu cặp kiểm → KHÔNG bịa |

## 2. LỚP A — số học tất định (đã code + kiểm)

**① 太玄数** (sách gọi "河洛配数例"; 3 nguồn TQ gọi 太玄数) — origin p9:
| 干 / 支 | Số | | 干 / 支 | Số |
|---|---|---|---|---|
| Giáp Kỷ · Tý Ngọ | 9 | | Đinh Nhâm · Mão Dậu | 6 |
| Ất Canh · Sửu Mùi | 8 | | Mậu Quý · Thìn Tuất | 5 |
| Bính Tân · Dần Thân | 7 | | Tỵ Hợi | 4 |

**② 先天八卦数** (Phục Hy, sohu xác nhận): Càn1 Đoài2 Ly3 Chấn4 Tốn5 Khảm6 Cấn7 Khôn8.
*(Khác 地支配卦 Hậu Thiên ở §3 — hai hệ số dùng ở hai bước.)*

**③ Công thức nền 先天命数** (北派 = 时+日; 南派 = 日+时干支):
> 基数 = (**时支序数 × 30** + 日干序数 + 调整数) ÷ 5
- ×30 KHỚP khẩu quyết sách **"爻从三十起"** (八卦加则).
- **KIỂM:** ca 163.com 戊(Mậu)日 午(Ngọ)时, 调整数=5 → (7×30 + 5 + 5)/5 = **44** ✓ (engine `co_so_bac_phai` ra đúng 44).
- 元堂动爻 = base mod 6 (1..6).

**④ 安身命** (origin p10, thuật toán sạch = Tử Vi): từ Dần khởi Giêng → cung tháng; từ đó khởi Tý, nghịch→Mệnh, thuận→Thân.

## 3. Các Lệ phối quái (origin p9-10, đọc đúng bản gốc)

- **天干配卦**: 壬甲乾, 乙坤, 庚艮, 辛巽, 己震, 戊离, 丙坎, 丁兑 *(庚 bản gốc lưỡng vị 坤/艮; 癸 chưa nêu — chờ bảng 纳卦 phân định)*.
- **地支配卦** (Hậu Thiên/Lạc Thư): 1坎 2坤 3震 4巽 5中 6乾 **7艮 8兑** 9离. *(Bản gốc IN 七艮八兑 — "sửa 7兑8艮" cũ của mình là SAI. ⚠ Lưu ý: 河洛理数 CHUẨN dùng 7兑8艮; sách 铁板 này dùng 7艮8兑 — khác hệ, giữ đúng bản.)*
- **日主配卦**: 亥子坎, 寅震, 巳午离, 丑坤, 卯酉乾, 辰兑, 未艮, 戌巽.
- **地支取数 Hà Đồ**: 亥子1·6 寅卯3·8 巳午2·7 申酉4·9 辰戌丑未5·10.
- **五虎遁**: Giáp/Kỷ→Bính, Ất/Canh→Mậu, Bính/Tân→Canh, Đinh/Nhâm→Nhâm, Mậu/Quý→Giáp. · **60 纳音** đọc trọn.

## 4. LỚP B — 考刻 = CƠ MẬT làm nên độ chuẩn

Sách (origin p8): *"từ bát tự **bản thân + cha mẹ**, mỗi giờ suy **tám khắc**, mỗi khắc suy **mười lăm phân**, suy đến đúng giờ thì toàn số đều hợp."*

→ 考刻 = **DÒ 调整数** trong không gian **8 khắc × 15 phân** sao cho điều văn **lục thân KHỚP sự thật đã biết** (số anh em, cha/mẹ còn-mất + con giáp, số con, biến cố...). 163.com chốt: *"调整数 không tính ra được, mà **'đối' ra"*.

**Hệ quả lớn:** không có lục thân (nhất là **bát tự cha mẹ**) thì **không chốt được số**. Đây CHÍNH LÀ lý do founder cần đưa **bát tự bố mẹ vào trang Gia Đạo** — gia đạo = đầu vào 考刻. Engine: `kao_khac_khung()` (`khoi_so.py`) liệt kê đúng cần đối chiếu gì, KHÔNG bịa 条文.

南派 / 北派: Nam trọng 日+时干支; Bắc trọng 月柱+时辰. (Chọn phái khi có cặp kiểm.)

## 5. LỚP C — phần GIẤU (KHÔNG ship số)

- **秘数** (基数 ± 秘数 → số điều văn theo loại việc: huynh đệ, phụ mẫu, thê, tử...): **mọi nguồn TQ cố tình KHÔNG công bố** (知乎 tác giả: "条文 và 秘数 tôi vẫn không chép lên").
- **Bảng 纳卦 8 集** (查阅条文): **sách Anh CÓ CHỨA** — origin page_idx 16+ (坤集... mỗi 集 nhiều khối 纳乾坤屯卦/纳艮卦/纳师卦..., mỗi khối là dãy **signature 干支 4-5 chữ + hành**). In rõ, nhưng cực dày (~hàng nghìn dòng × 8 集); MinerU làm vỡ.
- **THIẾU cặp kiểm**: không có "bát tự X → số điều Y" đã biết để validate (không như 304-313 của Hoàng Cực).

⛔ **Không làm:** ship "bát tự → số điều" khi thiếu 秘数 + cặp kiểm = **bói giả-chính-xác**, phản đạo (Iron Rule #4/#6). Nhất là đời người.

## 6. Liên hệ HOÀNG CỰC (phát hiện kèm)

Bước ③ là **皇极起数 (元会运世)** — chính hệ Hoàng Cực ta ĐÃ có engine (`engine/hoang_cuc`). Tức Thiết Bản mượn khung Nguyên-Hội-Vận-Thế của tổ sư để định "先天命数". Đây là cầu nối 2 hệ trong cùng nhà Thiệu Khang Tiết.

## 7. Đường tới (PATH ③-④ keystone)

1. **Số hoá 8 集 bảng 纳卦** từ origin page_idx 16+ (vision OCR cẩn thận từng 集, KHÔNG dùng MinerU). Lưu thành tra cứu.
2. **Tìm ≥1 cặp kiểm** (một lá số 铁板 đã có sẵn dãy số điều văn — sách案例 / thầy / cộng đồng) → validate base + 秘数.
3. Có cặp kiểm → giải ngược **秘数** → bật engine `base ± 秘数 → tra 纳卦`.
4. Nối **考刻** vào trang Gia Đạo (lục thân bố mẹ) → chốt 调整数.

## Nguồn

- Bản gốc: `data/yi_publishing_mineru/shao-yong-.../auto/..._origin.pdf` tr.9-21.
- [163.com 铁板神数皇极起数法](https://www.163.com/dy/article/KE5DP1V30521C9T8.html) — 6 bước + ca 戊日午时→44 + 调整数 "đối ra".
- [sohu 朴易天下 详细计算方法](https://www.sohu.com/a/965131029_479097) — 太玄数 + 先天八卦数 + 元会运世.
- [知乎 铁版神数的N种算法](https://zhuanlan.zhihu.com/p/137658598) — N biến thể, tác giả giấu 秘数.
- [baidu 铁版神数](https://baike.baidu.com/item/铁版神数/3901251) — 南/北派 考时定刻.

---

*Trung thực tối đa: phép đã THẤU (6 bước + 3 lớp), lớp A đã code + kiểm (ca 44), lớp B (考刻) thành khung gia đạo; lớp C (秘数 + bảng) chờ số hoá + cặp kiểm. Cơ mật lớn nhất: số là CÁ NHÂN (考刻), không bịa từ ngày sinh.*
