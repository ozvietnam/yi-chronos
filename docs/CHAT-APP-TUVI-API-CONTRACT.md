# API Contract — Tích hợp "Tử Vi" cho App Chat

> **Đối tượng đọc:** đội phát triển app chat (client + backend của app chat).
> **Backend cung cấp:** YI-Chronos (FastAPI, `api/main.py`).
> **Cập nhật:** 2026-06-13. Mọi schema dưới đây **introspect trực tiếp từ Pydantic model thật** + smoke test live (`TestClient`), không phải tài liệu giả định.

"Tử Vi" là **tên gọi chung** user nhìn thấy. Thực tế backend phục vụ nhiều môn: **Tử Vi Đẩu Số, Tứ Trụ (Bát Tự), Kinh Dịch (Lục Hào / Hà Lạc), So khớp tình duyên, và module Tìm lại giờ sinh**. App chat có thể bắt đầu với một mặt và mở dần.

---

## 0. Trạng thái sẵn sàng (đọc trước)

| Khối | Trạng thái | Ghi chú |
|---|---|---|
| Lập lá số: Tử Vi / Bát Tự / Hà Lạc | ✅ **LIVE** | Không cần LLM, không cần DB. 200 OK đã verify. |
| Lập quẻ: Lục Hào | ✅ **LIVE** | Cần `interaction_signal` (entropy động tác). |
| So khớp tình duyên (Bát Tự + Hôn nhân nạp âm) | ✅ **LIVE** | Offline, không cần LLM/DB. |
| **Tìm lại giờ sinh (quiz v2)** | ✅ logic LIVE · ⚠️ **cần LLM** | Provider đã chốt: **MiniMax token plan**. Không có provider → endpoint trả `status:error`. |
| Hiệu chỉnh giờ theo **khu vực sinh** (true-solar-time) | 🟡 **PLANNED** | Đã chốt sẽ làm. Hiện backend chỉ map timezone. Xem §6. |
| Auth / rate-limit | 🟡 **ĐỀ XUẤT** | Xem §1. Hiện endpoint public. |

---

## 1. Auth — đề xuất (chưa implement)

App chat đã xác thực user bằng **SĐT + email**. Không nên dựng lại auth ở YI-Chronos. Đề xuất mô hình **server-to-server tin cậy**:

- App chat gọi YI-Chronos **từ backend của app chat** (không gọi trực tiếp từ mobile client).
- Mỗi request kèm header:
  - `X-API-Key: <khóa dịch vụ dùng chung>` — xác thực rằng caller là app chat.
  - `X-User-Id: <id user đã đăng nhập bên app chat>` — để rate-limit theo user + gắn hồ sơ person.
- YI-Chronos **tin** `X-User-Id` (đã được app chat xác thực), không tự verify SĐT/email.
- Rate-limit: theo `X-User-Id` (vd quiz giờ sinh tốn LLM → giới hạn N session/ngày/user).

> Em (YI-Chronos) implement lớp này khi anh duyệt. Trước khi có, endpoint đang public — app chat **phải** gate ở tầng của mình.

**Base URL (prod):** `https://<yi-chronos-host>` · **Content-Type:** `application/json`.

---

## 2. Quy ước chung

| Mục | Quy ước |
|---|---|
| **Định dạng giờ** | `birth_datetime_local` / `datetime_local` = ISO local, vd `"1990-08-20T09:30:00"`. **Không** kèm offset — timezone tách riêng. |
| **Timezone** | mặc định `"Asia/Ho_Chi_Minh"`. |
| **Giới tính** | **BẮT BUỘC đúng chuỗi `"nam"` hoặc `"nữ"` (có dấu).** Gửi `"nu"`, `"female"`… → engine raise lỗi. |
| **Ngày âm/dương** | Tử Vi nhận **cả 2 mode** (xem §3.1). Bát Tự/Hà Lạc nhận **dương lịch**, tự convert nội bộ. |
| **Paradigm guardrail** | Output là **"đọc đồng dạng"**, KHÔNG phải tiên tri cát/hung. UI/copy app chat **không** được khung kiểu bói tương lai (xem field `paradigm_guard` trong response). |

