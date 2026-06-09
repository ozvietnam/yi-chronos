_Tổng: **200 atoms** / 8 sections_
# ATOMS REVIEW — CUNG MỆNH v2 (sub-agent bám sách)

**Ngày**: 2026-06-09
**Sách**: Trung Châu Tử Vi Đẩu Số Q2 (Vương Đình Chỉ)
**Quy trình**: 7 sub-agents parallel đọc text → JSON → ingest DB
**Quality**: `viet_thuan` 100% PARAPHRASE source_quote, `nguyen_ly`/`vi_du` NULL nếu sách không nói

## Hướng dẫn anh review

Mỗi atom có ô tick `[ ]`. Anh đánh:
- **✅ đúng paradigm** — atom đúng, để confidence 0.85 → upgrade 0.95
- **⚠ cần sửa** — note lý do, em sửa
- **❌ ẨU bỏ** — em xóa khỏi DB

Không cần review hết 1 lần — anh tick được bao nhiêu thì em xử bấy nhiêu.

---

## Section 5.1.10 — Cự Môn ở cung Mệnh (20 atoms)

### [ ] tcq2-5.1.10-Q01 — p533
**❓ Câu hỏi**: Vì sao Cự Môn được gọi là 'ám tinh'?

**📜 Source quote (NGUYÊN VĂN, p533)**:
> Cự Môn là "ám tinh", không phải là bản thân sao này không có ánh sáng, mà chỉ là nó có thể che ánh sáng của các sao khác mà thôi. Cho nên gọi là "Cự Môn" (cửa lớn) là có ý nghĩa "che ám".

**📖 Hán-Việt giải**: Cự Môn (巨門) = cửa lớn; ám tinh (暗星) = sao tối/che
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn là sao 'che', nó che ánh sáng của các sao khác chứ không phải tự nó tối.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q02 — p533
**❓ Câu hỏi**: Cự Môn có thể che được ánh sáng của Thái Dương không?

**📜 Source quote (NGUYÊN VĂN, p533)**:
> Nói về ánh sáng của các sao, chỉ Thái Dương là không có chỗ nào không chiếu đến, vì vậy Cự Môn không thể che ánh sáng của Thái Dương. Chỉ khi Thái Dương lạc hãm, lúc có ánh sáng yếu nhất, **Cự Môn** mới che được, do đó **Thái Dương** lạc hãm cũng không nên hội **Cự Môn**.

**📖 Hán-Việt giải**: Lạc hãm (落陷) = sao rơi vào cung yếu, mất ánh sáng
**🇻🇳 Việt thuần (paraphrase)**: Thái Dương sáng thì Cự Môn không che được. Thái Dương yếu/lạc hãm thì Cự Môn mới che được — nên Thái Dương lạc hãm không nên gặp Cự Môn.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q03 — p534
**❓ Câu hỏi**: Khi Thiên Đồng gặp Cự Môn đồng độ hoặc vây chiếu thì biến hóa thế nào?

**📜 Source quote (NGUYÊN VĂN, p534)**:
> Nếu **Thiên Đồng** gặp **Cự Môn đồng độ** hoặc vây chiếu, vì Thiên Đồng chủ về tình cảm và tâm trạng, nên nó sẽ biến thành tình cảm và tâm trạng u ám. Người này có nỗi đau khổ thẩm kín trong nội tâm mà không thể cho ai biết.

**📖 Hán-Việt giải**: Đồng độ (同度) = cùng cung; vây chiếu = các cung tam phương chiếu vào
**🇻🇳 Việt thuần (paraphrase)**: Thiên Đồng + Cự Môn → người có nỗi đau giấu kín, không nói được với ai.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q04 — p534
**❓ Câu hỏi**: Khi Thiên Cơ gặp Cự Môn đồng độ hoặc vây chiếu thì biến hóa thế nào?

**📜 Source quote (NGUYÊN VĂN, p534)**:
> Tương tự, nếu **Thiên Cơ** gặp **Cự Môn đồng độ** hoặc vây chiếu, vì Thiên Cơ chủ về cơ mưu, kế hoạch, nên nó sẽ biến thành cơ mưu và kế hoạch bị tính toán sai, dẫn đến phản ứng sai lầm, tiến thoái không hợp thời cơ, gây ra sự do dự và thiếu quyết đoán.

**📖 Hán-Việt giải**: Cơ mưu (機謀) = mưu kế, tính toán
**🇻🇳 Việt thuần (paraphrase)**: Thiên Cơ + Cự Môn → mưu tính sai, tiến/lùi không đúng lúc, do dự.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q05 — p534
**❓ Câu hỏi**: Khi Thái Dương gặp Cự Môn đồng độ hoặc vây chiếu (miếu vượng vs lạc hãm) khác nhau ra sao?

**📜 Source quote (NGUYÊN VĂN, p534)**:
> Có điều, nếu **Thái Dương** gặp **Cự Môn đồng độ** hoặc vây chiếu: Nếu **Thái Dương** nhập miếu thì sẽ không bị **Cự Môn** "ám", ánh sáng vẫn được chiếu xa, chủ về việc được người ngoại quốc hoặc người ở nơi xa xem trọng. Ngược lại, nếu lạc hãm thì ánh sáng lu mờ, khiến công việc đầu voi đuôi chuột.

**📖 Hán-Việt giải**: Nhập miếu (入廟) = sao ở vị trí tốt nhất; đầu voi đuôi chuột = bắt đầu lớn, kết thúc nhỏ
**🇻🇳 Việt thuần (paraphrase)**: Thái Dương + Cự Môn: Thái Dương miếu → được người xa/ngoại quốc trọng vọng. Thái Dương hãm → công việc dở dang.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q06 — p534
**❓ Câu hỏi**: Khi Thiên Cơ Hóa Quyền cùng Cự Môn thì 'che ám' biến thành cái gì?

**📜 Source quote (NGUYÊN VĂN, p534)**:
> "**Thiên Cơ, Cự Môn**" vốn chủ về phản ứng sai lầm, tiến thoái không hợp thời cơ, cho nên người này thường mang ý chí không kiên định. Tuy nhiên, nếu **Thiên Cơ Hóa Quyền**, làm tăng tính ổn định, thì lực "che ám" của **Cự Môn** lại biến thành sự chủ quan quyết định mà phạm sai lầm, vì vậy mà đánh mất cơ hội tốt.

**📖 Hán-Việt giải**: Hóa Quyền (化權) = một trong Tứ Hóa, làm tăng quyền lực/ổn định
**🇻🇳 Việt thuần (paraphrase)**: Thiên Cơ Hóa Quyền + Cự Môn → ổn định hơn nhưng quá chủ quan, quyết định sai, mất cơ hội.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q07 — p534
**❓ Câu hỏi**: Khi Thiên Đồng Hóa Lộc cùng Cự Môn thì 'ẩn tình' biến thành cái gì?

**📜 Source quote (NGUYÊN VĂN, p534)**:
> Lại ví dụ như "**Thiên Đồng, Cự Môn**" vốn chủ về có ẩn tình che giấu triển miên, nhưng nếu **Thiên Đồng Hóa Lộc**, thì lại có thể biến thành sự chấp trước một môn học nào đó hoặc chấp trước một thú vui, sở thích nào đó. Như vậy chưa chắc là không tốt.

**📖 Hán-Việt giải**: Hóa Lộc (化祿) = một trong Tứ Hóa, mang tài lộc/hứng thú; chấp trước = bám chặt, đam mê
**🇻🇳 Việt thuần (paraphrase)**: Thiên Đồng Hóa Lộc + Cự Môn → biến từ 'ẩn tình' thành đam mê một môn học / thú vui — chưa chắc xấu.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q08 — p534
**❓ Câu hỏi**: Thái Dương Cự Môn ở cung Dần được cát hóa và có sao cát thì chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p534)**:
> **Cự Môn** rất ưa **Thái Dương** miếu vượng; nên "**Thái Dương, Cự Môn**" ở cung Dần được cát hóa và có sao cát, chủ về nhờ phú mà được quý, còn dương danh ở nơi xa.

**📖 Hán-Việt giải**: Dương danh (揚名) = nổi danh, làm rạng danh
**🇻🇳 Việt thuần (paraphrase)**: Thái Dương + Cự Môn ở Dần + cát hóa + cát tinh → nhờ giàu mà sang, nổi danh ở nơi xa.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q09 — p534
**❓ Câu hỏi**: Thái Dương Cự Môn ở cung Thân được cát hóa và có sao cát thì chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p534)**:
> Trong khi đó, "**Thái Dương, Cự Môn**" ở cung Thân, được cát hóa và có sao cát, lại chủ về nhờ quý mà được phú, vì vậy rất thích hợp làm công việc ngoại giao hoặc luật sư.

**🇻🇳 Việt thuần (paraphrase)**: Thái Dương + Cự Môn ở Thân + cát hóa + cát tinh → nhờ sang mà giàu, hợp làm ngoại giao / luật sư.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q10 — p534
**❓ Câu hỏi**: Cự Môn đồng độ với Thiên Đồng ở cung Sửu/Mùi có yêu cầu gì? Cổ nhân nhận định ra sao?

**📜 Source quote (NGUYÊN VĂN, p534)**:
> **Cự Môn** và **Thiên Đồng đồng độ**, phải có sao Lộc; nếu không có Lộc thì dù gặp cát tinh cũng không cát tường. Cổ nhân nói: "*Cự Môn ở Sửu, Mùi là hạ cách, dù phú quý cũng không được lâu.*" (Tức là: Sửu Mùi **Cự Môn** ở hạ cách, túng nhiên phú quý việc bất trường).

**📖 Hán-Việt giải**: Túng nhiên (縱然) = dù cho; bất trường (不長) = không lâu
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn + Thiên Đồng đồng độ → bắt buộc phải có sao Lộc. Ở Sửu/Mùi là hạ cách — giàu sang cũng không bền.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q11 — p534
**❓ Câu hỏi**: Khuyết điểm của kết cấu Cự Môn + Thiên Đồng (Sửu/Mùi) là gì?

**📜 Source quote (NGUYÊN VĂN, p534)**:
> Khuyết điểm của kết cấu tinh hệ này là ở chỗ dễ nghe lời. / Đèm xiểm, nói xấu, xử sự nặng tình cảm mà dẫn đến thất bại.

**📖 Hán-Việt giải**: Đèm xiểm = lời xu nịnh, gièm pha
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn + Thiên Đồng → dễ nghe lời nịnh, lời gièm; xử sự nặng tình cảm → thất bại.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q12 — p535
**❓ Câu hỏi**: Cự Môn đồng độ với Thiên Cơ có yêu cầu gì, ở cung nào tốt hơn, và sợ gặp gì?

**📜 Source quote (NGUYÊN VĂN, p535)**:
> **Cự Môn** đồng độ với **Thiên Cơ** cần phải được cát hóa và có sao cát, mới phú quý (ở cung Mão ưu hơn ở cung Dậu); nhưng gặp **Hỏa Tinh**, **Linh Tinh** cùng bay đến là phá cách, chủ về cuộc đời nhiều chìm nổi. Không gặp cát tinh hoặc không được cát hóa, mà gặp sát tinh thì phá tán, thất bại.

**📖 Hán-Việt giải**: Phá cách (破格) = cách cục bị phá hỏng
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn + Thiên Cơ → cần cát hóa + cát tinh (Mão tốt hơn Dậu). Gặp Hỏa/Linh là phá cách, đời nhiều chìm nổi. Gặp sát tinh không cát → phá tán.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q13 — p535
**❓ Câu hỏi**: Cự Môn ở cung Tý/Ngọ là cách gì? Hóa Lộc và Hóa Quyền chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p535)**:
> **Cự Môn** ở hai cung Tý hoặc Ngọ là cách "Thạch trung ẩn ngọc", được cát hóa là tốt. **Hóa Lộc** thì chủ về phú; **Hóa Quyền** thì chủ về quý. Có điều, cuộc đời không nên ở vị trí tối cao.

**📖 Hán-Việt giải**: Thạch trung ẩn ngọc (石中隱玉) = ngọc giấu trong đá
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn ở Tý/Ngọ = cách 'Thạch trung ẩn ngọc'. Hóa Lộc → giàu. Hóa Quyền → sang. Nhưng không nên ở vị trí cao nhất.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q14 — p535
**❓ Câu hỏi**: Cự Môn Hóa Lộc / Hóa Quyền ở Tý/Ngọ thường thất bại ở đại vận nào? Vì sao? Thành công ở đâu?

**📜 Source quote (NGUYÊN VĂN, p535)**:
> Trường hợp **Cự Môn Hóa Lộc** hay **Hóa Quyền**, thường thất bại ở đại vận cung Tị; **Hóa Quyền** thì thất bại vì tranh quyền; **Hóa Lộc** thì thất bại vì quá muốn làm giàu. Nó thường thành công ở các đại vận "**Vũ Khúc**, **Thất Sát**", **Thiên Phủ**.

**📖 Hán-Việt giải**: Đại vận (大運) = vận lớn 10 năm
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn Hóa Lộc/Quyền (Tý/Ngọ) → thất bại ở đại vận Tị (Quyền: tranh quyền; Lộc: quá tham giàu). Thành công ở đại vận Vũ Khúc–Thất Sát, Thiên Phủ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q15 — p535
**❓ Câu hỏi**: Cự Môn ở Tý/Ngọ đồng độ với Lộc Tồn yêu cầu gì, kỵ gì?

**📜 Source quote (NGUYÊN VĂN, p535)**:
> **Cự Môn** ở hai cung Tý hoặc Ngọ, đồng độ với **Lộc Tồn**, cần phải gặp cát tinh mới phú quý. Rất kỵ cung hạn **Thiên Cơ**; cũng không ưa cung tam phương có **Địa Không**, **Địa Kiếp** bay đến. Nó thường thành công ở đại vận gặp sao lộc trùng điệp.

**📖 Hán-Việt giải**: Lộc Tồn (祿存) = sao tài lộc; tam phương = 3 cung chiếu vào
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn + Lộc Tồn (Tý/Ngọ) → cần cát tinh mới giàu sang. Kỵ vận Thiên Cơ, kỵ tam phương có Không/Kiếp. Thành công khi đại vận có nhiều sao lộc.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q16 — p535
**❓ Câu hỏi**: Cự Môn ở Tý/Ngọ không có sao lộc thì luận thế nào?

**📜 Source quote (NGUYÊN VĂN, p535)**:
> **Cự Môn** ở hai cung Tý hoặc Ngọ, không có sao lộc, cần phải đến đại vận hoặc lưu niên gặp sao lộc mới chủ về phát vượt lên; gặp niên hạn có **Địa Không**, **Địa Kiếp** và **Hóa Kỵ** (nhất là **Thiên Cơ Hóa Kỵ**) sẽ chủ về phá tán, thất bại.

**📖 Hán-Việt giải**: Lưu niên (流年) = năm hành niên, vận từng năm
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn Tý/Ngọ thiếu sao lộc → phải chờ đại vận/lưu niên có sao lộc mới phát. Gặp Không/Kiếp + Hóa Kỵ (nhất là Thiên Cơ Hóa Kỵ) → phá tán.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q17 — p535
**❓ Câu hỏi**: Cự Môn ở Tý/Ngọ ảnh hưởng đến Huynh Đệ và hôn nhân thế nào?

**📜 Source quote (NGUYÊN VĂN, p535)**:
> **Cự Môn** ở hai cung Tý hoặc Ngọ, thông thường bất lợi cung Huynh Đệ. Vì vậy không nên hợp tác với người khác, cũng thường chủ về kết hôn muộn, **Cự Môn** ở cung Tý thì càng đúng.

**📖 Hán-Việt giải**: Huynh Đệ = cung anh chị em / bạn bè / partner
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn Tý/Ngọ → bất lợi anh em / partner → không nên hợp tác. Kết hôn muộn — đặc biệt rõ ở cung Tý.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q18 — p535
**❓ Câu hỏi**: Cự Môn ở hai cung Thìn/Tuất thường có tính chất gì? Cổ nhân nhận định?

**📜 Source quote (NGUYÊN VĂN, p535)**:
> **Cự Môn** ở hai cung Thìn hoặc Tuất, thông thường là bất lợi. Cổ nhân nói: "**Cự Môn** ngại bị hãm ở hai cung Thìn Tuất." Chủ về vất vả, tranh chấp thị phi. **Cự Môn Hóa Kỵ**, có sát tinh bay đến là hạ cách.

**📖 Hán-Việt giải**: Thị phi (是非) = đúng sai, tranh cãi
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn Thìn/Tuất → bất lợi, vất vả, tranh chấp thị phi. Hóa Kỵ + sát tinh → hạ cách.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q19 — p535
**❓ Câu hỏi**: Cự Môn ở Thìn/Tuất, cung hạn nào nên đến, cung hạn nào không nên đến?

**📜 Source quote (NGUYÊN VĂN, p535)**:
> **Cự Môn** ở hai cung Thìn hoặc Tuất không nên đến các cung hạn **Thiên Tướng**, **Thiên Lương**, **Thiên Đồng**, **Thiên Phủ**, thường xảy ra sự cỗ; mà nên đến các cung hạn **Thái Âm**, **Thái Dương** nhập miếu. Rất nên đến các vận hạn gặp **Lộc Tồn**, **Hóa Lộc**. Điều này có thể hóa giải tai ách của **Cự Môn**.

**📖 Hán-Việt giải**: Tai ách (災厄) = tai họa, ách nạn
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn Thìn/Tuất: KHÔNG nên gặp vận Thiên Tướng/Lương/Đồng/Phủ. NÊN gặp vận Thái Âm/Thái Dương miếu, đặc biệt Lộc Tồn / Hóa Lộc → hóa giải tai ách.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.10-Q20 — p535
**❓ Câu hỏi**: Cự Môn Hóa Lộc ở cung Thìn cùng Văn Xương Hóa Kỵ thì luận thế nào?

**📜 Source quote (NGUYÊN VĂN, p535)**:
> **Cự Môn Hóa Lộc** ở cung Thìn, có **Văn Xương Hóa Kỵ** đồng cung hoặc vây chiếu, là cách cục đặc biệt, rất phú quý. Đến cung hạn **Thiên Phủ**, là đại vận phát đạt. **Cự Môn** ưa sao tiền tài, cho nên ưa...

**📖 Hán-Việt giải**: Cách cục đặc biệt (特殊格局) = cách cục đặc thù, khác thông thường
**🇻🇳 Việt thuần (paraphrase)**: Cự Môn Hóa Lộc (Thìn) + Văn Xương Hóa Kỵ đồng cung/vây chiếu → cách cục đặc biệt, rất giàu sang. Đại vận Thiên Phủ phát đạt. Cự Môn ưa sao tiền tài.
**⚠ Iron Rule warning**: Đoạn này bị cắt ở cuối trang 535 ('cho nên ưa...') — atom chỉ ghi đến chỗ text dừng. Phần tiếp theo cần xem trang 536.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
## Section 5.1.11 — Thiên Tướng ở cung Mệnh (Thân) (19 atoms)

### [ ] tcq2-5.1.11-Q01 — p536
**❓ Câu hỏi**: Người xưa luận Thiên Tướng thường nhấn mạnh điều gì, và Vương Đình Chi đính chính ra sao?

**📜 Source quote (NGUYÊN VĂN, p536)**:
> Người xưa luận **Thiên Tướng**, thường nhấn mạnh quá đáng phương diện "tường hòa". **Thiên Tướng** gặp thiện thì thành thiện, gặp ác thì thành ác.

**📖 Hán-Việt giải**: tường hòa = điềm lành, hiền hòa, an thuận
**🇻🇳 Việt thuần (paraphrase)**: Thiên Tướng không phải sao thuần cát; nó là 'tấm gương' phản chiếu môi trường — tốt thì thêm tốt, xấu thì hùa theo xấu.
**⚠ Iron Rule warning**: KHÔNG mặc định Thiên Tướng = tốt. Phải xem các sao chung quanh.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q02 — p536
**❓ Câu hỏi**: Khi Tử Vi và Thiên Tướng đồng độ, vai trò của Thiên Tướng thay đổi thế nào?

**📜 Source quote (NGUYÊN VĂN, p536)**:
> Ví dụ như "Tử Vi, Thiên Tướng" đồng độ, nếu có "bách quan triểu củng", thì **Thiên Tướng** sẽ phát huy lực tương trợ; nhưng nếu Tử Vi là "tại dã cô quân", thì **Thiên Tướng** cũng có thể giúp Trụ phò ác.

**📖 Hán-Việt giải**: bách quan triều củng = trăm quan chầu về vua; tại dã cô quân = vua đơn độc ngoài đồng nội; giúp Trụ phò ác = ám chỉ tích Trụ Vương — phụ tá theo bạo chúa làm điều ác
**🇻🇳 Việt thuần (paraphrase)**: Cùng một sao Thiên Tướng cạnh Tử Vi, nếu có quân thần đầy đủ thì thành tướng giỏi; nếu vua trơ trọi thì thành kẻ tiếp tay bạo chúa.
**💡 Nguyên lý**: Tính chất Thiên Tướng = tùy chủ; chủ minh thì phò minh, chủ ác thì phò ác.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q03 — p536
**❓ Câu hỏi**: Trong 14 chính diệu, vì sao Thiên Tướng đặc biệt xem trọng việc giáp cung?

**📜 Source quote (NGUYÊN VĂN, p536)**:
> Trong 14 chính diệu của Đẩu Số, chỉ có **Thiên Tướng** là rất xem trọng việc giáp cung. Bị các sao như Kình Dương, Đà La giáp cung; **Hỏa Tinh**, **Linh Tinh** giáp cung; Địa Không, Địa Kiếp giáp cung; đều không cát tường. Phần nhiều chủ về thị phi, rối rắm, vất vả, bôn ba, đột nhiên xảy ra trắc trở.

**📖 Hán-Việt giải**: giáp cung = hai cung kề bên (trước và sau)
**🇻🇳 Việt thuần (paraphrase)**: Thiên Tướng nhạy với 'hàng xóm hai bên' — sao gì kẹp hai bên ảnh hưởng cực mạnh, hơn các chính tinh khác.
**💡 Nguyên lý**: Thiên Tướng tượng tể tướng cần người phù trợ; hai cung giáp = phụ tá tả hữu.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q04 — p537
**❓ Câu hỏi**: Cách 'Hình kỵ giáp ấn' của Thiên Tướng được Vương Đình Chi định nghĩa lại thế nào?

**📜 Source quote (NGUYÊN VĂN, p537)**:
> Xấu nhất là "Hình kỵ giáp ấn". ...tức **Cự Môn Hóa Kỵ** và **Thiên Lương** giáp cung, chủ về phạm pháp, hình phạt (theo Vương Đình Chi, người xưa lầm là "Hình tù giáp ấn", nên cho là **Kình Dương** và **Liêm Trinh** giáp cung).

**📖 Hán-Việt giải**: ấn = ấn tín = Thiên Tướng (sao tượng tể tướng cầm ấn); Hình kỵ giáp ấn = Hình (Thiên Lương có tính 'hình') và Kỵ (Cự Môn Hóa Kỵ) kẹp Thiên Tướng
**🇻🇳 Việt thuần (paraphrase)**: Đây là điểm hiệu chỉnh quan trọng của Trung Châu phái: cách hung của Thiên Tướng là Cự Môn Hóa Kỵ + Thiên Lương giáp, KHÔNG phải Kình Dương + Liêm Trinh giáp như sách xưa nhầm lẫn.
**⚠ Iron Rule warning**: Khi tra cứu 'Hình kỵ giáp ấn' từ sách cũ, phải đối chiếu định nghĩa Vương Đình Chi.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q05 — p537
**❓ Câu hỏi**: Những sao nào giáp cung Thiên Tướng được coi là cát?

**📜 Source quote (NGUYÊN VĂN, p537)**:
> Nếu **Văn Xương**, **Văn Khúc** giáp cung; **Tả Phụ**, **Hữu Bật** giáp cung; **Thiên Khôi**, **Thiên Việt** giáp cung; đều là điểm cát. Rất ưa "Tài ấm giáp ấn", tức là **Cự Môn Hóa Lộc** đến giáp cung.

