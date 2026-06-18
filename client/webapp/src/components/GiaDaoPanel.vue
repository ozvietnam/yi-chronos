<template>
  <div class="gd2">
    <header class="gd2-hero">
      <div class="gd2-icon">🏡</div>
      <h2>Gia Đạo</h2>
      <p class="gd2-sub">Cưới rồi — ăn ở thế nào cho hợp đạo, đón con năm nào thuận, đặt tên con ra sao.</p>
    </header>

    <div class="gd2-mode">
      <button :class="{ on: tab==='nha' }" @click="tab='nha'">🧭 Nếp nhà & đón con</button>
      <button :class="{ on: tab==='con' }" @click="tab='con'">👶 Luận lá số con</button>
      <button :class="{ on: tab==='ten' }" @click="tab='ten'">✍️ Đặt tên con</button>
      <button :class="{ on: tab==='phuc' }" @click="tab='phuc'">🏮 Phúc ấm & quan hệ</button>
    </div>

    <!-- Phúc Đức (mộ phần tổ tiên) + Nô Bộc (đối tác / lứa đôi) -->
    <section v-if="tab==='phuc'" class="gd2-card">
      <p class="gd2-sub">Đọc sâu cung Phúc Đức (phúc ấm tổ tiên) và Nô Bộc (kẻ dưới / đối tác / lứa đôi) — theo Toàn Thư cổ + góc dân gian Việt (ghi rõ nguồn).</p>
      <div class="gd2-person" style="max-width:340px;margin:0 auto;">
        <input v-model="pbirth" type="datetime-local" class="gd2-in" />
        <select v-model="pgender" class="gd2-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
      </div>
      <button class="gd2-run" :disabled="!pbirth || ploading" @click="runPhuc">{{ ploading ? '⏳ Đang đọc...' : '🏮 Đọc Phúc Đức & Nô Bộc' }}</button>
      <p v-if="perr" class="gd2-err">{{ perr }}</p>
      <div v-if="phuc" class="gd2-result">
        <div class="gd2-box" v-for="(blk,key) in {'🏮 Phúc Đức (phúc ấm tổ tiên)':phuc.phuc_duc, '🤝 Nô Bộc (đối tác / kẻ dưới / lứa đôi)':phuc.no_boc}" :key="key">
          <h5>{{ key }} — {{ blk.chinh_tinh.join(', ') || 'vô chính diệu' }}</h5>
          <ul><li v-for="(l,i) in blk.luan_co_van" :key="i">{{ l }}</li></ul>
          <div class="gd2-viet">
            <b>🇻🇳 Góc dân gian Việt:</b> {{ blk.goc_dan_gian_viet.noi_dung }}
            <div class="gd2-nguon">Nguồn: {{ blk.goc_dan_gian_viet.nguon }}</div>
          </div>
          <p class="gd2-note">{{ blk.paradigm }}</p>
        </div>
      </div>
    </section>

    <!-- Nếp nhà + năm đón con (cặp) -->
    <section v-if="tab==='nha'" class="gd2-card">
      <div class="gd2-form">
        <div class="gd2-person">
          <h4>Chồng</h4>
          <input v-model="h.ten" placeholder="Tên" class="gd2-in" />
          <input v-model="h.birth" type="datetime-local" class="gd2-in" />
          <select v-model="h.gender" class="gd2-in"><option value="nam">Nam</option><option value="nữ">Nữ</option></select>
        </div>
        <div class="gd2-person">
          <h4>Vợ</h4>
          <input v-model="w.ten" placeholder="Tên" class="gd2-in" />
          <input v-model="w.birth" type="datetime-local" class="gd2-in" />
          <select v-model="w.gender" class="gd2-in"><option value="nữ">Nữ</option><option value="nam">Nam</option></select>
        </div>
      </div>
      <button class="gd2-run" :disabled="!h.birth || !w.birth || loading" @click="runNha">
        {{ loading ? '⏳ Đang xem...' : '🧭 Xem nếp nhà & năm đón con' }}
      </button>
      <p v-if="err" class="gd2-err">{{ err }}</p>

      <div v-if="nha" class="gd2-result">
        <div class="gd2-box">
          <h5>📜 Gia quy ăn ở hợp đạo</h5>
          <ol><li v-for="(g,i) in nha.gia_quy.gia_quy" :key="i">{{ g }}</li></ol>
          <p class="gd2-note">{{ nha.gia_quy.tinh_than }}</p>
        </div>
        <div class="gd2-box">
          <h5>🍼 Năm thuận đón con ({{ nha.nam_sinh_con.tu_nam }}–{{ nha.nam_sinh_con.den_nam }})</h5>
          <div v-if="nha.nam_sinh_con.nam.length" class="gd2-years">
            <span v-for="(y,i) in nha.nam_sinh_con.nam" :key="i" class="gd2-year"><b>{{ y.nam }}</b> <small>({{ y.cung.join('/') }} · {{ y.sao }})</small></span>
          </div>
          <p v-else class="gd2-note">Không có năm sao hỉ nổi bật — cứ thuận theo sức khỏe & kế hoạch của hai vợ chồng.</p>
          <p class="gd2-note">{{ nha.nam_sinh_con.ghi_chu }}</p>
        </div>
      </div>
    </section>

    <!-- Luận lá số con cái -->
    <section v-if="tab==='con'" class="gd2-card">
      <p class="gd2-sub">Nhập ngày + giờ sinh của bé. Thêm ngày sinh Bố/Mẹ → đối chiếu <b>trường năng lượng</b>
        (con = năng lượng lúc sinh ⊗ gen bố mẹ ⊗ môi trường) để biết hướng <b>nuôi dưỡng</b>.
        Đọc cái NỀN bé được trao, KHÔNG phán định đời bé.</p>
      <div class="gd2-form">
        <div class="gd2-person">
          <h4>👶 Con</h4>
          <input v-model="con.birth" type="datetime-local" class="gd2-in" />
          <select v-model="con.gender" class="gd2-in"><option value="nam">Bé trai</option><option value="nữ">Bé gái</option></select>
        </div>
        <div class="gd2-person">
          <h4>Bố / Mẹ <small>(tuỳ chọn — để đối chiếu trường khí)</small></h4>
          <label class="gd2-lbl">Bố — ngày sinh</label>
          <input v-model="con.bo" type="date" class="gd2-in" />
          <label class="gd2-lbl">Mẹ — ngày sinh</label>
          <input v-model="con.me" type="date" class="gd2-in" />
        </div>
      </div>
      <button class="gd2-run" :disabled="!con.birth || lloading" @click="runLuanCon">
        {{ lloading ? '⏳ Đang luận...' : '👶 Luận lá số con' }}
      </button>
      <p v-if="lerr" class="gd2-err">{{ lerr }}</p>

      <div v-if="luancon" class="gd2-result">
        <div v-if="luancon.bat_tu && luancon.bat_tu.nhat_chu" class="gd2-box gd2-hanh">
          <h5>🌱 Hướng nuôi dưỡng (theo Bát Tự bé)</h5>
          <p class="gd2-mini">Nhật chủ bé: <b>{{ luancon.bat_tu.nhat_chu }}</b> ({{ luancon.bat_tu.nhat_chu_hanh }})
            · thân {{ luancon.bat_tu.than }} · hành con cần: <b>{{ luancon.bat_tu.hanh_con_can.join(', ') }}</b></p>
          <p class="gd2-mini">{{ luancon.bat_tu.huong_nuoi }}</p>
        </div>

        <div v-if="luancon.truong_bo_me" class="gd2-box">
          <h5>👨‍👩‍👧 Trường năng lượng Bố Mẹ ⊗ cái con cần ({{ luancon.truong_bo_me.con_can }})</h5>
          <ul>
            <li v-for="(x,i) in luancon.truong_bo_me.doi_chieu" :key="i">
              <b>{{ x.vai }}</b> ({{ x.hanh }}) — <span v-html="md(x.loi)"></span>
            </li>
          </ul>
          <p class="gd2-note">{{ luancon.truong_bo_me.ghi_chu }}</p>
        </div>

        <div v-for="(c,i) in luancon.cung" :key="i" class="gd2-box">
          <h5>{{ c.cung }}
            <small v-if="!c.vo_chinh_dieu">— {{ c.chinh_tinh.join(', ') }}</small>
            <small v-else>— vô chính diệu</small>
          </h5>
          <p class="gd2-mini"><b>Khí chất:</b> {{ c.khi_chat }}</p>
          <p class="gd2-mini"><b>Hướng dìu:</b> {{ c.nuoi }}</p>
        </div>

        <div v-if="luancon.van_tinh" class="gd2-box gd2-hanh">
          <h5>📚 Văn tinh — duyên học</h5>
          <p class="gd2-mini">{{ luancon.van_tinh.luan }}</p>
        </div>

        <p class="gd2-note">{{ luancon.paradigm }}</p>
      </div>
    </section>

    <!-- Đặt tên con -->
    <section v-if="tab==='ten'" class="gd2-card">
      <p class="gd2-sub">Nhập ngày + giờ sinh của bé — hệ thống tính Bát Tự, tìm hành bé cần (dụng thần) và gợi ý chữ/tên.</p>
      <div class="gd2-person" style="max-width:340px;margin:0 auto;">
        <input v-model="cbirth" type="datetime-local" class="gd2-in" />
      </div>
      <button class="gd2-run" :disabled="!cbirth || tloading" @click="runTen">
        {{ tloading ? '⏳ Đang tính...' : '👶 Gợi ý tên cho bé' }}
      </button>
      <p v-if="terr" class="gd2-err">{{ terr }}</p>

      <div v-if="ten" class="gd2-result">
        <div class="gd2-box">
          <p class="gd2-mini">Nhật chủ bé: <b>{{ ten.nhat_chu }}</b> ({{ ten.nhat_chu_hanh }}) · thân {{ ten.than }} · thiếu nhất: <b>{{ ten.hanh_thieu_nhat }}</b></p>
          <p class="gd2-mini">Hành nên bổ (dụng thần): <b>{{ ten.hanh_nen_bo.join(', ') }}</b></p>
        </div>
        <div v-for="(g,i) in ten.goi_y_ten" :key="i" class="gd2-box gd2-hanh">
          <h5>{{ g.hanh }} — {{ g.y_nghia }}</h5>
          <p class="gd2-mini">Bộ thủ: {{ g.bo_thu }}</p>
          <div class="gd2-names"><span v-for="(t,j) in g.goi_y" :key="j" class="gd2-name">{{ t }}</span></div>
        </div>
        <p class="gd2-note">{{ ten.ghi_chu }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { activeBirthDatetime } from "../stores/userDataStore.js";

const tab = ref("nha");
const h = ref({ ten: "Chồng", birth: "", gender: "nam" });
const w = ref({ ten: "Vợ", birth: "", gender: "nữ" });
const nha = ref(null); const loading = ref(false); const err = ref("");
const cbirth = ref(""); const ten = ref(null); const tloading = ref(false); const terr = ref("");
const pbirth = ref(""); const pgender = ref("nam"); const phuc = ref(null); const ploading = ref(false); const perr = ref("");
const con = ref({ birth: "", gender: "nam", bo: "", me: "" });
const luancon = ref(null); const lloading = ref(false); const lerr = ref("");
// đổi **đậm** → <b> (loi do server sinh, không phải input user → an toàn v-html)
function md(s) { return String(s || "").replace(/\*\*(.+?)\*\*/g, "<b>$1</b>"); }
async function runLuanCon() {
  if (!con.value.birth) return;
  lloading.value = true; lerr.value = ""; luancon.value = null;
  try {
    const r = await fetch("/api/tu-vi/luan-con", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth_con: con.value.birth, gender_con: con.value.gender,
        bo_birth: con.value.bo || null, me_birth: con.value.me || null,
      }),
    });
    const d = await r.json();
    if (d.error) lerr.value = d.error; else luancon.value = d;
  } catch (e) { lerr.value = "Lỗi kết nối."; } finally { lloading.value = false; }
}
async function runPhuc() {
  if (!pbirth.value) return;
  ploading.value = true; perr.value = ""; phuc.value = null;
  try {
    const r = await fetch("/api/tu-vi/cung-sau", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ birth: pbirth.value, gender: pgender.value }),
    });
    const d = await r.json();
    if (d.error) perr.value = d.error; else phuc.value = d;
  } catch (e) { perr.value = "Lỗi kết nối."; } finally { ploading.value = false; }
}

