# Ruleset `bac_phai_v1`

Phạm vi tài liệu này định nghĩa bộ quy tắc vận hành hiện tại theo **Bắc phái** cho MVP.
Mục tiêu: chuẩn hóa rule để backend/frontend/test dùng cùng một nguồn.

## 1) Metadata

- `ruleset_id`: `bac_phai_v1`
- `school`: `bac_phai`
- `status`: `active`
- `owner`: `yi-chronos`
- `compatibility`: `ALGORITHM_VERSION >= mvp-0.1.0`

## 2) Nguồn tham chiếu

- `HUONG_DAN_DOC_VA_SU_DUNG_THU_VIEN.md` (khung đọc và trích xuất rule)
- `thư viện sách/Tam Thiên Dịch Số.pdf` (nền lý số, hệ âm dương - chu kỳ)
- Tài liệu Bắc phái bổ sung sẽ được nối thêm tại phiên bản `bac_phai_v1.x`

## 3) Rule Definitions

### RULE `bac.time.ganzhi.cycle60`

- **Input**:
  - `datetime_local`
  - `timezone`
- **Logic**:
  - Quy đổi về UTC, lấy số ngày từ mốc epoch, tính `cycle_60_idx = days % 60`.
  - Suy ra Can-Chi năm/tháng/ngày/giờ theo các công thức đang chạy trong `core/chronos.py`.
- **Output**:
  - `ganzhi.year`, `ganzhi.month`, `ganzhi.day`, `ganzhi.hour`, `cycle_60_idx`.
- **Confidence**: `medium` (MVP deterministic, còn cần đối chiếu thêm lịch pháp chuyên sâu)
- **TestHint**:
  - Cùng input phải ra cùng output.
  - Test regression theo các mốc ngày cố định.

### RULE `bac.time.solar_term.approx24`

- **Input**:
  - `datetime_local`
- **Logic**:
  - Nội suy kinh độ mặt trời gần đúng và ánh xạ về 24 tiết khí (`15°/term`).
- **Output**:
  - `solar_term.id`, `solar_term.name_vi`, `solar_term.solar_longitude`.
- **Confidence**: `medium-low` (đang là bản gần đúng cho MVP)
- **TestHint**:
  - Kiểm tra tính liên tục quanh ranh giới tiết khí.

### RULE `bac.time.moon_phase.synodic`

- **Input**:
  - `datetime_local`
- **Logic**:
  - Dùng chu kỳ giao hội để tính `phase_norm`, nội suy `illumination`, ánh xạ nhãn pha trăng.
- **Output**:
  - `moon_phase.name`, `moon_phase.illumination`, `moon_phase.phase_norm`.
- **Confidence**: `medium`
- **TestHint**:
  - Snapshot quanh sóc/vọng phải chuyển pha hợp lý.

### RULE `bac.yi.hexagram.seed`

- **Input**:
  - `cycle_60_idx`
  - `solar_term.id`
  - `ganzhi.hour`
- **Logic**:
  - Tạo seed deterministic và ánh xạ về 64 quẻ nhị phân.
- **Output**:
  - `yi_state.hexagram_binary`
  - `yi_state.transformed_binary`
  - `yi_state.moving_lines`
- **Confidence**: `medium-low` (MVP placeholder logic, chưa thay bằng engine Bắc phái đầy đủ)
- **TestHint**:
  - Với input giống nhau, quẻ phải giống nhau.

### RULE `bac.yi.hexagram.core64.ngotatto`

- **Input**:
  - `cycle_60_idx`
  - `solar_term.id`
  - `local hour`
- **Logic**:
  - Dùng bộ `hexagrams_master` chuẩn 64 quẻ (King Wen) với cấu trúc quẻ thượng/quẻ hạ.
  - Sinh quẻ hiện hành theo chu kỳ thời gian, sau đó áp dụng hào động để ra quẻ biến.
  - Phân loại chính sách đọc theo số hào động:
    - `0`: `original_judgement`
    - `1-2`: `moving_line_texts`
    - `3`: `dual_hexagram_context`
    - `4-5`: `transformed_focus`
    - `6`: `fully_transformed`
- **Output**:
  - `yi_state.hexagram_name`
  - `yi_state.king_wen_index`
  - `yi_state.upper_trigram`, `yi_state.lower_trigram`
  - `yi_state.moving_lines`, `yi_state.moving_line_policy`
  - `yi_state.transformed_hexagram_name`
  - `yi_state.source_ref`
- **Primary source**:
  - `thư viện sách/Kinh Dịch Trọn Bộ - Ngô Tất Tố - khoahoctamlinh.vn.pdf`
- **Confidence**: `medium`
- **TestHint**:
  - Dataset phải đủ 64 quẻ, không trùng binary/KingWen index.
  - Hào động áp dụng phải deterministic.

