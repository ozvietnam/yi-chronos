"""Quét bao quát toàn lá số → rút ĐIỂM NỔI BẬT NHẤT (Anh chốt 2026-06-13).

Đầu bếp giỏi nhìn cả mâm nguyên liệu trước khi nấu — không để LLM tự mò trong
đống atoms. Engine chấm điểm độ nổi bật của: dị cách Mệnh · cách cục có tên ·
bộ phụ tinh 12 cung · Tứ Hóa đặc biệt · cung rực/nặng nhất. Trả top-N để khai
vị kể ƯU TIÊN.

Đọc từ three_layer (đã tính) + la_so_input — KHÔNG query DB, nhẹ.
"""
from __future__ import annotations

CHI_RING = ["ty", "suu", "dan", "mao", "thin", "ti", "ngo", "mui", "than", "dau", "tuat", "hoi"]

SAT_TINH = {"kinh_duong", "da_la", "hoa_tinh", "linh_tinh", "dia_khong", "dia_kiep",
            "thien_hinh", "hoa_ky"}
CAT_TINH = {"hoa_loc", "hoa_quyen", "hoa_khoa", "loc_ton", "thien_ma", "ta_phu",
            "huu_bat", "van_xuong", "van_khuc", "thien_khoi", "thien_viet",
            "long_tri", "phuong_cac", "an_quang", "thien_quy", "tam_thai", "bat_toa"}

_FN_VI = {"menh": "Mệnh", "phu_the": "Phu Thê", "tai_bach": "Tài Bạch",
          "quan_loc": "Quan Lộc", "thien_di": "Thiên Di", "phuc_duc": "Phúc Đức",
          "tat_ach": "Tật Ách", "dien_trach": "Điền Trạch", "no_boc": "Nô Bộc",
          "huynh_de": "Huynh Đệ", "tu_tuc": "Tử Tức", "phu_mau": "Phụ Mẫu"}


