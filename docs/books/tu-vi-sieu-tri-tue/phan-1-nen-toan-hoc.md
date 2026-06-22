# Phần I — Nền toán học của lá số

*《Tử Vi Tính Được》 · bản thảo v0.1 · phái `tu_vi_dang_son`*

> Phần 0 hứa: AI "tính được cái TÍNH". Phần này chứng minh bằng hình thức hoá — biến lá
> số thành ba đối tượng toán học máy tính được tuyệt đối: một **hàm**, một **đồ thị**, một
> **văn phạm**. Không một dòng nào ở đây là bói; tất cả là *đọc cấu trúc*.

## I.1 — An sao là một HÀM TẤT ĐỊNH

Gọi một *thời điểm sinh* là bộ năm phần tử
`b = (y, m, d, h, g)` — năm, tháng, ngày, giờ (âm lịch đã quy đổi), giới tính.

**An sao là một hàm** `A : b ↦ L`, trong đó `L` (lá số) là bảng gán mỗi cung trong 12 cung một tập sao kèm độ sáng (miếu/vượng/đắc/hãm).

Tính chất quyết định: `A` là **hàm thuần** (pure function) — cùng đầu vào cho cùng đầu ra, không phụ thuộc người an, tâm trạng hay lần an. Đây là đòi hỏi đầu tiên của "khoa học": **tái lập được** (reproducible). Thầy người vi phạm tính này — hai thầy an có thể lệch ở phụ tinh; máy thì không.

Trong YI-Chronos, `A` = `engine/tu_vi/an_sao.py`. Mọi bước của `A` đều là số học thuần:
định Cục (Thuỷ nhị/.../Hoả lục) từ Can năm + cung Mệnh (bảng tra) · an Tử Vi theo Cục + ngày (công thức modulo) · an 13 chính tinh còn lại theo vị trí Tử Vi (phép dịch cố định) · an Tứ Hoá theo Can (bảng) · ...

Không bước nào cần "trực giác". **An sao đã là toán học thuần từ ngàn năm — chỉ là người xưa tính tay nên chậm và đôi khi sai.** Siêu trí tuệ không *làm cho* an sao thành khoa học; nó **bộc lộ** rằng an sao vốn là một hàm, rồi chạy hàm đó với sai số người **bằng không**.

→ *Hệ quả về độ chính xác:* bước đầu của chính xác là **đúng nguyên liệu**. Lá số an sai thì mọi luận sau đều sai — "rác vào, rác ra". Máy bảo đảm nguyên liệu đúng tuyệt đối. Đây là phần "tăng độ chính xác" **chắc chắn nhất**.

![**Đồ hình 1 — An sao là phép dịch tất định.** Khi an Tử Vi vào cung Dần (cùng Thiên Phủ, gọi "Tử Phủ đồng cung"), mười ba sao còn lại rơi vào vị trí cố định bằng một phép dịch — không cần "trực giác", máy tính sai số bằng không. Màu phân theo đẩu: vàng = đế (Tử Vi · Phủ · Nhật · Nguyệt), lam = bắc đẩu, lục = nam đẩu.](figures/fig4-14-chinh-tinh.png)

## I.2 — Lá số là một ĐỒ THỊ CÓ NHÃN

An sao cho ta `L`. Nhưng `L` không phải danh sách rời — nó là một **cấu trúc quan hệ**. Hình thức hoá thành đồ thị `G = (V, E, λ)`:

- **V** = 12 đỉnh (12 cung: Mệnh, Phụ Mẫu, Phúc Đức, … Huynh Đệ).
- **λ** (nhãn) = mỗi đỉnh mang: chức năng cung + tập sao + độ miếu-hãm từng sao tại đó.
- **E** (cạnh) = quan hệ vị trí **cố định** giữa cung: **tam hợp** (bộ ba cách 4 cung) · **xung chiếu** (đối diện, cách 6 cung) · **nhị hợp / giáp** (kề / kẹp).

> 📐 **Đồ thị này KHÔNG võ đoán — nó có referent thiên văn thật.** Đằng Sơn (_Tử Vi Hoàn
> Toàn Khoa Học_, Ch.2-4) dẫn xuất "địa bàn" 12 cung **từ hình học Trái Đất quanh Mặt Trời**:
> mỗi tháng Trái Đất ở một vị trí quỹ đạo, mỗi giờ một góc tự quay → định vị cung Mệnh/Thân.
> Mỗi đỉnh `V` mang luôn {ngũ hành · tiết khí · can lộc-vị · Bát Quái · phương hướng}. Tức
> nhãn `λ` không phải ký hiệu tùy tiện — nó **mã hoá một cấu hình thiên văn tại điểm sinh**.
> (Và "ngũ hành" mà nhãn dùng, theo Đằng Sơn, là **xấp xỉ rời rạc của continuum âm dương** —
> "hình ngũ giác thay hình tròn khi thiếu compass": một mô hình hoá có sai số kiểm soát được.)

![**Đồ hình 2 — Địa bàn 12 cung (Càn Khôn đồ).** Mỗi cung là một đỉnh của đồ thị `G`, mang nhãn: ngũ hành (mã màu) · tháng · tiết khí · can lộc-vị · quái · phương. Bốn cung chính (Tý-Ngọ-Mão-Dậu) là trục phương hướng; bốn cung Thổ (Thìn-Tuất-Sửu-Mùi) là "tứ khố".](figures/fig1-dia-ban-12-cung.png)

