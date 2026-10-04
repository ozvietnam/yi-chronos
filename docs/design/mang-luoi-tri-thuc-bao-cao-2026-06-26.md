# Báo cáo: Mạng lưới tri thức "như não" — thực trạng & hướng triển khai

**Ngày:** 2026-06-26
**Người yêu cầu:** Anh (CEO)
**Người thực hiện:** Em (học trò Thiệu Khang Tiết)
**Bối cảnh:** Anh hỏi — tích hợp NotebookLM + Obsidian + wiki dự án thành một mạng lưới tri thức như bộ não (đọc hiểu, ghi nhớ, liên kết khái niệm). Anh nhớ "hình như đã xây theo hướng này rồi", yêu cầu kiểm tra dự án hiện có + tìm hiểu lại NotebookLM + viết báo cáo thực trạng & hướng triển khai.

**Phương pháp:** 2 đợt rà soát đa-agent (8 thợ điều tra) quét code + data thật (`data/yi_wiki/wiki.sqlite3` live) + research web 2025-2026. Mọi số liệu dưới đây đã verify bằng truy vấn SQLite thật, không phải ước lượng.

---

## TL;DR (đọc 30 giây)

1. **Anh đã xây gần xong bộ xương "não" này từ trước** — schema mạng liên kết, máy trích quan hệ, bảng vector, giao diện đồ hình đều CÓ. Nhưng phần lớn **"dựng xong mà chưa bật điện"**: bảng cạnh `atom_relations` = **0 dòng**, embedding atoms = **0**, máy đa-bước có code nhưng chưa nối.
2. **Thư viện còn rất nhiều sách chưa tiêu hoá**: 66 sách trong catalog, **~45 sách còn là PDF thô** (0 khái niệm), chỉ **11 sách** đã rút thành atoms. Trực giác của Anh ("cần máy tự tiêu hoá sách như NotebookLM") là **đúng hướng**.
3. **NotebookLM KHÔNG mã nguồn mở** (Google chưa bao giờ mở code). Cái trên GitHub là bản clone cộng đồng — và bản đó **không trích khái niệm/công thức, không có graph thật** → không dùng làm engine được.
4. **Hướng đúng:** giữ pipeline tự-tiêu-hoá đo-ni-đóng-giày của mình làm xương sống, **mượn thuật toán đa-bước của LightRAG**, bổ sung 3 mảnh nhỏ. Chạy **2 tốc độ**: máy tiêu hoá sách thường (tự động), Anh đọc sâu sách tổ sư (tay).

---

## Phần 1 — Thực trạng thư viện (sách đã/chưa tiêu hoá)

### 1.1 Số tổng quan

| Chỉ số | Con số | Ghi chú |
|---|---:|---|
| Sách trong catalog (`books.json`) | 66 | 60 ở "stage 1" = PDF thô chưa xử lý |
| Sách đã OCR phục dựng trên đĩa | 45 | `data/restored_books/` |
| Corpora đã tiêu hoá thành atoms (Q&A) | 11 | + 1 bảng tra (Thiết Bản đồ giải) = 12 |
| Corpora ở mức "passages-only" | 13 | có text, search được, **chưa** rút thành Q&A |
| Sách còn là PDF thô (0 khái niệm) | ~45 | phần lớn là batch TUVIFULL thêm 23/6 |
| Tổng atoms tri thức | 17.793 | |
| Tổng khái niệm (`concept_index`) | 3.641 | |
| Tổng điều văn bảng tra (`tabular_verses`) | 18.767 | Thiết Bản |

> Định nghĩa "tiêu hoá": sách được rút thành **atoms** (câu hỏi-đáp nguyên tử có dẫn nguồn) HOẶC **bảng tra** (điều văn). Đây là tri thức có cấu trúc mà engine truy vấn được. Sách "passages-only" mới chỉ là text thô bỏ vào kho — tầng trung gian.

### 1.2 Sách ĐÃ tiêu hoá (11 corpora có atoms)

