"""Phác hoạ CHÂN DUNG BIỂU TƯỢNG người phối ngẫu (đọc đồng dạng — Iron #4/#6/#8).

⚠️ PARADIGM TUYỆT ĐỐI: đây KHÔNG phải tiên đoán gương mặt người thật mà user sẽ cưới.
Đây là chân dung BIỂU TƯỢNG / ĐỒNG DẠNG — hình tượng hoá KHÍ CHẤT của cung Phu Thê,
tức KIỂU người mà cấu trúc tâm-thân của user VẬN HÀNH hợp. Mệnh là ĐỘNG TỪ: lá số cho
biết TÍNH (nguyên liệu trời ban), engine chỉ vẽ ra hình tượng của cái tính đó — KHÔNG
cát/hung, KHÔNG phán, KHÔNG cá nhân hoá thành 'người sẽ cưới'.

Lập hồ sơ (deterministic, grounded vào bảng #4 + 形性赋 qua tuong_mao_phoi_ngau.json):
  - chính tinh + trạng thái cung Phu Thê (la_so palaces[2])
  - ngũ hành 官杀 (Quan Sát = sao chồng/vợ) suy từ thap_than Bát Tự
  - chi NGÀY sinh → mức nổi bật ngoại hình
  - đào hoa (Tham Lang / Thiên Diêu / Hồng Loan) → nụ cười duyên
  - nghề đặc trưng (cung Quan Lộc + Phu Thê)

Vẽ ảnh: TÁI DÙNG engine.yi_publishing.image_redraw_gemini — graceful khi không có
key/lỗi (trả image_b64=None + note, KHÔNG sập).
"""
from __future__ import annotations

import base64
import logging
import time
from pathlib import Path
from typing import Optional

from engine.tinh_duyen import knowledge_loader as KL

logger = logging.getLogger(__name__)

_ANH_DIR = Path(__file__).resolve().parents[2] / "data" / "tinh_duyen_anh"

_DISCLAIMER = (
    "Đây là chân dung BIỂU TƯỢNG phản chiếu khí chất cung Phu Thê — một KIỂU người "
    "hợp với cấu trúc của bạn, KHÔNG phải gương mặt người bạn sẽ cưới. Không có yếu "
    "tố tiên đoán hay cát/hung."
)

_NGUON = "Bảng tướng mạo phối ngẫu (Tài liệu #4) + 形性赋 (Hình Tính Phú, Tử Vi Đẩu Số Toàn Thư)"

# Day Master element (ngũ hành chữ Nhật can) bị KHẮC bởi hành nào = hành của 官杀.
# Quan Sát (sao chồng/vợ) = ngũ hành KHẮC nhật chủ.
# Kim khắc Mộc, Mộc khắc Thổ, Thổ khắc Thủy, Thủy khắc Hỏa, Hỏa khắc Kim.
_KHAC_NGUOC = {  # day_master_element -> hành khắc nó (= hành 官杀)
    "mộc": "Kim",
    "thổ": "Mộc",
    "thủy": "Thổ",
    "hỏa": "Thủy",
    "kim": "Hỏa",
}

_HANH_VI = {"kim": "Kim", "mộc": "Mộc", "thủy": "Thủy", "hỏa": "Hỏa", "thổ": "Thổ"}

_TU_CHINH = {"Tý", "Ngọ", "Mão", "Dậu"}
_TU_SINH = {"Dần", "Thân", "Tị", "Tỵ", "Thân", "Hợi"}
_TU_MO = {"Thìn", "Tuất", "Sửu", "Mùi"}

# Đào hoa tinh — có mặt trong cung Phu Thê → thêm nụ cười duyên.
_DAO_HOA_STARS = {"Tham Lang", "Thiên Diêu", "Hồng Loan", "Đào Hoa", "Hàm Trì"}

# Nghề theo cung Quan Lộc (chính tinh) — fallback khi Phu Thê không có nghề rõ.
# Tái dùng nghe_dac_trung của chính tinh trong bảng #4 (chinh_tinh_phu_the).

_GIOI_NGUOC = {
    "nữ": "nam", "nu": "nam", "female": "nam", "f": "nam",
    "nam": "nữ", "male": "nữ", "m": "nữ",
}


# ── helpers grounded vào la_so / bat_tu ───────────────────────────────────────