**📖 Hán-Việt giải**: Tài ấm giáp ấn = Tài (Cự Môn Hóa Lộc) và ấm (Thiên Lương có tính ấm độ) kẹp Thiên Tướng (ấn)
**🇻🇳 Việt thuần (paraphrase)**: Ngược lại với 'Hình kỵ giáp ấn', cách 'Tài ấm giáp ấn' (Cự Môn Hóa Lộc + Thiên Lương kẹp) là cát thượng đẳng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q06 — p537
**❓ Câu hỏi**: Câu cổ 'Thiên Tướng có thể hóa giải cái ác của Liêm Trinh' nên hiểu thế nào cho đúng?

**📜 Source quote (NGUYÊN VĂN, p537)**:
> Người xưa nhấn mạnh "**Thiên Tướng** có thể hóa giải cái ác của **Liêm Trinh**". Ở đây không phải nói tổ hợp tính hệ "**Liêm Trinh**, **Thiên Tướng**". **Thiên Tướng** tọa mệnh, đến cung hạn **Liêm Trinh** tọa thủ, gặp sao cát thì cát, gặp sao hung thì giảm hung, cũng là điểm hóa giải cái ác.

**🇻🇳 Việt thuần (paraphrase)**: Cổ quyết bị hiểu sai. Không phải Liêm-Tướng đồng cung là tốt; mà là người Mệnh Thiên Tướng khi đi vào đại vận/lưu niên cung có Liêm Trinh thì giảm hung.
**⚠ Iron Rule warning**: Phân biệt 'đồng độ' (cùng cung) vs 'đến cung hạn' (đi qua khi luận vận).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q07 — p537
**❓ Câu hỏi**: Trường hợp Hình kỵ giáp ấn nào được coi là hung nhất?

**📜 Source quote (NGUYÊN VĂN, p537)**:
> Cục "Hình kỵ giáp ấn", rất ngại **Thiên Lương** đổng độ với **Kình Dương**, là cách "Hình kỵ giáp ấn" khá hung. Vì đổng thời sẽ bị **Kình Dương** và **Đà La** giáp cung. Lúc này **Thiên Tướng** tuy đổng độ với **Lộc Tồn**, nhưng chủ về tiền bạc phá tán, khó tụ, mà còn dễ vì tiền bạc mà sinh điểu tiếng thị phi, kiện tụng.

**🇻🇳 Việt thuần (paraphrase)**: Khi Thiên Lương + Kình Dương đồng cung, đối cung Thiên Tướng tự động bị Kình + Đà kẹp. Có Lộc Tồn cũng vô ích — tiền vào lại ra, lại gây kiện tụng.
**💡 Nguyên lý**: Lộc Tồn luôn được Kình - Đà kẹp; khi rơi vào cấu hình này thì Lộc Tồn không cứu được Thiên Tướng.
**⚠ Iron Rule warning**: Thấy Lộc Tồn đừng mừng vội — phải xem Kình Đà có đang kẹp gây hại không.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q08 — p537
**❓ Câu hỏi**: Thiên Tướng đồng độ Hỏa Linh kết hợp Kình Đà giáp hoặc Hình kỵ giáp ấn dẫn đến điều gì?

**📜 Source quote (NGUYÊN VĂN, p537)**:
> **Thiên Tướng** đổng độ với **Hỏa Tinh**, **Linh Tinh**, lại gặp **Kình Dương**, **Đà La** giáp cung, hoặc "Hình kỵ giáp ấn", chủ về lúc nhỏ bất lợi chủ về cha mẹ, hoặc làm con nuôi của người khác. Nếu cung phúc đức là **Thất Sát** lại hội các sao sát, hình, kị, hao, thì chủ về tàn tật.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Tướng + Hỏa Linh cùng cung + 2 nhóm sát kẹp → dấu hiệu hung khi nhỏ với cha mẹ. Phải xem thêm cung Phúc Đức để xác định mức độ.
**⚠ Iron Rule warning**: Cần kiểm tra cung phúc đức trước khi kết luận tàn tật.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q09 — p537
**❓ Câu hỏi**: Vì sao phải xem kèm cung Phụ Mẫu khi Thiên Tướng tọa Mệnh?

**📜 Source quote (NGUYÊN VĂN, p537)**:
> Hễ **Thiên Tướng** tọa mệnh, nên xem kèm cát hung của cung phụ mẫu. Vì **Thiên Tướng** cần được người phù trợ, cung phụ mẫu là cấp trên phù trợ. Lúc này cung phụ mẫu ắt là **Thiên Lương**, tối kỵ **Thiên Lương** đổng độ với **Lộc Tồn**, lại có **Hỏa Tinh**, **Linh Tinh** đổng cung, chủ về suốt đời không có hậu trường để nương dựa, mà bản thân lại khó tự sáng lập sự nghiệp. Có tài mà không gặp thời, thường thường là cách cục này.

**📖 Hán-Việt giải**: hậu trường = chỗ dựa phía sau (cha mẹ, cấp trên, người đỡ đầu)
**🇻🇳 Việt thuần (paraphrase)**: Mệnh Thiên Tướng thì cung Phụ Mẫu luôn là Thiên Lương (cố định trong vòng sao). Nếu cung Phụ Mẫu xấu (Thiên Lương + Lộc Tồn + Hỏa/Linh) thì cả đời không có người đỡ đầu.
**💡 Nguyên lý**: Thiên Tướng = tể tướng, phải có vua + cấp trên dùng mới phát huy. Mất cấp trên = mất đất dụng võ.
**⚠ Iron Rule warning**: Luận Mệnh Thiên Tướng BẮT BUỘC xem cung Phụ Mẫu (Thiên Lương).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q10 — p537
**❓ Câu hỏi**: Thiên Tướng gặp Văn Xương - Văn Khúc cần điều kiện gì để cát?

**📜 Source quote (NGUYÊN VĂN, p537)**:
> **Thiên Tướng** gặp **Văn Xương**, **Văn Khúc**, thì không được gặp **Hóa Kỵ** và **Kình Dương**, **Đà La** mới cát. Nếu không, thì thông minh nhưng mệnh bạc, cũng là điểm có tài mà không gặp thời. Cổ nhân cho rằng, nếu là nữ mệnh là mạng thị thiếp, cũng có ý vị thông minh mà mệnh bạc.

**📖 Hán-Việt giải**: thị thiếp = vợ lẽ, người hầu hạ
**🇻🇳 Việt thuần (paraphrase)**: Văn Xương Khúc tăng tài hoa cho Thiên Tướng, nhưng chỉ tốt khi không bị Hóa Kỵ và Kình Đà phá. Bị phá thì thông minh mà bạc mệnh; nữ mệnh dễ làm thị thiếp.
**⚠ Iron Rule warning**: Đọc nguyên tắc 'thị thiếp' theo paradigm đồng dạng — phản ánh cấu trúc bị dùng làm phụ tá, không tự chủ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q11 — p538
**❓ Câu hỏi**: Cổ quyết về Thiên Tướng gặp Tham-Liêm-Vũ-Phá và Kình-Đà có ý nghĩa gì?

**📜 Source quote (NGUYÊN VĂN, p538)**:
> Cổ nhân cho rằng, (**Thiên Tướng**) **Tham Lang**, **Liêm Trinh**, **Vũ Khúc**, **Phá Quân** **Kình Dương**, **Đà La** mà gặp nhau thì chủ về nhờ tay nghề khéo mà yên thân. Cổ quyết này trọng điểm là ở **Liêm Trinh**. **Liêm Trinh** gặp **Thiên Tướng** chủ về thông minh mẫn tiệp, lại có ý vị... Phục vụ. Cho nên gặp các sao cát thì thích hợp làm việc trong chính giới; nếu gặp **Kình Dương**, **Đà La** thì không nên làm việc trong chính giới, mà thích hợp làm việc hưởng lương, có thể theo ngành nghề công nghệ, khoa học kỹ thuật. Chỉ trường hợp **Thiên Tướng** ở hai cung **Mão** hoặc **Dậu** mới có cách cục này.

**📖 Hán-Việt giải**: tay nghề khéo = thủ nghệ; chính giới = chính trị, công chức nhà nước
**🇻🇳 Việt thuần (paraphrase)**: Cổ quyết chỉ áp dụng được khi Thiên Tướng ở Mão hoặc Dậu (do vòng sao Liêm Trinh - Thiên Tướng hội tụ tại Mão/Dậu). Có sát kẹp thì làm kỹ thuật hưởng lương thay vì làm quan.
**💡 Nguyên lý**: Liêm Trinh + Thiên Tướng = bản chất phục vụ, mẫn tiệp; sát chế khắc thì rẽ hướng kỹ thuật.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q12 — p538
**❓ Câu hỏi**: Thiên Tướng ở cung Mệnh của lưu niên ưa và kỵ những lưu diệu nào?

**📜 Source quote (NGUYÊN VĂN, p538)**:
> **Thiên Tướng** ở cung Mệnh của lưu niên, cũng mẫn cảm đối với các sao cát, hung. Vì vậy không nên gặp các lưu diệu như **Tang Môn**, **Điếu Khách**, **Bạch Hổ**, **Đại Hao**, **Quán Sách**, **Quan Phù**; ưa gặp các sao cát như **Thanh Long**, **Tấu Thư**, **Long Đức**, **Thiên Đức**.

**📖 Hán-Việt giải**: lưu diệu = các sao lưu (chuyển động theo năm)
**🇻🇳 Việt thuần (paraphrase)**: Khi luận lưu niên (vận năm), nếu Thiên Tướng đang tọa cung Mệnh năm đó, đặc biệt nhạy với 'bộ tứ hung lưu' (Tang Điếu Bạch Hổ Đại Hao) và Quán Sách - Quan Phù.
**💡 Nguyên lý**: Tính 'tùy môi trường' của Thiên Tướng lặp lại cả ở vận năm.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q13 — p538
**❓ Câu hỏi**: Thiên Tướng đồng độ Vũ Khúc ở Dần/Thân tra cứu ở đâu?

**📜 Source quote (NGUYÊN VĂN, p538)**:
> "**Thiên Tướng, Vũ Khúc**" đồng độ ở hai cung **Dần** hoặc **Thân**, xin tham khảo đoạn "Vũ Khúc, Thiên Tướng" thuật ở trước.

**🇻🇳 Việt thuần (paraphrase)**: Sách tự chỉ về mục Vũ Khúc khi cần luận tổ hợp Vũ-Tướng tại Dần/Thân.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q14 — p538
**❓ Câu hỏi**: Thiên Tướng độc tọa Sửu hoặc Mùi với Tả Hữu thì sao?

**📜 Source quote (NGUYÊN VĂN, p538)**:
> **Thiên Tướng** độc tọa ở hai cung **Sửu** hoặc **Mùi**, rất ưa có **Tả Phụ**, **Hữu Bật** đồng độ; nếu cung kế cận là **Thiên Đồng Hóa Kỵ**, tuy không thành cách "Hình Kị Giáp Ấn", nhưng cũng không tốt, chủ về tuy có hậu trường để dựa dẫm, nhưng thường thường vào lúc quan trọng thì lại không được trợ lực, cũng là điểm tượng có tài mà không gặp thời. Lúc này nếu có **Tả Phụ**, **Hữu Bật** đồng độ, sẽ chủ về tuy không được bậc trên trước nâng đỡ, trợ lực, nhưng lại được bạn bè chỉ viện.

**🇻🇳 Việt thuần (paraphrase)**: Ở Sửu/Mùi mà cạnh Thiên Đồng Hóa Kỵ thì cấp trên hứa nhiều mà giúp ít. May có Tả-Hữu thì bạn bè đỡ thay.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q15 — p538
**❓ Câu hỏi**: Thiên Tướng ưa 'bách quan triều củng' với ý nghĩa gì?

**📜 Source quote (NGUYÊN VĂN, p538)**:
> **Thiên Tướng** cũng ưa "bách quan triều củng", đây là ý tể tướng chỉ dưới một người mà trên vạn người. Nhưng rốt cuộc thì bị cấp trên gây trắc trở.

**📖 Hán-Việt giải**: bách quan triều củng = trăm quan chầu về (Tả Phụ Hữu Bật, Văn Xương Văn Khúc, Thiên Khôi Thiên Việt cùng hội chiếu)
**🇻🇳 Việt thuần (paraphrase)**: Có đủ phụ tá thì Thiên Tướng phát huy thân tể tướng. Nhưng vì luôn ở dưới 'vua' (Tử Vi/Phá Quân vây chiếu) — cuối cùng vẫn bị cấp trên cản.
**💡 Nguyên lý**: Tể tướng = thân phận thứ hai; số phận luôn lệ thuộc vua chủ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q16 — p538
**❓ Câu hỏi**: Thiên Tướng ở Sửu/Mùi vì sao chủ về nặng thành kiến?

**📜 Source quote (NGUYÊN VĂN, p538)**:
> **Thiên Tướng** ở hai cung **Sửu** hoặc **Mùi**, có "**Tử Vi, Phá Quân**" vây chiếu, cho nên cũng chủ về nặng thành kiến, chủ quan. Nếu có **Hỏa Tình**, **Linh Tinh** đồng độ, thường vì thành kiến chủ quan mà chuốc thất bại.

**📖 Hán-Việt giải**: vây chiếu = đối cung hoặc tam phương chiếu vào
**🇻🇳 Việt thuần (paraphrase)**: Tử Vi (vua) + Phá Quân (xung phá) ở đối cung làm Thiên Tướng nhiễm tính bảo thủ + phá cách. Có Hỏa Linh đốt thêm → cố chấp đến mức tự thua.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q17 — p538
**❓ Câu hỏi**: Thiên Tướng độc tọa Mão hoặc Dậu nên hướng nghề thế nào?

**📜 Source quote (NGUYÊN VĂN, p538)**:
> **Thiên Tướng** độc tọa hai cung **Mão** hoặc **Dậu**, gặp các sao sát, kỵ thì chỉ nên theo ngành công nghệ hay kỹ thuật để mưu sinh. Được cát hóa và có sao cát, chủ về dùng kỹ năng chuyên môn để khởi nghiệp.

**🇻🇳 Việt thuần (paraphrase)**: Mão/Dậu là vị trí đặc trưng cho hướng kỹ thuật. Sát kỵ nhiều = thợ lành nghề; cát hóa + cát tinh = chuyên gia khởi nghiệp.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q18 — p538
**❓ Câu hỏi**: Thiên Tướng độc tọa Mão/Dậu gặp các sao tài nghệ thì sao? Trường hợp xấu là gì?

**📜 Source quote (NGUYÊN VĂN, p538)**:
> **Thiên Tướng** độc tọa hai cung **Mão** hoặc **Dậu**, ưa gặp các sao tài nghệ, như **Thiên Tài**, **Long Trì**, **Phượng Các**; gặp **Tấu Thư** cũng cát. Nếu đồng thời lại gặp sát tinh và **Văn Xương**, **Văn Khúc Hóa Kỵ**, thì đây là thanh khách của nhà giàu thời cổ đại.

**📖 Hán-Việt giải**: thanh khách = môn khách thanh nhã (văn sĩ, nghệ sĩ sống nhờ nhà giàu nuôi)
**🇻🇳 Việt thuần (paraphrase)**: Có Thiên Tài/Long Trì/Phượng Các/Tấu Thư = đa tài đa nghệ. Nhưng nếu thêm sát + Xương Khúc Hóa Kỵ thì biến thành kẻ tài hoa sống nhờ ô dù nhà giàu, không tự lập.
**⚠ Iron Rule warning**: Đọc 'thanh khách nhà giàu' theo paradigm đồng dạng — không phải predict 'anh sẽ làm môn khách'.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.11-Q19 — p538
**❓ Câu hỏi**: Thông thường Thiên Tướng độc tọa Mão/Dậu khi gặp sao lộc kết quả ra sao?

**📜 Source quote (NGUYÊN VĂN, p538)**:
> Trong các tình huống thông thường, **Thiên Tướng** độc tọa hai cung **Mão** hoặc **Dậu** thì nên gặp sao lộc, thì tài cao nghề giỏi, có thể lập thân, trở nên giàu có. Nhưng cuối cùng dễ bị người ta gây trắc trở hoặc điều khiển.

**🇻🇳 Việt thuần (paraphrase)**: Lộc cứu Mão/Dậu: thành thợ giỏi → giàu có. Nhưng bản chất Thiên Tướng = phụ tá → luôn bị người khác chen ngang hoặc điều khiển ở chặng cuối.
**💡 Nguyên lý**: Đây là chủ đề lặp suốt mục Thiên Tướng: dù tốt đến đâu vẫn bị cấp trên/đối tác cản.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
## Section 5.1.12 — Thiên Lương ở cung Mệnh (Thân) (24 atoms)

### [ ] tcq2-5.1.12-Q01 — p539
**❓ Câu hỏi**: Thiên Lương trong Đẩu Số được xếp loại sao gì, và chữ 'ấm' của Thiên Lương bao hàm những nghĩa nào?

**📜 Source quote (NGUYÊN VĂN, p539)**:
> Thiên Lương là 'ấm tinh'. Trong Đẩu Số, 'ấm' có nhiều ý nghĩa, như: Tiêu tai giải ách; kéo dài tuổi thọ; trợ lực của cấp trên hay cha mẹ; hoặc có sinh hoạt tinh thần phong phú về tôn giáo, tín ngưỡng. Tất cả đều mang ý vị 'che chở'. Cần lưu ý, những lực che chở này đều thuộc về tinh thần, không thuộc về vật chất. Từ đó có thể biết đặc tính của Thiên Lương.

**📖 Hán-Việt giải**: 'Ấm tinh' (蔭星) = sao che chở, thuộc tính 'âm phù' (giấu mà nâng đỡ).
**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương là sao 'che chở'. Sự che chở của nó là che chở tinh thần (giải tai, sống thọ, được trên đỡ, có niềm tin tôn giáo), KHÔNG phải che chở vật chất (tiền của).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q02 — p539
**❓ Câu hỏi**: Vì sao tính chất 'tiêu tai giải ách' của Thiên Lương bao hàm việc phải gặp nạn trước rồi mới hóa giải?

**📜 Source quote (NGUYÊN VĂN, p539)**:
> Tính chất 'tiêu tai giải ách' của Thiên Lương, bao hàm ý vị là phải gặp nạn tai trước rồi mới hóa giải. Cho nên ắt sẽ trải qua nguy khó rồi mới bình an; bị bệnh hoạn rồi mới khỏi bệnh; không có chỗ nhờ cậy rồi mới được người ta phù trợ; cảm thấy tinh thần trống rỗng (ý vị cuộc đời có kích thích khá lớn) rồi mới ký thác nơi tôn giáo, những thứ như vậy không cách nào liệt kê ra hết được.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương 'giải hạn' nhưng phải có hạn rồi mới giải được. Người Thiên Lương Mệnh không phải tránh được nạn, mà là phải gặp nạn xong mới qua được.
**💡 Nguyên lý**: Cơ chế 'ấm' là 'nạn → giải', không phải 'tránh nạn'.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q03 — p540
**❓ Câu hỏi**: Vì sao Thiên Lương ưa Hóa Khoa nhưng không ưa Hóa Lộc, Hóa Quyền?

**📜 Source quote (NGUYÊN VĂN, p540)**:
> Do Thiên Lương thiên nặng về tinh thần, mà không thiên nặng về vật chất, cho nên Thiên Lương ưa Hóa Khoa, mà không ưa Hóa Lộc. Hóa Lộc sẽ mang lại thị phi, rối rắm, bị người oán hận. Nó cũng rất ghét Hóa Quyền, lúc Hóa Quyền có thể thành khuynh hướng lộng quyền; gặp Hỏa Tinh, Linh Tinh thì càng đúng.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương vốn là sao tinh thần nên rất hợp Hóa Khoa (tăng danh tiếng). Hóa Lộc đem tiền tài làm Thiên Lương sinh thị phi, người ghét. Hóa Quyền làm Thiên Lương lộng quyền — có Hỏa/Linh thì càng tệ.
**💡 Nguyên lý**: Sao tinh thần + tứ hóa vật chất/quyền lực = lệch bản tính = họa.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q04 — p540
**❓ Câu hỏi**: Vì sao Thiên Lương có thể biểu trưng cho 'hình pháp, kỷ luật' và quan thanh liêm như Bao Công, Hải Thụy?

**📜 Source quote (NGUYÊN VĂN, p540)**:
> Do ý nghĩa 'che chở', có thể mở rộng thành 'hình pháp, kỷ luật', bởi vì 'hình pháp' có thể giữ cho mọi người được thiện lương. Vì vậy Thiên Lương có thể biểu trưng cho vị quan thanh liêm vì dân trừ hại, như Bao Công hay Hải Thụy trong truyền thuyết dân gian. Lúc luận đoán cần phải lưu ý điểm này.

**🇻🇳 Việt thuần (paraphrase)**: 'Che chở' mở rộng thành 'kỷ luật, hình phạt' — hình phạt giữ cho dân giữ thiện. Vì vậy Thiên Lương = quan thanh liêm trừ hại cho dân (Bao Công, Hải Thụy).
**💡 Nguyên lý**: Hình pháp = công cụ giữ thiện = một dạng che chở.
**🎬 Ví dụ đời sống**: Bao Công, Hải Thụy — quan tuần trừ tham, bảo vệ dân.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q05 — p540
**❓ Câu hỏi**: Thiên Lương có hàm nghĩa 'giám sát' biểu hiện qua những nghề nghiệp gì, và hàm nghĩa đó còn diễn hóa thành ý vị gì?

**📜 Source quote (NGUYÊN VĂN, p540)**:
> Do hàm nghĩa mở rộng ở trên, Thiên Lương còn là chức vị giám sát. Phẩm nhiều kiểm toán viên, quản đốc, tranh tra, hoặc chuyên viên nghiên cứu thị trường, chuyên viên kế hoạch tài vụ, v.v... phẩm nhiều cung Mệnh hay cung Sự Nghiệp đều gặp Thiên Lương. Hàm nghĩa 'giám sát' của Thiên Lương cũng có thể diễn hóa thành ý vị 'lui về hậu trường'.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương = sao của vai trò giám sát/kiểm tra: kiểm toán, quản đốc, thanh tra, nghiên cứu thị trường, kế hoạch tài chính. Nó còn nghiêng về 'lui hậu trường' — đứng sau, không đứng trước.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q06 — p540
**❓ Câu hỏi**: Vì sao bác sĩ, thầy thuốc, luật sư thường có quan hệ với Thiên Lương, và Thiên Lương được định là loại nhân tài gì?

**📜 Source quote (NGUYÊN VĂN, p540)**:
> Do 'che chở' có thể mở rộng 'phục vụ người khác', cho nên trị bản của bác sĩ, thầy thuốc, luật sư cũng thường thường có quan hệ mật thiết với Thiên Lương. Dựa vào tiêu chuẩn này có thể định Thiên Lương là nhân tài chuyên nghiệp, là chuyên viên.

**🇻🇳 Việt thuần (paraphrase)**: Che chở mở rộng thành phục vụ người: bác sĩ, thầy thuốc, luật sư. Thiên Lương = chuyên viên, nhân tài chuyên nghiệp.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q07 — p540
**❓ Câu hỏi**: Thiên Lương gặp Thái Dương, Thiên Hình, Kình Dương, Thiên Nguyệt định ra ngành nghề gì?

**📜 Source quote (NGUYÊN VĂN, p540)**:
> Thiên Lương có Thái Dương đồng độ hoặc vây chiếu, gặp Thiên Hình, thích hợp làm nhân viên ngành tư pháp; nếu gặp Kình Dương, thì không phải là bác sĩ ngoại khoa (bao gồm khoa phụ sản); nếu gặp Thiên Nguyệt, là người trong giới y học.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương + Thái Dương + Thiên Hình → ngành tư pháp. + Kình Dương → bác sĩ ngoại khoa (gồm phụ sản). + Thiên Nguyệt → giới y.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q08 — p540
**❓ Câu hỏi**: Tổ hợp 'Thiên Lương, Thiên Cơ' và 'Thiên Lương + Thiên Mã' ứng với loại nghề nghiệp nào?

