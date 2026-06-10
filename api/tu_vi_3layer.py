"""API endpoint render 3-Layer cho lá số bất kỳ.

POST /api/tu-vi/3-layer
Body: {
  "can": "mau", "chi": "thin",
  "menh_palace": "ty", "than_palace": "than",
  "cuc": "thuy_nhi_cuc", "gender": "M",
  "chinh_tinh_per_palace": {"ty": ["thien_dong"], ...}
}

Returns: {
  "lop_1_chuyen_ve_anh": str,
  "lop_2_vi_sao": str,
  "lop_3_sach_co": dict,
  "warnings": list,
  "metadata": dict
}

Built 2026-06-10 Phase C.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from engine.atomization.output_filler_v2 import render_3_layer

router = APIRouter(prefix="/api/tu-vi", tags=["tu-vi-3layer"])


class LaSoInput(BaseModel):
    can: str = Field(..., description="Can năm sinh canonical lowercase (vd: mau, giap)")
    chi: str = Field(..., description="Chi năm sinh canonical (vd: thin, ngo)")
    menh_palace: str = Field(..., description="Cung Mệnh (chi canonical, vd: ty)")
    than_palace: str = Field(..., description="Cung Thân (chi canonical)")
    cuc: str = Field("thuy_nhi_cuc", description="Cục Mệnh canonical")
    gender: str = Field("M", description="M or F")
    chinh_tinh_per_palace: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map cung chi → list chính tinh canonical (snake_case)"
    )


@router.post("/3-layer")
async def render_3_layer_api(la_so: LaSoInput) -> dict:
    """Render 3-Layer output cho 1 lá số bất kỳ."""
    return render_3_layer(la_so.dict())


@router.get("/3-layer/founder-demo")
async def founder_demo() -> dict:
    """Demo lá số founder Mậu Thìn (1988-06-05 23:30 Nam)."""
    la_so = {
        "can": "mau",
        "chi": "thin",
        "menh_palace": "ty",
        "than_palace": "than",
        "cuc": "thuy_nhi_cuc",
        "gender": "M",
        "chinh_tinh_per_palace": {
            "ty": ["thien_dong"],
            "than": ["vu_khuc"],
            "thin": ["tu_vi"],
            "hoi": ["thien_co"],
            "dau": ["thai_am"],
            "mao": ["thai_duong"],
            "ngo": ["lien_trinh"],
            "tuat": ["that_sat"],
            "dan": ["thien_phu"],
            "mui": ["thien_luong"],
            "suu": ["thien_tuong"],
            "ti": ["pha_quan"],
        }
    }
    return render_3_layer(la_so)
