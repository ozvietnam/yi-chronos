# 📋 PoC v2 TWO-PASS — Trung Châu Q2 + 4 sách khác (145 atomic Q)

> Run: 2026-06-09 · MiniMax-M2 · TWO-PASS (meta-Q gen → atomic extract)
> Anh chỉ ra v1 sai: hardcode câu hỏi mặc định = vi phạm paradigm bottom-up
> v2 fix: LLM tự propose knowledge_categories + question_templates per chunk

**Validation:**
- v1: 96 atoms / 1 sách / 1 format (nguyen_ly)
- v2: 145 atoms (+51%) / 4 sách / 3 format (+tho_phu +ket_qua)

**Anh review từng chunk: ✅ đúng / ⚠ mơ hồ / ❌ sai**

---

## 📄 trung-chau-tu-vi-dau-so-2 · p0347 — `luận giải case Vũ-Phá Tỵ`

**Archetype:** `chu_the+cong_thuc+luan_giai+kinh_nghiem` | **Format:** `nguyen_ly` | **12 atoms**

**Knowledge Categories (LLM tự propose — bottom-up):**
- cách cục Vũ Khúc Phá Quân tọa cung Tỵ với Cự Môn ở Tuất
- luận giải Giao Hữu trong Đại Vận Bính Dần
- định nghĩa Thiên Tướng độc tọa ở cung Tỵ hoặc Hợi
- công thức xác định Thiên Tướng có sức khai sáng

**Chunk preview:**
> <!-- page 347 -->  Cung Mệnh là “Vũ Khúc, Phá Quân” tọa cung Tỵ, cung Giao Hữu là Cự Môn ở Tuất. Người sinh năm Kỷ, Cự Môn hội hợp với Thái Dương và Lộc Tồn ở cung Ngọ, vì vậy mệnh tạo giao du rộng.  Đến Đại Vận Bính Dần, cung Giao Hữu là Thiên Phủ đ...

### 🎯 cách cục Vũ Khúc Phá Quân tọa cung Tỵ với Cự Môn ở Tuất (3 atoms)

- **Q:** Cung Mệnh Vũ Khúc Phá Quân tọa cung Tỵ có đặc điểm gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Cách cục Cung Mệnh Vũ Khúc Phá Quân tọa cung Tỵ có đặc điểm gì?
  - **IDs:** `sao`: Vũ Khúc, Phá Quân · `cung`: Tỵ · `cung_menh`: Cung Mệnh
  - **Quote:** _Cung Mệnh là “Vũ Khúc, Phá Quân” tọa cung Tỵ..._

- **Q:** Tại sao người sinh năm Kỷ có mệnh tạo giao du rộng?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao người sinh năm Kỷ có mệnh tạo giao du rộng?
  - **IDs:** `nam`: Kỷ · `sao`: Cự Môn, Thái Dương, Lộc Tồn · `cung`: Ngọ
  - **Quote:** _Người sinh năm Kỷ, Cự Môn hội hợp với Thái Dương và Lộc Tồn ở cung Ngọ, vì vậy mệnh tạo giao du rộng...._

- **Q:** Cự Môn ở cung Giao Hữu Tuất kết hợp với sao nào tạo thành?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Cự Môn ở cung Giao Hữu Tuất kết hợp với sao nào tạo thành?
  - **IDs:** `sao`: Cự Môn · `cung`: Giao Hữu · `chi`: Tuất
  - **Quote:** _Cung Giao Hữu là Cự Môn ở Tuất...._

### 🎯 luận giải Giao Hữu trong Đại Vận Bính Dần (3 atoms)

- **Q:** Đại Vận Bính Dần cung Giao Hữu có những sao nào hiện diện?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Đại Vận Bính Dần cung Giao Hữu có những sao nào hiện diện?
  - **IDs:** `dai_van`: Bính Dần · `cung`: Giao Hữu · `sao`: Thiên Phủ, Kình Dương, Liêm Trinh, Thất Sát, Tử Vi, Tham Lang, Linh Tồn, Văn Khúc
  - **Quote:** _Đến Đại Vận Bính Dần, cung Giao Hữu là Thiên Phủ độc tọa, có Kình Dương của nguyên cục đồng độ, đối cung là “Liêm Trinh, Thất Sát” mà Liêm Trinh Hóa Kỵ, hội hợp với “Tử Vi, Tham Lang” mượn sao an cung..._

- **Q:** Tại sao cung Giao Hữu Đại Vận Bính Dần gặp Văn Khúc Hóa Kỵ lại chủ về tình cảm trắc trở?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao cung Giao Hữu gặp Văn Khúc Hóa Kỵ lại chủ về tình cảm trắc trở?
  - **IDs:** `dai_van`: Bính Dần · `cung`: Giao Hữu · `sao`: Văn Khúc
  - **Quote:** _cung này lại gặp Văn Khúc Hóa Kỵ, cho nên chủ về tình cảm trắc trở...._

- **Q:** Linh Tham cách trong cung Giao Hữu Đại Vận Bính Dần có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Linh Tham cách trong cung Giao Hữu Đại Vận Bính Dần có ý nghĩa gì?
  - **IDs:** `dai_van`: Bính Dần · `cung`: Giao Hữu · `sao`: Linh Tồn, Tham Lang · `cach`: Linh Tham
  - **Quote:** _Tuy có Linh Tồn đồng độ, thành “Linh Tham” cách..._

### 🎯 định nghĩa Thiên Tướng độc tọa ở cung Tỵ hoặc Hợi (3 atoms)

- **Q:** Thiên Tướng độc tọa ở cung Tỵ hoặc Hợi có đặc tính gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Tướng độc tọa ở cung Tỵ hoặc Hợi có đặc tính gì?
  - **IDs:** `sao`: Thiên Tướng · `cung`: Tỵ hoặc Hợi
  - **Quote:** _Thiên Tướng độc tọa ở hai cung Tỵ hoặc Hợi, đối cung là “Vũ Khúc, Phá Quân”, phương tam hợp là Thiên Phủ độc tọa, và “Tử Vi, Tham Lang” mượn sao an cung. Thiên Tướng độc tọa ở hai cung này, là ổn nhất..._

- **Q:** Thiên Tướng độc tọa ở cung Tỵ hoặc Hợi có phải là ổn định nhất trong 12 cung không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Tướng độc tọa ở hai cung này là ổn định nhất trong 12 cung có đúng không?
  - **IDs:** `sao`: Thiên Tướng · `cung`: Tỵ hoặc Hợi
  - **Quote:** _Thiên Tướng độc tọa ở hai cung này, là ổn nhất trong 12 cung...._

- **Q:** Thiên Tướng độc tọa ở cung Tỵ hoặc Hợi thiếu tính độc lập thể hiện như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Tướng độc tọa thiếu tính độc lập thể hiện như thế nào?
  - **IDs:** `sao`: Thiên Tướng · `cung`: Tỵ hoặc Hợi · `tinh_tinh`: thiếu tính độc lập
  - **Quote:** _Nhưng do bản thân Thiên Tướng thiếu tính độc lập, cho nên rất khó tự làm chủ...._

### 🎯 công thức xác định Thiên Tướng có sức khai sáng (3 atoms)

- **Q:** Làm sao phân biệt Thiên Tướng có sức khai sáng hay chỉ nhờ người khác mà thành việc?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Làm sao phân biệt Thiên Tướng có sức khai sáng hay chỉ nhờ người khác?
  - **IDs:** `sao`: Thiên Tướng, Lộc, Liêm Trinh, Thiên Phủ
  - **Quote:** _Hễ Thiên Tướng gặp sao Lộc, mà sao Lộc không vây chiếu Thiên Phủ, là cách cục “có sức khai sáng”. Nói một cách cụ thể hơn, tức là Liêm Trinh Hóa Lộc ở hai cung Sửu hoặc Mùi vây chiếu Thiên Phủ...._

- **Q:** Liêm Trinh Hóa Lộc ở cung nào thì vây chiếu được Thiên Phủ?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh Hóa Lộc ở cung nào thì vây chiếu được Thiên Phủ?
  - **IDs:** `sao`: Liêm Trinh, Thiên Phủ · `chi`: Sửu, Mùi · `hoa`: Hóa Lộc
  - **Quote:** _Nói một cách cụ thể hơn, tức là Liêm Trinh Hóa Lộc ở hai cung Sửu hoặc Mùi vây chiếu Thiên Phủ...._

- **Q:** Điều kiện để Thiên Tướng thuộc cách cục có sức khai sáng là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Điều kiện để Thiên Tướng thuộc cách cục có sức khai sáng là gì?
  - **IDs:** `sao`: Thiên Tướng, Lộc, Thiên Phủ · `dieu_kien`: gặp sao Lộc, sao Lộc không vây chiếu Thiên Phủ
  - **Quote:** _Hễ Thiên Tướng gặp sao Lộc, mà sao Lộc không vây chiếu Thiên Phủ, là cách cục “có sức khai sáng”...._

---

## 📄 trung-chau-tu-vi-dau-so-2 · p0412 — `chủ thể Liêm Trinh`

**Archetype:** `chu_the+luan_giai+to_hop+kinh_nghiem` | **Format:** `nguyen_ly` | **16 atoms**

**Knowledge Categories (LLM tự propose — bottom-up):**
- định nghĩa và phân loại cung Liêm Trinh (mẫn cảm vs thiết thực)
- tổ hợp Liêm Trinh với sao đào hoa và văn sao
- tổ hợp Liêm Trinh với Hỏa Tinh/Linh Tinh và hậu quả cách cục
- tổ hợp Liêm Trinh với Địa Không/Địa Kiếp
- tổ hợp Liêm Trinh với Lộc Tồn và Tham Lang
- tương tác Liêm Trinh với Phá Quân trong cung hạn

**Chunk preview:**
> <!-- page 412 -->  **Liêm Trinh** thuộc loại “mẫn cảm” thông thường có khí chất nghệ thuật, xem trọng sinh hoạt tinh thần. Có **Tham Lang Hóa Kỵ** vây chiếu, hoặc **Liêm Trinh Hóa Kỵ** thì sắc thái này càng nặng. **Văn Xương**, **Văn Khúc**, **Thiên ...

### 🎯 định nghĩa và phân loại cung Liêm Trinh (mẫn cảm vs thiết thực) (4 atoms)

- **Q:** Liêm Trinh loại 'mẫn cảm' khác loại 'thiết thực' ở điểm nào về cơ sở sinh hoạt?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh loại 'mẫn cảm' khác loại 'thiết thực' ở điểm nào?
  - **IDs:** `sao`: Liêm Trinh · `loai_cung`: mẫn cảm, thiết thực
  - **Quote:** _Liêm Trinh thuộc loại 'mẫn cảm' thông thường có khí chất nghệ thuật, xem trọng sinh hoạt tinh thần. Liêm Trinh thuộc loại 'thiết thực', dù cũng xem trọng sinh hoạt tinh thần, nhưng lấy hưởng thụ vật c..._

- **Q:** Liêm Trinh loại 'mẫn cảm' có đặc điểm khí chất gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh 'mẫn cảm' có đặc điểm tính cách gì?
  - **IDs:** `sao`: Liêm Trinh · `loai_cung`: mẫn cảm · `dac_diem`: khí chất nghệ thuật
  - **Quote:** _Liêm Trinh thuộc loại 'mẫn cảm' thông thường có khí chất nghệ thuật, xem trọng sinh hoạt tinh thần...._

- **Q:** Liêm Trinh loại 'thiết thực' lấy gì làm cơ sở trong sinh hoạt?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh 'thiết thực' lấy gì làm cơ sở trong sinh hoạt?
  - **IDs:** `sao`: Liêm Trinh · `loai_cung`: thiết thực · `dac_diem`: hưởng thụ vật chất
  - **Quote:** _Liêm Trinh thuộc loại 'thiết thực', dù cũng xem trọng sinh hoạt tinh thần, nhưng lấy hưởng thụ vật chất làm cơ sở...._

- **Q:** Tham Lang Hóa Kỵ vây chiếu Liêm Trinh 'mẫn cảm' có tác động gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Hóa Kỵ vây chiếu Liêm Trinh 'mẫn cảm'会造成什么影响?
  - **IDs:** `sao`: Liêm Trinh · `sao_hoa_ky`: Tham Lang Hóa Kỵ · `loai_cung`: mẫn cảm · `hieu_ung`: sắc thái nặng hơn
  - **Quote:** _Có Tham Lang Hóa Kỵ vây chiếu, hoặc Liêm Trinh Hóa Kỵ thì sắc thái này càng nặng...._

### 🎯 tổ hợp Liêm Trinh với sao đào hoa và văn sao (2 atoms)

