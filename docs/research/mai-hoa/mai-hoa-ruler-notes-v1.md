# Mai Hoa / Tam Thiên - Ruler Notes v1.7

Mục tiêu: rút các "ruler" có thể chuyển thành rule engine cho Trang 2 (Lục Hào chi tiết + 64 quẻ + Mai Hoa môi trường).

Nguồn đọc bổ sung:
- `thư viện sách/Tam Thiên Dịch Số.pdf`
- cụm nội dung quanh phần `Định Hệ Từ` và `Bảng truy tầm 64 thức hệ`

## Tracking tiến độ đọc (bắt buộc provenance)

- Sách: `thư viện sách/Tam Thiên Dịch Số.pdf`
- Tổng số trang PDF: `281`
- Đã đọc đến: `trang 281/281`
- Trạng thái: `completed` (đã đọc hết cuốn hiện có trong thư viện)

Quy ước trích nguồn:
- Mỗi rule phải có `source_ref` theo dạng:
  - `Tam Thiên Dịch Số.pdf | p.xxx-yyy | section/quẻ`
- Khi nâng cấp/sửa rule, phải giữ lại ref cũ + thêm ref mới.

## 1) Ruler nền tảng (ưu tiên engine hóa)

## R1 - Thoán từ vs Tượng từ (macro/micro split)
- Thoán từ: mô tả toàn quẻ (bối cảnh tổng thể).
- Tượng từ: mô tả biến động theo hào (chi tiết tiến trình).
- Mapping implementation:
  - Trang 2 Tab Tổng quan: ưu tiên `thoan-layer`.
  - Trang 2 Tab Chi tiết: ưu tiên `tuong-layer` + moving lines.

## R2 - Động/Tĩnh là trục quyết định nhịp
- Quẻ/hào có tính động => thiên về thời gian gần, dễ xuất sự.
- Quẻ/hào có tính tĩnh => thiên về dưỡng lực/chờ thời, ứng kỳ xa hơn.
- Mapping implementation:
  - tăng/giảm trọng số pace bucket trong `calculate_timing()`.

## R3 - Đóng/Mở (Khôn/Càn) như chu kỳ trạng thái
- Đóng cửa là Khôn, mở cửa là Càn; mỗi lần đóng/mở là một biến.
- Mapping implementation:
  - thêm state machine 2 pha `CLOSE -> OPEN`.
  - dùng để giải thích vì sao một mốc ứng kỳ cần "chờ mở chu kỳ".

## R4 - 64 x 64 là không gian chuyển hóa
- Văn bản nhấn mạnh không gian biến thiên rộng (`64 x 64 = 4096` dạng tổ hợp luận quẻ).
- Mapping implementation:
  - giữ output hiện tại 1 quẻ chủ + 1 quẻ biến cho MVP.
  - chuẩn bị hook mở rộng "quẻ liên đới" trong rule namespace, không bật mặc định.

## R5 - Cẩn mật dữ liệu đầu vào
- Tài liệu nhấn mạnh "cẩn mật lời nói/việc làm" trước khi quyết đoán.
- Mapping implementation:
  - nếu input mơ hồ -> hạ confidence và ép chế độ conservative.
  - chỉ mở chế độ advanced khi user profile/account/data-confirm đầy đủ.

## 2) Ruler diễn giải cho Trang 2 (đề xuất)

- `ruler_context`: Thoán từ + quan hệ ngũ hành Mai Hoa môi trường.
- `ruler_process`: Tượng từ + hào động + trạng thái phá/không.
- `ruler_timing`: pace bucket + ứng kỳ best match + ứng viên fallback.
- `ruler_action`: nên làm / nên hoãn / nên tránh, theo mức đồng thuận.

## 3) Đề xuất contract dữ liệu (v2)

Thêm vào payload Trang 2:
- `ruler_profile.id` = `tam_thien_v1`
- `ruler_profile.layers` = [`context`, `process`, `timing`, `action`]
- `ruler_profile.confidence` = `low|medium|high`
- `ruler_profile.notes` = lý do hạ/tăng confidence

