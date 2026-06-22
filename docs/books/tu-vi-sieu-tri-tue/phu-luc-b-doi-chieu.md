# Phụ lục B — Đối chiếu attribution: cổ-văn vs Đằng-Sơn vs mô-hình-mới

*《Tử Vi Tính Được》 · vận hành guardrail của phái `tu_vi_dang_son`: mọi luận điểm phải gắn
nguồn — `cổ-văn` (bám Toàn Thư/Trung Châu), `đằng-sơn` (sáng tạo của Đằng Sơn), `mô-hình-mới`
(hình thức hoá của cuốn này), hay `metaphor` (ẩn dụ, KHÔNG phải chứng cứ). Bảng v0.1 — **cần
đối chiếu corpus `wiki.sqlite3` để xác nhận cột cuối** (việc chưa làm, đánh dấu ⏳).*

| Luận điểm trong sách | Phần | Tag | Trạng thái đối chiếu |
|---|---|---|---|
| An sao là hàm tất định | I.1 | `cổ-văn` (an sao kinh điển) + `mô-hình-mới` (gọi tên "hàm") | ✅ chắc |
| Lá số = đồ thị; ý nghĩa sao ở *vị trí*/hội hợp | I.2 | `cổ-văn` ("sao không đứng một mình") + `mô-hình-mới` (đồ thị) | ✅ chắc |
| 545 cách cục = văn phạm | I.3 | `cổ-văn` (Phú Thái Vi) + `mô-hình-mới` (văn phạm) | ✅ chắc |
| Mỗi sao = một *thái độ với số phận* | II.1 | `đằng-sơn` (trực giác gốc) | ⏳ đối chiếu bảng gốc đủ 14 sao |
| Nhãn Destinism/Fatalism… cho từng sao | II.1 | `đằng-sơn` — **lỏng, không chuẩn triết học** | ⏳ giữ làm gợi ý, không chân lý |
| Không gian thái-độ 4 trục + vector sao | II.2 | `mô-hình-mới` (ta hình thức hoá + mở rộng Đằng Sơn) | ⏳ pattern-mining kiểm |
| Đồng dạng / Tam Tài | III.1 | `cổ-văn` (Vận Pháp Thi, Thiệu Khang Tiết — Iron #4) | ✅ chắc |
| Đồng dạng = functor; tương ứng ≠ nhân quả | III.2–3 | `mô-hình-mới` (ngôn ngữ phạm trù) | ✅ (diễn đạt mới của ý cổ) |
| "Thái Cực = sóng hấp dẫn / bẻ cong không-thời-gian" | 0.1, IV.4 | `metaphor` (Đằng Sơn) — **ẩn dụ, KHÔNG phải vật lý** | ✅ đã gắn cờ rõ |
| Đại Vận/Lưu Niên = hệ động lực (đèn rọi) | IV.2 | `cổ-văn` (hành vận) + `mô-hình-mới` (hệ động lực) | ✅ chắc |
| "Xem vận" = kích hoạt chủ đề, KHÔNG dự báo sự kiện | IV.3 | `cổ-văn`-paradigm (Iron #4/#6) + `mô-hình-mới` | ✅ chắc |
| Mệnh là động từ; "cùng lý–tận tính–chí ư mệnh" | V.3, 0.2 | `cổ-văn` (Quan Vật Nội Thiên — Iron #8) | ✅ chắc |
| "P vs NP của số mệnh"; nghịch lý kẻ-biết-lá-số | V.1–2 | `metaphor` (KHKMT) + `mô-hình-mới` (lập luận bất khả tính) | ✅ đã gắn cờ |

## Việc còn lại để hoàn tất Phụ lục B (sau khi đủ 8 ảnh + truy corpus)
1. Lấy **bảng đầy đủ 14 sao** của Đằng Sơn (ảnh mới thấy ~9 sao) → điền vector `vₛ` cho cả 14.
2. Đối chiếu từng nghĩa sao với **Toàn Thư / Trung Châu** trong `wiki.sqlite3` (dùng `cross_school._fetch_atom_details`) → xác nhận `cổ-văn` vs `đằng-sơn`.
3. Truy gốc **"Càn Khôn đồ"** + **"Hồ sư ngũ kỳ trận pháp"** (ảnh 7/9) — cổ văn nào? hay Đằng Sơn dựng?
4. Mọi atom nhập wiki phái `tu_vi_dang_son` mang tag cột "Tag" ở trên + cờ `metaphor_not_proof` khi chạm khoa học hiện đại.
