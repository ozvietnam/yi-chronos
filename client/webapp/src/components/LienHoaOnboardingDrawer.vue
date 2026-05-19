<script setup>
import { ref } from "vue";

const open = ref(false);

const steps = [
  {
    id: 1,
    symbol: "☯",
    title: "Thái Cực",
    body: "Khởi nguyên — trạng thái hỗn nguyên trước khi phân chia. Mọi quẻ đều sinh từ một niệm động tại Thái Cực.",
  },
  {
    id: 2,
    symbol: "⚊ ⚋",
    title: "Lưỡng Nghi",
    body: "Thái Cực sinh Âm Dương. Hai nét vạch — liền (Dương) và đứt (Âm) — là ngôn ngữ gốc của toàn bộ Dịch học.",
  },
  {
    id: 3,
    symbol: "⚌ ⚍ ⚎ ⚏",
    title: "Tứ Tượng",
    body: "Âm Dương chồng đôi sinh 4 hình: Thái Dương, Thiếu Âm, Thiếu Dương, Thái Âm — bốn khuynh hướng vận động cơ bản.",
  },
  {
    id: 4,
    symbol: "☰ ☱ ☲ ☳ ☴ ☵ ☶ ☷",
    title: "Bát Quái",
    body: "Tứ Tượng cộng thêm một vạch sinh 8 đơn quái: Càn, Đoài, Ly, Chấn, Tốn, Khảm, Cấn, Khôn — tám phương vị, tám đức tính.",
  },
  {
    id: 5,
    symbol: "䷀ … ䷿",
    title: "64 Quẻ",
    body: "Bát Quái chồng đôi (thượng × hạ) sinh 64 trùng quái — bản đồ vận hành trọn vẹn của vạn sự.",
  },
  {
    id: 6,
    symbol: "🔢",
    title: "Liên Hoa Độn Pháp",
    body: "Liên Hoa dùng 2 con số tâm ý (tay Phải = thượng, tay Trái = hạ) + tổng số tính Hào động → sinh Tiên đề. Sau đó áp công thức gia số [+4 thượng, +6 hạ, +4 hào động] để sinh ra chuỗi 5, 9 hoặc 13 Không Thời Sự liên hoàn — đặc trưng riêng của trường phái này.",
  },
];
</script>

<template>
  <div class="onboarding-drawer">
    <button class="drawer-toggle" type="button" @click="open = !open">
      <span class="toggle-icon">{{ open ? "▾" : "▸" }}</span>
      📖 Liên Hoa Độn Pháp hoạt động thế nào?
      <small v-if="!open">— bấm để mở chuỗi Thái Cực → 64 Quẻ</small>
    </button>

    <transition name="drawer">
      <div v-if="open" class="drawer-body">
        <p class="drawer-intro">
          Trước khi gieo, hãy hiểu sơ đồ phát triển của Dịch học — Liên Hoa là một biến thể đặc biệt của
          dòng chảy này, dùng <b>số tâm ý</b> thay cho lịch tự nhiên.
        </p>

        <ol class="step-chain">
          <li v-for="step in steps" :key="step.id" class="step-card">
            <div class="step-head">
              <span class="step-symbol">{{ step.symbol }}</span>
              <h6>
                <span class="step-num">{{ step.id }}.</span>
                {{ step.title }}
              </h6>
            </div>
            <p class="step-body">{{ step.body }}</p>
          </li>
        </ol>

        <p class="drawer-footnote">
          Tham khảo: <em>Liên Hoa Độn Pháp</em> (thư viện sách dự án), Chu Hi <em>Chu Dịch Bản Nghĩa</em>,
          Thiệu Khang Tiết <em>Hoàng Cực Kinh Thế</em>.
        </p>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.onboarding-drawer {
  background: rgba(91, 229, 211, 0.04);
  border: 1px solid rgba(91, 229, 211, 0.22);
  border-radius: 8px;
  overflow: hidden;
}

.drawer-toggle {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--text-primary, #e6eef5);
  padding: 11px 14px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  text-align: left;
}
.drawer-toggle:hover { background: rgba(91, 229, 211, 0.06); }
.drawer-toggle small {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  margin-left: auto;
}
.toggle-icon {
  color: var(--accent-teal, #5be5d3);
  font-size: 11px;
  transition: transform 0.2s;
}

.drawer-body {
  padding: 14px 16px 18px;
  border-top: 1px dashed rgba(91, 229, 211, 0.2);
}

.drawer-intro {
  margin: 0 0 14px 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
}
.drawer-intro b { color: var(--accent-gold-soft, #f5e6b1); }

.step-chain {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.step-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 6px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  position: relative;
}
.step-card::before {
  content: "";
  position: absolute;
  inset: 0;
  border-left: 3px solid var(--accent-teal, #5be5d3);
  border-radius: 6px 0 0 6px;
  pointer-events: none;
  opacity: 0.6;
}

.step-head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.step-symbol {
  font-size: 20px;
  color: var(--accent-gold, #e8c95a);
  font-family: ui-sans-serif, "Noto Sans Symbols 2", system-ui;
  line-height: 1;
}
.step-head h6 {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-gold-soft, #f5e6b1);
}
.step-num {
  color: var(--text-muted, rgba(230, 238, 245, 0.45));
  font-weight: 500;
  margin-right: 4px;
}

.step-body {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--text-secondary, rgba(230, 238, 245, 0.76));
}

.drawer-footnote {
  margin: 14px 0 0 0;
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.42));
  font-style: italic;
  border-top: 1px dashed rgba(255, 255, 255, 0.06);
  padding-top: 10px;
}
.drawer-footnote em { color: var(--text-secondary, rgba(230, 238, 245, 0.6)); font-style: normal; }

.drawer-enter-active, .drawer-leave-active {
  transition: max-height 0.3s ease, opacity 0.2s;
  overflow: hidden;
}
.drawer-enter-from, .drawer-leave-to {
  max-height: 0;
  opacity: 0;
}
.drawer-enter-to, .drawer-leave-from {
  max-height: 1600px;
  opacity: 1;
}

@media (max-width: 640px) {
  .step-chain { grid-template-columns: 1fr; }
  .drawer-toggle small { display: none; }
}
</style>