- **Q:** Văn Xương, Văn Khúc, Thiên Tài, Long Trì, Phượng Các, Hoa Cái có tác dụng gì với Liêm Trinh 'mẫn cảm'?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Văn Xương, Văn Khúc, Thiên Tài, Long Trì, Phượng Các, Hoa Cái ảnh hưởng thế nào đến Liêm Trinh?
  - **IDs:** `sao`: Liêm Trinh · `sao_van`: ['Văn Xương', 'Văn Khúc', 'Thiên Tài', 'Long Trì', 'Phượng Các', 'Hoa Cái'] · `loai_cung`: mẫn cảm · `hieu_ung`: mạnh tính chất nghệ thuật
  - **Quote:** _Văn Xương, Văn Khúc, Thiên Tài, Long Trì, Phượng Các, Hoa Cái, và các sao đào hoa khác, đều làm mạnh thêm tính chất kể trên...._

- **Q:** Tả Phụ và Hữu Bật có tác dụng gì với Liêm Trinh 'thiết thực'?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tả Phụ và Hữu Bật có tác dụng gì với Liêm Trinh loại nào?
  - **IDs:** `sao`: Liêm Trinh · `sao_phu`: ['Tả Phụ', 'Hữu Bật'] · `loai_cung`: thiết thực · `hieu_ung`: mạnh tính chất thiết thực
  - **Quote:** _Gặp các sao phụ, tá sẽ làm tính chất này mạnh thêm, nhất là Tả Phụ và Hữu Bật...._

### 🎯 tổ hợp Liêm Trinh với Hỏa Tinh/Linh Tinh và hậu quả cách cục (2 atoms)

- **Q:** Liêm Trinh đồng độ Hỏa Tinh hoặc Linh Tinh có làm hỏng cách cục 'Hùng Tú Kiển Nguyên' không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh đồng độ Hỏa Tinh hoặc Linh Tinh có hỏng cách cục 'Hùng Tú Kiển Nguyên' không?
  - **IDs:** `sao`: Liêm Trinh · `sao_hoa`: ['Hỏa Tinh', 'Linh Tinh'] · `cach_cuc`: Hùng Tú Kiển Nguyên · `hieu_ung`: làm hỏng cách cục
  - **Quote:** _Liêm Trinh đồng độ với Hỏa Tinh hoặc Linh Tinh, không những làm hỏng cách cục 'Hùng Tú Kiển Nguyên'...._

- **Q:** Liêm Trinh 'mẫn cảm' gặp Hỏa Tinh hoặc Linh Tinh sẽ biến thành tính xấu gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh 'mẫn cảm' gặp Hỏa Tinh/Linh Tinh sẽ biến thành tính gì xấu?
  - **IDs:** `sao`: Liêm Trinh · `sao_hoa`: ['Hỏa Tinh', 'Linh Tinh'] · `loai_cung`: mẫn cảm · `tinh_xau`: ['tự cho mình là người yêu của người nào đó', 'có trăng quên đèn', 'xu phụ quyển thế', 'cơ hội'] · `hieu_ung`: biến thành không lành
  - **Quote:** _mà còn khiến tính chất 'mẫn cảm' của nó biến thành không lành, như tự cho mình là người yêu của người nào đó, hoặc có trăng quên đèn; là kết cấu sao rất xấu, có thể biến thành tính xu phụ quyển thế, c..._

### 🎯 tổ hợp Liêm Trinh với Địa Không/Địa Kiếp (2 atoms)

- **Q:** Liêm Trinh 'thiết thực' gặp Địa Không hoặc Địa Kiếp đồng độ hoặc vây chiếu có hậu quả gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh 'thiết thực' gặp Địa Không/Địa Kiếp đồng độ hoặc vây chiếu có hậu quả gì?
  - **IDs:** `sao`: Liêm Trinh · `sao_sat`: ['Địa Không', 'Địa Kiếp'] · `loai_cung`: thiết thực · `hieu_ung`: đời người bị trắc trở nghiêm trọng ít nhất một lần
  - **Quote:** _Liêm Trinh thuộc loại 'thiết thực' không nên gặp Địa Không, Địa Kiếp đồng độ hoặc vây chiếu; nếu một sao ở cung Mệnh và một sao ở cung Thiên Di, thì đời người ít nhất cũng bị trắc trở nghiêm trọng một..._

- **Q:** Liêm Trinh 'mẫn cảm' gặp Địa Không hoặc Địa Kiếp thì tinh thần và vật chất như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh 'mẫn cảm' gặp Địa Không/Địa Kiếp thì tinh thần và vật chất ra sao?
  - **IDs:** `sao`: Liêm Trinh · `sao_sat`: ['Địa Không', 'Địa Kiếp'] · `loai_cung`: mẫn cảm · `hieu_ung`: tinh thần lẫn vật chất đều rối rắm
  - **Quote:** _Nếu Liêm Trinh thuộc loại 'mẫn cảm' gặp tình hình này thì tinh thần lẫn vật chất đều rối rắm...._

### 🎯 tổ hợp Liêm Trinh với Lộc Tồn và Tham Lang (2 atoms)

- **Q:** Liêm Trinh có ưa hội Lộc Tồn không và khi nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh ưa hội Lộc Tồn khi nào?
  - **IDs:** `sao`: Liêm Trinh · `sao_loc`: Lộc Tồn · `hieu_ung`: ưa hội
  - **Quote:** _Liêm Trinh cũng ưa hội Lộc Tồn, rất ưa Lộc Tồn đồng độ với Tham Lang...._

- **Q:** Lộc Tồn đồng độ với Tham Lang và Liêm Trinh có ý nghĩa gì về cảnh ngộ cuộc đời?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Lộc Tồn đồng độ Tham Lang với Liêm Trinh có ý nghĩa gì về cảnh ngộ cuộc đời?
  - **IDs:** `sao`: ['Liêm Trinh', 'Lộc Tồn', 'Tham Lang'] · `hieu_ung`: cuộc đời gặp nhiều cảnh ngộ thuận lợi toại ý, thường gặp may mắn bất ngờ trong những lúc khó khăn
  - **Quote:** _rất ưa Lộc Tồn đồng độ với Tham Lang, chủ về cuộc đời gặp nhiều cảnh ngộ thuận lợi toại ý, và thường gặp may mắn bất ngờ trong những lúc khó khăn...._

### 🎯 tương tác Liêm Trinh với Phá Quân trong cung hạn (4 atoms)

- **Q:** Liêm Trinh có ưa cung hạn Phá Quân độc tọa không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Liêm Trinh có ưa cung hạn Phá Quân độc tọa không?
  - **IDs:** `sao`: Liêm Trinh · `cung_han`: Phá Quân độc tọa · `hieu_ung`: thông thường không ưa
  - **Quote:** _Cung hạn Phá Quân độc tọa, thông thường Liêm Trinh không ưa đến...._

- **Q:** Phá Quân cần điều kiện gì để trở nên có lợi cho Liêm Trinh?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Phá Quân cần điều kiện gì để trở nên có lợi cho Liêm Trinh?
  - **IDs:** `cung_han`: Phá Quân · `dieu_kien`: ['cung hạn được cát hóa', 'Thiên Khôi giáp cung hoặc tương hội', 'Thiên Việt giáp cung hoặc tương hội'] · `hieu_ung`: vận trình có tính sáng tạo
  - **Quote:** _Trừ phi cung hạn được cát hóa, Phá Quân lại được Thiên Khôi, Thiên Việt giáp cung hoặc tương hội, đây là vận trình có tính sáng tạo...._

- **Q:** Thiên Khôi, Thiên Việt giáp cung hoặc tương hội với Phá Quân tạo ra vận trình gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Khôi, Thiên Việt giáp cung hoặc tương hội với Phá Quân tạo ra vận trình gì?
  - **IDs:** `sao`: ['Thiên Khôi', 'Thiên Việt'] · `cung_han`: Phá Quân · `hieu_ung`: vận trình có tính sáng tạo
  - **Quote:** _Phá Quân lại được Thiên Khôi, Thiên Việt giáp cung hoặc tương hội, đây là vận trình có tính sáng tạo...._

- **Q:** Khi Liêm Trinh gặp Phá Quân được cát hóa, cần kiểm tra gì ở hậu vận?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Khi Liêm Trinh gặp Phá Quân được cát hóa, cần kiểm tra gì ở hậu vận?
  - **IDs:** `sao`: Liêm Trinh · `cung_han`: Phá Quân cát hóa · `kiem_tra`: hậu vận hoặc các lưu niên sau đó · `khuyen_nghi`: nếu hậu vận không tiếp tục tốt thì nên chọn phương kế bảo thủ
  - **Quote:** _Lúc này cần phải kiểm tra hậu vận (hoặc các lưu niên sau đó), nếu hậu vận không tiếp tục tốt, thì nên chọn phương kế bảo thủ hơn là tiến thủ...._

---

## 📄 trung-chau-tu-vi-dau-so-2 · p0501 — `12 cung định nghĩa`

**Archetype:** `chu_the+luan_giai+to_hop+kinh_nghiem` | **Format:** `nguyen_ly` | **0 atoms**

**Knowledge Categories (LLM tự propose — bottom-up):**
- định nghĩa 12 cung trong Tử Vi và tính chất cơ bản
- khái niệm Phi Động - di chuyển cung khi luận Đại Hạn/Lưu Niên
- phương pháp Di Cung Hoán Vị của phái Trung Châu
- tổ hợp Phiếm Thủy Đào Hoa (Tử Vi + Kình Dương + Tham Lang)
- cách cục Tử Vi độc tọa cung Ngọ và ảnh hưởng qua các Đại Hạn

**Chunk preview:**
> <!-- page 501 -->  Chương này luận về các cung, là nói về 12 cung: **cung Mệnh** (cũng gọi là cung Thân), **cung Huynh Đệ**, **cung Phu Thê**, **cung Tử Tức**, **cung Tài Bạch**, **cung Tật Ách**, **cung Thiên Di**, **cung Giao Hữu**, **cung Sự Nghiệ...

⚠ Pass 2 fail: JSONDecodeError: Expecting ',' delimiter: line 1 column 373 (char 372)

---

## 📄 trung-chau-tu-vi-dau-so-2 · p0502 — `Cô Quân Vô Đạo case`

**Archetype:** `chu_the+luan_giai+to_hop+kinh_nghiem` | **Format:** `nguyen_ly` | **20 atoms**

**Knowledge Categories (LLM tự propose — bottom-up):**
- định nghĩa cách cục Cô Quân Vô Đạo và điều kiện hình thành
- phản ứng của sao Thiên Đồng Hóa Lộc với Thái Âm Hóa Kỵ trong cung Mệnh đại hạn
- so sánh phản ứng của Tử Vi và Thiên Cơ khi gặp Thiên Đồng Hóa Lộc trong đại hạn Ất Mùi
- ảnh hưởng của Kình Dương đồng đội với Tử Vi trong cách cục Cô Quân Vô Đạo
- ảnh hưởng của Thiên Cơ Hóa Quyền trong cách cục Cô Quân Vô Đạo
- nguyên tắc theo cát tránh hung qua phản ứng 12 cung

**Chunk preview:**
> <!-- page 502 -->  ...củng”, đây là cách cục “Cô Quân Vô Đạo”. Lúc đi thuận đến cung Mùi, mượn **Thiên Đồng**, **Cự Môn** của đối cung để an sao, mà **Thiên Đồng Hóa Lộc**. Nếu gặp sao lộc ở cung Mùi là cung mệnh của đại hạn, nhất định sẽ ưa Thiên Đồ...

### 🎯 định nghĩa cách cục Cô Quân Vô Đạo và điều kiện hình thành (2 atoms)

- **Q:** Cách cục Cô Quân Vô Đạo được định nghĩa như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Cách cục Cô Quân Vô Đạo được định nghĩa như thế nào?
  - **IDs:** `sao`: Tử Vi · `cung`: cung Mùi · `cach_cuc`: Cô Quân Vô Đạo · `sao_anh_huong`: Thiên Đồng, Cự Môn
  - **Quote:** _đây là cách cục "Cô Quân Vô Đạo". Lúc đi thuận đến cung Mùi, mượn Thiên Đồng, Cự Môn của đối cung để an sao, mà Thiên Đồng Hóa Lộc...._

- **Q:** Điều kiện để hình thành cách cục Cô Quân Vô Đạo là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Điều kiện để hình thành cách cục Cô Quân Vô Đạo là gì?
  - **IDs:** `sao`: Tử Vi, Thiên Đồng, Cự Môn · `cung`: cung Mùi · `cung_doi`: đối cung · `che_bien`: Thiên Đồng Hóa Lộc
  - **Quote:** _Lúc đi thuận đến cung Mùi, mượn Thiên Đồng, Cự Môn của đối cung để an sao, mà Thiên Đồng Hóa Lộc...._

