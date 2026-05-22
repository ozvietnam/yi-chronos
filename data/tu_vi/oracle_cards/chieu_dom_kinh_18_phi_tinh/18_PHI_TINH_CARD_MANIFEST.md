# 18 Phi Tinh Card Manifest

Ngày lập: 2026-05-22

Mục tiêu: quản lý 18 thẻ ảnh của hệ **Chiếu Đởm Kinh / 18 Phi Tinh** theo đúng thứ tự, đúng tên, đúng trường phái.

Trạng thái:

- `planned`: đã có brief, chưa vẽ.
- `prompted`: đã có prompt đặt vẽ.
- `generated`: đã có ảnh gốc.
- `web_ready`: đã có ảnh tối ưu cho website.
- `mounted`: đã gắn vào UI.

## Quy ước ID

`cdk_phi_XX_slug`

`XX` giữ thứ tự cố định theo schema 9 Dương tinh trước, 9 Âm tinh sau.

## Danh sách thẻ

| ID | Tên Việt | Hán tự | Nhóm | Ngũ hành | Hỷ cung | File gốc đề xuất | Trạng thái |
|---|---|---|---|---|---|---|---|
| cdk_phi_01_tu | Tử | 紫 | dương | mộc | Thân, Tý, Tỵ, Dậu, Hợi | `generated_cards/cdk_phi_01_tu__zi__duong_moc.png` | web_ready |
| cdk_phi_02_van | Văn | 文 | dương | mộc | Dần, Ngọ, Tuất | `generated_cards/cdk_phi_02_van__wen__duong_moc.png` | web_ready |
| cdk_phi_03_phuc | Phúc | 福 | dương | thổ | Dần, Mão, Tỵ, Ngọ | `generated_cards/cdk_phi_03_phuc__fu__duong_tho.png` | web_ready |
| cdk_phi_04_loc | Lộc | 禄 | dương | mộc | Dần, Mão, Tỵ, Ngọ | `generated_cards/cdk_phi_04_loc__lu__duong_moc.png` | web_ready |
| cdk_phi_05_an | Ấn | 印 | dương | thổ | Tý, Mão, Thìn | `generated_cards/cdk_phi_05_an__yin__duong_tho.png` | web_ready |
| cdk_phi_06_tho | Thọ | 寿 | dương | thổ | Hợi, Dậu, Dần | `generated_cards/cdk_phi_06_tho__shou__duong_tho.png` | web_ready |
| cdk_phi_07_truong | Trượng | 杖 | dương | mộc | Tý, Thân, Hợi | `generated_cards/cdk_phi_07_truong__zhang__duong_moc.png` | web_ready |
| cdk_phi_08_kho | Khố | 库 | dương | thổ | Mão, Tỵ, Ngọ, Mùi, Hợi | `generated_cards/cdk_phi_08_kho__ku__duong_tho.png` | web_ready |
| cdk_phi_09_dieu | Diêu | 姚 | dương | thổ | Mão, Thìn, Tuất, Hợi | `generated_cards/cdk_phi_09_dieu__yao__duong_tho.png` | web_ready |
| cdk_phi_10_quy | Quý | 贵 | âm | thổ | Dần, Thìn, Hợi, Mão, Mùi | `generated_cards/cdk_phi_10_quy__gui__am_tho.png` | web_ready |
| cdk_phi_11_hong | Hồng | 红 | âm | kim | Thìn, Sửu, Dần, Mão, Hợi | `generated_cards/cdk_phi_11_hong__hong__am_kim.png` | web_ready |
| cdk_phi_12_di | Dị | 异 | âm | thổ | Sửu, Dần, Thìn, Mùi | `generated_cards/cdk_phi_12_di__yi__am_tho.png` | web_ready |
| cdk_phi_13_mao | Mao | 毛 | âm | thủy | Tý, Mão, Mùi, Dần, Tuất | `generated_cards/cdk_phi_13_mao__mao__am_thuy.png` | web_ready |
| cdk_phi_14_hu | Hư | 虚 | âm | thủy | Ngọ, Mùi, Dậu, Hợi | `generated_cards/cdk_phi_14_hu__xu__am_thuy.png` | web_ready |
| cdk_phi_15_quan | Quán | 贯 | âm | thổ | Mão, Tỵ, Ngọ, Mùi, Hợi | `generated_cards/cdk_phi_15_quan__guan__am_tho.png` | web_ready |
| cdk_phi_16_hinh | Hình | 刑 | âm | hỏa | Dần, Dậu, Ngọ, Tuất | `generated_cards/cdk_phi_16_hinh__xing__am_hoa.png` | web_ready |
| cdk_phi_17_nhan | Nhận | 刃 | âm | kim | Thân, Tỵ, Ngọ, Dần | `generated_cards/cdk_phi_17_nhan__ren__am_kim.png` | web_ready |
| cdk_phi_18_khoc | Khốc | 哭 | âm | kim | Sửu, Thân, Mão, Ngọ | `generated_cards/cdk_phi_18_khoc__ku__am_kim.png` | web_ready |

## Nhóm ưu tiên đặt vẽ

Ưu tiên 1:

1. `cdk_phi_14_hu`
2. `cdk_phi_18_khoc`
3. `cdk_phi_17_nhan`
4. `cdk_phi_16_hinh`
5. `cdk_phi_01_tu`
6. `cdk_phi_02_van`

Ưu tiên 2:

7. `cdk_phi_10_quy`
8. `cdk_phi_05_an`
9. `cdk_phi_04_loc`
10. `cdk_phi_03_phuc`
11. `cdk_phi_07_truong`
12. `cdk_phi_12_di`

Ưu tiên 3:

13. `cdk_phi_06_tho`
14. `cdk_phi_08_kho`
15. `cdk_phi_15_quan`
16. `cdk_phi_11_hong`
17. `cdk_phi_09_dieu`
18. `cdk_phi_13_mao`
