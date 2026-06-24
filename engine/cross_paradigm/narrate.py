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
