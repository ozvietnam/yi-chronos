"""元会运世法 — phép Thiết Bản nối lý thuyết NGUYÊN-HỘI-VẬN-THẾ của Thiệu Ung
(图解 tr.99-100). TẤT ĐỊNH theo giờ sinh, KHÔNG thiếu bảng (khác 八卦滚).

Quy trình (图解 "14.元会运世法(一)"):
  1-2. Tứ trụ + 太玄数.
  3. 元数=年干+年支 (太玄); 会数=月干+月支; 运数=日干+日支; 世数=时干+时支.
  4. 元会基本数 = 元数(2 chữ đầu) ‖ 会数(2 chữ sau).  运世基本数 = ĐẢO(运数) ‖ ĐẢO(世数).
  5. 基本数一 = 元会基本数 + 年干太玄 ×1000 (千位 +年干). [考刻 ±30 theo đời → chốt, cần lục thân]
  6. 4 条文 từ 基本数一: +月干×100, +日干×10, +时干×1, +日干×1.
  7. 基本数二 = 运世基本数 + 年干太玄 ×1000; nếu >13000 thì −12000.
  8. 4 条文 từ 基本数二 (cùng quy tắc).  9. Tra 条文.

VALIDATE cặp kiểm sách (男 乙亥 丁亥 壬子 辛亥): 元数12 会数10 运数15 世数11 →
  元会基本数1210, 运世基本数5111 → 基本数一9210, 基本数二1111 →
  [9810,9270,9217,9216] + [1711,1171,1118,1117].

Nối Hoàng Cực: 元-会-运-世 = khung vũ trụ Thiệu Ung (engine/hoang_cuc). Đọc cái ĐÃ ĐỊNH,
KHÔNG bói; 基本数 chốt cuối qua 考刻 (đối chiếu đời) — base ở đây là 初 (chưa ±30).
"""
from __future__ import annotations

from engine.thiet_ban.lap_so import tra_dieu_van


def _dao(n: int) -> int:
    """ĐẢO 十位↔个位 của số 2 chữ. 15→51, 11→11, 10→1."""
    return (n % 10) * 10 + (n // 10)


def _gioi_han(so: int) -> int:
    """条文 >13000 thì −12000 (图解 tr.88)."""
    return so - 12000 if so > 13000 else so


def _bon_dieu_van(bd: int, nguyet_can: int, nhat_can: int, thoi_can: int) -> list[int]:
    """4 条文 từ 1 基本数: +月干(百位), +日干(十位), +时干(个位), +日干(个位)."""
    return [_gioi_han(bd + nguyet_can * 100),
            _gioi_han(bd + nhat_can * 10),
            _gioi_han(bd + thoi_can),
            _gioi_han(bd + nhat_can)]


def tinh_so(yc, yz, mc, mz, dc, dz, hc, hz) -> dict:
    """Lõi số học 元会运世 từ 8 太玄数 (thuần, để test cặp kiểm). Trả các 基本数 + 8 SỐ 条文."""
    nguyen, hoi, van, the = yc + yz, mc + mz, dc + dz, hc + hz
    nh_co_ban = nguyen * 100 + hoi                     # 元会基本数
    vt_co_ban = _dao(van) * 100 + _dao(the)            # 运世基本数
    co_ban_1 = nh_co_ban + yc * 1000                   # 基本数一 (千位 +年干)
    co_ban_2 = _gioi_han(vt_co_ban + yc * 1000)        # 基本数二
    return {"nguyen": nguyen, "hoi": hoi, "van": van, "the": the,
            "nguyen_hoi_co_ban": nh_co_ban, "van_the_co_ban": vt_co_ban,
            "co_ban_mot": co_ban_1, "co_ban_hai": co_ban_2,
            "so_nguyen_hoi": _bon_dieu_van(co_ban_1, mc, dc, hc),
            "so_van_the": _bon_dieu_van(co_ban_2, mc, dc, hc)}


def nguyen_hoi_van_the(birth_dt: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """元会运世法 từ giờ sinh → 元会运世数 + 2 基本数 + 8 条文 (4+4)."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.thiet_ban.khoi_so import TAI_HUYEN_CAN, TAI_HUYEN_CHI
    p = extract_tu_tru(birth_dt, timezone)["pillars"]

    def thx(pk):
        return TAI_HUYEN_CAN[p[pk]["stem"]], TAI_HUYEN_CHI[p[pk]["branch"]]

    (yc, yz), (mc, mz), (dc, dz), (hc, hz) = (thx("year"), thx("month"),
                                             thx("day"), thx("hour"))
    s = tinh_so(yc, yz, mc, mz, dc, dz, hc, hz)
    nh_co_ban, vt_co_ban = s["nguyen_hoi_co_ban"], s["van_the_co_ban"]
    co_ban_1, co_ban_2 = s["co_ban_mot"], s["co_ban_hai"]
    nguyen, hoi, van, the = s["nguyen"], s["hoi"], s["van"], s["the"]

    def pack(sos):
        out = []
        for s in sos:
            v = tra_dieu_van(s, prefer_tujie=True) or {}
            out.append({"so": s, "dieu_van": v.get("zh"), "vi": v.get("vi"),
                        "nguon": v.get("nguon")})
        return out

    return {
        "bat_tu": f"{p['year']['stem']}{p['year']['branch']} {p['month']['stem']}"
                  f"{p['month']['branch']} {p['day']['stem']}{p['day']['branch']} "
                  f"{p['hour']['stem']}{p['hour']['branch']}",
        "nguyen_so": nguyen, "hoi_so": hoi, "van_so": van, "the_so": the,
        "nguyen_hoi_co_ban": nh_co_ban, "van_the_co_ban": vt_co_ban,
        "co_ban_mot": co_ban_1, "co_ban_hai": co_ban_2,
        "dieu_van_nguyen_hoi": pack(s["so_nguyen_hoi"]),
        "dieu_van_van_the": pack(s["so_van_the"]),
        "_phap": "元会运世法(一) — TẤT ĐỊNH giờ sinh. 基本数 là SƠ; chốt cuối qua 考刻 "
                 "(±30 đối chiếu đời/lục thân). Nối khung Nguyên-Hội-Vận-Thế (Hoàng Cực).",
    }