## 4) Việc cần làm tiếp (không phá MVP)

1. Tạo file seed riêng: `data/seeds/mai_hoa_ruler_v1.json`.
2. Refactor nhẹ `engine/luc_hao.py` để nhận `ruler_profile` optional.
3. Hiển thị ở Trang 2 một block "Ruler đang dùng" để truy vết.
4. Mỗi lần đọc thêm 10-20 trang, cập nhật note + bump `tam_thien_v1.x`.

---

## 5) Bổ sung từ vòng đọc mới (Định Hệ Từ, cụm ~69-78)

## R6 - Đếm ngược để luận biến (reverse progression)
- Văn bản nêu "đếm cái trước thuận, biết cái sau nghịch, Kinh Dịch đếm ngược".
- Mapping implementation:
  - với timeline ứng kỳ, giữ mốc forward D+N cho UI, nhưng thêm trường phụ:
    - `reverse_probe`: số bước nghịch để kiểm lại mốc chính.
  - dùng `reverse_probe` để cảnh báo mốc dễ "đảo pha" (đẹp trước, khó sau).

## R7 - Trục 8 quái theo phương vị và chức năng
- Cụm mô tả phương vị/chức năng của từng quái (Chấn động, Tốn nhập, Ly sáng, Khôn dưỡng, Đoài duyệt, Khảm hiểm, Cấn chỉ, Càn chủ).
- Mapping implementation:
  - thêm bảng `trigram_role_map` cho layer `context`.
  - sinh câu diễn giải theo cặp:
    - thượng quái = môi trường chi phối
    - hạ quái = cơ chế vận hành cục bộ.

## R8 - "Tốt/Xấu/Hối/Tiếc" là tín hiệu chất lượng quyết định
- Văn bản nhấn mạnh tốt/xấu và hối/tiếc là hệ tín hiệu sau khi quẻ/hào động.
- Mapping implementation:
  - thêm `decision_quality` trong `ruler_profile`:
    - `favorable`, `caution`, `regret-risk`.
  - khi có nhiều dấu "hối/tiếc" (hào phá/không + xung đột), auto hạ confidence.

## R9 - Ruler đức hạnh theo cụm quẻ neo (Lý/Khiêm/Phục/Hằng/Tổn/Ích/Khốn/Tỉnh/Tốn)
- Đoạn sách cho nhóm quẻ làm "trục đức".
- Mapping implementation:
  - thêm `virtue_anchor`:
    - nếu quẻ chủ hoặc quẻ biến nằm trong nhóm neo -> thêm câu khuyến nghị chuẩn hóa hành vi.
  - ưu tiên đưa vào `action-layer` để tránh luận thuần kỹ thuật.

## R10 - Cùng tắc biến, biến tắc thông (gating chiến lược)
- Tinh thần chuyển trạng thái khi bế tắc đã rõ.
- Mapping implementation:
  - nếu `verdict=caution` liên tục + mốc ứng kỳ trễ:
    - đề xuất switch chiến lược từ `execute` -> `reframe`.
  - hiển thị gợi ý "đổi cách" thay vì chỉ "chờ".

## 6) Delta contract đề xuất cho `tam_thien_v1.1`

Thêm các field không phá backward compatibility:
- `ruler_profile.reverse_probe`
- `ruler_profile.context_trigram_roles`
- `ruler_profile.decision_quality`
- `ruler_profile.virtue_anchor`
- `ruler_profile.strategy_mode` (`execute|stabilize|reframe`)

Ghi chú:
- Vẫn giữ mặc định conservative khi dữ liệu user chưa đủ chuẩn.
- Các field mới có thể nullable ở giai đoạn đầu để không phá API hiện hữu.

---

## 7) Bổ sung từ vòng đọc mới (Định Thức Hệ Từ + Định Tạp/Định Tự, cụm ~85-96)

