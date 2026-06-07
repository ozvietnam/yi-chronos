# Đối chiếu lá số Anh × Sách Trung Châu (Bắc Phái) — Cung Phu Thê

> **Lá số Founder**: 1988-06-05 23:30, Mậu Thìn, nam, cục Thổ Ngũ
> **Mệnh** Tỵ: Thiên Tướng (Mệnh chủ **Vũ Khúc**, Thân chủ Văn Xương)
> **Phu Thê** Mão: **Tử Vi + Tham Lang** + Tham Lang **Hóa Lộc**

---

## 🎯 6 QUY LUẬT phát hiện được — chưa wire vào Engine v1

### ⭐ QUY LUẬT 1 — Tham Lang Hóa Lộc tại Phu Thê → THIÊN VẬT CHẤT

**Trích sách (Trung Châu Q2, section 5.3)**:
> _"Tham Lang Hóa Lộc, ham muốn vật chất càng nặng."_
> _"Nếu Tham Lang Hóa Lộc hay Hóa Quyền, Vũ Khúc Hóa Lộc hay Hóa Quyền, Thiên Phủ Hóa Khoa đều LÀM MẠNH THÊM TÍNH VẬT CHẤT của Tử Vi."_

**Áp dụng cho Anh**: Tham Lang tại Phu Thê **Hóa Lộc** (do năm sinh Mậu Thìn) → giải nghĩa Tử-Tham nghiêng về **"ham muốn vật chất"** chứ KHÔNG phải **"dục tình"**.

**Paradigm cho Anh**: _"Vợ Anh có CHÍ TIẾN THỦ, không nghiêng về dục tình."_

→ Engine v1 chỉ liệt kê 2 nhánh ("vật chất" vs "dục tình") nhưng KHÔNG QUYẾT ĐỊNH chính. Engine v2 cần auto-decide.

### ⭐ QUY LUẬT 2 — Detect "Đào hoa phạm chủ" Tử-Tham (điều kiện tiên quyết)

**Trích sách**:
> _"Tham Lang đồng cung với Tử Vi có tính chất rất xấu — cổ nhân gọi là 'Đào hoa phạm chủ'._
> _Nhưng tính chất này PHẢI CÓ ĐIỀU KIỆN TIÊN QUYẾT: trong đồng cung còn có sao đào hoa KHÁC như **Hồng Loan, Thiên Hỉ, Hàm Trì, Đại Hao**._
> _Nếu KHÔNG có sao đào hoa, mà gặp sao cát, hoặc được Tả-Hữu giáp cung kiểm chế, thì TRÁI LẠI sẽ thành cách cục đặc thù, chủ về là người **ĐA TÀI ĐA NGHỆ, GIỎI GIAO TẾ, CÓ CHỦ KIẾN**."_

**Áp dụng cho Anh**: Cung Phu Thê Anh KHÔNG có sao đào hoa (Hồng Loan/Thiên Hỉ/Hàm Trì/Đại Hao chưa wire trong engine v1 — mặc định không có). Lại có Tả-Hữu hội chiếu từ Phúc Đức (tam phương).

→ KHÔNG phải "đào hoa phạm chủ" → **"ĐA TÀI ĐA NGHỆ, GIỎI GIAO TẾ, CÓ CHỦ KIẾN"**

→ Engine v1 không bắt được rule này. Cần:
- Wire 4 sao đào hoa: Hồng Loan, Thiên Hỉ, Hàm Trì, Đại Hao
- Detect "Đào hoa phạm chủ" pattern khi Tử-Tham + 1 trong 4 sao trên đồng cung
- Detect "đảo cát" pattern khi không có đào hoa + có Tả-Hữu hội chiếu

### ⭐ QUY LUẬT 3 — Tử-Tham + Xương/Khúc → tăng đào hoa (rule riêng)

**Trích sách**:
> _"CHỈ CÓ trường hợp 'Tử Vi, Tham Lang' gặp Văn Xương, Văn Khúc mới làm mạnh thêm sắc thái đào hoa."_