---

## 3. BÀI TOÁN A — Lập lá số / quẻ

### 3.1 Tử Vi Đẩu Số — `POST /api/tu-vi/cast`

**Request** (2 mode, chọn 1):

```jsonc
// Mode tiện lợi (khuyến nghị cho app chat): dương lịch
{ "birth_datetime_local": "1990-08-20T09:30:00", "timezone": "Asia/Ho_Chi_Minh",
  "gender": "nữ", "include_interpretation": true }

// Mode trực tiếp: nhập thẳng can/chi âm lịch (khi đã biết)
{ "lunar_month": 7, "lunar_day": 1, "hour_branch": "Tỵ",
  "year_stem": "Canh", "year_branch": "Ngọ", "gender": "nữ" }
```

| Field | Kiểu | Bắt buộc | Mặc định |
|---|---|---|---|
| `birth_datetime_local` | string ISO | mode tiện lợi | `null` |
| `lunar_month`,`lunar_day` | int | mode trực tiếp | `null` |
| `hour_branch`,`year_stem`,`year_branch` | string | mode trực tiếp | `null` |
| `gender` | `"nam"\|"nữ"` | — | `"nam"` |
| `timezone` | string | — | `Asia/Ho_Chi_Minh` |
| `target_year` | int | — | `null` (lưu niên) |
| `include_interpretation` | bool | — | `true` |

**Response 200:** `{ algorithm_version, input_resolved, la_so{ menh_index, menh_branch, than_index, 12 cung + sao… }, interpretation }`.

### 3.2 Tứ Trụ / Bát Tự — `POST /api/bat-tu/cast`

```json
{ "birth_datetime_local": "1990-08-20T09:30:00", "timezone": "Asia/Ho_Chi_Minh", "gender": "nữ" }
```
**Response 200:** `{ algorithm_version, bat_tu_state{ tu_tru, thap_than_meanings, thap_than_distribution, ngu_hanh, truong_sinh, than_sat, … } }`.

**Luận giải sâu (cùng request shape, thêm `current_age?`):**
`/api/bat-tu/luan-giai` · `/luu-nien` · `/hon-nhan` · `/su-nghiep` · `/tai-van` · `/suc-khoe` · `/luc-than` · `/bao-menh-pdf` (trả PDF).

### 3.3 Kinh Dịch — Hà Lạc — `POST /api/ha-lac/cast`

```json
{ "birth_datetime_local": "1990-08-20T09:30:00", "timezone": "Asia/Ho_Chi_Minh", "gender": "nữ" }
```
**Response 200:** `{ algorithm_version, ha_lac_state{ 2 quẻ Tiên/Hậu thiên + decade trajectory } }`.

### 3.4 Kinh Dịch — Lục Hào — `POST /api/luc-hao/cast`

Quẻ sinh từ **entropy động tác** của user (giữ + di chuyển ngón tay trên màn hình). App chat **bắt cử chỉ** rồi gửi 4 chỉ số:

```json
{ "datetime_local": "2026-06-13T11:40:00", "timezone": "Asia/Ho_Chi_Minh",
  "question_text": "Câu hỏi của user",
  "interaction_signal": { "hold_duration_ms": 1200, "move_event_count": 3,
                          "path_length_px": 42.5, "release_timestamp_ms": 1718276400000 } }
```
**Tất cả 4 field `interaction_signal` đều bắt buộc.** **Response 200:** `{ luc_hao_state{ primary_hexagram, transformed_hexagram, moving_lines, the_line, ung_line, dung_than, timing_prediction, … } }`.

> Nếu app chat chỉ có text-box (không bắt được cử chỉ): báo em thêm **mode gieo thủ công** (6 hào / 3 đồng xu). Chưa có sẵn.

---

## 4. BÀI TOÁN B — Tìm lại giờ sinh (user không nhớ giờ)

Module **`birth-hour-quiz-v2`**: quiz tương tác nhiều vòng, loại dần 12 giờ ứng viên dựa trên đặc điểm user. Suy **22 trait / 5 domain** mỗi giờ (ngoại hình · tính cách · năng lượng đồng hồ TCM · biến cố đời gồm thời điểm kết hôn · tật ách/bệnh sử) → hỏi câu phân biệt → scoring.

