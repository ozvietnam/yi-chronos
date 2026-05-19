<script setup>
/**
 * LifeOverviewModal — Báo cáo tổng quan cuộc đời (~30 trang A4).
 *
 * 10 sections + nút PRINT để xuất PDF qua browser.
 */
import { ref } from "vue";

const emit = defineEmits(["close"]);

const form = ref({
  birth_date: "1988-05-02",
  birth_hour: 8,
  gender: "nam",
  name: "Đệ tử",
  spouse_birth_date: "",
  spouse_birth_hour: 8,
  spouse_name: "Bạn đời",
});

const report = ref(null);
const loading = ref(false);
const error = ref("");

async function generate() {
  loading.value = true;
  error.value = "";
  try {
    const birth_iso = `${form.value.birth_date}T${String(form.value.birth_hour).padStart(2,'0')}:00:00`;
    const body = {
      birth_iso, gender: form.value.gender, name: form.value.name,
    };
    if (form.value.spouse_birth_date) {
      body.spouse_birth_iso = `${form.value.spouse_birth_date}T${String(form.value.spouse_birth_hour).padStart(2,'0')}:00:00`;
      body.spouse_name = form.value.spouse_name;
    }
    const r = await fetch("/api/yi-wiki/life-overview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const d = await r.json();
    if (d.status !== "ok") {
      error.value = d.message || "Lỗi"; return;
    }
    report.value = d;
  } finally {
    loading.value = false;
  }
}

function printReport() {
  window.print();
}
</script>

<template>
  <div class="lo-modal" @click.self="emit('close')">
    <div class="lo-content">
      <!-- Form input -->
      <div v-if="!report" class="lo-form">
        <button class="lo-close" @click="emit('close')">✕</button>
        <h2>📖 Tổng quan cuộc đời — báo cáo ~30 trang A4</h2>
        <p class="lo-hint">
          Báo cáo đầy đủ về 1 người: Tứ Trụ + Nhật chủ + Dụng thần + Đại Vận + Hà Lạc +
          Sự nghiệp + Hôn nhân + Sức khoẻ + Phương hướng + Lời Thầy.
          Có thể IN ra giấy hoặc xuất PDF.
        </p>

        <h4>Đệ tử (người chính)</h4>
        <div class="form-row">
          <label>Tên: <input v-model="form.name" /></label>
          <label>Giới tính:
            <select v-model="form.gender">
              <option value="nam">Nam</option>
              <option value="nu">Nữ</option>
            </select>
          </label>
        </div>
        <div class="form-row">
          <label>Ngày sinh: <input v-model="form.birth_date" type="date" /></label>
          <label>Giờ sinh:
            <select v-model.number="form.birth_hour">
              <option v-for="h in 24" :key="h-1" :value="h-1">{{ String(h-1).padStart(2,'0') }}h</option>
            </select>
          </label>
        </div>

        <details class="spouse-section">
          <summary>+ Thêm bạn đời (tuỳ chọn — để phân tích hợp tuổi)</summary>
          <div class="form-row">
            <label>Tên: <input v-model="form.spouse_name" /></label>
          </div>
          <div class="form-row">
            <label>Ngày sinh: <input v-model="form.spouse_birth_date" type="date" /></label>
            <label>Giờ sinh:
              <select v-model.number="form.spouse_birth_hour">
                <option v-for="h in 24" :key="h-1" :value="h-1">{{ String(h-1).padStart(2,'0') }}h</option>
              </select>
            </label>
          </div>
        </details>

        <button class="btn-primary" @click="generate" :disabled="loading">
          {{ loading ? "Đang luận..." : "🪷 Lập báo cáo tổng quan" }}
        </button>
        <p v-if="error" class="err">❌ {{ error }}</p>
      </div>

      <!-- Report -->
      <div v-else class="lo-report">
        <div class="lo-toolbar no-print">
          <button class="btn-secondary" @click="report = null">↺ Mới</button>
          <button class="btn-primary" @click="printReport">🖨 In / Xuất PDF (A4)</button>
          <button class="btn-secondary" @click="emit('close')">✕ Đóng</button>
        </div>

        <article class="lo-paper">
          <!-- COVER -->
          <header class="lo-cover">
            <div class="lo-watermark">🪷</div>
            <h1>BÁO CÁO TỔNG QUAN CUỘC ĐỜI</h1>
            <h2>{{ report.meta.name }}</h2>
            <p class="lo-subtitle">
              Sinh: {{ report.meta.birth_iso.slice(0,10) }} ·
              Giờ: {{ report.meta.birth_iso.slice(11,16) }} ·
              {{ report.meta.gender === 'nam' ? 'Nam' : 'Nữ' }}
            </p>
            <p class="lo-school">
              <em>Phái Mai Hoa Dịch Số — Tổ sư Thiệu Khang Tiết (1011-1077)</em><br>
              Tích hợp Bát Tự + Hà Lạc Lý Số
            </p>
            <p class="lo-disclaimer">
              ⚠️ Báo cáo dựa trên thuật pháp cổ truyền Á Đông.
              Tham khảo, không thay thế cho quyết định cá nhân.
            </p>
          </header>

          <!-- SECTION 1: Tứ Trụ -->
          <section class="lo-section">
            <h2>{{ report.section_1_tu_tru.title }}</h2>
            <div class="four-pillars">
              <div v-for="key in ['year','month','day','hour']" :key="key"
                   class="pillar-col" :class="{ master: key === 'day' }">
                <div class="p-pos">{{ report.section_1_tu_tru.pillars[key].position_vi }}</div>
                <div class="p-domain">{{ report.section_1_tu_tru.pillars[key].domain_vi }}</div>
                <div class="p-stem">{{ report.section_1_tu_tru.pillars[key].stem }}</div>
                <div class="p-branch">{{ report.section_1_tu_tru.pillars[key].branch }}</div>
                <div class="p-el">
                  {{ report.section_1_tu_tru.pillars[key].stem_element }} ·
                  {{ report.section_1_tu_tru.pillars[key].branch_element }}
                </div>
                <div class="p-hidden">
                  Tàng: {{ report.section_1_tu_tru.pillars[key].hidden_stems.join(', ') }}
                </div>
              </div>
            </div>

            <h3>Nạp âm</h3>
            <p><b>{{ report.section_1_tu_tru.nap_am.name }}</b> ({{ report.section_1_tu_tru.nap_am.hanh }})
              — đây là "vỏ tuổi" theo 60 Giáp Tý.</p>

            <h3>Ngũ hành 8 chữ</h3>
            <div class="hanh-bars">
              <div v-for="(c, h) in report.section_1_tu_tru.hanh_count" :key="h" class="hanh-bar">
                <span class="hb-name">{{ h }}</span>
                <span class="hb-bar" :style="{ width: (c*40) + 'px' }"></span>
                <span class="hb-count">{{ c }}</span>
              </div>
            </div>
            <p v-if="report.section_1_tu_tru.thieu_hanh.length">
              <b>Hành THIẾU (cần bù):</b>
              <span v-for="h in report.section_1_tu_tru.thieu_hanh" :key="h" class="hanh-pill">{{ h }}</span>
            </p>
            <p v-if="report.section_1_tu_tru.thua_hanh.length">
              <b>Hành THỪA:</b>
              <span v-for="h in report.section_1_tu_tru.thua_hanh" :key="h" class="hanh-pill bad">{{ h }}</span>
            </p>
            <p><b>Con giáp năm sinh:</b> {{ report.section_1_tu_tru.con_giap }}</p>
          </section>

          <!-- SECTION 2: Nhật chủ -->
          <section class="lo-section">
            <h2>{{ report.section_2_day_master.title }}</h2>
            <div class="day-master-box">
              <div class="dm-label">{{ report.section_2_day_master.stem_profile.label }}</div>
              <div class="dm-image">{{ report.section_2_day_master.stem_profile.image }}</div>
              <p class="dm-personality">{{ report.section_2_day_master.stem_profile.personality }}</p>
            </div>

            <h3>Vai trò của 5 hành với Nhật chủ</h3>
            <div class="roles-grid">
              <div v-for="(role, hanh) in report.section_2_day_master.element_roles" :key="hanh" class="role-cell">
                <b>{{ hanh }}</b> → {{ role }}
              </div>
            </div>
          </section>

          <!-- SECTION 3: Dụng thần -->
          <section class="lo-section">
            <h2>{{ report.section_3_dung_than.title }}</h2>
            <pre v-if="report.section_3_dung_than.dung_than">{{ JSON.stringify(report.section_3_dung_than.dung_than, null, 2) }}</pre>
            <p v-else><i>Đang tính dụng thần...</i></p>
          </section>

          <!-- SECTION 4: Đại Vận -->
          <section class="lo-section">
            <h2>{{ report.section_4_dai_van.title }}</h2>
            <p v-if="!report.section_4_dai_van.vans.length"><i>Đại Vận sẽ được bổ sung sau.</i></p>
            <div v-else class="dai-van-grid">
              <div v-for="v in report.section_4_dai_van.vans" :key="v.age || v.start_age" class="van-cell">
                <b>Vận {{ v.age || v.start_age }}+</b>
                <span>{{ v.stem }} {{ v.branch }}</span>
                <p v-if="v.summary">{{ v.summary }}</p>
              </div>
            </div>
          </section>

          <!-- SECTION 5: Hà Lạc -->
          <section class="lo-section">
            <h2>{{ report.section_5_ha_lac.title }}</h2>
            <div v-if="report.section_5_ha_lac.ha_lac && !report.section_5_ha_lac.ha_lac.error">
              <h3>Tiên thiên Quái</h3>
              <pre>{{ JSON.stringify(report.section_5_ha_lac.ha_lac.tien_thien, null, 2) }}</pre>
              <h3>Hậu thiên Quái</h3>
              <pre>{{ JSON.stringify(report.section_5_ha_lac.ha_lac.hau_thien, null, 2) }}</pre>
            </div>
            <p v-else><i>Hà Lạc chưa khả dụng cho input này.</i></p>
          </section>

          <!-- SECTION 6: Sự nghiệp -->
          <section class="lo-section">
            <h2>{{ report.section_6_career.title }}</h2>
            <p><b>Hành chủ đạo dụng thần:</b> {{ report.section_6_career.dung_hanh }}</p>
            <h3>Lĩnh vực phù hợp (12 gợi ý)</h3>
            <div class="career-grid">
              <div v-for="c in report.section_6_career.candidates" :key="c" class="career-pill">{{ c }}</div>
            </div>
          </section>

          <!-- SECTION 7: Hôn nhân -->
          <section class="lo-section">
            <h2>{{ report.section_7_marriage.title }}</h2>
            <p v-if="!report.section_7_marriage.marriage" class="note">
              {{ report.section_7_marriage.note }}
            </p>
            <div v-else>
              <p><b>Bạn đời:</b> {{ report.section_7_marriage.marriage.person_b.name }} —
                Năm {{ report.section_7_marriage.marriage.person_b.year }} —
                Nạp âm {{ report.section_7_marriage.marriage.person_b.nap_am }}</p>
              <p><b>Tổng điểm:</b> {{ report.section_7_marriage.marriage.total_score }}</p>
              <p><b>Đánh giá:</b> {{ report.section_7_marriage.marriage.grade }}</p>
              <p>{{ report.section_7_marriage.marriage.summary }}</p>
              <h4 v-if="report.section_7_marriage.marriage.blessings.length">⭐ Điểm tốt</h4>
              <ul><li v-for="b in report.section_7_marriage.marriage.blessings" :key="b">{{ b }}</li></ul>
              <h4 v-if="report.section_7_marriage.marriage.warnings.length">⚠️ Cần lưu ý</h4>
              <ul><li v-for="w in report.section_7_marriage.marriage.warnings" :key="w">{{ w }}</li></ul>
            </div>
          </section>

          <!-- SECTION 8: Sức khoẻ -->
          <section class="lo-section">
            <h2>{{ report.section_8_health.title }}</h2>
            <p v-if="report.section_8_health.weak_areas.length">
              <b>Khu vực cần chú ý đặc biệt (hành thiếu):</b>
              {{ report.section_8_health.weak_areas.join(', ') }}
            </p>
            <h3>Chi tiết theo hành</h3>
            <ul class="health-list">
              <li v-for="(note, h) in report.section_8_health.health_notes" :key="h">
                <b>{{ h }}:</b> {{ note }}
              </li>
            </ul>
          </section>

          <!-- SECTION 9: Phương hướng + may mắn -->
          <section class="lo-section">
            <h2>{{ report.section_9_favorable.title }}</h2>
            <div class="fav-grid">
              <div class="fav-cell good">
                <h4>✅ Nên dùng</h4>
                <p><b>Màu sắc:</b> {{ report.section_9_favorable.favorable.colors }}</p>
                <p><b>Phương hướng:</b> {{ report.section_9_favorable.favorable.direction }}</p>
                <p><b>Số may mắn:</b> {{ report.section_9_favorable.favorable.numbers?.join(', ') }}</p>
              </div>
              <div class="fav-cell bad" v-if="report.section_9_favorable.avoid_colors.length">
                <h4>❌ Hạn chế</h4>
                <p><b>Màu:</b> {{ report.section_9_favorable.avoid_colors.join(', ') }}</p>
                <p><b>Hành cần tránh thêm:</b> {{ report.section_9_favorable.avoid_hanh.join(', ') }}</p>
              </div>
            </div>
          </section>

          <!-- SECTION 10: Lời Thầy -->
          <section class="lo-section advice">
            <h2>{{ report.section_10_advice.title }}</h2>
            <ol class="advice-list">
              <li v-for="(p, i) in report.section_10_advice.key_principles" :key="i">{{ p }}</li>
            </ol>
            <hr/>
            <p class="lo-footer-quote">
              <em>"Vạn vật bị ư ngã. Quẻ là gương, tâm là gốc."</em><br>
              — Thầy Thiệu Khang Tiết
            </p>
          </section>

          <footer class="lo-footer no-print">
            <p>YI-Chronos · Phái Mai Hoa Dịch Số · Báo cáo phiên bản {{ report.meta.report_version }}</p>
          </footer>
        </article>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lo-modal {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.85);
  z-index: 2000;
  display: flex; align-items: flex-start; justify-content: center;
  padding: 2rem 1rem;
  overflow-y: auto;
}
.lo-content {
  background: #0f172a;
  border-radius: 8px;
  width: 100%;
  max-width: 800px;
  position: relative;
  color: #e2e8f0;
}