def quet_diem_noi_bat(la_so_input: dict, three_layer: dict, top_n: int = 5) -> list[dict]:
    """Quét toàn lá → list điểm nổi bật {loai, mo_ta, diem, vi_tri}, sort điểm giảm."""
    from engine.tu_vi.viet_names import vi_star, vi_chi

    hl: list[dict] = []
    lop3 = three_layer.get("lop_3_sach_co", {})
    menh_chi = la_so_input.get("menh_palace")
    than_chi = la_so_input.get("than_palace")
    ct = {k: v for k, v in (la_so_input.get("chinh_tinh_per_palace") or {}).items() if k in CHI_RING}
    fn_to_chi = la_so_input.get("fn_to_chi") or {}
    chi_to_fn = {c: f for f, c in fn_to_chi.items()}

    # ── 1. DỊ CÁCH MỆNH (hiếm + đặc biệt, điểm cao) ──
    if menh_chi and not (ct.get(menh_chi)):
        hl.append({"loai": "di_cach", "diem": 95, "vi_tri": "Mệnh",
                   "mo_ta": "Mệnh VÔ CHÍNH DIỆU (không có chính tinh thủ Mệnh) — phải mượn sao đối cung, "
                            "tính cách uyển chuyển, đa diện, dễ thích nghi nhưng cần điểm tựa rõ ràng."})
    if menh_chi and menh_chi == than_chi:
        hl.append({"loai": "menh_than", "diem": 80, "vi_tri": "Mệnh",
                   "mo_ta": "Mệnh và Thân ĐỒNG CUNG — con người nhất quán, bản chất và hành động hợp nhất, "
                            "ít giằng xé trong-ngoài."})
    tuan = set(la_so_input.get("tuan_chi") or [])
    triet = set(la_so_input.get("triet_chi") or [])
    if menh_chi in tuan or menh_chi in triet:
        nh = "Tuần" if menh_chi in tuan else "Triệt"
        hl.append({"loai": "di_cach", "diem": 88, "vi_tri": "Mệnh",
                   "mo_ta": f"{nh} án ngữ cung Mệnh — như tấm màn che, đời thường có khúc 'khởi đầu muộn' "
                            "hoặc phải qua trắc trở mới định, nhưng hóa giải được nhiều cái xấu đồng cung."})
    menh_stars = set(ct.get(menh_chi) or []) | set((la_so_input.get("phu_tinh_per_palace") or {}).get(menh_chi, []))
    if {"dia_khong", "dia_kiep"} & menh_stars:
        hl.append({"loai": "di_cach", "diem": 82, "vi_tri": "Mệnh",
                   "mo_ta": "Không/Kiếp thủ Mệnh — tư duy khác người, dễ nghĩ điều người khác không nghĩ tới; "
                            "hợp tâm linh/sáng tạo, cần tránh hư vô bi quan."})

    # ── 2. CÁCH CỤC CÓ TÊN (đã match rule) ──
    for cc in (lop3.get("cach_cuc_named") or []):
        base = 78 if cc.get("loai") == "cat" else 74 if cc.get("loai") == "hung" else 70
        base += min((cc.get("total_atoms") or 0) // 10, 8)  # cách phổ biến trong sách → nhỉnh
        hl.append({"loai": "cach_cuc", "diem": base, "vi_tri": "toàn lá",
                   "mo_ta": f"Cách '{cc['ten']}' ({_loai_vi(cc.get('loai'))}): {cc.get('dieu_kien','')}"})

    # ── 3. TỨ HÓA đặc biệt ──
    for t in (la_so_input.get("tu_hoa") or []):
        hoa = t.get("hoa"); fn = t.get("palace_fn")
        if hoa == "hoa_ky" and fn in ("menh", "phu_the", "tai_bach", "tat_ach"):
            hl.append({"loai": "tu_hoa", "diem": 76, "vi_tri": _FN_VI.get(fn, fn),
                       "mo_ta": f"Hóa Kỵ ({vi_star(t.get('star',''))}) đóng cung {_FN_VI.get(fn,fn)} — "
                                "điểm cần giữ gìn, nơi dễ vướng mắc/trăn trở nhất trong đời."})
        elif hoa in ("hoa_loc", "hoa_quyen", "hoa_khoa") and fn == "menh":
            hl.append({"loai": "tu_hoa", "diem": 72, "vi_tri": "Mệnh",
                       "mo_ta": f"{_hoa_vi(hoa)} ({vi_star(t.get('star',''))}) ngay tại Mệnh — "
                                "một thiên phú trời cho, nét sáng bẩm sinh."})

    # ── 4. BỘ PHỤ TINH nổi bật toàn 12 cung (đủ cặp + sát/hung, hoặc cát mạnh ngoài Mệnh) ──
    for chi, bos in (lop3.get("bo_phu_tinh_per_palace") or {}).items():
        cung_vi = _FN_VI.get(chi_to_fn.get(chi), vi_chi(chi))
        for b in (bos or []):
            if not b.get("du_cap"):
                continue
            if b.get("loai") in ("sat", "hung") and b.get("the") in ("dong_cung", "giap", "xung_chieu"):
                d = 70 if chi == menh_chi else 58
                hl.append({"loai": "bo_phu_tinh", "diem": d, "vi_tri": cung_vi,
                           "mo_ta": f"Bộ {b['ten']} {b['the_vi']} tại {cung_vi} — điểm cần lưu tâm."})

    # ── 5. CUNG RỰC / NẶNG nhất trong 12 cung ──
    sang, toi = _cung_sang_toi(la_so_input)
    if sang:
        hl.append({"loai": "cung_ruc", "diem": 56, "vi_tri": sang[1],
                   "mo_ta": f"Cung {sang[1]} tụ nhiều sao tốt nhất lá số — mảng đời được trời ưu ái, nên dồn sức."})
    if toi:
        hl.append({"loai": "cung_nang", "diem": 54, "vi_tri": toi[1],
                   "mo_ta": f"Cung {toi[1]} nặng sát tinh nhất — mảng đời cần cẩn trọng, gia cố."})

    hl.sort(key=lambda x: -x["diem"])
    # Khử trùng vị-trí+loại để khỏi lặp
    seen, out = set(), []
    for h in hl:
        k = (h["loai"], h["vi_tri"])
        if k in seen:
            continue
        seen.add(k); out.append(h)
    return out[:top_n]


def _cung_sang_toi(la_so_input: dict):
    fn_to_chi = la_so_input.get("fn_to_chi") or {}
    chi_to_fn = {c: f for f, c in fn_to_chi.items()}
    from engine.tu_vi.viet_names import vi_chi
    allp: dict[str, list[str]] = {}
    for src in ("chinh_tinh_per_palace", "phu_tinh_per_palace", "vong_sao_per_palace"):
        for chi, stars in (la_so_input.get(src) or {}).items():
            if chi in CHI_RING:
                allp.setdefault(chi, []).extend(stars)
    best_c = best_s = None
    for chi, stars in allp.items():
        nc = sum(1 for s in stars if s in CAT_TINH)
        ns = sum(1 for s in stars if s in SAT_TINH)
        vi = _FN_VI.get(chi_to_fn.get(chi), vi_chi(chi))
        if best_c is None or nc > best_c[0]:
            best_c = (nc, vi)
        if best_s is None or ns > best_s[0]:
            best_s = (ns, vi)
    sang = best_c if best_c and best_c[0] >= 2 else None
    toi = best_s if best_s and best_s[0] >= 2 else None
    return sang, toi


def _loai_vi(l):
    return {"cat": "cát", "hung": "hung", "hung_hoa_cat": "tùy hóa", "dao_hoa": "đào hoa"}.get(l, l or "")


def _hoa_vi(h):
    return {"hoa_loc": "Hóa Lộc", "hoa_quyen": "Hóa Quyền", "hoa_khoa": "Hóa Khoa"}.get(h, h)