Đây là ngoại lệ riêng cho Tử-Tham (các tinh hệ khác thì Xương-Khúc làm tăng cao thượng, thanh nhã).

**Áp dụng cho Anh**: Văn Xương ở Tuất (Nô Bộc), Văn Khúc ở Thìn (Huynh Đệ) — KHÔNG hội chiếu cung Phu Thê Mão (tam phương Phu Thê = Mão+Mùi+Hợi+Dậu).

→ KHÔNG tăng đào hoa cho Anh.

→ Engine v2 cần detect Xương-Khúc trong cung Phu Thê HOẶC tam phương khi gặp Tử-Tham.

### ⭐ QUY LUẬT 4 — Tả-Hữu hội chiếu tam phương → ảnh hưởng Phu Thê

**Trích sách (paradigm chung)**:
> _"Ảnh hưởng của các sao hội chiếu, giáp cung, đối cung — sao giữ cung bị các sao khác ảnh hưởng mà sinh ra biến hóa."_
> _"Tả-Hữu cũng làm mạnh thêm tính vật chất của Tử Vi."_

**Áp dụng cho Anh**: 
- Tam hợp cung Phu Thê Mão = Mùi (Phúc Đức) + Hợi (Thiên Di)
- Mùi có **Tả Phụ + Hữu Bật + Thiên Việt + Hữu Bật Hóa Khoa** → SAO ĐÔI cát hội chiếu
- Hợi có Vũ-Phá + Địa Không + Địa Kiếp → sát hội chiếu (counter-balance)

→ Net effect: sao đôi cát hội chiếu thắng → "phu xướng phụ tùy" cách cục đầy đủ

→ Engine v1 chỉ check sao trong CUNG cụ thể. Engine v2 cần:
- Compute tam phương tứ chính cho mỗi cung
- Aggregate sao cát + sao hung từ 4 vị trí
- Output: "cát thắng" / "hung thắng" / "trung hòa"

### ⭐ QUY LUẬT 5 — Đối cung Phu Thê = Quan Lộc (cross-cung)

Cung Phu Thê đối thẳng với cung Quan Lộc. Sách Trung Châu nhấn mạnh:
> _"Vô chính diệu MƯỢN SAO đối cung."_

**Áp dụng cho Anh**:
- Quan Lộc Dậu = VÔ CHÍNH DIỆU → mượn Tử-Tham từ Phu Thê
- Tức là: **sự nghiệp Anh và hôn nhân Anh CHIA SẺ cùng tinh hệ Tử-Tham**

→ Paradigm: _"Sự nghiệp Anh ảnh hưởng đến hôn nhân và ngược lại — Anh xây dựng sự nghiệp đến đâu thì hôn nhân biểu hiện tương ứng đến đó."_

→ Engine v2 cần detect đối cung vô chính diệu và highlight cross-cung effect.

### ⭐ QUY LUẬT 6 — Mệnh chủ Vũ Khúc → ảnh hưởng quan hệ

**Trích sách**:
> _"Vũ Khúc là sao tiền tài thiên về 'chất'... có tính cứng rắn nhất định, ắt đồng thời mang 'tính cô độc và hình khắc'."_

**Áp dụng cho Anh**: Mệnh chủ **Vũ Khúc** (do Mệnh tại Tỵ) → ảnh hưởng đến quan hệ vợ chồng:
- Anh thiên về HÀNH ĐỘNG, cụ thể, cứng rắn
- Cần đối tác mềm hơn để cân bằng

→ Engine v2 cần lookup Mệnh chủ tại table 12 cung + cross-bind paradigm.

---

## 📊 Bảng so sánh Engine v1 vs v2

