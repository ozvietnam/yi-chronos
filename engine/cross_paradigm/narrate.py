"""Sage narrate cho TÌNH DUYÊN nữ mệnh (chặng 3 của bookflow đọc đồng dạng).

Engine `read_tinh_duyen` trả DỮ LIỆU CẤU TRÚC (deterministic, paradigm-safe). Lớp NÀY
gọi LLM (sage 'tu_vi', model non-reasoning DeepSeek deepseek-chat — nhanh) để DIỄN ĐẠT
dữ liệu đó thành lời cho user, ĐÚNG khẩu vị giao tiếp + đúng chặng tuổi.

PARADIGM (Iron Rule #4/#6/#8): KHÔNG bói. Mệnh là động từ — "cấu trúc của em vận hành
tốt nhất khi…". TUYỆT ĐỐI không phán 'khắc chồng / số cô quả / sẽ ly hôn'.

An toàn: mọi lỗi LLM/registry → trả '' (UI fallback về bản cấu trúc, KHÔNG sập).
"""
from __future__ import annotations

import json as _json
from typing import Any


def _quy_trinh_highlights(td: dict) -> tuple[str, list[str]]:
    """Trích tổng-hợp kim-tự-tháp + vài bước NỔI BẬT (ưu tiên trực tiếp) để bơm
    vào prompt → lời thầy giàu hơn (bám đúng quy trình 22 bước đã ground)."""
    qt = td.get("quy_trinh_day_du") or {}
    tong_hop = (qt.get("tong_hop_kim_tu_thap") or "").strip()

    xep_hang = qt.get("xep_hang_yeu_to") or {}
    noi_bat: list[str] = []
    # Ưu tiên các yếu tố TRỰC TIẾP (đỉnh kim tự tháp), rồi GIÁN TIẾP — lấy tối đa 5.
    for bucket in ("truc_tiep", "gian_tiep"):
        for it in (xep_hang.get(bucket) or []):
            ten = (it.get("ten_buoc") or "").strip()
            tom = (it.get("luan_tom") or "").strip()
            if ten and tom:
                noi_bat.append(f"[{bucket}] {ten}: {tom}")
            if len(noi_bat) >= 5:
                break
        if len(noi_bat) >= 5:
            break
    return tong_hop, noi_bat


def _cham_cap_block(td: dict) -> str:
    """Dựng khối CHẨN ĐOÁN CẤP ĐỘ (chấm cấp + lộ trình) để bơm vào system-prompt.

    Lời thầy phải: GỌI TÊN độ khó như KHÁI NIỆM ('mức độ thử thách N/5') + chỉ lộ
    trình cụ thể — KHÔNG phán-vào-người ('em sẽ khắc chồng / số cô quả')."""
    cc = td.get("chan_doan_cap_do") or {}
    if not cc:
        return ""
    cap = cc.get("cap_do")
    ten = cc.get("ten_cap")
    muc = cc.get("muc_do_thu_thach")
    doi = cc.get("do_thay_doi_duoc")
    phan_loai = cc.get("phan_loai")
    tin_hieu = cc.get("tin_hieu_kich_hoat") or []
    lo_trinh = cc.get("lo_trinh") or []

    lines = [
        "## CHẨN ĐOÁN CẤP ĐỘ THỬ THÁCH (chấm cấp + chỉ lối — ngôn ngữ XÂY DỰNG)",
        f"- Mức độ thử thách: {muc} ({ten}); phân loại: {phan_loai}; "
        f"khả năng chuyển hoá bằng rèn/chọn: {doi}.",
        "- Diễn đạt độ khó như một KHÁI NIỆM phân tích ('mức độ thử thách "
        f"{muc}', 'cấu trúc Thương Quan', 'áp lực lên cung phối ngẫu') — TUYỆT ĐỐI "
        "KHÔNG phán-vào-người ('em sẽ khắc chồng / số cô quả / chắc chắn ly hôn').",
    ]
    if tin_hieu:
        lines.append("- Tín hiệu THẬT trên lá này (gọi tên cấu trúc, không kết án):")
        lines += [f"  · {t}" for t in tin_hieu[:5]]
    if lo_trinh:
        lines.append(f"- LỘ TRÌNH cụ thể cần CHỈ cho người đọc (theo cấp {cap}):")
        lines += [f"  · {b}" for b in lo_trinh[:5]]
    lines.append(
        "- BẮT BUỘC đính khung 'mệnh là động từ': cấp độ đo ĐỘ KHÓ của nguyên liệu "
        "trời ban (TÍNH), KHÔNG đo kết cục — kết cục do HÀNH VI + LỰA CHỌN quyết định. "
        "Cấp cao = cần 'chọn khôn' nhiều hơn, KHÔNG = 'chắc chắn khổ'."
    )
    return "\n".join(lines) + "\n\n"


