<script setup>
/**
 * 📖 Hồ sơ 14 Chính Tinh + Vô Chính Diệu — thư viện nghiên cứu sâu.
 *
 * Anh chốt 2026-06-12: "trang mình chưa nghiên cứu sâu 14 chính tinh rõ nét,
 * chưa đưa âm dương ngũ hành vào làm kiến thức nền tảng."
 *
 * 3 tầng mỗi sao: metadata cổ truyền Q2 (hành/âm dương/hóa khí/chủ về)
 * + Ngũ Uẩn 5 lớp (Tử Vi Bôn Ba) + bảng miếu-hãm 12 chi (độ khó bài học).
 * Mở đầu = kiến thức nền Âm Dương Ngũ Hành (định nghĩa + vòng sinh khắc).
 */
import { ref } from "vue";

const open = ref(false);
const loading = ref(false);
const error = ref("");
const nenTang = ref(null);
const profiles = ref([]);
const paradigmNote = ref("");
const selected = ref(null);

const UAN_LABELS = {
  sac: "Sắc — biểu hiện ra ngoài",
  tho: "Thọ — cảm xúc",
  tuong: "Tưởng — cách nhìn cuộc đời",
  hanh: "Hành — phản ứng & thói quen",
  thuc: "Thức — niềm tin sâu nhất",
};
const UAN_KEYS = ["sac", "tho", "tuong", "hanh", "thuc"];

async function toggle() {
  open.value = !open.value;
  if (open.value && !profiles.value.length && !loading.value) {
    loading.value = true;
    error.value = "";
    try {
      const resp = await fetch("/api/tu-vi/star-profiles");
      const d = await resp.json();
      if (d.status !== "ok") throw new Error("API trả " + d.status);
      nenTang.value = d.nen_tang;
      profiles.value = d.profiles || [];
      paradigmNote.value = d.paradigm_note || "";
      selected.value = profiles.value[0] || null;
    } catch (e) {
      error.value = "Không tải được hồ sơ sao: " + (e?.message || e);
    } finally {
      loading.value = false;
    }
  }
}

function uanOf(profile, key) {
  const u = profile?.ngu_uan?.ngu_uan?.[key];
  if (!u) return null;
  if (typeof u === "string") return { mo_ta: u };
  return u;
}

function levelClass(lv) {
  if (lv === "miếu" || lv === "vượng") return "lv-thuan";
  if (lv === "đắc") return "lv-kha";
  if (lv === "hãm" || lv === "lạc") return "lv-kho";
  return "lv-binh";
}
</script>

