"""Kiểm chứng bằng máy các ĐỊNH LÝ DẪN XUẤT của Đằng Sơn (kế thừa, tiếp tục công trình).

Mỗi test mã hóa một mệnh đề Đằng Sơn nêu BẰNG TAY trong 《Tử Vi Hoàn Toàn Khoa Học》 Q1,
rồi để engine kiểm trên dữ liệu canonical (chinh_tinh.json + mieu_vuong_ham.json).
Khoa học thật: luật phải TÁI TẠO được dữ liệu — chỗ nào khép kín, chỗ nào hở, nói thật.
"""
from engine.tu_vi import dang_son_verify as dsv


def test_ngu_hanh_sinh_chain_recognized():
    # hỏa→thổ→kim là chuỗi sinh hợp lệ; hỏa→kim (hỏa KHẮC kim) thì không
    assert dsv.is_sinh_chain(["hỏa", "thổ", "kim"]) is True
    assert dsv.is_sinh_chain(["hỏa", "kim", "thổ"]) is False


def test_tam_hop_tu_vu_liem_is_sinh_chain():
    # Đằng Sơn tr.200: "Bộ tam hợp Liêm Tử Vũ theo thứ tự ngũ hành sinh (hỏa-thổ-kim)"
    g = dsv.verify_tam_hop()["Tử-Vũ-Liêm"]
    assert g["is_sinh_chain"] is True
    assert g["sinh_order_hanh"] == ["hỏa", "thổ", "kim"]


def test_tam_hop_sat_pha_tham_is_sinh_chain():
    # Đằng Sơn tr.200: "Sát Phá Tham cũng theo ngũ hành sinh (kim-thủy-mộc)"
    g = dsv.verify_tam_hop()["Sát-Phá-Tham"]
    assert g["is_sinh_chain"] is True
    assert g["sinh_order_hanh"] == ["kim", "thủy", "mộc"]


def test_truong_sinh_hoa_tho_starts_dan():
    # Đằng Sơn tr.243 gom Hỏa-Thổ cùng vòng: Trường Sinh ở Dần → Đế Vượng ở Ngọ
    assert dsv.truong_sinh_stage("hỏa", "Dần") == "Trường Sinh"
    assert dsv.truong_sinh_stage("hỏa", "Ngọ") == "Đế Vượng"
    assert dsv.truong_sinh_stage("thổ", "Dần") == "Trường Sinh"


def test_brightness_truong_sinh_has_positive_signal():
    # Định lý tr.243: độ sáng (miếu-hãm) ~ giai đoạn Trường Sinh của hành sao tại cung.
    # Nếu định lý có thật, tương quan giữa "sức Trường Sinh" và "điểm độ sáng" phải DƯƠNG.
    r = dsv.verify_brightness()
    assert r["n_pairs"] > 100          # phủ đủ rộng (14 sao × 12 cung trừ đa-hành)
    assert -1.0 <= r["correlation"] <= 1.0
    assert r["correlation"] > 0        # có tín hiệu thuận, không phản


def test_brightness_relation_nourish_brighter_than_deplete():
    # Đằng Sơn Ch.8 (tr.80): cung SINH sao (dưỡng) ở thế lợi; sao SINH cung (bị tiết
    # khí) ở thế thiệt. → độ sáng TB nhóm "cung sinh sao" phải CAO HƠN "sao sinh cung".
    g = dsv.verify_brightness_relation()["group_means"]
    assert g["cung sinh sao"] > g["sao sinh cung"]
    # và mô hình quan-hệ (Ch.8) khá hơn Trường Sinh đơn (Vòng 1)
    r_rel = dsv.verify_brightness_relation()["correlation"]
    r_ts = dsv.verify_brightness()["correlation"]
    assert r_rel >= r_ts


def test_hoa_ky_duong_can_is_tu_vi_chum_minus_tu_vi():
    # Đằng Sơn tr.170: Hóa Kỵ 5 can DƯƠNG = chùm Tử Vi bỏ Tử Vi
    # ("bỏ Tử Vi ra ngoài thì được 5 sao hóa y hệt tài liệu hiện hành")
    r = dsv.verify_hoa_ky_structure()
    assert r["duong_match_tu_vi_chum_minus_tuvi"] is True
    assert set(r["duong_ky"]) == {"Thái Dương", "Liêm Trinh", "Thiên Cơ",
                                   "Thiên Đồng", "Vũ Khúc"}


def test_hoa_ky_am_can_pulls_in_xuong_khuc():
    # Đằng Sơn tr.172 "Âm Kỵ là lý do hiện hữu của Xương Khúc": Hóa Kỵ can ÂM kéo
    # Văn Xương + Văn Khúc (phụ tinh) vào → dấu vết định luật bảo toàn ③
    r = dsv.verify_hoa_ky_structure()
    assert "Văn Xương" in r["am_auxiliary_stars"]
    assert "Văn Khúc" in r["am_auxiliary_stars"]


def test_tu_hoa_aux_stars_internally_balanced():
    # V4: âm-dương Tứ Hóa KHÔNG cân theo truyền thống (③ không phải số học ngây thơ)
    # NHƯNG phụ tinh Xương/Khúc/Tả/Hữu tự cân → ③ đúng ở dạng CẤU TRÚC zero-sum.
    r = dsv.verify_tu_hoa_balance()
    assert r["naive_balanced"] is False        # tổng lệch (15 dương / 25 âm)
    assert r["aux_balanced"] is True           # phụ tinh tự cân 3/3


def test_loc_quyen_single_walk_reproduces_table():
    # Ch.14 (tr.163-165): toàn bộ Lộc+Quyền 10 can đọc từ MỘT đường đi 11 sao;
    # Quyền = Lộc kế tiếp (+1). 20 ô Tứ Hóa dẫn xuất từ 1 cấu trúc.
    r = dsv.verify_loc_quyen_walk()
    assert r["loc_match"] == 10      # 10/10 Lộc khớp TU_HOA_TABLE
    assert r["quyen_match"] == 10    # 10/10 Quyền khớp
    assert r["perfect"] is True


def test_star_hoa_participation_reveals_nature():
    # Ch.17: Phủ/Tướng/Sát hoàn toàn không hóa; Cơ/Nguyệt/Vũ hóa đủ 4/4; Tử/Lương không Kỵ.
    r = dsv.verify_star_hoa_participation()
    assert r["phu_tuong_sat_never_hoa"] is True
    assert r["co_nguyet_vu_full_hoa"] is True
    assert set(r["never_ky"]) == {"Tử Vi", "Thiên Lương"}


def test_report_runs_end_to_end():
    # Báo cáo tổng phải chạy trọn, trả đủ các mảng định lý
    rep = dsv.full_report()
    assert set(rep) >= {"tam_hop", "brightness", "brightness_relation", "hoa_ky_structure",
                        "loc_quyen_walk", "star_hoa_participation", "tu_hoa_balance", "conservation"}
