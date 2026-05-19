# Lien Hoa Don Phap - Ingest Guide (Targeted)

Muc tieu:
- Tieu hoa tri thuc Lien Hoa Don Phap thanh rule co the code.
- Khong doc ca site; chi doc cac bai buoc/chuong trong index.

## Tep da tao

- `data/seeds/lien_hoa_source_index.json`
- `data/seeds/lien_hoa_rules_v1.json`
- `data/seeds/lien_hoa_reading_queue.json`
- `core/lien_hoa_data.py`

## Nguon ingest dot 1 (Vugioi)

- Muc luc:
  - `https://vugioi.com/muc-luc-lien-hoa-don-phap/`
- Buoc 1:
  - `https://vugioi.com/buoc-1-du-lieu-tam-y-trong-lien-hoa-don-phap/`
- Buoc 2:
  - `https://vugioi.com/buoc-2-thiet-lap-chanh-ho-bien-quai-trong-lien-hoa-don-phap/`
- Buoc 3:
  - `https://vugioi.com/buoc-3-khong-thoi-su-trong-lien-hoa-don-phap/`
- Buoc 4:
  - `https://vugioi.com/buoc-4-dat-luc-than-vao-khong-thoi/`
- Buoc 5:
  - `https://vugioi.com/buoc-5-don-phap-trong-lien-hoa-don-phap/`

## Quy trinh hang ngay

1. Chon `day_id` trong `lien_hoa_reading_queue.json`.
2. Doc dung `source_id` va pham vi bai duoc gan.
3. Trich rule theo schema:
   - `rule_id`
   - `input_contract`
   - `logic_summary`
   - `output_contract`
   - `confidence`
   - `source_refs`
4. Nang `status` tu `draft` len `active` chi khi co test.

## Muc tieu ky thuat tiep theo

- Tao `engine/lien_hoa.py` (stepwise):
  - input P/T
  - chanh/ho/bien
  - ta/su
  - khong thoi
  - luc than
  - dun 4-6-4 cycle
- Gan vao action layer cho khuyen nghi:
  - tien/lui/don/hoa giai
