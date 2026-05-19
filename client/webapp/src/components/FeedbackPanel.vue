<script setup>
import { reactive, watch } from "vue";

const props = defineProps({
  prompt: {
    type: Object,
    default: null
  },
  disabled: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(["submit-feedback"]);
const form = reactive({
  response_enum: "unknown",
  confidence_enum: "unsure",
  tags: [],
  free_text_optional: ""
});

const tags = ["sức khỏe", "công việc", "tài chính", "gia đình", "quan hệ", "tinh thần"];
const responses = [
  ["matched", "Đúng"],
  ["partly", "Một phần"],
  ["false", "Sai"],
  ["unknown", "Không nhớ"]
];

function toggleTag(tag) {
  if (form.tags.includes(tag)) {
    form.tags = form.tags.filter((item) => item !== tag);
  } else {
    form.tags = [...form.tags, tag];
  }
}

function submit() {
  if (!props.prompt) return;
  emit("submit-feedback", {
    prompt_id: props.prompt.prompt_id,
    response_enum: form.response_enum,
    confidence_enum: form.confidence_enum,
    tags: form.tags,
    free_text_optional: form.free_text_optional
  });
}

watch(
  () => props.prompt?.prompt_id,
  () => {
    form.response_enum = "unknown";
    form.confidence_enum = "unsure";
    form.tags = [];
    form.free_text_optional = "";
  }
);
</script>

<template>
  <section class="panel feedback-panel">
    <div class="panel-title">
      <span>Phản hồi</span>
      <small>Dữ liệu cho trí tuệ</small>
    </div>
    <p class="prompt-text">
      {{ prompt?.prompt_text || "Nhập ngày giờ sinh để tạo mốc cần kiểm chứng." }}
    </p>

    <form class="feedback-form" :class="{ disabled }" @submit.prevent="submit">
      <div class="segmented">
        <button
          v-for="[value, label] in responses"
          :key="value"
          type="button"
          :class="{ selected: form.response_enum === value }"
          :disabled="disabled"
          @click="form.response_enum = value"
        >
          {{ label }}
        </button>
      </div>
      <div class="tag-list">
        <button
          v-for="tag in tags"
          :key="tag"
          type="button"
          :class="{ selected: form.tags.includes(tag) }"
          :disabled="disabled"
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
      <textarea
        v-model="form.free_text_optional"
        :disabled="disabled"
        placeholder="Mô tả thêm nếu muốn"
      ></textarea>
      <p class="consent-copy">
        Phản hồi được lưu để đối chiếu chất lượng tín hiệu. Bạn có thể để trống phần mô tả tự do.
      </p>
      <button class="primary-button" type="submit" :disabled="disabled">Gửi phản hồi</button>
    </form>
  </section>
</template>