## R11 - Tám quái giao nhau, luận theo cặp lực
- Văn bản nhấn mạnh: sấm-gió, nước-lửa, núi-đầm thông khí và thúc đẩy nhau.
- Mapping implementation:
  - thêm `pair_dynamics` trong context:
    - `thunder_wind`, `water_fire`, `mountain_lake`.
  - dùng để giải thích "động lực chính" của case thay vì chỉ nhìn một quẻ độc lập.

## R12 - Rule "đếm ngược" phải kèm chiều thuận
- Sách nói "đếm trước thuận, biết sau nghịch", nhưng thực hành cần cả hai chiều.
- Mapping implementation:
  - thêm `timing_dual_view`:
    - `forward_offsets` (D+N)
    - `reverse_probe` (N-1/N/N+1)
  - UI mặc định forward, reverse để kiểm nhiễu.

## R13 - Định Tạp: quẻ có "từ khóa ngắn" trực tiếp
- Cụm Định Tạp cho mỗi quẻ một nhãn ngắn (ví dụ: bế tắc, hanh thông, mục nát...).
- Mapping implementation:
  - thêm seed `hexagram_short_tag` cho 64 quẻ.
  - ưu tiên hiển thị ở Tab 1 làm "nhãn nhanh" trước khi mở phân tích sâu.

## R14 - Định Tự: chuỗi chuyển quẻ là narrative pipeline
- Định Tự trình bày 64 quẻ theo chuỗi logic diễn tiến.
- Mapping implementation:
  - thêm `narrative_next_hint`:
    - từ quẻ hiện tại gợi ý 1-2 quẻ kế tiếp trong chuỗi.
  - dùng cho action-layer: "nếu giữ chiến lược hiện tại, case dễ trôi về trạng thái nào".

## R15 - 5 phần chuẩn cho mỗi thức hệ (đã khớp schema v2)
- Sách xác nhận rõ 5 phần:
  - Thế gian sự vụ
  - Nhập thế
  - Xuất thế
  - Thế gian vận
  - An bài thế sự
- Mapping implementation:
  - giữ `hexagram_interpretation_v2` là schema chuẩn.
  - thêm cờ provenance: `source_section = Dinh He Tu / Bang Truy Tam`.

## R16 - Rule tối giản hóa để tránh luận dài dòng
- Tác giả chủ trương "vắn tắt gọn gàng, biết ngay kết quả sở cầu".
- Mapping implementation:
  - giữ hai lớp output:
    - `fast_read` (1-2 câu)
    - `deep_read` (4-layer/5-layer đầy đủ)
  - mặc định cho khách xem `fast_read`, bấm mở sâu khi cần.

---

## 8) Bổ sung từ vòng đọc mới (Bảng truy tầm + mở đầu quẻ 1, cụm ~97-107)

## R17 - Quy trình tra quẻ chuẩn hóa (lookup pipeline)
- Văn bản mô tả rõ quy trình:
  - gieo 6 đồng tiền (xếp từ dưới lên),
  - truy bảng 64 thức hệ lấy số thứ tự + tên,
  - đọc phần luận giải theo thứ tự quẻ.
- Mapping implementation:
  - chuẩn hóa pipeline UI:
    1) `capture_input`
    2) `build_hexagram`
    3) `lookup_king_wen`
    4) `render_fast_read`
    5) `expand_deep_read`

## R18 - Fast-read là mặc định, deep-read là tùy chọn
- Tác giả nhấn mạnh "biết ngay kết quả sở cầu", không luận dài dòng.
- Mapping implementation:
  - Tab 2 nên có block "Kết luận nhanh 1 dòng" cố định.
  - Các lớp khác mở rộng theo accordion/tab để không gây rối.

## R19 - 5 phần luận là skeleton bắt buộc cho mỗi quẻ
- Được xác nhận lại trong phần dẫn nhập:
  - Thế gian sự vụ
  - Nhập thế
  - Xuất thế
  - Thế gian vận
  - An bài thế sự