def _chinh_tinh_o_cung(la_so: dict, palace_index: int = 2) -> list[str]:
    """Chính tinh toạ tại 1 cung (mặc định Phu Thê = palaces[2]).

    chinh_tinh = {tên_sao: branch_index}; palace có branch_index riêng → match.
    """
    if not la_so:
        return []
    palaces = la_so.get("palaces") or []
    if palace_index >= len(palaces):
        return []
    bidx = palaces[palace_index].get("branch_index")
    chinh = la_so.get("chinh_tinh") or {}
    return [star for star, b in chinh.items() if b == bidx]


def _co_dao_hoa_cung_phu_the(la_so: dict) -> bool:
    """Đào hoa tinh (Tham Lang ở chính tinh / Thiên Diêu / Hồng Loan ở phụ tinh) ở Phu Thê."""
    if not la_so:
        return False
    palaces = la_so.get("palaces") or []
    if len(palaces) <= 2:
        return False
    bidx = palaces[2].get("branch_index")
    for group_key in ("chinh_tinh", "sao_q2", "phu_tinh", "sat_tinh"):
        grp = la_so.get(group_key) or {}
        for star, b in grp.items():
            if b == bidx and any(d in star for d in _DAO_HOA_STARS):
                return True
    return False


def _hanh_quan_sat(bat_tu_state: dict) -> Optional[str]:
    """Ngũ hành 官杀 (sao chồng/vợ) = hành KHẮC nhật chủ. Trả 'Kim'/'Mộc'/... hoặc None."""
    if not bat_tu_state:
        return None
    try:
        dm = (bat_tu_state.get("ngu_hanh", {})
              .get("day_master_assessment", {})
              .get("day_master_element"))
    except Exception:
        dm = None
    if not dm:
        # fallback: stem_element của trụ ngày
        try:
            dm = bat_tu_state["tu_tru"]["pillars"]["day"]["stem_element"]
        except Exception:
            dm = None
    if not dm:
        return None
    return _KHAC_NGUOC.get(str(dm).strip().lower())


def _chi_ngay(bat_tu_state: dict) -> Optional[str]:
    """Địa chi NGÀY sinh ('Tý'/'Ngọ'/...) từ trụ ngày Bát Tự."""
    if not bat_tu_state:
        return None
    try:
        return bat_tu_state["tu_tru"]["pillars"]["day"]["branch"]
    except Exception:
        return None


def _muc_noi_bat(chi: Optional[str]) -> dict:
    """chi ngày → khối mức nổi bật ngoại hình (3 nhóm Tứ Chính / Tứ Sinh / Tứ Mộ)."""
    tm = KL.get("tuong_mao_phoi_ngau")["chi_ngay"]
    if not chi:
        return {}
    if chi in _TU_CHINH:
        return tm["tu_chinh_dao_hoa"]
    if chi in _TU_SINH:
        return tm["tu_sinh_thong_minh"]
    if chi in _TU_MO:
        return tm["tu_mo_don_hau"]
    return {}


# ── lập hồ sơ tướng mạo ───────────────────────────────────────────────────────