| Sách | Atoms |
|---|---:|
| Hoàng Cực Kinh Thế Kim Thuyết (Thượng) | 7.154 |
| Trung Châu phái Tử Vi quyển 2 | 5.584 |
| Tử Vi Hàm Số | 1.185 |
| Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục) | 1.156 |
| Tử Vi Đẩu Số Toàn Thư (bản Hán) | 980 |
| Thiên Lương (Nghiệm Lý Toàn Thư) | 769 |
| Tử Vi Bôn Ba (research TikTok) | 478 |
| Nguyệt Đồ Số Mệnh (research TikTok) | 180 |
| Huy Tuấn Tử Vi (research TikTok) | 157 |
| Âm Dương Ngũ Hành (Lê Văn Sửu) | 109 |
| Thiết Bản Thần Số | 41 atoms + 12.009 bảng tra |

Khái niệm theo trường phái: Mai Hoa 1.941 · Tử Vi 787 · Kinh Dịch 589 · Hà Lạc 98 · Tứ Trụ 70.

### 1.3 Sách CHƯA tiêu hoá (đáng chú ý)

Toàn bộ batch **TUVIFULL** (thêm 23/6, ~45 cuốn, PDF thô, 0 atom):
- TAP CHI KHHB TRUOC 1975 (1.184tr), Tam Hợp Phái q1 (860tr) + q2 (900tr)
- Tử Vi Đẩu Số Quyển Thượng Mệnh Lý (608tr), Tử vi ảo bí (486tr), Tử vi tổng hợp (442tr)
- Tử vi hoàn toàn khoa học t1 (380tr), Trung Châu giáo trình hạ (304tr), ... và ~38 cuốn nữa

**Đáng lưu ý — sách CỐT LÕI nhưng mới ở mức passages-only (chưa atomize):**
- **Mai Hoa Dịch Số** (q1q2 + bản Thiệu Khang Tiết) — trường phái gốc của hệ, nhưng chưa rút Q&A
- **Kinh Dịch Trọn Bộ** Ngô Tất Tố — chỉ 64 passages
- **Bát Tự Hà Lạc** — 605 passages, chưa atomize

> **Điểm cốt lõi cho Anh:** kho sách đang phình nhanh hơn tốc độ tiêu hoá. Đây chính là vấn đề Anh trực giác thấy → cần cỗ máy tự tiêu hoá.

---

## Phần 2 — Thực trạng "bộ não" (5 mảnh đã có)

Anh đã xây **5 mảnh** theo hướng mạng lưới tri thức, nhưng rời rạc và phần lớn chưa bật:

| Mảnh | Vai trò trong "não" | Tình trạng |
|---|---|---|
| `atom_relations` | **Synapse** — cạnh nối atom↔atom, 6 loại quan hệ (luận giải thêm, công thức áp dụng, trái nghĩa, cách cục liên quan, liên phái...) | Schema + máy trích (`relations_extract.py`) ĐÃ viết · **0 / 17.793 cạnh** · chưa chạy lần nào |
| Embedding atoms (`atom_vec`) | **Myelin** — số hoá nghĩa để tìm theo ý | Bảng tạo rồi · **0 atoms** số hoá · retrieval phải dùng từ khoá |
| Đồ hình Kinh Dịch | Mạng trực quan + giao diện | ✅ **Đang chạy** (64 quẻ, 124 cạnh, `KinhDichGraph.vue`) — nhưng cạnh viết cứng tay, chỉ cho 64 quẻ |
| Mạng Lexicon | Khái niệm → thuộc tính ngũ hành/âm dương + theo dõi mâu thuẫn đa phái | ✅ Chạy (195 khái niệm, 351 liên kết) — nhưng là khái niệm→thuộc-tính, **không phải** khái niệm↔khái niệm |
| Tìm kiếm Council | Tầng truy xuất cho Hội Đồng sage | ✅ Chạy — nhưng **1 bước, từ khoá** (FTS5/BM25), không vector, không đi theo mạng |

### 2.1 Cách Hội Đồng (sage) trả lời hôm nay

```
Câu hỏi → mỗi sage tìm SÁCH đúng 1 lần (từ khoá BM25)
        → lấy 12 đoạn, giữ 4, cắt còn 280 chữ
        → dán vào LLM → trả lời
Trọng tài cuối chỉ đọc LỜI VĂN các sage, KHÔNG đọc lại sách
```

