# ADR — Hồ sơ mệnh-lý 3 TẦNG + versioning (chuẩn cho YI + AppChat)

> Ngày: 2026-06-18 · Trạng thái: **CHỐT (Anh duyệt)** · Phạm vi: YI-Chronos (lõi) + AppChat (tiêu thụ).
> Nền: H6.0 đã LIVE (council/quick + cache + evolve_gate + RLS). ADR này chuẩn hoá cách *chuẩn bị trước* hồ sơ mệnh-lý.

## 1. Bối cảnh / vấn đề
Phục vụ triệu user, cần: hồ sơ mệnh-lý "luôn sẵn sàng", lớn dần theo sách mới, **nhưng không đốt tiền** (không pre-generate prose LLM cho mọi user). Phải tách rõ **cái tất định (rẻ)** khỏi **cái LLM (đắt)** và **cái chung** khỏi **cái riêng**.

## 2. Quyết định — MÔ HÌNH 3 TẦNG

| Tầng | Là gì | Phạm vi | Tính sẵn? | Chi phí |
|---|---|---|---|---|
| **T1 — KIẾN THỨC CHUNG** | wiki + skill + sage + "lăng kính" (cách đọc cách cục, lời quẻ…) | **CHUNG** mọi user | có (versioned) | 1 lần / cả hệ |
| **T2 — DỮ KIỆN RIÊNG** | lá số an sao / tứ trụ / cách cục-match / quẻ của CHÍNH user | **RIÊNG** (RLS) | **CÓ — pre-compute + cache** | rẻ (engine tất định) |
| **T3 — LUẬN GIẢI** | prose LLM = ghép T1 × T2 | RIÊNG kết quả | **KHÔNG pre-gen** — lazy khi hỏi + cache | đắt → tier + cache |

**Nguyên tắc vàng:** *"Chuẩn bị trước" = T1 + T2 + cấu trúc mẫu. T3 (LLM) luôn lazy-sinh + cache, KHÔNG pre-generate cho mọi user.*

## 3. Versioning (mấu chốt để sách mới lan đúng)
- **`knowledge_version`** (số nguyên toàn hệ): bump mỗi khi `evolve_gate` DUYỆT cập nhật T1 (sách mới / lăng kính mới / sage mới).
- **`profile_schema_version`**: version cấu trúc mẫu T2 (khi thêm trường dữ kiện mới).
- **Cache T3 key** = `hash(chart_facts + intent + câu hỏi chuẩn hoá) + knowledge_version + algo_version`.
  → sách mới bump `knowledge_version` ⇒ cache cũ **tự hết hạn** ⇒ lần hỏi sau luận lại với kiến thức mới. (Mở rộng `engine/hermes_service._cached` hiện tại: thêm version vào khoá thay vì chỉ TTL 24h.)

## 4. Sách mới ảnh hưởng user thế nào (ĐÚNG cách)
```
Sách mới → distill → evolve_gate DUYỆT → T1 lớn lên + bump knowledge_version
   • Lá số user (T2) KHÔNG đổi (chart cố định) — chỉ MỞ THÊM lăng kính mới.
   • KHÔNG re-generate prose cho mọi user.
   • Cache T3 (theo version) tự vô hiệu → lần hỏi tới luận bằng kiến thức mới.
   • Đánh dấu "lăng kính mới khả dụng" → digest/proactive cho user liên quan (gói).
```

## 5. Data model (đề xuất tối thiểu, dual-driver engine.db)
- **T2** — `user_menh_profile(user_id PK, schema_version, facts_json, computed_at)`: bundle dữ kiện tất định (an sao/tứ trụ/cách cục…), tính lúc sync giờ sinh, RLS theo user_id. (Hoặc tái dùng `user_castings method='profile_facts'` nếu không muốn bảng mới — chọn bảng riêng cho rõ.)
- **T1 version** — `system_meta(key, value)` lưu `knowledge_version` (bump bởi `evolve_gate.review(approve)` khi kind đụng T1). Lăng kính = registry trong wiki/skill (đã có cấu trúc skill).
- **T3** — giữ `user_castings` (đã có) làm cache + lịch sử; thêm cột/khoá `knowledge_version` + `algo_version` (đã có algo_version) vào điều kiện cache.

## 6. Tác vụ cho dev (test-first, theo nếp P0/H6)
1. **`engine/menh_profile.py`**: `build_profile(user_id)` → tính T2 facts (gọi engine cast bat_tu/tu_vi/… theo person), lưu `user_menh_profile` + `schema_version`. Idempotent. Test dual-driver.
2. **`system_meta` + `knowledge_version`**: helper `get/bump_knowledge_version()`; gọi `bump` trong `evolve_gate.review` khi `approve` + impact chạm T1. Test.
3. **Sửa cache T3** (`hermes_service._cached`): đưa `knowledge_version` (+ `algo_version`) vào khoá → sách mới tự vô hiệu cache. Test: bump version → cache cũ miss.
4. **Profile sẵn sàng lúc sync**: `upsert-from-firebase` (hoặc job nền) gọi `build_profile` khi đã có giờ sinh → T2 luôn sẵn. Test.
5. **Lăng kính mới → proactive**: digest tuần thêm mục "lăng kính mới từ sách X" cho user gói. Test.
6. **(AppChat)** không đổi hợp đồng — chỉ hiển thị; tham chiếu plan `prvchat/.../2026-06-18-h6-hermes-appchat-integration.md`.

## 7. Ràng buộc (không được vi phạm)
- **Northstar:** mọi fact trong T3 phải khớp T2 (engine) — LLM KHÔNG bịa lá số.
- **Paradigm (Iron #4/#6/#8):** "khai mở thêm" = trích sâu T1 có dẫn nguồn, KHÔNG predict.
- **Chi phí:** T3 lazy + cache + tier (free nông, gói sâu) — quy tắc thu ≥10× chi phí LLM.
- **Privacy:** T2/T3 cô lập RLS; gửi LLM bản pseudonymize (không tên/uid/sđt).

## 8. Acceptance
- T2 tính sẵn sau sync (đọc tức thì, không LLM).
- Bump `knowledge_version` ⇒ cache T3 cũ miss ⇒ luận lại bằng kiến thức mới (test).
- Lá số user không đổi khi thêm sách; chỉ thêm lăng kính.
- Không có đường nào pre-generate prose LLM cho toàn bộ user.
