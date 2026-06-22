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


def test_report_runs_end_to_end():
    # Báo cáo tổng phải chạy trọn, trả đủ 3 mảng định lý
    rep = dsv.full_report()
    assert set(rep) >= {"tam_hop", "brightness", "conservation"}