<template>
  <section class="ctl-block">
    <button type="button" class="ctl-toggle" @click="toggle">
      <span>📖 Hồ sơ 14 Chính Tinh — kiến thức nền Âm Dương Ngũ Hành</span>
      <small>{{ open ? "thu gọn ▲" : "mở ra ▼" }}</small>
    </button>

    <div v-if="open" class="ctl-body">
      <p v-if="loading" class="ctl-note">Đang tải hồ sơ sao…</p>
      <p v-else-if="error" class="ctl-error">{{ error }}</p>

      <template v-else-if="profiles.length">
        <!-- ── Kiến thức nền ── -->
        <div v-if="nenTang" class="ctl-nen">
          <p class="ctl-nen-line"><b>Âm dương:</b> {{ nenTang.dinh_nghia.am_duong }}</p>
          <p class="ctl-nen-line"><b>Ngũ hành:</b> {{ nenTang.dinh_nghia.ngu_hanh }}</p>
          <div class="ctl-vong">
            <span class="ctl-vong-label">Vòng sinh:</span>
            <template v-for="(pair, i) in nenTang.vong_sinh" :key="'s' + i">
              <span class="nh-badge" :data-hanh="pair[0]">{{ pair[0] }}</span>
              <span class="ctl-arrow">→</span>
            </template>
            <span class="nh-badge" data-hanh="mộc">mộc</span>
          </div>
          <div class="ctl-vong">
            <span class="ctl-vong-label">Vòng khắc:</span>
            <template v-for="(pair, i) in nenTang.vong_khac" :key="'k' + i">
              <span class="nh-badge" :data-hanh="pair[0]">{{ pair[0] }}</span>
              <span class="ctl-arrow">⊣</span>
            </template>
            <span class="nh-badge" data-hanh="mộc">mộc</span>
          </div>
          <p class="ctl-nen-line ctl-nen-sinh-khac">{{ nenTang.dinh_nghia.sinh_khac }}</p>
        </div>

        <!-- ── Lưới chọn sao ── -->
        <div class="ctl-grid">
          <button
            v-for="p in profiles" :key="p.co_ban.ten_vi"
            type="button"
            class="ctl-chip"
            :class="{ active: selected === p }"
            :data-hanh="(p.co_ban.ngu_hanh || '').split('/')[0].trim()"
            @click="selected = p"
          >
            {{ p.co_ban.ten_vi }}
            <small v-if="p.co_ban.ngu_hanh">{{ p.co_ban.am_duong }} {{ p.co_ban.ngu_hanh }}</small>
          </button>
        </div>

        <!-- ── Hồ sơ sao đang chọn ── -->
        <article v-if="selected" class="ctl-detail">
          <header class="ctl-head">
            <h5>
              {{ selected.co_ban.ten_vi }}
              <span v-if="selected.co_ban.ten_zh" class="ctl-zh">{{ selected.co_ban.ten_zh }}</span>
            </h5>
            <div class="ctl-head-badges">
              <span v-if="selected.co_ban.ngu_hanh" class="nh-badge"
                :data-hanh="(selected.co_ban.ngu_hanh || '').split('/')[0].trim()">
                {{ selected.co_ban.am_duong }} {{ selected.co_ban.ngu_hanh }}
              </span>
              <span v-if="selected.co_ban.hoa_khi" class="ctl-hoakhi">hóa khí: {{ selected.co_ban.hoa_khi }}</span>
              <span v-if="(selected.co_ban.chu_ve || []).length" class="ctl-chuve">
                chủ về: {{ selected.co_ban.chu_ve.join(", ") }}
              </span>
            </div>
            <p v-if="(selected.co_ban.keywords || []).length" class="ctl-kw">
              {{ selected.co_ban.keywords.join(" · ") }}
            </p>
          </header>

          <p v-if="selected.ngu_uan?.menh_de_dinh_vi" class="ctl-dinh-vi">
            {{ selected.ngu_uan.menh_de_dinh_vi }}
          </p>
          <p v-if="selected.sao_o_dau_thi" class="ctl-odau">☞ {{ selected.sao_o_dau_thi }}</p>

          <!-- 5 uẩn -->
          <dl v-if="selected.ngu_uan" class="ctl-uan">
            <template v-for="key in UAN_KEYS" :key="key">
              <template v-if="uanOf(selected, key)">
                <dt>{{ UAN_LABELS[key] }}</dt>
                <dd>
                  {{ uanOf(selected, key).mo_ta }}
                  <span v-if="uanOf(selected, key).khi_manh" class="ctl-manh">
                    ▲ Khi mạnh: {{ uanOf(selected, key).khi_manh }}</span>
                  <span v-if="uanOf(selected, key).khi_lech" class="ctl-lech">
                    ▽ Khi lệch: {{ uanOf(selected, key).khi_lech }}</span>
                </dd>
              </template>
            </template>
          </dl>

          <p v-if="selected.ngu_uan?.can_de_phat_huy" class="ctl-can">
            ✦ Cần để phát huy: {{ selected.ngu_uan.can_de_phat_huy }}
          </p>

          <!-- Tích cực / tiêu cực cổ truyền -->
          <p v-if="selected.co_ban.tich_cuc" class="ctl-pos">✦ {{ selected.co_ban.tich_cuc }}</p>
          <p v-if="selected.co_ban.tieu_cuc" class="ctl-neg">⚠ {{ selected.co_ban.tieu_cuc }}</p>

          <!-- Miếu hãm 12 chi -->
          <div v-if="Object.keys(selected.mieu_ham_12_chi || {}).length" class="ctl-mh">
            <span class="ctl-mh-label">Độ khó bài học tại 12 đất cung:</span>
            <span v-for="(lv, chi) in selected.mieu_ham_12_chi" :key="chi"
              class="ctl-mh-chip" :class="levelClass(lv)">
              {{ chi }}<b v-if="lv"> {{ lv }}</b><b v-else> —</b>
            </span>
          </div>

          <!-- Ẩn dụ + quotes gốc -->
          <ul v-if="(selected.ngu_uan?.vi_du_an_du || []).length" class="ctl-andu">
            <li v-for="(a, i) in selected.ngu_uan.vi_du_an_du" :key="i">🌿 {{ a }}</li>
          </ul>
          <blockquote v-for="(q, i) in (selected.ngu_uan?.quotes || []).slice(0, 3)" :key="'q' + i"
            class="ctl-quote">“{{ q }}”</blockquote>
        </article>

        <p v-if="paradigmNote" class="ctl-paradigm">{{ paradigmNote }}</p>
      </template>
    </div>
  </section>