**📜 Source quote (NGUYÊN VĂN, p540)**:
> 'Thiên Lương, Thiên Cơ' là vạch kế sách quản lý; gặp Thiên Mã, thì làm những nghề nghiệp có tính lưu động, như hàng hải, hàng không, điện tử, v.v... (Có một ví dụ đáng để tham khảo, Vương Đình Chi kể, ông từng đoán mệnh cho một người làm thuê chuyên sao chép băng hình. Nghề nghiệp này nếu không nói ra thì rất khó đoán, nhưng nói ra rồi, thì biết được nghề nghiệp có tính phục vụ và tính lưu động. So với trị bản thì không có chỗ nào là không hợp, do đó có thể thấy nghề nghiệp thời hiện đại, thường thường rất khó nói cụ thể.)

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương + Thiên Cơ = vạch kế sách quản lý. Thêm Thiên Mã = nghề lưu động (hàng hải, hàng không, điện tử...). Nghề hiện đại đa dạng, khó đoán cụ thể.
**🎬 Ví dụ đời sống**: Vương Đình Chi đoán 1 người sao chép băng hình — nghề có tính phục vụ + lưu động.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q09 — p540
**❓ Câu hỏi**: Thiên Lương gặp Văn Xương, Văn Khúc, Tấu Thư đồng độ ứng với nghề gì?

**📜 Source quote (NGUYÊN VĂN, p540)**:
> Thiên Lương có Văn Xương, Văn Khúc, Tấu Thư đồng độ, cũng có thể xem là nhân tài trong ngành pháp luật, sở trường văn thư án lệ, nhưng có lúc cũng có thể là thư kí văn phòng của công ty lớn, hoặc là người trong giới văn hóa, xuất bản.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương + Văn Xương + Văn Khúc + Tấu Thư = nhân tài pháp luật (giỏi văn thư án lệ), hoặc thư ký công ty lớn, hoặc người văn hóa xuất bản.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q10 — p541
**❓ Câu hỏi**: Thiên Lương gặp Bạch Hổ đồng độ chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p541)**:
> Thiên Lương có Bạch Hổ đồng độ, có thể xem là điểm tượng chủ về 'hình pháp, kỷ luật', cũng có thể là bác sĩ phẫu thuật, ngoại khoa.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương + Bạch Hổ = hình pháp kỷ luật, hoặc bác sĩ phẫu thuật/ngoại khoa.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q11 — p541
**❓ Câu hỏi**: Câu cổ 'Thiên Lương Thiên Mã hãm, phiêu đãng vô nghi' có nghĩa gì và nên luận đoán hiện đại như thế nào?

**📜 Source quote (NGUYÊN VĂN, p541)**:
> Cổ nhân nói: 'Thiên Lương và Thiên Mã ở hãm địa, cuộc đời nhất định trôi dạt.' (Thiên Lương Thiên Mã hãm, phiêu đãng vô nghĩ.) Đây là nói Thiên Lương ở hai cung Tị hoặc Hợi, chủ về rời xa quê hương. Ở thời hiện đại người ta thường rời khỏi quê hương để phát triển, vì vậy không nên đoán là trôi dạt; chỉ trong tình hình gặp sao không, hao đồng cung với Hỏa Tinh, Linh Tinh, mới có thể đoán là không giữ một nghề, rời khỏi quê hương mà không có nền tảng. Gặp các sao khoa văn là người cuồng ngạo phóng túng.

**📖 Hán-Việt giải**: 'Phiêu đãng vô nghi' (飄蕩無疑) = trôi dạt không nghi ngờ gì.
**🇻🇳 Việt thuần (paraphrase)**: Cổ: Thiên Lương + Thiên Mã ở hãm → đời trôi dạt (= ở Tị/Hợi, rời quê). Hiện đại: rời quê là bình thường, không đoán trôi dạt; chỉ khi thêm Không/Hao + Hỏa/Linh mới là 'không giữ nghề, rời quê không có nền'. Thêm sao văn → cuồng ngạo phóng túng.
**⚠ Iron Rule warning**: Cổ luận cần điều chỉnh theo thời hiện đại — không phải mọi rời quê đều là trôi dạt.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q12 — p541
**❓ Câu hỏi**: Câu cổ 'Thiên Lương hãm địa kiến Dương Đà, thương phong bại tục' áp dụng cho nữ mệnh ở cung nào, và nên luận hiện đại ra sao?

**📜 Source quote (NGUYÊN VĂN, p541)**:
> Cổ nhân nói: 'Thiên Lương ở hãm địa gặp Kình Dương, Đà La, là trái với thuần phong mĩ tục.' (Thiên Lương hãm địa kiến Dương Đà, thương phong bại tục.) Đây là nói nữ mệnh Thiên Lương ở hai cung Tị hoặc Hợi. Ở thời hiện đại, có thể luận đoán cuộc đời mệnh tạo gặp nhiều đau khổ về tình cảm. Rất ngại Thiên Lương đồng độ với Hỏa Tinh, Linh Tinh, mà Thiên Đồng của đối cung Hóa Kỵ; hoặc hội Thiên Cơ Hóa Kỵ, mà Kình Dương, Đà La giáp Thiên Lương, càng gặp nhiễu tình huống rối rắm khó xử và đau khổ về tình cảm.

**📖 Hán-Việt giải**: 'Thương phong bại tục' (傷風敗俗) = trái thuần phong mỹ tục.
**🇻🇳 Việt thuần (paraphrase)**: Cổ: nữ mệnh Thiên Lương ở Tị/Hợi gặp Kình Dương + Đà La = trái thuần phong. Hiện đại: đời nhiều đau khổ tình cảm. Nặng hơn nữa: Thiên Lương + Hỏa/Linh, đối cung Thiên Đồng Hóa Kỵ; hoặc hội Thiên Cơ Hóa Kỵ + Kình Đà giáp → tình cảm cực rối ren đau khổ.
**⚠ Iron Rule warning**: Cổ ngữ 'thương phong bại tục' không nên translate sống — phải hiểu là tình cảm gập ghềnh.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q13 — p541
**❓ Câu hỏi**: Thiên Lương đến hai cung Tị hoặc Hợi gặp sát, hình, không, hao thì ứng nghiệm tai họa ở những đại vận / lưu niên nào?

**📜 Source quote (NGUYÊN VĂN, p541)**:
> Thiên Lương đến hai cung Tị hoặc Hợi, gặp các sao sát, hình, không, hao, chủ về cuộc đời nhiều tai họa, hoặc nhiều hung hiểm. Thường ứng nghiệm ở niên hạn 'Thiên Cơ, Cự Môn', hay 'Thái Âm, Thái Dương'. Niên hạn gặp Hóa Kỵ cũng thường ngầm chứa nguy cơ họa hoạn. Ngoài ra, các cung hạn Tham Lang, Thiên Đồng tọa thủ là những niên hạn có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương ở Tị/Hợi + sát/hình/không/hao = đời nhiều tai họa. Ứng vào hạn Thiên Cơ-Cự Môn, Thái Âm-Thái Dương, hạn Hóa Kỵ, hạn Tham Lang, hạn Thiên Đồng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q14 — p541
**❓ Câu hỏi**: Thiên Lương ở hai cung Tí hoặc Ngọ không gặp Văn Xương, Văn Khúc thì sao? Cung nào tốt hơn?

**📜 Source quote (NGUYÊN VĂN, p541)**:
> Thiên Lương ở hai cung Tí hoặc Ngọ, không gặp Văn Xương, Văn Khúc là đã thông minh, nhưng thông minh quá lộ, nhìn sự việc quá rõ, nên duyên với người không tốt, nhất là phương hại đến hôn nhân. Ở cung Tí tốt hơn ở cung Ngọ.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương ở Tí/Ngọ không gặp Xương Khúc cũng đã thông minh — nhưng quá lộ, nhìn quá rõ → duyên với người không tốt, hại hôn nhân. Tí tốt hơn Ngọ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q15 — p541
**❓ Câu hỏi**: Thiên Lương ở Tí hoặc Ngọ không gặp sao đào hoa có chủ về tình cảm như thế nào?

**📜 Source quote (NGUYÊN VĂN, p541)**:
> Thiên Lương ở hai cung Tí hoặc Ngọ, không cần gặp sao đào hoa cũng dễ thay đổi tình cảm. Ở xã hội thời cổ đại, đàn ông nạp nhiều thiếp, nên cũng chủ về có nỗi đau khổ không ai biết trong quan hệ hôn nhân.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương ở Tí/Ngọ vốn dễ thay đổi tình cảm dù không có đào hoa. Cổ đại đàn ông nạp thiếp → có nỗi khổ giấu trong hôn nhân.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q16 — p541
**❓ Câu hỏi**: Thiên Lương ở Tí hoặc Ngọ gặp sao lộc kỵ điều gì, và cách xoay chuyển?

**📜 Source quote (NGUYÊN VĂN, p541)**:
> Thiên Lương ở hai cung Tí hoặc Ngọ, nếu gặp sao lộc, rất kỵ là người thông minh mà lạnh lùng, nghiêm khắc. Cần phải đối đãi với người chân thành nhân hậu mới có thể xoay chuyển mệnh vận.

Nếu không, phần nhiều vào Đại Vận thứ ba sẽ xảy ra trắc trở gây ảnh hưởng rất sâu xa. Nhưng thường thường mệnh tạo không tự biết, lúc đến hậu vận gập ghểnh, bất đắc chí, thì oán trời trách người, mà không biết họa căn đã có từ lâu.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương ở Tí/Ngọ + sao Lộc → người thông minh nhưng lạnh lùng nghiêm khắc — rất kỵ. Phải đối đãi chân thành nhân hậu để xoay mệnh. Nếu không, Đại Vận 3 sẽ có trắc trở sâu — nhưng mệnh tạo không biết, đến hậu vận thì đổ tại trời.
**💡 Nguyên lý**: Họa căn gieo từ thái độ sống → biểu hiện trễ ở Đại Vận 3.
**⚠ Iron Rule warning**: Đây là điểm hiếm sách dạy 'tự chuyển mệnh vận' bằng tâm — không phải predict cứng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q17 — p542
**❓ Câu hỏi**: Thiên Lương ở cung Ngọ vì sao không cát tường?

**📜 Source quote (NGUYÊN VĂN, p542)**:
> Thiên Lương ở cung Ngọ thì không cát tường, do hội Thái Âm và Thái Dương đểu ở cung hãm nhược. Nếu cung Tài Bạch là 'Thiên Cơ, Thái Âm' gặp các sao sát, hao, Thiên Mã, sẽ chủ về mệnh tạo có lỗi suy nghĩ đặc biệt, không hợp quần, ít qua lại với ai, và khó gần gũi, gây ảnh hưởng đến sự nghiệp, thu nhập không ổn định. Ví dụ như đột nhiên bị cách chức, bỗng nhiên khách hàng bỏ đi sang chỗ khác, hoặc thường thay đổi cương vị công tác, v.v...

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương ở Ngọ không tốt vì hội Thái Âm + Thái Dương cả 2 hãm. Nếu Tài Bạch là Cơ-Âm + sát/hao/Mã → người có lối nghĩ kỳ lạ, không hợp quần, khó gần → sự nghiệp bị ảnh hưởng (bị cách chức, mất khách, đổi việc liên tục).
**🎬 Ví dụ đời sống**: Đột nhiên bị cách chức, khách hàng bỏ đi, đổi cương vị công tác.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q18 — p542
**❓ Câu hỏi**: Thiên Lương ở Tý hoặc Ngọ điều kiện phú quý là gì?

**📜 Source quote (NGUYÊN VĂN, p542)**:
> Thiên Lương ở hai cung Tý hoặc Ngọ, cần phải gặp Tả Phụ, Hữu Bật, Thiên Khôi, Thiên Việt hội hợp; lại không gặp các sao sát, kị, hình, hao; mới phú quý, mà phú cũng nhờ quý mà có.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương ở Tí/Ngọ phú quý cần: Tả Hữu Khôi Việt hội + không có sát/kỵ/hình/hao. Phú do quý mà ra (danh tiếng → tiền tài).
**💡 Nguyên lý**: Thiên Lương sao tinh thần → quý trước, phú theo sau.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q19 — p542
**❓ Câu hỏi**: Các niên hạn then chốt của Thiên Lương ở Tý hoặc Ngọ là gì?

**📜 Source quote (NGUYÊN VĂN, p542)**:
> Đối với Thiên Lương ở hai cung Tý hoặc Ngọ, các cung hạn 'Thiên Cơ, Thái Âm', Cự Môn, Thái Dương, Thiên Đồng là những niên hạn có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Niên hạn then chốt của Thiên Lương Tí/Ngọ: hạn Cơ-Âm, Cự Môn, Thái Dương, Thiên Đồng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q20 — p542
**❓ Câu hỏi**: Thiên Lương ở Sửu hoặc Mùi vì sao chủ về kế hoạch và tính cơ động, và gặp sát hao chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p542)**:
> Thiên Lương ở hai cung Sửu hoặc Mùi, vì Thiên Cơ vây chiếu, nên chủ về kế hoạch mưu lược, còn chủ về tính cơ động, không ổn định. Vì vậy, nếu gặp các sao sát, hao, cổ nhân cho rằng đây là mạng xuất gia làm tăng nhân, đạo sĩ. Ở thời hiện đại, phần nhiều chủ về có nhân sinh quan đặc biệt (khác với lối suy nghĩ đặc biệt của Thiên Lương ở cung Ngọ, ở đây cần phải phân biệt, một bên là nhân sinh quan, một bên là tác phong xử sự.) Cho nên nếu có các sao Văn Xương, Văn Khúc, Thiên Tài bay đến, thì mệnh tạo là người thông minh tuyệt đỉnh, nhưng không yên ở một nghề, khiến về già không có thành tựu.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương ở Sửu/Mùi có Thiên Cơ vây chiếu → mưu lược + cơ động không ổn. Gặp sát hao: cổ đoán xuất gia tăng đạo; hiện đại = nhân sinh quan đặc biệt (Sửu/Mùi là quan niệm về đời, Ngọ là cách xử sự). Thêm Xương Khúc Thiên Tài → thông minh tuyệt đỉnh, nhưng không yên một nghề → già không thành tựu.
**⚠ Iron Rule warning**: Phải phân biệt: Sửu/Mùi = nhân sinh quan đặc biệt, Ngọ = tác phong xử sự đặc biệt. Đừng nhầm.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q21 — p542
**❓ Câu hỏi**: Thiên Lương ở cung Mùi vì sao không bằng ở Sửu, và ngành nghề nào phù hợp?

**📜 Source quote (NGUYÊN VĂN, p542)**:
> Thiên Lương ở cung Mùi hội Thái Dương của cung Hợi, nên cũng không bằng ở cung Sửu. Hễ Thiên Lương hội Thái Dương ở cung hãm nhược, đều chủ về chuốc oán trách. Nhưng nếu gặp sao hình và các sao Văn Xương, Văn Khúc, Long Trì, Phương Các, Thanh Long, Tấu Thư, Quan Phù, mà không gặp Hỏa Tinh, Linh Tinh, Kình Dương, Đà La, Địa Không, Địa Kiếp thì thích hợp với công tác pháp luật, hoặc liên quan đến 'hình pháp, kỷ luật'.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương ở Mùi (hội Thái Dương Hợi hãm) kém Sửu. Hội Thái Dương hãm → chuốc oán. Nhưng nếu có sao Hình + Xương Khúc + Long Phượng + Thanh Long + Tấu Thư + Quan Phù, KHÔNG có Hỏa Linh Kình Đà Không Kiếp → ngành pháp luật, hình pháp kỷ luật.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q22 — p542
**❓ Câu hỏi**: Thiên Lương ở cung Sửu khi cung Phu Thê là Cự Môn cát hóa chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p542)**:
> Thiên Lương ở cung Sửu, nếu cung Phu Thê là Cự Môn cát hóa (ưa nhất là Hóa Lộc), chủ về có thể kết hôn với người ngoại quốc.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương Sửu + Phu Thê Cự Môn cát hóa (đặc biệt Hóa Lộc) → có thể kết hôn với người nước ngoài.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q23 — p543
**❓ Câu hỏi**: Thiên Lương ở Sửu hoặc Mùi ưa tổ hợp sao nào về sự nghiệp, và rất kỵ đại vận nào?

**📜 Source quote (NGUYÊN VĂN, p543)**:
> Thiên Lương ở hai cung Sửu hoặc Mùi, ưa Thiên Vũ đồng độ với Thái Dương, chủ về được bậc trưởng bối để giúp đỡ, nâng đỡ trong sự nghiệp.

Thiên Lương ở hai cung Sửu hoặc Mùi, rất ngại đến đại vận Tham Lang Hóa Kỵ. Theo bí truyền của phái Trung Châu Vương Đình Chi, đây là hạn vì sắc mà gây ra họa, hoặc là vận gặp nhiều trăn chấp. Cần phải xem hội các sao nào mà định.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương Sửu/Mùi ưa: Thiên Vũ đi với Thái Dương → có trưởng bối nâng đỡ. RẤT NGẠI: đại vận Tham Lang Hóa Kỵ — bí truyền Trung Châu: vận vì sắc gây họa, hoặc nhiều trắc trở.
**⚠ Iron Rule warning**: Đây là bí truyền phái Trung Châu Vương Đình Chi — ghi rõ school.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.12-Q24 — p543
**❓ Câu hỏi**: Thiên Lương ở Sửu hoặc Mùi có khí chất gì dù không gặp sao văn, và các niên hạn then chốt là gì?

**📜 Source quote (NGUYÊN VĂN, p543)**:
> Thiên Lương ở hai cung Sửu hoặc Mùi, không gặp các sao khoa văn cũng đã có khí chất nghệ thuật, nhưng thường có biểu hiện cuồng ngạo, phóng túng.

Đối với Thiên Lương ở hai cung Sửu hoặc Mùi, các cung hạn Tham Lang, Cự Môn, Thái Dương, Thiên Đồng là những lưu niên hay đại vận có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương Sửu/Mùi tự có khí chất nghệ thuật dù không có sao văn — nhưng hay cuồng ngạo phóng túng. Niên hạn then chốt: Tham Lang, Cự Môn, Thái Dương, Thiên Đồng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
## Section 5.1.13 — 5.1.13 (25 atoms)

### [ ] tcq2-5.1.13-Q01 — p543
**❓ Câu hỏi**: Thất Sát đồng cung hay đối nhau với Tử Vi thì hóa làm sao gì, và gặp Tử Vi Hóa Quyền thì sao?

**📜 Source quote (NGUYÊN VĂN, p543)**:
> Thất Sát đồng cung với Tử Vi hay đổi nhau với Tử Vi, đều hóa làm sao Quyền. Nếu gặp Tử Vi Hóa Quyền, thì quyền quá nặng, chưa chắc có lợi. Đến các đại hạn hay lưu niên này ắt không cát tường, cần để phòng xảy ra thất bại. Rất ghét gặp cung hạn Vũ Khúc Hóa Kỵ.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát đồng cung hay đối Tử Vi → tự hóa Quyền. Tử Vi Hóa Quyền thêm vào → quyền quá nặng, không có lợi. Hạn đó dễ thất bại. RẤT GHÉT hạn Vũ Khúc Hóa Kỵ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q02 — p543
**❓ Câu hỏi**: Thiên Lương và Thất Sát đều chủ về 'phong tục luật pháp' — khác nhau ở chỗ nào?

**📜 Source quote (NGUYÊN VĂN, p543)**:
> Thiên Lương chủ về 'phong tục, luật pháp', Thất Sát cũng chủ về 'phong tục, luật pháp', nên cũng chủ về 'hình pháp, kỷ luật'. Có điều, Thiên Lương thuộc văn, Thất Sát thuộc võ; Thiên Lương có thể lui về hậu trường, Thất Sát thì bước lên phía trước. Cho nên Thiên Lương có thể nhuyễn hóa thành 'giám sát', Thất Sát thì nhuyễn hóa thành 'quản lí'.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Lương = văn (lui hậu trường) → giám sát. Thất Sát = võ (bước lên trước) → quản lí. Cả 2 đều liên quan luật pháp kỷ luật.
**💡 Nguyên lý**: Cùng bản chất 'kỷ luật' nhưng văn/võ khác = vai trò khác.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q03 — p543
**❓ Câu hỏi**: Câu cổ 'Hai cung mà gặp nó, định phải trải qua gian khổ' nói về điều gì?

**📜 Source quote (NGUYÊN VĂN, p543)**:
> Cổ nhân nói: 'Hai cung mà gặp nó, định phải trải qua gian khổ.' Tức là hai cung Mệnh Thân mà gặp Thất Sát, đời người ắt sẽ có một thời kì gian khổ. Đại khái là, Thất Sát rất kị đến hai cung hạn Thiên Cơ, Cự Môn tọa thủ; cẩn phải có hành động thiết thực để qua giai đoạn này, mới có thể hởi lòng hởi dạ.

**🇻🇳 Việt thuần (paraphrase)**: Cổ: Mệnh Thân có Thất Sát → đời phải trải qua một giai đoạn gian khổ. Kị hạn Thiên Cơ và Cự Môn tọa thủ. Phải hành động thiết thực mới qua được.
**⚠ Iron Rule warning**: Đây là điểm sách dạy chủ động vượt qua bằng hành động — không phải predict 'chắc chắn khổ'.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q04 — p543
**❓ Câu hỏi**: Thất Sát đối nhau với Thiên Phủ thì sao về tính chất công thủ?

**📜 Source quote (NGUYÊN VĂN, p543)**:
> Thất Sát ắt sẽ đối nhau với Thiên Phủ. Thất Sát chủ về công, Thiên Phủ chủ về thủ, hai sao kiểm chế lẫn nhau, cẩn phải xem ảnh hưởng của hai bên như thế nào.

hoặc Thân có Lộc Tồn đồng độ, đối cung là Tử Vi, Thiên Phủ, mà Thiên Phủ được Lộc Tồn vây chiếu. Cho nên lợi về thủ, mà bất lợi về công. Lúc này Thất Sát tuy chịu ảnh hưởng của Tử Vi ở đối cung, quyền lực của nó cũng nên có khuynh hướng bảo thủ, rất nên phát triển trong cục diện hiện có, mà không nên lập ra cục diện mới, cũng không nên có nhiều thay đổi.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát đối Thiên Phủ: Sát = công (tiến), Phủ = thủ (giữ). Hai sao chế nhau, phải xem bên nào mạnh. Nếu Thân có Lộc Tồn đồng độ + đối cung Tử-Phủ + Thiên Phủ được Lộc Tồn vây chiếu → lợi thủ, bất lợi công → bảo thủ, không mở cục mới, không đổi nhiều.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q05 — p544
**❓ Câu hỏi**: Thất Sát kị tổ hợp Hỏa Tinh, Linh Tinh, Kình Dương như thế nào? Tổ hợp nào xấu nhất?

**📜 Source quote (NGUYÊN VĂN, p544)**:
> Thất Sát kỵ Hỏa Tinh, Linh Tinh. Kỵ nhất là tổ hợp 'Kình Dương, Hỏa Tinh', hay 'Kình Dương, Linh Tinh'. Trong hai nhóm, 'Kình Dương, Linh Tinh' là rất xấu; nếu có Thiên Hình đồng độ, gặp các sao Âm Sát, Đại Hao, Thiên Hư, sẽ chủ về phạm pháp hình sự.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát kỵ Hỏa/Linh. Tệ nhất là Kình + Hỏa hoặc Kình + Linh — Kình Linh tệ hơn. Thêm Thiên Hình + Âm Sát + Đại Hao + Thiên Hư → phạm pháp hình sự.
**⚠ Iron Rule warning**: Tổ hợp này là tổ hợp nguy hiểm cấp tệ nhất của Thất Sát — phải flag riêng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q06 — p544
**❓ Câu hỏi**: Thất Sát ở miếu vượng và ở hãm địa khi gặp Kình-Hỏa, Kình-Linh khác nhau thế nào?

**📜 Source quote (NGUYÊN VĂN, p544)**:
> Thất Sát ở cung miếu vượng, gặp 'Kình Dương, Hỏa Tinh' thì còn được, chỉ chủ về lực kích phát, đời người không ngừng trắc trở nhưng có thể nhờ đó mà tiến bộ. Nếu gặp 'Kình Dương, Linh Tinh', thì có ý vị luân bại dần dần, ở hãm địa thì càng nặng, còn chủ về không có duyên với lục thân, cuộc đời ít được trợ lực.

