"""考时定刻 / 乾坤流度数法 — 考刻 LỤC THÂN (Thiết Bản, 图解 tr.118 + tr.2172-2197).

考刻 = đỉnh cao chính xác Thiết Bản: dùng LỤC THÂN ĐÃ BIẾT (sinh tiêu cha/mẹ...) để
neo đúng KHẮC sinh (8 khắc × 15 phân). Đặt ở GIA ĐẠO (cần bát tự / sinh tiêu cha mẹ).

乾坤流度数法 (sách tr.2184-2197), VALIDATE cặp kiểm 图解:
  年柱 起卦 (河洛数, KHÁC 太玄) → 六爻纳甲 → 父母爻 → tra 乾宫/坤宫甲流度 → sinh tiêu cha/mẹ.
  Ví dụ sách: 年柱 甲子 → 水地比 → 父母爻 乙巳 → 乾宫[巳]=9253 "父命蛇年生方合" (蛇=巳). ✓

KHÁC các phép khác: 起卦 ở đây dùng 河洛配数 (戊1乙癸2庚3辛4 壬甲6 丁7丙8己9 · 5寄中;
địa chi 河图 sinh-thành), KHÔNG phải 太玄数. Tái dùng 六爻纳甲 từ engine.luc_hao.jingfang.
"""
from __future__ import annotations

from core.hexagram import get_hexagram_by_binary
from engine.luc_hao import jingfang as jf
from engine.thiet_ban.bat_quai_lan import HAU_THIEN_TO_BITS
from engine.thiet_ban.lap_so import tra_dieu_van

# ── 河洛 起卦 (考刻) — 天干配数: 戊1, 乙癸2, 庚3, 辛4, 壬甲6, 丁7, 丙8, 己9 (5寄中) ──
HALOC_CAN = {"Giáp": 6, "Ất": 2, "Bính": 8, "Đinh": 7, "Mậu": 1,
             "Kỷ": 9, "Canh": 3, "Tân": 4, "Nhâm": 6, "Quý": 2}
# 地支 河图 sinh-thành (mỗi chi 2 số): 亥子1,6 · 寅卯3,8 · 巳午2,7 · 申酉4,9 · 辰戌丑未5,10
HALOC_CHI = {"Tý": (1, 6), "Hợi": (1, 6), "Dần": (3, 8), "Mão": (3, 8),
             "Tỵ": (2, 7), "Ngọ": (2, 7), "Thân": (4, 9), "Dậu": (4, 9),
             "Thìn": (5, 10), "Tuất": (5, 10), "Sửu": (5, 10), "Mùi": (5, 10)}

CHI12 = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
         "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
ZODIAC = {"Tý": "鼠 (Chuột)", "Sửu": "牛 (Trâu)", "Dần": "虎 (Hổ)", "Mão": "兔 (Mèo)",
          "Thìn": "龙 (Rồng)", "Tỵ": "蛇 (Rắn)", "Ngọ": "马 (Ngựa)", "Mùi": "羊 (Dê)",
          "Thân": "猴 (Khỉ)", "Dậu": "鸡 (Gà)", "Tuất": "狗 (Chó)", "Hợi": "猪 (Lợn)"}
ZODIAC_ZH = {"Tý": "鼠", "Sửu": "牛", "Dần": "虎", "Mão": "兔", "Thìn": "龙", "Tỵ": "蛇",
             "Ngọ": "马", "Mùi": "羊", "Thân": "猴", "Dậu": "鸡", "Tuất": "狗", "Hợi": "猪"}
# Vùng 条文 流度 (9003-10155) rơi vào trang 下篇 THIẾU trong scan → corpus dính code 流度
# (vd "辛丙壬戊") thay vì câu thật. Câu CHUẨN tái dựng theo pattern sách đã xác nhận:
#   乾宫[chi]="父命〔zodiac〕年生方合" (KIỂM 9003鼠/9303午/9253蛇); 坤宫[chi]="母命〔zodiac〕年生方合".
_CAN_CHARS = set("甲乙丙丁戊己庚辛壬癸月支")

