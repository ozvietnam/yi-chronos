"""CẦU NỐI sức khỏe — ghép HAI MẮT: Tử Vi (CÁI GÌ) × Bát Tự/Đông y (KHI NÀO).

Anh chốt 2026-07-23: _"Phải có hai mắt thì mới ra đúng. Một cái cho biết THỜI ĐIỂM, một
cái cho biết chính xác CÁI GÌ, bệnh gì sẽ bùng phát."_

Cầu nối KHÔNG tự tính lại — nó GỌI hai hệ đã có rồi GHÉP (Iron #1 + #3, giữ hai phái
độc lập, đối chiếu chéo):
  • Mắt TỬ VI (WHAT) — cung Tật Ách + sao (đích danh tạng + bệnh) + Thiên Thương/Thiên Sứ.
      → engine/tu_vi/van_han.py (_the_dung_block, tang_ngu_hanh, thuong_su_canh_bao)
  • Mắt BÁT TỰ (WHEN + thể trạng) — thể trạng ngũ hành + lịch tháng áp lực + Ngũ Vận Lục Khí.
      → engine/bat_tu/suc_khoe.py, engine/dong_y/{health_monthly_view, ngu_van_luc_khi}.py

GIAO ĐIỂM = "tạng [Tử Vi] (bệnh cụ thể) cần giữ vào [tháng/năm áp lực của Bát Tự]"; độ tin
CAO khi hai mắt CÙNG chỉ một tạng. Iron #9: đọc để DƯỠNG–PHÒNG, KHÔNG đoán ngày dữ/tử vong.
"""
from __future__ import annotations

from typing import Optional


def _norm_hanh(e: str) -> str:
    """Chuẩn hóa tên hành: bat_tu dùng 'thủy'/'thổ' (thường), tu_vi dùng 'Thủy'/'Thổ'."""
    return (e or "").strip().capitalize()


# ── MẮT 1 — TỬ VI: CÁI GÌ (tạng + bệnh đích danh) ────────────────────────────
def mat_tu_vi(birth_datetime_local: str, gender: str = "nam") -> dict:
    from engine.tu_vi import van_han as vh
    from engine.tu_vi.from_birth import cast_la_so_from_birth
    la_so = cast_la_so_from_birth(birth_datetime_local=birth_datetime_local, gender=gender)
    tat = next((p for p in la_so.get("palaces", []) if p["name"] == "Tật Ách"), None)
    if tat is None:
        return {"available": False}
    blk = vh._the_dung_block(la_so, tat["branch_index"], "Nguyên cục")
    tnh = blk.get("tang_ngu_hanh") or {}
    return {
        "available": True,
        "cung": {"vi_tri": blk["vi_tri"], "sao": blk["sao"]},
        "hanh_tang": _norm_hanh(tnh.get("hanh", "")),
        "tang": tnh.get("tang", ""),
        "benh_co_nguon": [{"noi_dung": g["dich"], "nguon": g["nguon"]}
                          for g in blk.get("sao_nguon", [])[:3]],
        "thoi_diem_sao": blk.get("thuong_su_canh_bao"),   # Thiên Thương/Sứ hội sát (nếu động)
    }


# ── MẮT 2 — BÁT TỰ / ĐÔNG Y: KHI NÀO (+ thể trạng đối chiếu) ─────────────────
def mat_bat_tu(birth_datetime_local: str, gender: str = "nam", *,
               timezone: str = "Asia/Ho_Chi_Minh", year: int = 2026) -> dict:
    out: dict = {"available": False, "year": year}
    try:
        from engine.bat_tu import analyze_suc_khoe, cast_bat_tu, extract_tu_tru
        from engine.bat_tu.constants import STEM_ELEMENT as SE
        from engine.bat_tu.luu_nien import compute_luu_nien_pillar_by_year
        from engine.dong_y.health_monthly_view import build_monthly_health_view
        from engine.dong_y.ngu_van_luc_khi import compute_ngu_van_luc_khi
    except Exception as e:                       # engine thiếu → mắt này 'nhắm', vẫn trả mắt kia
        out["error"] = repr(e)
        return out
    try:
        st = cast_bat_tu(birth_datetime_local=birth_datetime_local, timezone=timezone, gender=gender)
        sk = analyze_suc_khoe(st)
        con = sk.get("constitution", {})
        out["the_trang"] = {"the_element": _norm_hanh(con.get("element", "")),
                            "tang_chu": con.get("primary_tang", ""),
                            "manh_yeu": con.get("tag", ""),
                            "narrative": con.get("narrative", "")}
        out["tang_thua_thieu"] = sk.get("tang_phu_warnings", [])

        tt = extract_tu_tru(birth_datetime_local, timezone)
        dm = tt.get("day_master")
        dm_stem = dm.get("stem") if isinstance(dm, dict) else dm
        # KHI NÀO — lịch tháng (đã fuse Tử Vi+Bát Tự bên Đông y)
        mv = build_monthly_health_view(tt, year)
        summ = mv.get("summary", {})
        out["thang_can_giu"] = summ.get("thang_can_trong", [])
        out["thang_duong"] = summ.get("thang_tot_nhat", [])
        out["thang_chi_tiet"] = [{"thang": m.get("month_index"), "tiet_khi": m.get("tiet_khi"),
                                  "level": m.get("level"), "y_nghia": m.get("level_meaning"),
                                  "tang": m.get("tang_dac_biet")} for m in mv.get("months", [])]
        # KHI NÀO — khí năm (Ngũ Vận Lục Khí)
        yp = compute_luu_nien_pillar_by_year(year)
        r = compute_ngu_van_luc_khi(can_nam=yp["stem"], chi_nam=yp["branch"], year=year,
                                    day_master_element=SE.get(dm_stem, ""))
        rd = r.to_dict() if hasattr(r, "to_dict") else r
        out["khi_nam"] = {"trung_van": rd.get("trung_van_hanh"),
                          "luc_khi": rd.get("luc_khi_name"),
                          "canh_bao": rd.get("luc_dam_canh_bao")}
        out["available"] = True
    except Exception as e:
        out["error"] = repr(e)
    return out