- Mapping implementation:
  - giữ schema v2 hiện tại làm chuẩn cứng.
  - thêm kiểm thử dữ liệu: record nào thiếu 1/5 phần thì fail seed validation.

## R20 - Cảnh báo provenance và thiên kiến diễn giải
- Phần mở đầu có nhiều nhận định lịch sử/tiên tri mang tính lập trường.
- Mapping implementation:
  - thêm `source_bias_note` trong metadata của dataset.
  - khi render cho end-user:
    - tách "rule vận hành" khỏi "đoạn diễn ngôn niềm tin/chính trị".
  - không dùng đoạn mang tính tiên tri xã hội để huấn luyện quyết định cá nhân.

---

## 9) Bổ sung từ vòng đọc mới (quẻ 2-7, cụm ~107-118)

## R21 - Rule "đại sự/chuyện nhỏ" (scope gating)
- Nhiều quẻ trong cụm này lặp lại thông điệp: chuyện nhỏ có thể chạy, đại sự chưa nên chốt.
- Mapping implementation:
  - thêm `scope_gate`:
    - `small_ok_big_wait`
    - `small_big_ok`
    - `all_wait`
  - hiển thị rõ ở action-layer để user tránh over-commit.

## R22 - Rule "ẩn nhẫn chờ thời" (timing posture)
- Các quẻ Bỉ/Độn/Vô Vọng nhấn mạnh án binh, chỉnh lực, chờ thời.
- Mapping implementation:
  - thêm `posture_mode`:
    - `advance`, `stabilize`, `hide_and_wait`.
  - map trực tiếp từ combo:
    - `decision_quality`
    - `pace_bucket`
    - `relation_tag`.

## R23 - Rule "hy sinh tiểu tiết để thành đại cục"
- Quẻ Thái và các ví dụ lịch sử nhấn mạnh đổi nhỏ lấy lớn.
- Mapping implementation:
  - thêm `tradeoff_hint`:
    - nếu mốc ứng kỳ đẹp nhưng nguồn lực hạn chế -> gợi ý "cắt việc phụ".

## R24 - Rule "thiên thời-địa lợi-nhân hòa" như điều kiện kích hoạt
- Cụm Đại Súc nêu rõ đủ 3 điều kiện mới tiến được đại sự.
- Mapping implementation:
  - thêm `triple_condition_check`:
    - `timing_ready` (ứng kỳ)
    - `resource_ready` (nội lực/tài lực)
    - `social_ready` (đồng thuận/hợp lực)
  - chỉ khi >=2/3 mới cho `strategy_mode=execute`.

## R25 - Rule "fast_read một dòng theo quẻ"
- Các đoạn diễn giải đều có thể tóm thành 1 câu hành động rõ.
- Mapping implementation:
  - thêm trường `one_line_verdict` vào `ruler_profile`.
  - ưu tiên hiển thị ở đầu Tab 2 trước toàn bộ layer chi tiết.

---

## 10) Bổ sung từ vòng đọc mới (quẻ 8-17, cụm ~119-142)

## R26 - Rule "đồng nhân/đại hữu": đại sự cần hợp lực + tín nhiệm
- Cụm Đồng Nhân, Đại Hữu nhấn mạnh: muốn đi đại cục phải có lực tập thể và niềm tin giữa các bên.
- Mapping implementation:
  - thêm `coalition_strength` (low/medium/high):
    - dựa trên `social_ready`, số hào động đồng pha, và độ rõ câu hỏi.
  - nếu `coalition_strength=low` thì action tự động chuyển về `stabilize` dù timing đẹp.

## R27 - Rule "tụng": ưu tiên tự xử, giảm đối đầu pháp lý trực diện
- Quẻ Tụng lặp thông điệp tránh kiện tụng/đấu công khai khi thế chưa thuận.
- Mapping implementation:
  - thêm `conflict_mode`:
    - `negotiate_first`, `legal_last`.
  - trong action-layer: khi `decision_quality` thấp + `relation_tag=conflicting`, ưu tiên đàm phán/tái khung thay vì công kích trực diện.