def lap_ho_so_tuong_mao(la_so: dict,
                        bat_tu_state: dict,
                        gender: str = "nữ",
                        vung_mien: Optional[str] = None,
                        dan_toc: Optional[str] = None,
                        do_tuoi: Optional[str] = None) -> dict:
    """Đọc lá số + bát tự → hồ sơ tướng mạo BIỂU TƯỢNG của KIỂU phối ngẫu.

    Args:
        la_so: output cast_la_so_from_birth (cần palaces, chinh_tinh).
        bat_tu_state: output cast_bat_tu (cần tu_tru, ngu_hanh).
        gender: giới tính của USER ('nữ'/'nam'/...). Phối ngẫu = giới NGƯỢC lại.
        vung_mien / dan_toc / do_tuoi: tuỳ chọn, ghi vào hồ sơ để build prompt.

    Returns: dict hồ sơ — gioi_tinh_phoi_ngau, khuon_mat, chieu_cao, dang_nguoi, da,
        mat, mui, toc, nghe, moi_truong, phong_cach, bieu_cam, _nguon, _disclaimer.
        LUÔN trả đủ field (fallback 'chưa rõ') để downstream build prompt an toàn.
    """
    tm = KL.get("tuong_mao_phoi_ngau")
    chinh_map = tm["chinh_tinh_phu_the"]
    nh_map = tm["ngu_hanh_quan_sat"]
    nhan_tuong = tm["nhan_tuong"]

    g = (gender or "nữ").strip().lower()
    gioi_phoi = _GIOI_NGUOC.get(g, "nam" if g in ("nữ", "nu") else "nữ")

    # 1) chính tinh cung Phu Thê → sao chủ tướng mạo.
    sao_phu_the = _chinh_tinh_o_cung(la_so, 2)
    # sao chủ = sao đầu tiên có trong bảng #4 (chính tinh, không phải vô chính diệu).
    sao_chu = None
    for s in sao_phu_the:
        if s in chinh_map:
            sao_chu = s
            break
    base = chinh_map.get(sao_chu) if sao_chu else None

    # 2) ngũ hành 官杀 → da + dáng tinh chỉnh.
    hanh = _hanh_quan_sat(bat_tu_state)
    nh = nh_map.get(hanh) if hanh else None

    # 3) chi ngày → mức nổi bật.
    chi = _chi_ngay(bat_tu_state)
    noi_bat = _muc_noi_bat(chi)

    # 4) đào hoa → nụ cười duyên.
    co_dao_hoa = _co_dao_hoa_cung_phu_the(la_so)

    # 5) nghề: ưu tiên Phu Thê; bổ sung Quan Lộc.
    nghe_parts = []
    if base and base.get("nghe_dac_trung"):
        nghe_parts.append(base["nghe_dac_trung"])
    sao_quan_loc = _chinh_tinh_o_cung(la_so, 8)
    for s in sao_quan_loc:
        info = chinh_map.get(s)
        if info and info.get("nghe_dac_trung"):
            nghe_parts.append(info["nghe_dac_trung"])
            break

    # tóc + dáng đi theo ngũ hành.
    toc = nhan_tuong["toc_theo_ngu_hanh"].get(hanh, "tóc gọn gàng tự nhiên") if hanh else "tóc gọn gàng tự nhiên"
    dang_di = ""
    if hanh:
        dang_di = nhan_tuong["dang_di"]["_theo_ngu_hanh"].get(hanh, "")

    # chiều cao theo giới phối ngẫu.
    chieu_cao = "chưa rõ"
    if base:
        chieu_cao = base.get("chieu_cao_nam" if gioi_phoi == "nam" else "chieu_cao_nu") \
            or base.get("chieu_cao_nam") or "chưa rõ"

    # khuôn mặt: chính tinh chủ + tinh chỉnh ngũ hành.
    khuon_mat = (base or {}).get("khuon_mat", "ngũ quan hài hoà, nét dễ nhìn")
    if nh and nh.get("mat_khuon"):
        khuon_mat = f"{khuon_mat}; {nh['mat_khuon']}"
    if noi_bat.get("goi_y_prompt"):
        khuon_mat = f"{khuon_mat}; {noi_bat['goi_y_prompt']}"

    da = (nh or {}).get("da", "da sáng tự nhiên")
    dang_nguoi = (base or {}).get("dang_nguoi", "vóc cân đối")
    if nh and nh.get("dang"):
        dang_nguoi = f"{dang_nguoi}; {nh['dang']}"
    if dang_di:
        dang_nguoi = f"{dang_nguoi}; {dang_di}"

    mat = (base or {}).get("mat", "ánh mắt hài hoà")
    mui = (base or {}).get("mui", "mũi cân đối")
    mieng = (base or {}).get("mieng", "miệng cân đối")
    if co_dao_hoa:
        mieng = f"{mieng}, nụ cười duyên"
    bieu_cam = (base or {}).get("bieu_cam", "thần thái ôn hoà")
    phong_cach = (base or {}).get("nghe_dac_trung", "phong cách lịch thiệp")

    nghe = "; ".join(dict.fromkeys(nghe_parts)) if nghe_parts else "nghề lịch thiệp ổn định"
    moi_truong = "studio chân dung, ánh sáng dịu" if not noi_bat else \
        f"studio chân dung, ánh sáng dịu — {noi_bat.get('ten', '')}".strip(" —")

    return {
        "gioi_tinh_phoi_ngau": gioi_phoi,
        "sao_chu_phu_the": sao_chu,
        "sao_cung_phu_the": sao_phu_the,
        "hanh_quan_sat": hanh,
        "chi_ngay": chi,
        "co_dao_hoa": co_dao_hoa,
        "khuon_mat": khuon_mat,
        "chieu_cao": chieu_cao,
        "dang_nguoi": dang_nguoi,
        "da": da,
        "mat": mat,
        "mui": mui,
        "mieng": mieng,
        "toc": toc,
        "nghe": nghe,
        "moi_truong": moi_truong,
        "phong_cach": phong_cach,
        "bieu_cam": bieu_cam,
        "vung_mien": vung_mien,
        "dan_toc": dan_toc,
        "do_tuoi": do_tuoi,
        "_nguon": _NGUON,
        "_disclaimer": _DISCLAIMER,
    }


