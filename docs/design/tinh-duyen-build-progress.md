# 💍 Sản phẩm GIEO DUYÊN — Tình duyên Nữ Mệnh (build tracker)

GOAL (Anh chốt 2026-06-24): sản phẩm gieo duyên **nữ-mệnh chuyên tình duyên** — Tử Vi + Bát Tự song song (hội tụ=chắc, lệch=sắc thái) · đọc theo **TUỔI (6 chặng) × TÍNH CÁCH × KHẨU VỊ giao tiếp** · paradigm KHÔNG bói · đẩy AppChat thu phí. Anh giao TỰ QUYẾT, dùng nhiều agent, không hỏi trước-sau.

## Chặng 1 — Nền tri thức ✅ XONG
6 file `engine/tinh_duyen/knowledge/*.json` (grounded sách thật, verified):
- `tuvi_phuthe.json` — 14 chính tinh cung Phu Thê + đào hoa + tứ hóa + sát + định thời + biện chính 王亭之
- `batu_hon_nhan.json` — 官杀(phu tinh)/日支(phối ngẫu)/đào hoa/tổ hợp/hợp hôn/định thời *(đã nắn khỏi `_meta`)*
- `tuvi_batu_reconcile.json` — 8 chủ đề đối chiếu song-engine (hội tụ/dị biệt)
- `personality_comm_style.json` — 14 chính tinh → khí chất + cách yêu + **khẩu vị giao tiếp** {giọng,độ dài,cách khung,nên,tránh} + đối chiếu 十神
- `cach_cuc_tinh_duyen.json` — **157 cách cục** tình duyên (điều kiện phát hiện + ý nghĩa)
- `life_stages.json` — 6 chặng tuổi {tuổi,môi trường,tâm lý,câu hỏi chính,giọng,độ sâu,gói,giá xu}

## Chặng 2 — Engine `tinh_duyen` ✅ XONG (paradigm-safe, pytest 38)
`engine/tinh_duyen/reading.py` :: `read_tinh_duyen(birth_datetime_local, gender='nữ', timezone, as_of_year)` — MỞ RỘNG `cross_paradigm/hon_nhan_song_phai`. Output dict keys: `method_id, input{tuoi,menh_branch,phu_the_branch}, stage{stage_id,moi_truong,tam_ly_cot_loi,cau_hoi_chinh,giong_van}, personality{menh_chinh_tinh,khi_chat,cach_yeu,khau_vi_giao_tiep{giong,do_dai,cach_khung,nen,tranh}}, cung_phu_the_tuvi, batu_hon_nhan, song_phai_reconcile[], cach_cuc[], dinh_thoi, base_12_khia_canh, paradigm_ok, scrub_caution_count, sources, _disclaimer`.
- ⚠️ **Bài học lớn**: phản biện đối kháng bắt được BLOCKER paradigm (build-pytest-xanh vẫn surface "khắc chồng/cô độc" cho bé gái 17t). Đã fix: reframe 157 cách cục → `bien_chinh` (đọc-đồng-dạng) + `gioi_tinh` flag (loại 30 phú góc-nhìn-nam khỏi nữ mệnh) + **hàng rào cứng `_scrub_tree`** (cấm verdict lexicon) + reuse `engine.hermes_guard`. Verified: forbidden=0 trên 6 lá nữ, moat-voice 36×, stage đúng (`stage_id`).
- Cast: `engine.tu_vi.from_birth.cast_la_so_from_birth` + `engine.bat_tu.cast.cast_bat_tu`. Tests: `tests/test_tinh_duyen.py` (38).

## Chặng 3 — Wiring ⏭️ CHỜ ENGINE (blueprint sẵn)
| Điểm ráp | File | Pattern |
|---|---|---|
| Service | `engine/cross_paradigm/service.py:150+` | `run_tinh_duyen(uid,person)` = `_chart_of` + `read_tinh_duyen` + `_charge_and_run(...,"cross_paradigm_tinh_duyen",sig,...)` (trừ `GIA_XU`=30, cache, hoàn xu nếu lỗi) |
| API web | `api/cross_paradigm.py:47` | `POST /api/cross-paradigm/tinh-duyen` + `require_caller` + `_person(uid,key)` → 402 insufficient_xu |
| API AppChat | `api/sync.py:1022` | `POST /api/sync/tinh-duyen` + `X-API-Key` + `_user_id_for_uid`+`_person_by_key`; chung service → ví xu trung tâm (không double-charge) |
| Sage narrate | `engine/cross_paradigm/narrate.py` (mới) | `narrate_tinh_duyen(...)` dùng `engine.ai.agents.run_agent` + `sage_model()` (DeepSeek `deepseek-chat` non-reasoning, nhanh). **Giọng = `output['personality']['khau_vi_giao_tiep']`** (engine đã tính sẵn!) → KHÔNG cần table riêng |
| UX | `client/webapp/src/components/GieoDuyenPanel.vue:14+` | thêm mode `'tinh'` + nút 💍 + `runTinh()` gọi `/api/cross-paradigm/tinh-duyen`; birth/gender từ `stores/tuviPersonStore.js` (`tuviPersonBirth/Gender`) |

Notes: cache `_charge_and_run` TTL 86400s; reason `cross_paradigm_tinh_duyen` → group admin `giao_duyen`; lưu `user_castings` → AppChat đọc lại qua `/api/sync/history`.