## R28 - Rule "nhu": lùi một nhịp để tiến hai nhịp (staged execution)
- Quẻ Nhu nhấn mạnh chờ thời nhưng không thụ động: vừa chờ vừa chuẩn bị lực.
- Mapping implementation:
  - thêm `staged_plan` gồm 3 pha:
    - `prepare` (chuẩn bị),
    - `trigger` (kích hoạt đúng mốc),
    - `push` (đẩy sau kích hoạt).
  - mốc ứng kỳ chỉ mở pha `trigger`, không nhảy thẳng `push` nếu resource chưa đạt.

## R29 - Rule "cấu": gặp thời/gặp người nhưng phải lọc tiểu nhân
- Quẻ Cấu nêu "gặp gỡ" là cơ hội, nhưng kèm rủi ro bị lợi dụng.
- Mapping implementation:
  - thêm `counterparty_risk`:
    - `screen_required` khi xuất hiện dấu hiệu lệch pha giữa context thuận và process nhiễu.
  - action-layer sinh checklist "lọc đối tác": bằng chứng, cam kết, ràng buộc.

## R30 - Rule "tiểu súc/lý": thời nghẽn thì giữ chuẩn và giảm đòn bẩy
- Cụm Tiểu Súc + Lý cho thấy: khi vận chưa thông, giữ khuôn phép và đi bước ngắn để bảo toàn cục.
- Mapping implementation:
  - thêm `leverage_mode`:
    - `light` (đòn bẩy thấp),
    - `normal`,
    - `high` (chỉ khi confidence cao).
  - nếu `posture_mode=hide_and_wait|stabilize` thì ép `leverage_mode=light`.

## R31 - Rule "quải": quyết đoán phải đi cùng chứng cứ công khai
- Quẻ Quải nhấn mạnh muốn "quyết" phải minh định tội/trạng thái trước tập thể, không hành động mù.
- Mapping implementation:
  - thêm `evidence_gate`:
    - thiếu bằng chứng -> không cho `execute`.
  - UI thêm nhắc "chốt quyết định sau khi đủ bằng chứng/điều kiện đối chiếu".

## R32 - Rule "khôn/phục": phục hồi theo chu kỳ, có mốc quay lại
- Quẻ Khôn và Phục cho pattern "thất trước thành sau", "trở lại theo chu kỳ" (có mốc hồi phục).
- Mapping implementation:
  - thêm `recovery_cycle`:
    - `is_recovery_case`,
    - `reentry_window` (mốc quay lại ưu tiên từ timing candidates).
  - nếu case thuộc phục hồi, action-layer ưu tiên "khôi phục nền" trước "mở rộng".

---

## 11) Provenance index theo cụm rule (để truy hồi/sửa/nâng cấp)

- `R1-R5`
  - `source_ref`: `Tam Thiên Dịch Số.pdf | p.61-78 (xấp xỉ) | Định Hệ Từ + nguyên lý Động/Tĩnh, Thoán/Tượng`
- `R6-R10`
  - `source_ref`: `Tam Thiên Dịch Số.pdf | p.69-78 (xấp xỉ) | Đếm ngược, trục 8 quái, tín hiệu tốt/xấu/hối/tiếc, đức-hạnh`
- `R11-R16`
  - `source_ref`: `Tam Thiên Dịch Số.pdf | p.85-96 | Định Thức Hệ Từ, Định Tạp, Định Tự`
- `R17-R20`
  - `source_ref`: `Tam Thiên Dịch Số.pdf | p.97-107 | Bảng truy tầm + phần mở đầu luận quẻ`
- `R21-R25`
  - `source_ref`: `Tam Thiên Dịch Số.pdf | p.107-118 | cụm quẻ 2-7`
- `R26-R32`
  - `source_ref`: `Tam Thiên Dịch Số.pdf | p.119-142 | cụm quẻ 8-17 (Đồng Nhân -> Phục)`