# ── build prompt tiếng Anh (mô tả 1 KIỂU người, KHÔNG cá nhân hoá) ────────────

_GENDER_EN = {"nam": "man", "nữ": "woman", "nu": "woman"}

_VUNG_EN = {
    "bắc": "northern Vietnamese region",
    "bac": "northern Vietnamese region",
    "trung": "central Vietnamese region",
    "nam": "southern Vietnamese region",
}


def _en(s: Optional[str]) -> str:
    """Rút gọn cụm tiếng Việt -> mô tả ngắn dùng được trong prompt ảnh.

    Giữ nguyên (ảnh model hiểu mô tả tiếng Việt kém) nhưng vẫn bám nét — ta dịch
    các từ khoá tướng mạo phổ biến sang tiếng Anh để prompt thuần Anh hơn."""
    if not s:
        return ""
    repl = {
        "mặt vuông": "square face", "mặt tròn": "round face", "mặt dài": "long face",
        "mặt trái xoan": "oval face", "mặt nhỏ": "small face",
        "da trắng": "fair skin", "da ngăm": "tan skin", "da đỏ hồng": "rosy complexion",
        "da vàng": "warm golden skin", "da sáng": "bright clear skin",
        "da hơi ngăm": "lightly tanned skin",
        "tóc mượt thẳng": "sleek straight hair", "tóc dày khỏe": "thick healthy hair",
        "tóc mềm gợn sóng": "soft wavy hair", "tóc hơi xoăn": "slightly curly hair",
        "tóc dày chắc": "thick dark hair", "tóc gọn gàng": "neat hair",
        "mũi cao": "high nose", "mũi thẳng": "straight nose", "mũi đầy": "full nose",
        "mắt sáng": "bright eyes", "mắt to": "large eyes", "mắt sắc": "sharp eyes",
        "mắt hiền": "gentle eyes", "mắt sâu": "deep-set eyes",
        "nụ cười duyên": "charming smile", "cười tươi": "warm smile",
        "cao": "tall", "tầm thước": "average height", "thấp": "shorter",
        "gầy": "slim build", "đầy đặn": "fuller build", "vạm vỡ": "robust build",
        "rắn chắc": "firm build", "thanh mảnh": "slender build",
    }
    # match key DÀI nhất trước (vd 'da hơi ngăm' trước 'da ngăm') → nét chính xác hơn.
    for vi in sorted(repl, key=len, reverse=True):
        if vi in s:
            return repl[vi]
    return s


def build_prompt_anh(ho_so: dict,
                     vung_mien: Optional[str] = None,
                     dan_toc: Optional[str] = None,
                     do_tuoi: Optional[str] = None) -> str:
    """Ghép prompt text-to-image TIẾNG ANH mô tả 1 KIỂU người Việt (a TYPE, not a person).

    KHÔNG cá nhân hoá ('the person you will marry'). Mô tả một archetype trung tính,
    photorealistic studio portrait. Luôn an toàn-paradigm.
    """
    gioi = (ho_so.get("gioi_tinh_phoi_ngau") or "nữ").strip().lower()
    subject = _GENDER_EN.get(gioi, "person")

    vm = (vung_mien or ho_so.get("vung_mien") or "").strip().lower()
    region = _VUNG_EN.get(vm, "Vietnamese")

    age = (do_tuoi or ho_so.get("do_tuoi") or "").strip()
    if age:
        age_clause = age if "year" in age.lower() else f"around {age}-year-old"
    else:
        age_clause = "around 30-year-old"

    ethnic = (dan_toc or ho_so.get("dan_toc") or "").strip()
    ethnic_clause = f", {ethnic} ethnicity" if ethnic and ethnic.lower() not in ("kinh", "việt") else ""

    feats = []
    for key in ("khuon_mat", "da", "mui", "mat", "toc"):
        en = _en(ho_so.get(key))
        if en:
            feats.append(en)
    if ho_so.get("co_dao_hoa"):
        feats.append("charming smile")
    # dáng người
    dang = _en(ho_so.get("dang_nguoi"))
    if dang:
        feats.append(dang)

    feat_clause = ", ".join(dict.fromkeys([f for f in feats if f]))

    # nghề -> attire gợi ý
    nghe = (ho_so.get("nghe") or "").lower()
    if any(k in nghe for k in ("tài chính", "ngân hàng", "quản lý", "lãnh đạo", "luật", "hành chính")):
        attire = "business attire"
    elif any(k in nghe for k in ("nghệ thuật", "thiết kế", "giải trí")):
        attire = "creative smart-casual attire"
    elif any(k in nghe for k in ("y", "chăm sóc", "giáo")):
        attire = "neat professional attire"
    else:
        attire = "smart-casual attire"

    parts = [
        f"Portrait of a {age_clause} Vietnamese {subject}",
        region + ethnic_clause,
    ]
    if feat_clause:
        parts.append(feat_clause)
    parts.append(attire)
    parts.append("gentle expression")
    parts.append("studio lighting, soft background, photorealistic, head and shoulders, 50mm lens")
    # archetype framing (a TYPE, not a specific real person)
    prompt = (", ".join(p for p in parts if p)
              + ". This is a symbolic archetype illustrating a personality type, "
                "not a specific real individual.")
    return prompt


