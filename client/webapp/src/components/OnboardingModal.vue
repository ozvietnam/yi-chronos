<script setup>
/**
 * OnboardingModal — hiển thị 1 lần sau khi user đăng ký / hoặc login lần đầu chưa setup.
 *
 * Yêu cầu nhập: tên hiển thị, giới tính, ngày-giờ sinh, nơi sinh (tuỳ chọn).
 * Lưu vào user_persons (person_key='self'). Lần sau login không phải nhập lại.
 */
import { ref, computed } from "vue";
import {
  currentUser, currentPerson, needsProfileSetup, setupProfile, isAuthenticated,
} from "../stores/authStore.js";
import { fetchAvailablePersons } from "../stores/tuviPersonStore.js";

const visible = computed(() => isAuthenticated.value && needsProfileSetup.value);

const form = ref({
  name: "",
  gender: "nam",
  birth_date: "", // YYYY-MM-DD
  birth_time: "12:00",
  birth_place: "",
  timezone: "Asia/Ho_Chi_Minh",
});
const busy = ref(false);
const error = ref("");

// Pre-fill name from user.display_name once
function prefillName() {
  if (!form.value.name && currentUser.value?.display_name) {
    form.value.name = currentUser.value.display_name;
  }
}

async function submit() {
  error.value = "";
  if (!form.value.birth_date) {
    error.value = "Vui lòng nhập ngày sinh dương lịch";
    return;
  }
  if (!form.value.gender) {
    error.value = "Vui lòng chọn giới tính";
    return;
  }
  busy.value = true;
  try {
    const birth_datetime_local = `${form.value.birth_date}T${form.value.birth_time || "12:00"}:00`;
    await setupProfile({
      name: form.value.name || currentUser.value?.display_name,
      gender: form.value.gender,
      birth_datetime_local,
      timezone: form.value.timezone,
      birth_place: form.value.birth_place || null,
    });
    // Refresh available persons so dropdown tử vi update ngay
    await fetchAvailablePersons();
  } catch (e) {
    error.value = e.message || "Không lưu được hồ sơ";
  } finally {
    busy.value = false;
  }
}

function skip() {
  // Tạm thời ẩn modal — nhưng flag vẫn true ở backend; lần load /me sau vẫn show lại
  needsProfileSetup.value = false;
}

// Trigger prefill khi visible thay đổi
import { watch } from "vue";
watch(visible, (v) => { if (v) prefillName(); }, { immediate: true });
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="ob-backdrop">
      <div class="ob-modal">
        <header>
          <h2>✨ Chào mừng đến với YI-CHRONOS</h2>
          <p>
            Để xem lá số Tử Vi / Bát Tự / Mai Hoa của riêng bạn, hệ thống cần thông tin
            <b>ngày-giờ sinh dương lịch</b>. Bạn chỉ phải nhập <b>1 lần duy nhất</b> — các
            lần đăng nhập sau sẽ tự động dùng.
          </p>
        </header>

        <form @submit.prevent="submit" class="ob-form">
          <label>
            <span>Tên hiển thị</span>
            <input v-model="form.name" type="text" placeholder="Vd: Nguyễn Văn A" />
          </label>

          <label>
            <span>Giới tính</span>
            <select v-model="form.gender">
              <option value="nam">Nam</option>
              <option value="nữ">Nữ</option>
            </select>
          </label>

          <div class="ob-row">
            <label>
              <span>Ngày sinh dương lịch</span>
              <input v-model="form.birth_date" type="date" required />
            </label>
            <label>
              <span>Giờ sinh (giờ:phút)</span>
              <input v-model="form.birth_time" type="time" required />
            </label>
          </div>

          <label>
            <span>Nơi sinh (tuỳ chọn)</span>
            <input v-model="form.birth_place" type="text" placeholder="Vd: TP. Hồ Chí Minh" />
          </label>

          <label>
            <span>Múi giờ</span>
            <select v-model="form.timezone">
              <option value="Asia/Ho_Chi_Minh">Việt Nam (GMT+7)</option>
              <option value="Asia/Bangkok">Bangkok (GMT+7)</option>
              <option value="Asia/Hong_Kong">Hong Kong (GMT+8)</option>
              <option value="Asia/Tokyo">Tokyo (GMT+9)</option>
              <option value="UTC">UTC</option>
            </select>
          </label>

          <p v-if="error" class="ob-error">{{ error }}</p>

          <div class="ob-actions">
            <button type="button" class="ob-skip" @click="skip">Để sau</button>
            <button type="submit" class="ob-submit" :disabled="busy">
              {{ busy ? "⏳ Đang lưu..." : "💾 Lưu & bắt đầu" }}
            </button>
          </div>
        </form>

        <p class="ob-hint">
          🔒 Thông tin này lưu riêng cho bạn. Không hiển thị với user khác.
          Có thể chỉnh sửa sau trong tab <b>👨‍👩 Người thân</b> → mục <em>self</em>.
        </p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.ob-backdrop {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.82);
  backdrop-filter: blur(6px);
  z-index: 3000;
  display: flex; justify-content: center; align-items: center;
  padding: 1rem;
}
.ob-modal {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border: 1px solid #f59e0b;
  border-radius: 10px;
  padding: 1.5rem 1.8rem;
  max-width: 520px; width: 100%;
  color: #f1f5f9;
  box-shadow: 0 30px 90px rgba(245, 158, 11, 0.2), 0 30px 90px rgba(0,0,0,0.8);
  max-height: 92vh; overflow-y: auto;
}
.ob-modal header h2 {
  margin: 0 0 0.5rem; color: #fde68a; font-size: 1.3rem;
}
.ob-modal header p {
  margin: 0 0 1rem; font-size: 0.88rem; color: #cbd5e1; line-height: 1.5;
}
.ob-form { display: flex; flex-direction: column; gap: 0.7rem; }
.ob-form label {
  display: flex; flex-direction: column; gap: 0.25rem;
  font-size: 0.85rem; color: #cbd5e1;
}
.ob-form label > span {
  font-weight: 600; color: #fde68a; font-size: 0.82rem;
}
.ob-form input, .ob-form select {
  background: #0f172a; border: 1px solid #334155;
  border-radius: 4px; padding: 0.5rem 0.65rem;
  color: #f1f5f9; font-size: 0.92rem;
}
.ob-form input:focus, .ob-form select:focus {
  outline: none; border-color: #f59e0b;
}
.ob-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem;
}

.ob-error {
  color: #fca5a5; background: rgba(239,68,68,0.1);
  padding: 0.45rem 0.6rem; border-radius: 4px;
  margin: 0; font-size: 0.85rem;
}
.ob-actions {
  display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 0.5rem;
}
.ob-skip {
  background: transparent; border: 1px solid #475569; color: #94a3b8;
  padding: 0.5rem 0.9rem; border-radius: 4px; cursor: pointer; font-size: 0.88rem;
}
.ob-skip:hover { color: #cbd5e1; border-color: #64748b; }
.ob-submit {
  background: linear-gradient(135deg, #d97706, #f59e0b); border: none;
  color: white; padding: 0.5rem 1.1rem; border-radius: 4px;
  cursor: pointer; font-size: 0.9rem; font-weight: 600;
}
.ob-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #b45309, #d97706);
}
.ob-submit:disabled { opacity: 0.6; cursor: not-allowed; }

.ob-hint {
  margin: 1rem 0 0; padding-top: 0.7rem; border-top: 1px dashed #334155;
  font-size: 0.78rem; color: #94a3b8; line-height: 1.5;
}

@media (max-width: 600px) {
  .ob-row { grid-template-columns: 1fr; }
}
</style>