# ── 流度 密数 (图解 tr.4607-4661) — quy luật số học SẠCH, KIỂM khớp cặp kiểm ──
#  乾宫甲流度 (cha): 9003 + chi_index×50 ;  坤宫甲流度 (mẹ): 9605 + chi_index×50
LUU_DO_CAN = {c: 9003 + i * 50 for i, c in enumerate(CHI12)}    # cha
LUU_DO_KHON = {c: 9605 + i * 50 for i, c in enumerate(CHI12)}   # mẹ


def cast_que_kao_khac(can: str, chi: str) -> tuple[str, int, int]:
    """起卦 考刻 (河洛): tổng số LẺ → quái trên (后天), tổng CHẴN → quái dưới.
    KIỂM: 甲子 → 甲6,子(1,6): lẻ {1}=1→坎(上), chẵn {6,6}=12→2→坤(dưới) = 水地比 (010000)."""
    nums = [HALOC_CAN[can], *HALOC_CHI[chi]]
    odd = sum(n for n in nums if n % 2)
    even = sum(n for n in nums if n % 2 == 0)
    upper = HAU_THIEN_TO_BITS[odd % 10]      # 弃十位, lấy hàng đơn vị
    lower = HAU_THIEN_TO_BITS[even % 10]
    return upper + lower, odd, even


def phu_mau_hao(binary: str) -> str | None:
    """Tìm 父母爻 (hào sinh ra 卦宫) → trả CHI nạp giáp của nó. 2 hào → gần 世爻 hơn."""
    _, _, palace_elem = jf.palace_of(binary)
    najia = jf.najia_of(binary)                       # hào 1..6 (dưới→trên)
    shih = jf.shih_yao_position(binary)
    pm = [(i, chi) for i, (_, chi) in enumerate(najia, 1)
          if jf.luc_than_of(jf.BRANCH_ELEMENT[chi], palace_elem) == "Phụ Mẫu"]
    if not pm:
        return None
    if len(pm) > 1:
        pm.sort(key=lambda t: abs(t[0] - shih))       # gần 世 nhất
    return pm[0][1]


def _flu(mat_so: int) -> str | None:
    """条文 流度 thật từ corpus (nếu SẠCH); None nếu OCR dính prose/code 流度."""
    v = tra_dieu_van(mat_so, prefer_tujie=True) or {}
    zh = v.get("zh")
    if not zh:
        return None
    if any(k in zh for k in ("基本数", "起算", "运算", "步骤")):  # prose ví dụ
        return None
    if len(zh) <= 6 and set(zh) <= _CAN_CHARS:                  # code 流度 (vd 辛丙壬戊)
        return None
    return zh


def kao_khac_cha_me(year_can: str, year_chi: str) -> dict:
    """年柱 → 卦 → 父母爻 → 流度 → DỰ ĐOÁN sinh tiêu cha/mẹ (初刻).

    Trả lookup cả 乾宫(cha) + 坤宫(mẹ). Sinh tiêu = CHI của 父母爻 (流度[chi]→命(chi)年).
    Đây là KHẮC ĐẦU (初刻); nếu chưa khớp lục thân thật thì cần dò khắc/phân (考刻 sâu)."""
    binary, odd, even = cast_que_kao_khac(year_can, year_chi)
    que = get_hexagram_by_binary(binary).name_vi
    pm = phu_mau_hao(binary)
    if not pm:
        return {"que": que, "binary": binary, "phu_mau_chi": None,
                "ghi_chu": "Quẻ năm không có 父母爻 hiện (hiếm) — cần phép khắc khác."}
    cs, ms = LUU_DO_CAN[pm], LUU_DO_KHON[pm]
    z = ZODIAC_ZH[pm]
    return {
        "que": que, "binary": binary, "tong_le": odd, "tong_chan": even,
        "phu_mau_chi": pm, "sinh_tieu_du_doan": ZODIAC[pm],
        "cha": {"cung": "乾宫甲流度", "mat_so": cs, "sinh_tieu": ZODIAC[pm],
                "dieu_van_chuan": f"父命{z}年生方合。", "dieu_van_corpus": _flu(cs)},
        "me": {"cung": "坤宫甲流度", "mat_so": ms, "sinh_tieu": ZODIAC[pm],
               "dieu_van_chuan": f"母命{z}年生方合。", "dieu_van_corpus": _flu(ms)},
        "_phap": "乾坤流度数法 (考刻 初刻). 男命khớp 乾(cha) trước, 女命khớp 坤(mẹ) trước. "
                 "Câu CHUẨN tái dựng theo pattern sách (vùng 条文 này thiếu trong scan).",
    }