### 🎯 phản ứng của sao Thiên Đồng Hóa Lộc với Thái Âm Hóa Kỵ trong cung Mệnh đại hạn (4 atoms)

- **Q:** Thiên Đồng Hóa Lộc gặp Thái Âm Hóa Kỵ trong cung Mệnh đại hạn của Tử Vi Cô Quân Vô Đạo có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Đồng Hóa Lộc gặp Thái Âm Hóa Kỵ trong cung Mệnh đại hạn có ý nghĩa gì?
  - **IDs:** `sao`: Thiên Đồng, Thái Âm, Tử Vi · `cung`: cung Mệnh, cung Mùi · `che_bien`: Thiên Đồng Hóa Lộc, Thái Âm Hóa Kỵ · `cach_cuc`: Cô Quân Vô Đạo
  - **Quote:** _cung mệnh của đại hạn đồng thời còn hội Thái Âm Hóa Kỵ, đối với Tử Vi "Cô Quân Vô Đạo" mà nói, Hóa Lộc hội lộc của "Thiên Đồng, Cự Môn", sẽ vì Thái Âm Hóa Kỵ mà diễn hóa thành vì tiền mà gây nên tình ..._

- **Q:** Tại sao sự kết hợp giữa Thiên Đồng Hóa Lộc và Thái Âm Hóa Kỵ trong cung Mệnh đại hạn lại dẫn đến vì tiền mà gây nên tình hình bất lợi?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao sự kết hợp này lại dẫn đến vì tiền mà gây nên tình hình bất lợi?
  - **IDs:** `sao`: Thiên Đồng, Thái Âm, Cự Môn · `cung`: cung Mệnh, cung Mùi · `che_bien`: Thiên Đồng Hóa Lộc, Thái Âm Hóa Kỵ · `chi`: Ất Mùi
  - **Quote:** _sẽ vì Thái Âm Hóa Kỵ mà diễn hóa thành vì tiền mà gây nên tình hình bất lợi. Nói một cách cụ thể hơn, rất có thể là, vì tham lợi nhỏ mà phạm sai lầm, làm ảnh hưởng đến sự nghiệp...._

- **Q:** Lỗi phạm sai lầm vì tham lợi nhỏ trong trường hợp Thiên Đồng Hóa Lộc gặp Thái Âm Hóa Kỵ trong cung Mệnh đại hạn Ất Mùi thể hiện như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Lỗi phạm sai lầm vì tham lợi nhỏ trong trường hợp này thể hiện như thế nào?
  - **IDs:** `sao`: Thiên Đồng, Thái Âm · `cung`: cung Mệnh, cung Mùi · `che_bien`: Thiên Đồng Hóa Lộc, Thái Âm Hóa Kỵ · `chi`: Ất Mùi · `nam_sinh`: Bính
  - **Quote:** _rất có thể là, vì tham lợi nhỏ mà phạm sai lầm, làm ảnh hưởng đến sự nghiệp...._

- **Q:** Cung can Ất có Lưu Lộc (Tổn) ở cung Mão ảnh hưởng gì đến luận đoán trong cách cục Cô Quân Vô Đạo?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Cung can Ất có Lưu Lộc (Tổn) ở cung Mão ảnh hưởng gì đến luận đoán?
  - **IDs:** `cung_can`: Ất · `cung`: cung Mão · `sao`: Lưu Lộc · `che_bien`: Tổn · `chi`: Ất Mùi
  - **Quote:** _Thêm vào đó cung can là Ất, có Lưu Lộc (Tổn) ở cung Mão đến hội, do đó dễ luận đoán là vận tốt, mà còn có thể luận đoán đây là vận trình phát tài, tay trắng làm nên...._

### 🎯 so sánh phản ứng của Tử Vi và Thiên Cơ khi gặp Thiên Đồng Hóa Lộc trong đại hạn Ất Mùi (4 atoms)

- **Q:** Tử Vi tọa mệnh ở cung Ngọ gặp Thiên Đồng Hóa Lộc trong đại hạn Ất Mùi khác gì với Thiên Cơ tọa mệnh ở cung Tị?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tử Vi tọa mệnh ở cung Ngọ gặp Thiên Đồng Hóa Lộc trong đại hạn Ất Mùi khác gì với Thiên Cơ tọa mệnh ở cung Tị?
  - **IDs:** `sao`: Tử Vi, Thiên Cơ · `cung`: cung Ngọ, cung Tị · `chi`: Ất Mùi · `nam_sinh`: Bính · `che_bien`: Thiên Đồng Hóa Lộc
  - **Quote:** _Thiên Cơ tọa mệnh ở cung Tị, cũng là người sinh năm Bính... đến đại hạn Ất Mùi, cũng vậy, gặp Thiên Đồng Hóa Lộc... Chỉ xét riêng tam phương tứ chính của cung Mùi, thì tương đồng với ví dụ trước Tử Vi..._

- **Q:** Tại sao Tử Vi tọa mệnh ở cung Ngọ lại có Kình Dương đồng đội còn Thiên Cơ tọa mệnh ở cung Tị thì không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao Tử Vi lại có Kình Dương đồng đội còn Thiên Cơ thì không?
  - **IDs:** `sao`: Tử Vi, Thiên Cơ, Kình Dương · `cung`: cung Ngọ, cung Tị · `chi`: Ất Mùi · `nam_sinh`: Bính
  - **Quote:** _theo bí truyền của phái Trung Châu Vương Đình Chí, thì do tính chất của Thiên Cơ Hóa Quyền, nên khác với Tử Vi có Kình Dương đồng đội, vì vậy xảy ra phản ứng khác nhau..._

- **Q:** Sự khác nhau về phản ứng khi đầu tư giữa Tử Vi tọa mệnh ở cung Ngọ và Thiên Cơ tọa mệnh ở cung Tị trong đại hạn Ất Mùi là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Sự khác nhau về phản ứng khi đầu tư giữa hai người trong ví dụ là gì?
  - **IDs:** `sao`: Tử Vi, Thiên Cơ · `cung`: cung Ngọ, cung Tị · `chi`: Ất Mùi · `nam_sinh`: Bính · `hanh_dong`: đầu tư
  - **Quote:** _biến thành lúc đầu tư đang kiếm tiền thuận lợi, đột nhiên vì bị ảnh hưởng của người khác mà đưa ra quyết định sai lầm, khiến đầu tư bị tổn thất...._

- **Q:** Theo phái Trung Châu Vương Đình Chí, điều gì quyết định sự khác biệt phản ứng giữa Tử Vi và Thiên Cơ khi gặp Thiên Đồng Hóa Lộc trong đại hạn Ất Mùi?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Theo phái Trung Châu Vương Đình Chí, điều gì quyết định sự khác biệt này?
  - **IDs:** `phai`: Trung Châu Vương Đình Chí · `sao`: Tử Vi, Thiên Cơ, Kình Dương · `chi`: Ất Mùi · `che_bien`: Thiên Cơ Hóa Quyền
  - **Quote:** _theo bí truyền của phái Trung Châu Vương Đình Chí, thì do tính chất của Thiên Cơ Hóa Quyền, nên khác với Tử Vi có Kình Dương đồng đội, vì vậy xảy ra phản ứng khác nhau..._

### 🎯 ảnh hưởng của Kình Dương đồng đội với Tử Vi trong cách cục Cô Quân Vô Đạo (3 atoms)

- **Q:** Kình Dương đồng đội với Tử Vi trong cách cục Cô Quân Vô Đạo có tác dụng gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Kình Dương đồng đội với Tử Vi trong cách cục Cô Quân Vô Đạo có tác dụng gì?
  - **IDs:** `sao`: Tử Vi, Kình Dương · `cach_cuc`: Cô Quân Vô Đạo · `cung`: cung Ngọ
  - **Quote:** _Tử Vi có Kình Dương đồng đội, vì vậy xảy ra phản ứng khác nhau..._

- **Q:** Tại sao Kình Dương đồng đội lại khiến phản ứng của Tử Vi khác với Thiên Cơ trong cách cục Cô Quân Vô Đạo?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao Kình Dương lại khiến phản ứng của Tử Vi khác với Thiên Cơ?
  - **IDs:** `sao`: Tử Vi, Thiên Cơ, Kình Dương · `cach_cuc`: Cô Quân Vô Đạo · `cung`: cung Ngọ, cung Tị
  - **Quote:** _do tính chất của Thiên Cơ Hóa Quyền, nên khác với Tử Vi có Kình Dương đồng đội, vì vậy xảy ra phản ứng khác nhau..._

- **Q:** Kình Dương đồng đội với Tử Vi trong cách cục Cô Quân Vô Đạo mang tính chất Cát hay Hung?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Kình Dương trong cách cục này mang tính chất Cát hay Hung?
  - **IDs:** `sao`: Tử Vi, Kình Dương · `cach_cuc`: Cô Quân Vô Đạo · `cung`: cung Ngọ · `tinh_chat`: Cát/Hung
  - **Quote:** _Tử Vi có Kình Dương đồng đội, vì vậy xảy ra phản ứng khác nhau..._

### 🎯 ảnh hưởng của Thiên Cơ Hóa Quyền trong cách cục Cô Quân Vô Đạo (3 atoms)

- **Q:** Thiên Cơ Hóa Quyền ảnh hưởng như thế nào đến cách cục Cô Quân Vô Đạo?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ Hóa Quyền ảnh hưởng như thế nào đến cách cục Cô Quân Vô Đạo?
  - **IDs:** `sao`: Thiên Cơ · `che_bien`: Thiên Cơ Hóa Quyền · `cach_cuc`: Cô Quân Vô Đạo · `cung`: cung Tị
  - **Quote:** _Thiên Cơ tọa mệnh ở cung Tị, cũng là người sinh năm Bính, Thiên Cơ Hóa Quyền, đồng độ với Lộc Tồn...._

- **Q:** Tại sao Thiên Cơ Hóa Quyền lại dẫn đến quyết định sai lầm do ảnh hưởng người khác trong đại hạn Ất Mùi?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao Thiên Cơ Hóa Quyền lại dẫn đến quyết định sai lầm do ảnh hưởng người khác?
  - **IDs:** `sao`: Thiên Cơ · `che_bien`: Thiên Cơ Hóa Quyền · `cung`: cung Tị · `chi`: Ất Mùi · `nam_sinh`: Bính · `hanh_dong`: đầu tư
  - **Quote:** _biến thành lúc đầu tư đang kiếm tiền thuận lợi, đột nhiên vì bị ảnh hưởng của người khác mà đưa ra quyết định sai lầm, khiến đầu tư bị tổn thất...._

- **Q:** Thiên Cơ Hóa Quyền kết hợp với Lộc Tồn và Cự Môn trong đại hạn Ất Mùi tạo ra kết quả gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ Hóa Quyền kết hợp với Lộc Tồn và Cự Môn trong đại hạn Ất Mùi tạo ra kết quả gì?
  - **IDs:** `sao`: Thiên Cơ, Lộc Tồn, Cự Môn · `che_bien`: Thiên Cơ Hóa Quyền · `chi`: Ất Mùi · `cung`: cung Tị
  - **Quote:** _Thiên Cơ Hóa Quyền, đồng độ với Lộc Tồn. Đến đại hạn Ất Mùi, cũng vậy, gặp Thiên Đồng Hóa Lộc, có Cự Môn đồng đội, Lộc Tồn đến hội, và Thái Âm Hóa Kỵ hội chiếu...._

### 🎯 nguyên tắc theo cát tránh hung qua phản ứng 12 cung (4 atoms)

- **Q:** Nguyên tắc theo cát tránh hung được vận dụng như thế nào trong luận đoán 12 cung?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Theo cát tránh hung được vận dụng như thế nào trong luận đoán 12 cung?
  - **IDs:** `phuong_phap`: theo cát tránh hung · `doi_tuong`: 12 cung
  - **Quote:** _Có thể thấy, cần phải nhận thức một cách rõ ràng phản ứng của các sao ở 12 cung, sau đó mới có thể luận đoán một cách chính xác, và từ đó có thể tìm ra cách vận dụng phép "theo cát tránh hung"...._

- **Q:** Tại sao chỉ xem xét tam phương tứ chính của cung mệnh rất dễ luận đoán sai trong đại hạn Ất Mùi?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao chỉ xem xét tam phương tứ chính của cung mệnh rất dễ luận đoán sai?
  - **IDs:** `cung`: cung Mệnh · `tam_phuong_tu_chinh`: tam phương tứ chính · `chi`: Ất Mùi · `vi_du`: Tử Vi cung Ngọ, Thiên Cơ cung Tị
  - **Quote:** _Chỉ xét riêng tam phương tứ chính của cung Mùi, thì tương đồng với ví dụ trước Tử Vi tọa mệnh ở cung Ngọ. Nhưng theo bí truyền của phái Trung Châu Vương Đình Chí... xảy ra phản ứng khác nhau... Nếu ch..._

