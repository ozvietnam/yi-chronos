<template>
  <div class="gieo-duyen">
    <header class="gd-hero">
      <div class="gd-hero-icon">💞</div>
      <h2>Gieo Duyên</h2>
      <p class="gd-sub">Đạo phu thê soi qua ba hệ Đông phương — Tử Vi · Bát Tự · Kinh Dịch</p>
      <p class="gd-tag">Đúc kết sau khi đọc nhiều sách và tự phản biện · không bói toán, mệnh là động từ</p>
      <div class="gd-actions">
        <a class="gd-pdf-btn" href="/GIEO-DUYEN.pdf" target="_blank" rel="noopener">📄 Đọc / tải bản PDF</a>
      </div>
    </header>

    <!-- Chọn chế độ -->
    <div class="gd-mode">
      <button :class="{ on: mode === 'tim' }" @click="mode = 'tim'">🔍 Tôi đang tìm</button>
      <button :class="{ on: mode === 'cap' }" @click="mode = 'cap'">💑 Đã có đôi</button>
      <button :class="{ on: mode === 'so' }" @click="mode = 'so'">⚖️ So nhiều người</button>
    </div>

    <!-- CHẾ ĐỘ ĐANG TÌM: 4 tính năng cho người độc thân -->
    <section v-if="mode === 'tim'" class="gd-tool">
      <h3>🔍 Duyên của tôi</h3>
      <p class="gd-tool-sub">Nhập lá số của bạn — hệ thống vẽ chân dung nửa kia, đọc đường tình duyên, chỉ năm có duyên và tuổi hợp.</p>
      <div class="gd-form">
        <div class="gd-person" style="flex:1">
          <input v-model="dn" placeholder="Tên (tuỳ chọn)" class="gd-in" />
          <input v-model="db" type="datetime-local" class="gd-in" />
          <select v-model="dg" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        </div>
      </div>
      <button class="gd-run" :disabled="!db || dloading" @click="runDuyen">
        {{ dloading ? '⏳ Đang xem...' : '💗 Xem duyên của tôi' }}
      </button>
      <p v-if="derr" class="gd-err">{{ derr }}</p>

      <div v-if="dres" class="gd-result">
        <!-- Chân dung nửa kia -->
        <div class="gd-card">
          <h5>💗 Chân dung nửa kia</h5>
          <ul><li v-for="(m,i) in dres.chan_dung_nua_kia.mo_ta" :key="i">{{ m }}</li></ul>
          <p class="gd-mini">Con giáp dễ hợp:
            <b v-for="(g,i) in dres.chan_dung_nua_kia.con_giap_hop.tam_hop" :key="i">{{ g }} </b>
            <b v-if="dres.chan_dung_nua_kia.con_giap_hop.luc_hop">· {{ dres.chan_dung_nua_kia.con_giap_hop.luc_hop }}</b>
          </p>
          <p class="gd-note">{{ dres.chan_dung_nua_kia.loi_khuyen }}</p>
        </div>
        <!-- Đường tình duyên -->
        <div class="gd-card">
          <h5>🔍 Đường tình duyên — xu hướng: <b>{{ dres.duyen_ca_nhan.xu_huong }}</b></h5>
          <ul><li v-for="(t,i) in dres.duyen_ca_nhan.tin_hieu" :key="i">{{ t.noi_dung }}</li></ul>
          <p class="gd-mini">Cách vận hành (mệnh là động từ):</p>
          <ul class="gd-do"><li v-for="(c,i) in dres.duyen_ca_nhan.cach_van_hanh" :key="i">{{ c }}</li></ul>
        </div>
        <!-- Năm có duyên -->
        <div class="gd-card">
          <h5>📅 Năm có duyên ({{ dres.nam_co_duyen.tu_nam }}–{{ dres.nam_co_duyen.den_nam }})</h5>
          <div v-if="dres.nam_co_duyen.nam_co_duyen.length" class="gd-years">
            <span v-for="(y,i) in dres.nam_co_duyen.nam_co_duyen" :key="i" class="gd-year">
              <b>{{ y.nam }}</b> <small>({{ y.cung.join('/') }} · {{ y.sao }})</small>
            </span>
          </div>
          <p v-else class="gd-mini">Không có năm sao hỉ nổi bật trong 12 năm tới — duyên đến tự nhiên, chủ động vẫn hơn.</p>
          <p class="gd-note">{{ dres.nam_co_duyen.ghi_chu }}</p>
        </div>
        <!-- Tuổi hợp -->
        <div class="gd-card">
          <h5>🧭 Tuổi hợp – tuổi cần ý thức (bạn tuổi {{ dres.tuoi_hop.con_giap }})</h5>
          <div class="gd-tuoi">
            <span class="ok">Tam hợp: <b>{{ dres.tuoi_hop.tam_hop.map(x=>x.con_giap).join(', ') }}</b></span>
            <span class="ok">Lục hợp: <b>{{ dres.tuoi_hop.luc_hop.con_giap }}</b></span>
            <span class="warn">Xung: {{ dres.tuoi_hop.luc_xung.con_giap }}</span>
            <span class="warn">Hại: {{ dres.tuoi_hop.luc_hai.con_giap }}</span>
          </div>
          <p class="gd-note">{{ dres.tuoi_hop.ghi_chu }}</p>
        </div>
        <!-- Món 2: lời văn ấm -->
        <div class="gd-card gd-tho-card">
          <button v-if="!dtho && !dthoLoading" class="gd-soft-btn" @click="runDuyenTho">💌 Nghe lời tâm tình về duyên của bạn</button>
          <p v-if="dthoLoading" class="gd-mini">✍️ Thầy đang viết đôi lời...</p>
          <div v-if="dtho" class="gd-tho">{{ dtho }}</div>
        </div>
        <!-- Món 4: chia sẻ -->
        <div class="gd-share">
          <button class="gd-soft-btn" @click="shareCard('Chân dung nửa kia của tôi', dres.chan_dung_nua_kia.mo_ta[0]||'', 'Xu hướng: '+dres.duyen_ca_nhan.xu_huong, null)">📤 Tạo thẻ chia sẻ</button>
        </div>
        <p class="gd-para">⚖️ {{ dres.paradigm }}</p>
      </div>
    </section>

    <!-- CHẾ ĐỘ SO NHIỀU NGƯỜI -->
    <section v-if="mode === 'so'" class="gd-tool">
      <h3>⚖️ So nhiều người</h3>
      <p class="gd-tool-sub">Đang phân vân giữa vài người? Nhập lá số của bạn và của họ — hệ thống xếp hạng độ tương ứng.</p>
      <div class="gd-person" style="margin-bottom:12px;">
        <h4>Bạn</h4>
        <input v-model="soMe.ten" placeholder="Tên (tuỳ chọn)" class="gd-in" />
        <input v-model="soMe.birth" type="datetime-local" class="gd-in" />
        <select v-model="soMe.gender" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
      </div>
      <div v-for="(o,i) in soOthers" :key="i" class="gd-other-row">
        <input v-model="o.ten" :placeholder="'Người '+(i+1)" class="gd-in" style="flex:1" />
        <input v-model="o.birth" type="datetime-local" class="gd-in" style="flex:1.4" />
        <select v-model="o.gender" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        <button class="gd-x" @click="rmOther(i)" v-if="soOthers.length>1">✕</button>
      </div>
      <button class="gd-add" @click="addOther" v-if="soOthers.length<8">+ Thêm người</button>
      <button class="gd-run" :disabled="soLoading" @click="runSoSanh">{{ soLoading ? '⏳ Đang so...' : '⚖️ Xếp hạng' }}</button>
      <p v-if="soErr" class="gd-err">{{ soErr }}</p>
      <div v-if="soRes" class="gd-result">
        <div v-for="(r,i) in soRes.xep_hang" :key="i" class="gd-rank">
          <span class="gd-rank-no">{{ i+1 }}</span>
          <div class="gd-rank-body">
            <div class="gd-rank-top"><b>{{ r.ten }}</b> <span class="gd-rank-score">{{ r.diem_tong }}</span> <span v-if="r.ung_nhau" class="gd-ung">cương–nhu ứng ✓</span></div>
            <div class="gd-rank-muc">{{ r.muc }}</div>
            <div v-if="r.diem_noi_bat" class="gd-rank-k">🔑 {{ r.diem_noi_bat }}</div>
          </div>
        </div>
        <p class="gd-note">{{ soRes.ghi_chu }}</p>
      </div>
    </section>

    <!-- CHẾ ĐỘ ĐÃ CÓ ĐÔI: Xem tuổi đôi lứa -->
    <section v-if="mode === 'cap'" class="gd-tool">
      <h3>🔮 Xem tuổi đôi lứa — ba hệ</h3>
      <p class="gd-tool-sub">Nhập lá số của bạn và một lá số khác. Hệ thống soi Tử Vi · Bát Tự · Kinh Dịch, chấm độ <em>tương ứng</em> và gợi ý <strong>gia quy</strong>.</p>
      <div class="gd-form">
        <div class="gd-person">
          <h4>Người 1 (bạn)</h4>
          <input v-model="n1" placeholder="Tên (tuỳ chọn)" class="gd-in" />
          <input v-model="b1" type="datetime-local" class="gd-in" />
          <select v-model="g1" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        </div>
        <div class="gd-heart">💞</div>
        <div class="gd-person">
          <h4>Người 2</h4>
          <input v-model="n2" placeholder="Tên (tuỳ chọn)" class="gd-in" />
          <input v-model="b2" type="datetime-local" class="gd-in" />
          <select v-model="g2" class="gd-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        </div>
      </div>
      <button class="gd-run" :disabled="!b1 || !b2 || loading" @click="run">
        {{ loading ? '⏳ Đang soi ba hệ...' : '✨ Xem tương ứng' }}
      </button>
      <p v-if="err" class="gd-err">{{ err }}</p>

      <!-- Kết quả -->
      <div v-if="res" class="gd-result">
        <div class="gd-score">
          <div class="gd-score-num">{{ res.diem_tong }}<span>/100</span></div>
          <div class="gd-score-muc">{{ res.muc }}</div>
        </div>

        <div class="gd-truc" :class="res.truc_cuong_nhu.ung_nhau ? 'ung' : 'chua'">
          <strong>Trục Cương–Nhu:</strong>
          {{ res.ten1 }} <b>{{ res.truc_cuong_nhu.xu_huong_1 }}</b> ·
          {{ res.ten2 }} <b>{{ res.truc_cuong_nhu.xu_huong_2 }}</b>
          {{ res.truc_cuong_nhu.ung_nhau ? '→ ỨNG NHAU ✓' : '' }}
          <div class="gd-truc-gt">{{ res.truc_cuong_nhu.giai_thich }}</div>
        </div>

        <div class="gd-he">
          <span>Tử Vi <b>{{ res.tu_vi.diem }}</b></span>
          <span>Bát Tự <b>{{ res.bat_tu.diem }}</b></span>
          <span>Kinh Dịch <b>{{ res.ha_lac.diem }}</b></span>
        </div>

        <div class="gd-cols">
          <div class="gd-col khoa">
            <h5>🔑 Khóa duyên</h5>
            <ul><li v-for="(k,i) in res.khoa_duyen" :key="i">{{ k }}</li></ul>
          </div>
          <div class="gd-col giu">
            <h5>🛠 Chỗ phải giữ</h5>
            <ul><li v-for="(c,i) in res.cho_phai_giu" :key="i">{{ c }}</li></ul>
          </div>
        </div>

        <div class="gd-giaquy">
          <h5>📜 Gia quy gợi ý cho hai bạn</h5>
          <ol><li v-for="(g,i) in res.gia_quy" :key="i">{{ g }}</li></ol>
        </div>

        <div v-if="res.nghe_nghiep" class="gd-card">
          <h5>💼 Nghề nghiệp đôi bên</h5>
          <p class="gd-mini"><b>{{ res.ten1 }}</b> ({{ res.nghe_nghiep.nguoi1.thien_huong }}): {{ (res.nghe_nghiep.nguoi1.nghe || []).join('; ') }}</p>
          <p class="gd-mini"><b>{{ res.ten2 }}</b> ({{ res.nghe_nghiep.nguoi2.thien_huong }}): {{ (res.nghe_nghiep.nguoi2.nghe || []).join('; ') }}</p>
          <p class="gd-note">{{ res.nghe_nghiep.doi_ben }}</p>
        </div>
        <div v-if="res.con_cai" class="gd-card" :class="{ 'gd-hit': res.con_cai.khop }">
          <h5>👶 Con cái có khớp không</h5>
          <p class="gd-mini">Cung Con Cái: {{ res.ten1 }} ở {{ res.con_cai.chi_nguoi1 }} · {{ res.ten2 }} ở {{ res.con_cai.chi_nguoi2 }}
            <b v-if="res.con_cai.quan_he"> ({{ res.con_cai.quan_he }})</b></p>
          <p class="gd-note">{{ res.con_cai.ghi_chu }}</p>
        </div>

        <div v-if="res.nam_hop_cuoi && res.nam_hop_cuoi.nam.length" class="gd-card">
          <h5>📅 Năm hợp cưới ({{ res.nam_hop_cuoi.tu_nam }}–{{ res.nam_hop_cuoi.den_nam }})</h5>
          <div class="gd-years">
            <span v-for="(y,i) in res.nam_hop_cuoi.nam" :key="i" class="gd-year" :class="{ dam: y.ca_hai }">
              <b>{{ y.nam }}</b> <small>{{ y.ca_hai ? '⭐ cả hai' : 'một người' }}</small>
            </span>
          </div>
          <p class="gd-note">{{ res.nam_hop_cuoi.ghi_chu }}</p>
        </div>

        <div class="gd-share">
          <button class="gd-soft-btn" @click="shareCard(res.ten1+' 💞 '+res.ten2, res.muc, 'Trục cương–nhu: '+(res.truc_cuong_nhu.ung_nhau?'ứng nhau ✓':'cần dung hòa'), res.diem_tong)">📤 Tạo thẻ chia sẻ</button>
        </div>

        <details class="gd-guide">
          <summary>📖 Hướng dẫn đọc kết quả (đọc trước khi tin)</summary>
          <ul><li v-for="(h,i) in res.huong_dan" :key="i">{{ h }}</li></ul>
          <p class="gd-para">⚖️ {{ res.paradigm }}</p>
        </details>
      </div>
    </section>

    <details class="gd-book-toggle">
      <summary>📖 Đọc sách <b>"Gieo Duyên"</b> — đúc kết đầy đủ qua 3 hệ (một ca điển hình)</summary>
      <article class="gd-body reading-surface" v-html="rendered"></article>
      <p class="gd-foot">Cuốn sách là đúc kết của một ca điển hình. Công cụ phía trên áp cùng phương pháp cho lá số bất kỳ — đọc đồng dạng, không bói toán.</p>
    </details>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import manuscript from "../content/gieo-duyen.md?raw";