def doi_chieu_luc_than(year_can: str, year_chi: str,
                       cha_chi: str | None = None,
                       me_chi: str | None = None) -> dict:
    """GIA ĐẠO: so sinh tiêu cha/mẹ ĐÃ BIẾT với dự đoán 父母爻 → xác nhận / cần dò khắc.

    cha_chi/me_chi = ĐỊA CHI năm sinh cha/mẹ (từ bát tự gia đạo). Trả khớp hay lệch."""
    r = kao_khac_cha_me(year_can, year_chi)
    pm = r.get("phu_mau_chi")
    if not pm:
        return {**r, "ket_qua": "không lập được 父母爻"}
    khop = []
    if cha_chi and cha_chi == pm:
        khop.append(f"CHA sinh năm {ZODIAC[pm]} — KHỚP 乾宫流度 (sơ khắc xác nhận)")
    if me_chi and me_chi == pm:
        khop.append(f"MẸ sinh năm {ZODIAC[pm]} — KHỚP 坤宫流度 (sơ khắc xác nhận)")
    if not khop and (cha_chi or me_chi):
        msg = (f"父母爻 sơ-khắc dự đoán {ZODIAC[pm]}, KHÁC sinh tiêu cha"
               f"({ZODIAC.get(cha_chi, cha_chi)})/mẹ({ZODIAC.get(me_chi, me_chi)}) đã biết "
               f"→ cần DÒ khắc/phân khác (考刻 sâu: ±khắc tới khi khớp).")
        return {**r, "ket_qua": "lệch sơ-khắc", "ghi_chu": msg}
    return {**r, "ket_qua": "khớp",
            "khop": khop or ["chưa cấp sinh tiêu cha/mẹ để đối chiếu"]}


def kao_khac_from_birth(birth_dt: str, cha_chi: str | None = None,
                        me_chi: str | None = None,
                        timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """考刻 từ GIỜ SINH: rút 年柱 → 乾坤流度 → dự đoán + đối chiếu sinh tiêu cha/mẹ.

    cha_chi/me_chi = ĐỊA CHI năm sinh cha/mẹ (vd 'Thìn'); để trống = chỉ dự đoán sơ-khắc."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    p = extract_tu_tru(birth_dt, timezone)["pillars"]
    yc, yz = p["year"]["stem"], p["year"]["branch"]
    out = {"nam_tru": f"{yc} {yz}", **doi_chieu_luc_than(yc, yz, cha_chi, me_chi)}
    # 父母生肖化卦取数 (lục thân bổ sung) khi có cả sinh tiêu cha + mẹ
    if cha_chi and me_chi:
        from engine.thiet_ban.bat_quai_gia_tac import phu_mau_sinh_tieu
        q = phu_mau_sinh_tieu(cha_chi, me_chi)
        v = tra_dieu_van(q["so"], prefer_tujie=True) or {}
        out["phu_mau_hoa_que"] = {**q, "dieu_van": v.get("zh"), "vi": v.get("vi"),
                                  "phap": "父母生肖化卦取数 (父支上·母支下 → 八卦加则)"}
    return out