# ── vẽ ảnh (tái dùng Gemini, graceful fallback) ──────────────────────────────

def ve_anh_phoi_ngau(ho_so: dict,
                     vung_mien: Optional[str] = None,
                     dan_toc: Optional[str] = None,
                     do_tuoi: Optional[str] = None,
                     prompt: Optional[str] = None) -> dict:
    """Tạo ảnh chân dung BIỂU TƯỢNG từ hồ sơ. Tái dùng image_redraw_gemini.

    Lỗi / không có key → trả {image_b64: None, ho_so, prompt, note} (KHÔNG sập).
    Thành công → {image_path, image_b64, prompt, ho_so}.

    note phân biệt nguyên nhân để nút 'Thử tạo lại' có nghĩa:
      - "chưa cấu hình khoá ảnh" (thiếu key — bấm lại vô ích cho tới khi cài key)
      - "tạo ảnh lỗi tạm thời (...)"  (key có nhưng API lỗi/quota — bấm lại có thể được)
    """
    if prompt is None:
        prompt = build_prompt_anh(ho_so, vung_mien, dan_toc, do_tuoi)

    from engine.yi_publishing import image_redraw_gemini as G

    # 1) Phải có khoá ảnh — thiếu key thì báo riêng để 'Thử tạo lại' không vô nghĩa.
    try:
        G._get_api_key()
    except Exception as exc:  # noqa: BLE001
        logger.info("ve_anh_phoi_ngau: thiếu khoá ảnh — %s", exc)
        return {
            "image_b64": None,
            "image_path": None,
            "prompt": prompt,
            "ho_so": ho_so,
            "note": "chưa cấu hình khoá ảnh",
            "note_code": "no_key",
            "_disclaimer": _DISCLAIMER,
        }

    # 2) Có key → gọi text2img THẬT (generate_image_gemini). Lỗi API/quota = tạm thời.
    try:
        _ANH_DIR.mkdir(parents=True, exist_ok=True)
        out_path = _ANH_DIR / f"phoi_ngau_{int(time.time() * 1000)}.png"

        gen = getattr(G, "generate_image_gemini", None)
        if gen is None:
            raise RuntimeError("backend không có hàm text2img generate_image_gemini")
        res = gen(prompt, output_path=out_path)

        saved_path = res.get("output_path") if isinstance(res, dict) else str(out_path)
        b64 = None
        p = Path(saved_path)
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        return {
            "image_path": str(saved_path),
            "image_b64": b64,
            "prompt": prompt,
            "ho_so": ho_so,
            "_disclaimer": _DISCLAIMER,
        }
    except Exception as exc:  # noqa: BLE001 — graceful, không sập UX
        logger.warning("ve_anh_phoi_ngau: tạo ảnh lỗi (có key) — %s", exc)
        return {
            "image_b64": None,
            "image_path": None,
            "prompt": prompt,
            "ho_so": ho_so,
            "note": f"tạo ảnh lỗi tạm thời ({type(exc).__name__})",
            "note_code": "gen_error",
            "_disclaimer": _DISCLAIMER,
        }
