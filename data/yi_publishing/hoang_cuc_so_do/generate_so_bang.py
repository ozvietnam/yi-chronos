#!/usr/bin/env python3
"""Generator BẢNG SỐ KHỞI-CHUNG (天地始终之数表) — Hoàng Cực Kinh Thế.

Chứng minh hiểu: tái sinh toàn bộ 64 ô từ NGUYÊN LÝ của Thiệu Ung,
KHÔNG chép số. Đối chiếu với bản qwen-VL đọc từ ảnh để verify.

Nguyên lý (giải mã từ tr.230-231 + Nội Thiên tr.235):
- 8 hàng đẳng (rank) đồng dạng 3 lớp:
    quẻ tiên-thiên | đơn vị thời gian | thiên thể
- 8 số nền S: khởi 1, nhân luân phiên ×12 (số hội/thế/nguyệt...) rồi ×30 (vận/tuế/nhật...)
- SỐ tại ô (ngoài a, trong b) = S[a] × S[b]   (bảng đối xứng theo số)
- QUẺ tại ô = quẻ-ngoài(thượng) + quẻ-trong(hạ) theo tiên thiên phương đồ
"""
import json
from pathlib import Path

# 8 đẳng — đồng dạng 3 lớp (thứ tự tiên thiên: Càn Đoài Ly Chấn Tốn Khảm Cấn Khôn)
TRIGRAM = ["乾","兑","离","震","巽","坎","艮","坤"]
TRI_VI  = ["Càn","Đoài","Ly","Chấn","Tốn","Khảm","Cấn","Khôn"]
TIME    = ["元","会","运","世","岁","月","日","时"]
TIME_VI = ["Nguyên","Hội","Vận","Thế","Tuế","Nguyệt","Nhật","Thời"]
BODY    = ["日","月","星","辰","石","土","火","水"]
BODY_VI = ["Nhật","Nguyệt","Tinh","Thần","Thạch","Thổ","Hỏa","Thủy"]

# 8 số nền: 1, ×12, ×30, ×12, ×30, ×12, ×30, ×12
S = [1]
for i in range(1, 8):
    S.append(S[-1] * (12 if i % 2 == 1 else 30))

# 64 quẻ Phục Hy phương đồ: hàng = quẻ THƯỢNG (ngoài), cột = quẻ HẠ (trong).
# Tên 64 quẻ theo cặp (thượng, hạ) — bảng chuẩn Kinh Dịch.
HEX64 = {
 ("乾","乾"):"乾",("乾","兑"):"夬",("乾","离"):"大有",("乾","震"):"大壮",("乾","巽"):"小畜",("乾","坎"):"需",("乾","艮"):"大畜",("乾","坤"):"泰",
 ("兑","乾"):"履",("兑","兑"):"兑",("兑","离"):"睽",("兑","震"):"归妹",("兑","巽"):"中孚",("兑","坎"):"节",("兑","艮"):"损",("兑","坤"):"临",
 ("离","乾"):"同人",("离","兑"):"革",("离","离"):"离",("离","震"):"丰",("离","巽"):"家人",("离","坎"):"既济",("离","艮"):"贲",("离","坤"):"明夷",
 ("震","乾"):"无妄",("震","兑"):"随",("震","离"):"噬嗑",("震","震"):"震",("震","巽"):"益",("震","坎"):"屯",("震","艮"):"颐",("震","坤"):"复",
 ("巽","乾"):"姤",("巽","兑"):"大过",("巽","离"):"鼎",("巽","震"):"恒",("巽","巽"):"巽",("巽","坎"):"井",("巽","艮"):"蛊",("巽","坤"):"升",
 ("坎","乾"):"讼",("坎","兑"):"困",("坎","离"):"未济",("坎","震"):"解",("坎","巽"):"涣",("坎","坎"):"坎",("坎","艮"):"蒙",("坎","坤"):"师",
 ("艮","乾"):"遁",("艮","兑"):"咸",("艮","离"):"旅",("艮","震"):"小过",("艮","巽"):"渐",("艮","坎"):"蹇",("艮","艮"):"艮",("艮","坤"):"谦",
 ("坤","乾"):"否",("坤","兑"):"萃",("坤","离"):"晋",("坤","震"):"豫",("坤","巽"):"观",("坤","坎"):"比",("坤","艮"):"剥",("坤","坤"):"坤",
}
HEX_VI = {"乾":"Càn","夬":"Quải","大有":"Đại Hữu","大壮":"Đại Tráng","小畜":"Tiểu Súc","需":"Nhu","大畜":"Đại Súc","泰":"Thái",
 "履":"Lý","兑":"Đoài","睽":"Khuê","归妹":"Quy Muội","中孚":"Trung Phu","节":"Tiết","损":"Tổn","临":"Lâm",
 "同人":"Đồng Nhân","革":"Cách","离":"Ly","丰":"Phong","家人":"Gia Nhân","既济":"Ký Tế","贲":"Bí","明夷":"Minh Di",
 "无妄":"Vô Vọng","随":"Tùy","噬嗑":"Phệ Hạp","震":"Chấn","益":"Ích","屯":"Truân","颐":"Di","复":"Phục",
 "姤":"Cấu","大过":"Đại Quá","鼎":"Đỉnh","恒":"Hằng","巽":"Tốn","井":"Tỉnh","蛊":"Cổ","升":"Thăng",
 "讼":"Tụng","困":"Khốn","未济":"Vị Tế","解":"Giải","涣":"Hoán","坎":"Khảm","蒙":"Mông","师":"Sư",
 "遁":"Độn","咸":"Hàm","旅":"Lữ","小过":"Tiểu Quá","渐":"Tiệm","蹇":"Kiển","艮":"Cấn","谦":"Khiêm",
 "否":"Bĩ","萃":"Tụy","晋":"Tấn","豫":"Dự","观":"Quán","比":"Tỷ","剥":"Bác","坤":"Khôn"}

def build():
    cells = []
    for a in range(8):        # ngoài (thượng) — cột nhóm
        for b in range(8):    # trong (hạ) — hàng trong nhóm
            out = HEX64[(TRIGRAM[a], TRIGRAM[b])]
            cells.append({
                "stt": f"{b+1}-{a+1}",
                "que": out, "que_vi": HEX_VI[out],
                "thoi_gian": f"{TIME[a]}之{TIME[b]}", "tg_vi": f"{TIME_VI[a]}-chi-{TIME_VI[b]}",
                "thien_the": f"{BODY[a]}之{BODY[b]}", "tt_vi": f"{BODY_VI[a]}-chi-{BODY_VI[b]}",
                "que_kep": f"{TRIGRAM[a]}之{TRIGRAM[b]}", "qk_vi": f"{TRI_VI[a]}-chi-{TRI_VI[b]}",
                "so": S[a] * S[b],
            })
    return cells

if __name__ == "__main__":
    cells = build()
    Path("data/yi_publishing/hoang_cuc_so_do/so_bang_64.json").write_text(
        json.dumps({"S_nen": S, "cells": cells}, ensure_ascii=False, indent=1))
    print(f"Sinh {len(cells)} ô. S nền = {S}")
    print("Vài ô kiểm chứng:")
    idx = {c["que_kep"]: c for c in cells}
    for qk in ["乾之乾","乾之兑","离之离","离之坤","震之坤","坤之坤"]:
        c = idx[qk]
        print(f"  {c['que']:>4}({c['que_vi']:<8}) {c['que_kep']:>6} {c['thoi_gian']:>6} {c['thien_the']:>6} = {c['so']:,}")