### RULE `bac.maihoa.ruler.tamthien_v1`

- **Input**:
  - `primary_hexagram`
  - `moving_lines`
  - `mai_hoa_environment`
  - `timing_prediction`
- **Logic**:
  - Áp dụng ruler 4 lớp từ ghi chú Tam Thiên:
    - `context`: Thoán (toàn quẻ) + môi trường ngũ hành.
    - `process`: Tượng (biến động hào) + trạng thái động/tĩnh.
    - `timing`: nhịp nhanh/chậm + phễu ứng kỳ.
    - `action`: hành động nên làm/hoãn/tránh.
  - Nếu dữ liệu đầu vào mơ hồ (question/profile yếu), hạ confidence và chuyển chế độ conservative.
- **Output**:
  - `ruler_profile.id = tam_thien_v1`
  - `ruler_profile.layers = [context, process, timing, action]`
  - `ruler_profile.confidence`
  - `ruler_profile.notes`
- **Primary source**:
  - `docs/research/mai-hoa/mai-hoa-ruler-notes-v1.md`
  - `thư viện sách/Tam Thiên Dịch Số.pdf` (Định Hệ Từ + Bảng truy tầm 64 thức hệ)
- **Confidence**: `medium-low` (đã có khung, cần đọc bổ sung để nâng bản)
- **TestHint**:
  - Cùng input phải cho cùng `ruler_profile`.
  - Input thiếu rõ ràng phải hạ confidence theo rule.

### RULE `bac.calendar.convert.solar_lunar_vn`

- **Input**:
  - `datetime_local`
  - `timezone`
  - `source_calendar` (`solar`/`lunar`)
  - `is_leap_month`
- **Logic**:
  - Dùng thuật toán âm dương lịch VN (Julian day + New Moon + Sun Longitude).
  - Chuyển đổi 2 chiều âm/dương có xét tháng nhuận.
- **Output**:
  - `converted_datetime_local`
  - `target_calendar`
  - `is_leap_month`
- **Confidence**: `medium`
- **TestHint**:
  - Round-trip test: solar -> lunar -> solar phải khớp ngày.

### RULE `bac.compare.basic.v1`

- **Input**:
  - `birth_datetime_local`
  - `timezone`
  - `location_ref` (optional)
- **Logic**:
  - Tạo snapshot chronos + lấy vector hành tinh tại thời điểm sinh.
  - Chấm check cơ bản theo khung thời gian, pha trăng, vector Trái Đất.
- **Output**:
  - `checks[]`
  - `confidence`
  - `report_markdown`
- **Confidence**: `medium-low` (định hướng so sánh cơ bản, chưa phải phán định tuyệt đối)
- **TestHint**:
  - Báo cáo phải luôn kèm `ziwei_ruleset_id`.

### RULE `bac.almanac.vannien.basic`

- **Input**:
  - `datetime_local`
  - `timezone`
  - `cycle_60_idx`, `month_idx`, `hour_idx`
- **Logic**:
  - Chuyển đổi âm lịch cơ bản theo lịch VN.
  - Suy ra thứ trong tuần, trực ngày và nhãn vận hạn mức cơ bản cho năm/tháng/ngày/giờ.
- **Output**:
  - `almanac.lunar_date`
  - `almanac.weekday_vi`
  - `almanac.truc_of_day`
  - `almanac.annual_fortune`, `monthly_fortune`, `daily_fortune`, `hourly_fortune`
- **Confidence**: `medium-low` (khung vận hành cơ bản cho MVP, chưa bao trùm toàn bộ thần sát Bắc phái)
- **TestHint**:
  - Với cùng timestamp/timezone, block `almanac` phải ổn định và lặp lại.

## 4) Quy tắc vận hành API

Mọi API chính liên quan tính toán/lịch/so sánh phải trả về:

- `ziwei_school`
- `ziwei_ruleset_id`
- (khuyến nghị) `ziwei_ruleset_label`

Mục đích: truy vết kết quả theo đúng chuẩn đã chốt.

## 5) Out-of-scope trong `bac_phai_v1`

- Chưa triển khai đầy đủ 108 sao Bắc phái theo bảng an sao chi tiết.
- Chưa có phi hóa nâng cao theo từng tầng đại hạn/lưu niên/lưu nguyệt/lưu nhật/lưu thời.
- Chưa có bộ đối chiếu đúng-sai tuyệt đối với học phái khác.

## 6) Tiêu chí nâng version

Nâng từ `bac_phai_v1` lên `bac_phai_v1.1+` khi:

1. Có bổ sung rule mới + provenance sách rõ ràng.
2. Có test regression đi kèm.
3. Không phá backward compatibility của output contract (hoặc có migration note).
