"""Nữ Mệnh (女命) — Trích Thiên Tủy Chương 6 (Phần II Lục Thân).

Paradigm Nhậm Thiết Tiều dành riêng cho mệnh NỮ:
- **Phu** (chồng) = Quan tinh (đối với nữ, Quan/Sát là chồng)
- **Con** = Thực Thương tinh (nữ sinh Thực Thương)
- **Tài** = ăn-mặc, tài vận
- **Ấn** = mẹ chồng + học vấn

Khác mệnh nam (Quan = sự nghiệp, Tài = vợ, Thực Thương = con + sáng tạo).

4 chủ đề chính Trích Thiên Tủy Ch.6:
1. **Khắc Phu** — chồng = Quan, Quan thụ thương → khắc chồng
2. **Có con** — Thực Thương sinh ra:
   - Nhật vượng + Ấn trọng + Thực Thương khinh → ít con
   - Nhật vượng + có Tài + Ấn → nhiều con
   - Nhật nhược + Ấn (không Thực Thương) → nhiều con
   - Nhật nhược + Thực Thương vượng + không Ấn → không con
3. **Dâm Tà** — Thực Thương vượng + Tỉ Kiếp + Tài → phong lưu
4. **Tính cách Nữ** — Quan ổn định + Ấn = đoan chính; xung khắc nhiều = ngổn ngang

⚠️ Iron Rule #4+6:
- KHÔNG predict "anh sẽ ly dị". Chỉ output tín hiệu cấu trúc.
- "Dâm Tà" là paradigm cận đại — engine output WARN paradigm note rằng:
  + ngày xưa = stigma; ngày nay = tính cách thoáng, không phải xấu
- Nữ mệnh hiện đại KHÔNG bằng nữ mệnh cổ — môi trường xã hội thay đổi
"""

from __future__ import annotations


