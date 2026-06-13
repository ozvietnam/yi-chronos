/**
 * Composable: bind a panel's `inputBirth` ref to the ACTIVE PERSON's birth,
 * và (tùy chọn) tự CHẠY KẾT QUẢ luôn khi đã có ngày sinh.
 *
 * Anh chốt 2026-06-13: "nhập ngày giờ sinh 1 lần → các giao diện khác khỏi nhập
 * lại, chỗ nào chạy ra kết quả thì chạy luôn. Muốn xem người khác → chuyển profile."
 *
 * Hành vi:
 *   - Mở panel (mount): nếu active person có birth → điền sẵn + gọi `onReady` (auto-compute).
 *   - ĐỔI PROFILE (person_key đổi): GHI ĐÈ birth của người mới + gọi `onReady` (chạy lại).
 *     → đây là cách "xem cho người khác": vào chuyển profile, mọi panel tự cập nhật.
 *   - Sửa profile (đổi birth cùng người): đồng bộ lại.
 *   - Guest gõ tay: KHÔNG auto-run (tránh chạy giữa chừng khi đang gõ) — vẫn bấm nút.
 *
 * Source: userDataStore.activePerson (API user_persons khi login / localStorage khi guest).
 */
import { onMounted, watch } from "vue";

import { activePerson } from "./userDataStore.js";

export function useActivePersonBirth(birthRef, opts = {}) {
  const { onLatLon, onReady } = opts;
  let lastSynced = null; // birth value gần nhất ta tự điền — để phân biệt với edit tay

  function fire(val) {
    if (!onReady) return;
    try {
      Promise.resolve(onReady(val)).catch(() => {});
    } catch {
      /* panel tự xử lỗi của nó */
    }
  }

  function sync(force) {
    const val = activePerson.value?.birth_datetime_local;
    if (!val) return;
    // Đẩy giá trị khi: ô rỗng | force (đổi người) | chưa bị sửa tay kể từ lần đồng bộ trước.
    if (force || !birthRef.value || birthRef.value === lastSynced) {
      const changed = birthRef.value !== val;
      birthRef.value = val;
      lastSynced = val;
      if (changed || force) fire(val); // auto-compute khi birth vừa có / vừa đổi người
    }
  }

  onMounted(() => sync(false));
  // Đổi PROFILE (sang người khác) → ghi đè + chạy lại, kể cả khi ô đang có giá trị cũ.
  watch(() => activePerson.value?.person_key, () => sync(true));
  // Đổi birth của CÙNG người (sửa profile) → đồng bộ.
  watch(() => activePerson.value?.birth_datetime_local, () => sync(false));

  // Tùy chọn: panel phương Tây cần lat/lon.
  if (onLatLon) {
    onMounted(() => {
      const loc = activePerson.value?.birth_location;
      if (loc) onLatLon(loc);
    });
    watch(() => activePerson.value?.person_key, () => {
      const loc = activePerson.value?.birth_location;
      if (loc) onLatLon(loc);
    });
  }
}