/* Form (initial) */
.lo-form {
  padding: 1.5rem 1.75rem;
}
.lo-close {
  position: absolute; top: 0.7rem; right: 1rem;
  background: rgba(167,139,250,0.2);
  color: #c4b5fd;
  border: none; padding: 0.3rem 0.7rem;
  border-radius: 4px; cursor: pointer;
}
.lo-form h2 { margin: 0 0 0.4rem; color: #fbbf24; }
.lo-form h4 { color: #c4b5fd; margin: 0.85rem 0 0.3rem; font-size: 0.9rem; }
.lo-hint { color: #94a3b8; font-size: 0.85rem; line-height: 1.6; margin: 0 0 0.85rem; }
.form-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
.form-row label { flex: 1; display: flex; flex-direction: column; font-size: 0.8rem; color: #94a3b8; }
.form-row input, .form-row select {
  margin-top: 0.18rem;
  padding: 0.38rem 0.55rem;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.12);
  color: #e2e8f0;
  border-radius: 3px;
  font-size: 0.85rem;
}
.spouse-section { margin: 0.5rem 0 0.85rem; padding: 0.4rem 0; }
.spouse-section summary { cursor: pointer; color: #c4b5fd; font-size: 0.85rem; padding: 0.3rem 0; }
.btn-primary, .btn-secondary {
  padding: 0.55rem 1rem;
  border: none; border-radius: 4px; cursor: pointer;
  font-weight: 600; font-size: 0.88rem;
  margin: 0.5rem 0.4rem 0 0;
}
.btn-primary { background: #a78bfa; color: #1e1b4b; }
.btn-secondary { background: rgba(167,139,250,0.2); color: #c4b5fd; }
.err { color: #f87171; margin: 0.4rem 0 0; }

/* Toolbar */
.lo-toolbar {
  display: flex;
  gap: 0.4rem;
  padding: 0.85rem 1rem;
  background: rgba(15,23,42,0.95);
  position: sticky; top: 0; z-index: 10;
  border-radius: 8px 8px 0 0;
}

/* Report (A4 simulation) */
.lo-report { padding: 0; max-height: 90vh; overflow-y: auto; }
.lo-paper {
  background: #fef3c7;
  color: #1c1917;
  padding: 2rem 2.5rem;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 11pt;
  line-height: 1.55;
}

/* Cover */
.lo-cover {
  text-align: center;
  padding: 4rem 1rem 5rem;
  border-bottom: 2px dashed #a16207;
  position: relative;
  page-break-after: always;
}
.lo-watermark {
  font-size: 6rem;
  color: rgba(124,45,18,0.15);
  position: absolute;
  top: 30%;
  left: 50%;
  transform: translate(-50%, -50%);
}
.lo-cover h1 {
  font-size: 26pt;
  letter-spacing: 0.05em;
  color: #7c2d12;
  margin: 0 0 0.5rem;
}
.lo-cover h2 { color: #a16207; font-size: 20pt; margin: 0 0 1rem; }
.lo-subtitle { color: #57534e; font-size: 11pt; }
.lo-school { color: #7c2d12; font-style: italic; margin: 2rem 0; }
.lo-disclaimer { font-size: 9pt; color: #78716c; margin-top: 3rem; }

.lo-section {
  margin: 1.5rem 0;
  page-break-inside: avoid;
}
.lo-section h2 {
  color: #7c2d12;
  border-bottom: 1px solid #a16207;
  padding-bottom: 0.3rem;
  font-size: 14pt;
  margin: 2rem 0 0.85rem;
}
.lo-section h3 { color: #a16207; font-size: 12pt; margin: 0.85rem 0 0.3rem; }
.lo-section h4 { color: #7c2d12; font-size: 11pt; margin: 0.6rem 0 0.25rem; }
.lo-section p { margin: 0.4rem 0; }
.lo-section b { color: #7c2d12; }

/* 4 pillars */
.four-pillars {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  margin: 0.6rem 0;
}
.pillar-col {
  border: 1px solid #a16207;
  border-radius: 4px;
  padding: 0.5rem 0.4rem;
  text-align: center;
  background: rgba(255,255,255,0.4);
  font-size: 9pt;
}
.pillar-col.master {
  background: rgba(251,191,36,0.3);
  border: 2px solid #7c2d12;
}
.p-pos { font-size: 8pt; color: #57534e; }
.p-domain { font-size: 7pt; color: #78716c; margin-bottom: 0.2rem; line-height: 1.3; }
.p-stem { font-size: 15pt; font-weight: 700; color: #7c2d12; }
.p-branch { font-size: 13pt; color: #a16207; margin-top: -0.2rem; }
.p-el { font-size: 8pt; color: #57534e; }
.p-hidden { font-size: 7pt; color: #78716c; margin-top: 0.3rem; }

.hanh-bars { padding: 0.4rem 0; }
.hanh-bar { display: flex; align-items: center; gap: 0.4rem; padding: 0.15rem 0; }
.hb-name { width: 50px; font-weight: 600; color: #7c2d12; }
.hb-bar { height: 12px; background: #a16207; border-radius: 2px; }
.hb-count { font-size: 9pt; color: #57534e; }

.hanh-pill {
  display: inline-block;
  padding: 0.1rem 0.4rem;
  margin: 0 0.15rem;
  background: #fbbf24;
  color: #7c2d12;
  border-radius: 3px;
  font-size: 9pt;
}
.hanh-pill.bad { background: #fca5a5; color: #7f1d1d; }

/* Day master */
.day-master-box {
  background: rgba(251,191,36,0.2);
  border-left: 3px solid #7c2d12;
  padding: 0.7rem 1rem;
  border-radius: 4px;
  margin: 0.6rem 0;
}
.dm-label { font-size: 14pt; font-weight: 700; color: #7c2d12; }
.dm-image { color: #a16207; font-style: italic; margin: 0.2rem 0 0.4rem; }
.dm-personality { line-height: 1.65; }

.roles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.3rem;
  font-size: 9pt;
}
.role-cell { padding: 0.3rem 0.5rem; background: rgba(255,255,255,0.4); border-radius: 3px; }

/* Đại Vận */
.dai-van-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.3rem;
}
.van-cell { border: 1px solid #a16207; padding: 0.35rem; border-radius: 3px; font-size: 9pt; }

/* JSON pre */
pre {
  background: rgba(255,255,255,0.5);
  padding: 0.5rem 0.7rem;
  border-radius: 3px;
  font-size: 8pt;
  white-space: pre-wrap;
  overflow-x: auto;
  border: 1px solid #d6d3d1;
}

/* Career */
.career-grid {
  display: flex; flex-wrap: wrap; gap: 0.3rem;
  margin: 0.3rem 0;
}
.career-pill {
  background: rgba(251,191,36,0.3);
  padding: 0.25rem 0.6rem;
  border-radius: 3px;
  font-size: 9pt;
}

/* Health */
.health-list { padding-left: 1.4rem; }
.health-list li { padding: 0.2rem 0; }

/* Favorable */
.fav-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}
.fav-cell { padding: 0.5rem 0.7rem; border-radius: 4px; }
.fav-cell.good { background: rgba(52,211,153,0.18); border-left: 2px solid #34d399; }
.fav-cell.bad { background: rgba(248,113,113,0.12); border-left: 2px solid #f87171; }
.fav-cell h4 { margin: 0 0 0.3rem; }

/* Advice */
.advice-list { padding-left: 1.3rem; }
.advice-list li {
  padding: 0.3rem 0;
  line-height: 1.65;
}
.lo-footer-quote {
  text-align: center;
  margin-top: 1.5rem;
  padding: 1rem;
  border: 1px dashed #a16207;
  border-radius: 5px;
  font-style: italic;
  color: #7c2d12;
}
.lo-footer { text-align: center; font-size: 8pt; color: #78716c; padding: 1rem; }

.note { color: #78716c; font-style: italic; }

/* PRINT MODE — A4 */
@media print {
  .lo-modal {
    position: static;
    background: white;
    padding: 0;
    overflow: visible;
  }
  .lo-content {
    background: white;
    max-width: none;
    box-shadow: none;
  }
  .lo-paper {
    padding: 1.5cm 2cm;
    font-size: 10.5pt;
  }
  .no-print { display: none !important; }
  .lo-section { page-break-inside: avoid; }
  .lo-cover { page-break-after: always; }
  pre { font-size: 7pt; }
  body { background: white !important; }
}
</style>
