# GIA ĐẠO — Trang gia đình & Luận lá số con cái

> Founder chốt 2026-06-18: *"cần bát tự của bố mẹ thì càng tốt, cho vào trang gia đạo, luận lá số cho Con cái."*
> Nền tư tưởng: **"mô hình hình thành con người"** — _con = trường năng lượng lúc sinh ⊗ gen bố mẹ ⊗ môi trường_ (Tam Tài hiện đại).

---

## GOAL

Trang **Gia Đạo** = nơi đọc cả **HỘ** (vợ chồng + con) như một trường năng lượng, KHÔNG chỉ từng cá nhân rời. Trọng tâm founder nhấn: **luận lá số con cái** — đọc cái NỀN bé được trao để biết hướng **nuôi dưỡng/dìu dắt**, không phán định đời bé.

## Vị trí trên web

Tab **"Gia đạo"** (`activeMainTab==='family'`, App.vue) render theo thứ tự:
1. **`GiaDaoPanel.vue`** — 4 mục: 🧭 Nếp nhà & đón con · **👶 Luận lá số con** (mới) · ✍️ Đặt tên con · 🏮 Phúc ấm & quan hệ.
2. `FamilySystemPanel.vue` — cộng hưởng đa thành viên (4 layer: quẻ ngày cưới, Thái Tuế nhập quái, Mai Hoa hợp nhất, element bridging).
3. `PersonalResonance` — hồ sơ.

## Tính năng "Luận lá số con" (shipped 2026-06-18)

**Backend**
- `engine/tu_vi/gia_dao.py::luan_la_so_con(child_ls, child_pillars, parents=None)`
- API `POST /api/tu-vi/luan-con` (`api/tu_vi_3layer.py`): input `birth_con`, `gender_con`, `bo_birth?`, `me_birth?`.
  - Lập lá số bé (`render_from_birth`) + Bát Tự bé (`extract_tu_tru`).
  - Bố/mẹ: từ ngày sinh → hành **nhật chủ** (giờ tuỳ chọn, mặc định 12:00 vì day-pillar ổn định).

**Đọc gì** (3 lớp):
1. **6 cung lăng kính TRẺ** — Mệnh (khí chất), Phụ Mẫu (duyên cha mẹ + nẻo học), Phúc Đức (phúc ấm), Tật Ách (thân, chỗ chăm), Huynh Đệ (bạn/anh em), Quan Lộc (mầm thiên hướng). Mỗi cung: chính tinh → **khí chất bẩm** + **hướng dìu**. Vô chính diệu → "môi trường định hình mạnh".
2. **Bát Tự → dụng thần** = hành con CẦN → **hướng nuôi** (môi trường/hoạt động/màu mang hành đó). Văn tinh (Xương/Khúc/Hóa Khoa) chiếu Mệnh/Quan/Phụ Mẫu → duyên chữ nghĩa.
3. **Trường năng lượng Bố Mẹ ⊗ cái con cần** (nếu có bát tự bố mẹ): hành nhật chủ bố/mẹ vs dụng thần con → sinh/đồng/khắc-nhẹ/trung tính → **hướng nuôi**, KHÔNG chấm điểm bố mẹ hợp/khắc con.

## Đạo đọc (Iron Rule #4/#6 — thận trọng GẤP ĐÔI vì trẻ em)

- Đọc **THỂ** (cái nền: khí chất, thân, phúc), KHÔNG phán **DỤNG** (bé sẽ sống ra sao). **Mệnh là dịch** — bé lớn lên tự viết phần DỤNG ([[founder_menh_la_dich]]).
- Không hù doạ, không "số bé sẽ…". Mọi điều = **thiên hướng cần vun**, không phải bản án.
- Trường bố mẹ = để biết **hướng nuôi**, không phải "bố/mẹ khắc con".

## Liên hệ Thiết Bản 考刻

Bát tự bố mẹ thu ở trang này **đồng thời** là dữ kiện cho **考刻 Thiết Bản** (neo khắc/phân cần bát tự cha mẹ + sự kiện đời) — xem `docs/design/THIET-BAN-KHOI-SO.md` §5. Khi có bảng 纳卦 từng 集 + cặp kiểm, 考刻 nối thẳng vào đây.

## Chưa làm (đường tới)

- Lưu hộ (cha/mẹ/con) vào `persons.sqlite3` + `relationships.py` (parent/child sẵn có) để khỏi nhập lại; auto đọc khi chọn người.
- Lời văn ấm (LLM) cho bản luận con — như `duyen-tho` đã làm cho Duyên.
- Nối 考刻 Thiết Bản khi keystone đủ bảng 纳卦 + cặp kiểm.