**🇻🇳 Việt thuần (paraphrase)**: Miếu vượng + Kình Hỏa: trắc trở nhưng kích phát, tiến bộ. Miếu vượng + Kình Linh: luân bại dần dần. Hãm địa + Kình Linh: nặng hơn nữa — không duyên lục thân, ít trợ lực cả đời.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q07 — p544
**❓ Câu hỏi**: Thất Sát gặp một mình Văn Xương, Văn Khúc (không có phụ tá khác) thì sao?

**📜 Source quote (NGUYÊN VĂN, p544)**:
> Thất Sát không nên chỉ hội Văn Xương, Văn Khúc, mà không hội các sao phụ, tá cát khác. Nếu không, thì càng thông minh càng, độc đoán, không chịu nghe ý kiến của người khác, thường là do mệnh tạo gây ra trắc trở.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát không nên CHỈ gặp Xương Khúc mà thiếu phụ tá khác — sẽ thông minh + độc đoán, không nghe ai, tự gây trắc trở.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q08 — p544
**❓ Câu hỏi**: Thất Sát ưa Thiên Khôi Thiên Việt thế nào, và Lưu Khôi Lưu Việt có ý nghĩa gì?

**📜 Source quote (NGUYÊN VĂN, p544)**:
> Thất Sát rất ưa gặp Thiên Khôi, Thiên Việt, thậm chí đến các cung hạn có Lưu Khôi, Lưu Việt vây chiếu hay hội hợp, thường đây cũng là cơ hội chuyển biến theo hướng tốt.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát rất ưa Khôi Việt. Hạn nào có Lưu Khôi Lưu Việt vây chiếu/hội hợp → cơ hội chuyển biến tốt.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q09 — p544
**❓ Câu hỏi**: Thất Sát ưa các sao Hóa Lộc nào, và mức độ tốt khác nhau ra sao?

**📜 Source quote (NGUYÊN VĂN, p544)**:
> Thất Sát cũng ưa gặp sao lộc. Ưa nhất là gặp Phá Quân Hóa Lộc, chủ về đời người trải qua một lần chuyển biến quan trọng mà được phú quý; kế đến là Tham Lang Hóa Lộc, cũng có thể được vinh hoa, nhưng đề phòng phú quý không lâu dài; Vũ Khúc Hóa Lộc cũng tốt, nhưng cách cục kém hơn.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát ưa sao lộc. Xếp hạng: Phá Quân Hóa Lộc (tốt nhất, chuyển biến lớn → phú quý) > Tham Lang Hóa Lộc (vinh hoa nhưng không bền) > Vũ Khúc Hóa Lộc (cũng tốt, cách kém hơn).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q10 — p544
**❓ Câu hỏi**: Vì sao Thất Sát có Sát Hình Không Hao đồng độ thường có khuynh hướng tôn giáo?

**📜 Source quote (NGUYÊN VĂN, p544)**:
> Thất Sát đối nhau với Thiên Phủ, là đã có hàm nghĩa gây trở ngại lẫn nhau, là mâu thuẫn về tính chất. Cho nên lúc Thất Sát có các sao sát, hình, không, hao đồng độ, thường dễ vì gặp trắc trở mà cảm thấy đời người là hư ảo, phần nhiều vì vậy mà có khuynh hướng tôn giáo, bước vào của Phật, Đạo. Có điều, nếu Thiên Phủ gặp sao lộc, thì trước sau vẫn tham luyến duyên trần.

**🇻🇳 Việt thuần (paraphrase)**: Sát + Phủ vốn mâu thuẫn (công vs thủ). Thất Sát + sát/hình/không/hao → trắc trở → đời hư ảo → vào Phật/Đạo. Nhưng nếu Thiên Phủ có sao Lộc → vẫn tham luyến trần thế.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q11 — p544
**❓ Câu hỏi**: Thất Sát ở Tí hoặc Ngọ tổ hợp đối cung là gì, và sao lộc có vai trò gì?

**📜 Source quote (NGUYÊN VĂN, p544)**:
> Thất Sát ở hai cung Tí hoặc Ngọ, có 'Vũ Khúc, Thiên Phủ' vây chiếu, gặp sao lộc thì 'tài tinh' Vũ Khúc có gốc rễ, có thể điều hòa khí chất của Thất Sát. Cho nên có thể nhuyễn hóa thành người.

Trong giới làm ăn kinh doanh. Nếu là người nắm quyền về kinh tế tài chính mà không có sao lộc, chỉ cần không có các sao sát, kị, hình, cũng chủ về được bậc trưởng thượng dùng tài lực giúp đỡ. Đây là được dư khí che chở.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát Tí/Ngọ có Vũ Khúc-Thiên Phủ vây chiếu. + Sao Lộc → Vũ Khúc (tài) có gốc → điều hòa Thất Sát → người làm kinh doanh. Không có Lộc nhưng cũng không có sát/kỵ/hình → vẫn được trưởng thượng giúp tài lực (dư khí che chở).
**💡 Nguyên lý**: Tài tinh Vũ Khúc + Lộc = điều hòa khí võ của Thất Sát.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q12 — p545
**❓ Câu hỏi**: Vì sao Thất Sát ở Tí Ngọ đặc biệt ưa Khôi Việt, Tả Hữu, và Lưu Khôi Lưu Việt có ý nghĩa gì?

**📜 Source quote (NGUYÊN VĂN, p545)**:
> Bởi vì liên quan đến 'sự che chở', cho nên Thất Sát ở hai cung Tý hoặc Ngọ đặc biệt ưa gặp Thiên Khôi, Thiên Việt, Tả Phụ, Hữu Bật. Nếu đến đại vận hoặc lưu niên có Lưu Khôi, Lưu Việt xung kích Thiên Khôi, Thiên Việt của nguyên cục, thì vận hạn hay niên hạn này, đại khái có thể xem là cát lợi, chủ về được người tri ngộ; nhưng nếu có các sao sát, kị, hình hội hợp thì thuộc ngoại lệ.

**🇻🇳 Việt thuần (paraphrase)**: Vì có 'che chở', Thất Sát Tí/Ngọ rất ưa Khôi Việt + Tả Hữu. Lưu Khôi Lưu Việt xung kích Khôi Việt nguyên cục → vận đó cát lợi, có người tri ngộ. Trừ khi có sát/kỵ/hình thì là ngoại lệ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q13 — p545
**❓ Câu hỏi**: Cách 'Hùng Tú Kiền Nguyên' thành ở cung nào, và đại kỵ gì?

**📜 Source quote (NGUYÊN VĂN, p545)**:
> Nếu Thất Sát ở cung Ngọ, thành cách 'Hùng Tú Kiển Nguyên', thì đại kỵ có Hỏa Tình, Linh Tỉnh đồng độ. Cách cục này là hỏa luyện âm kim, gặp Hỏa Tinh, Linh Tỉnh thì hỏa hầu quá lớn, không những đời người gian khổ, mà e rằng còn bị tàn tật. Trường hợp thành cách, cũng ưa đến các đại vận hoặc lưu niên có Tả Phụ, Hữu Bật, Thiên Khôi, Thiên Việt.

**📖 Hán-Việt giải**: 'Hùng Tú Kiền Nguyên' (雄宿乾元) = sao hùng mạnh ở gốc trời.
**🇻🇳 Việt thuần (paraphrase)**: Thất Sát ở Ngọ + đủ điều kiện = cách Hùng Tú Kiền Nguyên. Đại kỵ Hỏa/Linh đồng độ (hỏa luyện âm kim, lửa quá lớn → đời khổ, có thể tàn tật). Thành cách thì ưa các vận có Tả Hữu Khôi Việt.
**💡 Nguyên lý**: Thất Sát = âm kim. Cung Ngọ = hỏa. Hỏa luyện kim vừa đủ = thành cách. Thêm Hỏa/Linh = quá lửa = hủy.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q14 — p545
**❓ Câu hỏi**: Vì sao Thất Sát ở cung Tý KHÔNG thành cách 'Hùng Tú Kiền Nguyên'?

**📜 Source quote (NGUYÊN VĂN, p545)**:
> Thất Sát ở cung Tý không thành cách 'Hùng Tú Kiển Nguyên', vì Tý là phương Bắc thuộc thủy, thủy có thể khắc hỏa. Dù có Hỏa Tinh, Linh Tỉnh đồng độ, cũng chỉ chủ về bôn ba vất vả, nhưng không đến nỗi phá cách.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát ở Tý KHÔNG thành cách Hùng Tú Kiền Nguyên — vì Tý là phương Bắc, thuộc thủy → thủy khắc hỏa. Có Hỏa/Linh thì chỉ bôn ba vất vả, không phá cách.
**💡 Nguyên lý**: Ngũ hành: Tý = Bắc = Thủy → khắc Hỏa của Hỏa/Linh → bảo vệ Thất Sát.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q15 — p545
**❓ Câu hỏi**: Cách Hùng Tú Kiền Nguyên thành công thì ưa tổ hợp nào, và vận phát đạt nhất ở đâu?

**📜 Source quote (NGUYÊN VĂN, p545)**:
> Trường hợp thành cách 'Hùng Tú Kiển Nguyên', rất ưa Liêm Trinh Hóa Lộc, là thượng cách. Chủ về sức sống mạnh, mà còn kiên nghị trác tuyệt, trải qua phấn đấu mà thành đại nghiệp. Vận phát đạt ắt sẽ ở cung hạn Phá Quân tọa thủ. Năm phát đạt nhất sẽ ở cung hạn Liêm Trinh hoặc Tham Lang tọa thủ.

**🇻🇳 Việt thuần (paraphrase)**: Thành cách Hùng Tú Kiền Nguyên + Liêm Trinh Hóa Lộc = thượng cách: sức sống mạnh, kiên nghị, phấn đấu thành đại nghiệp. Vận phát đạt: hạn Phá Quân tọa thủ. Năm đỉnh nhất: hạn Liêm Trinh hoặc Tham Lang tọa thủ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q16 — p545
**❓ Câu hỏi**: Thất Sát Tí/Ngọ không thành cách hoặc phá cách thì kỵ những cung hạn nào?

**📜 Source quote (NGUYÊN VĂN, p545)**:
> Thất Sát ở hai cung Tý hoặc Ngọ, không thành cách hoặc phá cách, lại không nên đến cung hạn Liêm Trinh, chủ về hôn nhân gặp nhiều sóng gió, trắc trở; cũng không nên đến cung hạn 'Thiên Cơ, Cự Môn' tọa thủ, thường thường là giai đoạn thất bại.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát Tí/Ngọ không thành cách hoặc bị phá cách: kỵ hạn Liêm Trinh (hôn nhân sóng gió), kỵ hạn Cơ-Cự Môn (giai đoạn thất bại).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q17 — p545
**❓ Câu hỏi**: Thất Sát ở Dần hoặc Thân có tổ hợp đối cung là gì, và ưa Hóa Khoa hay Hóa Quyền?

**📜 Source quote (NGUYÊN VĂN, p545)**:
> Thất Sát ở hai cung Dần hoặc Thân, đối nhau với 'Tử Vi, Thiên Phủ', không ưa Tử Vi Hóa Quyền, mà rất ưa Tử Vi Hóa Khoa, Thiên Phủ Hóa Khoa. Tử Vi Hóa Khoa chủ về công, Thiên Phủ Hóa Khoa sẽ chủ về thủ.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát Dần/Thân đối Tử-Phủ. KHÔNG ưa Tử Vi Hóa Quyền. RẤT ƯA Tử Vi Hóa Khoa (chủ công) hoặc Thiên Phủ Hóa Khoa (chủ thủ).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q18 — p545
**❓ Câu hỏi**: Thất Sát ở Dần hoặc Thân có tính cách thế nào, và gặp Xương Khúc, Lộc Tồn ra sao?

**📜 Source quote (NGUYÊN VĂN, p545)**:
> Thất Sát ở hai cung Dần hoặc Thân, là người độc đoán; gặp Văn Xương, Văn Khúc thì vì thông minh mà phạm sai lầm; gặp Lộc Tồn đồng độ, khí mà hòa hoãn thì thành cách cục tốt, nhưng tính độc...

Đoán càng nặng. Lúc luận đoán phải chú ý điểm này. Cần phải xem xét kỹ cung Phúc Đức và cung Phu Thê để xác định phẩm tính của mệnh cục. Điều này ảnh hưởng rất lớn đến hậu vận.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát Dần/Thân = người độc đoán. + Xương Khúc → thông minh nhưng phạm sai. + Lộc Tồn đồng độ + khí hòa hoãn → cách tốt, nhưng tính độc đoán càng nặng. Phải xem Phúc Đức + Phu Thê để định phẩm tính mệnh cục → ảnh hưởng hậu vận.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q19 — p546
**❓ Câu hỏi**: Thất Sát ở Dần hoặc Thân gặp Hỏa Linh, và niên hạn then chốt là gì?

**📜 Source quote (NGUYÊN VĂN, p546)**:
> Thất Sát ở hai cung Dần hoặc Thân, gặp Hỏa Tinh, Linh Tỉnh thì nóng nảy, bộc chộp.

Đối với Thất Sát ở hai cung Dần hoặc Thân, các cung hạn 'Liêm Trinh, Thiên Tướng', Cự Môn, Phá Quân, Thái Dương là những đại hạn hoặc lưu niên có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát Dần/Thân + Hỏa/Linh → nóng nảy bộp chộp. Niên hạn then chốt: Liêm-Tướng, Cự Môn, Phá Quân, Thái Dương.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q20 — p546
**❓ Câu hỏi**: Thất Sát ở Thân với Liêm-Tướng ở Ngọ vì sao không thành cách 'Hùng Tú Kiền Nguyên', và vẫn ưa hạn nào?

**📜 Source quote (NGUYÊN VĂN, p546)**:
> Thất Sát ở cung Thân, 'Liêm Trinh, Thiên Tướng' ở cung Ngọ dù không thành cách 'Hùng tú kiển nguyên' (vì Thất Sát thuộc Kim; cung Thân cũng thuộc Kim; Liêm Trinh thuộc Hỏa, cung Ngọ cũng thuộc Hỏa, hai khí Kim Hỏa về gốc, thành mỗi bên một khí, không có tác dụng hỗ tương), nhưng vẫn ưa hai cung hạn Liêm Trinh Hóa Lộc và Phá Quân Hóa Lộc, đây là giai đoạn phát đạt.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát ở Thân + Liêm-Tướng ở Ngọ không thành Hùng Tú Kiền Nguyên vì: Thất Sát Kim + Thân Kim, Liêm Trinh Hỏa + Ngọ Hỏa → Kim-Kim và Hỏa-Hỏa về gốc, mỗi bên 1 khí, không hỗ tương được. Nhưng vẫn ưa hạn Liêm Trinh Hóa Lộc và Phá Quân Hóa Lộc → phát đạt.
**💡 Nguyên lý**: Ngũ hành cùng loại + cùng cung = thuần khí, không có tương sinh/khắc → không tạo cách.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q21 — p546
**❓ Câu hỏi**: Thất Sát ở Thìn hoặc Tuất có tổ hợp đối cung là gì, và kỵ tổ hợp nào?

**📜 Source quote (NGUYÊN VĂN, p546)**:
> Thất Sát ở hai cung Thìn hoặc Tuất, có 'Liêm Trinh, Thiên Phủ' vây chiếu, thì nặng lí trí hơn 'Liêm Trinh, Thất Sát' đồng độ ở hai cung Sửu hoặc Mùi, nhưng phần nhiều người có tư tưởng đặc biệt. Cho nên rất kỵ có Địa Không, Địa Kiếp hội hợp, nếu không, người ta sẽ khó mà hiểu được họ, vì cảm thấy đời người thiếu tri kỷ, nên thành người cô độc, thậm chí nhiều không tưởng, thiểu thực tế.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát Thìn/Tuất có Liêm-Phủ vây chiếu — nặng lý trí hơn Liêm-Sát đồng độ Sửu/Mùi, nhưng đa số có tư tưởng đặc biệt. RẤT KỴ Không/Kiếp hội → người khó hiểu họ → cô độc → không tưởng thiếu thực tế.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q22 — p546
**❓ Câu hỏi**: Thất Sát Thìn/Tuất gặp Xương Khúc và Tham Lang Hóa Lộc thì sao?

**📜 Source quote (NGUYÊN VĂN, p546)**:
> Thất Sát ở hai cung Thìn hoặc Tuất, gặp Văn Xương, Văn Khúc còn được, nhưng cần phải gặp Thiên Khôi, Thiên Việt hoặc Tả Phụ, Hữu Bật, mới có thể phú quý. Nhưng nếu Tham Lang Hóa Lộc đến hội hợp (chú ý, Tham Lang cũng ảnh hưởng cung Phúc Đức), e rằng dục vọng khó thỏa mãn, thế là, tuy phú quý nhưng cũng nhiều vất vả.

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát Thìn/Tuất + Xương Khúc còn được. Cần thêm Khôi Việt hoặc Tả Hữu mới phú quý. Nhưng Tham Lang Hóa Lộc hội (chú ý: Tham Lang ảnh hưởng Phúc Đức) → dục vọng khó thỏa → phú quý nhưng vất vả.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q23 — p546
**❓ Câu hỏi**: Niên hạn then chốt của Thất Sát ở Thìn hoặc Tuất là những hạn nào?

**📜 Source quote (NGUYÊN VĂN, p546)**:
> Đối với Thất Sát ở hai cung Thìn hoặc Tuất, các cung hạn 'Vũ Khúc, Thiên Tướng', 'Thiên Đồng, Cự Môn', Tham Lang, hoặc cung hạn có tỉnh hệ vây chiếu thuật ở trên, là những đại vận hoặc lưu niên có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Niên hạn then chốt của Thất Sát Thìn/Tuất: Vũ-Tướng, Đồng-Cự, Tham Lang, và các cung hạn có tinh hệ vây chiếu đã nêu.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q24 — p546
**❓ Câu hỏi**: Thất Sát ở Thìn/Tuất khi Phúc Đức là Tử Vi Hóa Quyền thì hôn nhân ra sao?

**📜 Source quote (NGUYÊN VĂN, p546)**:
> Thất Sát ở hai cung Thìn hoặc Tuất, nếu cung Phúc Đức là Tử Vi Hóa Quyển, ắt sẽ bất lợi trong hôn nhân, nhất là nữ mệnh, thường chủ về không có sinh hoạt hôn nhân, hay thiếu lạc thú vợ chổng (vì bận rộn, hoặc vì người bạn đời bệnh tật, cần phải xem tổ hợp sao thực tế mà định).

**🇻🇳 Việt thuần (paraphrase)**: Thất Sát Thìn/Tuất + Phúc Đức là Tử Vi Hóa Quyền → bất lợi hôn nhân, đặc biệt nữ mệnh: thường không sinh hoạt vợ chồng, thiếu lạc thú (do bận rộn, hoặc bạn đời bệnh — phải xem tổ hợp sao thực tế).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.13-Q25 — p546
**❓ Câu hỏi**: So sánh tổng quát Thất Sát ở Tí/Ngọ, Dần/Thân, Thìn/Tuất về độ 'thiết thực'?

**📜 Source quote (NGUYÊN VĂN, p546)**:
> Đại khái là, Thất Sát ở hai cung Tí hoặc Ngọ thiết thực hơn Thất Sát ở hai cung Dần hoặc Thân, hay Thất Sát ở hai cung Thìn.

**🇻🇳 Việt thuần (paraphrase)**: Thứ tự thiết thực: Thất Sát Tí/Ngọ > Dần/Thân > Thìn/Tuất.
**⚠ Iron Rule warning**: Câu kết bị cắt ở cuối trang ('hay Thất Sát ở hai cung Thìn') — có thể nguyên văn là 'Thìn hoặc Tuất'.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
## Section 5.1.14 — Phá Quân ở cung Mệnh (Thân) (26 atoms)

### [ ] tcq2-5.1.14-Q01 — p547
**❓ Câu hỏi**: Phá Quân thủ Mệnh gặp sao Lộc có tác dụng gì?

**📜 Source quote (NGUYÊN VĂN, p547)**:
> Phá Quân có sao Lộc rất tốt, là có gốc rễ. Có thể tiêu trừ khuyết điểm hao tổn, phá tán của Phá Quân, làm tăng năng lực sáng tạo.

**🇻🇳 Việt thuần (paraphrase)**: Phá Quân vốn chủ phá hoại, hao tán — gặp Lộc thì có gốc, biến phá thành xây.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q02 — p547
**❓ Câu hỏi**: Phá Quân Hóa Quyền ở Dần (hoặc Thân) có Lộc Tồn đồng độ/vây chiếu thì sao?

**📜 Source quote (NGUYÊN VĂN, p547)**:
> Phá Quân Hóa Quyền ở cung Dần, có Lộc Tồn đồng độ cũng cát, có điểu, tuy phú quý nhưng đời người ắt sẽ có khiếm khuyết. Ví dụ như bản thân sức khỏe không tốt... Phá Quân Hóa Quyền ở cung Thân, có Lộc Tồn vây chiếu, cũng có cùng tình huống.

**🇻🇳 Việt thuần (paraphrase)**: Hóa Quyền + Lộc Tồn → phú quý nhưng đổi lại có khiếm khuyết (thường về sức khỏe).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q03 — p547
**❓ Câu hỏi**: Phá Quân gặp Tả Phụ, Hữu Bật, Thiên Khôi, Thiên Việt thì nghiệp gì, phú hay quý?

**📜 Source quote (NGUYÊN VĂN, p547)**:
> Phá Quân gặp Tả Phụ, Hữu Bật, Thiên Khôi, Thiên Việt, chủ về phú quý, nhưng quý lớn hơn phú, tức tiền bạc nhờ địa vị mà có.

**🇻🇳 Việt thuần (paraphrase)**: Cát phụ tinh hội thì quý trước — có địa vị rồi tiền theo sau.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q04 — p547
**❓ Câu hỏi**: Phá Quân hội cát phụ tinh nhưng có Tứ Sát lẫn vào thì hợp ngành gì?

**📜 Source quote (NGUYÊN VĂN, p547)**:
> Nhưng nếu có Tứ Sát tinh lẫn lộn trong đó, thì thích hợp làm việc trong ngành công thương nghiệp;

**🇻🇳 Việt thuần (paraphrase)**: Có sát thì hướng nghề thương — không thuần chính trị/quan trường.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q05 — p547
**❓ Câu hỏi**: Phá Quân gặp Văn Xương, Văn Khúc có sát tinh thì là người thế nào?

**📜 Source quote (NGUYÊN VĂN, p547)**:
> nếu gặp Văn Xương, Văn Khúc mà có sát tinh, người này là hàn sĩ mang tâm trạng có tài mà không gặp thời.

**🇻🇳 Việt thuần (paraphrase)**: Văn tinh + sát + Phá Quân → trí thức nghèo, uất ức không thi triển.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q06 — p547
**❓ Câu hỏi**: Phá Quân khi sát tinh nặng, cát tinh nhẹ thì nên theo nghề gì?

**📜 Source quote (NGUYÊN VĂN, p547)**:
> Nếu gặp sát tinh nặng mà cát tinh nhẹ, thì nên theo ngành công nghệ, hoặc làm công nhân chuyên nghiệp.

**🇻🇳 Việt thuần (paraphrase)**: Khi cán cân nghiêng về sát thì làm nghề kỹ thuật, lao động chuyên môn.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q07 — p547
**❓ Câu hỏi**: Phá Quân ở Hợi, Tý, Sửu kỵ gặp sao nào, đặc biệt là biến hóa nào?

**📜 Source quote (NGUYÊN VĂN, p547)**:
> Phá Quân ở ba cung Hợi, Tí, Sửu, đều không nên có Văn Khúc đồng độ, ngại nhất là Văn Khúc Hóa Kỵ, chủ về tuổi trẻ rời xa quê hương, hoặc bị tàn tật, hoặc gặp trắc trở nghiêm trọng. Cổ nhân nói: "Cùng với Văn Khúc vào thủy vực, thì tàn tật rời xa, quê hương." (Dữ Văn Khúc nhập thủy vực, tàn tật lí hương.), là nói lý luận này. "Thủy vực" là nói ba cung, Hợi, Tí, Sửu, thuộc hành Thủy.