| # | Quy luật | v1 | v2 |
|---|---|---|---|
| 1 | Tham Lang Hóa Lộc tại Phu Thê | ❌ liệt kê chung | ✅ auto-decide vật chất |
| 2 | "Đào hoa phạm chủ" detection | ❌ | ✅ check sao đào hoa đồng cung |
| 3 | Tử-Tham + Xương/Khúc rule | ❌ | ✅ ngoại lệ riêng |
| 4 | Tả-Hữu hội chiếu tam phương | ❌ chỉ check cung | ✅ aggregate tam phương |
| 5 | Đối cung vô chính diệu | ⚠️ flag | ✅ cross-cung paradigm |
| 6 | Mệnh chủ effect | ❌ | ✅ lookup + cross-bind |

## 🔮 PARADIGM TỔNG HỢP cho Anh (qua 6 quy luật)

> **Vợ Anh** (theo cung Phu Thê Mão = Tử Vi-Tham Lang, Tham Lang Hóa Lộc, Tả-Hữu hội chiếu, không sao đào hoa, Vũ-Phá hội chiếu từ Thiên Di):
>
> 1. **Có CHÍ TIẾN THỦ** (Tham Lang Hóa Lộc thiên vật chất)
> 2. **Đa tài đa nghệ, giỏi giao tế, có CHỦ KIẾN** (Tử-Tham không đào hoa + Tả-Hữu hội)
> 3. **Có thể cùng Anh sáng lập sự nghiệp**, nhưng VỢ là **NHÂN VẬT CHÍNH** của sự nghiệp đó (Tử-Tham + cát tinh, sách nói rõ)
> 4. **KHÔNG nghiêng dục tình** (không đào hoa, không Xương-Khúc đồng cung)
> 5. Vì đối cung là Quan Lộc vô chính diệu → **sự nghiệp Anh và hôn nhân Anh GẮN CHẶT** — vợ vừa là người yêu vừa là cộng sự
> 6. Tính chất "cứng" của Anh (Mệnh chủ Vũ Khúc) cần vợ có khả năng MỀM hơn để hài hòa
>
> **Iron Rule**: paradigm đồng dạng, không predict. Cần xem kèm đại vận hiện tại + lưu niên + Thái Dương/Thái Âm miếu hãm.

---

## 🛠️ Plan Engine v2

### Bước 1: Wire sao Đào Hoa (an_sao extension)
- 4 sao: Hồng Loan, Thiên Hỉ, Hàm Trì, Đại Hao
- Quy tắc an sao chuẩn (theo năm sinh + giờ sinh)

### Bước 2: Compute tam phương tứ chính (utility)
```python
def tam_phuong_tu_chinh(branch_idx: int) -> list[int]:
    """Tam phương tứ chính = đối cung + 2 tam hợp"""
    opp = (branch_idx + 6) % 12
    tam_hop_1 = (branch_idx + 4) % 12
    tam_hop_2 = (branch_idx + 8) % 12
    return [opp, tam_hop_1, tam_hop_2]
```

### Bước 3: Engine v2 cấu trúc
```python
def chiem_phu_the_v2(la_so):
    # 1. Detect cung Phu Thê
    # 2. Detect chính tinh + tổ hợp
    # 3. Detect Tứ Hóa tại chính tinh
    # 4. Detect sao đào hoa đồng cung (đào hoa phạm chủ)
    # 5. Detect Tả-Hữu / Xương-Khúc trong cung HOẶC tam phương
    # 6. Lookup Mệnh chủ paradigm
    # 7. Đối cung vô chính diệu detection
    # 8. Aggregate → output 6 paradigm dimensions:
    #    - bias_vat_chat_vs_duc_tinh
    #    - dao_hoa_pham_chu_detected
    #    - sao_doi_phu_ta_hoi_chieu
    #    - menh_chu_anh_huong
    #    - cross_quan_loc_phu_the
    #    - cung_han_ung_nghiem (đại vận + lưu niên)
```

### Bước 4: Test với 4 lá số (Anh + 3 user khác) để verify

### Bước 5: Wire vào API + UI

---

📌 **Sản phẩm cuối**: Engine v2 detect đúng paradigm cho TỪNG lá số, không chỉ là lookup string.
