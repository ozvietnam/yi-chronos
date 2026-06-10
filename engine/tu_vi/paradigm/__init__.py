"""Paradigm engine — 6 paradigm functions wired từ 4 hệ phái Tử Vi.

Sources:
- Trần Đoàn (Toàn Thư - Vũ Tài Lục): Nhân Cung, Bát Pháp, Thập Dụ
- Thiên Lương (Nghiệm Lý Toàn Thư): 5 Bậc Tuổi Can-Chi, 3 Vòng Lớn, Tam Hợp Lộc
- Trung Châu (Vương Đình Chỉ Q2): paradigm cốt, cách cục
- Nguyễn Phát Lộc (Hàm Số): khoa học nhân văn, phương pháp hàm số

Built 2026-06-10 Phase A1.
"""
from .nhan_cung import is_nhan_cung, NHAN_CUNG
from .bac_tuoi import bac_tuoi, BAC_TUOI_NAMES
from .ba_vong import ba_vong_lon, vong_loc_ton, vong_thai_tue, vong_trang_sinh
from .bat_phap import bat_phap_classify, BAT_PHAP_CACH
from .thap_du import thap_du_eval, THAP_DU_NAMES
from .tam_hop_loc import tam_hop_loc_ton, LOC_TON_TAM_HOP_BY_CAN
from .to_hop_cung import tam_phuong_tu_chinh, giap_cung, muon_sao, to_hop_cung

__all__ = [
    "is_nhan_cung", "NHAN_CUNG",
    "tam_phuong_tu_chinh", "giap_cung", "muon_sao", "to_hop_cung",
    "bac_tuoi", "BAC_TUOI_NAMES",
    "ba_vong_lon", "vong_loc_ton", "vong_thai_tue", "vong_trang_sinh",
    "bat_phap_classify", "BAT_PHAP_CACH",
    "thap_du_eval", "THAP_DU_NAMES",
    "tam_hop_loc_ton", "LOC_TON_TAM_HOP_BY_CAN",
]