**📖 Hán-Việt giải**: Dữ Văn Khúc nhập thủy vực, tàn tật lí hương = Cùng Văn Khúc nhập vào miền thủy (Hợi-Tý-Sửu), thì tàn tật và xa quê.
**🇻🇳 Việt thuần (paraphrase)**: Phá Quân + Văn Khúc (đặc biệt Hóa Kỵ) ở 3 cung Thủy → ly hương sớm, tàn tật, trắc trở nặng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q08 — p547
**❓ Câu hỏi**: Phá Quân sợ Kình-Đà hay sợ Hỏa-Linh hơn, hậu quả khác nhau thế nào?

**📜 Source quote (NGUYÊN VĂN, p547)**:
> Phá Quân sợ Kình Dương, Đà La hơn là sợ Hỏa Tinh, Linh Tinh. Gặp Hỏa Tinh, Linh Tinh chỉ chủ về vất vả, bôn ba mà thôi; gặp Kình Dương, Đà La thì có họa tai, cũng chủ về cuối mang tật, hoặc nhiễm thú vui không lành mạnh.

**🇻🇳 Việt thuần (paraphrase)**: Hỏa-Linh → bôn ba khổ sức; Kình-Đà → tai họa, bệnh tật cuối đời, dễ nhiễm xấu.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q09 — p547
**❓ Câu hỏi**: Tính chất 'thừa kế cái cũ mà đổi mới' của Phá Quân biểu hiện thế nào về nghề nghiệp, và Hóa Lộc thêm gì?

**📜 Source quote (NGUYÊN VĂN, p547)**:
> Phá Quân có đặc tính thừa kế cái cũ mà đổi mới. Cho nên phần nhiều đều làm kiêm nhiều nghề, hay kiêm nhiều chức vụ khác nhau. Hóa Lộc sẽ chủ về nhờ sự nghiệp cũ mà có sự nghiệp mới, mà còn đồng thời kinh doanh cả hai, mới lẫn cũ.

**🇻🇳 Việt thuần (paraphrase)**: Phá Quân = phá cũ dựng mới — thường kiêm nhiệm; Hóa Lộc giúp duy trì cả mới và cũ song song.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q10 — p548
**❓ Câu hỏi**: Lực phá hoại của Phá Quân khác với Thất Sát thế nào?

**📜 Source quote (NGUYÊN VĂN, p548)**:
> Lực phá hoại của Phá Quân tuy lớn, nhưng lại khác với Thất Sát. Lực phá hoại của Phá Quân chủ về xảy ra thay đổi lập tức, biểu hiện chủ yếu là "thà là ngọc nát, chứ không chịu là gạch ngói nguyên vẹn", cho nên có tính chất hao tán. Nếu đồng độ với Kình Dương, tức là "hình hao", thường thường làm mạnh thêm ý vị "thà là ngọc nát".

**📖 Hán-Việt giải**: Thà ngọc nát chứ không làm ngói lành = thà gãy chứ không cong, thà chết vinh hơn sống nhục.
**🇻🇳 Việt thuần (paraphrase)**: Phá Quân = thay đổi chớp nhoáng + hao tán; gặp Kình Dương ('hình hao') càng quyết liệt 'thà nát'.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q11 — p548
**❓ Câu hỏi**: Phá Quân đồng độ/vây chiếu Tử Vi có quyền gì? Khác quyền 'Tử Vi - Thất Sát' ra sao?

**📜 Source quote (NGUYÊN VĂN, p548)**:
> Phá Quân cũng ưa đồng độ với Tử Vi, hoặc có Tử Vi vây chiếu, chủ về có quyển. Nhưng khác quyển của "Tử Vi, Thất Sát". Quyển của "Tử Vi, Phá Quân" là ở phương diện lớn, mở rộng; còn quyển của "Tử Vi, Thất Sát" chỉ thuộc phạm vi nhỏ, nội bộ, như quản đốc công xưởng. Một công, một tư, một lớn, một nhỏ; cần phân biệt tỉ mỉ.

**🇻🇳 Việt thuần (paraphrase)**: Tử-Phá = quyền lớn-công-mở rộng; Tử-Sát = quyền nhỏ-tư-nội bộ (giống quản đốc).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q12 — p548
**❓ Câu hỏi**: Phá Quân ở Mệnh/Thân dù gặp cát tinh thì vẫn không toàn mỹ — biểu hiện ra sao?

**📜 Source quote (NGUYÊN VĂN, p548)**:
> Hễ Phá Quân ở cung Mệnh hay cung Thân, bất kể cát tinh hội hợp như thế nào, ắt cũng không toàn mỹ. Phú thì không quý, hoặc quý thì phú; hoặc vợ (chồng) bất toàn; hoặc mắc bệnh mãn tính, phá tướng.

**🇻🇳 Việt thuần (paraphrase)**: Phá Quân ở Mệnh-Thân luôn có 1 mảng khuyết: hoặc phú-quý lệch, hoặc hôn nhân khuyết, hoặc bệnh kinh niên, hoặc phá tướng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q13 — p548
**❓ Câu hỏi**: Phá Quân Hóa Lộc gặp sát-hình thì biểu hiện gì với nam và nữ?

**📜 Source quote (NGUYÊN VĂN, p548)**:
> Phá Quân Hóa Lộc mà gặp các sao sát, hình; nữ mệnh chủ về giải phẫu thẩm mĩ, nam mệnh chủ về bị tổn thương làm phá tướng phải giải phẫu thẩm mĩ.

**🇻🇳 Việt thuần (paraphrase)**: Hóa Lộc + sát-hình → nữ chủ động đi thẩm mỹ; nam bị thương phá tướng rồi mới thẩm mỹ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q14 — p548
**❓ Câu hỏi**: Phá Quân thủ Mệnh khởi nghiệp thế nào? Khác Thiên Đồng ở điểm nào?

**📜 Source quote (NGUYÊN VĂN, p548)**:
> Phá Quân thủ Mệnh, chủ về tay trắng lập nên sự nghiệp. Nhưng khác với Thiên Đồng là phá sạch tổ nghiệp rồi mới lập nên sự nghiệp. Phá Quân có thể nhờ sự che chở, giúp đỡ của cha mẹ, rồi tự khai sáng, cải cách mà tạo sự nghiệp.

**🇻🇳 Việt thuần (paraphrase)**: Thiên Đồng = phá sạch tổ nghiệp xong mới làm lại; Phá Quân = vẫn nhận đỡ từ cha mẹ rồi cải cách dựng nghiệp riêng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q15 — p548
**❓ Câu hỏi**: Vì sao khi xét Phá Quân thủ Mệnh phải coi trọng cung Thiên Di?

**📜 Source quote (NGUYÊN VĂN, p548)**:
> Phá Quân ắt sẽ đối nhau với Thiên Tướng. Thiên Tướng ngoại trừ bị ảnh hưởng của các sao Tả Phụ, Hữu Bật giáp cung ra, còn bị ảnh hưởng của Phá Quân cũng khá lớn. Do người Phá Quân thủ Mệnh phần nhiều đều rời xa quê hương, vì vậy cát hung của Phá Quân có thể ảnh hưởng đến cát hung của Thiên Tướng ở cung Thiên Di. Mức độ chịu ảnh hưởng của Thiên Tướng cũng quan hệ rất lớn đến đời người, cho nên không thể xem thường cung Thiên Di.

**🇻🇳 Việt thuần (paraphrase)**: Phá Quân-Mệnh luôn ly hương → Thiên Tướng ở Thiên Di gánh nặng — phải coi trọng Thiên Di ngang Mệnh.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q16 — p548
**❓ Câu hỏi**: Phá Quân ở Tý/Ngọ, đối cung là gì, và khi nào thành cách bại?

**📜 Source quote (NGUYÊN VĂN, p548)**:
> Phá Quân ở hai cung Tý hoặc Ngọ, đối cung là "Liêm Trinh, Thiên Tướng", Liêm Trinh có thể hòa với khí của Phá Quân, vì vậy nếu được cát hóa và có sao cát thì có thể phú quý. Có điều, nếu Liêm Trinh Hóa Kỵ, hoặc Thiên Tướng bị "Hình kị giáp ấn", thì thành bại cục. Phá Quân có Kình Dương đồng cung, hội Thiên Mã mà không có lộc, cũng là bại cục.

**📖 Hán-Việt giải**: Hình kỵ giáp ấn = Thiên Hình + Hóa Kỵ kẹp hai bên Thiên Tướng (ấn tinh) → cách hung.
**🇻🇳 Việt thuần (paraphrase)**: Phá Quân Tý-Ngọ đối Liêm-Tướng: cát hóa thì phú quý; nhưng Liêm Hóa Kỵ / Thiên Tướng bị Hình-Kỵ giáp / Kình + Mã thiếu Lộc → bại cục.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q17 — p548
**❓ Câu hỏi**: Cách 'Anh tinh nhập miếu' là gì? Nó nói lên điều gì xưa và nay?

**📜 Source quote (NGUYÊN VĂN, p548)**:
> Phá Quân ở hai cung Tý hoặc Ngọ, được cát hóa, gọi là cách "Anh tinh nhập miếu". Rất ra đối cung là Thiên Tướng gặp sao lộc, ở thời cổ đại chủ về lập công ở biên cương, hoặc là trọng thần quân. [p549] Ở thời hiện đại thì chủ về đột nhiên hưng phát sự nghiệp, cho nên cũng có thể thành nhân tài lãnh đạo công ty.

**📖 Hán-Việt giải**: Anh tinh nhập miếu = sao kiệt xuất vào miếu vượng — Phá Quân Tý/Ngọ được cát hóa.
**🇻🇳 Việt thuần (paraphrase)**: Phá Quân Tý-Ngọ + cát hóa + Thiên Tướng đối có Lộc = Anh tinh nhập miếu; xưa lập công biên cương, nay làm thủ lĩnh doanh nghiệp.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q18 — p549
**❓ Câu hỏi**: Cách 'Anh tinh nhập miếu' phát ở vận nào, kỵ vận nào?

**📜 Source quote (NGUYÊN VĂN, p549)**:
> Cách cục "Anh Tỉnh nhập miếu" bắt đầu phát đạt ở vận Thái Âm hoặc vận Thiên Đồng; nhưng không nên đến lưu niên Phá Quân, cũng không ưa đến cung hạn Vũ Khúc Hóa Kỵ, hoặc Liêm Trinh Hóa Kỵ. Cung hạn chỉ hơi có chút sát tinh, thì không toàn mỹ. Vì vậy nên xem xét kỹ những khiếm khuyết ở 12 cung.

**🇻🇳 Việt thuần (paraphrase)**: Anh tinh nhập miếu phát ở vận Thái Âm/Thiên Đồng; kỵ lưu niên Phá Quân và cung hạn Vũ-Kỵ/Liêm-Kỵ; cát mấy cũng phải quét 12 cung.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q19 — p549
**❓ Câu hỏi**: Phá Quân ở Tý/Ngọ KHÔNG thành cách 'Anh tinh nhập miếu' thì sao?

**📜 Source quote (NGUYÊN VĂN, p549)**:
> Phá Quân ở hai cung Tý hoặc Ngọ mà không thành cách "Anh Tỉnh nhập miếu" thì không có duyên với lục thân, việc gì cũng phải đích thân làm, mà còn dễ mắc bệnh.

**📖 Hán-Việt giải**: Lục thân = sáu loại thân quyến (cha-mẹ-anh-em-vợ-con).
**🇻🇳 Việt thuần (paraphrase)**: Phá Quân Tý/Ngọ không đủ cát hóa thì mất duyên ruột thịt, việc gì cũng phải tự làm, dễ bệnh.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q20 — p549
**❓ Câu hỏi**: Phá Quân ở Tý/Ngọ — đại vận và lưu niên nào là then chốt?

**📜 Source quote (NGUYÊN VĂN, p549)**:
> Đối với Phá Quân ở hai cung Tý hoặc Ngọ, các cung hạn "Tử Vi, Thiên Phủ", Cự Môn, Vũ Khúc, Thiên Lương tọa thủ, là những lưu niên có tính then chốt. Đại vận thì xem các cung hạn Vũ Khúc, hoặc "Tử Vi, Thiên Phủ" là có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Phá Quân Tý/Ngọ: lưu niên then chốt = Tử-Phủ / Cự / Vũ / Lương; đại vận then chốt = Vũ Khúc / Tử-Phủ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q21 — p549
**❓ Câu hỏi**: Khi Phá Quân nguyên cục không có Lộc gặp sát, đến vận tài tinh có cứu được không?

**📜 Source quote (NGUYÊN VĂN, p549)**:
> Vũ Khúc và Thiên Phủ là hai sao tiền tài, nếu Phá Quân của nguyên cục không có sao lộc, mà gặp sát tinh, đến cung hạn sao tiền tài tọa thủ, gặp sao lộc và gặp cát tinh, thì cũng có thể bổ cứu; nếu không gặp sao lộc mà gặp sát tinh, thì vận trình cuộc đời nhiều trắc trở.

**🇻🇳 Việt thuần (paraphrase)**: Phá Quân nguyên cục thiếu Lộc + có Sát → vận tài tinh có Lộc + Cát = cứu được; vận tài tinh vẫn không Lộc + Sát = trắc trở suốt đời.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q22 — p549
**❓ Câu hỏi**: Phá Quân ở Dần/Thân — không cần gặp Hỏa-Linh đã có biểu hiện gì? Gặp Lộc-Mã ở Thiên Di thì sao?

**📜 Source quote (NGUYÊN VĂN, p549)**:
> Phá Quân ở hai cung Dần hoặc Thân, không cần gặp Hỏa Tinh, Linh Tinh, cũng đã chủ về lúc nhỏ đã chia lìa với gia đình. Gặp Lộc Tồn, Thiên Mã ở cung thiên di thì chủ về phát đạt ở nơi xa, tha hương.

**🇻🇳 Việt thuần (paraphrase)**: Phá Quân Dần/Thân: tự thân đã ly gia từ nhỏ; Lộc-Mã ở Thiên Di → phát ở phương xa.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q23 — p549
**❓ Câu hỏi**: Phá Quân Dần/Thân gặp Hỏa-Linh ở Mệnh hoặc Phụ Mẫu thì sao?

**📜 Source quote (NGUYÊN VĂN, p549)**:
> Nếu gặp Hỏa Tinh, Linh Tinh ở cung mệnh hoặc cung phụ mẫu, thì chủ về làm con nuôi của người khác, cũng chủ về cuộc đời hay bị đổi cấp trên.

**🇻🇳 Việt thuần (paraphrase)**: Phá Quân Dần/Thân + Hỏa-Linh ở Mệnh / Phụ Mẫu → làm con nuôi; hoặc cả đời thay đổi sếp.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q24 — p549
**❓ Câu hỏi**: Phá Quân Dần/Thân hội Hỏa-Linh dẫn đến đặc trưng vận mệnh và nguyên do thất bại nào?

**📜 Source quote (NGUYÊN VĂN, p549)**:
> Phá Quân ở hai cung Dần hoặc Thân, hội "Hỏa Tinh", "Linh Tinh", chủ về cuộc đời gặp nhiều sóng gió, trắc trở rất lớn, bạo phát bạo bại, hoành phát hoành phá. Nguyên do gây ra thất bại thường là vì quá chủ quan, lại cố xuất đầu lộ diện, hoặc không tự lượng sức đi cạnh tranh với người khác.

**📖 Hán-Việt giải**: Bạo phát bạo bại / hoành phát hoành phá = phát nhanh sụp nhanh, lên ngang xuống ngang.
**🇻🇳 Việt thuần (paraphrase)**: Phá Quân Dần/Thân + Hỏa-Linh → cuộc đời sóng gió, lên xuống chớp nhoáng; thất bại do chủ quan + hiếu thắng + không lượng sức.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q25 — p549
**❓ Câu hỏi**: Phá Quân Dần/Thân — cung hạn nào then chốt, và bại cục xảy ra khi nào?

**📜 Source quote (NGUYÊN VĂN, p549)**:
> Đối với Phá Quân ở hai cung Dần hoặc Thân, hai cung hạn Thiên Cơ, "Liêm Trinh, Thiên Phủ" là có tính then chốt. Nếu cung hạn cát thì hậu vận cũng khá thuận lợi toại ý. Nếu không, năm cung hạn hội hợp Vũ Khúc Hóa Kỵ, hoặc Thiên Tướng bị "Hình kị giáp ân" thì sẽ suy sụp nhanh chóng, mà có thể từ đó không còn đứng lên được.

**🇻🇳 Việt thuần (paraphrase)**: Phá Quân Dần/Thân then chốt ở cung hạn Thiên Cơ + Liêm-Phủ; gặp Vũ Khúc Hóa Kỵ hoặc Thiên Tướng Hình-Kỵ giáp ấn → sụp đổ không gượng dậy nổi.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.14-Q26 — p549
**❓ Câu hỏi**: Phá Quân và Tham Lang gặp Lộc Tồn, Thiên Mã — cổ nhân nói gì?

**📜 Source quote (NGUYÊN VĂN, p549)**:
> Phá Quân và Tham Lang mà gặp Lộc Tồn, Thiên Mã, cổ nhân cho rằng, nam nhân nhiều phóng đãng nữ nhân nhiều đa dâm.

**🇻🇳 Việt thuần (paraphrase)**: Sát-Phá-Tham hệ + Lộc-Mã → cổ nhân cảnh báo về dục vọng: nam phóng đãng, nữ đa dâm.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
## Section 5.1.6 — Liêm Trinh ở cung Mệnh (thân) (33 atoms)

### [ ] tcq2-5.1.6-Q01 — p521
**❓ Câu hỏi**: Liêm Trinh chủ về điều gì, và Liêm Trinh Hóa Kỵ chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p521)**:
> **Liêm Trinh** chủ về tình cảm, cũng chủ về máu. **Liêm Trinh Hóa Kỵ**, về phương diện quan hệ nhân tế là tình cảm bị tổn thương, họa hại; về phương diện cơ thể là bệnh tật liên quan đến máu.

**📖 Hán-Việt giải**: Hóa Kỵ = sao biến hóa thành Kỵ, mang nghĩa trục trặc, tổn hại; nhân tế = quan hệ giữa người với người.
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh chủ tình cảm và máu. Khi hóa thành Kỵ, tình cảm bị tổn thương và cơ thể dễ mắc bệnh về máu.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q02 — p521
**❓ Câu hỏi**: Vì sao Liêm Trinh được gọi là sao 'đào hoa thứ', và khác đào hoa của Tham Lang ở chỗ nào?

**📜 Source quote (NGUYÊN VĂN, p521)**:
> Vì **Liêm Trinh** chủ về tình cảm, nên khi có các sao đào hoa hội hợp, bèn chuyển biến thành tình cảm nam nữ, vì vậy gọi nó là sao “đào hoa thứ”. “Đào hoa thứ” là đối nhau với “đào hoa chính” của **Tham Lang**. **Tham Lang** chủ về hành động, **Liêm Trinh** chủ về tư tưởng, nên gọi là “thứ”. Nói cách khác, đào hoa của **Tham Lang** chủ về theo đuổi sắc tình; còn đào hoa của **Liêm Trinh** là chủ về ghi lòng tạc dạ.

**📖 Hán-Việt giải**: Đào hoa thứ = đào hoa hạng phụ/thứ yếu (so với 'chính'); ghi lòng tạc dạ = khắc sâu trong lòng, tình cảm thuộc về nội tâm tư tưởng.
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh là 'đào hoa thứ' vì thiên về tư tưởng, còn Tham Lang là 'đào hoa chính' vì thiên về hành động. Tham Lang đuổi theo sắc; Liêm Trinh khắc ghi tình.
**💡 Nguyên lý**: Tham Lang = hành động → đào hoa chính; Liêm Trinh = tư tưởng → đào hoa thứ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q03 — p521
**❓ Câu hỏi**: Liêm Trinh liên quan thế nào đến chính trị, và tinh hệ nào đặc biệt có tính chất này?

**📜 Source quote (NGUYÊN VĂN, p521)**:
> **Liêm Trinh** còn là chính trị, hoặc đối với chính trị rất cuồng nhiệt và có lí tưởng. Tinh hệ “**Liêm Trinh**, **Thiên Tướng**” đặc biệt có tính chất này. Tính chất này khi nhuyễn hóa sẽ thành quyền biến hay thủ đoạn; khác với khuynh hướng quan hệ giao tế thiên về tửu sắc của **Tham Lang**.

**📖 Hán-Việt giải**: Nhuyễn hóa = mềm hóa, biến chuyển nhẹ; quyền biến = linh hoạt mưu lược; thủ đoạn = cách thức hành động (có thể trung tính hoặc xấu).
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh có tính cuồng nhiệt với chính trị, nhất là khi đi với Thiên Tướng. Nhẹ thì thành quyền biến, nặng thì thành thủ đoạn — khác với kiểu giao tế tửu sắc của Tham Lang.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q04 — p521
**❓ Câu hỏi**: Vì sao Liêm Trinh ưa Thiên Tướng còn Tham Lang ưa Vũ Khúc?

**📜 Source quote (NGUYÊN VĂN, p521)**:
> **Liêm Trinh** trôi nổi, nóng nảy, thuộc về phương diện tinh thần; **Tham Lang** lẳng lơ, thuộc về hành vi, cử chỉ. Cho nên **Liêm Trinh** ưa **Thiên Tướng**, nhuyễn hóa thành thủ đoạn chính trị linh hoạt và tính chất phục vụ; còn **Tham Lang** thì ưa **Vũ Khúc**, nhuyễn hóa thành thủ đoạn kiếm tiền linh động, khéo ăn khéo ở.

**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh thuộc tinh thần nên hợp Thiên Tướng (chính trị, phục vụ); Tham Lang thuộc hành vi nên hợp Vũ Khúc (kiếm tiền, khéo ăn ở).
**💡 Nguyên lý**: Liêm Trinh = tinh thần ↔ Thiên Tướng; Tham Lang = hành vi ↔ Vũ Khúc. Cặp đôi này quy định 'nhuyễn hóa' của mỗi sao.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q05 — p521
**❓ Câu hỏi**: Liêm Trinh có tính văn-võ thế nào, và cổ nhân nói gì khi Liêm Trinh gặp Văn Xương hoặc sát tinh?

**📜 Source quote (NGUYÊN VĂN, p521)**:
> **Liêm Trinh** có thể văn mà cũng có thể võ. Cho nên cổ nhân nói: “**Liêm Trinh** gặp **Văn Xương** thì giỏi lễ nhạc, gặp sát tinh võ”.

“nghiệp hiển hách.” Vì vậy lúc có **Văn Xương**, **Văn Khúc**, các sao Đào Hoa cùng bay đến, đây là thi tửu phong lưu; đồng độ với **Phá Quân**, gặp sát tinh, sẽ chủ về võ nghiệp, hoặc làm những nghề nghiệp có tính hung hiểm, hay có công cụ bén nhọn.

**📖 Hán-Việt giải**: Đồng độ = ở cùng một cung; sát tinh = các sao có tính sát phạt (Kình Dương, Đà La, Hỏa Tinh, Linh Tinh).
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh vừa văn vừa võ. Gặp Văn Xương thì giỏi lễ nhạc; gặp sát tinh thì võ nghiệp lừng lẫy. Có Văn Xương Văn Khúc + đào hoa = thi tửu phong lưu; đồng cung Phá Quân + sát tinh = võ nghiệp hoặc nghề hiểm/sắc bén.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q06 — p522
**❓ Câu hỏi**: Liêm Trinh tạo kết cấu tốt nào khi đồng độ với Thiên Phủ, hội Tử Vi và Vũ Khúc Thiên Tướng?

**📜 Source quote (NGUYÊN VĂN, p522)**:
> Rất ưa đồng độ với **Thiên Phủ**, hội **Tử Vi** của cung Ngọ và “**Vũ Khúc**, **Thiên Tướng**” của cung Dần, đây là kết cấu tốt. Gặp cát tinh có thể trở thành người hữu dụng. Đây đều là đặc tính văn võ bắt nguồn từ **Liêm Trinh**.

**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh + Thiên Phủ, có Tử Vi (cung Ngọ) và Vũ Khúc Thiên Tướng (cung Dần) hội về là kết cấu tốt; thêm cát tinh thì thành người hữu dụng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q07 — p522
**❓ Câu hỏi**: 'Liêm Trinh, Thiên Tướng' ở Tí/Ngọ và 'Liêm Trinh, Phá Quân' ở Mão/Dậu khác nhau về khí thế nào?

