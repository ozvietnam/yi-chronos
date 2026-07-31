<script setup>
import SchoolIcon from "./SchoolIcon.vue";

defineProps({
  icon: { type: String, default: "" },
  title: { type: String, required: true },
  purpose: { type: String, required: true },
  steps: { type: Array, default: () => [] },
  warning: { type: String, default: "" },
});
</script>

<template>
  <section class="tab-intro">
    <div class="ti-head">
      <span v-if="icon" class="ti-icon">
        <SchoolIcon :name="icon" :size="22" />
      </span>
      <div class="ti-text">
        <h2>{{ title }}</h2>
        <p>{{ purpose }}</p>
      </div>
    </div>
    <ol v-if="steps.length" class="ti-steps">
      <li v-for="(s, i) in steps" :key="i">{{ s }}</li>
    </ol>
    <p v-if="warning" class="ti-warning">⚠ {{ warning }}</p>
  </section>
</template>

<style scoped>
.tab-intro {
  background: linear-gradient(135deg, rgba(232,201,90,0.08), rgba(91,229,211,0.04));
  border: 1px solid var(--border-accent, rgba(232,201,90,0.25));
  border-radius: 12px;
  padding: 16px 18px;
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ti-head { display: flex; gap: 14px; align-items: flex-start; }
.ti-icon {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--border-accent, rgba(232,201,90,0.35));
  border-radius: 8px;
  color: var(--accent-gold, #e8c95a);
  background: rgba(232,201,90,0.08);
  line-height: 1;
}
.ti-text { flex: 1; }

.ti-text h2 {
  margin: 0 0 4px 0;
  font-size: 17px;
  color: var(--accent-gold-soft, #f5e6b1);
  font-weight: 700;
  letter-spacing: 0.3px;
}

.ti-text p {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-secondary, rgba(230,238,245,0.72));
}

.ti-steps {
  margin: 0;
  padding-left: 22px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 12.5px;
  color: var(--text-secondary, rgba(230,238,245,0.72));
}

.ti-steps li { line-height: 1.5; }
.ti-steps li::marker { color: var(--accent-gold, #e8c95a); font-weight: 700; }

.ti-warning {
  margin: 0;
  padding: 6px 10px;
  background: rgba(214,90,74,0.08);
  border-left: 3px solid rgba(214,90,74,0.5);
  border-radius: 4px;
  font-size: 12px;
  color: rgba(255,144,128,0.92);
}

@media (max-width: 560px) {
  .tab-intro {
    padding: 12px 14px;
    border-radius: 10px;
  }
  .ti-head {
    gap: 10px;
  }
  .ti-text h2 {
    font-size: 15px;
    line-height: 1.35;
  }
  .ti-text p,
  .ti-steps {
    font-size: 12px;
  }
  .ti-steps {
    padding-left: 18px;
  }
}
</style>