> ⚠️ **Cần LLM provider = MiniMax** (đã chốt). Domain tính cách + biến cố đời suy từ LLM. Nếu user chọn "không nhớ gì" (12 ứng viên) → LLM tải nặng, nên gợi ý user thu hẹp buổi (sáng/trưa/chiều/tối).

### 4.1 Bắt đầu — `POST /api/yi-wiki/birth-hour-quiz-v2/start`

```jsonc
{ "birth_date": "1990-08-20", "timezone": "Asia/Ho_Chi_Minh", "gender": "nữ",
  "hour_range": { "start": 6, "end": 12 } }   // optional — user nhớ mang máng buổi nào
```
**Response 200:**
```jsonc
{ "status": "ok", "session_id": "<sid>",
  "candidates": ["Mão","Thìn","Tỵ","Ngọ"],          // giờ ứng viên còn lại
  "strategy": "two_round",                            // single_round | two_round | three_round
  "round_1": { "round_num": 1, "total_rounds": 2, "questions": [ <Question> ] } }
```
`status:"error"` khi LLM chưa cấu hình (`message` + `hint`).

**Cấu trúc `<Question>`** (app chat render + thu answer):
```jsonc
{ "id": "introvert_extrovert",            // = trait_id, dùng làm KEY khi submit
  "question": "Bạn thiên về…?",           // text tiếng Việt
  "domain": "personality",
  "options": [
    { "id": "introvert", "label": "Hướng nội", "candidates": ["Mão","Tỵ"] },
    { "id": "extrovert", "label": "Hướng ngoại", "candidates": ["Thìn","Ngọ"] },
    { "id": "unsure",    "label": "Tôi không rõ / khó nói", "candidates": [] } ],
  "weight": 0.8 }
```

### 4.2 Nộp 1 vòng — `POST /api/yi-wiki/birth-hour-quiz-v2/submit-round`

```jsonc
{ "session_id": "<sid>", "round_num": 1,
  "answers": { "introvert_extrovert": "introvert", "<trait_id>": "<option_id>" } }
```
`answers` = map **`question.id` → `option.id`**.

**Response 200 — 1 trong 2 nhánh:**
```jsonc
// còn vòng:
{ "status": "CONTINUE", "scores": {...}, "candidates_remaining": [...],
  "next_round": { "round_num": 2, "total_rounds": 2, "questions": [ <Question> ] },
  "final_result": null }

// xong:
{ "status": "FINAL",            // hoặc "FINAL_UNCERTAIN"
  "scores": {...}, "candidates_remaining": ["Tỵ"],
  "final_result": { "top_chi": "Tỵ", … } }
```

### 4.3 Lấy lại session — `GET /api/yi-wiki/birth-hour-quiz-v2/session/{session_id}`

### 4.4 Lưu kết quả — `POST /api/yi-wiki/birth-hour-quiz-v2/save-result`

```json
{ "session_id": "<sid>", "person_id": "<id hồ sơ>" }
```
Ghi giờ suy ra vào hồ sơ person (`birth_confidence: "approx_hour"`). **Response:** `{ status, person_id, birth_datetime_local, inferred_chi }`. Sau đó dùng `birth_datetime_local` này gọi `/api/tu-vi/cast` để ra lá số đầy đủ.

> **Luồng app chat đề nghị:** user không nhớ giờ → `start` → lặp `submit-round` đến `FINAL` → `save-result` → `tu-vi/cast`.

---

## 5. BÀI TOÁN C — So khớp tình duyên

App chat cần **ghi nhận đường tình duyên** của user và **so khớp khi user yêu cầu**.

### 5.1 Đọc tình duyên từ chính lá số user

- `POST /api/bat-tu/hon-nhan` — luận hôn nhân (request = `{birth_datetime_local, timezone, gender}`).
- `POST /api/tu-vi/cung-phu-the/bac-phai` — cung Phu Thê + **đặc điểm bạn đời dự kiến**.
- Trait `marriage_timing_rough` (thời điểm kết hôn ước lệ) cũng có trong quiz §4.