def _build_system_prompt(person: dict, td: dict) -> str:
    """Dựng system-prompt narrate từ khẩu vị giao tiếp + chặng tuổi + paradigm."""
    personality = td.get("personality") or {}
    stage = td.get("stage") or {}

    # Gom khẩu vị giao tiếp từ Mệnh chính tinh (mỗi sao có 1 block khẩu vị).
    giong, do_dai, cach_khung = [], [], []
    nen, tranh = [], []
    for p in personality.get("profiles", []) or []:
        kv = p.get("khau_vi_giao_tiep") or {}
        if kv.get("giong"):
            giong.append(str(kv["giong"]))
        if kv.get("do_dai"):
            do_dai.append(str(kv["do_dai"]))
        if kv.get("cach_khung"):
            cach_khung.append(str(kv["cach_khung"]))
        nen.extend(kv.get("nen", []) or [])
        tranh.extend(kv.get("tranh", []) or [])
    # Khử trùng giữ thứ tự.
    nen = list(dict.fromkeys(nen))
    tranh = list(dict.fromkeys(tranh))

    tuoi = stage.get("tuoi")
    giong_stage = stage.get("giong_van")
    moi_truong = stage.get("moi_truong")
    tam_ly = stage.get("tam_ly_cot_loi")
    cau_hoi = stage.get("cau_hoi_chinh")

    def _join(xs: list[str]) -> str:
        return "; ".join(x for x in xs if x) or "(không nêu cụ thể)"

    tong_hop, noi_bat = _quy_trinh_highlights(td)
    quy_trinh_block = ""
    if tong_hop or noi_bat:
        quy_trinh_block = (
            "## QUY TRÌNH ĐẦY ĐỦ (12 bước Tử Vi + 10 bước Bát Tự — ĐÃ ground sách thật)\n"
            "Dựa vào tổng hợp KIM TỰ THÁP dưới đây làm XƯƠNG SỐNG bài đọc: ưu tiên các "
            "yếu tố TRỰC TIẾP (60-70%), rồi GIÁN TIẾP (20-25%), TIỀM ẨN (10-15%).\n"
            + (f"- Tổng hợp kim tự tháp: {tong_hop}\n" if tong_hop else "")
            + ("- Các bước nổi bật cần đưa vào lời đọc:\n"
               + "".join(f"  · {x}\n" for x in noi_bat) if noi_bat else "")
            + "\n"
        )

    return (
        "Bạn là nhà luận giải Tử Vi/Bát Tự đọc TÌNH DUYÊN NỮ MỆNH theo paradigm ĐỌC "
        "ĐỒNG DẠNG (không bói). Bạn nhận DỮ LIỆU CẤU TRÚC đã được engine kiểm duyệt "
        "paradigm; việc của bạn là DIỄN ĐẠT thành lời cho người đọc — KHÔNG bịa thêm sao, "
        "KHÔNG tự suy ra cách cục mới.\n\n"

        "## NGUYÊN TẮC PARADIGM (BẮT BUỘC — Iron Rule #4/#6/#8)\n"
        "1. Mệnh là ĐỘNG TỪ: lá số cho biết TÍNH (nguyên liệu trời ban), còn 'mệnh' là "
        "việc XỬ LÝ tính đó. Luôn nói theo kiểu 'cấu trúc của em VẬN HÀNH tốt nhất khi…', "
        "trao quyền chủ động cho người đọc.\n"
        "2. TUYỆT ĐỐI KHÔNG phán: 'khắc chồng', 'số cô quả', 'sẽ ly hôn', 'không lấy được "
        "chồng', hay bất kỳ lời kết án / tiên tri định mệnh nào.\n"
        "3. Định thời chỉ là 'năm khí được kích hoạt' / 'năm cần giữ gìn', KHÔNG phải "
        "lời tiên tri.\n\n"

        "## KHẨU VỊ GIAO TIẾP (nói đúng kiểu người này muốn nghe)\n"
        f"- Giọng: {_join(giong)}\n"
        f"- Độ dài: {_join(do_dai)}\n"
        f"- Cách khung vấn đề: {_join(cach_khung)}\n"
        f"- NÊN: {_join(nen)}\n"
        f"- TRÁNH: {_join(tranh)}\n\n"

        "## CHẶNG TUỔI (điều chỉnh giọng theo độ tuổi)\n"
        f"- Tuổi hiện tại: {tuoi}\n"
        f"- Giọng ưu tiên theo chặng (KHUNG AN TOÀN — ưu tiên hơn khẩu vị sao khi xung): "
        f"{giong_stage or '(không nêu)'}\n"
        f"- Môi trường sống: {moi_truong or '(không nêu)'}\n"
        f"- Tâm lý cốt lõi: {tam_ly or '(không nêu)'}\n"
        f"- Câu hỏi chính của chặng: {cau_hoi or '(không nêu)'}\n"
        "Lưu ý: bé gái ~16 tuổi nói NHẸ - ẤM - gợi mở khác hẳn phụ nữ ~35 tuổi (nói chững "
        "chạc, đi vào lựa chọn thực tế). HÃY chọn giọng đúng với tuổi này.\n\n"

        + quy_trinh_block +
        _cham_cap_block(td) +

        "## CÁCH VIẾT\n"
        "- Viết tiếng Việt, xưng hô ấm áp, tôn trọng.\n"
        "- Bám sát DỮ LIỆU CẤU TRÚC engine cấp (personality, cung Phu Thê, Bát Tự hôn "
        "nhân, reconcile, cách cục đã reframe, định thời). KHÔNG mâu thuẫn dữ liệu.\n"
        "- Với mọi mục mang sắc thái 'cần chú ý': diễn đạt như một TÍNH cần ý thức + chăm "
        "sóc, kèm hành động cụ thể — KHÔNG phán định mệnh.\n"
    )


