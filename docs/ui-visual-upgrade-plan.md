# YI-CHRONOS UI Visual Upgrade Plan

## Muc tieu

Lam giao dien dep hon, sinh dong hon, nhung van giu tinh chat san pham cong cu: du lieu ro, thao tac nhanh, khong bien thanh landing page.

## Thu tu nang cap

1. Sua responsive mobile cho app shell, topbar, clock chips va main tabs.
   - Trang thai: dang lam.
   - Ly do: mobile hien bi tran ngang va cat noi dung o topbar/tabs.

2. Dong bo icon dieu huong, thay emoji roi rac bang mot he icon nhat quan.
   - Trang thai: dang lam.
   - Ly do: emoji lam UI kem dong bo, kho tao visual identity rieng cho tung truong phai.

3. Them visual header cho tung tab.
   - Trang thai: cho lam.
   - Huong lam: moi tab co mot anh minh hoa nho/texture rieng dat trong `TabIntro`, khong lam che noi dung chinh.

4. Nang cap bo anh 64 que.
   - Trang thai: cho lam.
   - Huong lam: giu SVG que hien tai lam glyph, them artwork/card theo tung que, ngu hanh, trang thai dong/tinh.

5. Tao asset pipeline cho anh ve.
   - Trang thai: cho lam.
   - Huong lam: luu anh o `client/webapp/public/illustrations`, map bang JSON metadata thay vi hardcode trong component.

6. Sinh anh bang external model API theo batch.
   - Trang thai: cho lam.
   - Luu y: API keys chi de trong `.env.local`, khong commit secrets.

## Kiem tra bat buoc sau moi dot

- `cd client/webapp && npm run build`
- Render desktop va mobile bang Playwright.
- Kiem tra console khong co loi app nghiem trong.
- Chup lai screenshot truoc/sau neu thay doi giao dien dang ke.