def analyze_nu_menh(state: dict, gender: str = "nu") -> dict | None:
    """Phân tích nữ mệnh theo paradigm Trích Thiên Tủy Ch.6.

    Args:
        state: bat_tu state
        gender: "nu" / "nam" — chỉ analyze nếu "nu"

    Returns: dict với khả năng khắc phu / có con / tính cách
    """
    if gender.lower() not in ("nu", "female", "f"):
        return None

    distrib = state.get("thap_than_distribution", {})
    visible = distrib.get("visible", {}) if isinstance(distrib.get("visible"), dict) else {}
    hidden = distrib.get("hidden", {}) if isinstance(distrib.get("hidden"), dict) else {}

    def cnt(tt: str) -> float:
        return float(visible.get(tt, 0) or 0) + 0.5 * float(hidden.get(tt, 0) or 0)

    chinh_quan = cnt("Chính Quan")
    that_sat = cnt("Thất Sát")
    quan_sat = chinh_quan + that_sat
    thuc = cnt("Thực Thần")
    thuong = cnt("Thương Quan")
    thuc_thuong = thuc + thuong
    tai = cnt("Chính Tài") + cnt("Thiên Tài")
    an = cnt("Chính Ấn") + cnt("Thiên Ấn") + cnt("Kiêu Thần")
    tikiep = cnt("Tỉ Kiên") + cnt("Tỉ Kiếp") + cnt("Kiếp Tài")

    strength = state.get("ngu_hanh", {}).get("day_master_assessment", {}).get("strength_tag", "")
    day_strong = strength in ("strong", "very_strong")
    day_weak = strength in ("weak", "very_weak")

    patterns = []

    # 1. Khắc Phu
    if quan_sat < 0.5:
        patterns.append({
            "category": "khac_phu",
            "type": "quan_sat_vo_can",
            "severity": "high",
            "narrative": (
                "**Quan Sát vô căn** (cả Chính Quan + Thất Sát ≤0.5 trong Tứ Trụ). "
                "Trong paradigm Trích Thiên Tủy, Quan = phu — Quan không có = không có "
                "tín hiệu hôn nhân rõ trong cấu trúc. KHÔNG predict 'không lấy chồng' — "
                "chỉ là tín hiệu phải đầu tư communication và lựa chọn đối tác kỹ."
            ),
        })
    elif quan_sat >= 1 and thuc_thuong >= 2 and an < 0.5:
        patterns.append({
            "category": "khac_phu",
            "type": "thuong_quan_khac_quan",
            "severity": "high",
            "narrative": (
                f"**Thương Quan/Thực Thần ({thuc_thuong:.1f}) >> Quan Sát ({quan_sat:.1f})** + KHÔNG Ấn. "
                "Paradigm Trích Thiên Tủy: Thương Quan trực tiếp khắc Quan (= phu). "
                "Tín hiệu hôn nhân biến động. **Hóa giải**: dùng Ấn (học vấn, từ thiện) "
                "để 'Thương Quan phối Ấn' — biến trí tuệ thành hữu dụng."
            ),
        })
    elif quan_sat >= 2 and day_weak and an < 1:
        patterns.append({
            "category": "khac_phu",
            "type": "quan_qua_vuong_than_nhuoc",
            "severity": "medium",
            "narrative": (
                f"**Quan Sát quá vượng ({quan_sat:.1f}) + thân nhược + thiếu Ấn**. "
                "Khí phu áp đảo khí bản thân — nguy cơ bị chồng át hoặc kết hôn với "
                "đối tác overbearing. Hóa giải: bù Ấn (học vấn) + Tỉ Kiếp (bạn bè đồng vai)."
            ),
        })

    # 2. Có con
    children_pattern = None
    if day_strong and an >= 2 and thuc_thuong < 1:
        children_pattern = {
            "type": "an_trong_thuc_thuong_khinh",
            "count_tag": "it_con",
            "narrative": (
                "Nhật chủ vượng + Ấn trọng + Thực Thương khinh → "
                "**ÍT CON** (paradigm Trích Thiên Tủy). Ấn khắc Thực Thương."
            ),
        }
    elif day_strong and tai >= 1.5 and an >= 1 and thuc_thuong >= 0.5:
        children_pattern = {
            "type": "tai_giai_an_khac",
            "count_tag": "nhieu_con",
            "narrative": (
                "Nhật chủ vượng + có Tài + có Ấn + Thực Thương → "
                "**CON CÁI ĐẦY ĐỦ** (Tài chế Ấn, Ấn không khắc Thực Thương)."
            ),
        }
    elif day_weak and an >= 1 and thuc_thuong < 1:
        children_pattern = {
            "type": "nhuoc_co_an_khong_thuc",
            "count_tag": "co_con",
            "narrative": "Nhật chủ nhược + có Ấn (không Thực Thương) → CON CÁI ĐẦY ĐỦ.",
        }
    elif day_weak and thuc_thuong >= 2 and an < 0.5:
        children_pattern = {
            "type": "nhuoc_thuc_thuong_vuong_khong_an",
            "count_tag": "kho_con",
            "narrative": (
                "Nhật chủ nhược + Thực Thương vượng + không Ấn → "
                "**KHÓ CÓ CON** (cấu trúc khô — paradigm Trích Thiên Tủy). "
                "Cần điều chỉnh môi trường + bổ Ấn."
            ),
        }

    if children_pattern:
        patterns.append({
            "category": "co_con",
            **children_pattern,
        })

    # 3. Dâm Tà (paradigm cận đại — em ADD WARNING)
    if thuc_thuong >= 2 and tikiep >= 1.5 and tai >= 1.5:
        patterns.append({
            "category": "phong_luu",
            "type": "thuc_thuong_ti_kiep_tai",
            "severity": "neutral",
            "narrative": (
                "**Cấu trúc Thực Thương vượng + Tỉ Kiếp + Tài**. "
                "Paradigm Trích Thiên Tủy CỔ gọi là 'dâm tà' — NHƯNG đây là góc nhìn "
                "phong kiến. Theo paradigm hiện đại: cấu trúc này = tính cách THOÁNG, "
                "giao tiếp rộng, độc lập tài chính, sáng tạo. KHÔNG phải xấu. "
                "Chỉ là tính cách MẠNH MẼ, lựa chọn đối tác kỹ + communication tốt là đủ."
            ),
            "paradigm_warning": (
                "⚠️ Trích Thiên Tủy Ch.6 thuộc thời cận đại, có thiên kiến giới. "
                "Engine output giữ nguyên nguồn nhưng anh/chị đọc với góc nhìn hiện đại."
            ),
        })

    # 4. Tính cách
    if quan_sat >= 1 and an >= 1 and abs(quan_sat - an) < 1:
        patterns.append({
            "category": "tinh_cach",
            "type": "quan_an_can_bang",
            "severity": "positive",
            "narrative": (
                "**Quan + Ấn cân bằng** — paradigm cổ điển = 'nữ mệnh đoan chính, "
                "có học vấn, sự nghiệp + gia đình hài hòa'."
            ),
        })

    return {
        "patterns": patterns,
        "counts": {
            "quan_sat": round(quan_sat, 1),
            "thuc_thuong": round(thuc_thuong, 1),
            "tai": round(tai, 1),
            "an": round(an, 1),
            "ti_kiep": round(tikiep, 1),
        },
        "source": "Trích Thiên Tủy bình chú — Nhậm Thiết Tiều, Chương 6 Nữ Mệnh",
        "paradigm_guard": (
            "⚠️ Iron Rule #4+6: Đây là TÍN HIỆU CẤU TRÚC, KHÔNG predict tĩnh. "
            "Nữ mệnh hiện đại khác cổ điển — môi trường xã hội + lựa chọn cá nhân quyết định nhiều hơn cấu trúc."
        ),
    }