**📜 Source quote (NGUYÊN VĂN, p522)**:
> “**Liêm Trinh**, **Thiên Tướng**” đồng độ ở hai cung Tí hoặc Ngọ, khí hòa hoãn hơn, khác với “**Liêm Trinh**, **Phá Quân**” ở hai cung Mão hoặc Dậu có khí hấp tấp, quyết liệt. Trường hợp sau là trái ngược điển hình.

**📖 Hán-Việt giải**: Khí hòa hoãn = khí thế dịu, ôn hòa; khí hấp tấp quyết liệt = khí thế gấp gáp, mạnh, dứt khoát.
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh + Thiên Tướng ở Tí/Ngọ thì khí dịu hơn; Liêm Trinh + Phá Quân ở Mão/Dậu thì khí gấp và quyết liệt — đây là hai cực đối lập điển hình.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q08 — p522
**❓ Câu hỏi**: 'Liêm Trinh, Thiên Tướng' ở Tí/Ngọ kỵ Hỏa Tinh Linh Tinh thế nào, và trường hợp nào khuynh hướng tự sát rõ nhất?

**📜 Source quote (NGUYÊN VĂN, p522)**:
> “**Liêm Trinh**, **Thiên Tướng**” ở hai cung Tí hoặc Ngọ rất ngại có **Hỏa Tinh**, **Linh Tinh** đồng độ, chủ về gặp trắc trở nghiêm trọng, hoặc có khuynh hướng tự sát. Nhất là lúc **Liêm Trinh Hóa Kỵ** bị **Vũ Khúc Hóa Kỵ** xung hội, lại gặp thêm **Kình Dương**, **Đà La**, **Thiên Hình** xung hội, khuynh hướng này càng đúng.

**📖 Hán-Việt giải**: Đồng độ = ở cùng cung; xung hội = chiếu xung và hội chiếu, tức từ cung đối diện hoặc tam hợp tác động vào.
**🇻🇳 Việt thuần (paraphrase)**: Bộ Liêm-Tướng ở Tí/Ngọ rất sợ Hỏa-Linh đồng cung — dễ trắc trở nặng, có ý tự sát. Nặng nhất là khi Liêm Trinh Hóa Kỵ bị Vũ Khúc Hóa Kỵ xung kèm Kình-Đà-Thiên Hình.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q09 — p522
**❓ Câu hỏi**: Với 'Liêm Trinh, Thiên Tướng' ở Tí/Ngọ, người sinh năm Bính có vận trình hoạnh phát/hoạnh phá ở đâu?

**📜 Source quote (NGUYÊN VĂN, p522)**:
> “**Liêm Trinh**, **Thiên Tướng**” ở hai cung Tí hoặc Ngọ, người sinh năm Bính **Liêm Trinh Hóa Kỵ**, đến cung hạn Thiên Đồng thì hoạnh phát, đến cung hạn Vũ Khúc thì phải để phòng hoạnh phá.

**📖 Hán-Việt giải**: Hoạnh phát = phát giàu/đắc lợi bất ngờ; hoạnh phá = bị phá sản, mất bất ngờ.
**🇻🇳 Việt thuần (paraphrase)**: Bộ Liêm-Tướng Tí/Ngọ, tuổi Bính (Liêm Hóa Kỵ): vận Thiên Đồng phát bất ngờ; vận Vũ Khúc thì phòng phá bất ngờ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q10 — p522
**❓ Câu hỏi**: 'Liêm Trinh, Thiên Tướng' ở Tí/Ngọ ưa cách 'Tài ấm giáp ấn' và Hóa Lộc ra sao, và nên làm nghề gì?

**📜 Source quote (NGUYÊN VĂN, p522)**:
> “**Liêm Trinh**, **Thiên Tướng**” ở hai cung Tí hoặc Ngọ rất ưa “Tài ấm giáp ấn”, **Liêm Trinh Hóa Lộc**, hoặc **Phá Quân Hóa Lộc** ở đối cung, sẽ chủ về phú quý, nhưng vẫn chỉ nên ở vị trí phụ tá, hay phó, nghề nghiệp có tính chất làm việc hưởng lương.

**📖 Hán-Việt giải**: Tài ấm giáp ấn = cách Tài (Vũ Khúc) và Ấm (Thiên Lương) giáp cung có Thiên Tướng (Ấn), một kết cấu cát; đối cung = cung xung chiếu.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Tướng Tí/Ngọ ưa cách 'Tài ấm giáp ấn'; có Liêm Hóa Lộc hoặc Phá Quân Hóa Lộc ở đối cung thì phú quý — nhưng chỉ nên làm phụ tá/phó, hoặc nghề ăn lương.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q11 — p522
**❓ Câu hỏi**: Vận trình then chốt của 'Liêm Trinh, Thiên Tướng' (Tí/Ngọ) là gì?

**📜 Source quote (NGUYÊN VĂN, p522)**:
> “**Liêm Trinh**, **Thiên Tướng**” ngoại trừ người sinh năm Bính lấy hai cung hạn Thiên Đồng, Vũ Khúc làm vận trình có tính then chốt ra, còn lại là đều lấy các cung hạn “**Tử Vi**, **Thiên Phủ**”, **Vũ Khúc**, **Cự Môn**, **Phá Quân** làm đại vận hoặc lưu niên có tính then chốt.

**📖 Hán-Việt giải**: Đại vận = vận 10 năm; lưu niên = vận từng năm.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Tướng: tuổi Bính then chốt ở vận Thiên Đồng và Vũ Khúc; tuổi khác then chốt ở vận Tử Vi-Thiên Phủ, Vũ Khúc, Cự Môn, Phá Quân.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q12 — p522
**❓ Câu hỏi**: 'Liêm Trinh, Thất Sát' ở Sửu hoặc Mùi cấu thành cách 'Hùng tú kiển nguyên' ở cung nào, và điều kiện ra sao?

**📜 Source quote (NGUYÊN VĂN, p522)**:
> “**Liêm Trinh**, **Thất Sát**” ở hai cung Sửu hoặc Mùi, chỉ có cung Mùi mới có thể cấu tạo thành cách cục “Hùng tú kiển nguyên”. Điều kiện là gặp các sao phụ tá cát, không có tứ sát tinh và các sao hình, kị, Địa Không, Địa Kiếp xung hội, chủ về trải qua gian khổ mà thành giàu có. Ở cung Sửu chỉ có mức sống trung bình.

**📖 Hán-Việt giải**: Hùng tú kiển nguyên = cách cục mạnh, hào kiệt đứng đầu; tứ sát tinh = Kình Dương, Đà La, Hỏa Tinh, Linh Tinh; xung hội = chiếu xung và hội chiếu.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Sát chỉ thành 'Hùng tú kiển nguyên' ở cung Mùi, với điều kiện có phụ tá cát + không bị tứ sát/hình/kỵ/Không Kiếp xung hội — qua gian khổ mới giàu. Ở Sửu chỉ trung bình.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q13 — p522
**❓ Câu hỏi**: Khi 'Liêm Trinh, Thất Sát' ở cung Mùi có Liêm Trinh Hóa Lộc thì sao?

**📜 Source quote (NGUYÊN VĂN, p522)**:
> Ở cung Mùi, **Liêm Trinh Hóa Lộc**, là cách “thanh bạch”, cũng chủ về dư giả, nếu không có **Hỏa Tinh**, **Linh Tinh** hội chiếu sẽ chủ về phú quý; ở cung Sửu cũng chỉ thành cục trung bình.

**📖 Hán-Việt giải**: Cách thanh bạch = kết cấu trong sạch, giàu mà không nhơ nhuốc.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Sát ở Mùi mà Liêm Hóa Lộc = cách 'thanh bạch', dư giả; không có Hỏa-Linh hội chiếu thì phú quý. Ở Sửu cũng chỉ trung bình.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q14 — p523
**❓ Câu hỏi**: 'Liêm Trinh, Thất Sát' ở Sửu/Mùi không ưa các sao nào, và mỗi sao mang theo hậu quả gì?

**📜 Source quote (NGUYÊN VĂN, p523)**:
> “**Liêm Trinh**, **Thất Sát**” ở hai cung Sửu hoặc Mùi không ưa có...

Kinh Dương đông độ, chủ về gặp nhiều thị phi; cũng không ưa có Đà La đông độ, chủ về gặp nhiều rối ren vô vị; còn không ưa gặp Hỏa Tinh, Linh Tinh, chủ về bị trắc trở nghiêm trọng.

**📖 Hán-Việt giải**: Đồng độ (text in 'đông độ' = OCR lỗi của 'đồng độ') = ở cùng cung.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Sát ở Sửu/Mùi sợ: Kình Dương → nhiều thị phi; Đà La → nhiều rối ren vô nghĩa; Hỏa Linh → trắc trở nặng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q15 — p523
**❓ Câu hỏi**: Khi 'Liêm Trinh, Thất Sát' đồng độ mà Liêm Trinh Hóa Kỵ + sao hình hao sát thì sao? Còn khi Vũ Khúc/Văn Khúc/Văn Xương Hóa Kỵ xung khởi + Hỏa Linh?

**📜 Source quote (NGUYÊN VĂN, p523)**:
> “Liêm Trinh, Thất Sát” đông độ, mà Liêm Trinh Hóa Kỵ, lại gặp các sao hình, hao, sát, chủ về chết ở xứ người. Nếu Vũ Khúc Hóa Kỵ, hoặc Văn Khúc hay Văn Xương Hóa Kỵ xung khởi, lại có Hỏa Tinh, Linh Tinh hội hợp, chủ về sự cố bất trắc, nghiêm trọng thì ngầm có ý định tự sát.

**📖 Hán-Việt giải**: Sao hình, hao, sát = nhóm sao Thiên Hình, Đại Hao/Tiểu Hao, và các sát tinh; xung khởi = từ cung khác xung lên kích hoạt.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Sát đồng cung + Liêm Hóa Kỵ + hình-hao-sát → chết xứ người. Nếu Vũ/Văn Khúc/Văn Xương Hóa Kỵ xung kèm Hỏa-Linh → sự cố bất trắc nặng, có thể ngầm tính tự sát.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q16 — p523
**❓ Câu hỏi**: Vận trình then chốt của 'Liêm Trinh, Thất Sát' ở Sửu/Mùi là gì?

**📜 Source quote (NGUYÊN VĂN, p523)**:
> Đối với “Liêm Trinh, Thất Sát” ở hai cung Sửu hoặc Mùi, các cung hạn Thiên Lương, “Vũ Khúc, Phá Quân”, Thiên Đông là những lưu niên hay đại hạn có tính then chốt.

**📖 Hán-Việt giải**: 'Thiên Đông' trong text là OCR lỗi của 'Thiên Đồng'.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Sát Sửu/Mùi: vận then chốt là Thiên Lương, Vũ Khúc-Phá Quân, Thiên Đồng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q17 — p523
**❓ Câu hỏi**: Liêm Trinh độc tọa ở Dần hoặc Thân khác nhau thế nào về cách cục?

**📜 Source quote (NGUYÊN VĂN, p523)**:
> **Liêm Trinh độc tọa** ở hai cung Dần hoặc Thân, trường hợp ở cung Thân cũng thành cách cục “Hùng tú kiển nguyên”, có thể tham khảo đoạn ở trên. Trường hợp ở cung Dần, không thành cách cũng như trên.

**📖 Hán-Việt giải**: Độc tọa = một mình ngồi cung (không đồng cung với chính tinh khác).
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh độc tọa: ở Thân thành 'Hùng tú kiển nguyên'; ở Dần không thành cách này.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q18 — p523
**❓ Câu hỏi**: Liêm Trinh ở Dần/Thân kỵ tổ hợp nào dẫn đến trộm cắp và trụy lạc?

**📜 Source quote (NGUYÊN VĂN, p523)**:
> Liêm Trinh ở hai cung Dần hoặc Thân, rất kỵ Văn Khúc bay đến cung Thiên Di, cung Mệnh lại hội Văn Xương, còn hội các tạp điệu Âm Sát, Đại Hao, Thiên Hư, Thiên Hình, và Vũ Khúc Hóa Kỵ đến hội; các sao ác sát nặng, chủ về có khuynh hướng trộm cắp, mà còn chủ về quyến luyến tửu sắc, trụy lạc, mà dẫn đến thất bại.

**📖 Hán-Việt giải**: Tạp diệu (text 'tạp điệu' = OCR lỗi) = các sao phụ nhỏ; Thiên Di = cung di chuyển, đối cung Mệnh; ác sát = sao xấu sát phạt.
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh Dần/Thân sợ tổ hợp: Văn Khúc ở Thiên Di + Văn Xương hội Mệnh + Âm Sát, Đại Hao, Thiên Hư, Thiên Hình + Vũ Khúc Hóa Kỵ + ác sát nặng → khuynh hướng trộm cắp, đắm tửu sắc, trụy lạc, thất bại.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q19 — p523
**❓ Câu hỏi**: Cổ quyết 'Liêm Tham Sát Phá phùng, Văn Khúc Thiên Di tác bối nhung' nghĩa là gì, và có tranh luận chú giải nào?

**📜 Source quote (NGUYÊN VĂN, p523)**:
> Cổ quyết nói: “Liêm Trinh, Tham Lang, Thất Sát, Phá Quân gặp nhau, Văn Khúc ở Thiên Di là làm giặc.” (Trích: Liêm Trinh Tham Sát Phá Quân phùng, Văn Khúc Thiên Di tác bối nhung).

Theo Vương Đình Chỉ, hai chữ “bối nhung” ghép lại là chữ tặc “8X”. Đời nay, có người cho rằng đây là do chép lầm của hai chữ “binh nhung”, giải thích là “võ nghiệp hiển quý”, hoàn toàn trái ngược với kiến giải của Vương Đình Chỉ.

**📖 Hán-Việt giải**: Bối nhung 背戎 ghép = chữ 'tặc' (giặc); binh nhung 兵戎 = võ nghiệp/binh đao; phùng = gặp nhau.
**🇻🇳 Việt thuần (paraphrase)**: Cổ quyết: Liêm-Tham-Sát-Phá phùng + Văn Khúc ở Thiên Di → làm giặc. Vương Đình Chỉ giữ nguyên 'bối nhung' = ghép thành chữ tặc. Có người sửa thành 'binh nhung' = võ nghiệp hiển quý — trái ngược hoàn toàn.
**⚠ Iron Rule warning**: Có dị bản: 'bối nhung' (giặc) ↔ 'binh nhung' (võ nghiệp). Sách giữ lập trường Vương Đình Chỉ — em phải flag khi đối chiếu sách khác.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q20 — p523
**❓ Câu hỏi**: Liêm Trinh ở Dần/Thân có Tham Lang đối cung gặp Hỏa/Linh thì sao?

**📜 Source quote (NGUYÊN VĂN, p523)**:
> Liêm Trinh ở hai cung Dần hoặc Thân, cũng ưa Tham Lang ở đối cung thành cách “Hỏa Tham” hay cách “Linh Tham”, chủ về phát lên một cách đột ngột, cũng chủ về được tiền của nhờ vợ, hoặc nhờ vợ trợ giúp mà trở nên giàu có.

**📖 Hán-Việt giải**: Hỏa Tham = Tham Lang gặp Hỏa Tinh; Linh Tham = Tham Lang gặp Linh Tinh — đều là cách phát đột ngột.
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh Dần/Thân thích Tham Lang đối cung kết Hỏa Tham/Linh Tham — phát đột ngột, hoặc được tiền nhờ vợ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q21 — p523
**❓ Câu hỏi**: Vận trình then chốt của Liêm Trinh ở Dần/Thân là gì?

**📜 Source quote (NGUYÊN VĂN, p523)**:
> Đối với Liêm Trinh ở hai cung Dần hoặc Thân, các cung hạn **Thất Sát**, **Phá Quân**, **Tham Lang**, **Thiên Lương** và bản thân **Liêm Trinh**, là những lưu niên có tính then chốt; và các cung hạn **Thất Sát**, **Thiên Lương**, “Thiên Cơ, Cự Môn”, “Vũ Khúc, Thiên Phú” là những đại vận có tính then chốt.

**📖 Hán-Việt giải**: 'Thiên Phú' trong text là OCR lỗi của 'Thiên Phủ'.
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh Dần/Thân: lưu niên then chốt = Thất Sát, Phá Quân, Tham Lang, Thiên Lương, chính Liêm Trinh. Đại vận then chốt = Thất Sát, Thiên Lương, Thiên Cơ-Cự Môn, Vũ Khúc-Thiên Phủ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q22 — p524
**❓ Câu hỏi**: 'Liêm Trinh, Phá Quân' ở Mão/Dậu kỵ Hỏa Linh đồng độ, và gặp sát tinh nặng + Thiên Hình thì sao?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> Rất ngại có **Hỏa Tinh**, **Linh Tinh đồng độ**, chủ về suy sụp nhanh chóng; gặp **sát tinh** nặng, còn gặp thêm **Thiên Hình**, sẽ chủ về bị phẫu thuật, hoặc xảy ra sự cố bất trắc.

**🇻🇳 Việt thuần (paraphrase)**: Liêm-Phá Mão/Dậu sợ Hỏa-Linh đồng cung → suy sụp nhanh; nặng + Thiên Hình → mổ xẻ, sự cố bất trắc.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q23 — p524
**❓ Câu hỏi**: Khi nào là 'năm ứng nghiệm' của 'Liêm Trinh, Phá Quân' Mão/Dậu?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> **Liêm Trinh Hóa Kỵ** ở lưu niên xung khởi là năm ứng nghiệm (cung Mệnh của nguyên cục là “Liêm Trinh, Phá Quân”, lúc cung Tật Ách của lưu niên cũng là “Liêm Trinh, Phá Quân”, có sao kỵ xung phá cũng vậy).

**📖 Hán-Việt giải**: Lưu niên = năm vận hành hiện thời; xung khởi = từ cung khác xung lên kích hoạt; nguyên cục = lá số gốc; cung Tật Ách = cung bệnh tật.
**🇻🇳 Việt thuần (paraphrase)**: Năm ứng nghiệm của Liêm-Phá Mão/Dậu: khi lưu niên có Liêm Hóa Kỵ xung khởi, hoặc cung Tật Ách lưu niên cũng là Liêm-Phá có Kỵ xung phá.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q24 — p524
**❓ Câu hỏi**: Nếu 'Liêm Trinh, Phá Quân' Mão/Dậu gặp Liêm Trinh Hóa Lộc, thì bệnh tật rơi vào đâu?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> Nếu **Liêm Trinh, Phá Quân** ở hai cung Mão hoặc Dậu, và gặp **Liêm Trinh Hóa Lộc**, thì cung Tật Ách ắt sẽ là **Thái Dương Hóa Kỵ**, vì vậy chủ về bệnh tật ở mắt.

**📖 Hán-Việt giải**: Tật Ách = cung bệnh tật/tai ách.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Phá Mão/Dậu + Liêm Hóa Lộc → Tật Ách ắt có Thái Dương Hóa Kỵ → chủ bệnh ở mắt.
**💡 Nguyên lý**: Liêm Hóa Lộc kéo theo Thái Dương Hóa Kỵ (tứ hóa năm Giáp) → bệnh ở mắt vì Thái Dương chủ mắt.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q25 — p524
**❓ Câu hỏi**: 'Liêm Trinh, Phá Quân' Mão/Dậu gặp Kình Dương đồng độ (không có hình/hao) thì có đặc tính gì?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> “**Liêm Trinh, Phá Quân**” ở hai cung Mão hoặc Dậu, có năng lực sáng tạo, gặp **Kình Dương đồng độ**, không có các sao hình, hao, là chủ về suy nghĩ khéo, có tay nghề khéo.

**🇻🇳 Việt thuần (paraphrase)**: Liêm-Phá Mão/Dậu vốn có khả năng sáng tạo; thêm Kình Dương đồng cung mà không có hình/hao → suy nghĩ khéo, tay nghề khéo.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q26 — p524
**❓ Câu hỏi**: Người sinh năm Bính có 'Liêm Trinh, Phá Quân' Mão/Dậu thì hoạnh phát/hoạnh phá ở đâu?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> Đối với người sinh năm Bính, **“Liêm Trinh, Phá Quân”** ở hai cung Mão hoặc Dậu cũng chủ về hoạnh phát, hoạnh phá. Đến đại hạn **Thiên Phủ** thì hoạnh phát, để phòng đến cung hạn “**Thiên Đồng, Thái Âm**” thì hoạnh phá.

**🇻🇳 Việt thuần (paraphrase)**: Tuổi Bính + Liêm-Phá Mão/Dậu: vận Thiên Phủ phát bất ngờ; phòng vận Thiên Đồng-Thái Âm phá bất ngờ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q27 — p524
**❓ Câu hỏi**: Vận trình then chốt của 'Liêm Trinh, Phá Quân' Mão/Dậu là gì?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> Ngoài những điều thuật ở trên, đối với **“Liêm Trinh, Phá Quân”**, các cung hạn “**Vũ Khúc, Tham Lang**”, “**Thiên Đồng, Thái Âm**”, “**Thái Dương, Cự Môn**” là những niên hạn có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Liêm-Phá: vận then chốt = Vũ Khúc-Tham Lang, Thiên Đồng-Thái Âm, Thái Dương-Cự Môn.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q28 — p524
**❓ Câu hỏi**: 'Liêm Trinh, Thiên Phủ' ở Thìn/Tuất có khí thế nào, và Thiên Phủ là 'kho trống' hay 'kho lộ' thì sao?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> Khí rất hòa hoãn, gặp sao Lộc thì cát; **Thiên Phủ** là “kho trống”, “kho lộ” thì hung, nhưng nhẹ hơn các tổ hợp sao khác.

**📖 Hán-Việt giải**: Kho trống / kho lộ = thuật ngữ Tử Vi chỉ trạng thái Thiên Phủ (kho) khi không có Lộc giữ kho, hoặc bị Không Kiếp lộ kho.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Phủ Thìn/Tuất: khí dịu, gặp Lộc thì tốt. Thiên Phủ thành 'kho trống' hoặc 'kho lộ' thì hung — nhưng nhẹ hơn các tổ hợp khác.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q29 — p524
**❓ Câu hỏi**: 'Liêm Trinh, Thiên Phủ' Thìn/Tuất có bất lợi gì trong hôn nhân?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> Có điều, kết hôn sớm thì bất lợi, thường dễ bị tình trạng “ngó đứt mà tơ chưa lìa”, hoặc có một thời kì hữu danh vô thực.

**📖 Hán-Việt giải**: Ngó đứt mà tơ chưa lìa = chia tay rồi mà tình cảm vẫn chưa dứt; hữu danh vô thực = có danh mà không thực chất.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Phủ Thìn/Tuất bất lợi nếu cưới sớm: chia tay vẫn vương vấn, hoặc có lúc danh nghĩa vợ chồng mà không thực.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q30 — p524
**❓ Câu hỏi**: 'Liêm Trinh, Thiên Phủ' gặp sao Lộc + Phụ tá cát hợp với nghề gì?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> **“Liêm Trinh, Thiên Phủ”** gặp sao Lộc, lại có sao Phụ, tá cát, có thể làm việc trong giới kinh tế tài chính, hoặc là quan thuế. Gặp thêm **Tả Phụ, Hữu Bật** thì rất tốt.

**📖 Hán-Việt giải**: Phụ, tá = nhóm sao phụ trợ (Tả Phụ, Hữu Bật, Văn Xương, Văn Khúc, v.v.); quan thuế = công chức ngành thuế.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Phủ + sao Lộc + Phụ Tá cát: hợp ngành kinh tế tài chính hoặc quan thuế. Thêm Tả Phụ-Hữu Bật càng tốt.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q31 — p524
**❓ Câu hỏi**: 'Liêm Trinh, Thiên Phủ' được Thái Dương Thái Âm giáp cung thì cung nào ưu hơn?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> Nếu **“Liêm Trinh, Thiên Phủ”** được **Thái Dương** và **Thái Âm** giáp cung, thì ở cung Tuất ưu hơn ở cung Thìn. Nếu hội các sao cát là đại phú đại quý.