- **Q:** Cần nhận thức những gì để luận đoán chính xác phản ứng của các sao ở 12 cung?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Cần nhận thức những gì để luận đoán chính xác phản ứng của các sao ở 12 cung?
  - **IDs:** `doi_tuong`: 12 cung · `yeu_to`: phản ứng của các sao · `phuong_phap`: nhận thức rõ ràng
  - **Quote:** _Có thể thấy, cần phải nhận thức một cách rõ ràng phản ứng của các sao ở 12 cung, sau đó mới có thể luận đoán một cách chính xác..._

- **Q:** Làm thế nào để áp dụng linh hoạt các phản ứng cung trong thực tế theo phái Trung Châu Vương Đình Chí?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Làm thế nào để áp dụng linh hoạt các phản ứng cung trong thực tế?
  - **IDs:** `phai`: Trung Châu Vương Đình Chí · `phuong_phap`: dung hợp linh hoạt · `doi_tuong`: phản ứng cung
  - **Quote:** _Nếu có thể dung hợp một cách linh hoạt với những điều đã trình bày ở các chương trước, bạn đọc sẽ hiểu được yếu chỉ của cách luận đoán Đẩu Số theo phương pháp của phái Trung Châu Vương Đình Chí...._

---

## 📄 trung-chau-tu-vi-dau-so-2 · p0575 — `Thiên Cơ Tỵ/Hợi`

**Archetype:** `luan_giai+kinh_nghiem` | **Format:** `ket_qua` | **18 atoms**

**Knowledge Categories (LLM tự propose — bottom-up):**
- Luận giải Thiên Cơ cung Tị/Hợi về hôn nhân/bạn đời
- Luận giải cung hạn then chốt cho Thiên Cơ cung Tị/Hợi
- Luận giải Thiên Cơ cung Phu Thê
- Luận giải Thái Dương cung Tí trong cung Phu Thê
- Ảnh hưởng của sao Hóa Kỵ (Thái Dương, Cự Môn) đến hôn nhân nam/nữ mệnh
- Điều kiện cát tinh hội hợp biến nguy thành an trong hôn nhân

**Chunk preview:**
> <!-- page 575 -->  Thiên Cơ ở hai cung Tị hoặc Hợi, gặp Văn Xương, Văn Khúc, lại hội hợp các sao Đào Hoa, chủ về người bạn đời đã bị người khác theo đuổi. Cho nên, nếu gặp thêm các sao sát, kỵ, hình, sẽ chủ về vợ chổng giữa chừng chia tay. Trường hợp...

### 🎯 Luận giải Thiên Cơ cung Tị/Hợi về hôn nhân/bạn đời (4 atoms)

- **Q:** Thiên Cơ ở cung Tị hoặc Hợi gặp Văn Xương, Văn Khúc, Đào Hoa có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ ở cung Tị hoặc Hợi gặp Văn Xương, Văn Khúc, Đào Hoa có ý nghĩa gì?
  - **IDs:** `sao`: Thiên Cơ · `cung`: Tị/Hợi · `sao_kiem_tra`: Văn Xương, Văn Khúc, Đào Hoa
  - **Quote:** _Thiên Cơ ở hai cung Tị hoặc Hợi, gặp Văn Xương, Văn Khúc, lại hội hợp các sao Đào Hoa, chủ về người bạn đời đã bị người khác theo đuổi...._

- **Q:** Thiên Cơ Tị/Hợi gặp sao sát, kỵ, hình trong hôn nhân có điều gì bất lợi?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ Tị/Hợi gặp sao sát, kỵ, hình trong hôn nhân có điều gì bất lợi?
  - **IDs:** `sao`: Thiên Cơ · `cung`: Tị/Hợi · `sao_kiem_tra`: sao sát, kỵ, hình
  - **Quote:** _nếu gặp thêm các sao sát, kỵ, hình, sẽ chủ về vợ chổng giữa chừng chia tay...._

- **Q:** Thiên Cơ Tị/Hợi hội Thiên Đồng Hóa Lộc, Cự Môn Hóa Kỵ có tác động gì đến hôn nhân?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ Tị/Hợi hội Thiên Đồng Hóa Lộc, Cự Môn Hóa Kỵ có tác động gì đến hôn nhân?
  - **IDs:** `sao`: Thiên Cơ · `cung`: Tị/Hợi · `sao_kiem_tra`: Thiên Đồng Hóa Lộc, Cự Môn Hóa Kỵ
  - **Quote:** _Thiên Cơ ở hai cung Tị hoặc Hợi, nếu hội Thiên Đồng Hóa Lộc, Cự Môn Hóa Kỵ, thì bản thân mệnh tạo sau khi kết hôn dễ thay lòng đổi dạ, có người khác...._

- **Q:** Nữ mệnh Thiên Cơ Tị/Hợi gặp Thái Dương Hóa Kỵ và sao sát tinh có hậu quả gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Nữ mệnh Thiên Cơ Tị/Hợi gặp Thái Dương Hóa Kỵ và sao sát tinh có hậu quả gì?
  - **IDs:** `sao`: Thiên Cơ, Thái Dương Hóa Kỵ · `cung`: Tị/Hợi · `gioi_tinh`: nữ · `sao_kiem_tra`: sao sát tinh
  - **Quote:** _Nữ mệnh, hội Thái Dương Hóa Kỵ, gặp các sao sát tinh, chủ về sinh li với người bạn đời...._

### 🎯 Luận giải cung hạn then chốt cho Thiên Cơ cung Tị/Hợi (2 atoms)

- **Q:** Các cung hạn nào được coi là then chốt cho Thiên Cơ ở Tị/Hợi?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Các cung hạn nào được coi là then chốt cho Thiên Cơ ở Tị/Hợi?
  - **IDs:** `sao`: Thiên Cơ · `cung`: Tị/Hợi · `cung_han`: Thái Dương, Thiên Lương, Thiên Đồng Cự Môn, Phá Quân
  - **Quote:** _Đối với Thiên Cơ ở hai cung Tị hoặc Hợi, các cung hạn "Thái Dương, Thiên Lương", "Thiên Đồng Cự Môn", Phá Quân, là đại vận hoặc lưu niên có tính then chốt, ứng nghiệm cát hung...._

- **Q:** Cung hạn Thái Dương, Thiên Lương ứng nghiệm gì cho Thiên Cơ Tị/Hợi?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Cung hạn Thái Dương, Thiên Lương ứng nghiệm gì cho Thiên Cơ Tị/Hợi?
  - **IDs:** `sao`: Thiên Cơ · `cung`: Tị/Hợi · `cung_han`: Thái Dương, Thiên Lương
  - **Quote:** _các cung hạn "Thái Dương, Thiên Lương", "Thiên Đồng Cự Môn", Phá Quân, là đại vận hoặc lưu niên có tính then chốt, ứng nghiệm cát hung...._

### 🎯 Luận giải Thiên Cơ cung Phu Thê (3 atoms)

- **Q:** Thiên Cơ ở cung Phu Thê có đặc điểm gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ ở cung Phu Thê có đặc điểm gì?
  - **IDs:** `sao`: Thiên Cơ · `cung`: Phu Thê
  - **Quote:** _Về cơ bản là bất lợi...._

- **Q:** Thiên Cơ Phu Thê đối nhau hoặc đồng độ với Thái Âm, gặp cát tinh có kết quả gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ Phu Thê đối nhau hoặc đồng độ với Thái Âm có kết quả gì?
  - **IDs:** `sao`: Thiên Cơ, Thái Âm · `cung`: Phu Thê · `sao_kiem_tra`: cát tinh
  - **Quote:** _Nhưng trong tình hình đối nhau hoặc đồng độ với Thái Âm, gặp cát tinh, mới sống với nhau đến bạc đầu...._

- **Q:** Thiên Cơ Phu Thê gặp Thiên Đồng hay Cự Môn Hóa Kỵ có vấn đề gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ Phu Thê gặp Thiên Đồng hay Cự Môn Hóa Kỵ có vấn đề gì?
  - **IDs:** `sao`: Thiên Cơ · `cung`: Phu Thê · `sao_kiem_tra`: Thiên Đồng, Cự Môn Hóa Kỵ
  - **Quote:** _Thiên Cơ ở cung Phu Thê, rất ngại Thiên Đồng hay Cự Môn Hóa Kỵ, đều chủ về rắc rối khó xử về tình cảm, cổ đại cho rằng nữ mệnh là mạng tì thiếp...._

### 🎯 Luận giải Thái Dương cung Tí trong cung Phu Thê (4 atoms)

- **Q:** Thái Dương ở cung Tí trong Phu Thê có đặc điểm gì về bạn đời?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thái Dương ở cung Tí trong Phu Thê có đặc điểm gì về bạn đời?
  - **IDs:** `sao`: Thái Dương · `cung`: Tí · `cung_phu_the`: Phu Thê
  - **Quote:** _Phần nhiều người bạn đời có tính soi bói, bới móc, gặp Hỏa Tinh, Linh Tinh thì càng nặng...._

- **Q:** Thái Dương Tí gặp Hỏa Tinh, Linh Tinh có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thái Dương Tí gặp Hỏa Tinh, Linh Tinh có ý nghĩa gì?
  - **IDs:** `sao`: Thái Dương · `cung`: Tí · `sao_kiem_tra`: Hỏa Tinh, Linh Tinh
  - **Quote:** _gặp Hỏa Tinh, Linh Tinh thì càng nặng...._

- **Q:** Thái Dương Tí có Địa Không, Địa Kiếp đồng độ có kết quả gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thái Dương Tí có Địa Không, Địa Kiếp đồng độ có kết quả gì?
  - **IDs:** `sao`: Thái Dương · `cung`: Tí · `sao_kiem_tra`: Địa Không, Địa Kiếp
  - **Quote:** _Nếu có Địa Không, Địa Kiếp đồng độ, thì thường thường kết hôn muộn, hoặc tuy có hôn ước nhưng khó kết hợp...._

- **Q:** Thái Dương Hóa Lộc ở cung Tí kết hợp Lộc Tồn, Thiên Mã ở cung Thân có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thái Dương Hóa Lộc ở cung Tí kết hợp Lộc Tồn, Thiên Mã ở cung Thân có ý nghĩa gì?
  - **IDs:** `sao`: Thái Dương Hóa Lộc, Lộc Tồn, Thiên Mã · `cung`: Tí, Thân
  - **Quote:** _Nhưng có Lộc Tồn, Thiên Mã ở cung Thân, Thái Dương Hóa Lộc, sẽ chủ về nhân duyên ở xứ người, vẫn nên kết hôn muộn...._

### 🎯 Ảnh hưởng của sao Hóa Kỵ (Thái Dương, Cự Môn) đến hôn nhân nam/nữ mệnh (3 atoms)

- **Q:** Nữ mệnh cung Phu Thê là Thái Dương Hóa Kỵ ở cung Tí có đặc điểm gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Nữ mệnh Thái Dương Hóa Kỵ ở cung Tí trong Phu Thê có đặc điểm gì?
  - **IDs:** `sao`: Thái Dương Hóa Kỵ · `cung`: Tí, Phu Thê · `gioi_tinh`: nữ
  - **Quote:** _Cung Mệnh của đại hạn đến cung Tí, thường thường hôn nhân bất lợi, chủ về sinh li, hoặc gặp rắc rối về tình cảm, ảnh hưởng rất sâu nặng...._

- **Q:** Nam mệnh cung Phu Thê là Thái Dương Hóa Kỵ ở cung Tí có đặc điểm gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Nam mệnh Thái Dương Hóa Kỵ ở cung Tí trong Phu Thê có đặc điểm gì?
  - **IDs:** `sao`: Thái Dương Hóa Kỵ · `cung`: Tí, Phu Thê · `gioi_tinh`: nam
  - **Quote:** _Sau 30 tuổi dễ thay lòng đổi dạ...._

- **Q:** Người sinh ban đêm khi gặp Thái Dương Hóa Kỵ ở cung Tí có ảnh hưởng nặng hơn không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Người sinh ban đêm có ảnh hưởng nặng hơn không khi gặp Thái Dương Hóa Kỵ?
  - **IDs:** `sao`: Thái Dương Hóa Kỵ · `cung`: Tí · `thoi_gian`: ban đêm
  - **Quote:** _Người sinh vào ban đêm thì càng nặng...._

### 🎯 Điều kiện cát tinh hội hợp biến nguy thành an trong hôn nhân (2 atoms)