### 5.2 So khớp 2 người — `POST /api/bat-tu/compatibility` ✅ (offline)

```json
{ "person_a_birth": "1990-08-20T09:30:00", "person_a_gender": "nữ",
  "person_b_birth": "1988-03-15T07:30:00", "person_b_gender": "nam",
  "timezone": "Asia/Ho_Chi_Minh", "relationship_type": "spouse" }
```
`relationship_type` ∈ `"spouse"` · `"partner"` · `"parent_child"` · `"sibling"` (mặc định `"spouse"`).

**Response 200:** `{ chart_a, chart_b, compatibility{ paradigm_guard, nap_am, day_master_compat, cung_phoi, ngu_hanh_dynamics, spouse_check, overall, closing } }`.

### 5.3 So khớp hôn nhân nhanh (nạp âm) — `POST /api/yi-wiki/marriage-compat` ✅

```json
{ "birth_a_iso": "1990-08-20T09:30:00", "birth_b_iso": "1988-03-15T07:30:00",
  "name_a": "An", "name_b": "Bình" }
```
**Response 200:** `{ status, person_a, person_b, nap_am_relation, chi_relation, nhat_chu_relation, total_score, grade, summary, blessings, warnings }`. Nhẹ, hợp cho preview/kết quả nhanh.

> **Lưu hồ sơ đối tượng để so khớp lại:** dùng person store `engine/yi_hermes/persons` (đã có), hoặc app chat tự lưu rồi gọi API stateless. Chốt ở §7 item 4.

---

## 6. Khu vực sinh → hiệu chỉnh giờ mặt trời thật (🟡 PLANNED — đã duyệt)

Hiện backend chỉ dùng **timezone**, chưa hiệu chỉnh theo **kinh độ nơi sinh**. Đã chốt sẽ thêm **true-solar-time correction** (lệch giữa giờ đồng hồ và giờ mặt trời thật theo kinh độ tỉnh/thành) — quan trọng vì **giờ là biến bất định nhất**, ảnh hưởng trụ Giờ ở ranh giới canh.

**Khi triển khai**, các endpoint nhận birth time sẽ thêm field **optional** (backward-compatible):
```jsonc
{ "birth_province": "Lạng Sơn" }      // hoặc:
{ "birth_longitude": 106.76 }          // độ kinh Đông
```
App chat nên **thu thập khu vực sinh ngay từ form** để sẵn sàng, kể cả trước khi backend bật tính năng.

---

## 6b. Lịch sử & version (✅ LIVE 2026-06-17) — H1/H2/H3

Hợp đồng để **mọi lần hỏi / lá số / so khớp đều được lưu thành lịch sử**, và để cache
diễn giải bên app chat **tự làm tươi** khi YI nâng cấp engine ("mỗi tuần một khám phá").
Tất cả dùng auth **service-to-service** giống §1 (`X-API-Key` + `firebase_uid` trong body/path).
Điều kiện: user đã được sync trước qua `POST /api/sync/upsert-from-firebase` (nếu chưa → `404`).

### H3 — Version contract

`GET /api/version` (nhẹ, không auth — chỉ là số version):
```json
{ "algo_version": "mvp-0.1.0",
  "ziwei_ruleset": "bac_phai_v1",
  "methods": { "tu_vi": "tu_vi-1", "bat_tu": "bat_tu-1", "couple_match": "couple_match-1", "...": "..." },
  "server_time": 1750000000 }
```
App chat lưu `algo_version` (toàn cục) **và** `methods[<method>]` kèm mỗi reading đã cache.
Khi gọi lại: **khác version → refetch** (ghi đè cache); **trùng version nhưng quá TTL 24h → refetch**;
**trùng + trong TTL → dùng cache**. (Chi tiết §5bis spec gieo duyên.)

### H1 — Lưu lịch sử (app chat đẩy sang sau khi cast/so khớp)

