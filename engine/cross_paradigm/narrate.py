"""Sage narrate cho TÌNH DUYÊN nữ mệnh (chặng 3 của bookflow đọc đồng dạng).

Engine `read_tinh_duyen` trả DỮ LIỆU CẤU TRÚC (deterministic, paradigm-safe). Lớp NÀY
gọi LLM (model non-reasoning, nhanh) để DIỄN ĐẠT dữ liệu đó thành lời cho user, ĐÚNG
khẩu vị giao tiếp + đúng chặng tuổi.

CHẮC TAY (Pha A 2026-06-26): "lời thầy" là sản phẩm TRẢ PHÍ (30 xu) nên KHÔNG được
phụ thuộc 1 provider — rớt 1 cái là mất lời thầy. Ta thử LẦN LƯỢT chuỗi provider
[deepseek, minimax, gemini] (đều model non-reasoning, nhanh). MỖI provider đi qua ĐỦ
guard sẵn có (chặn mock-leak '[MOCK', reframe_check → regenerate 1 lần với cảnh báo
cứng). Provider nào cho kết quả SẠCH + non-empty đầu tiên → DÙNG luôn (thắng). Hết
chuỗi vẫn fail → '' (UI fallback bản cấu trúc đã-sạch, an toàn như cũ).

PARADIGM (Iron Rule #4/#6/#8): KHÔNG bói. Mệnh là động từ — "cấu trúc của em vận hành
tốt nhất khi…". TUYỆT ĐỐI không phán 'khắc chồng / số cô quả / sẽ ly hôn'.

An toàn: mọi lỗi LLM/registry → trả '' (UI fallback về bản cấu trúc, KHÔNG sập).
"""
from __future__ import annotations

import concurrent.futures as _futures
import json as _json
import logging as _logging
import re as _re
from typing import Any

_log = _logging.getLogger(__name__)

# BUG5 — số token TỐI ĐA cho 1 lượt narrate. 1400 cắt CỤT lời thầy giữa câu
# ("…nếu không sẽ tìm n"). Nâng lên 2400 (lời thầy giàu hơn, đủ kết câu). Model
# non-reasoning nên token = chữ thật, không tốn vào <think>.
_NARRATE_MAX_TOKENS = 2400

# BUG7 — timeout MỖI lượt gọi LLM (giây). Provider treo/chậm bị BỎ → nhảy provider
# kế; tổng narrate KHÔNG treo vô hạn. 45s đủ cho model non-reasoning trả ~2400 token.
_NARRATE_CALL_TIMEOUT_S = 45.0

# Dấu KẾT CÂU hợp lệ để cắt sạch (BUG5): kết thúc tại 1 trong các dấu này.
_SENTENCE_END_RE = _re.compile(r"[.!?…。！？”\"')\]]+$")


def _trim_to_last_sentence(text: str) -> str:
    """BUG5 — nếu text bị cắt CỤT giữa câu (do hết token), lùi về RANH GIỚI CÂU
    HOÀN CHỈNH cuối cùng để không bỏ lửng ('…sẽ tìm n').

    - Đã kết thúc bằng dấu kết câu → giữ nguyên.
    - Ngược lại: cắt tại dấu kết câu cuối cùng (. ! ? … 。！？) còn 1 đoạn đủ dài.
      Nếu không tìm thấy dấu nào (cả bài là 1 câu cụt) → giữ nguyên (thà có còn hơn
      mất; reframe vẫn chạy)."""
    if not text:
        return text
    s = text.rstrip()
    if not s:
        return s
    # Đã kết câu sạch → khỏi cắt.
    if _SENTENCE_END_RE.search(s):
        return s
    # Tìm vị trí dấu kết câu cuối cùng (gồm cả dấu đóng nháy/ngoặc liền sau).
    last = -1
    for m in _re.finditer(r"[.!?…。！？]+[”\"')\]]*", s):
        last = m.end()
    if last <= 0:
        return s  # không có ranh giới câu nào → cả bài là 1 câu cụt, giữ nguyên
    head = s[:last].rstrip()
    # Giữ phần ĐẦU (đã kết câu sạch) nếu nó đủ dày tối thiểu (≥40 ký tự = ít nhất 1
    # câu thật). Bỏ phần đuôi cụt ('…nếu không sẽ tìm n'). Nếu head quá ngắn (cả bài
    # gần như chỉ là 1 mệnh đề chưa xong) → giữ nguyên (thà có còn hơn mất).
    if len(head) >= 40:
        return head
    return s