**📖 Hán-Việt giải**: Giáp cung = hai sao ở hai cung kề bên (trái-phải) kẹp lấy cung chính.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Phủ được Thái Dương-Thái Âm giáp: cung Tuất tốt hơn cung Thìn; hội cát tinh thì đại phú đại quý.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q32 — p524
**❓ Câu hỏi**: Vận trình then chốt của 'Liêm Trinh, Thiên Phủ' Thìn/Tuất là gì?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> Đối với **“Liêm Trinh, Thiên Phủ”**, các cung hạn **Phá Quân, Tham Lang**, “**Thái Dương, Thiên Lương**”, có **Văn Xương, Văn Khúc** là những đại vận hoặc lưu niên có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Liêm-Phủ: vận then chốt = Phá Quân, Tham Lang, Thái Dương-Thiên Lương, có Văn Xương-Văn Khúc.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.6-Q33 — p524
**❓ Câu hỏi**: 'Liêm Trinh, Tham Lang' đồng độ ở Tị/Hợi gặp sát kỵ thì sao?

**📜 Source quote (NGUYÊN VĂN, p524)**:
> **“Liêm Trinh, Tham Lang” đồng độ ở hai cung Tị hoặc Hợi:**
Gặp các sao sát, kỵ, chủ về phiêu lưu tứ hải, rời xa quê hương.

**📖 Hán-Việt giải**: Phiêu lưu tứ hải = lang bạt khắp bốn biển, sống không cố định.
**🇻🇳 Việt thuần (paraphrase)**: Liêm-Tham đồng cung Tị/Hợi + sát kỵ → lang bạt tứ phương, xa quê.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
## Section 5.1.7 — Thiên Phủ ở cung Mệnh (Thân) (21 atoms)

### [ ] tcq2-5.1.7-Q01 — p525
**❓ Câu hỏi**: Quan hệ giữa Thiên Phủ và Tử Vi trong cấu trúc tinh bàn như thế nào?

**📜 Source quote (NGUYÊN VĂN, p525)**:
> Thiên Phủ ưa tương hội Tử Vi ở tam phương, mà lại không ưa đồng độ, hễ đồng độ ắt sẽ có khuyết điểm. Cần xem xét các sao ở cung Phúc Đức, cung Sự Nghiệp và cung Phu Thê mà định tính chất.

**📖 Hán-Việt giải**: Tam phương = ba phương chiếu nhau (Tài-Quan-Thiên Di chiếu Mệnh); đồng độ = ở cùng một cung.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ ưa Tử Vi chiếu từ xa (tam phương) chứ không thích ở cùng cung; ở cùng cung thì có khuyết điểm. Khi luận phải xem thêm cung Phúc Đức, Sự Nghiệp và Phu Thê.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q02 — p525
**❓ Câu hỏi**: Thiên Phủ ở cung Mệnh gặp sao Lộc thì ý nghĩa gì?

**📜 Source quote (NGUYÊN VĂN, p525)**:
> **Thiên Phủ ở cung Mệnh, gặp sao Lộc:** Là điều kiện cơ bản để thu hoạch lợi ích; sau đó mới xem tính chất của Thiên Tướng để định cách cục cao thấp.

**📖 Hán-Việt giải**: Sao Lộc = chỉ Lộc Tồn hoặc Hóa Lộc; cách cục = mô hình bố trí sao.
**🇻🇳 Việt thuần (paraphrase)**: Có sao Lộc với Thiên Phủ chỉ là nền tảng có lợi; muốn biết cao thấp thì phải xem thêm Thiên Tướng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q03 — p525
**❓ Câu hỏi**: Thiên Phủ đến cung hạn nào là tốt?

**📜 Source quote (NGUYÊN VĂN, p525)**:
> **Thiên Phủ ưa đến các cung hạn Thiên Lương, Thái Dương:** Nếu có các sao cát, sẽ chủ về địa vị thăng tiến. Ưa đến cung hạn có Lộc Tồn, Hóa Lộc, hội hợp sao cát, chủ về tài phú tăng nhiều.

**📖 Hán-Việt giải**: Cung hạn = cung mà Đại Vận hoặc Lưu Niên đi tới.
**🇻🇳 Việt thuần (paraphrase)**: Khi vận đi qua cung có Thiên Lương hoặc Thái Dương kèm sao cát thì Thiên Phủ chủ thăng tiến địa vị; nếu đi qua cung có Lộc Tồn hoặc Hóa Lộc kèm sao cát thì chủ tài phú tăng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q04 — p525
**❓ Câu hỏi**: Cách Tài ấm giáp ấn của Thiên Phủ - Thiên Tướng nghĩa là gì?

**📜 Source quote (NGUYÊN VĂN, p525)**:
> **Thiên Phủ hội Thiên Tướng là “Tài ấm giáp ấn”**: Thì Thiên Phủ cũng chủ về phú quý, sự nghiệp không từ tay trắng làm nên.

**📖 Hán-Việt giải**: Tài ấm giáp ấn = sao Tài và sao Ấm giáp hai bên sao Ấn (Thiên Tướng).
**🇻🇳 Việt thuần (paraphrase)**: Khi Thiên Tướng được cách Tài ấm giáp ấn và hội với Thiên Phủ thì Thiên Phủ chủ phú quý, có sẵn nền tảng (không phải tay trắng dựng nghiệp).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q05 — p525
**❓ Câu hỏi**: Cách Hình kị giáp ấn của Thiên Phủ - Thiên Tướng thì sao?

**📜 Source quote (NGUYÊN VĂN, p525)**:
> Nếu là **“Hình kị giáp ấn”**: Sẽ chủ về bị cô lập, không có cứu viện, tinh thần bị áp lực, vật chất thì bị tranh đoạt.

**📖 Hán-Việt giải**: Hình kị giáp ấn = sao Hình và sao Kị giáp hai bên sao Ấn (Thiên Tướng).
**🇻🇳 Việt thuần (paraphrase)**: Nếu Thiên Tướng bị Hình kị giáp ấn thì Thiên Phủ chủ bị cô lập, không người trợ giúp, áp lực tinh thần, của cải bị giành giật.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q06 — p525
**❓ Câu hỏi**: Tại sao luận Thiên Phủ phải xem Thiên Tướng (phùng Phủ khán Tướng)?

**📜 Source quote (NGUYÊN VĂN, p525)**:
> Đối cung của Thiên Phủ ắt là Thất Sát, đây là một cách bố trí các sao rất xảo diệu. Thiên Phủ chỉ sở trường phòng thủ, không giỏi... Khai sảng, cũng không giỏi chỉ huy. Năng lực khai sáng và quyền lực có vận dụng được tự nhiên hay không, cần phải xem các sao hội hợp cung **Thất Sát** mà định. Cho nên gọi là “phùng Phủ khán Tướng” (gặp Thiên Phủ thì phải xem Thiên Tướng), thực ra cũng là “phùng Tướng khán Phủ” (gặp Thiên Tướng thì phải xem Thiên Phủ).

**📖 Hán-Việt giải**: Đối cung = cung đối diện (xung chiếu); phùng Phủ khán Tướng = gặp Phủ phải xem Tướng; sở trường = thế mạnh.
**🇻🇳 Việt thuần (paraphrase)**: Cung đối diện Thiên Phủ luôn là Thất Sát. Thiên Phủ chỉ giỏi giữ, không giỏi mở mang cũng không giỏi chỉ huy. Muốn biết Thiên Phủ phát huy được không phải xem các sao hội ở cung Thất Sát. Vì vậy có câu phùng Phủ khán Tướng, và ngược lại.
**💡 Nguyên lý**: Thiên Phủ thiên về phòng thủ — cần kiểm tra cung Thất Sát (đối cung) và Thiên Tướng (hợp xung) để biết khả năng khai sáng và quyền lực.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q07 — p526
**❓ Câu hỏi**: Thiên Phủ bị coi là kho trống khi nào?

**📜 Source quote (NGUYÊN VĂN, p526)**:
> **Thiên Phủ** không có sao Lộc, là “kho trống”, hội **Địa Không**, **Địa Kiếp**, cũng là “kho trống”. Hề kho trống mà **Thất Sát** ở đối cung, hội hợp các sao cát, mới chủ về tạo dựng sự nghiệp từ “hư không”.

**📖 Hán-Việt giải**: Kho trống = kho không có của; hội = gặp ở tam phương tứ chính.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ không sao Lộc, hoặc bị Địa Không Địa Kiếp hội, gọi là kho trống. Kho trống mà Thất Sát đối cung có sao cát thì chủ tạo dựng sự nghiệp từ tay trắng (từ hư không).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q08 — p526
**❓ Câu hỏi**: Thiên Phủ là kho lộ khi nào và cần điều kiện gì để giàu?

**📜 Source quote (NGUYÊN VĂN, p526)**:
> **Thiên Phủ** có Tứ Sát Tinh hội hợp, đây là “kho lộ”. Hễ kho lộ thì **Thiên Tướng** cần phải có sao Lộc, hoặc thành cách “Tài ấm giáp ấn”, mới chủ về giỏi cạnh tranh, và nhờ đó mà giàu có.

**📖 Hán-Việt giải**: Tứ Sát Tinh = bốn sát tinh (Kình Dương, Đà La, Hỏa Tinh, Linh Tinh); kho lộ = kho bị lộ ra.
**🇻🇳 Việt thuần (paraphrase)**: Khi Thiên Phủ bị Tứ Sát hội thì như kho bị lộ. Lúc này phải có Thiên Tướng kèm sao Lộc hoặc thành Tài ấm giáp ấn thì mới giỏi cạnh tranh và giàu được.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q09 — p526
**❓ Câu hỏi**: Liêm Trinh - Thiên Phủ ở cung Tuất luận thế nào?

**📜 Source quote (NGUYÊN VĂN, p526)**:
> **Thiên Phủ** có các sao khác đồng độ: trường hợp “**Liêm Trinh**, **Thiên Phủ**” đồng độ ở cung Tuất là tốt nhất. Cổ nhân nói “Thiên Phủ đến cung Tuất có sao phù trợ, là đai vàng áo tía”. Trường hợp **Liêm Trinh Hóa Lộc**, hoặc hội **Vũ Khúc Hóa Lộc** là thượng cách; hội **Tử Vi Hóa Khoa** là quý mà không phú; còn ưa **Tả Phụ**, **Hữu Bật** đến hội; **Thiên Khôi**, **Thiên Việt** giáp cung, sẽ chủ về địa vị rất cao.

**📖 Hán-Việt giải**: Đai vàng áo tía = biểu tượng đại quan; thượng cách = cách cao nhất; giáp cung = kẹp hai bên cung.
**🇻🇳 Việt thuần (paraphrase)**: Liêm Trinh + Thiên Phủ đứng cung Tuất là tốt nhất. Cổ nhân ví là làm quan to. Nếu Liêm Trinh Hóa Lộc hoặc hội Vũ Khúc Hóa Lộc là cách cao nhất; nếu hội Tử Vi Hóa Khoa thì có địa vị nhưng không giàu; thêm Tả Phụ Hữu Bật thì quý; Thiên Khôi Thiên Việt giáp cung thì địa vị rất cao.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q10 — p526
**❓ Câu hỏi**: Tử Vi - Thiên Phủ đồng độ thì luận chủ phụ thế nào?

**📜 Source quote (NGUYÊN VĂN, p526)**:
> Nếu “**Tử Vi**, **Thiên Phủ**” đồng độ, thì **Tử Vi** là chủ, **Thiên Phủ** là phụ. Cho nên cũng ưa **Tả Phụ**, **Hữu Bật**, **Thiên Khôi**, **Thiên Việt** hội hợp. Không có sao phụ, tá, thì tính hệ này có những khiếm khuyết đáng tiếc, chủ về tiến thoái thiếu quyết đoán; nếu có Lộc Tồn đồng độ, thì **Thiên Phủ** sẽ thành vai chủ, luận đoán cát hung cũng nặng về tính chất của **Thiên Phủ**.

**📖 Hán-Việt giải**: Sao phụ, tá = các sao phụ trợ (Tả Phụ Hữu Bật là phụ; Thiên Khôi Thiên Việt là tá).
**🇻🇳 Việt thuần (paraphrase)**: Tử Vi + Thiên Phủ đồng cung thì Tử Vi đóng vai chính, Thiên Phủ phụ. Cần Tả Phụ Hữu Bật Thiên Khôi Thiên Việt hội. Thiếu sao phụ tá thì tinh hệ này hay do dự. Có Lộc Tồn đồng độ thì Thiên Phủ thành vai chính, luận cát hung phải nặng theo Thiên Phủ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q11 — p526
**❓ Câu hỏi**: Vũ Khúc - Thiên Phủ ở Tý hoặc Ngọ luận về tài chính thế nào?

**📜 Source quote (NGUYÊN VĂN, p526)**:
> “**Vũ Khúc**, **Thiên Phủ**” đồng độ hai cung Tý hoặc Ngọ, gặp Lộc Tồn ở cung Tài Bạch tốt hơn ở cung Mệnh; gặp **Vũ Khúc Hóa Lộc**, thì gặp ở cung Mệnh tốt hơn. Trường hợp trước, gặp ở cung Mệnh thì chủ về bủn xỉn, keo kiệt, tham lam; gặp ở cung Tài Bạch thì chủ về giỏi quản lí tài chính, giỏi kiếm tiền. Trường hợp sau, gặp ở cung Mệnh thì chủ về độ lượng, còn có năng lực quyết đoán và quản lí tài chính.

**📖 Hán-Việt giải**: Lộc Tồn = sao Lộc cố định theo can năm; Hóa Lộc = một trong Tứ Hóa.
**🇻🇳 Việt thuần (paraphrase)**: Vũ Khúc + Thiên Phủ ở Tý hay Ngọ: Lộc Tồn nên ở cung Tài Bạch hơn ở Mệnh (Lộc Tồn ở Mệnh khiến keo kiệt). Còn Vũ Khúc Hóa Lộc thì lại nên ở Mệnh (chủ độ lượng, biết quyết đoán quản tiền).
**💡 Nguyên lý**: Cùng là Lộc nhưng tính chất khác nhau: Lộc Tồn cố hữu mang tính giữ — đặt ở Mệnh thì sinh keo kiệt; Hóa Lộc động — đặt ở Mệnh thì sinh độ lượng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q12 — p526
**❓ Câu hỏi**: Thiên Phủ độc tọa ở Sửu hoặc Mùi được giáp cung bởi Văn Xương Văn Khúc hoặc Tả Phụ Hữu Bật thì khác nhau thế nào?

**📜 Source quote (NGUYÊN VĂN, p526)**:
> **Thiên Phủ** độc tọa ở hai cung Sửu hoặc Mùi, có **Văn Xương**, **Văn Khúc** giáp cung thì lợi về cẩu danh, tiền của thì xem địa vị xã hội mà định; được **Tả Phụ**, **Hữu Bật** giáp cung thì lợi về tiền của, địa vị xã hội thì xem tiền của nhiều ít mà định. Do đó có thể định mục tiêu nỗ lực của **Thiên Phủ**.

**📖 Hán-Việt giải**: Giáp cung = sao ở hai cung bên cạnh kẹp Thiên Phủ; cầu danh = theo đường danh tiếng.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ đứng một mình ở Sửu hay Mùi: nếu Văn Xương Văn Khúc kẹp hai bên thì hợp đi đường danh, tiền bạc tùy địa vị; nếu Tả Phụ Hữu Bật kẹp hai bên thì hợp đi đường tiền, địa vị tùy tiền nhiều ít. Từ đó xác định mục tiêu phấn đấu.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q13 — p527
**❓ Câu hỏi**: Vì sao Thiên Phủ độc tọa ở cung Mùi tốt hơn ở cung Sửu?

**📜 Source quote (NGUYÊN VĂN, p527)**:
> Thiên Phủ độc tọa ở hai cung Sửu hoặc Mùi, trường hợp ở cung Mùi tốt hơn; vì ở cung Sửu sẽ hội **Thiên Tướng** ở cung Tỵ, mà **Thiên Lương** ở cung Ngọ giáp **Thiên Tướng**, khí “Hình Sát” khá nặng, gián tiếp gây ảnh hưởng khiến Thiên Phủ bị áp lực khá nặng.

**📖 Hán-Việt giải**: Hình Sát = khí của Hình tinh và Sát tinh; giáp = kẹp hai bên.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ ở Sửu hoặc Mùi: Mùi tốt hơn. Vì khi ở Sửu, Thiên Tướng (cung Tỵ) bị Thiên Lương (cung Ngọ) giáp, khí Hình Sát nặng, gián tiếp đè áp lực lên Thiên Phủ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q14 — p527
**❓ Câu hỏi**: Các cung hạn then chốt của Thiên Phủ độc tọa ở Sửu hoặc Mùi là gì?

**📜 Source quote (NGUYÊN VĂN, p527)**:
> Đối với Thiên Phủ độc tọa ở hai cung Sửu hoặc Mùi, các cung hạn “Tử Vi, Tham Lang”, **Thiên Lương**, “Liêm Trinh, Thất Sát”, “Vũ Khúc, Phá Quân”, có Lộc Tồn và Hóa Lộc là những lưu niên, đại vận có tính then chốt.

**📖 Hán-Việt giải**: Lưu niên = năm trôi qua (Lưu Niên); đại vận = vận lớn 10 năm.
**🇻🇳 Việt thuần (paraphrase)**: Với Thiên Phủ độc tọa Sửu Mùi, các vận đi qua cung có Tử Vi Tham Lang, Thiên Lương, Liêm Trinh Thất Sát, Vũ Khúc Phá Quân, có Lộc Tồn hoặc Hóa Lộc là những vận then chốt.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q15 — p527
**❓ Câu hỏi**: Thiên Phủ độc tọa ở Mão hoặc Dậu có đặc trưng gì?

**📜 Source quote (NGUYÊN VĂN, p527)**:
> Thiên Phủ độc tọa ở hai cung Mão hoặc Dậu, là ở nhược địa, nếu có hai sao **Địa Không**, **Địa Kiếp**, một sao bay đến cung Mệnh, một sao bay đến cung Sự Nghiệp, thì Thiên Phủ là “Kho Lộ”, “Kho Trống”, lại gặp thêm sát tinh, chủ về cơ mưu cỡ nào thì cũng chẳng được gì.

**📖 Hán-Việt giải**: Nhược địa = vị trí yếu; Kho Lộ + Kho Trống = vừa bị lộ vừa rỗng.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ một mình ở Mão hoặc Dậu là vị trí yếu. Nếu Địa Không Địa Kiếp chia nhau vào cung Mệnh và cung Sự Nghiệp thì Thiên Phủ vừa lộ vừa rỗng, lại có sát tinh thì mưu mẹo gì cũng vô ích.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q16 — p527
**❓ Câu hỏi**: Thiên Phủ độc tọa ở Mão hoặc Dậu sợ điều gì khi đi đại vận?

**📜 Source quote (NGUYÊN VĂN, p527)**:
> Thiên Phủ độc tọa ở hai cung Mão hoặc Dậu, ưa **Tả Phụ** đồng cung, hội **Hữu Bật**, sẽ chủ về có địa vị rất cao, hoặc có sự nghiệp hiện có đang phát triển. Có điều rất sợ đến niên hạn **Thái Dương Hóa Kỵ**, bị “Hình Kị Giáp Ấn” là điểm tượng đổ vỡ, gặp trắc trở nghiêm trọng.

**📖 Hán-Việt giải**: Niên hạn = năm hạn (lưu niên); Hóa Kỵ = một trong Tứ Hóa, chủ trở ngại.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ ở Mão Dậu thích Tả Phụ ngồi cùng và Hữu Bật chiếu, chủ địa vị cao hoặc sự nghiệp tăng tiến. Nhưng rất sợ vận năm có Thái Dương Hóa Kỵ tạo Hình Kị Giáp Ấn — là dấu hiệu đổ vỡ, gặp trở ngại nặng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q17 — p527
**❓ Câu hỏi**: Các cung hạn then chốt của Thiên Phủ độc tọa ở Mão hoặc Dậu?

**📜 Source quote (NGUYÊN VĂN, p527)**:
> Đối với Thiên Phủ độc tọa ở hai cung Mão hoặc Dậu, ngoài trừ những điều thuật ở trên ra, các cung hạn “Tử Vi, Phá Quân”, “Liêm Trinh, Tham Lang” là những đại vận hoặc lưu niên có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Với Thiên Phủ một mình ở Mão hoặc Dậu, ngoài các điểm trên, các vận đi qua cung Tử Vi - Phá Quân hoặc Liêm Trinh - Tham Lang là then chốt.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q18 — p527
**❓ Câu hỏi**: Thiên Phủ độc tọa ở Tị hoặc Hợi có đặc trưng gì đối với nữ mệnh?

**📜 Source quote (NGUYÊN VĂN, p527)**:
> Thiên Phủ độc tọa ở hai cung Tị hoặc Hợi, đối cung là “Tử Vi, Thất Sát”, là tinh hệ quyển lực. Cho nên chủ về nữ mệnh thao túng chồng, ở thời hiện đại, còn chủ về phụ nữ có sự nghiệp riêng.

**📖 Hán-Việt giải**: Tinh hệ quyền lực = nhóm sao mang khí quyền lực.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ một mình ở Tị hoặc Hợi: đối cung là Tử Vi - Thất Sát, mang khí quyền lực. Với nữ mệnh chủ thao túng chồng; thời nay còn chỉ phụ nữ có sự nghiệp riêng.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q19 — p527
**❓ Câu hỏi**: Vì sao Thiên Phủ ở Tị hoặc Hợi không cần các sao phụ tá, mà ưa Lộc Tồn và Tài Ấm Giáp Ấn?

**📜 Source quote (NGUYÊN VĂN, p527)**:
> Thiên Phủ độc tọa ở hai cung Tị hoặc Hợi gặp các sao phụ, tá, bất quá chỉ làm tăng trợ lực, nhưng vì đối nhau với “Tử Vi, Thất Sát”, nên chẳng cần thiết. Không bằng gặp Lộc Tồn và **Thiên Tướng** thuộc loại “Tài Ấm Giáp Ấn”, hoặc hội **Vũ Khúc Hóa Lộc** (mượn sao an cung) và **Tham Lang Hóa Lộc** là tốt, có thể phú quý song toàn.

**📖 Hán-Việt giải**: Mượn sao an cung = khi cung không có sao chính, mượn từ cung đối; phú quý song toàn = vừa giàu vừa sang.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ một mình ở Tị Hợi: thêm sao phụ tá chỉ thêm trợ lực mà thôi (vì đã đối Tử Vi - Thất Sát rồi nên không cần). Quan trọng hơn là có Lộc Tồn cùng Thiên Tướng thuộc Tài Ấm Giáp Ấn, hoặc hội Vũ Khúc Hóa Lộc (mượn từ cung khác) và Tham Lang Hóa Lộc — vừa giàu vừa sang.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q20 — p527
**❓ Câu hỏi**: Thiên Phủ Tị hoặc Hợi thành Tài Ấm Giáp Ấn thì thời hiện đại biểu thị điều gì?

**📜 Source quote (NGUYÊN VĂN, p527)**:
> Thiên Phủ độc tọa ở hai cung Tị hoặc Hợi, nếu **Thiên Tướng** được “Tài Ấm Giáp Ấn”, ở thời hiện đại phần nhiều chủ về được người ngoại quốc (hay người ở phương xa) giúp đỡ. Nếu không, cần phải gặp **Thiên Khôi**, **Thiên Việt** mới chủ về được quý nhân để giúp đỡ.

**📖 Hán-Việt giải**: Quý nhân = người giúp đỡ; người phương xa / ngoại quốc = bối cảnh hiện đại.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ một mình ở Tị Hợi, nếu Thiên Tướng được Tài Ấm Giáp Ấn thì thời nay thường được người nước ngoài hoặc người ở xa giúp đỡ. Không được vậy thì phải có Thiên Khôi Thiên Việt mới chủ có quý nhân.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.7-Q21 — p527
**❓ Câu hỏi**: Thiên Phủ Tị hoặc Hợi rất ưa cung hạn nào và biểu nghĩa gì?

**📜 Source quote (NGUYÊN VĂN, p527)**:
> Thiên Phủ độc tọa ở hai cung Tị hoặc Hợi rất ưa đến cung hạn “Thiên Khôi, Thiên Việt trùng điệp” (tức Lưu Khôi và Lưu Việt trùng điệp với Thiên Khôi, Thiên Việt của nguyên cục, xung khởi nhau, chủ về phát đột ngột.)