`POST /api/sync/castings` — một lần cast/luận:
```json
{ "firebase_uid": "abc", "method": "tu_vi",
  "subject_person_key": "self", "question": "Lá số của tôi?",
  "input_json": { "...": "đầu vào" }, "result_json": { "...": "kết quả engine" },
  "verdict": null, "tags": null, "note": null }
```
→ `200 { "status":"ok", "id": 12, "algo_version": "mvp-0.1.0+tu_vi-1" }`
(YI tự đóng dấu `algo_version` theo `method` — app chat không cần gửi.)

`POST /api/sync/favorites` — một mục đã lưu (vd gieo duyên):
```json
{ "firebase_uid": "abc", "kind": "couple_match",
  "label": "Tôi × Lan Anh", "payload_json": { "score": 82 } }
```
→ `200 { "status":"ok", "id": 5 }`

### H2 — Đọc lịch sử hợp nhất (dựng tab "Lịch sử")

`GET /api/sync/history/{firebase_uid}?type=&method=&kind=&limit=50&offset=0`
- `type`: `casting` | `favorite` | bỏ trống (cả hai)
- `method`: lọc trong castings · `kind`: lọc trong favorites
```json
{ "found": true, "yi_user_id": 3, "total": 12, "count": 2,
  "items": [
    { "type":"casting", "id":12, "method":"tu_vi", "question":"…",
      "result":{…}, "verdict":null, "algo_version":"mvp-0.1.0+tu_vi-1", "created_at":1750000000 },
    { "type":"favorite", "id":5, "kind":"couple_match", "label":"Tôi × Lan Anh",
      "payload":{"score":82}, "created_at":1749990000 }
  ] }
```
Mới nhất trước. `found:false` nếu uid chưa sync. Test: `tests/test_sync_history.py`, `tests/test_version_contract.py`.

---

## 6c. Gieo Duyên — Tử Vi & Gợi ý bạn đời (✅ LIVE 2026-06-17) — G1/G2/G3/G4

Hàm thuần xác định (KHÔNG cần LLM/DB), mỗi response mang `algo_version` (freshness §5bis).
Paradigm guard "đọc đồng dạng, không tiên tri" có trong mọi response (mặt tiền diễn đạt lại — Q1).

### G1 — Hồ sơ suy diễn (cụm A): nạp âm + cung mệnh Bát Trạch
`POST /api/bat-tu/profile-derived` → `{ "birth_year": 1986, "gender": "nam" }`
```json
{ "algo_version": "mvp-0.1.0+profile_derived-1",
  "profile_derived": {
    "nap_am": { "element":"hỏa", "name":"Lư Trung Hỏa", "can_chi":"Bính Dần" },
    "cung_menh": { "quai":"...", "element":"...", "menh_group":"dong|tay",
                   "menh_group_label":"Đông/Tây Tứ Mệnh", "label":"..." },
    "paradigm_guard": "..." } }
```

### G2 — Tuổi hợp (cụm B)
`POST /api/bat-tu/compatible-years` → `{ "birth_year":1990, "gender":"nam", "span":10, "top":6 }`
```json
{ "algo_version":"mvp-0.1.0+compatible_years-1", "paradigm_guard":"...",
  "compatible_years":[ {"year":1991,"can_chi":"Tân Mùi","age_gap":-1,
                        "score":5,"grade":"Rất hợp","reason":"Ngọ+Mùi lục hợp; ..."} ] }
```

### G3 — Tuổi kết hôn (cụm C) — cần giờ sinh
`POST /api/bat-tu/marriage-years` → `{ "birth_datetime_local":"1990-08-20T09:30:00",
"gender":"nam", "timezone":"Asia/Ho_Chi_Minh", "from_year":2026, "count":3, "scan":6 }`
```json
{ "algo_version":"mvp-0.1.0+marriage_years-1", "paradigm_guard":"...",
  "marriage_years":[ {"year":2026,"can_chi":"Bính Ngọ","score":3,"grade":"Hợp","reason":"..."} ] }
```