def _td_payload_for_llm(td: dict) -> dict:
    """Trích phần dữ liệu cốt lõi để bơm cho sage (gọn, đủ ground)."""
    return {
        "input": td.get("input"),
        "stage": td.get("stage"),
        "personality": td.get("personality"),
        "cung_phu_the_tuvi": td.get("cung_phu_the_tuvi"),
        "batu_hon_nhan": td.get("batu_hon_nhan"),
        "song_phai_reconcile": td.get("song_phai_reconcile"),
        "cach_cuc": td.get("cach_cuc"),
        "dinh_thoi": td.get("dinh_thoi"),
        "narration_brief": td.get("narration_brief"),
        # Chẩn đoán cấp độ (chấm cấp + lộ trình) — gọn, đủ để sage chỉ lối cụ thể.
        "chan_doan_cap_do": {
            "cap_do": (td.get("chan_doan_cap_do") or {}).get("cap_do"),
            "ten_cap": (td.get("chan_doan_cap_do") or {}).get("ten_cap"),
            "muc_do_thu_thach": (td.get("chan_doan_cap_do") or {}).get("muc_do_thu_thach"),
            "do_thay_doi_duoc": (td.get("chan_doan_cap_do") or {}).get("do_thay_doi_duoc"),
            "phan_loai": (td.get("chan_doan_cap_do") or {}).get("phan_loai"),
            "tin_hieu_kich_hoat": (td.get("chan_doan_cap_do") or {}).get("tin_hieu_kich_hoat"),
            "lo_trinh": (td.get("chan_doan_cap_do") or {}).get("lo_trinh"),
            "ranh_gioi": (td.get("chan_doan_cap_do") or {}).get("ranh_gioi"),
        },
        # Quy trình đầy đủ: chỉ bơm phần TỔNG HỢP + XẾP HẠNG (gọn, đủ ground) —
        # KHÔNG bơm trọn 22 bước raw để tránh prompt phình + loãng giọng.
        "quy_trinh_tong_hop": {
            "tong_hop_kim_tu_thap":
                (td.get("quy_trinh_day_du") or {}).get("tong_hop_kim_tu_thap"),
            "xep_hang_yeu_to":
                (td.get("quy_trinh_day_du") or {}).get("xep_hang_yeu_to"),
        },
        "_disclaimer": td.get("_disclaimer"),
    }