# Chuỗi provider thử lần lượt cho "lời thầy" tình duyên. ƯU TIÊN deepseek (giỏi Đông
# phương + nhanh + tin cậy), rồi minimax (token plan), rồi gemini (free, dự phòng). Mỗi
# provider sẽ được map sang model NHANH non-reasoning qua sage_model (prompt sage lớn →
# model reasoning đốt token vào <think> → rỗng). mock KHÔNG nằm trong chuỗi (mock-leak
# bị chặn ở _call).
# BUG6 — chuỗi DÀI hơn để 1 provider chết (key sai / 401 / treo) KHÔNG làm rỗng lời
# thầy (sản phẩm 30 xu). Ưu tiên rẻ+nhanh trước (deepseek/minimax/gemini), rồi
# escalate provider khác (zai/openrouter free, anthropic chất lượng) nếu nhóm đầu
# fail. mock KHÔNG trong chuỗi (mock-leak bị chặn ở _call). Provider chưa cấu hình /
# unhealthy bị skip ở vòng lặp → chuỗi tự co theo môi trường.
_NARRATE_PROVIDER_CHAIN: list[str] = [
    "deepseek", "minimax", "gemini", "zai", "openrouter", "anthropic",
]


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


def _cau_hoi_tuoi_block(td: dict) -> str:
    """Dựng khối CÂU HỎI THEO TUỔI — lời thầy cấu trúc QUANH việc TRẢ LỜI các câu hỏi
    chính của chặng tuổi (tự nhiên hơn so với liệt kê dữ liệu khô).

    Mỗi câu đã có sẵn câu trả lời rút từ section (paradigm-safe). Lời thầy nên dệt
    các câu trả lời này thành mạch, ưu tiên câu tần suất CAO, và:
    - câu can_gieo_que=True: KHÔNG tự chốt, mời người đọc gieo quẻ Mai Hoa (cần tâm).
    - câu can_la_so_doi=True: nhắc cần lá số người kia (so-sánh-duyên)."""
    items = td.get("cau_hoi_tuoi") or []
    if not items:
        return ""
    lines = [
        "## CÂU HỎI CHÍNH CỦA TUỔI NÀY (dệt lời thầy QUANH việc trả lời các câu này)",
        "Người ở tuổi này thường mang đúng những thắc mắc dưới đây. Hãy để bài đọc TRẢ "
        "LỜI tự nhiên cho chúng — KHÔNG liệt kê khô, mà dệt thành mạch tâm tình, ưu tiên "
        "câu tần suất CAO. Mỗi câu kèm sẵn câu trả lời ĐÃ ground section (đừng bịa thêm):",
    ]
    # Ưu tiên câu tần suất cao lên trước, giữ tối đa 6 câu cho prompt gọn.
    ordered = sorted(items, key=lambda q: 0 if q.get("tan_suat") == "cao" else 1)
    for q in ordered[:6]:
        ch = (q.get("cau_hoi") or "").strip()
        tl = (q.get("tra_loi") or "").strip()
        if not ch:
            continue
        lines.append(f"- HỎI: {ch}")
        if q.get("can_gieo_que"):
            lines.append(
                "  → ĐÂY LÀ CÂU QUYẾT ĐỊNH: KHÔNG tự chốt nên/không từ lá số. Nhẹ nhàng "
                "mời người đọc GIEO QUẺ MAI HOA (đọc đồng dạng — cần tâm + ngoại ứng + "
                "tư thế), nói rõ quyết định là của họ."
            )
        elif q.get("can_la_so_doi"):
            lines.append(
                "  → Cần lá số người kia (so-sánh-duyên); chưa có thì gợi đọc cung Phu Thê "
                "của chính người hỏi (kiểu khí chất hợp), KHÔNG chấm điểm hợp/không."
            )
        if tl:
            lines.append(f"  ĐÁP (ground sẵn): {tl}")
    lines.append(
        "- Với mọi câu mang sắc thái lo sợ ('khắc chồng', 'người thứ ba', 'có con "
        "không'): TRẢ LỜI qua CẤP ĐỘ + lộ trình + cấu trúc cần để ý — TUYỆT ĐỐI không "
        "verdict có/không, không phán-vào-người."
    )
    return "\n".join(lines) + "\n\n"


