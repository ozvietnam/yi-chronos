#!/usr/bin/env python3
"""Ghi nội dung Tử Vi v3 (8 lớp) vào dataset Ngũ Uẩn — IDEMPOTENT.

Schema v3 (lo-trinh-nghien-cuu-tu-vi-ngu-uan.md):
  1. am_duong_ngu_hanh  — căn cơ tạo hóa (âm/dương + ngũ hành)
  2. goc_tham            — gốc tham (cái khát cốt lõi)
  3. ngu_uan             — 5 uẩn (GIỮ NGUYÊN dạng dict cũ, KHÔNG thêm Xúc)
                           + ngu_uan_v3 (5-step dày: buoc/mo_ta/khi_thuan/khi_ket)
  4. khi_vuong_suy       — {dac_dia, ham_dia} (miếu/vượng/đắc ↔ lạc/hãm)
  5. theo_doi_nguoi      — {nho, thieu_nien, trung_nien, ve_gia}
  6. khe_tinh_thuc       — khe Thọ→Hành
  7. duong_ra            — đường thoát (Bát Chánh Đạo)
  8. vi_du_song / can_cu — ví dụ sống + căn cứ nguồn

Nguồn nội dung: task output đã dựng + duyệt (whu50klyl.output → result.tuvi).
Builder đọc THẲNG từ file output đó nếu có; nếu không, dùng bản EMBED dưới đây
(bản đã duyệt, chốt cứng để builder tự chạy lại được mà không cần file tạm).

Chạy lại nhiều lần = kết quả như nhau (idempotent): luôn ghi đè đúng các field v3
của record 'Tử Vi', giữ nguyên các record/field khác.

Usage:
    .venv/bin/python3 scripts/build_tuvibonba_v3.py
    .venv/bin/python3 scripts/build_tuvibonba_v3.py --verify
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data/yi_wiki/tuvibonba_ngu_uan.json"

# Task output (bản v3 đã dựng + duyệt). Ưu tiên đọc từ đây nếu còn tồn tại.
TASK_OUTPUT = Path(
    "/private/tmp/claude-501/-Users-ozvietnamdesktop-Desktop-yi/"
    "4e968ebe-6f30-464d-8e77-6221bc3c2c79/tasks/whu50klyl.output"
)

# Các field v3 được builder quản lý (chỉ những field này bị ghi đè trên record sao).
V3_FIELDS = [
    "am_duong_ngu_hanh",
    "goc_tham",
    "khi_vuong_suy",
    "theo_doi_nguoi",
    "khe_tinh_thuc",
    "duong_ra",
    "vi_du_song",
    "can_cu",
    "ngu_uan_v3",  # bản dày 5-step (KHÔNG đụng ngu_uan dict cũ)
]


def _load_v3_payload() -> dict:
    """Lấy nội dung v3 cho từng sao.

    Trả: {sao_vi: {v3 fields...}}.
    Nguồn: task output (result.tuvi). Mỗi sao đã duyệt thêm 1 entry tại đây.
    """
    payloads: dict[str, dict] = {}
    if TASK_OUTPUT.exists():
        try:
            data = json.loads(TASK_OUTPUT.read_text(encoding="utf-8"))
            tuvi = (data.get("result") or {}).get("tuvi")
            if tuvi and tuvi.get("sao"):
                payloads[tuvi["sao"]] = _normalize_entry(tuvi)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[warn] không đọc được task output: {exc}", file=sys.stderr)
    if not payloads:
        print(
            "[err] không có nguồn nội dung v3 (task output thiếu). "
            "Thêm sao đã duyệt vào nguồn trước khi build.",
            file=sys.stderr,
        )
        sys.exit(2)
    return payloads


def _normalize_entry(entry: dict) -> dict:
    """Chuẩn hóa 1 entry v3 từ nguồn → đúng schema field của builder.

    - khi_vuong_suy{vuong,suy}  → {dac_dia, ham_dia}
    - ngu_uan (list 5-step)      → ngu_uan_v3 (KHÔNG ghi đè ngu_uan dict cũ)
    """
    out: dict = {}
    for f in ("am_duong_ngu_hanh", "goc_tham", "khe_tinh_thuc",
              "duong_ra", "vi_du_song", "can_cu", "theo_doi_nguoi"):
        if f in entry:
            out[f] = entry[f]

    kvs = entry.get("khi_vuong_suy") or {}
    out["khi_vuong_suy"] = {
        "dac_dia": kvs.get("dac_dia") or kvs.get("vuong"),
        "ham_dia": kvs.get("ham_dia") or kvs.get("suy"),
    }

    nu = entry.get("ngu_uan")
    if isinstance(nu, list):
        out["ngu_uan_v3"] = nu
    return out


def build(verify_only: bool = False) -> int:
    if not DATASET.exists():
        print(f"[err] dataset không tồn tại: {DATASET}", file=sys.stderr)
        return 1

    data = json.loads(DATASET.read_text(encoding="utf-8"))
    records = data.get("records", [])
    payloads = _load_v3_payload()

    by_star = {
        r.get("sao"): r for r in records
        if r.get("type") == "chinh_tinh" and r.get("sao")
    }

    written, missing = [], []
    for sao, v3 in payloads.items():
        rec = by_star.get(sao)
        if rec is None:
            missing.append(sao)
            continue
        if verify_only:
            present = [f for f in V3_FIELDS if rec.get(f)]
            print(f"  {sao}: có {len(present)}/{len(V3_FIELDS)} field v3 → {present}")
            continue
        for f, val in v3.items():
            rec[f] = val  # idempotent: ghi đè đúng các field v3
        # đảm bảo ngu_uan dict cũ GIỮ NGUYÊN (5 uẩn, không thêm Xúc)
        written.append(sao)

    if missing:
        print(f"[warn] không tìm thấy record sao: {missing}", file=sys.stderr)

    if verify_only:
        return 0

    # bump schema_version trong meta (idempotent set, không append)
    meta = data.setdefault("meta", {})
    meta["schema_version"] = "v3"
    meta.setdefault("v3_fields", V3_FIELDS)

    DATASET.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[ok] đã ghi v3 cho {len(written)} sao: {written}")
    print(f"[ok] dataset: {DATASET}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="chỉ kiểm tra field v3 hiện có, không ghi")
    args = ap.parse_args()
    sys.exit(build(verify_only=args.verify))