### G4 — So khớp hàng loạt (cụm D): compatKey + batch
Trước hết AppChat lưu sẵn **compatKey** mỗi người (rẻ, không cần giờ sinh): can-chi năm +
nạp âm (+ nhật chủ nếu có). Hình dạng compatKey = `{year, year_can_chi, year_branch, nap_am_element, day_master?}`.
`POST /api/bat-tu/compat-batch`:
```json
{ "anchor": {"year":1990,"year_branch":"Ngọ","nap_am_element":"thổ","day_master":"Giáp"},
  "candidates": [ {"id":"u1","year":1991,"year_branch":"Mùi","nap_am_element":"thổ","day_master":"Kỷ"} ] }
```
→
```json
{ "algo_version":"mvp-0.1.0+couple_match-1", "paradigm_guard":"...", "count":1,
  "scores":[ {"id":"u1","score":8,"percent":99,"stars":5,"grade":"Rất hợp","highlight":"..."} ] }
```
1 lời gọi cho N ứng viên (giữ YI single-source, tránh O(N) request). Lưu kết quả là `couple_match` qua §6b/H1.
Test: `tests/test_gieo_duyen.py`.

---

## 7. Hạng mục cần chốt tiếp (roadmap)

| # | Hạng mục | Trạng thái |
|---|---|---|
| 1 | Wire **MiniMax** cho quiz giờ sinh + chạy E2E start→submit→save | ✅ provider đã chốt — chờ em wire |
| 2 | **True-solar-time** theo khu vực sinh (§6) | đã duyệt — chờ em làm |
| 3 | **Auth + rate-limit** (§1) | em đề xuất — chờ anh duyệt |
| 4 | Chuẩn lưu **hồ sơ tình duyên / person** (yi_hermes vs app chat tự lưu) | ✅ chốt: YI là sổ cái — lịch sử qua §6b (H1/H2), person qua `/api/sync/*` |
| 5 | **Mode gieo Lục Hào thủ công** (nếu app chat không bắt cử chỉ) | tùy nhu cầu |

---

## 8. Mã trạng thái

- `200` + body: thành công (lưu ý vài endpoint trả `{"status":"error", …}` trong body 200 — app chat phải đọc field `status`, không chỉ HTTP code).
- `422`: sai schema request (thiếu field bắt buộc, sai kiểu). Body liệt kê field lỗi.
- `500`: lỗi engine (vd thiếu provider ở endpoint cần LLM).

> Mọi schema trong doc này khớp Pydantic model tại thời điểm cập nhật. Khi engine đổi, doc cập nhật theo cùng commit.

## 6d. Luận sâu DeepSeek — H5 (✅ orchestration 2026-06-17, async, gói trả phí)

Job dài (~30–90s) → **async qua Celery `q_deepread`**. Gói trả phí (`tu_vi_phe_menh_sau`).
Bọc engine `TuViAnalyzer.phe_menh()` + gating + hard-stop ngân sách LLM + lưu lịch sử + trừ lượt.

### Tạo job
`POST /api/sync/deep-reading` (service key) → `{ "firebase_uid":"abc", "person_key":"self" }`
- Pre-check nhanh: `404` chưa sync · `422` thiếu giờ sinh · `403` không có quyền (gói).
- Hợp lệ → `200 { "status":"processing", "job_id":"<celery-id>" }`.

### Poll trạng thái
`GET /api/sync/deep-reading/{job_id}` (service key) →
`{ "job_id", "state":"PENDING|STARTED|SUCCESS|FAILURE", "result"?: {...} }`
- `state=SUCCESS` → `result = { "status":"done", "casting_id", "algo_version", "provider", "remaining_uses" }`.
- Kết quả luận sâu lưu vào `user_castings` (method `tu_vi`, tag `deep,phe_menh`) → đọc lại qua §6b history.

### An toàn
- **Hard-stop ngân sách**: nếu chi LLM ngày ≥ `LLM_DAILY_BUDGET_USD` → job trả `budget_exceeded`, KHÔNG gọi LLM.
- **Không tính phí khi lỗi**: generation lỗi → KHÔNG `consume_use`, KHÔNG `record_spend`.
- **Pseudonymize**: chỉ chart facts vào LLM (không tên/uid). Test: `tests/test_deep_reading.py`.