- **Q:** Thiên Cơ Tị/Hợi gặp cát hóa, Tả Phụ, Hữu Bật, Thiên Khôi, Thiên Việt có kết quả gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ Tị/Hợi gặp cát hóa, Tả Phụ, Hữu Bật, Thiên Khôi, Thiên Việt có kết quả gì?
  - **IDs:** `sao`: Thiên Cơ · `cung`: Tị/Hợi · `sao_kiem_tra`: Tả Phụ, Hữu Bật, Thiên Khôi, Thiên Việt, cát hóa
  - **Quote:** _Trường hợp có cát hóa, gặp Tả Phụ, Hữu Bật, Thiên Khôi, Thiên Việt, sẽ chủ về người bạn đời giỏi giang, có thể lập nên sự nghiệp...._

- **Q:** Điều kiện nào để Thiên Cơ Phu Thê sống với nhau đến bạc đầu?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Điều kiện nào để Thiên Cơ Phu Thê sống với nhau đến bạc đầu?
  - **IDs:** `sao`: Thiên Cơ · `cung`: Phu Thê · `sao_kiem_tra`: Thái Âm, cát tinh
  - **Quote:** _Nhưng trong tình hình đối nhau hoặc đồng độ với Thái Âm, gặp cát tinh, mới sống với nhau đến bạc đầu...._

---

## 📄 tu-vi-dau-so-toan-thu-vu-tai-luc · p0050 — `BẢNG cặp sao hợp chiếu`

**Archetype:** `chu_the+luan_giai+to_hop+kinh_nghiem` | **Format:** `nguyen_ly` | **21 atoms**

**Knowledge Categories (LLM tự propose — bottom-up):**
- định nghĩa tính chất sao Hóa Kỵ (đa quản chỉ thần, hành Thủy)
- các cặp sao hợp chiếu tốt (Khoa Quyền Lộc hợp chiếu)
- miếu địa và vượng địa của sao Hóa Kỵ theo cung
- tác động của Hóa Kỵ đến vận mệnh (thi cử, công danh, tài lộc)
- kinh nghiệm xử trí Hóa Kỵ tại các cung đặc biệt (Tài Bạch, Điền Trạch)
- văn thơ cổ điển về sao Hóa Kỵ

**Chunk preview:**
> <!-- page 50 -->  ### Các Cặp Sao Hợp Chiếu  *   **Khoa Quyền Lộc hợp Phú Quý Song Toàn:** Có cả Khoa, Quyền, Lộc hợp chiếu, giàu sang vẹn cả. *   **Lộc Quyền Mệnh Phùng Hợp Cát Uy Quyền Áp Chúng Tướng Vương Triều:** Có Lộc và Quyền ở Mệnh cùng với c...

### 🎯 định nghĩa tính chất sao Hóa Kỵ (đa quản chỉ thần, hành Thủy) (3 atoms)

- **Q:** Sao Hóa Kỵ là sao gì, có ý nghĩa như thế nào trong Tử Vi?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Sao Hóa Kỵ là sao gì, có ý nghĩa như thế nào trong Tử Vi?
  - **IDs:** `sao`: Hóa Kỵ · `ham`: Thủy · `tinh_chat`: đa quản chỉ thần
  - **Quote:** _Hóa Kỵ là đa quản (2) chỉ thần, ở Thân Mệnh suốt đời bất thuật...._

- **Q:** Tại sao nói Hóa Kỵ là đa quản chỉ thần?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao nói Hóa Kỵ là đa quản chỉ thần?
  - **IDs:** `sao`: Hóa Kỵ · `tinh_chat`: đa quản chỉ thần
  - **Quote:** _Hóa Kỵ là đa quản (2) chỉ thần, ở Thân Mệnh suốt đời bất thuận...._

- **Q:** Hóa Kỵ thuộc hành gì, tính chất ra sao?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Hóa Kỵ thuộc hành gì, tính chất ra sao?
  - **IDs:** `sao`: Hóa Kỵ · `ham`: Thủy
  - **Quote:** _Hóa Kỵ tính chất thuộc hành Thủy...._

### 🎯 các cặp sao hợp chiếu tốt (Khoa Quyền Lộc hợp chiếu) (6 atoms)

- **Q:** Các cặp sao hợp chiếu nào được xem là tốt trong Tử Vi?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Các cặp sao hợp chiếu nào được xem là tốt trong Tử Vi?
  - **IDs:** `doi_tuong`: các cặp sao hợp chiếu
  - **Quote:** _Khoa Quyền Lộc hợp Phú Quý Song Toàn: Có cả Khoa, Quyền, Lộc hợp chiếu, giàu sang vẹn cả...._

- **Q:** Khoa Quyền Lộc hợp Phú Quý Song Toàn có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Khoa Quyền Lộc hợp Phú Quý Song Toàn có ý nghĩa gì?
  - **IDs:** `sao`: Khoa Quyền Lộc · `doi_hop`: Phú Quý Song Toàn · `y_nghia`: giàu sang vẹn cả
  - **Quote:** _Khoa Quyền Lộc hợp Phú Quý Song Toàn: Có cả Khoa, Quyền, Lộc hợp chiếu, giàu sang vẹn cả...._

- **Q:** Lộc Quyền Mệnh Phùng Hợp Cát Uy Quyền Áp Chúng Tướng Vương Triều mang lại kết quả gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Lộc Quyền Mệnh Phùng Hợp Cát Uy Quyền Áp Chúng Tướng Vương Triều mang lại kết quả gì?
  - **IDs:** `sao`: Lộc Quyền · `cung`: Mệnh · `y_nghia`: uy quyền hơn người làm tướng trong cung vua
  - **Quote:** _Lộc Quyền Mệnh Phùng Hợp Cát Uy Quyền Áp Chúng Tướng Vương Triều: Có Lộc và Quyền ở Mệnh cùng với các sao tốt khác, uy quyền hơn người làm tướng trong cung vua...._

- **Q:** Quyền Lộc Trùng Phùng Tài Quan Song Mỹ có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Quyền Lộc Trùng Phùng Tài Quan Song Mỹ có ý nghĩa gì?
  - **IDs:** `sao`: Quyền Lộc · `y_nghia`: tiền nhiều chức lớn
  - **Quote:** _Quyền Lộc Trùng Phùng Tài Quan Song Mỹ: Gặp Quyền Lộc tiền nhiều chức lớn...._

- **Q:** Quyền Lộc giữ cung Tài Bạch mang lại ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Quyền Lộc giữ cung Tài Bạch mang lại ý nghĩa gì?
  - **IDs:** `sao`: Quyền Lộc · `cung`: Tài Bạch · `y_nghia`: phúc đức người hào phóng, sang giàu
  - **Quote:** _Quyền Lộc Thủ Tài Phúc Chỉ Vị Xử Thế Vinh Hoa: Quyền Lộc giữ cung Tài Bạch, phúc đức người hào phóng, sang giàu...._

- **Q:** Quyền Lộc đóng vào cung Nô Bộc có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Quyền Lộc đóng vào cung Nô Bộc có ý nghĩa gì?
  - **IDs:** `sao`: Quyền Lộc · `cung`: Nô Bộc · `y_nghia`: làm quan thì cũng khốn khổ, đôn đáo
  - **Quote:** _Quyền Lộc Cát Tỉnh Nô Bộc Vị, Túng Nhiên Quan Quý Đã Bôn Trì: Quyền Lộc đóng vào cung Nô Bộc nếu có được làm quan thì cũng khốn khổ, đôn đáo...._

### 🎯 miếu địa và vượng địa của sao Hóa Kỵ theo cung (3 atoms)

- **Q:** Hóa Kỵ ở cung nào được gọi là nhập miếu (miếu địa)?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Hóa Kỵ ở cung nào được gọi là nhập miếu (miếu địa)?
  - **IDs:** `sao`: Hóa Kỵ · `mieu_dia`: Tý, Hợi
  - **Quote:** _Miếu địa của sao Hóa Kỵ là hai cung Tý, Hợi...._

- **Q:** Cung nào là vượng địa của sao Hóa Kỵ?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Cung nào là vượng địa của sao Hóa Kỵ?
  - **IDs:** `sao`: Hóa Kỵ · `vuong_dia`: Dần, Mão, Dậu, Thân
  - **Quote:** _Vượng địa của nó cũng ở các cung Dần, Mão, Dậu, Thân...._

- **Q:** Tại sao Tý Hợi là miếu địa của Hóa Kỵ?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao Tý Hợi là miếu địa của Hóa Kỵ?
  - **IDs:** `sao`: Hóa Kỵ · `cung`: Tý, Hợi · `loai`: miếu địa
  - **Quote:** _Miếu địa của sao Hóa Kỵ là hai cung Tý, Hợi...._

### 🎯 tác động của Hóa Kỵ đến vận mệnh (thi cử, công danh, tài lộc) (3 atoms)

- **Q:** Sao Hóa Kỵ ảnh hưởng như thế nào đến thi cử và công danh?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Sao Hóa Kỵ ảnh hưởng như thế nào đến thi cử và công danh?
  - **IDs:** `sao`: Hóa Kỵ · `tac_dong`: thi cử, công danh
  - **Quote:** _Tiểu Hạn gặp Hóa Kỵ một năm làm ăn không hay, Đại Hạn thì 10 năm lận đận...._

- **Q:** Khi gặp Hóa Kỵ trong Tiểu Hạn và Đại Hạn có khác nhau không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Khi gặp Hóa Kỵ trong Tiểu Hạn và Đại Hạn có khác nhau không?
  - **IDs:** `sao`: Hóa Kỵ · `han`: Tiểu Hạn, Đại Hạn
  - **Quote:** _Tiểu Hạn gặp Hóa Kỵ một năm làm ăn không hay, Đại Hạn thì 10 năm lận đận...._

- **Q:** Hóa Kỵ gặp Tứ Sát thì hậu quả ra sao?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Hóa Kỵ gặp Tứ Sát thì hậu quả ra sao?
  - **IDs:** `sao`: Hóa Kỵ · `sao_gap`: Tứ Sát · `tac_dong`: phá phách, công danh tiền bạc chẳng mặt nào khá
  - **Quote:** _Nếu gặp luôn Tứ Sát hợp lại phá phách thì cả công danh lẫn tiền bạc chẳng mặt nào khá...._

### 🎯 kinh nghiệm xử trí Hóa Kỵ tại các cung đặc biệt (Tài Bạch, Điền Trạch) (3 atoms)

- **Q:** Hóa Kỵ ở cung Tài Bạch hoặc Điền Trạch có xấu không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Hóa Kỵ ở cung Tài Bạch hoặc Điền Trạch có xấu không?
  - **IDs:** `sao`: Hóa Kỵ · `cung`: Tài Bạch, Điền Trạch · `danh_gia`: rất đắc dụng, thần giữ cửa giỏi giang
  - **Quote:** _Ví dụ nó ở vào hai cung Tài Bạch và Điền Trạch lại rất đắc dụng, một thứ thần giữ cửa giỏi giang...._

- **Q:** Hóa Kỵ hội với Hóa Quyền có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Hóa Kỵ hội với Hóa Quyền có ý nghĩa gì?
  - **IDs:** `sao`: Hóa Kỵ · `sao_hoi`: Hóa Quyền · `ket_qua`: biến thành người mưu lược
  - **Quote:** _Nó hội với Hóa Quyền lập tức biến thành người mưu lược...._

- **Q:** Hóa Kỵ gặp Thanh Long, Long Đức được xử lý như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Hóa Kỵ gặp Thanh Long, Long Đức được xử lý như thế nào?
  - **IDs:** `sao`: Hóa Kỵ · `sao_hoi`: Thanh Long, Long Đức · `ket_qua`: biến ra đám mây che chở cho rồng vùng vẫy
  - **Quote:** _hội với Thanh Long, Long Đức biến ra đám mây che chở cho rồng vùng vẫy...._

### 🎯 văn thơ cổ điển về sao Hóa Kỵ (3 atoms)

- **Q:** Câu thơ 'Kị tỉnh nhập miếu phần vi giai' nghĩa là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Câu thơ 'Kị tỉnh nhập miếu phần vi giai' nghĩa là gì?
  - **IDs:** `cau_tho`: Kị tỉnh nhập miếu phần vi giai · `y_nghia`: Sao Hóa Kỵ nhập miếu lại thành hay
  - **Quote:** _Kị tỉnh nhập miếu phần vi giai - Nghĩa là: Sao Hóa Kỵ nhập miếu lại thành hay, dù có gặp tai hoạ cũng chẳng hề hấn gì...._

- **Q:** Câu 'Túng hữu quan tai diệc bất thương' trong Tử Vi Đẩu Số Toàn Thư giải thích điều gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Câu 'Túng hữu quan tai diệc bất thương' trong Tử Vi Đẩu Số Toàn Thư giải thích điều gì?
  - **IDs:** `cau_tho`: Túng hữu quan tai diệc bất thương · `y_nghia`: dù có gặp tai hoạ cũng chẳng hề hấn gì
  - **Quote:** _Túng hữu quan tai diệc bất thương - Nghĩa là: Sao Hóa Kỵ nhập miếu lại thành hay, dù có gặp tai hoạ cũng chẳng hề hấn gì...._