import { activeBirthDatetime, activePerson } from "../stores/userDataStore.js";

const mode = ref("tim");  // 'tim' | 'cap' | 'so'

// Món 2: lời văn ấm
const dtho = ref(""); const dthoLoading = ref(false);
async function runDuyenTho() {
  if (!db.value) return;
  dthoLoading.value = true; dtho.value = "";
  try {
    const r = await fetch("/api/tu-vi/duyen-tho", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ birth: db.value, gender: dg.value }),
    });
    const d = await r.json();
    dtho.value = d.narrative || ("Lỗi: " + (d.error || "thử lại"));
  } catch (e) { dtho.value = "Lỗi kết nối."; } finally { dthoLoading.value = false; }
}

// Món 1: so nhiều người
const soMe = ref({ ten: "", birth: "", gender: "nam" });
const soOthers = ref([{ ten: "", birth: "", gender: "nữ" }, { ten: "", birth: "", gender: "nữ" }]);
const soRes = ref(null); const soLoading = ref(false); const soErr = ref("");
function addOther() { if (soOthers.value.length < 8) soOthers.value.push({ ten: "", birth: "", gender: "nữ" }); }
function rmOther(i) { soOthers.value.splice(i, 1); }
async function runSoSanh() {
  if (!soMe.value.birth) { soErr.value = "Nhập lá số của bạn."; return; }
  const others = soOthers.value.filter(o => o.birth);
  if (!others.length) { soErr.value = "Nhập ít nhất 1 người để so."; return; }
  soLoading.value = true; soErr.value = ""; soRes.value = null;
  try {
    const r = await fetch("/api/tu-vi/so-sanh-duyen", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ me: soMe.value, others }),
    });
    const d = await r.json();
    if (d.error) soErr.value = d.error; else soRes.value = d;
  } catch (e) { soErr.value = "Lỗi kết nối."; } finally { soLoading.value = false; }
}

