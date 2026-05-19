# YI-CHRONOS MVP

MVP mô hình hóa trạng thái thời gian, xây từ `deep-research-report.md`.

## Chạy backend cục bộ

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Chạy frontend cục bộ

```bash
npm install --prefix client/webapp
```

## Chạy 1 lệnh (chuẩn cố định)

```bash
./scripts/dev-up.sh
```

- Backend cố định: `http://127.0.0.1:8000`
- Frontend cố định: `http://127.0.0.1:5173`
- Script tự nối `VITE_API_BASE` đúng backend.
- Dừng toàn bộ stack bằng `Ctrl+C`.

## Kiểm tra

```bash
source .venv/bin/activate
python -m pytest tests -q
python scripts/safety_scan.py
cd client/webapp && npm run build
```

## Phạm vi MVP

Ứng dụng triển khai Trạng thái vũ trụ, Cộng hưởng cá nhân và Phản hồi. GuppyLM được hoãn có chủ đích cho tới khi có dữ liệu phản hồi có cấu trúc.

## Chuẩn lá số đã chốt

- Phái triển khai hiện tại: `Bắc phái`
- Ruleset đang dùng trong API/report: `bac_phai_v1`
- Đặc tả ruleset: `docs/rulesets/bac_phai_v1.md`

## Tri thức 64 quẻ (nguồn)

- Nguồn chính: `thư viện sách/Kinh Dịch Trọn Bộ - Ngô Tất Tố - khoahoctamlinh.vn.pdf`
- Nguồn bổ sung luận giải ngắn: `thư viện sách/Tam Thiên Dịch Số.pdf`
- Seed dữ liệu:
  - `data/seeds/hexagram_texts_ngotatto.json`
  - `data/seeds/hexagram_insights_tam_thien.json`

## Huong dan doc thu vien

- Xem `HUONG_DAN_DOC_VA_SU_DUNG_THU_VIEN.md` de doc dung thu tu va bien tri thuc sach thanh rule co the dua vao code/test.