- `R33-R36`
  - `source_ref`: `Tam Thiên Dịch Số.pdf | p.143-152 | cụm quẻ 18-22 (Dự -> Tấn, đang đọc tiếp)`
- `R37-R42`
  - `source_ref`: `Tam Thiên Dịch Số.pdf | p.153-257 | cụm quẻ 23-64 + pattern lặp cuối sách`
- `R43-R44` (phụ lục, confidence thấp hơn)
  - `source_ref`: `Tam Thiên Dịch Số.pdf | p.258-267 | Phụ lục I-II (vận hành tiên tri, xây dựng nhà cửa)`

Ghi chú:
- Đây là provenance theo cụm đọc để giữ tốc độ triển khai.
- Khi chốt release kế tiếp (`v1.7+`), cần bổ sung ref chi tiết tới từng quẻ/hạng mục để tăng độ chính xác truy hồi.

---

## 12) Bổ sung từ vòng đọc mới (quẻ 18-22, cụm ~143-152)

## R33 - Rule "được trợ lực thì chống tự mãn"
- Quẻ Dự nhấn mạnh có trợ lực nhưng dễ hỏng vì phô trương/chễnh mảng.
- Mapping implementation:
  - thêm cảnh báo trong action-layer: `momentum_with_humility`.
  - nếu `decision_quality=favorable` nhưng tín hiệu nhiễu tăng, auto chèn nhắc "giảm phô trương, siết kỷ luật vận hành".

## R34 - Rule "khiêm để tích lực và nhận trợ giúp"
- Quẻ Khiêm lặp lại mẫu: nhún nhường đúng lúc giúp tích lực và mở hỗ trợ.
- Mapping implementation:
  - ưu tiên `posture_mode=stabilize` với task lớn khi social chưa đủ.
  - thêm gợi ý "chia nhỏ mục tiêu + tăng đồng thuận" trước bước execute.

## R35 - Rule "bác/minh di": bỉ cực thì thủ chính, bảo toàn lõi
- Quẻ Bác và Minh Di nhấn mạnh giai đoạn tổn thương/mục nát cần giữ tiết tháo, chờ thời.
- Mapping implementation:
  - khi `scope_gate=all_wait` hoặc `decision_quality=regret-risk`, ép `leverage_mode=light`.
  - phát sinh `one_line_verdict` thiên về bảo toàn tài nguyên + giữ lõi hệ thống.

## R36 - Rule "tấn": khi vận sáng phải chuẩn hóa tiếp đãi và vận hành"
- Quẻ Tấn cho mẫu tăng trưởng nhanh khi thời vận sáng, nhưng yêu cầu lễ độ/kỷ luật để giữ đà.
- Mapping implementation:
  - nếu `triple_condition_check.allow_execute=true`, thêm checklist hậu kích hoạt:
    - chuẩn hóa phối hợp,
    - quản trị tải tăng,
    - giữ chất lượng dịch vụ.

---

## 13) Bổ sung từ cụm cuối sách (quẻ 23-64 + phụ lục)

## R37 - Rule "chính danh + kỷ luật vận hành" là điều kiện bền vững
- Cụm quẻ giữa và cuối (23-64) lặp đi lặp lại: thiếu chính danh/kỷ luật thì nhanh suy.
- Mapping implementation:
  - thêm cờ `governance_gate` (pass/fail) cho action-layer:
    - fail -> không cho execute lớn dù timing thuận.
- `source_ref`: `Tam Thiên Dịch Số.pdf | p.153-257 | quẻ 23-64 (nhiều đoạn II/IV/V)`

## R38 - Rule "thành tín" là bộ lọc đối tác/hợp tác
- Cụm Trung Phu/Hàm/Tụy/Quan nhấn mạnh tín nhiệm, thành tín, tránh dối trá.
- Mapping implementation:
  - tăng trọng số `evidence_gate` + `counterparty_risk`.
  - thiếu chứng cứ/thiếu tín nhiệm -> chỉ cho chạy việc nhỏ.