**📖 Hán-Việt giải**: Trùng điệp = chồng lên nhau; Lưu Khôi/Lưu Việt = Thiên Khôi/Thiên Việt theo lưu niên; nguyên cục = lá số gốc.
**🇻🇳 Việt thuần (paraphrase)**: Thiên Phủ một mình ở Tị Hợi rất hợp khi vận đi qua cung mà Lưu Khôi Lưu Việt chồng lên Thiên Khôi Thiên Việt gốc, xung khởi nhau, chủ phát đột ngột.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
## Section 5.1.8 — **Thái Âm** ở cung Mệnh (thân) (32 atoms)

### [ ] tcq2-5.1.8-Q01 — p528
**❓ Câu hỏi**: Thái Âm ở cung Mệnh nên ở trạng thái nào, và hợp với người sinh giờ nào?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Thái Âm nên nhập miếu, không nên lạc hãm, nên là người sinh vào ban đêm, không nên là người sinh vào ban ngày.

**📖 Hán-Việt giải**: Nhập miếu = sao vào cung sáng tỏ nhất; lạc hãm = sao rơi vào cung yếu/tối.
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm là mặt trăng, sáng nhất khi vào miếu địa và hợp với người sinh ban đêm. Lạc hãm hoặc sinh ban ngày đều không tốt.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q02 — p528
**❓ Câu hỏi**: Người sinh ban đêm gặp Thái Âm nhập miếu thì sao?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Nếu người sinh vào ban đêm gặp Thái Âm nhập miếu thì rất tốt; người sinh vào ban ngày thì giảm phúc.

**🇻🇳 Việt thuần (paraphrase)**: Người sinh ban đêm hợp Thái Âm miếu là rất tốt; sinh ban ngày thì phúc khí giảm đi.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q03 — p528
**❓ Câu hỏi**: Người sinh ban đêm gặp Thái Âm lạc hãm có chắc chắn hung không?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Nếu người sinh vào ban đêm gặp Thái Âm lạc hãm, chưa chắc đã hung, vẫn cần phải xem xét các sao phụ, tá, sát, hóa mà định

**📖 Hán-Việt giải**: Phụ tá = sao trợ lực; sát = sao xấu; hóa = Tứ Hóa (Lộc/Quyền/Khoa/Kỵ).
**🇻🇳 Việt thuần (paraphrase)**: Sinh ban đêm gặp Thái Âm lạc hãm không nhất định xấu — phải xét thêm các sao bổ trợ, sát, hóa quanh đó.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q04 — p528
**❓ Câu hỏi**: Người sinh ban ngày gặp Thái Âm lạc hãm thì ứng nghiệm gì?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> nếu người sinh vào ban ngày gặp Thái Âm lạc hãm, ắt sẽ bất lợi đối với người thân phái nữ. Nữ mệnh cũng bất lợi đối với bản thân, hoặc sớm mổ cồi.

**📖 Hán-Việt giải**: Mổ côi = mồ côi (mất mẹ sớm).
**🇻🇳 Việt thuần (paraphrase)**: Sinh ban ngày gặp Thái Âm lạc hãm sẽ bất lợi cho người nữ thân thuộc (mẹ, chị, em gái); nữ mệnh thì hại chính mình hoặc mồ côi mẹ sớm.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q05 — p528
**❓ Câu hỏi**: Mệnh vô chính diệu, Thân ở Thiên Di là Thái Âm lạc hãm gặp sát tinh ứng nghiệm gì?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Cung Mệnh vô chính diệu, cung Thân ở cung Thiên Di là Thái Âm lạc hãm, gặp sát tinh (sợ nhất là Hỏa Tình, Linh Tinh), người sinh vào ban ngày chủ về theo mẹ cải giá, hoặc làm con thừa tự của bác hay chú.

**📖 Hán-Việt giải**: Vô chính diệu = không có chính tinh; cải giá = mẹ tái hôn; thừa tự = nối dõi cho người khác.
**🇻🇳 Việt thuần (paraphrase)**: Mệnh không chính tinh, Thân ở Thiên Di gặp Thái Âm hãm + sát tinh (sợ nhất Hỏa Linh) + sinh ban ngày → theo mẹ cải giá hoặc làm con nối dõi cho chú/bác.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q06 — p528
**❓ Câu hỏi**: Thái Âm thủ Mệnh chia thành hai nhóm theo ngày sinh thượng huyển/hạ huyển thế nào?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Thái Âm thủ Mệnh, lại còn chia ra hai nhóm, nhóm người sinh vào thượng huyển (ngày 1 đến 15) và người sinh vào hạ huyển (ngày 16 đến 30). Sinh vào thượng huyển thì cát, đây là thời kỳ trăng tròn dần; sinh vào hạ huyển thì không cát tường, đây là thời kỳ trăng khuyết dần.

**📖 Hán-Việt giải**: Thượng huyển = nửa đầu tháng âm (trăng đang tròn dần); hạ huyển = nửa sau tháng (trăng đang khuyết dần).
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm thủ Mệnh chia hai: sinh 1–15 là tốt (trăng lên), sinh 16–30 không tốt (trăng xuống).

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q07 — p528
**❓ Câu hỏi**: Người sinh vào hạ huyển ứng với câu nào ở trên?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Người sinh vào hạ huyển càng đúng với ứng nghiệm "theo mẹ cải giá" thuật ở trên.

**🇻🇳 Việt thuần (paraphrase)**: Người sinh nửa cuối tháng âm càng dễ ứng vào cảnh theo mẹ tái hôn đã nói trước.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q08 — p528
**❓ Câu hỏi**: Thái Âm nhập miếu gặp sao cát tam phương hội chiếu chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Thái Âm nhập miếu, gặp sao cát ở tam phương đến hội, chủ về hưởng thụ, nhất là hưởng thụ tinh thần. Tức không mang toàn bộ tình thần tập trung vào việc kiếm tiền và theo đuổi sinh hoạt vật chất.

**📖 Hán-Việt giải**: Tam phương = ba phương hội chiếu (tài, quan, đối).
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm miếu được sao tốt từ tam phương chiếu vào thì hưởng thụ, đặc biệt là hưởng thụ tinh thần — không chỉ chạy theo tiền bạc và vật chất.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q09 — p528
**❓ Câu hỏi**: Thái Âm nhập miếu kết hợp với các sao Văn Xương/Văn Khúc, Thiên Đồng, Thiên Cơ, Thái Dương ra sao?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Còn gặp Văn Xương, Văn Khúc thì thiên về văn chương; gặp Thiên Đồng thì ưa thích âm nhạc, dù gặp Thiên Cơ cũng chủ về có hứng thú nhiều lĩnh vực, lấy đó để tiêu khiển. Chỉ đồng độ với Thái Dương là thiểu sinh hoạt tinh thần.

**🇻🇳 Việt thuần (paraphrase)**: Thái Âm cộng Xương Khúc → văn chương; cộng Thiên Đồng → âm nhạc; cộng Thiên Cơ → đa sở thích tiêu khiển; nhưng đồng cung Thái Dương lại thiếu đời sống tinh thần.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q10 — p528
**❓ Câu hỏi**: Luận đoán Thái Âm thủ Mệnh phải xem kèm cung nào và sao gì?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Hễ Thái Âm ở cung Mệnh, lúc luận đoán cần phải xem kèm cung Phúc Đức, mà cung Phúc Đức ắt sẽ là Cự Môn tọa thủ, cát hung, của nó có thể ảnh hưởng đến Thái Âm của cung Mệnh, nhất là về phương diện hưởng thụ tinh thần.

**🇻🇳 Việt thuần (paraphrase)**: Khi Thái Âm thủ Mệnh, luôn phải nhìn cung Phúc Đức — nơi đó có Cự Môn. Cự Môn tốt xấu ảnh hưởng trực tiếp đến hưởng thụ tinh thần của Mệnh.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q11 — p528
**❓ Câu hỏi**: Thái Âm chủ về gì và ưa gặp sao nào?

**📜 Source quote (NGUYÊN VĂN, p528)**:
> Thái Âm chủ về phú, nên ưa có Lộc Tồn hoặc Hóa Lộc đồng độ hoặc vây chiếu; trường hợp... hoặc Hóa Lộc ở cung tam hợp là kế đó.

**📖 Hán-Việt giải**: Đồng độ = ở cùng cung; vây chiếu = giáp hai bên; tam hợp = ba cung cùng tam hợp chiếu lên.
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm chủ giàu, nên rất thích Lộc Tồn hay Hóa Lộc cùng cung hoặc kẹp hai bên; nếu Hóa Lộc nằm ở cung tam hợp thì là phương án tốt thứ hai.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q12 — p529
**❓ Câu hỏi**: Thái Âm gặp Hóa Quyền, Hóa Khoa mà không gặp sao lộc chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> Gặp Hóa Quyền, Hóa Khoa mà không gặp sao lộc, sẽ chủ về tài lộc do địa vị xã hội và học lực quyết định. Cho nên cẩn phải cực lực tranh thủ tiến bộ; gặp Văn Xương, Văn Khúc là chủ về thông minh; gặp Tả Phụ, Hữu Bật mới có thể làm tăng địa vị.

**🇻🇳 Việt thuần (paraphrase)**: Thái Âm có Quyền/Khoa mà thiếu Lộc thì tiền tài đến từ địa vị và học vấn — phải nỗ lực phấn đấu. Xương Khúc cho thông minh; Tả Hữu mới nâng được địa vị.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q13 — p529
**❓ Câu hỏi**: Bản tính Thái Âm là gì, và khi hướng nội thái quá thì hậu quả ra sao?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> Thái Âm có bản tính hướng nội, nhưng nếu hướng nội thái quá sẽ chủ về tiêu trầm.

**📖 Hán-Việt giải**: Tiêu trầm = chán nản, trầm uất.
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm vốn hướng nội; nếu hướng nội quá mức sẽ thành trầm uất, suy sụp tinh thần.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q14 — p529
**❓ Câu hỏi**: Thái Âm không ưa gặp những sao nào, và hậu quả khi tụ tập sao hình hao là gì?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> Nó không ưa các sao Đà La, Linh Tỉnh, Hóa Kỵ, Âm Sát, Địa Không, Địa Kiếp, Thiên Hình. Nếu có các sao hình, hao tụ tập, sẽ chủ về chứng tự kỷ, thiểu năng trí tuệ, hoặc có tâm lý mặc cảm; nhất là ở bốn cung Dần, Thân, Mão, Dậu thì càng đúng.

**📖 Hán-Việt giải**: Hình hao = sao gây thương tổn, mất mát.
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm ngại Đà La, Linh Tinh, Hóa Kỵ, Âm Sát, Không Kiếp, Thiên Hình. Khi nhiều sao hình hao tụ → tự kỷ, kém trí, mặc cảm — đặc biệt ở Dần Thân Mão Dậu.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q15 — p529
**❓ Câu hỏi**: Cách cục 'Nhật Tị Nguyệt Dậu, an mệnh Sửu' chủ về gì?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> "Thái Dương ở cung Tị, Thái Âm ở cung Dậu, an mệnh ở cung Sửu là chủ về phú, bước lên cung Hằng" (Nhật Tị Nguyệt Dậu, an mệnh Sửu phú, bộ thiêm cung).

**📖 Hán-Việt giải**: Bộ thiềm cung = bước lên cung trăng (đậu đạt cao).
**🇻🇳 Việt thuần (paraphrase)**: Cổ quyết: Thái Dương ở Tị, Thái Âm ở Dậu, an Mệnh ở Sửu → giàu, lên chức cao.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q16 — p529
**❓ Câu hỏi**: Cách cục 'Nhật Mão Nguyệt Hợi, an mệnh Mùi' chủ về gì?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> "Thái Dương ở cung Mão, Thái Âm ở cung Hợi, an mệnh ở cung Mùi, phần nhiều đỗ đạt" (Nhật Mão Nguyệt Hợi, an mệnh Mùi cung, đa chiết quê).

**📖 Hán-Việt giải**: Đa chiết quế = nhiều lần bẻ cành quế (thi đỗ).
**🇻🇳 Việt thuần (paraphrase)**: Cổ quyết: Thái Dương Mão + Thái Âm Hợi + an Mệnh Mùi → đa số đỗ đạt khoa cử.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q17 — p529
**❓ Câu hỏi**: Hai cổ quyết trên thuộc trường hợp Nhật Nguyệt thế nào và còn cách 'Nhật Nguyệt đồng Mùi an mệnh Sửu' chủ gì?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> Đây là trường hợp Thái Dương, Thái Âm miếu vượng, hội chiếu cùng mệnh. Còn nói: "Thái Dương, Thái Âm cùng ở cung Mùi, an mệnh ở cung Sửu, là tài đến bậc hẩu bá" (Nhật Nguyệt đồng Mùi, an mệnh Sửu, hấu bá chỉ tài).

**📖 Hán-Việt giải**: Hầu bá = tước vương hầu cao quý.
**🇻🇳 Việt thuần (paraphrase)**: Hai cổ quyết trên đều là Nhật–Nguyệt miếu vượng chiếu Mệnh. Thêm: Nhật Nguyệt đồng cung Mùi + Mệnh tại Sửu → tài năng tới mức hầu bá.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q18 — p529
**❓ Câu hỏi**: So sánh Nhật Nguyệt hội chiếu và Nhật Nguyệt đồng cung thì ai tốt hơn?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> Hễ Thái Dương, Thái Âm hội chiếu, trong các tình hình thông thường thì tốt hơn Thái Dương, Thái Âm đồng cung. Vì tính chất của Thái Dương, Thái Âm đồng cung không hợp nhau, dễ sinh khuyết điểm.

**🇻🇳 Việt thuần (paraphrase)**: Thông thường Nhật Nguyệt hội chiếu tốt hơn đồng cung — vì hai sao đồng cung tính chất xung khắc nhau, dễ phát sinh thiếu sót.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q19 — p529
**❓ Câu hỏi**: Cung Mệnh được Thái Dương Thái Âm giáp cung ứng nghiệm gì?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> Cung mệnh được Thái Dương, Thái Âm giáp, nếu Thái Dương và Thái Âm miếu vượng thì cũng chủ về phú quý. Giáp Thiên Phủ Hóa Khoa, hoặc Thiên Phủ đối nhau với Liêm Trinh Hóa Lộc là cát lợi; giáp Vũ Khúc, Tham Lang Hóa Lộc là kế đó.

**📖 Hán-Việt giải**: Giáp = hai sao kẹp hai bên cung Mệnh.
**🇻🇳 Việt thuần (paraphrase)**: Mệnh bị Nhật Nguyệt kẹp + cả hai miếu vượng → phú quý. Bên trong là Thiên Phủ Hóa Khoa hoặc Thiên Phủ đối Liêm Trinh Hóa Lộc thì rất tốt; nếu là Vũ Khúc, Tham Lang Hóa Lộc thì tốt thứ hai.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q20 — p529
**❓ Câu hỏi**: Trường hợp Thái Dương ở Hợi, Thái Âm ở Mão có phải cách 'phản bối' không? Cách 'phản bối' thật là gì?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> Thái Dương ở cung Hợi, Thái Âm ở cung Mão, không phải là cách cục "phản bồi", các sách thường lầm. "Phản bối" là Thái Dương ở Tuất, Thái Âm ở cung Thìn.

**📖 Hán-Việt giải**: Phản bối = quay lưng (cách cục tên gọi).
**🇻🇳 Việt thuần (paraphrase)**: Nhật Hợi Nguyệt Mão KHÔNG phải cách Phản Bối — đây là chỗ nhiều sách nhầm. Phản Bối đúng là Nhật Tuất Nguyệt Thìn.
**⚠ Iron Rule warning**: Sách khác thường chép sai — phải nhớ chuẩn: Phản Bối = Nhật Tuất, Nguyệt Thìn.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q21 — p529
**❓ Câu hỏi**: Cách cục 'Phản Bối' chủ về điều gì?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> Cách cục "phản bối" chủ về rời xa quê hương, hay làm con nuôi người khác, nếu có Hỏa Tinh, Linh Tinh đồng cung, thì còn bé đã rời xa cha mẹ, sát tinh nặng chủ về bị bỏ rơi. Nếu lại gặp các sao phụ tá cát, thì rời xa quê hương mà phát phúc.

**🇻🇳 Việt thuần (paraphrase)**: Cách Phản Bối: rời quê / con nuôi. Cộng Hỏa Linh → bé đã xa cha mẹ; sát nặng → bị bỏ rơi; có phụ tá cát → đi xa lập nghiệp phát phúc.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q22 — p529
**❓ Câu hỏi**: Thái Âm gặp Kình Đà ở Mệnh ứng nghiệm gì?

**📜 Source quote (NGUYÊN VĂN, p529)**:
> Thái Âm không ưa có Kình Dương, Đà La cùng ở cung mệnh, chủ về gian khổ.

**🇻🇳 Việt thuần (paraphrase)**: Thái Âm rất kỵ Kình Đà đồng cung Mệnh — chủ cuộc đời gian khổ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q23 — p530
**❓ Câu hỏi**: Thái Âm Hóa Kỵ bị Kình Đà giáp cung ứng nghiệm gì?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Âm Hóa Kỵ bị Kình Dương, Đà La giáp cung, đều chủ về không có duyên với lục thân, cô quả linh đinh, còn chủ về dễ đầu tư sai lầm.

**📖 Hán-Việt giải**: Lục thân = sáu người thân (cha, mẹ, vợ/chồng, anh em, con, bằng hữu); cô quả linh đinh = cô đơn lẻ loi.
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm Hóa Kỵ + bị Kình Đà giáp hai bên → không có duyên với người thân, cô đơn lẻ loi, dễ đầu tư sai lầm.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q24 — p530
**❓ Câu hỏi**: Thái Âm chủ về ẩn tàng, không nên đồng độ với sao nào, và mức không cát ra sao so với Thái Dương?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Thái Âm chủ về ẩn tàng, vì vậy cũng không nên có Địa Không, Địa Kiếp, Thiên Không đồng độ. Mức độ không cát tường lớn hơn so với Thái Dương.

**📖 Hán-Việt giải**: Ẩn tàng = giấu ẩn, kín đáo.
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm chủ ẩn tàng nên kỵ Không Kiếp Thiên Không đồng cung — mức xấu nặng hơn so với Thái Dương gặp các sao này.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q25 — p530
**❓ Câu hỏi**: Thái Âm chủ về phú nên ưa gặp sao gì, và Thái Âm Hóa Quyền chủ điều gì?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Thái Âm chủ về phú, cho nên rất ưa gặp sao lộc. Hóa Lộc là rất tốt, Lộc Tồn là kế đó. Thái Âm Hóa Quyền chỉ chủ về quản lý tài chính, hoặc nắm quyền tài chính, dù có thể phú cũng nhờ đó mà ra.

**🇻🇳 Việt thuần (paraphrase)**: Thái Âm chủ giàu → ưa sao lộc nhất; Hóa Lộc số 1, Lộc Tồn số 2. Thái Âm Hóa Quyền chỉ là quản lý hoặc nắm quyền tài chính — giàu có là nhờ vai trò này.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q26 — p530
**❓ Câu hỏi**: Thái Âm độc tọa ở Mão và Dậu so sánh thế nào, và trường hợp 'phản bối' Mão ra sao?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Thái Âm độc tọa ở hai cung Mão hoặc Dậu, ở cung Dậu ưu ở cung Mão rất nhiều. Có điều, nếu ở cung Mão gặp các sao phụ, tá cát mà không gặp sát tinh, lại được cát hóa, đây là cách cục "phản bối", chủ về đại phú.

**📖 Hán-Việt giải**: Cát hóa = được Tứ Hóa tốt (Lộc/Quyền/Khoa).
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm ở Dậu hơn ở Mão rất nhiều. Nhưng Mão nếu có phụ tá cát + không sát + được cát hóa → thành cách Phản Bối, đại phú.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q27 — p530
**❓ Câu hỏi**: Đại vận / lưu niên then chốt của Thái Âm độc tọa ở Mão hoặc Dậu là gì?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Đối với Thái Âm độc tọa ở hai cung Mão hoặc Dậu, các cung hạn Cự Môn, "Liêm Trinh, Thiên Tướng", Thất Sát, Thiên Cơ là những đại vận hoặc lưu niên có tính then chốt. Cách cục "phản bối" thì không luận Thiên Cơ.

**🇻🇳 Việt thuần (paraphrase)**: Với Thái Âm Mão/Dậu, đại vận hoặc lưu niên then chốt rơi vào: Cự Môn, Liêm-Tướng, Thất Sát, Thiên Cơ. Riêng cách Phản Bối thì không xét Thiên Cơ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q28 — p530
**❓ Câu hỏi**: Thái Âm độc tọa ở Thìn/Tuất ra sao và điều kiện thành phú quý?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Thái Âm độc tọa ở hai cung Thìn hoặc Tuất, Thái Dương và Thái Âm đều sáng, là thượng cách. Có điều, cần phải được cát hóa mới chủ về phú quý. Nếu không có sao cát, mà gặp sát tinh, sẽ chủ về danh lợi đều trống rỗng, hôn nhân cũng bất lợi.

**🇻🇳 Việt thuần (paraphrase)**: Thái Âm Thìn/Tuất → cả Nhật và Nguyệt đều sáng, thượng cách. Phải có cát hóa mới phú quý. Nếu không cát mà gặp sát → danh lợi đều rỗng, hôn nhân không tốt.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q29 — p530
**❓ Câu hỏi**: Đại vận / lưu niên then chốt của Thái Âm độc tọa Thìn/Tuất là gì?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Đối với Thái Âm độc tọa ở hai cung Thìn hoặc Tuất, các cung hạn "Liêm Trinh, Tham Lang", Cự Môn, "Vũ Khúc, Thất Sát", Thiên Cơ là đại vận hoặc lưu niên có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Thái Âm Thìn/Tuất, đại vận–lưu niên then chốt: Liêm-Tham, Cự Môn, Vũ-Sát, Thiên Cơ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q30 — p530
**❓ Câu hỏi**: Thái Âm độc tọa ở Tị hoặc Hợi khác nhau thế nào?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Thái Âm độc tọa ở hai cung Tị hoặc Hợi, ở cung Tị phần nhiều dễ có những khiếm khuyết đáng tiếc; nữ mệnh chủ về chổng là người tính toán cho người khác nhiều hơn là tính toán cho mình; nam mệnh phần nhiều trôi dạt. Đây là do Thái Âm lạc hãm, phát tán thái quá. Ở cung Hợi, gọi là "Nguyệt lãng thiên môn", gặp sao lộc thì chủ về kiếm được tiền một cách bất ngờ mà thành đại phú.

**📖 Hán-Việt giải**: Nguyệt lãng thiên môn = trăng sáng cửa trời.
**🇻🇳 Việt thuần (paraphrase)**: Thái Âm Tị: hãm, dễ khiếm khuyết — nữ mệnh chồng lo cho người khác, nam mệnh trôi dạt. Thái Âm Hợi: 'Nguyệt lãng thiên môn', gặp lộc thì giàu lớn bất ngờ.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q31 — p530
**❓ Câu hỏi**: Thái Âm độc tọa ở Tị hoặc Hợi gặp sao Đào Hoa và sát hình kỵ hao ra sao?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Thái Âm độc tọa ở hai cung Tị hoặc Hợi, gặp các sao Đào Hoa và các sao sát, hình, kỵ, hao, chủ về nhiều âm mưu mà còn ham tửu sắc.

**🇻🇳 Việt thuần (paraphrase)**: Thái Âm Tị/Hợi gặp Đào Hoa + sát hình kỵ hao → nhiều mưu mô và ham tửu sắc.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---
### [ ] tcq2-5.1.8-Q32 — p530
**❓ Câu hỏi**: Đại vận / lưu niên then chốt của Thái Âm độc tọa Tị/Hợi là gì?

**📜 Source quote (NGUYÊN VĂN, p530)**:
> Đối với Thái Âm độc tọa ở hai cung Tị hoặc Hợi, các cung hạn "Thiên Đồng, Cự Môn", Thất Sát, "Liêm Trinh, Thiên Phủ", "Thái Dương, Thiên Lương" là những đại vận hoặc lưu niên có tính then chốt.

**🇻🇳 Việt thuần (paraphrase)**: Thái Âm Tị/Hợi, đại vận–lưu niên then chốt rơi vào: Đồng-Cự, Thất Sát, Liêm-Phủ, Dương-Lương.

**Anh tick**: ✅ đúng paradigm  ⚠ cần sửa  ❌ ẨU bỏ

---