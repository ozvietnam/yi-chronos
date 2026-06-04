<script setup>
/**
 * Unified citation / study-note block.
 *   <RefBlock kind="cite">Thiệu Vĩ Hoa — <i>Dự đoán theo Tứ trụ</i>, Q.1 tr.101</RefBlock>
 *   <RefBlock kind="note">Đọc đồng dạng, KHÔNG predict.</RefBlock>
 * Styling lives in main.css (.ref-cite / .ref-note) so it follows the active
 * reading theme + global text scale.
 */
const props = defineProps({
  kind: { type: String, default: "cite" }, // "cite" | "note"
  label: { type: String, default: "" },
});

const isCite = props.kind !== "note";
const defaultLabel = isCite ? "📚 Nguồn:" : "💡 Ghi chú:";
</script>

<template>
  <div :class="isCite ? 'ref-cite' : 'ref-note'">
    <span class="ref-lbl">{{ label || defaultLabel }}</span>
    <span class="ref-body"><slot /></span>
  </div>
</template>

<style scoped>
.ref-body { margin-left: 0.4em; }
</style>