# ── CẦU NỐI — ghép hai mắt ────────────────────────────────────────────────────
def cau_noi_suc_khoe(*, birth_datetime_local: str, gender: str = "nam",
                     timezone: str = "Asia/Ho_Chi_Minh", year: int = 2026) -> dict:
    tv = mat_tu_vi(birth_datetime_local, gender)
    bt = mat_bat_tu(birth_datetime_local, gender, timezone=timezone, year=year)

    # Đối chiếu chéo TẠNG: hai mắt có cùng chỉ một tạng không?
    tang_tv = tv.get("hanh_tang", "") if tv.get("available") else ""
    tang_bt = bt.get("the_trang", {}).get("the_element", "") if bt.get("available") else ""
    khop = bool(tang_tv) and tang_tv == tang_bt
    dong_thuan = {
        "khop_tang": khop,
        "tang_tu_vi": tang_tv, "tang_bat_tu": tang_bt,
        "do_tin": "cao (hai mắt đồng thuận)" if khop else
                  ("một mắt" if (tang_tv or tang_bt) else "chưa đủ dữ liệu"),
    }

    # GIAO ĐIỂM = CÁI GÌ (Tử Vi) đặt vào KHI NÀO (Bát Tự)
    cau_noi: list[str] = []
    if tv.get("available"):
        tang = tv.get("tang") or f"tạng hành {tang_tv}"
        benh = "; ".join(b["noi_dung"].rstrip(". ") for b in tv.get("benh_co_nguon", [])[:1]) \
               or "(chưa có mô tả bệnh có nguồn)"
        if bt.get("available") and bt.get("thang_can_giu"):
            khi = ", ".join(bt["thang_can_giu"][:3])
            cau_noi.append(f"CÁI GÌ (Tử Vi): giữ **{tang}** — biểu hiện dõi theo: {benh}.")
            cau_noi.append(f"KHI NÀO (Bát Tự): các kỳ áp lực trong {year} → {khi}.")
            cau_noi.append(f"→ CẦU NỐI: vào các kỳ trên, chú ý {tang.split(',')[0]}"
                           + (f" (hai mắt cùng chỉ tạng {tang_tv} — độ tin cao)." if khop
                              else "; đối chiếu thêm thể trạng Bát Tự."))
        else:
            cau_noi.append(f"CÁI GÌ (Tử Vi): giữ **{tang}** — {benh}. (Mắt Bát Tự chưa mở "
                           "được để ghép thời điểm.)")
    # bổ sung: bệnh Bát Tự (tạng thừa) như lớp đối chiếu
    for w in (bt.get("tang_thua_thieu") or [])[:2]:
        cau_noi.append(f"Đối chiếu Bát Tự: {w.get('tang','')} {w.get('polarity','')} — "
                       f"{w.get('symptoms','')}")

    return {
        "status": "ok",
        "hai_mat": {"tu_vi_CAI_GI": tv, "bat_tu_KHI_NAO": bt},
        "dong_thuan_tang": dong_thuan,
        "cau_noi": cau_noi,
        "disclaimer": ("Hai mắt để SOI cho DƯỠNG–PHÒNG (giữ gìn + khám đúng lúc), KHÔNG "
                       "đoán ngày dữ / tử vong / gọi tên tai họa, KHÔNG thay khám–thuốc. "
                       "Tử Vi (sao) và Bát Tự (khí) là hai phái độc lập, ở đây đối chiếu "
                       "chéo — khớp thì tin cao, lệch thì flag để xét thêm."),
    }