</template>

<style scoped>
.ctl-block { margin: 14px 0; }
.ctl-toggle {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  background: rgba(232, 201, 90, 0.07);
  border: 1px solid rgba(232, 201, 90, 0.25);
  border-radius: 6px;
  color: var(--accent-gold, #e8c95a);
  font-size: 13px;
  cursor: pointer;
  text-align: left;
}
.ctl-toggle small { color: var(--text-secondary, rgba(230, 238, 245, 0.6)); }
.ctl-body {
  margin-top: 10px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-radius: 6px;
}
.ctl-note, .ctl-error { font-size: 12.5px; color: var(--text-secondary, rgba(230,238,245,0.7)); }
.ctl-error { color: #f5a08c; }

.ctl-nen {
  padding: 8px 10px;
  border-left: 2px solid rgba(232, 201, 90, 0.4);
  margin-bottom: 12px;
}
.ctl-nen-line { margin: 2px 0; font-size: 12.5px; line-height: 1.55; color: var(--text-secondary, rgba(230,238,245,0.8)); }
.ctl-nen-sinh-khac { font-style: italic; opacity: 0.85; }
.ctl-vong { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; margin: 5px 0; }
.ctl-vong-label { font-size: 11.5px; color: var(--text-secondary, rgba(230,238,245,0.6)); margin-right: 4px; }
.ctl-arrow { font-size: 11px; color: var(--text-secondary, rgba(230,238,245,0.55)); }

.ctl-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.ctl-chip {
  display: flex; flex-direction: column; align-items: flex-start;
  padding: 5px 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: var(--text-primary, rgba(230, 238, 245, 0.9));
  font-size: 12.5px;
  cursor: pointer;
}
.ctl-chip small { font-size: 10px; color: var(--text-secondary, rgba(230,238,245,0.55)); }
.ctl-chip.active { border-color: var(--accent-gold, #e8c95a); background: rgba(232, 201, 90, 0.1); }

/* màu 5 hành cho viền chip */
.ctl-chip[data-hanh="mộc"], .nh-badge[data-hanh="mộc"] { border-color: rgba(90,176,122,0.55); }
.ctl-chip[data-hanh="hỏa"], .nh-badge[data-hanh="hỏa"] { border-color: rgba(214,90,74,0.55); }
.ctl-chip[data-hanh="thổ"], .nh-badge[data-hanh="thổ"] { border-color: rgba(192,168,120,0.6); }
.ctl-chip[data-hanh="kim"], .nh-badge[data-hanh="kim"] { border-color: rgba(220,220,230,0.45); }
.ctl-chip[data-hanh="thủy"], .nh-badge[data-hanh="thủy"] { border-color: rgba(110,160,220,0.55); }
.nh-badge {
  font-size: 11.5px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: var(--text-primary, rgba(230, 238, 245, 0.9));
}
.nh-badge[data-hanh="mộc"] { color: #8fd6a6; }
.nh-badge[data-hanh="hỏa"] { color: #f5a08c; }
.nh-badge[data-hanh="thổ"] { color: #d9c08e; }
.nh-badge[data-hanh="kim"] { color: #e3e6ee; }
.nh-badge[data-hanh="thủy"] { color: #9cc3f0; }

.ctl-detail { border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 10px; }
.ctl-head h5 { margin: 0 0 4px 0; font-size: 14.5px; color: var(--accent-gold, #e8c95a); }
.ctl-zh { font-weight: 400; margin-left: 6px; opacity: 0.7; }
.ctl-head-badges { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.ctl-hoakhi, .ctl-chuve { font-size: 11.5px; color: var(--text-secondary, rgba(230,238,245,0.7)); font-style: italic; }
.ctl-kw { margin: 5px 0 0 0; font-size: 12px; color: var(--text-secondary, rgba(230,238,245,0.65)); font-style: italic; }
.ctl-dinh-vi { margin: 8px 0 4px 0; font-size: 13px; line-height: 1.6; color: var(--text-primary, rgba(230,238,245,0.92)); }
.ctl-odau {
  margin: 4px 0 8px 0; font-size: 12.5px; line-height: 1.55;
  color: var(--text-primary, rgba(230,238,245,0.85));
  border-left: 2px solid rgba(232, 201, 90, 0.4); padding-left: 8px;
}
.ctl-uan { margin: 8px 0; }
.ctl-uan dt { font-size: 11.5px; font-weight: 600; color: var(--accent-gold, #e8c95a); opacity: 0.85; margin-top: 7px; }
.ctl-uan dd { margin: 2px 0 0 0; font-size: 12.5px; line-height: 1.6; color: var(--text-secondary, rgba(230,238,245,0.8)); }
.ctl-manh { display: block; margin-top: 3px; color: #88d39e; }
.ctl-lech { display: block; margin-top: 2px; color: #f5b08c; }
.ctl-can { margin: 8px 0 0 0; font-size: 12.5px; line-height: 1.55; color: var(--text-primary, rgba(230,238,245,0.88)); }
.ctl-pos { margin: 6px 0 0 0; font-size: 12px; color: #88d39e; line-height: 1.5; }
.ctl-neg { margin: 3px 0 0 0; font-size: 12px; color: #f5b08c; line-height: 1.5; }
.ctl-mh { margin: 10px 0 0 0; display: flex; flex-wrap: wrap; gap: 5px; align-items: center; }
.ctl-mh-label { font-size: 11.5px; color: var(--text-secondary, rgba(230,238,245,0.6)); width: 100%; }
.ctl-mh-chip {
  font-size: 11px; padding: 2px 7px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.12); color: var(--text-secondary, rgba(230,238,245,0.75));
}
.ctl-mh-chip.lv-thuan { border-color: rgba(90,176,122,0.5); color: #88d39e; }
.ctl-mh-chip.lv-kha { border-color: rgba(192,168,120,0.55); color: #d9c08e; }
.ctl-mh-chip.lv-kho { border-color: rgba(214,90,74,0.5); color: #f5a08c; }
.ctl-andu { margin: 10px 0 0 0; padding-left: 4px; list-style: none; }
.ctl-andu li { font-size: 12px; line-height: 1.55; color: var(--text-secondary, rgba(230,238,245,0.75)); }
.ctl-quote {
  margin: 8px 0 0 0; padding: 6px 10px;
  border-left: 2px solid rgba(232, 201, 90, 0.45);
  background: rgba(232, 201, 90, 0.04);
  font-size: 12px; font-style: italic; line-height: 1.55;
  color: var(--text-primary, rgba(230,238,245,0.85));
}
.ctl-paradigm {
  margin: 12px 0 0 0; font-size: 11.5px; font-style: italic;
  color: var(--text-secondary, rgba(230,238,245,0.55));
}
</style>