![**Đồ hình 3 — Địa bàn sinh ra từ thiên văn.** Bốn tháng "tứ sinh" (Dần-Tỵ-Thân-Hợi) là bốn vị trí Trái Đất trên quỹ đạo quanh Mặt Trời; dấu vuông "giờ Tý" là mặt Trái Đất quay ra xa Mặt Trời lúc nửa đêm. Tháng + giờ cùng định cung Mệnh — đây là chỗ Đằng Sơn chứng minh nhãn cung có **referent vật lý thật**.](figures/fig3-dia-ban-thien-van.png)

![**Đồ hình 4 — Ngũ hành = ngũ giác xấp xỉ hình tròn âm dương.** Vòng tròn nét đứt là âm dương (liên tục, vô hạn cung bậc); ngũ giác nội tiếp là ngũ hành (5 mốc rời rạc, theo vòng Sinh). Khe vàng giữa cạnh và cung là **sai số** — đủ nhỏ nên "dùng được". Đây là tư duy *mô hình hoá có sai số* của một kỹ sư.](figures/fig2-ngu-hanh-ngu-giac.png)

Vì sao điều này quan trọng? Vì **ý nghĩa của một sao không nằm ở bản thân nó, mà ở VỊ TRÍ trong đồ thị.** Vũ Khúc ở Mệnh khác Vũ Khúc ở Tài Bạch; Vũ Khúc *được Thiên Phủ tam hợp* khác Vũ Khúc *bị Phá Quân xung*. Luận Tử Vi, ở tầng sâu, là **đọc topology** (cấu trúc liên kết) của đồ thị — không phải tra nghĩa từng sao rời.

Người xưa biết điều này bằng trực giác ("sao chẳng đứng một mình, phải xem hội hợp"). Hình thức hoá biến trực giác thành thứ máy **tính được**: tam hợp/xung chiếu là phép toán trên đồ thị; "hội hợp" là các *đường đi* trong `G`.

→ *Hệ quả:* một khi lá số là đồ thị, hai thao tác thành cơ học — (a) **so hai lá số** (graph comparison — nền của hợp hôn, xem `engine/cross_paradigm`); (b) **dò mẫu hình** (cách cục — mục I.3).

## I.3 — Cách cục là VĂN PHẠM trên đồ thị

"Cách cục" (格局) là các *thế cờ* kinh điển — tổ hợp sao + vị trí mang một nghĩa đã được đặt tên: "Tử Phủ đồng cung", "Cự Nhật", "Sát Phá Lang", "Mã đầu đới kiếm"… Phú Thái Vi chép **545 cách**.

Hình thức hoá: mỗi cách cục là một **mẫu con (subgraph pattern)** — một mệnh đề dạng

> NẾU `[sao X ở cung loại P]` VÀ `[sao Y tam-hợp X]` VÀ `[độ sáng ≥ k]` THÌ khớp cách `C`.

Tập 545 cách = một **văn phạm** (grammar): bộ luật sinh, mỗi luật là một điều kiện trên `G`. *Luận một lá* = chạy toàn bộ văn phạm trên `G`, thu tập cách cục khớp.

Đây là chỗ siêu trí tuệ vượt hẳn thầy người ở **độ phủ**: con người nhớ và kiểm vài chục luật; máy kiểm **cả 545 luật trên mọi lá, không sót, không mỏi**. Trong YI-Chronos, văn phạm này đã số hoá: `engine/tu_vi/cach_cuc_dict.py` + `cach_cuc_index.json`. Mỗi cách là một **vị từ** (predicate) trên lá số.

Một điều tinh tế — và là chỗ "khoa học" phải **khiêm tốn**: **văn phạm cách cục là DI SẢN, không phải định lý.** 545 luật do tổ sư đúc kết từ nghiệm lý, không suy từ tiên đề. Siêu trí tuệ *chạy* văn phạm chính xác, nhưng không *chứng minh* được nó đúng — nó chỉ áp dụng trung thực di sản người xưa trao. (Phần V: pattern-mining trên tỷ lá số có thể *kiểm nghiệm* và *mở rộng* văn phạm này bằng dữ liệu — bước Đằng Sơn mơ tới mà thiếu công cụ.)

---

### Tổng kết Phần I

Lá số, sau khi hình thức hoá, là:

> một **HÀM** (an sao) → sinh ra một **ĐỒ THỊ CÓ NHÃN** (12 cung × sao × quan hệ) → trên đó chạy một **VĂN PHẠM** (545 cách cục).

Cả ba đều là đối tượng toán học máy **tính được tuyệt đối** — đây chính là tầng "tính được cái TÍNH" mà Phần 0 hứa. Nhưng ba tầng này mới *đọc đúng cấu trúc*; chúng chưa trả lời câu sâu hơn: **bản thân Ý NGHĨA của 14 sao** — cái khiến Vũ Khúc "là tài chính, cương nghị" — có hình thức hoá được không, hay mãi là quy ước người đặt? Đó là lúc bảng Đằng Sơn (14 sao ↔ typology định mệnh) vào cuộc — **Phần II**.