**Hệ quả:** hỏi diễn đạt khác chữ trong sách → tìm hụt; chỉ ~4 đoạn ground một câu hỏi mệnh trong khi có 17.793 atoms; dễ "trôi" khỏi nguồn (citation drift). Đây là RAG **một-bước, một-tầng, theo chữ** — ngược với cách não liên tưởng nhiều bước.

### 2.2 Quy luật chung phát hiện được

**"Schema dựng xong, dữ liệu chưa đổ vào"** lặp ở khắp nơi:
- `atom_relations` = 0 (cạnh mạng)
- `atom_vec` = 0 (embedding)
- `persons.relationships` = 0 (mạng xã hội)
- `contextual_meanings.modifier_ids` = 0 (ghép khái niệm)
- Cột `formulas_json` / `combos_json` chưa bao giờ được ghi

→ Bộ xương não ~80% đã có. Cái thiếu là **chạy các job để đổ đầy** + **nối lại thành một mạng**.

---

## Phần 3 — Pipeline sách → khái niệm → công thức (as-built)

Đây là mục tiêu Anh nêu: "từ sách >> khái niệm >> công thức >> làm tốt nhất cho kho backend". Tin tốt: **pipeline này ĐÃ TỒN TẠI**, chỉ chạy dở dang.

### 3.1 Đường đi thực tế (as-built)

```
A. Sách PDF → phục dựng trang (MarkItDown / MinerU OCR)         → data/restored_books/<sách>/pages/p####.md
B. Librarian phân tier S/A/B/C (đọc 6 trang đầu, LLM đề xuất)    → engine/yi_lexicon/librarian.py
C. Chunk (mỗi trang = 1 chunk + tóm tắt cuốn chiếu)             → chunks_v2 (2.274)
D. Atomize 2-pass:
   Pass 1 — phân loại 5 "archetype" + format + đề xuất template  → chunk_classifications (720 = ~32%)
   Pass 2 — sinh atomic Q&A {câu hỏi, dẫn nguồn, định danh sao}  → atomic_questions (17.793)
E. Làm giàu Phase-2:
   - Chú giải 4 lớp (hán-việt / thuần việt / nguyên lý / ví dụ)  → atom_commentaries (6.458 = ~36%)
   - Trích quan hệ atom↔atom (6 loại)                            → atom_relations (0 — CHƯA CHẠY)
F. Truy xuất (FTS5 + workbench Duyệt Atoms)
G. Khái niệm — TÁCH RỜI, soạn tay                                → concept_index (3.641)
H. Nhánh bảng tra cho sách "số" (Thiết Bản)                      → tabular_verses (18.767)
```

### 3.2 Khái niệm được tạo thế nào

Hiện có **2 hệ khái niệm tách rời**, và **máy atomize KHÔNG nuôi cái nào**:
- `concept_index` (3.641, trong `wiki.sqlite3`) — soạn **TAY**, từng dải trang hardcoded trong `extract.py` lúc Anh đọc sâu. Đây là hệ đang vận hành.
- `concepts` của Lexicon — từ điển ký hiệu cosmology, nuôi bởi `distill.py` từ council/LLM.

→ **Lỗ hổng:** không có cầu nối **atom → khái niệm**. Nhãn `from_category`/`from_template` mà LLM tự sinh trên mỗi atom (16.866 atoms có) **không được chuẩn hoá** vào bảng khái niệm nào.

### 3.3 Công thức được xử lý thế nào

| Cơ chế | Tình trạng |
|---|---|
| Cờ `is_cong_thuc` (boolean trên chunk) | 281 chunks gắn cờ — chỉ là cờ, không có nội dung công thức |
| Cờ `is_to_hop` (cách cục/combo) | 157 chunks — cũng chỉ là cờ |
| Cột `formulas_json` / `combos_json` | **Khai báo nhưng KHÔNG bao giờ được ghi** → nội dung công thức chưa trích |
| Quan hệ `cong_thuc_apdung` (cạnh) | Định nghĩa rồi nhưng `atom_relations`=0 → graph công thức **không tồn tại trong data** |
| `tabular_verses` (bảng tra điều văn) | ✅ **Chạy thật, 18.767 dòng** — chỗ DUY NHẤT "công thức thành dữ liệu" đã vật chất hoá |
| Từ điển 545 cách cục Phú Thái Vi | Nằm RỜI ở `engine/tu_vi/cach_cuc_dict.py`, **không nối** với atoms |