def _build_system_prompt(person: dict, td: dict) -> str:
    """Dựng system-prompt narrate từ khẩu vị giao tiếp + chặng tuổi + paradigm.

    Giới-tính-hoá: nữ (flagship) = 'chồng / 官杀'; nam (mirror) = 'vợ / 财'. Prompt
    nhắc sage nói đúng phối ngẫu theo giới + KHÔNG bao giờ phán 'tái hôn/khắc chồng'
    kiểu nữ cho nam.
    """
    personality = td.get("personality") or {}
    stage = td.get("stage") or {}
    gender = ((td.get("input") or {}).get("gender")
              or (person or {}).get("gender") or "nữ")
    is_male = str(gender).strip().lower() in ("nam", "male", "m", "trai", "boy")
    label = "vợ" if is_male else "chồng"
    gioi_label = "NAM MỆNH" if is_male else "NỮ MỆNH"
    sao_pn = "财 (Chính Tài/Thiên Tài)" if is_male else "官杀 (Chính Quan/Thất Sát)"
    khac_pn = "比劫 Tỷ Kiếp đoạt Tài" if is_male else "伤官 Thương Quan khắc Quan"
    cam_verdict = ("'khắc vợ', 'sẽ ly hôn', 'không lấy được vợ'" if is_male
                   else "'khắc chồng', 'số cô quả', 'sẽ ly hôn', 'không lấy được chồng'")

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
        f"Bạn là nhà luận giải Tử Vi/Bát Tự đọc TÌNH DUYÊN {gioi_label} theo paradigm ĐỌC "
        "ĐỒNG DẠNG (không bói). Bạn nhận DỮ LIỆU CẤU TRÚC đã được engine kiểm duyệt "
        "paradigm; việc của bạn là DIỄN ĐẠT thành lời cho người đọc — KHÔNG bịa thêm sao, "
        "KHÔNG tự suy ra cách cục mới.\n\n"

        "## GIỚI TÍNH NGƯỜI ĐỌC (BẮT BUỘC nói đúng phối ngẫu)\n"
        f"- Người đọc là {gioi_label}: phối ngẫu = '{label}'. Sao phối ngẫu = {sao_pn}; "
        f"cấu trúc khắc phối ngẫu = {khac_pn}.\n"
        f"- Luôn gọi phối ngẫu là '{label}' (KHÔNG nói '{'chồng' if is_male else 'vợ'}'). "
        + ("Với NAM: KHÔNG BAO GIỜ dùng khung nữ mệnh ('tái hôn kiểu nữ', 'khắc chồng', "
           "'số làm lẽ') — đọc cơ học 财/khắc thê cho đúng.\n\n" if is_male else
           "\n\n")

        + "## NGUYÊN TẮC PARADIGM (BẮT BUỘC — Iron Rule #4/#6/#8)\n"
        "1. Mệnh là ĐỘNG TỪ: lá số cho biết TÍNH (nguyên liệu trời ban), còn 'mệnh' là "
        "việc XỬ LÝ tính đó. Luôn nói theo kiểu 'cấu trúc của em VẬN HÀNH tốt nhất khi…', "
        "trao quyền chủ động cho người đọc.\n"
        f"2. TUYỆT ĐỐI KHÔNG phán: {cam_verdict}, hay bất kỳ lời kết án / tiên tri định mệnh nào.\n"
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

        + _cau_hoi_tuoi_block(td) +
        quy_trinh_block +
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
        # Câu hỏi chính của tuổi + câu trả lời ground sẵn — XƯƠNG SỐNG để dệt lời thầy.
        "cau_hoi_tuoi": td.get("cau_hoi_tuoi"),
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

    CHẮC TAY — CHUỖI FALLBACK PROVIDER (Pha A): thử lần lượt [deepseek, minimax, gemini]
    (model non-reasoning, nhanh). MỖI provider đi qua ĐỦ guard 2-pass: pass-1 → nếu dính
    paradigm thì regenerate 1 lần với cảnh báo cứng (pass-2). Provider cho kết quả SẠCH +
    non-empty đầu tiên → DÙNG luôn. Provider trả rỗng / mock-leak / vi-phạm-không-cứu-được
    → THỬ provider kế. Hết chuỗi vẫn fail → '' (UI fallback bản cấu trúc đã-sạch).

    PARADIGM ENFORCEMENT (Iron #4/#6/#8): output LLM free-form (temp 0.6) là tầng rủi ro
    CAO NHẤT — LLM có thể bịa verdict định mệnh dù data gốc đã sạch. Vì thế output BẮT
    BUỘC qua reframe_check (hermes_guard.paradigm_violations) ở MỖI provider.

    An toàn tuyệt đối: bất kỳ lỗi nào (registry/provider/LLM) → trả '' (caller fallback
    về bản cấu trúc). KHÔNG charge xu ở đây (đã charge ở run_tinh_duyen). Log provider
    nào THẮNG để quan sát — KHÔNG lộ ra user.
    """
    td = tinh_duyen_output or {}
    try:
        from engine.ai.agents import run_agent
        from engine.ai.council import sage_model
        from engine.ai.registry import get_registry

        from engine.cross_paradigm._common import reframe_check

        base_system_prompt = _build_system_prompt(person, td)
        payload = _td_payload_for_llm(td)

        stage = td.get("stage") or {}
        tuoi = stage.get("tuoi")
        _gender = ((td.get("input") or {}).get("gender")
                   or (person or {}).get("gender") or "nữ")
        _gioi = ("nam mệnh" if str(_gender).strip().lower() in
                 ("nam", "male", "m", "trai", "boy") else "nữ mệnh")
        question = (
            f"Hãy đọc TÌNH DUYÊN {_gioi} (tuổi {tuoi}) dựa trên DỮ LIỆU CẤU TRÚC dưới đây. "
            "Diễn đạt đúng khẩu vị giao tiếp + đúng giọng của chặng tuổi đã nêu trong "
            "system prompt. Nói theo paradigm 'mệnh là động từ', trao quyền chủ động, "
            "KHÔNG bói, KHÔNG phán định mệnh.\n\n"
            "DỮ LIỆU CẤU TRÚC (JSON):\n"
            + _json.dumps(payload, ensure_ascii=False)
        )

        reg = get_registry()

        def _call(provider, model, system_prompt: str) -> str:
            """1 lần gọi LLM trên `provider`. Trả '' nếu rỗng HOẶC mock-leak (mock-fallback
            khi thiếu key / lỗi tạm KHÔNG được lộ cho user trả phí).

            BUG7 — bọc TIMEOUT (_NARRATE_CALL_TIMEOUT_S) bằng thread: provider treo/chậm
            (mỗi provider tự đặt HTTP-timeout riêng, có cái 180s) bị BỎ → caller nhảy
            provider kế. KHÔNG để 1 lượt treo kéo cả narrate >10 phút.
            BUG5 — nâng max_tokens + cắt sạch ở ranh giới câu (không bỏ lửng giữa câu)."""
            def _do() -> str:
                resp = run_agent(
                    agent_id="tu_vi",
                    provider=provider,
                    model=model,
                    question=question,
                    chart_data={"system_prompt_override": system_prompt,
                                "tinh_duyen": payload},
                    max_tokens=_NARRATE_MAX_TOKENS,
                    temperature=0.6,
                )
                return (getattr(resp, "content", "") or "").strip()

            # KHÔNG dùng `with ThreadPoolExecutor` (context-exit gọi shutdown(wait=True)
            # → BLOCK chờ thread treo xong, vô hiệu hoá timeout). Tạo executor rời, khi
            # timeout thì shutdown(wait=False) bỏ mặc thread chết nền (HTTP-timeout
            # provider sẽ tự kết nó), narrate đi tiếp ngay.
            ex = _futures.ThreadPoolExecutor(max_workers=1)
            try:
                fut = ex.submit(_do)
                content = fut.result(timeout=_NARRATE_CALL_TIMEOUT_S)
                ex.shutdown(wait=False)
            except _futures.TimeoutError:
                ex.shutdown(wait=False, cancel_futures=True)
                _log.warning("narrate_tinh_duyen: provider %s TIMEOUT >%.0fs → bỏ, thử kế",
                             getattr(provider, "name", "?"), _NARRATE_CALL_TIMEOUT_S)
                return ""
            except Exception:
                ex.shutdown(wait=False, cancel_futures=True)
                return ""
            if not content:
                return ""
            if "[MOCK" in content or "mock response" in content or "paste api key" in content.lower():
                return ""
            # BUG5 — cắt sạch ở câu hoàn chỉnh cuối (tránh '…sẽ tìm n').
            return _trim_to_last_sentence(content)

        def _try_provider(provider, model) -> str:
            """Chạy ĐỦ guard 2-pass cho 1 provider. Trả lời SẠCH+non-empty hoặc ''."""
            # Pass 1.
            content = _call(provider, model, base_system_prompt)
            if content:
                ok, flags = reframe_check(content)
                if ok:
                    return content
                # Pass 2 — regenerate với cảnh báo cứng (chuẩn reject+regenerate toàn hệ).
                content = _call(provider, model, base_system_prompt + _hard_guard_note(flags))
                if content:
                    ok, _ = reframe_check(content)
                    if ok:
                        return content
            return ""

        # ── CHUỖI FALLBACK ─────────────────────────────────────────────────────
        for name in _NARRATE_PROVIDER_CHAIN:
            try:
                provider = reg.get(name)
            except KeyError:
                continue
            # Bỏ qua provider chưa cấu hình hoặc đã đánh dấu unhealthy phiên này.
            if not provider.is_configured or reg.is_unhealthy(name):
                continue
            model = sage_model(provider, fallback=provider.default_model)
            try:
                content = _try_provider(provider, model)
            except Exception:
                content = ""
            if content:
                _log.info("narrate_tinh_duyen: provider THẮNG = %s (model=%s)", name, model)
                return content
            _log.info("narrate_tinh_duyen: provider %s fail (rỗng/mock/vi-phạm) → thử kế", name)

        # Hết chuỗi vẫn fail → KHÔNG leak. Trả '' để UI fallback bản cấu trúc đã-sạch.
        _log.warning("narrate_tinh_duyen: hết chuỗi provider, fallback bản cấu trúc")
        return ""
    except Exception:
        return ""


__all__ = ["narrate_tinh_duyen"]