// Món 4: thẻ chia sẻ (SVG → tải ảnh)
function shareCard(title, line1, line2, score) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="315" viewBox="0 0 600 315">
    <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fff6f0"/><stop offset="1" stop-color="#fbe6ef"/></linearGradient></defs>
    <rect width="600" height="315" fill="url(#g)"/>
    <rect x="12" y="12" width="576" height="291" rx="18" fill="none" stroke="#d9a7b8" stroke-width="2"/>
    <text x="300" y="70" text-anchor="middle" font-family="Georgia,serif" font-size="30" fill="#9c3a5a">💞 Gieo Duyên</text>
    <text x="300" y="108" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#7d4357">${_esc(title)}</text>
    ${score != null ? `<text x="300" y="185" text-anchor="middle" font-family="Georgia,serif" font-size="64" font-weight="bold" fill="#9c3a5a">${score}<tspan font-size="22" fill="#c98aa0">/100</tspan></text>` : ""}
    <text x="300" y="${score != null ? 230 : 175}" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#5d4450">${_esc(line1)}</text>
    <text x="300" y="${score != null ? 256 : 205}" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#8a7079">${_esc(line2)}</text>
    <text x="300" y="292" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b89aa3">kinhdich.online · đọc đồng dạng, không bói toán</text>
  </svg>`;
  const img = new Image();
  const blob = new Blob([svg], { type: "image/svg+xml" });
  const url = URL.createObjectURL(blob);
  img.onload = () => {
    const c = document.createElement("canvas"); c.width = 1200; c.height = 630;
    const ctx = c.getContext("2d"); ctx.scale(2, 2); ctx.drawImage(img, 0, 0);
    URL.revokeObjectURL(url);
    c.toBlob((b) => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(b); a.download = "gieo-duyen.png"; a.click();
    });
  };
  img.src = url;
}
function _esc(s) { return String(s || "").slice(0, 80).replace(/[<>&]/g, ""); }

// ── Chế độ ĐANG TÌM: Duyên của tôi ──
const dn = ref(""); const db = ref(""); const dg = ref("nam");
const dloading = ref(false); const dres = ref(null); const derr = ref("");
async function runDuyen() {
  if (!db.value) return;
  dloading.value = true; derr.value = ""; dres.value = null;
  try {
    const r = await fetch("/api/tu-vi/duyen", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ birth: db.value, gender: dg.value }),
    });
    const d = await r.json();
    if (d.error) derr.value = d.error; else dres.value = d;
  } catch (e) { derr.value = "Lỗi kết nối, thử lại."; } finally { dloading.value = false; }
}

// ── Công cụ Xem tuổi đôi lứa ──
const n1 = ref(""); const b1 = ref(""); const g1 = ref("nam");
const n2 = ref(""); const b2 = ref(""); const g2 = ref("nữ");
const loading = ref(false); const res = ref(null); const err = ref("");

onMounted(() => {
  // prefill lá số người dùng nếu đã đăng nhập / có active person
  const bd = activeBirthDatetime?.value;
  if (bd) { b1.value = String(bd).slice(0, 16); db.value = String(bd).slice(0, 16); }
  const p = activePerson?.value;
  if (p?.name) { n1.value = p.name; dn.value = p.name; }
  if (p?.gender) {
    const gg = p.gender === "nữ" || p.gender === "nu" || p.gender === "F" ? "nữ" : "nam";
    g1.value = gg; dg.value = gg;
  }
});

async function run() {
  if (!b1.value || !b2.value) return;
  loading.value = true; err.value = ""; res.value = null;
  try {
    const r = await fetch("/api/tu-vi/hop-hon", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth1: b1.value, gender1: g1.value, ten1: n1.value || "Người 1",
        birth2: b2.value, gender2: g2.value, ten2: n2.value || "Người 2",
      }),
    });
    const d = await r.json();
    if (d.error) { err.value = d.error; } else { res.value = d; }
  } catch (e) { err.value = "Lỗi kết nối, thử lại."; } finally { loading.value = false; }
}

// Markdown nhẹ → HTML (đủ cho sách: heading, đậm, nghiêng, trích dẫn, bảng, hr, list)
function renderMarkdown(md) {
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const lines = md.split("\n");
  const out = [];
  let i = 0;
  const inline = (t) =>
    esc(t)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/`(.+?)`/g, "<code>$1</code>");
  while (i < lines.length) {
    let ln = lines[i];
    if (/^\s*$/.test(ln)) { i++; continue; }
    // bảng
    if (ln.includes("|") && i + 1 < lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1])) {
      const header = ln.split("|").map((c) => c.trim()).filter(Boolean);
      i += 2;
      const rows = [];
      while (i < lines.length && lines[i].includes("|")) {
        rows.push(lines[i].split("|").map((c) => c.trim()).filter((_, k, a) => !(k === 0 && a[0] === "") ));
        i++;
      }
      let t = "<table><thead><tr>" + header.map((h) => `<th>${inline(h)}</th>`).join("") + "</tr></thead><tbody>";
      for (const r of rows) {
        const cells = r.filter((c) => c !== "");
        t += "<tr>" + cells.map((c) => `<td>${inline(c)}</td>`).join("") + "</tr>";
      }
      t += "</tbody></table>";
      out.push(t);
      continue;
    }
    if (/^####\s/.test(ln)) { out.push(`<h5>${inline(ln.replace(/^####\s/, ""))}</h5>`); i++; continue; }
    if (/^###\s/.test(ln)) { out.push(`<h4>${inline(ln.replace(/^###\s/, ""))}</h4>`); i++; continue; }
    if (/^##\s/.test(ln)) { out.push(`<h3>${inline(ln.replace(/^##\s/, ""))}</h3>`); i++; continue; }
    if (/^#\s/.test(ln)) { out.push(`<h2 class="gd-h1">${inline(ln.replace(/^#\s/, ""))}</h2>`); i++; continue; }
    if (/^>\s?/.test(ln)) {
      const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) { buf.push(inline(lines[i].replace(/^>\s?/, ""))); i++; }
      out.push(`<blockquote>${buf.join("<br>")}</blockquote>`);
      continue;
    }
    if (/^(-{3,}|\*{3,})\s*$/.test(ln)) { out.push("<hr>"); i++; continue; }
    if (/^\s*[-*]\s+/.test(ln) || /^\s*\d+\.\s+/.test(ln)) {
      const ordered = /^\s*\d+\.\s+/.test(ln);
      const buf = [];
      while (i < lines.length && (/^\s*[-*]\s+/.test(lines[i]) || /^\s*\d+\.\s+/.test(lines[i]))) {
        buf.push(`<li>${inline(lines[i].replace(/^\s*(?:[-*]|\d+\.)\s+/, ""))}</li>`);
        i++;
      }
      out.push((ordered ? "<ol>" : "<ul>") + buf.join("") + (ordered ? "</ol>" : "</ul>"));
      continue;
    }
    // đoạn văn
    const buf = [];
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^[#>|]/.test(lines[i]) && !/^(-{3,})/.test(lines[i]) && !/^\s*[-*]\s+/.test(lines[i]) && !/^\s*\d+\.\s+/.test(lines[i])) {
      buf.push(inline(lines[i]));
      i++;
    }
    out.push(`<p>${buf.join(" ")}</p>`);
  }
  return out.join("\n");
}

const rendered = computed(() => renderMarkdown(manuscript));
</script>

<style scoped>
.gieo-duyen { max-width: 760px; margin: 0 auto; padding: 16px; }
.gd-hero { text-align: center; padding: 28px 16px 22px; background: linear-gradient(160deg,#fff6f0,#fdeef5); border: 1px solid #e8cdd6; border-radius: 16px; margin-bottom: 22px; }
.gd-hero-icon { font-size: 2.4em; }
.gd-hero h2 { margin: 6px 0 4px; font-size: 1.9em; color: #9c3a5a; letter-spacing: 1px; }
.gd-sub { margin: 4px 0; color: #6a4555; font-size: 0.98em; }
.gd-tag { margin: 8px 0 0; color: #9a7886; font-size: 0.84em; font-style: italic; }
.gd-actions { margin-top: 16px; }
.gd-pdf-btn { display: inline-block; padding: 10px 22px; border-radius: 24px; background: #9c3a5a; color: #fff; text-decoration: none; font-size: 0.92em; transition: all .15s; }
.gd-pdf-btn:hover { background: #7d2c47; transform: translateY(-1px); }

/* Chọn chế độ */
.gd-mode { display: flex; gap: 10px; justify-content: center; margin-bottom: 18px; }
.gd-mode button { flex: 1; max-width: 260px; padding: 12px; border: 1.5px solid #d8b8c3; border-radius: 24px; background: transparent; color: #9c3a5a; font: inherit; font-size: 0.95em; cursor: pointer; transition: all .15s; }
.gd-mode button.on { background: #9c3a5a; color: #fff; border-color: #9c3a5a; }
.gd-mode button:hover:not(.on) { background: #fbeef2; }

/* Thẻ kết quả duyên */
.gd-card { margin: 12px 0; padding: 14px 16px; background: #fdf6f8; border: 1px solid #ecd7df; border-radius: 12px; }
.gd-card h5 { margin: 0 0 8px; color: #9c3a5a; font-size: 1em; }
.gd-card h5 b { text-transform: capitalize; }
.gd-card ul { margin: 6px 0; padding-left: 18px; } .gd-card li { margin: 5px 0; font-size: 0.9em; line-height: 1.55; color: var(--read-text,#3a3a38); }
.gd-card ul.gd-do li { color: #2e7d32; }
.gd-mini { margin: 8px 0 2px; font-size: 0.86em; color: #7d4357; }
.gd-mini b { color: #9c3a5a; }
.gd-note { margin: 8px 0 0; font-size: 0.82em; font-style: italic; color: var(--read-text-faint,#888); line-height: 1.5; }
.gd-years { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0; }
.gd-year { padding: 5px 12px; background: #eef9f0; border: 1px solid #b6dfc0; border-radius: 16px; font-size: 0.88em; }
.gd-year b { color: #2e7d32; }
.gd-tuoi { display: flex; flex-wrap: wrap; gap: 10px; margin: 6px 0; font-size: 0.88em; }
.gd-tuoi .ok { color: #2e7d32; } .gd-tuoi .warn { color: #b06a28; }
.gd-year.dam { background: #ffeef5; border-color: #e09ab8; } .gd-year.dam b { color: #9c3a5a; }
.gd-card.gd-hit { background: #eef9f0; border-color: #b6dfc0; }
.gd-card.gd-hit h5 { color: #2e7d32; }
/* Lời văn ấm */
.gd-soft-btn { padding: 9px 18px; border: 1.5px solid #c98aa0; border-radius: 20px; background: transparent; color: #9c3a5a; font: inherit; font-size: 0.9em; cursor: pointer; transition: all .15s; }
.gd-soft-btn:hover { background: #9c3a5a; color: #fff; }
.gd-tho-card { text-align: center; }
.gd-tho { white-space: pre-wrap; text-align: left; line-height: 1.85; color: var(--read-text,#3a3a38); font-size: 0.95em; margin-top: 8px; }
.gd-share { text-align: center; margin: 12px 0; }
/* So nhiều người */
.gd-other-row { display: flex; gap: 8px; margin-bottom: 8px; align-items: center; }
.gd-x { padding: 6px 10px; border: 1px solid #e0b0bd; border-radius: 8px; background: #fff; color: #c0392b; cursor: pointer; }
.gd-add { display: block; margin: 4px 0 0; padding: 6px 14px; border: 1px dashed #c98aa0; border-radius: 16px; background: transparent; color: #9c3a5a; font: inherit; font-size: 0.85em; cursor: pointer; }
.gd-rank { display: flex; gap: 12px; align-items: flex-start; padding: 12px; margin: 8px 0; background: #fdf6f8; border: 1px solid #ecd7df; border-radius: 12px; }
.gd-rank-no { flex: none; width: 30px; height: 30px; border-radius: 50%; background: #9c3a5a; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.gd-rank-body { flex: 1; }
.gd-rank-top { display: flex; align-items: center; gap: 8px; }
.gd-rank-score { font-size: 1.3em; font-weight: 700; color: #9c3a5a; }
.gd-ung { font-size: 0.78em; color: #2e7d32; background: #eef9f0; padding: 1px 8px; border-radius: 10px; }
.gd-rank-muc { font-size: 0.85em; color: #7d4357; margin: 2px 0; }
.gd-rank-k { font-size: 0.82em; color: var(--read-text-faint,#777); }

/* Công cụ Xem tuổi đôi lứa */
.gd-tool { margin: 0 0 30px; padding: 22px; background: var(--read-surface,#fff); border: 1px solid #e8cdd6; border-radius: 16px; }
.gd-tool h3 { margin: 0 0 4px; color: #9c3a5a; font-size: 1.3em; text-align: center; }
.gd-tool-sub { margin: 0 0 16px; text-align: center; color: var(--read-text-faint,#777); font-size: 0.9em; }
.gd-form { display: flex; align-items: stretch; gap: 12px; flex-wrap: wrap; }
.gd-person { flex: 1; min-width: 210px; display: flex; flex-direction: column; gap: 8px; padding: 12px; background: #fdf6f8; border-radius: 10px; }
.gd-person h4 { margin: 0 0 2px; color: #7d2c47; font-size: 0.95em; }
.gd-in { padding: 8px 10px; border: 1px solid #dcc6cd; border-radius: 8px; font: inherit; font-size: 0.9em; background: #fff; color: #333; }
.gd-heart { display: flex; align-items: center; font-size: 1.6em; }
.gd-run { display: block; width: 100%; margin-top: 14px; padding: 12px; border: none; border-radius: 24px; background: #9c3a5a; color: #fff; font: inherit; font-size: 1em; cursor: pointer; transition: all .15s; }
.gd-run:hover:not(:disabled) { background: #7d2c47; }
.gd-run:disabled { opacity: .5; cursor: not-allowed; }
.gd-err { color: #c0392b; text-align: center; margin-top: 10px; font-size: 0.9em; }

.gd-result { margin-top: 22px; }
.gd-score { text-align: center; margin-bottom: 16px; }
.gd-score-num { font-size: 3em; font-weight: 700; color: #9c3a5a; line-height: 1; }
.gd-score-num span { font-size: 0.35em; color: #b88; font-weight: 400; }
.gd-score-muc { color: #7d4357; font-size: 1.02em; margin-top: 4px; }
.gd-truc { padding: 12px 16px; border-radius: 10px; margin-bottom: 14px; font-size: 0.94em; }
.gd-truc.ung { background: #eef9f0; border: 1px solid #b6dfc0; }
.gd-truc.chua { background: #fbf6ee; border: 1px solid #e6d6b8; }
.gd-truc b { color: #9c3a5a; text-transform: capitalize; }
.gd-truc-gt { margin-top: 6px; color: var(--read-text,#444); font-size: 0.92em; line-height: 1.55; }
.gd-he { display: flex; justify-content: center; gap: 18px; margin-bottom: 16px; font-size: 0.9em; color: #7d4357; }
.gd-he b { color: #9c3a5a; font-size: 1.1em; }
.gd-cols { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
.gd-col { flex: 1; min-width: 230px; padding: 12px 14px; border-radius: 10px; }
.gd-col.khoa { background: #eef9f0; border: 1px solid #c4e6cd; }
.gd-col.giu { background: #fdf3ec; border: 1px solid #ecd3bf; }
.gd-col h5 { margin: 0 0 8px; font-size: 0.95em; }
.gd-col.khoa h5 { color: #2e7d32; } .gd-col.giu h5 { color: #b06a28; }
.gd-col ul { margin: 0; padding-left: 18px; } .gd-col li { margin: 6px 0; font-size: 0.88em; line-height: 1.5; color: var(--read-text,#3a3a38); }
.gd-giaquy { padding: 14px 16px; background: #f5f0fa; border: 1px solid #d8cce8; border-radius: 10px; margin-bottom: 14px; }
.gd-giaquy h5 { margin: 0 0 8px; color: #6a4a9c; }
.gd-giaquy ol { margin: 0; padding-left: 20px; } .gd-giaquy li { margin: 6px 0; font-size: 0.9em; line-height: 1.55; }
.gd-guide summary { cursor: pointer; color: #8a6d1a; font-size: 0.9em; padding: 6px 0; }
.gd-guide ul { padding-left: 18px; } .gd-guide li { margin: 6px 0; font-size: 0.86em; color: var(--read-text-faint,#777); line-height: 1.5; }
.gd-para { font-style: italic; color: #9c3a5a; font-size: 0.88em; margin-top: 8px; }

.gd-book-toggle { margin-top: 24px; border-top: 1px solid #ecd7df; padding-top: 14px; }
.gd-book-toggle > summary { cursor: pointer; padding: 12px 16px; background: #fdf6f8; border: 1px solid #ecd7df; border-radius: 10px; color: #9c3a5a; font-size: 0.98em; list-style: none; }
.gd-book-toggle > summary::-webkit-details-marker { display: none; }
.gd-book-toggle > summary::before { content: '▸ '; color: #c98aa0; }
.gd-book-toggle[open] > summary::before { content: '▾ '; }
.gd-book-toggle > summary:hover { background: #fbeef2; }
.gd-body { line-height: 1.85; color: var(--read-text, #2b2b2b); font-size: var(--reading-scale, 1em); margin-top: 16px; }
.gd-body :deep(.gd-h1) { display: none; } /* tiêu đề sách đã ở hero */
.gd-body :deep(h3) { margin: 28px 0 10px; padding-top: 14px; border-top: 1px solid #eddfe4; color: #9c3a5a; font-size: 1.25em; }
.gd-body :deep(h4) { margin: 20px 0 8px; color: #7d4357; font-size: 1.08em; }
.gd-body :deep(h5) { margin: 16px 0 6px; color: #8a6d1a; font-size: 0.98em; }
.gd-body :deep(p) { margin: 12px 0; }
.gd-body :deep(blockquote) { margin: 16px 0; padding: 12px 18px; background: #fbf3f6; border-left: 3px solid #c98aa0; border-radius: 6px; color: #5d4450; font-style: italic; }
.gd-body :deep(table) { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.9em; }
.gd-body :deep(th), .gd-body :deep(td) { border: 1px solid #e6d5db; padding: 7px 10px; text-align: left; vertical-align: top; }
.gd-body :deep(th) { background: #f7e9ee; color: #7d2c47; }
.gd-body :deep(ul), .gd-body :deep(ol) { margin: 12px 0; padding-left: 22px; }
.gd-body :deep(li) { margin: 5px 0; }
.gd-body :deep(hr) { border: none; border-top: 1px dashed #d8c2c9; margin: 26px 0; }
.gd-body :deep(code) { background: #f3e8ec; padding: 1px 5px; border-radius: 4px; font-size: 0.88em; }
.gd-body :deep(strong) { color: #7d2c47; }

.gd-foot { margin-top: 28px; padding: 16px; background: #f7f3f0; border-radius: 12px; text-align: center; color: var(--read-text-faint,#777); font-size: 0.9em; }
</style>
