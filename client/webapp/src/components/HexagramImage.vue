<script setup>
import { computed } from "vue";

const props = defineProps({
  kingWen: { type: [Number, String], required: true },
  size: { type: [Number, String], default: 40 },
  title: { type: String, default: "" },
});

const padded = computed(() => String(props.kingWen).padStart(2, "0"));
const src = computed(() => `/que-images/${padded.value}.svg`);
const altText = computed(() => props.title || `Quẻ ${props.kingWen}`);
</script>

<template>
  <img
    class="hexagram-image"
    :src="src"
    :alt="altText"
    :title="altText"
    :width="size"
    :height="size"
    loading="lazy"
    onerror="this.style.opacity=0.2;this.title='Hình quẻ chưa có'"
  />
</template>

<style scoped>
.hexagram-image {
  display: inline-block;
  vertical-align: middle;
  filter: drop-shadow(0 0 4px rgba(232, 201, 90, 0.18));
}
</style>