- **Q:** Câu phú 'Hóa Kị chính sao Kế Đò' của tiền nhân Việt nói gì về Hóa Kỵ?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Câu phú 'Hóa Kị chính sao Kế Đò' của tiền nhân Việt nói gì về Hóa Kỵ?
  - **IDs:** `cau_tho`: Hóa Kị chính sao Kế Đò · `tac_gia`: tiền nhân Việt · `y_nghia`: Am trần cơ sảo mưu đồ cạnh tranh
  - **Quote:** _Hóa Kị chính sao Kế Đò - Am trần cơ sảo mưu đồ cạnh tranh..._

---

## 📄 tu-vi-dau-so-toan-thu-vu-tai-luc · p0100 — `THƠ PHÚ Vũ Khúc Nhập Hạn`

**Archetype:** `luan_giai+kinh_nghiem` | **Format:** `tho_phu` | **19 atoms**

**Knowledge Categories (LLM tự propose — bottom-up):**
- ý nghĩa Vũ Khúc Nhập Hạn trong tử vi
- ý nghĩa Thái Âm Nhập Hạn trong tử vi
- ý nghĩa Tham Lang Nhập Hạn trong tử vi
- quy tắc Hóa Khoa Quyển Lộc khi nhập hạn
- tác động sao Hỏa Tinh/Linh Tinh/Dương Đà khi gặp Thái Âm hãm địa

**Chunk preview:**
> <!-- page 100 -->  ## Tử Vi Đầu Số Toàn Thư ~ Vũ Tài Lục 90  ### **Vũ Khúc Nhập Hạn** Thả dả nhuận thân tịnh nhuận ốc, Nam Đẩu tôn tinh nhập hạn lai. Sở vi mưu sự xứng tâm hoài, nhược hoàn hựu Hóa Khoa Quyển Lộc, chỉ nhận hân nhiên triển đại tài.  **...

### 🎯 ý nghĩa Vũ Khúc Nhập Hạn trong tử vi (4 atoms)

- **Q:** Câu phú 'Thả dả nhuận thân tịnh nhuận ốc' nghĩa Việt là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Câu phú 'Thả dả nhuận thân tịnh nhuận ốc' nghĩa Việt là gì?
  - **IDs:** `sao`: Vũ Khúc · `cung`: Hạn
  - **Quote:** _Hạn đến sao Thiên Phủ chủ về tài lộc, kẻ sĩ cũng như thứ nhân đều hay, thêm tiền thêm mừng vui vô tai họa, ấm thân xây cao nhà cửa...._

- **Q:** Vũ Khúc Nhập Hạn có ý nghĩa gì về tài lộc?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Vũ Khúc Nhập Hạn có ý nghĩa gì về tài lộc?
  - **IDs:** `sao`: Vũ Khúc · `cung`: Hạn · `tai_loc`: tài lộc
  - **Quote:** _Hạn đến sao Thiên Phủ chủ về tài lộc, kẻ sĩ cũng như thứ nhân đều hay, thêm tiền thêm mừng vui vô tai họa, ấm thân xây cao nhà cửa...._

- **Q:** 'Tam Hóa Khoa Quyển Lộc' được nhắc đến trong đoạn có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ 'Tam Hóa Khoa Quyển Lộc' trong câu phú này là gì?
  - **IDs:** `sao`: Tam Hóa · `chi_tiet`: Khoa Quyển Lộc
  - **Quote:** _nếu có cả tam Hóa Khoa Quyển Lộc nữa thì có thể định ngày phát triển tài năng sẵn có..._

- **Q:** Điều kiện nào để Vũ Khúc Nhập Hạn có thể định ngày phát tài?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Điều kiện nào để Vũ Khúc Nhập Hạn 'phát triển tài năng sẵn có'?
  - **IDs:** `sao`: Vũ Khúc · `cung`: Hạn · `dieu_kien`: Tam Hóa Khoa Quyển Lộc
  - **Quote:** _nếu có cả tam Hóa Khoa Quyển Lộc nữa thì có thể định ngày phát triển tài năng sẵn có..._

### 🎯 ý nghĩa Thái Âm Nhập Hạn trong tử vi (3 atoms)

- **Q:** Câu phú 'Thái Âm tỉnh hạn trùng phùng' nghĩa Việt là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Câu phú 'Thái Âm tỉnh hạn trùng phùng' nghĩa là gì?
  - **IDs:** `sao`: Thái Âm · `cung`: Hạn
  - **Quote:** _Hạn đến Thái Âm, tài lộc nhiễu mưu việc tốt, lấy vợ lấy chồng đẻ con thêm đỉnh thêm tài, nhà cửa hưng vượng...._

- **Q:** Thái Âm Nhập Hạn có tác động gì đến việc cưới hỏi sinh con?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thái Âm Nhập Hạn có tác động gì đến việc cưới hỏi sinh con?
  - **IDs:** `sao`: Thái Âm · `cung`: Hạn · `su_kien`: cưới hỏi sinh con
  - **Quote:** _lấy vợ lấy chồng đẻ con thêm đỉnh thêm tài, nhà cửa hưng vượng..._

- **Q:** 'Thái Âm cư phản bội' nghĩa là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ 'Thái Âm cư phản bội' nghĩa là gì?
  - **IDs:** `sao`: Thái Âm · `cung`: Hạn · `trang_thai`: hãm địa
  - **Quote:** _Hạn mà gặp Thái Âm hãm địa (phản bội) lại thêm Dương Đà, Linh Hỏa nữa thì rất nguy hiểm..._

### 🎯 tác động sao Hỏa Tinh/Linh Tinh/Dương Đà khi gặp Thái Âm hãm địa (5 atoms)

- **Q:** Thái Âm Nhập Hạn khi gặp Hỏa Tinh, Linh Tinh có xấu không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thái Âm Nhập Hạn khi gặp Hỏa Tinh/Linh Tinh có xấu không?
  - **IDs:** `sao`: Thái Âm · `cung`: Hạn · `sao_xau`: Hỏa Tinh, Linh Tinh
  - **Quote:** _Đại Tiểu Hạn nên gặp Thái Âm phúc lộc không ít nhưng chớ có Hỏa Tinh, Linh Tinh mới được nếu có tất bị tai ách bệnh hoạn..._

- **Q:** Tại sao Hỏa Tinh gặp Thái Âm lại bệnh hoạn?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao Hỏa Tinh gặp Thái Âm lại 'bệnh hoạn lắm'?
  - **IDs:** `sao`: Hỏa Tinh · `cung`: Hạn · `sao_gap`: Thái Âm
  - **Quote:** _Đại Tiểu Hạn nên gặp Thái Âm phúc lộc không ít nhưng chớ có Hỏa Tinh, Linh Tinh mới được nếu có tất bị tai ách bệnh hoạn..._

- **Q:** 'Dương Đà tam sát hội' trong câu phú nghĩa là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ 'Dương Đà tam sát hội' trong câu phú nghĩa là gì?
  - **IDs:** `sao`: Dương Đà · `cung`: Hạn · `tam_sat`: Hỏa Tinh, Linh Tinh
  - **Quote:** _Hạn mà gặp Thái Âm hãm địa (phản bội) lại thêm Dương Đà, Linh Hỏa nữa thì rất nguy hiểm..._

- **Q:** Hạn gặp Thái Âm hãm địa cộng Dương Đà, Linh Hỏa có nguy hiểm không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Hạn gặp Thái Âm hãm địa cộng Dương Đà/Linh Hỏa có nguy hiểm không?
  - **IDs:** `sao`: Thái Âm · `cung`: Hạn · `trang_thai`: hãm địa · `sao_ghep`: Dương Đà, Linh Hỏa
  - **Quote:** _Hạn mà gặp Thái Âm hãm địa (phản bội) lại thêm Dương Đà, Linh Hỏa nữa thì rất nguy hiểm..._

- **Q:** Sao nào được coi là hung nhất khi Thái Âm Nhập Hạn?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Sao nào được coi là 'hung' nhất trong Thái Âm Nhập Hạn?
  - **IDs:** `sao`: Thái Âm · `cung`: Hạn · `sao_hung_nhat`: Hỏa Tinh, Dương Đà
  - **Quote:** _Hỏa Tinh nhị hạn tối vi hung, ngược bất quan tai đa phá hối. Hạn chí Thái Âm cư phản bội, bất hỉ Dương Đà tam sát hội...._

### 🎯 ý nghĩa Tham Lang Nhập Hạn trong tử vi (4 atoms)

- **Q:** Câu phú 'Bắc Đẩu Tham Lang nhập hạn lai' nghĩa Việt là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Câu phú 'Bắc Đẩu Tham Lang nhập hạn lai' nghĩa Việt là gì?
  - **IDs:** `sao`: Tham Lang · `cung`: Hạn · `vi_tri`: Bắc Đẩu
  - **Quote:** _Tham Lang chủ hạn tứ mộ làm cánh hỉ nhân sinh tứ mộ sinh..._

- **Q:** Tham Lang Nhập Hạn 'miếu' và 'hãm' khác nhau thế nào về kết quả?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang Nhập Hạn 'miếu' và 'hãm' khác nhau thế nào?
  - **IDs:** `sao`: Tham Lang · `cung`: Hạn · `trang_thai`: miếu và hãm
  - **Quote:** _Nhược hoàn nhập miếu sự hài hoà, Khoa Lộc sĩ lộ đa thành tựu, tất chử đương niên phát hoạnh tài. [...] Hạn chí Tham Lang hãm bất lương, chỉ nghỉ tiết dục tức tai thương, đổ đãng phong lưu khứ tài bảo...._

- **Q:** Câu phú 'Tham Lang chủ hạn tứ mộ làm cánh hỉ nhân sinh tứ mộ sinh' có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ 'Tham Lang chủ hạn tứ mộ làm cánh hỉ nhân sinh tứ mộ sinh' có ý nghĩa gì?
  - **IDs:** `sao`: Tham Lang · `cung`: Hạn · `tinh_huong`: tứ mộ
  - **Quote:** _Tham Lang chủ hạn tứ mộ làm cánh hỉ nhân sinh tứ mộ sinh..._

- **Q:** Khi Tham Lang hãm bất lương thì kết quả như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Khi Tham Lang hãm bất lương thì kết quả ra sao?
  - **IDs:** `sao`: Tham Lang · `cung`: Hạn · `trang_thai`: hãm bất lương
  - **Quote:** _Hạn chí Tham Lang hãm bất lương, chỉ nghỉ tiết dục tức tai thương, đổ đãng phong lưu khứ tài bảo..._

### 🎯 quy tắc Hóa Khoa Quyển Lộc khi nhập hạn (3 atoms)

- **Q:** 'Tam Hóa Khoa Quyển Lộc' trong phú thơ có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ 'Hóa Khoa Quyển Lộc' trong phú thơ có ý nghĩa gì?
  - **IDs:** `sao`: Tam Hóa · `chi_tiet`: Khoa Quyển Lộc · `cung`: Hạn
  - **Quote:** _nếu có cả tam Hóa Khoa Quyển Lộc nữa thì có thể định ngày phát triển tài năng sẵn có..._

- **Q:** Tại sao có 'Tam Hóa Khoa Quyển Lộc' thì có thể định ngày phát tài?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao có 'Hóa Khoa Quyển Lộc' thì có thể 'định ngày phát tài'?
  - **IDs:** `sao`: Tam Hóa · `chi_tiet`: Khoa Quyển Lộc · `cung`: Hạn · `dieu_kien`: phát tài
  - **Quote:** _nếu có cả tam Hóa Khoa Quyển Lộc nữa thì có thể định ngày phát triển tài năng sẵn có..._

- **Q:** 'Tam Hóa' được nhắc đến trong đoạn là những sao nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ 'Tam Hóa' được nhắc đến trong đoạn là những sao nào?
  - **IDs:** `sao`: Tam Hóa · `chi_tiet`: Khoa Quyển Lộc
  - **Quote:** _nếu có cả tam Hóa Khoa Quyển Lộc nữa thì có thể định ngày phát triển tài năng sẵn có..._

---

## 📄 tu-vi-dau-so-toan-thu-vu-tai-luc · p0150 — `THƠ PHÚ kết quả cứng`

⚠ Pass 1 fail: JSONDecodeError: Expecting ',' delimiter: line 1 column 1276 (char 1275)

## 📄 tu-vi-ham-so · p0100 — `CHỦ THỂ Tham Lang tính cách`

