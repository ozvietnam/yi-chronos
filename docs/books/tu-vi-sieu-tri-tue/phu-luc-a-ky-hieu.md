# Phụ lục A — Bảng ký hiệu hình thức hoá

*《Tử Vi Tính Được》 · tra cứu nhanh các đối tượng toán học đã định nghĩa, kèm chỗ hiện thực trong engine YI-Chronos.*

| Ký hiệu | Nghĩa | Phần | Hiện thực engine |
|---|---|---|---|
| `b = (y,m,d,h,g)` | thời điểm sinh (năm/tháng/ngày/giờ âm + giới) | I.1 | input |
| `A : b ↦ L` | **an sao** — hàm thuần, tất định, sai số người = 0 | I.1 | `engine/tu_vi/an_sao.py` |
| `G = (V, E, λ)` | **lá số = đồ thị có nhãn** | I.2 | (suy từ `L`) |
| `V` | 12 đỉnh = 12 cung | I.2 | |
| `λ` | nhãn đỉnh = chức năng cung + tập sao + miếu-hãm | I.2 | |
| `E` | cạnh = tam hợp / xung chiếu / nhị hợp-giáp | I.2 | |
| `Γ = {C₁…C₅₄₅}` | **văn phạm cách cục** — mỗi `Cᵢ` là vị từ trên `G` | I.3 | `cach_cuc_dict.py`, `cach_cuc_index.json` |
| `Φ = (Định–Biến, Thụ–Tác, Nội–Ngoại, Cá-nhân–Siêu) ` | **không gian thái-độ-số-phận** (4 trục) | II.2 | (mô hình mới — cần seed) |
| `vₛ ∈ Φ` | vector thái-độ của sao `s` (embedding bảng Đằng Sơn) | II.2 | |
| `P(L) = Σ wₛ·vₛ` | **hồ sơ thái-độ-số-phận** của cả lá (trọng số `wₛ` theo miếu-hãm + cung) | II.3 | |
| `F : VũTrụ → LáSố → TínhNgười` | **functor đồng dạng** — bảo toàn *quan hệ* (không bảo toàn nhân quả) | III.2 | (Tam Tài) |
| `D(t)` | **đèn rọi Đại Vận** — chọn cung vận tại thập niên `t`, tái-trọng-số `G` | IV.2 | `dai_van` |
| `Y(t)` | **Lưu Niên** — bước thời gian mịn lồng trong `D(t)` | IV.2 | `luu_nien` |
| `Hₜ` | **toán tử Tứ Hoá** (Lộc/Quyền/Khoa/Kỵ) tác lên trạng thái sao tại `t` | II.3, IV.2 | |
| TÍNH ∈ "P" | cấu trúc bẩm phú — **khả tính** (A, G, Γ, F, D, Y đều tính được) | V.1 | ✅ tính |
| MỆNH ∉ khả-tính | sự vận hành — **bất khả tính** (tự do + tự-quy-chiếu + thông tin mở) | V.2 | ⛔ KHÔNG tính |

> Quy ước đọc: tất cả ký hiệu trên thuộc cõi **TÍNH** (tính được), trừ dòng cuối — ranh giới
> mà cuốn sách cung kính không bước qua.