onMounted(() => {
  const bd = activeBirthDatetime?.value;
  if (bd) { h.value.birth = String(bd).slice(0, 16); pbirth.value = String(bd).slice(0, 16); }
});

async function runNha() {
  if (!h.value.birth || !w.value.birth) return;
  loading.value = true; err.value = ""; nha.value = null;
  try {
    const r = await fetch("/api/tu-vi/gia-dao", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        birth1: h.value.birth, gender1: h.value.gender, ten1: h.value.ten || "Chồng",
        birth2: w.value.birth, gender2: w.value.gender, ten2: w.value.ten || "Vợ",
      }),
    });
    const d = await r.json();
    if (d.error) err.value = d.error; else nha.value = d;
  } catch (e) { err.value = "Lỗi kết nối."; } finally { loading.value = false; }
}

async function runTen() {
  if (!cbirth.value) return;
  tloading.value = true; terr.value = ""; ten.value = null;
  try {
    const r = await fetch("/api/tu-vi/dat-ten", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ birth_con: cbirth.value }),
    });
    const d = await r.json();
    if (d.error) terr.value = d.error; else ten.value = d;
  } catch (e) { terr.value = "Lỗi kết nối."; } finally { tloading.value = false; }
}
</script>

<style scoped>
.gd2 { max-width: 720px; margin: 0 auto; padding: 14px; }
.gd2-hero { text-align: center; padding: 24px 16px 18px; background: linear-gradient(160deg,#f3f9f3,#eef6ee); border: 1px solid #c9e0c9; border-radius: 16px; margin-bottom: 18px; }
.gd2-icon { font-size: 2.2em; }
.gd2-hero h2 { margin: 6px 0 4px; color: #2e7d32; font-size: 1.7em; }
.gd2-sub { margin: 4px 0; color: #5a6a55; font-size: 0.92em; }
.gd2-mode { display: flex; gap: 10px; justify-content: center; margin-bottom: 16px; }
.gd2-mode button { flex: 1; max-width: 240px; padding: 11px; border: 1.5px solid #b2d4b2; border-radius: 22px; background: transparent; color: #2e7d32; font: inherit; cursor: pointer; transition: all .15s; }
.gd2-mode button.on { background: #2e7d32; color: #fff; border-color: #2e7d32; }
.gd2-card { padding: 20px; background: var(--read-surface,#fff); border: 1px solid #d4e6d4; border-radius: 14px; }
.gd2-form { display: flex; gap: 12px; flex-wrap: wrap; }
.gd2-person { flex: 1; min-width: 200px; display: flex; flex-direction: column; gap: 8px; padding: 12px; background: #f5faf5; border-radius: 10px; }
.gd2-person h4 { margin: 0 0 2px; color: #2e7d32; font-size: 0.95em; }
.gd2-in { padding: 8px 10px; border: 1px solid #c6dcc6; border-radius: 8px; font: inherit; font-size: 0.9em; background: #fff; color: #333; }
.gd2-lbl { font-size: 0.78em; color: #5a6a55; margin: 2px 0 -4px; }
.gd2-box ul { margin: 0; padding-left: 18px; } .gd2-box li { margin: 6px 0; font-size: 0.9em; line-height: 1.55; color: var(--read-text,#3a3a38); }
.gd2-run { display: block; width: 100%; margin-top: 14px; padding: 12px; border: none; border-radius: 22px; background: #2e7d32; color: #fff; font: inherit; font-size: 1em; cursor: pointer; }
.gd2-run:disabled { opacity: .5; cursor: not-allowed; }
.gd2-err { color: #c0392b; text-align: center; margin-top: 10px; }
.gd2-result { margin-top: 18px; }
.gd2-box { margin: 12px 0; padding: 14px 16px; background: #f5faf5; border: 1px solid #d4e6d4; border-radius: 12px; }
.gd2-box h5 { margin: 0 0 8px; color: #2e7d32; }
.gd2-box ol { margin: 0; padding-left: 20px; } .gd2-box li { margin: 6px 0; font-size: 0.9em; line-height: 1.55; color: var(--read-text,#3a3a38); }
.gd2-mini { margin: 4px 0; font-size: 0.9em; color: #4a5a45; } .gd2-mini b { color: #2e7d32; }
.gd2-note { margin: 8px 0 0; font-size: 0.82em; font-style: italic; color: var(--read-text-faint,#888); line-height: 1.5; }
.gd2-years { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0; }
.gd2-year { padding: 5px 12px; background: #eef9f0; border: 1px solid #b6dfc0; border-radius: 16px; font-size: 0.88em; } .gd2-year b { color: #2e7d32; }
.gd2-hanh h5 { color: #8a6d1a; }
.gd2-names { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.gd2-name { padding: 6px 14px; background: #fff; border: 1px solid #d4af37; border-radius: 16px; color: #6a5212; font-size: 0.95em; }
.gd2-viet { margin: 10px 0 4px; padding: 10px 12px; background: #fff8ee; border: 1px solid #e6cfa0; border-radius: 8px; font-size: 0.86em; color: #6a5212; line-height: 1.55; }
.gd2-nguon { margin-top: 4px; font-size: 0.82em; font-style: italic; color: #9a7a3a; }
</style>