**Archetype:** `chu_the+luan_giai+to_hop+kinh_nghiem` | **Format:** `nguyen_ly` | **23 atoms**

**Knowledge Categories (LLM tự propose — bottom-up):**
- định nghĩa tính cách cơ bản của sao Tham Lang
- ý nghĩa Tham Lang hãm địa - tính cách tiêu cực
- ý nghĩa Tham Lang hãm địa đối với phụ nữ
- ý nghĩa tài lộc công danh khi Tham Lang đắc địa
- ý nghĩa tài lộc công danh khi Tham Lang hãm địa
- phúc thọ tai họa của Tham Lang theo vị trí cung
- cách tốt Tham Lang kết hợp với sao khác

**Chunk preview:**
> <!-- page 100 -->  Lòng tham dục vô bờ bến hay mưu tính những chuyện to lớn.  *   Nóng nảy, làm gì cũng muốn chóng xong, nhưng chỉ chuyên cần siêng năng buổi đầu, rồi về sau sinh lười biếng chán nản, bỏ dở. Tánh bất nhất. *   Thích ăn ngon mặc đẹp, c...

### 🎯 định nghĩa tính cách cơ bản của sao Tham Lang (3 atoms)

- **Q:** Sao Tham Lang đại diện cho tính cách nóng nảy, lười biếng và tham dục như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Sao Tham Lang đại diện cho tính cách gì?
  - **IDs:** `sao`: Tham Lang · `tinh_cach`: ['nong_nay', 'luoi_bieng', 'tham_duc']
  - **Quote:** _Nóng nảy, làm gì cũng muốn chóng xong, nhưng chỉ chuyên cần siêng năng buổi đầu, rồi về sau sinh lười biếng chán nản, bỏ dở. Tánh bất nhất...._

- **Q:** Tại sao Tham Lang được gọi là sao đào hoa và sao dâm dục?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao nói Tham Lang là sao đào hoa, sao dâm dục?
  - **IDs:** `sao`: Tham Lang · `hieu`: dam_duc
  - **Quote:** _Tham Lang vốn là sao đào hoa, sao đào hoa và sao dâm dục. Nếu kèm thêm các Riêu, Mộc, Cái, Đào, Hồng thì đó là hạng play boy, play girl rất hỗn tạp...._

- **Q:** Tham Lang có đặc điểm tính cách thích ăn ngon mặc đẹp, chơi bời cho thỏa chí như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang có những đặc điểm tính cách nào được đề cập trong đoạn này?
  - **IDs:** `sao`: Tham Lang · `tinh_cach`: ['an_ngon_mac_dep', 'choi_boi']
  - **Quote:** _Thích ăn ngon mặc đẹp, chơi bời cho thỏa chí...._

### 🎯 ý nghĩa Tham Lang hãm địa - tính cách tiêu cực (3 atoms)

- **Q:** Tham Lang hãm địa có tính cách gian hiểm, dối trá, ích kỷ, hiểm độc như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang hãm địa có tính cách như thế nào?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `tinh_cach`: ['gian_hiem', 'doi_tra', 'ich_ky', 'hieu_doc']
  - **Quote:** _Gian hiểm, dối trá, ích kỷ, hiểm độc...._

- **Q:** Tham Lang hãm địa có đặc điểm tham lam, nhiều dục vọng, hay ghen tuông như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Người có Tham Lang hãm địa thường có những điểm xấu nào về tính cách?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `tinh_cach`: ['tham_lam', 'duc_vong', 'gen_tulong']
  - **Quote:** _Tham lam, có nhiều dục vọng, hay ghen tuông...._

- **Q:** Tham Lang hãm địa ở Mão Dậu có đặc điểm không quả quyết, không bền chí, yếm thế như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang hãm địa ở Mão Dậu có đặc điểm gì khác biệt?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `cung`: Mao_Dau · `tinh_cach`: ['khong_quan_quyet', 'khong_ben_chi', 'yem_the']
  - **Quote:** _Không quả quyết, không bền chí, yếm thế (Mão Dậu)...._

### 🎯 ý nghĩa Tham Lang hãm địa đối với phụ nữ (3 atoms)

- **Q:** Phụ nữ có Tham Lang hãm địa dễ sa ngã, hư đốn, có chồng mà còn đa mang, ngoại tình như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Phụ nữ có Tham Lang hãm địa thường gặp vấn đề gì trong hôn nhân?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `doi_tuong`: phu_nu · `van_de`: ['sa_nga', 'hu_don', 'ngoai_tinh']
  - **Quote:** _Riêng đối với phụ nữ, người có Tham Lang hãm địa rất dễ sa ngã, hư đốn, có chồng mà còn đa mang, ngoại tình...._

- **Q:** Tham Lang hãm địa kết hợp với Liêm, Đào, Hồng, Mộc, Cái, Riêu, Ky có ý nghĩa gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang hãm địa kết hợp với các sao ái tình dâm dục có ý nghĩa gì?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `ket_hop`: ['Liem', 'Dao', 'Hong', 'Moc', 'Cai', 'Riêu', 'Ky'] · `y_nghia`: gai_giang_ho_tinh_nat dam_dang
  - **Quote:** _Đi kèm với các sao ái tình hay dâm dục khác như Liêm, Đào, Hồng, Mộc, Cái, Riêu, Ky, thì rất có thể là gái giang hồ, hoặc ít nhất tính nết hết sức dâm dãng, bạc tình...._

- **Q:** Tại sao phụ nữ có Tham Lang hãm địa rất dễ sa ngã, hư đốn?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao nói phụ nữ có Tham Lang hãm địa dễ sa ngã, hư đốn?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `doi_tuong`: phu_nu · `tinh_trang`: sa_nga_hu_don
  - **Quote:** _Riêng đối với phụ nữ, người có Tham Lang hãm địa rất dễ sa ngã, hư đốn, có chồng mà còn đa mang, ngoại tình...._

### 🎯 ý nghĩa tài lộc công danh khi Tham Lang đắc địa (3 atoms)

- **Q:** Tham Lang đắc địa có ý nghĩa giàu sang, càng già càng thịnh vượng như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang đắc địa có ý nghĩa gì về tài lộc và công danh?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: dac_dia · `y_nghia_tai_loc`: ['gianh_sang', 'cang_gia_cang_thinh_vuong']
  - **Quote:** _Nếu Tham Lang đắc địa trở lên thì giàu sang. Nhưng vì Tham Lang là sao Bắc Đẩu nên càng già càng thịnh vượng, an nhà, sung sướng...._

- **Q:** Tại sao nói Tham Lang là sao Bắc Đẩu càng già càng thịnh vượng, an nhà, sung sướng?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao nói Tham Lang là sao Bắc Đẩu càng già càng thịnh vượng?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: dac_dia · `danh_hieu`: Bac_Dau · `dac_diem`: ['cang_gia_cang_thinh_vuong', 'an_nha', 'sung_suong']
  - **Quote:** _Nhưng vì Tham Lang là sao Bắc Đẩu nên càng già càng thịnh vượng, an nhà, sung sướng...._

- **Q:** Tham Lang đắc địa đồng cung với Ky có ý nghĩa buôn bán mà giàu có như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang đắc địa đồng cung với Ky có ý nghĩa gì?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: dac_dia · `dong_cung`: Ky · `y_nghia`: buon_ban_giau_co
  - **Quote:** _Nếu đồng cung với Ky thì buôn bán mà giàu có...._

### 🎯 ý nghĩa tài lộc công danh khi Tham Lang hãm địa (3 atoms)

- **Q:** Tham Lang hãm địa có óc kinh doanh thường chuyên mỹ nghệ, thương mại, thủ công nhưng tài lộc, công danh chật vật như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang hãm địa về tài lộc công danh như thế nào?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `nghe_nghiep`: ['my_nghe', 'thuong_mai', 'thu_cong'] · `y_nghia_tai_loc`: chat_vat
  - **Quote:** _Người ấy có óc kinh doanh thường chuyên mỹ nghệ, thương mại, thủ công, nhưng tài lộc, công danh chật vật...._

- **Q:** Tham Lang hãm địa đồng cung với Ky hay Riêu thường bị giam cầm hoặc hay bị tai nạn sông nước như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang hãm địa khi đồng cung với Ky hay Riêu có nguy cơ gì?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `dong_cung`: ['Ky', 'Riêu'] · `nguy_co`: ['giam_cam', 'tai_nan_song_nuoc']
  - **Quote:** _Nhưng dù miếu, vượng, đắc hay hãm địa, hoặc gặp Ky hay Riêu đồng cung, thường bị giam cầm (nếu thiếu sao giải) hoặc hay bị tai nạn sông nước...._

- **Q:** Người có Tham Lang hãm địa có óc kinh doanh thường chuyên nghề gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Người có Tham Lang hãm địa thường làm nghề gì?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `nghe_nghiep`: ['my_nghe', 'thuong_mai', 'thu_cong']
  - **Quote:** _Người ấy có óc kinh doanh thường chuyên mỹ nghệ, thương mại, thủ công, nhưng tài lộc, công danh chật vật...._

### 🎯 phúc thọ tai họa của Tham Lang theo vị trí cung (5 atoms)

- **Q:** Tham Lang đi cùng với ác tinh, sát tinh có hậu quả phá ách, tai họa nhiều thêm như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang kết hợp với ác tinh sát tinh có hậu quả gì?
  - **IDs:** `sao`: Tham Lang · `ket_hop`: ['ac_tinh', 'sat_tinh'] · `hau_qua`: ['pha_ach', 'tai_hoa_nhieu_them']
  - **Quote:** _Nói chung, Tham Lang đi cùng với ác tinh, sát tinh là phá ách, tai họa nhiều thêm...._

- **Q:** Tham Lang hãm địa ắt nhiều bệnh, hay bị giam cầm nếu không bỏ quê hương cầu thực thì yếu, cô độc như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang hãm địa có ảnh hưởng đến sức khỏe như thế nào?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `tac_dong`: ['nhieu_benh', 'giam_cam', 'yeu_con_dong'] · `giai_phap`: bo_que_huong_cau_thuc
  - **Quote:** _Nếu hãm địa, ắt nhiều bệnh, hay bị giam cầm nếu không bỏ quê hương cầu thực thì yếu, cô độc...._

- **Q:** Tham Lang ở Mão Dậu là người yếm thế, làm việc gì cũng thất bại và hay gặp sự chẳng lành như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang ở Mão Dậu gặp những tai họa gì?
  - **IDs:** `sao`: Tham Lang · `cung`: Mao_Dau · `tinh_trang`: ['yem_the', 'that_bai', 'chamg_lanh'] · `chi_huong`: di_tu
  - **Quote:** _Riêng Tham Lang ở Mão Dậu là người yếm thế, làm việc gì cũng thất bại và hay gặp sự chẳng lành. Người này chỉ có chí hướng đi tu...._

- **Q:** Tham Lang hãm địa phải bỏ quê hương cầu thực để tránh yếu, cô độc như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Điều kiện nào Tham Lang hãm địa phải bỏ quê cầu thực?
  - **IDs:** `sao`: Tham Lang · `vi_tri`: hamm_dia · `giai_phap`: bo_que_huong_cau_thuc · `tinh_trang`: ['yeu', 'con_dong']
  - **Quote:** _Nếu hãm địa, ắt nhiều bệnh, hay bị giam cầm nếu không bỏ quê hương cầu thực thì yếu, cô độc...._

- **Q:** Tham Lang ở Mão Dậu gặp thêm sát tinh hay Ky, Hình thì hay bị nạn khủng khiếp, giam cầm và yếu tử như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang hãm địa ở Mão Dậu gặp những tai họa gì khi kết hợp với sát tinh?
  - **IDs:** `sao`: Tham Lang · `cung`: Mao_Dau · `ket_hop`: ['sat_tinh', 'Ky', 'Hinh'] · `hau_qua`: ['nan_khung_bo', 'giam_cam', 'yeu_tu']
  - **Quote:** _Nếu gặp thêm sát tinh hay Ky, Hình thì hay bị nạn khủng khiếp, giam cầm và yếu tử...._

### 🎯 cách tốt Tham Lang kết hợp với sao khác (3 atoms)

- **Q:** Tham Lang hóa đồng cung miếu địa có ý nghĩa phú quý tột bậc, danh tiếng lừng lẫy như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tham Lang hóa đồng cung miếu địa có ý nghĩa gì?
  - **IDs:** `sao`: Tham Lang · `cach`: hoa_dong_cung_mieu_dia · `y_nghia`: ['phu_quy_tot_bac', 'danh_tiem_lung_lay'] · `dac_diem`: hien_dat_ve_vo_nghiep
  - **Quote:** _Tham Lang hóa đồng cung miếu địa hay Tham Lang linh đồng cung miếu địa: phú quý tột bậc, danh tiếng lừng lẫy. Rất hiển đạt về võ nghiệp...._