### 3.4 Phân tier S/A/B/C

CÓ tồn tại (S=kinh điển gốc, A=kinh điển phái, B=học giả VN hiện đại, C=đại chúng). NHƯNG:
- Tier chỉ điều khiển **quyền uy / xử lý mâu thuẫn đa phái** (tier cao thắng khi xung đột) — đúng Iron Rule #3.
- Tier **KHÔNG** điều tiết độ sâu đọc/atomize. Máy atomize "mù tier" — chạy đều mọi chunk.
- `reading_plan_2026_v1` có lịch đọc theo tuần nhưng **mọi tuần đều status: pending** — bộ lập lịch viết rồi chưa chạy.

### 3.5 Pipeline DỪNG ở đâu (các lỗ hổng)

1. **Atomize mới phủ ~32%** chunks; chỉ 1 sách (Trung Châu) atomize đáng kể, còn lại mảnh vụn.
2. **`atom_relations` = 0** — toàn bộ graph quan hệ (gồm công thức-áp-dụng, liên phái) là code suông.
3. **Nội dung công thức chưa trích** — chỉ có cờ boolean, không có payload cấu trúc.
4. **Lịch đọc tự động chưa chạy** (pending hết).
5. **Khái niệm soạn tay, tách rời** — không có linker atom→khái niệm.
6. **Chú giải mới ~36%**.

> **Kết luận Phần 3:** kiến trúc sách→chunk→atom→khái niệm→công thức→quan hệ **đã thiết kế đầy đủ, hiện thực một phần**, nhưng **chưa từng chạy tiêu hoá toàn kho tự động**. Nó dừng sau khi atomize dở dang một sách chính.

---

## Phần 4 — NotebookLM: đính chính + research

### 4.1 Đính chính (quan trọng)

