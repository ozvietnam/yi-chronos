<script setup>
import { computed, onMounted, ref } from "vue";

const manifest = ref(null);
const loading = ref(false);
const errorMsg = ref("");
const activeId = ref(null);
const selectedGroup = ref("Tất cả");

const cards = computed(() => manifest.value?.cards ?? []);
const groups = computed(() => {
  const uniqueGroups = cards.value.map((card) => card.group).filter(Boolean);
  return ["Tất cả", ...Array.from(new Set(uniqueGroups))];
});

const filteredCards = computed(() => {
  if (selectedGroup.value === "Tất cả") return cards.value;
  return cards.value.filter((card) => card.group === selectedGroup.value);
});

const activeCard = computed(() => {
  return (
    cards.value.find((card) => card.id === activeId.value) ??
    filteredCards.value[0] ??
    cards.value[0] ??
    null
  );
});

function selectCard(card) {
  activeId.value = card.id;
}

function setGroup(group) {
  selectedGroup.value = group;
  const nextCard = group === "Tất cả"
    ? cards.value[0]
    : cards.value.find((card) => card.group === group);
  if (nextCard) activeId.value = nextCard.id;
}

onMounted(async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const response = await fetch("/oracle-cards/tu-vi/cards.json");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    manifest.value = await response.json();
    if (cards.value.length) activeId.value = cards.value[0].id;
  } catch (err) {
    errorMsg.value = err?.message || "Không tải được bộ thẻ Tử Vi.";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section class="panel oracle-deck" aria-label="Tử Vi Oracle Cards">
    <header class="oracle-header">
      <div>
        <p class="oracle-kicker">Bộ ảnh tinh tuyển</p>
        <h2>Tử Vi Oracle Cards</h2>
        <p>
          30 thẻ đã đối chiếu mô tả trong xưởng ảnh. Bộ 31-45 giữ lịch cập nhật sau,
          để tránh đưa nhầm ảnh chưa duyệt vào giao diện chính.
        </p>
      </div>
      <div class="oracle-count" aria-label="Số thẻ đã duyệt">
        <strong>{{ cards.length || manifest?.total_cards || 0 }}</strong>
        <span>thẻ</span>
      </div>
    </header>

    <p v-if="loading" class="oracle-status">Đang tải bộ thẻ...</p>
    <p v-else-if="errorMsg" class="oracle-status error">{{ errorMsg }}</p>

    <template v-else-if="activeCard">
      <nav class="oracle-groups" aria-label="Lọc nhóm thẻ">
        <button
          v-for="group in groups"
          :key="group"
          type="button"
          :class="{ active: selectedGroup === group }"
          @click="setGroup(group)"
        >
          {{ group }}
        </button>
      </nav>

      <div class="oracle-showcase">
        <figure class="oracle-featured">
          <img :src="activeCard.image" :alt="`Thẻ ${activeCard.title}`" />
        </figure>

        <article class="oracle-reading">
          <div class="oracle-card-meta">
            <span>{{ activeCard.group }}</span>
            <span>#{{ String(activeCard.id).padStart(2, "0") }}</span>
          </div>
          <h3>{{ activeCard.title }}</h3>
          <p class="oracle-ascii">{{ activeCard.title_ascii }}</p>
          <p class="oracle-interpretation">{{ activeCard.interpretation }}</p>

          <dl class="oracle-facts">
            <div v-if="activeCard.category">
              <dt>Trục nghĩa</dt>
              <dd>{{ activeCard.category }}</dd>
            </div>
            <div v-if="activeCard.symbols">
              <dt>Biểu tượng</dt>
              <dd>{{ activeCard.symbols }}</dd>
            </div>
            <div v-if="activeCard.colors">
              <dt>Màu chủ đạo</dt>
              <dd>{{ activeCard.colors }}</dd>
            </div>
          </dl>

          <div class="oracle-polarity">
            <section>
              <span>Sáng</span>
              <p>{{ activeCard.light }}</p>
            </section>
            <section>
              <span>Lệch</span>
              <p>{{ activeCard.shadow }}</p>
            </section>
          </div>
        </article>
      </div>

      <div class="oracle-rail" aria-label="Danh sách thẻ">
        <button
          v-for="card in filteredCards"
          :key="card.id"
          type="button"
          class="oracle-thumb"
          :class="{ active: activeCard.id === card.id }"
          @click="selectCard(card)"
        >
          <img :src="card.image" :alt="card.title" loading="lazy" />
          <span>{{ card.title }}</span>
        </button>
      </div>
    </template>
  </section>
</template>

<style scoped>
.oracle-deck {
  display: grid;
  gap: 16px;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(232, 201, 90, 0.1), transparent 34%),
    linear-gradient(180deg, rgba(12, 22, 28, 0.92), rgba(8, 14, 20, 0.96));
}

.oracle-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(232, 201, 90, 0.16);
}