- **Q:** Tại sao nói Tham Lang sinh ở Dần Thân sống rất lâu?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao nói Tham Lang sinh ở Dần Thân sống rất lâu?
  - **IDs:** `sao`: Tham Lang · `chi`: ['Dan', 'Than'] · `y_nghia`: song_rat_lau
  - **Quote:** _Tham Lang sinh ở Dần Thân: sống rất lâu...._

- **Q:** Cách tốt nhất cho Tham Lang là hóa đồng cung miếu địa áp dụng cho tuổi Mậu Kỷ như thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Cách tốt nhất cho Tham Lang là gì và áp dụng cho tuổi nào?
  - **IDs:** `sao`: Tham Lang · `cach`: hoa_dong_cung_mieu_dia · `tuoi_ap_dung`: Mau_Ky · `y_nghia`: phu_quy_tot_bac
  - **Quote:** _Rất tốt cho hai tuổi Mậu Kỷ vì ứng hợp với cách này...._

---

## 📄 tu-vi-nghiem-ly-toan-thu-thien-luong · p0150 — `KINH NGHIỆM Thiên Lương Kim Cục`

**Archetype:** `chu_the+luan_giai+kinh_nghiem` | **Format:** `nguyen_ly` | **16 atoms**

**Knowledge Categories (LLM tự propose — bottom-up):**
- định nghĩa 14 chính tinh chia âm dương và tỷ lệ lực lượng 3/2
- định nghĩa bộ Tử Phủ và Phá Tham thuộc Tứ Tượng dương
- nguyên lý luận giải mệnh theo giai đoạn tuổi (Mệnh làm đích từ 20-40, Cục từ 40 về già)
- ý nghĩa vòng Tràng Sinh: Sinh Vượng Mộ vs Đức Suy Tuyệt
- tương tác giữa Thái Dương-Thái Âm với Thiên Lương-Cự Môn-Thiên Cơ-Thiên Đồng

**Chunk preview:**
> <!-- page 150 -->  # TỬ VI NGHIỆM LÝ TOÀN THƯ THIÊN LƯƠNG  **Mệnh** tuy đẹp không được **Sinh Vượng Mộ** giúp đỡ vì Kim Cục chỉ dành cho người âm nữ ở Dậu, Sửu. Tuy vậy đến đại vận gặp **Sinh Vượng Mộ** tuổi Canh Tuất cũng được tô điểm phân, nhưng th...

### 🎯 định nghĩa 14 chính tinh chia âm dương và tỷ lệ lực lượng 3/2 (3 atoms)

- **Q:** 14 chính tinh bên dương gồm những sao nào, bên âm gồm những sao nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ 14 chính tinh bên dương gồm những sao nào, bên âm gồm những sao nào?
  - **IDs:** `sao`: Tử Phủ, Vũ Khúc, Thiên Tướng, Phá Quân, Tham Lang, Liêm Trinh (dương); Cơ, Nguyệt, Thiên Lương, Cự Môn (âm) · `loai`: 14 chính tinh
  - **Quote:** _bên dương có Tử Phủ, Vũ Khúc, Thiên Tướng và Phá Quân, Tham Lang, Liêm Trinh, bên âm gồm Cơ, Nguyệt, Thiên Lương và Cự Môn..._

- **Q:** Tại sao 14 chính tinh chia bên dương 8 sao, bên âm chỉ có 6 sao?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao 14 chính tinh chia bên dương 8 sao, bên âm 6 sao?
  - **IDs:** `sao`: 14 chính tinh · `so_luong`: {'duong': 8, 'am': 6} · `ly_do`: thực lực bên dương luôn luôn mạnh hơn âm bằng tỷ số tương đối 3/2, bằng số 8 để chia cho hai bộ Tử Phủ và Phá Tham có lực lượng bằng nhau
  - **Quote:** _Tại sao 14 chính tinh lại chia cho bên dương những 8 mà bên âm chỉ có 6? Trên hình thức lưỡng nghi âm dương hình tượng bằng nhau, nhưng thực lực bên dương luôn luôn mạnh hơn âm bằng tỷ số tương đối 3/..._

- **Q:** Tỷ số lực lượng âm dương 3/2 có nghĩa gì trong luận đoán?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tỷ số lực lượng âm dương 3/2 có nghĩa gì trong luận đoán?
  - **IDs:** `he_so`: 3/2 · `y_nghia`: thực lực bên dương luôn luôn mạnh hơn âm
  - **Quote:** _nhưng thực lực bên dương luôn luôn mạnh hơn âm bằng tỷ số tương đối 3/2..._

### 🎯 định nghĩa bộ Tử Phủ và Phá Tham thuộc Tứ Tượng dương (3 atoms)

- **Q:** Bộ Tử Phủ và Phá Tham có đặc điểm gì chung?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Bộ Tử Phủ và Phá Tham có đặc điểm gì chung?
  - **IDs:** `bo_sao`: Tử Phủ, Phá Tham · `tuong_tuong`: Tứ Tượng dương · `tinh_cach`: linh động cương quyết · `hanh_dong`: thường xuyên đấu tranh với nhau để thỏa mãn ý muốn
  - **Quote:** _Bộ Tử Phủ và Phá Tham là hai thiên của Tứ Tượng thuộc dương, có tính cách linh động cương quyết, thường xuyên đấu tranh với nhau để thỏa mãn ý muốn..._

- **Q:** Tử Phủ và Phá Tham thuộc Tứ Tượng nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tử Phủ và Phá Tham thuộc Tứ Tượng nào?
  - **IDs:** `bo_sao`: Tử Phủ, Phá Tham · `tuong_tuong`: Tứ Tượng dương
  - **Quote:** _Bộ Tử Phủ và Phá Tham là hai thiên của Tứ Tượng thuộc dương..._

- **Q:** Khi nào Tử Vi xứng Đế ở Ngọ Môn, khi nào Phá Quân lên ngôi bá chủ ở Tý?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Khi nào Tử Vi xứng Đế ở Ngọ Môn, khi nào Phá Quân lên ngôi bá chủ ở Tý?
  - **IDs:** `sao`: Tử Vi, Phá Quân · `vi_tri`: {'Tử_Vi': 'Ngọ Môn', 'Phá_Quân': 'Tý (Bắc phương)'} · `truong_hop`: hai thiên đạt trường hợp tuyệt đối
  - **Quote:** _như khi hai thiên đạt trường hợp tuyệt đối là Tử Vi xứng Đế ở Ngọ Môn hay Phá Quân lên ngôi bá chủ ở Bắc phương (Tý)..._

### 🎯 nguyên lý luận giải mệnh theo giai đoạn tuổi (Mệnh làm đích từ 20-40, Cục từ 40 về già) (4 atoms)

- **Q:** Từ sơ sinh đến 13 tuổi có cần luận giải không?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Từ sơ sinh đến 13 tuổi có cần luận giải không?
  - **IDs:** `do_tuoi`: sơ sinh đến 13 tuổi · `ket_luan`: không đáng kể · `ly_do`: đã có bảng hạn đông niên
  - **Quote:** _từ lúc sơ sinh cho đến 13 tuổi không đáng kể, đã có bảng hạn đông niên..._

- **Q:** Tại sao từ 20 đến gần 40 tuổi được gọi là Mệnh làm đích?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Tại sao từ 20 đến gần 40 tuổi là Mệnh làm đích?
  - **IDs:** `do_tuoi`: 20 đến gần 40 · `ten_goi`: Mệnh làm đích
  - **Quote:** _Từ tuổi Quan Đới (20) cho đến gần 40 là Mệnh làm đích..._

- **Q:** Từ 40 tuổi trở về già luận giải theo Cục có nghĩa là gì?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Từ 40 tuổi trở về già luận giải theo Cục có nghĩa là gì?
  - **IDs:** `do_tuoi`: 40 trở về già · `phuong_phap`: Cục · `y_nghia`: nhận xét theo Cục
  - **Quote:** _Từ 40 đến ngày về già là Cục mà nhận xét..._

- **Q:** Bảng hạn đông niên I1 Mệnh 2 Tài 3 Ách 4 Thê 5 Phúc 6 Quan 7 Nô 8 Di 9 Tử 10 Bào II Phụ 12 Điện áp dụng cho độ tuổi nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Bảng hạn đông niên I1 Mệnh 2 Tài 3 Ách 4 Thê 5 Phúc 6 Quan 7 Nô 8 Di 9 Tử 10 Bào II Phụ 12 Điện áp dụng cho độ tuổi nào?
  - **IDs:** `bang_han`: hạn đông niên · `so_thu_tu`: I1 Mệnh 2 Tài 3 Ách 4 Thê 5 Phúc 6 Quan 7 Nô 8 Di 9 Tử 10 Bào II Phụ 12 Điện · `do_tuoi`: sơ sinh đến 13 tuổi
  - **Quote:** _đã có bảng hạn đông niên (I1 Mệnh 2 Tài 3 Ách 4 Thê 5 Phúc 6 Quan 7 Nô 8 Di 9 Tử 10 Bào II Phụ 12 Điện)..._

### 🎯 ý nghĩa vòng Tràng Sinh: Sinh Vượng Mộ vs Đức Suy Tuyệt (3 atoms)

- **Q:** Vòng Tràng Sinh có mấy mặt âm dương?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Vòng Tràng Sinh có mấy mặt âm dương?
  - **IDs:** `vong`: Tràng Sinh · `mat`: Sinh Vượng Mộ (dương), Đức Suy Tuyệt (âm) · `tong_so`: 2
  - **Quote:** _Vòng Tràng Sinh đã có hai mặt âm dương: Sinh Vượng Mộ và Đức Suy Tuyệt..._

- **Q:** Sinh Vượng Mộ và Đức Suy Tuyệt khác nhau thế nào?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Sinh Vượng Mộ và Đức Suy Tuyệt khác nhau thế nào?
  - **IDs:** `mat_duong`: Sinh Vượng Mộ · `mat_am`: Đức Suy Tuyệt · `vong`: Tràng Sinh · `tinh_chat`: {'Sinh_Vượng_Mộ': 'dương', 'Đức_Suy_Tuyệt': 'âm'}
  - **Quote:** _Vòng Tràng Sinh đã có hai mặt âm dương: Sinh Vượng Mộ và Đức Suy Tuyệt..._

- **Q:** Khi nào Mệnh thuận âm dương thì vòng Tràng Sinh phát huy tác dụng?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Khi nào Mệnh thuận âm dương thì vòng Tràng Sinh phát huy tác dụng?
  - **IDs:** `vong`: Tràng Sinh · `dieu_kien`: Mệnh thuận âm dương, vòng Thái Tuế, vòng Lộc Tồn xếp đặt có ăn ý · `luu_y`: hoặc phải bị trừ cho trúng mức độ chung toàn thể
  - **Quote:** _còn tùy Mệnh có thuận âm dương, vòng Thái Tuế, vòng Lộc Tồn xếp đặt có ăn ý, hay phải bị trừ cho trúng mức độ chung toàn thể..._

### 🎯 tương tác giữa Thái Dương-Thái Âm với Thiên Lương-Cự Môn-Thiên Cơ-Thiên Đồng (3 atoms)

- **Q:** Thái Dương và Thái Âm được ví như gì trong đoạn văn?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thái Dương và Thái Âm được ví như gì trong đoạn văn?
  - **IDs:** `sao`: Thái Dương, Thái Âm · `hinh_anh`: hai ngọn đuốc soi tỏ · `chuc_nang`: soi tỏ bước đường
  - **Quote:** _cặp Thái Dương và Thái Âm là hai ngọn đuốc soi tỏ..._

- **Q:** Thiên Lương và Cự Môn trong trường hợp nào cũng nắm chắc trong tay?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Lương và Cự Môn trong trường hợp nào cũng nắm chắc trong tay?
  - **IDs:** `sao`: Thiên Lương, Cự Môn · `dac_diem`: trường hợp nào cũng nắm chắc trong tay
  - **Quote:** _Thiên Lương và Cự Môn trường hợp nào cũng nắm chắc trong tay..._

- **Q:** Thiên Cơ và Thiên Đồng có vai trò gì trong cách cục?  `[ ] ✅ ⚠ ❌`
  - _Template:_ Thiên Cơ và Thiên Đồng có vai trò gì trong cách cục?
  - **IDs:** `Thiên_Cơ`: tất cả những gì cầu tạo tổ chức quản lý hành động · `Thiên_Đồng`: kế hoạch cải cách kiên tạo
  - **Quote:** _Thiên Cơ là tất cả những gì cầu tạo tổ chức quản lý hành động và Thiên Đồng là kế hoạch cải cách kiên tạo..._

---