- `source_ref`: `Tam Thiên Dịch Số.pdf | p.210-251 | quẻ 48, 58, 62`

## R39 - Rule "lùi chiến thuật khi thế xấu, giữ lực lượng"
- Cụm Kiển/Cấn/Khảm/Khốn: gặp thế bí thì ưu tiên rút, ẩn, bảo toàn lõi.
- Mapping implementation:
  - khi `posture_mode=hide_and_wait`:
    - ép `leverage_mode=light`,
    - ưu tiên `staged_plan.prepare`,
    - hoãn hành động không đảo ngược.
- `source_ref`: `Tam Thiên Dịch Số.pdf | p.190-239 | quẻ 40, 47, 56, 58`

## R40 - Rule "hợp lực đúng mục tiêu, chia rẽ thì giảm tốc"
- Cụm Lâm/Tụy/Hoán/Gia Nhân: đồng thuận và phối hợp giúp tăng lực; chia rẽ làm tiêu hao.
- Mapping implementation:
  - dùng `coalition_strength` làm hệ số cho strategy:
    - low -> `stabilize`,
    - medium/high + đủ điều kiện -> `execute`.
- `source_ref`: `Tam Thiên Dịch Số.pdf | p.155-249 | quẻ 27, 28, 53, 61`

## R41 - Rule "đại sự phải đi theo chuỗi: chuẩn bị -> kích hoạt -> hậu kiểm"
- Nhiều quẻ cuối mô tả một vòng đầy đủ từ tích lực, bùng nổ, rồi giữ thành quả.
- Mapping implementation:
  - chuẩn hóa `staged_plan` thành checklist bắt buộc:
    - prepare,
    - trigger,
    - push + kiểm lỗi.
- `source_ref`: `Tam Thiên Dịch Số.pdf | p.151-257 | quẻ 25-64 (pattern diễn tiến)`

## R42 - Rule "đọc nhanh 1 dòng + đọc sâu theo tầng" giữ UX gọn mà không mất chiều sâu
- Cuối sách vẫn giữ văn phong kết luận theo trục hành động.
- Mapping implementation:
  - giữ `one_line_verdict` là mặc định,
  - mở rộng deep-layer khi user cần truy nguyên.
- `source_ref`: `Tam Thiên Dịch Số.pdf | p.153-257 | toàn cụm quẻ cuối`

## R43 - Rule phụ lục "vận hành tiên tri" chỉ dùng tham khảo, không vào lõi deterministic
- Phụ lục I có quy trình vận hành theo bát hướng/phi mạng, thiên về trường hợp chuyên gia.
- Mapping implementation:
  - đưa vào `research-only` namespace, không bật mặc định cho core engine.
- `source_ref`: `Tam Thiên Dịch Số.pdf | p.258-261 | Phụ lục I`

## R44 - Rule phụ lục "xây dựng nhà cửa" dành cho module phong thủy riêng
- Phụ lục II thiên về bố trí không gian nhà ở và nghi lễ.
- Mapping implementation:
  - tách thành module `phong_thuy_layout` (nếu làm sau),
  - không trộn vào pipeline Lục Hào/Mai Hoa hiện tại.
- `source_ref`: `Tam Thiên Dịch Số.pdf | p.262-267 | Phụ lục II`

---

## 14) Ghi chú chất lượng nguồn (để tái sử dụng an toàn)

- Từ p.153 trở đi, nhiều đoạn chứa diễn ngôn lịch sử/chính trị và dự báo thời cuộc:
  - dùng để rút "pattern vận hành" (quản trị, nhịp, hợp lực, rủi ro),
  - không dùng nguyên văn làm kết luận quyết định cá nhân.
- Khi nâng cấp:
  - ưu tiên rule có thể test lặp lại,
  - giữ provenance trang/quẻ để truy hồi chính xác.