| Anh nghĩ | Thực tế (đã verify) |
|---|---|
| "NotebookLM có mã nguồn mở rồi" | **Sai.** Google CHƯA bao giờ mở code NotebookLM. Bản gốc đóng, chạy Gemini, data lên cloud Google. |
| Cái trên GitHub | Là **clone cộng đồng** — lớn nhất [open-notebook](https://github.com/lfnovo/open-notebook) (33k sao, MIT, self-host). |
| NotebookLM liên kết khái niệm? | CÓ tính năng **Mind Map** — nhưng là cây *sinh tạm thời* từ tài liệu, KHÔNG phải mạng lưu trữ lâu dài 2 chiều như Obsidian. |
| API dùng được? | KHÔNG có API công khai cho người thường (chỉ bản Enterprise trả phí). |

### 4.2 open-notebook làm/không làm gì (đã verify code)

**Làm:** nhận nhiều loại nguồn → chunk → embed (đa nhà cung cấp) → "transformations" (tóm tắt/insight) → lưu SurrealDB. Tức là *chat-trên-tài-liệu* bằng vector RAG.

**KHÔNG làm:** không trích khái niệm/entity · không xây graph khái niệm thật (cái họ gọi "knowledge graph" chỉ là **liên kết bản ghi** notebook→source→note kiểu khoá ngoại) · không trích công thức/quy tắc · không đa-bước.

→ **open-notebook trùng đúng những phần mình ĐÃ CÓ (chunk + embed + chú giải), và KHÔNG cho gì ở 3 chỗ mình đang thiếu.** Đừng dùng làm engine tiêu hoá. Cùng lắm mượn UX upload + lớp embedding đa-provider.

### 4.3 Research — hướng tiêu hoá tốt nhất 2025-2026

Đồng thuận học thuật: pipeline xây knowledge-graph bằng LLM gồm 5 tầng — **(0) parse giữ bố cục → (1) thiết kế ontology/schema TRƯỚC → (2) LLM trích entity+quan hệ có dẫn nguồn → (3) hợp nhất/khử trùng entity → (4) tầng kiểm chứng (LLM 2 soi từng triple) → (5) index cho vector + graph + FTS**.

- **LightRAG** = hợp nhất với mình (nhẹ, tăng dần, chạy được trên kho nhẹ kiểu SQLite, truy xuất 2 tầng, rẻ ~10x so với Microsoft GraphRAG).
- **GraphRAG** đầy đủ: đắt token, re-index chậm → chỉ mượn ý "tóm tắt cộng đồng" cho overview mỗi sách.
- **Công thức của mình** = quy tắc thủ tục + bảng tra (cách cục, sinh-khắc Thể-Dụng, an sao, điều văn) — **KHÔNG phải math/LaTeX**. → Mô hình hoá thành **node có kiểu** (điều kiện → hệ quả, áp-dụng-cho, nguồn) + giữ bảng tra dạng dòng (đúng pattern `tabular_verses`).

---

## Phần 5 — Hướng triển khai đề xuất

Nguyên tắc: **giữ pipeline đo-ni-đóng-giày của mình làm xương sống** (lợi thế độc quyền: chú giải đa phái Đông phương không tool generic nào có), chỉ **lấp 3 lỗ hổng hẹp**. KHÔNG migrate khỏi SQLite, KHÔNG rebuild.

### 5.1 Pipeline 2 TỐC ĐỘ (khớp đúng thực tế Anh + Iron Rule #2)

**LANE A — Máy tiêu hoá (sách thường, hàng loạt, tự động):**
1. Parse giữ bố cục (MarkItDown/MinerU sẵn có).
2. Chunk → atomize sẵn có, **THÊM** một lượt trích triple theo schema (kiểu LightRAG): sinh khái niệm + quan hệ có kiểu + quy tắc/cách cục, mỗi thứ **dẫn nguồn** (span-grounding).
3. Khử trùng entity dựa trên `concept_dict` canon + `tu_dien_thuan_viet` neo sẵn có (snap về ID có sẵn, không tạo trùng).
4. Lượt kiểm chứng (LLM 2) bỏ triple không có nguồn; mọi thứ vào kho với `founder_verified=0` (chưa duyệt) + điểm tin cậy + xuất xứ.
5. Đổ đầy embedding `atom_vec` cho mọi atom/khái niệm/cạnh; dựng bảng `edges`.
→ Mỗi sách chưa đọc thành **subgraph khái niệm + quy tắc** mà KHÔNG cần người, truy vấn đa-bước được, gắn cờ "máy làm".

**LANE B — Đọc sâu (sách tổ sư, Anh đọc tay):**
- Nghi thức `doc-sau-20-trang` giữ NGUYÊN. Đọc sâu sinh node/cạnh `founder_verified=1` + chú giải uy quyền **đè** triple máy khi xung đột.
- Máy (Lane A) dọn sẵn graph → Anh đọc vào một bản đồ đã có cấu trúc (nhanh hơn; việc của Anh thành *duyệt/sửa*, không phải *trích từ đầu*).

### 5.2 Ba mảnh cần BUILD (nhỏ, không phải viết lại)

1. **Lượt trích quan hệ** — đọc atoms/chunks ĐÃ CÓ (không parse lại sách), sinh triple có kiểu vào bảng `edges`, dẫn nguồn. Tái dùng chuỗi provider (Ollama rẻ → DeepSeek/MiniMax khi khó).
2. **Job đổ embedding** — số hoá nghĩa mọi atom + khái niệm + cạnh vào sqlite-vec.
3. **Bộ truy xuất đa-bước** — trên (FTS + vector + edges): khớp 2 tầng (entity + chủ đề) rồi lan 2-3 bước. ~50 dòng, không cần DB mới. Biến Council từ "tìm phẳng" thành thật-sự-đa-bước ("Vũ Khúc → khắc → ? → ở cung nào → cách cục gì").

### 5.3 Ontology cần định nghĩa TRƯỚC (bước đòn bẩy cao nhất)

- **Loại node:** khái niệm, sao, cung, quẻ, hào, tác giả, trường phái, quy-tắc/cách-cục, công-thức.
- **Loại quan hệ:** sinh, khắc, chế, hoá, thuộc-phái, an-tại-cung, biến-thành, dẫn (cites), mâu-thuẫn (contradicts).
- Trích theo schema giữ KG đa phái khỏi "nát thành cháo" + tôn trọng Iron Rule #3 (mâu thuẫn thành cạnh `contradicts`/`variant-of` tường minh, không gộp lén).

### 5.4 KEEP / BORROW / DON'T

- **KEEP:** atomization Q&A + chú giải 4 lớp (moat) · SQLite+FTS5+sqlite-vec · `tabular_verses` · kỷ luật `founder_verified` + dẫn nguồn.
- **BORROW (từ LightRAG):** prompt trích entity+quan hệ · truy xuất 2 tầng · cập nhật tăng dần (union sách mới vào graph).
- **DON'T:** đừng dùng open-notebook làm engine · đừng deploy full GraphRAG · đừng bỏ SQLite sang Neo4j/SurrealDB · đừng cho triple máy vào kho mà không kiểm chứng + cờ `founder_verified=0`.

---

## Phần 6 — Lộ trình & quyết định cần Anh chốt

### 6.1 Lộ trình đề xuất (rẻ → đáng giá)

| Bước | Việc | Kết quả thấy được | Công sức |
|---|---|---|---|
| 1 | Đổ embedding `atom_vec` (17.793 atoms) | Council tìm theo **nghĩa**, không chỉ chữ — ngay lập tức đỡ "tìm hụt" | ~nửa ngày máy chạy |
| 2 | Định nghĩa ontology + lượt trích `edges` (Lane A) trên atoms có sẵn | Mạng synapse có thật, đa-bước được | 1-2 ngày |
| 3 | Bộ truy xuất đa-bước nối vào Council | Sage luận sâu, đi theo mạng | 1 ngày |
| 4 | Chạy Lane A tiêu hoá batch sách thô (45 cuốn) ở `founder_verified=0` | Kho phình từ 11 → ~50 sách tiêu hoá | máy chạy nền nhiều ngày |
| 5 | Giao diện mạng khái niệm (nâng `KinhDichGraph` → data-driven, Cytoscape) | Anh "dạo" mạng như Obsidian, học bằng hình | 1-2 ngày |

### 6.2 Ba quyết định cần Anh chốt

1. **Bắt đầu từ đâu?** — Em đề xuất **Bước 1+2+3 (backend não)** trước, vì khớp hướng backend-first Anh chốt 10/6 và là nền cho mọi thứ sau. (Lựa khác: làm giao diện mạng trước để thấy bằng mắt.)

2. **Phạm vi tiêu hoá thử đầu tiên?** — Em đề xuất chạy Lane A thử trên **1 sách cốt lõi đang dang dở** (vd Mai Hoa q1q2 — trường phái gốc, mới passages-only) để kiểm chất lượng triple + công thức, rồi mới bung 45 sách.

3. **Ngưỡng tự động vs duyệt tay?** — Triple máy vào kho ở `founder_verified=0` (chưa duyệt), hiện trong workbench "Duyệt Atoms" để Anh/em duyệt dần lên `0.98`. Anh đồng ý cơ chế này chứ?

---

## Phụ lục — File & nguồn tham chiếu

**File code chính:**
- Pipeline: `engine/atomization/{atomizer,chunker,batch_atomize,relations_extract,commentary_gen,tabular_ingest_model,retriever}.py`
- Schema: `engine/atomization/{schema,schema_phase2,schema_tabular}.sql`
- Khái niệm: `engine/yi_wiki/{store,extract}.py` · `engine/yi_lexicon/{store,librarian,tiers}.py`
- Tier: `data/yi_lexicon/source_tiers.yaml`
- Council RAG: `engine/ai/{expert_context,agents,council,kanban_council,precast}.py`
- Đồ hình: `engine/yi_wiki/luan_sau_kinhdich.py` · `client/webapp/src/components/wiki/KinhDichGraph.vue`
- Data live: `data/yi_wiki/wiki.sqlite3` · `data/yi_lexicon/lexicon.sqlite3`

**Nguồn research:** Khảo sát KG-construction bằng LLM (arXiv:2510.20345) · LightRAG (HKUDS, EMNLP 2025) · ODKE+ ontology-guided (arXiv:2509.04696) · TextMine (arXiv:2509.15098) · benchmark trích công thức (arXiv:2512.09874) · open-notebook architecture docs + DeepWiki · Cognee/Graphiti benchmarks.

**So sánh engine (nếu cần tham khảo):** [LightRAG](https://github.com/HKUDS/LightRAG) (34k★) · [Cognee](https://github.com/topoteretes/cognee) (22.9k★) · [Graphiti](https://github.com/getzep/graphiti) (28k★) · [open-notebook](https://github.com/lfnovo/open-notebook) (33k★).