def _hard_guard_note(flags: list[str]) -> str:
    """Cảnh báo CỨNG chèn vào system-prompt khi regenerate sau khi bắt vi phạm."""
    return (
        "\n\n## ⛔ CẢNH BÁO CỨNG — LẦN TRƯỚC BẠN ĐÃ VI PHẠM PARADIGM\n"
        "Bản nháp vừa rồi dính giọng TIÊN TRI / lời KẾT ÁN ĐỊNH MỆNH (mẫu bắt được: "
        f"{', '.join(flags)}). VIẾT LẠI hoàn toàn: TUYỆT ĐỐI không 'khắc chồng', "
        "'số cô quả', 'sẽ ly hôn', 'khó/không lấy được chồng', không số đề, không "
        "'năm X chắc chắn sẽ…'. Chỉ đọc TÍNH (cấu trúc khí) và gợi cách VẬN HÀNH — "
        "'cấu trúc của em vận hành tốt nhất khi…'. Mệnh là ĐỘNG TỪ, trao quyền chủ động."
    )


def narrate_tinh_duyen(person: dict, tinh_duyen_output: dict) -> str:
    """Diễn đạt output engine tình duyên thành lời sage (đúng khẩu vị + chặng tuổi).

    PARADIGM ENFORCEMENT (Iron #4/#6/#8): output LLM free-form (temp 0.6) là tầng
    rủi ro CAO NHẤT — LLM có thể bịa verdict định mệnh dù data gốc đã sạch. Vì thế
    output BẮT BUỘC qua reframe_check (hermes_guard.paradigm_violations):
      1) sạch → trả luôn.
      2) dính → REGENERATE 1 lần với cảnh báo cứng liệt kê flags (đồng bộ chuẩn
         hermes_service reject+regenerate).
      3) vẫn dính → trả '' để UI fallback về bản cấu trúc ĐÃ-SẠCH (an toàn).

    An toàn tuyệt đối: bất kỳ lỗi nào (registry/provider/LLM) → trả '' (caller fallback
    về bản cấu trúc). KHÔNG charge xu ở đây (đã charge ở run_tinh_duyen).
    """
    td = tinh_duyen_output or {}
    try:
        from engine.ai.agents import run_agent
        from engine.ai.council import _get_agent_provider, sage_model

        from engine.cross_paradigm._common import reframe_check

        provider, model = _get_agent_provider("tu_vi", prefer_reasoning=False)
        model = sage_model(provider, fallback=model)

        base_system_prompt = _build_system_prompt(person, td)
        payload = _td_payload_for_llm(td)

        stage = td.get("stage") or {}
        tuoi = stage.get("tuoi")
        question = (
            f"Hãy đọc TÌNH DUYÊN nữ mệnh (tuổi {tuoi}) dựa trên DỮ LIỆU CẤU TRÚC dưới đây. "
            "Diễn đạt đúng khẩu vị giao tiếp + đúng giọng của chặng tuổi đã nêu trong "
            "system prompt. Nói theo paradigm 'mệnh là động từ', trao quyền chủ động, "
            "KHÔNG bói, KHÔNG phán định mệnh.\n\n"
            "DỮ LIỆU CẤU TRÚC (JSON):\n"
            + _json.dumps(payload, ensure_ascii=False)
        )

        def _call(system_prompt: str) -> str:
            resp = run_agent(
                agent_id="tu_vi",
                provider=provider,
                model=model,
                question=question,
                chart_data={"system_prompt_override": system_prompt, "tinh_duyen": payload},
                max_tokens=1400,
                temperature=0.6,
            )
            content = (getattr(resp, "content", "") or "").strip()
            # Provider mock-fallback (thiếu key / lỗi tạm) KHÔNG được lộ cho user trả phí.
            if "[MOCK" in content or "mock response" in content or "paste api key" in content.lower():
                return ""
            return content

        # Lần 1.
        content = _call(base_system_prompt)
        ok, flags = reframe_check(content)
        if ok:
            return content

        # Lần 2 (regenerate với cảnh báo cứng) — chuẩn reject+regenerate toàn hệ.
        content = _call(base_system_prompt + _hard_guard_note(flags))
        ok, _ = reframe_check(content)
        if ok:
            return content

        # Vẫn vi phạm → KHÔNG leak. Trả '' để UI fallback bản cấu trúc đã-sạch.
        return ""
    except Exception:
        return ""


__all__ = ["narrate_tinh_duyen"]
