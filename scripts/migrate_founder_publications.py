"""Migrate existing Founder_* files in data/published/ → user_publications/u1/self/

Mapping:
- Founder_PheMenhSau_V4_Q4Enriched.{docx,md}  → phe_menh_sau
- Founder_CDK_12Cung_VietThuan.{docx,md}       → cdk_12_cung
- Founder_CDK_DaiHan_8Vong.{docx,md}           → cdk_dai_han
- Founder_CDK_LuuNien_10nam.{docx,md}          → cdk_luu_nien
- Founder_CDK_TongDoanCuocDoi.{docx,md}        → cdk_tong_doan
- Founder_BoTongDoanMenh_2026.{pdf,html,md}    → master
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.publications import pub_dir, register_publication, PROJECT_ROOT

USER_ID = 1
PERSON_KEY = "self"
SRC = PROJECT_ROOT / "data/published"

MIGRATIONS = [
    {
        "src_prefix": "Founder_PheMenhSau_V4_Q4Enriched",
        "pub_type": "phe_menh_sau",
        "exts": ["docx", "md"],
        "chars": 44000, "cost": 0.05, "provider": "deepseek", "model": "v4_pro", "version": "v4_q4_enriched",
    },
    {
        "src_prefix": "Founder_CDK_12Cung_VietThuan",
        "pub_type": "cdk_12_cung",
        "exts": ["docx", "md"],
        "chars": 19000, "cost": 0.03, "provider": "deepseek", "model": "v4_pro_bulk", "version": "viet_thuan",
    },
    {
        "src_prefix": "Founder_CDK_DaiHan_8Vong",
        "pub_type": "cdk_dai_han",
        "exts": ["docx", "md"],
        "chars": 11400, "cost": 0.02, "provider": "deepseek", "model": "v4_pro_dai_han", "version": "8_vong",
    },
    {
        "src_prefix": "Founder_CDK_LuuNien_10nam",
        "pub_type": "cdk_luu_nien",
        "exts": ["docx", "md"],
        "chars": 17000, "cost": 0.02, "provider": "deepseek", "model": "v4_pro_luu_nien", "version": "10_nam",
    },
    {
        "src_prefix": "Founder_CDK_TongDoanCuocDoi",
        "pub_type": "cdk_tong_doan",
        "exts": ["docx", "md"],
        "chars": 7900, "cost": 0.01, "provider": "deepseek", "model": "v4_pro_synthesis", "version": "co_bien",
    },
    {
        "src_prefix": "Founder_BoTongDoanMenh_2026",
        "pub_type": "master",
        "exts": ["pdf", "html", "md"],
        "chars": 126000, "cost": 0, "provider": "(local)", "model": "pandoc+weasyprint", "version": "v1_2026",
    },
]


def main():
    print(f"🚚 Migrating Founder files → user_publications/u{USER_ID}/{PERSON_KEY}/")
    print()
    for m in MIGRATIONS:
        prefix = m["src_prefix"]
        pub_type = m["pub_type"]
        d = pub_dir(USER_ID, PERSON_KEY, pub_type)
        d.mkdir(parents=True, exist_ok=True)
        files_relpath = {}
        for ext in m["exts"]:
            src = SRC / f"{prefix}.{ext}"
            if not src.exists():
                print(f"  ⚠ Missing: {src.name}")
                continue
            dst_name = f"output.{ext}"
            dst = d / dst_name
            if not dst.exists():
                shutil.copy2(src, dst)
            files_relpath[ext] = dst_name
        if not files_relpath:
            print(f"  ⏭ Skip {pub_type} — no files")
            continue
        result = register_publication(
            user_id=USER_ID,
            person_key=PERSON_KEY,
            pub_type=pub_type,
            files_relpath=files_relpath,
            total_chars=m["chars"],
            cost_usd=m["cost"],
            provider=m["provider"],
            model=m["model"],
            version=m["version"],
            notes="Migrated from data/published/ (legacy Founder_*)",
        )
        print(f"  ✅ {pub_type}: {result.get('action')} (id={result.get('id')}) · formats: {list(files_relpath.keys())}")
    print()
    print("✓ Done")


if __name__ == "__main__":
    main()