.oracle-kicker {
  margin: 0 0 6px;
  color: var(--accent-teal, #5be5d3);
  font-size: 11px;
  font-weight: 760;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.oracle-header h2 {
  margin: 0;
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 24px;
  line-height: 1.18;
}

.oracle-header p:last-child {
  max-width: 720px;
  margin: 8px 0 0;
  color: var(--text-secondary, rgba(230, 238, 245, 0.74));
  font-size: 13px;
  line-height: 1.6;
}

.oracle-count {
  min-width: 78px;
  padding: 10px 12px;
  border: 1px solid rgba(232, 201, 90, 0.24);
  border-radius: 8px;
  background: rgba(232, 201, 90, 0.08);
  text-align: center;
}

.oracle-count strong,
.oracle-count span {
  display: block;
}

.oracle-count strong {
  color: #fff5c6;
  font-size: 24px;
  line-height: 1;
}

.oracle-count span {
  margin-top: 4px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

.oracle-status {
  margin: 0;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
  font-size: 13px;
}

.oracle-status.error {
  color: #f87171;
}

.oracle-groups {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.oracle-groups button {
  min-height: 34px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0 12px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-secondary, rgba(230, 238, 245, 0.74));
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.oracle-groups button:hover,
.oracle-groups button.active {
  border-color: rgba(232, 201, 90, 0.46);
  background: rgba(232, 201, 90, 0.12);
  color: var(--accent-gold-soft, #f5e6b1);
}

.oracle-showcase {
  display: grid;
  grid-template-columns: minmax(280px, 0.82fr) minmax(340px, 1fr);
  gap: 18px;
  align-items: stretch;
}

.oracle-featured {
  display: grid;
  place-items: center;
  min-height: 520px;
  margin: 0;
  border: 1px solid rgba(232, 201, 90, 0.18);
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.01)),
    #070d13;
  overflow: hidden;
}

.oracle-featured img {
  display: block;
  width: 100%;
  height: min(70vh, 620px);
  max-height: 620px;
  object-fit: contain;
}

.oracle-reading {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
  padding: 18px;
  border: 1px solid rgba(91, 229, 211, 0.15);
  border-radius: 8px;
  background: rgba(4, 12, 18, 0.58);
}

.oracle-card-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--accent-teal, #5be5d3);
  font-size: 11px;
  font-weight: 760;
  letter-spacing: 0.6px;
  text-transform: uppercase;
}

.oracle-reading h3 {
  margin: 0;
  color: #fff7d6;
  font-size: 30px;
  line-height: 1.08;
}

.oracle-ascii {
  margin: -8px 0 0;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-size: 12px;
  font-weight: 700;
}

.oracle-interpretation {
  margin: 0;
  color: rgba(248, 250, 252, 0.9);
  font-size: 15px;
  line-height: 1.68;
}

.oracle-facts {
  display: grid;
  gap: 10px;
  margin: 0;
}

.oracle-facts div {
  padding: 10px 12px;
  border-left: 2px solid rgba(232, 201, 90, 0.44);
  background: rgba(255, 255, 255, 0.035);
}

.oracle-facts dt {
  margin: 0 0 4px;
  color: var(--text-muted, rgba(230, 238, 245, 0.56));
  font-size: 11px;
  font-weight: 760;
  text-transform: uppercase;
}

.oracle-facts dd {
  margin: 0;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  font-size: 13px;
  line-height: 1.55;
}

.oracle-polarity {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: auto;
}

.oracle-polarity section {
  min-height: 92px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.035);
}

.oracle-polarity span {
  color: var(--accent-gold-soft, #f5e6b1);
  font-size: 11px;
  font-weight: 760;
  text-transform: uppercase;
}

.oracle-polarity p {
  margin: 6px 0 0;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  font-size: 13px;
  line-height: 1.55;
}

.oracle-rail {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 138px;
  gap: 10px;
  margin: 0 -16px -16px;
  padding: 0 16px 16px;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  scroll-snap-type: x proximity;
  scrollbar-color: rgba(232, 201, 90, 0.45) rgba(255, 255, 255, 0.06);
}

.oracle-thumb {
  display: grid;
  grid-template-rows: 180px minmax(34px, auto);
  gap: 8px;
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 8px;
  padding: 7px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-secondary, rgba(230, 238, 245, 0.76));
  cursor: pointer;
  scroll-snap-align: start;
  text-align: left;
}

.oracle-thumb:hover,
.oracle-thumb.active {
  border-color: rgba(232, 201, 90, 0.5);
  background: rgba(232, 201, 90, 0.1);
}

.oracle-thumb img {
  width: 100%;
  height: 100%;
  border-radius: 6px;
  object-fit: cover;
  background: #071018;
}

.oracle-thumb span {
  display: block;
  color: inherit;
  font-size: 11px;
  font-weight: 780;
  line-height: 1.25;
  text-align: center;
  overflow-wrap: anywhere;
}

@media (max-width: 900px) {
  .oracle-showcase {
    grid-template-columns: 1fr;
  }

  .oracle-featured {
    min-height: 0;
  }

  .oracle-featured img {
    height: min(68vh, 560px);
  }
}

@media (max-width: 640px) {
  .oracle-deck {
    gap: 14px;
  }

  .oracle-header {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 12px;
  }

  .oracle-header h2 {
    font-size: 21px;
  }

  .oracle-header p:last-child {
    font-size: 12.5px;
  }

  .oracle-count {
    min-width: 60px;
    padding: 8px;
  }

  .oracle-groups {
    flex-wrap: nowrap;
    margin: 0 -16px;
    padding: 0 16px 2px;
    overflow-x: auto;
  }

  .oracle-groups button {
    flex: 0 0 auto;
  }

  .oracle-reading {
    padding: 14px;
  }

  .oracle-reading h3 {
    font-size: 24px;
  }

  .oracle-featured img {
    height: min(64vh, 500px);
  }

  .oracle-polarity {
    grid-template-columns: 1fr;
  }

  .oracle-rail {
    grid-auto-columns: 124px;
  }

  .oracle-thumb {
    grid-template-rows: 162px minmax(38px, auto);
  }
}
</style>
