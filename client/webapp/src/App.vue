<script setup>
import { computed, defineAsyncComponent, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { Activity, Database, RotateCcw, Send, ShieldCheck } from "lucide-vue-next";
import SchoolIcon from "./components/SchoolIcon.vue";
import NavDropdown from "./components/NavDropdown.vue";
import UserBadge from "./components/UserBadge.vue";
import OnboardingModal from "./components/OnboardingModal.vue";
const AdminPanel = defineAsyncComponent(() => import("./components/AdminPanel.vue"));
const HermesAdminPanel = defineAsyncComponent(() => import("./components/HermesAdminPanel.vue"));
const MyPublicationsPanel = defineAsyncComponent(() => import("./components/MyPublicationsPanel.vue"));
import WikiPopup from "./components/WikiPopup.vue";
import { isOwner } from "./stores/authStore.js";
import { activePerson, activeBirthDatetime, personLabel } from "./stores/userDataStore.js";
import ReadingControls from "./components/ReadingControls.vue";
import { useReadingPrefs } from "./composables/useReadingPrefs.js";
const UniverseCore = defineAsyncComponent(() => import("./components/UniverseCore.vue"));
const MaiHoaClock3D = defineAsyncComponent(() => import("./components/MaiHoaClock3D.vue"));
const LucHaoResultPage = defineAsyncComponent(() => import("./components/LucHaoResultPage.vue"));
const ThanSoPanel = defineAsyncComponent(() => import("./components/ThanSoPanel.vue"));
const EnergyWeatherPanel = defineAsyncComponent(() => import("./components/EnergyWeatherPanel.vue"));
const PersonalResonance = defineAsyncComponent(() => import("./components/PersonalResonance.vue"));
const FeedbackPanel = defineAsyncComponent(() => import("./components/FeedbackPanel.vue"));
const ZiweiOrbitPanel = defineAsyncComponent(() => import("./components/ZiweiOrbitPanel.vue"));
const SkyChartPanel = defineAsyncComponent(() => import("./components/SkyChartPanel.vue"));
const LifeTimelinePanel = defineAsyncComponent(() => import("./components/LifeTimelinePanel.vue"));
const TransitTimelinePanel = defineAsyncComponent(() => import("./components/TransitTimelinePanel.vue"));
const SolarReturnsPanel = defineAsyncComponent(() => import("./components/SolarReturnsPanel.vue"));
const ProgressionsPanel = defineAsyncComponent(() => import("./components/ProgressionsPanel.vue"));
const LunarReturnsPanel = defineAsyncComponent(() => import("./components/LunarReturnsPanel.vue"));
const SolarArcPanel = defineAsyncComponent(() => import("./components/SolarArcPanel.vue"));
const EclipsesPanel = defineAsyncComponent(() => import("./components/EclipsesPanel.vue"));
const YiTimelineNarrativePanel = defineAsyncComponent(() => import("./components/YiTimelineNarrativePanel.vue"));
const YiDiepPanel = defineAsyncComponent(() => import("./components/YiDiepPanel.vue"));
const PersonalQuaiPanel = defineAsyncComponent(() => import("./components/PersonalQuaiPanel.vue"));
const GPSPanel = defineAsyncComponent(() => import("./components/GPSPanel.vue"));
const FamilySystemPanel = defineAsyncComponent(() => import("./components/FamilySystemPanel.vue"));
const GieoDuyenPanel = defineAsyncComponent(() => import("./components/GieoDuyenPanel.vue"));
const GiaDaoPanel = defineAsyncComponent(() => import("./components/GiaDaoPanel.vue"));
const ProfilesPanel = defineAsyncComponent(() => import("./components/ProfilesPanel.vue"));
import TabIntro from "./components/TabIntro.vue";
const LienHoaPanel = defineAsyncComponent(() => import("./components/LienHoaPanel.vue"));
const BatTuPanel = defineAsyncComponent(() => import("./components/BatTuPanel.vue"));
const HealthPanel = defineAsyncComponent(() => import("./components/HealthPanel.vue"));
const KyMonPanel = defineAsyncComponent(() => import("./components/KyMonPanel.vue"));
const HoangCucPanel = defineAsyncComponent(() => import("./components/HoangCucPanel.vue"));
const ChinhTinhLibraryPanel = defineAsyncComponent(() => import("./components/ChinhTinhLibraryPanel.vue"));
const NguCucLibraryPanel = defineAsyncComponent(() => import("./components/NguCucLibraryPanel.vue"));
const ThanMenhLibraryPanel = defineAsyncComponent(() => import("./components/ThanMenhLibraryPanel.vue"));
const VongSaoLibraryPanel = defineAsyncComponent(() => import("./components/VongSaoLibraryPanel.vue"));
const TuViLaSoPanel = defineAsyncComponent(() => import("./components/TuViLaSoPanel.vue"));
const DangSonPanel = defineAsyncComponent(() => import("./components/DangSonPanel.vue"));
const CungPhuTheBacPhaiPanel = defineAsyncComponent(() => import("./components/CungPhuTheBacPhaiPanel.vue"));
const ChieuDomKinhPanel = defineAsyncComponent(() => import("./components/ChieuDomKinhPanel.vue"));
const YiHermesChat = defineAsyncComponent(() => import("./components/YiHermesChat.vue"));
const HoiHermesPanel = defineAsyncComponent(() => import("./components/HoiHermesPanel.vue"));
const ChanDungPanel = defineAsyncComponent(() => import("./components/ChanDungPanel.vue"));
const DeepReadingPanel = defineAsyncComponent(() => import("./components/DeepReadingPanel.vue"));
const AtomVerifyPanel = defineAsyncComponent(() => import("./components/AtomVerifyPanel.vue"));
const LexiconPanel = defineAsyncComponent(() => import("./components/LexiconPanel.vue"));
const SettingsPanel = defineAsyncComponent(() => import("./components/SettingsPanel.vue"));
const ResearchPanel = defineAsyncComponent(() => import("./components/ResearchPanel.vue"));
const MasterView = defineAsyncComponent(() => import("./components/wiki/MasterView.vue"));
import QuickTasksPanel from "./components/QuickTasksPanel.vue";
const MaiHoaCastPanel = defineAsyncComponent(() => import("./components/wiki/MaiHoaCastPanel.vue"));
const KinhDichBrowser = defineAsyncComponent(() => import("./components/wiki/KinhDichBrowser.vue"));
const KinhDichGraph = defineAsyncComponent(() => import("./components/wiki/KinhDichGraph.vue"));
const HaoSpacedRepetition = defineAsyncComponent(() => import("./components/wiki/HaoSpacedRepetition.vue"));
const LuuVanDashboard = defineAsyncComponent(() => import("./components/wiki/LuuVanDashboard.vue"));
const NhatKyVanPanel = defineAsyncComponent(() => import("./components/wiki/NhatKyVanPanel.vue"));
const LuuNguyetTimeline = defineAsyncComponent(() => import("./components/wiki/LuuNguyetTimeline.vue"));
const RestoredLibrary = defineAsyncComponent(() => import("./components/library/RestoredLibrary.vue"));
// DailyHexagramPanel: DEPRECATED 2026-05-27 đêm — paradigm SAI (horoscope-style).
// Thay bằng LuuVanDashboard (7 vòng quẻ đúng paradigm Khang Tiết).
// import DailyHexagramPanel from "./components/wiki/DailyHexagramPanel.vue";
const CrossCastPanel = defineAsyncComponent(() => import("./components/wiki/CrossCastPanel.vue"));
const PublishingWorkspace = defineAsyncComponent(() => import("./components/publishing/PublishingWorkspace.vue"));
const LibraryView = defineAsyncComponent(() => import("./components/publishing/LibraryView.vue"));
import { applyBirthFromUrlOnMount } from "./composables/useBirthShare.js";
import { getActiveRuleset, getNatalUniverse, getPlanetPositions, getUniverseNow, submitFeedback, submitPersonalProfile } from "./lib/api";
import {
  createEmptyProfile,
  loadProfilesState,
  persistProfilesState,
  toPersonalProfileApiPayload
} from "./lib/profilesStorage";

const { profiles: profilesInitial, activeId: profilesActiveInitial } = loadProfilesState();
const profiles = ref(profilesInitial);
const activeProfileId = ref(profilesActiveInitial);

const universe = ref(null);
const planetPositions = ref(null);
const personal = ref(null);
const feedbackStatus = ref("");
const error = ref("");
const loadingUniverse = ref(false);

// Lá số trên nền vũ trụ thật (natal mode cho UniverseCore)
const natalData = ref(null);
const natalLoading = ref(false);
const natalError = ref("");
async function loadNatal() {
  const at = activeBirthDatetime.value;
  if (!at) {
    natalError.value = "Chưa có ngày sinh — chọn người ở hồ sơ trước.";
    return;
  }
  natalLoading.value = true;
  natalError.value = "";
  try {
    natalData.value = await getNatalUniverse({ at });
  } catch (err) {
    natalError.value = err?.message || String(err);
  } finally {
    natalLoading.value = false;
  }
}
function clearNatal() {
  natalData.value = null;
}
const activeRuleset = ref(null);
const SCHOOL_VI = { bac_phai: "Bắc phái", nam_phai: "Nam phái", trung_chau: "Trung Châu", dang_son: "Đằng Sơn", tu_vi_bon_ba: "Bôn Ba", tu_vi_huy_tuan: "Huy Tuấn" };
// Nhãn pill phái: dịch + DEDUPE (school == ruleset_id thì hiện 1, tránh "bac_phai · bac_phai")
const rulesetPill = computed(() => {
  const r = activeRuleset.value;
  if (!r || !r.ziwei_school) return "";
  const school = SCHOOL_VI[r.ziwei_school] || r.ziwei_school;
  let rid = r.ziwei_ruleset_id || "";
  // Bỏ tiền tố trùng tên phái (bac_phai_v1 → v1) để pill gọn: "Bắc phái · v1"
  if (rid.startsWith(r.ziwei_school)) rid = rid.slice(r.ziwei_school.length).replace(/^_/, "");
  return rid ? `${school} · ${rid}` : school;
});
const now = ref(new Date());
const selectedTimeZone = ref("Asia/Ho_Chi_Minh");
const activeMainTab = ref("profiles");

// Thư viện chia 2 sub-tab song song: 🔯 Tử Vi (sao/cung/cục) ⟷ 📚 Sách phục chế.
const libSubTab = ref("tu-vi");
// Hợp nhất 1 nơi tra sao: lá số bấm "📖 sao" → chuyển tab Thư viện + mở đúng sao.
const tuviLibRef = ref(null);
async function openLibraryStar(sao) {
  activeMainTab.value = "library";
  libSubTab.value = "tu-vi";   // mở đúng sub-tab Tử Vi
  await nextTick();
  let tries = 0;
  const tryOpen = () => {
    if (tuviLibRef.value?.openToStar) tuviLibRef.value.openToStar(sao);
    else if (tries++ < 20) setTimeout(tryOpen, 80);   // chờ async component render
  };
  tryOpen();
}

// Cấu trúc nav — gom mỗi nhóm vào 1 dropdown (menu xổ). Data-driven cho gọn.
const NAV_GROUPS = [
  { label: "Dữ liệu", tabs: [
    { id: "profiles", icon: "profiles", label: "Hồ sơ" },
    { id: "my-publications", icon: "my-publications", label: "Kết quả" },
  ] },
  { label: "Hermes", tabs: [
    { id: "chan-dung", icon: "chan-dung", label: "Chân Dung" },
    { id: "hoi-hermes", icon: "hoi-hermes", label: "Hỏi Hermes" },
  ] },
  { label: "Trường phái", tabs: [
    { id: "universe", icon: "universe", label: "Vũ trụ hiện tại" },
    { id: "western", icon: "western", label: "Chiêm tinh Tây" },
    { id: "maihoa", icon: "maihoa", label: "Mai Hoa" },
    { id: "luc-hao", icon: "luc-hao", label: "Lục Hào" },
    { id: "lien-hoa", icon: "lien-hoa", label: "Liên Hoa" },
    { id: "bat-tu", icon: "bat-tu", label: "Bát Tự" },
    { id: "tu-vi", icon: "tu-vi", label: "Tử Vi" },
    { id: "ky-mon", icon: "ky-mon", label: "Kỳ Môn" },
    { id: "pytago", icon: "pytago", label: "Pytago" },
    { id: "hoang-cuc", icon: "hoang-cuc", label: "Hoàng Cực" },
  ] },
  { label: "Tổng hợp", tabs: [
    { id: "library", icon: "library", label: "Thư viện" },
    { id: "gieo-duyen", icon: "gieo-duyen", label: "Gieo Duyên" },
    { id: "family", icon: "family", label: "Gia đạo" },
    { id: "gps", icon: "gps", label: "GPS" },
    { id: "health", icon: "health", label: "Sức khỏe" },
    { id: "settings", icon: "settings", label: "Cài đặt" },
  ] },
];
const NAV_DEV = { label: "Kiến thức · Dev", tabs: [
  { id: "lexicon", icon: "lexicon", label: "Lexicon" },
  { id: "research", icon: "research", label: "Research" },
  { id: "wiki", icon: "wiki", label: "Wiki Tổ sư" },
  { id: "publishing", icon: "publishing", label: "Dịch sách" },
  { id: "admin", icon: "admin", label: "Admin" },
  { id: "admin-hermes", icon: "admin-hermes", label: "Quản trị Hermes" },
  { id: "atom-verify", icon: "atom-verify", label: "Duyệt Atoms" },
] };

// 🔒 Chặn user thường lạc vào tab owner-only. Nav đã ẩn nhóm Dev (v-if isOwner);
// đây là LỚP 2: nếu state cũ / điều hướng lập trình đưa user tới tab admin → kéo về Hồ sơ.
const OWNER_ONLY_TABS = NAV_DEV.tabs.map((t) => t.id);
watch([isOwner, activeMainTab], () => {
  if (!isOwner.value && OWNER_ONLY_TABS.includes(activeMainTab.value)) {
    activeMainTab.value = "profiles";
  }
}, { immediate: true });
// Chân Dung → bấm sản phẩm tốt nhất → nhảy tab tương ứng (deep tạm về Hội Đồng — luận sâu nhất hiện có)
function onOpenProduct(key) {
  const map = { council: "hoi-hermes", deep: "deep-reading", duyen: "gieo-duyen" };
  activeMainTab.value = map[key] || "hoi-hermes";
}
// Chân Dung → nhảy sang TRANG CHUYÊN GIA luận sâu (Bát Tự 'bat-tu' / Tử Vi 'tu-vi' / Thần Số 'pytago')
function onOpenPage(tab) {
  activeMainTab.value = tab;
  if (typeof window !== "undefined") window.scrollTo({ top: 0, behavior: "smooth" });
}
// Publishing tab state: null = Library gallery, "<book_id>" = Workspace
const publishingSelectedBook = ref(null);
function openBookInWorkspace(bookId) { publishingSelectedBook.value = bookId; }
function backToLibrary() { publishingSelectedBook.value = null; }
const activeTuViSchool = ref("bac-phai");
const latestLucHaoResult = ref(null);
const latestLucHaoMeta = ref(null);
const urlBirthBanner = ref(null);
const urlBirthBannerDismissed = ref(false);
let clockTimer;
let universeRefreshTimer;

const selectedPrompt = computed(() => personal.value?.milestone_prompts?.[0] || null);
const activeUniverseProfile = computed(
  () => profiles.value.find((p) => p.id === activeProfileId.value) ?? null
);
const timeZoneOptions = computed(() => {
  if (typeof Intl.supportedValuesOf === "function") {
    return Intl.supportedValuesOf("timeZone");
  }
  return [
    "Asia/Ho_Chi_Minh",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Europe/London",
    "Europe/Paris",
    "America/New_York",
    "America/Los_Angeles",
    "Australia/Sydney",
    "UTC"
  ];
});

function formatClock(date, timeZone, withDate = false) {
  return new Intl.DateTimeFormat("vi-VN", {
    timeZone,
    weekday: withDate ? "short" : undefined,
    year: withDate ? "numeric" : undefined,
    month: withDate ? "2-digit" : undefined,
    day: withDate ? "2-digit" : undefined,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  }).format(date);
}

const selectedClock = computed(() => formatClock(now.value, selectedTimeZone.value, true));
const hanoiClock = computed(() => formatClock(now.value, "Asia/Ho_Chi_Minh"));
const utcClock = computed(() => formatClock(now.value, "UTC"));

async function loadUniverse() {
  loadingUniverse.value = true;
  error.value = "";
  try {
    const [universePayload, planetsPayload, rulesetPayload] = await Promise.all([
      getUniverseNow(),
      getPlanetPositions(),
      getActiveRuleset()
    ]);
    universe.value = universePayload;
    planetPositions.value = planetsPayload;
    activeRuleset.value = rulesetPayload;
  } catch (err) {
    error.value = "Không thể tải Trạng thái vũ trụ. Hãy kiểm tra backend FastAPI.";
  } finally {
    loadingUniverse.value = false;
  }
}

function persistProfiles() {
  persistProfilesState({
    profiles: profiles.value.map((p) => ({ ...p })),
    activeId: activeProfileId.value
  });
}

function onProfileSelect(id) {
  activeProfileId.value = id;
  persistProfiles();
}

function onProfileCreate() {
  const p = createEmptyProfile();
  profiles.value = [...profiles.value, p];
  activeProfileId.value = p.id;
  persistProfiles();
}

async function handleProfileSubmit(form) {
  error.value = "";
  feedbackStatus.value = "";
  try {
    const payload = toPersonalProfileApiPayload(form);
    // Guard: chưa có sinh thần (guest / chưa chọn hồ sơ) → đừng gọi (tránh 500)
    if (!payload || !(payload.birth_datetime_local || "").trim()) {
      personal.value = null;
      return;
    }
    personal.value = await submitPersonalProfile(payload);
    const ix = profiles.value.findIndex((p) => p.id === activeProfileId.value);
    if (ix >= 0) {
      const cur = profiles.value[ix];
      const label =
        typeof form.profile_label === "string" && form.profile_label.trim() !== ""
          ? form.profile_label.trim()
          : cur.label;
      const next = {
        ...cur,
        label,
        birth_datetime_local: payload.birth_datetime_local,
        timezone: payload.timezone,
        location_ref: form.location_ref || "",
        birth_precision: payload.birth_precision,
        gender_optional: payload.gender_optional
      };
      profiles.value.splice(ix, 1, next);
    }
    persistProfiles();
  } catch (_err) {
    error.value = "Không thể tính cộng hưởng cá nhân với dữ liệu hiện tại.";
  }
}

/** Lần đầu mở app: tính cộng hưởng với hồ sơ mặc định (Lại Minh Thắng) để test luồng. */
async function bootstrapPersonalProfile() {
  const p = profiles.value.find((x) => x.id === activeProfileId.value);
  if (!p) return;
  await handleProfileSubmit({ ...p, profile_label: p.label });
}

async function handleFeedbackSubmit(payload) {
  error.value = "";
  feedbackStatus.value = "";
  try {
    const result = await submitFeedback(payload);
    feedbackStatus.value = `Đã lưu phản hồi ${result.feedback_id.slice(0, 10)}`;
  } catch (err) {
    error.value = "Không thể lưu phản hồi. Vui lòng thử lại.";
  }
}

async function copyDiagnostics() {
  const diagnostics = {
    generated_at_utc: new Date().toISOString(),
    algorithm_version: activeRuleset.value?.algorithm_version || universe.value?.algorithm_version || "unknown",
    ziwei_school: activeRuleset.value?.ziwei_school || universe.value?.ziwei_school || "unknown",
    ziwei_ruleset_id: activeRuleset.value?.ziwei_ruleset_id || universe.value?.ziwei_ruleset_id || "unknown",
    ziwei_ruleset_label: activeRuleset.value?.ziwei_ruleset_label || universe.value?.ziwei_ruleset_label || "unknown",
    universe_timestamp_utc: universe.value?.timestamp_utc || null,
    planet_source: planetPositions.value?.source || null,
    planet_stale: planetPositions.value?.stale ?? null
  };
  try {
    await navigator.clipboard.writeText(JSON.stringify(diagnostics, null, 2));
    feedbackStatus.value = "Đã copy diagnostics vào clipboard.";
  } catch (err) {
    error.value = "Không thể copy diagnostics. Trình duyệt có thể chặn clipboard.";
  }
}

function handleLucHaoCastResult(payload) {
  latestLucHaoResult.value = payload.result;
  latestLucHaoMeta.value = payload.meta;
}

const { startReadingPrefs } = useReadingPrefs();

// ActivePersonBar "Đổi người / Nhập ở tab Hồ sơ" → chuyển sang tab quản lý hồ sơ.
function onNavTab(e) {
  const tab = e?.detail;
  if (typeof tab === "string" && tab) activeMainTab.value = tab;
}

onMounted(() => {
  startReadingPrefs(); // apply saved reading theme + text scale to <html>
  window.addEventListener("yi-nav-tab", onNavTab);
  clockTimer = window.setInterval(() => {
    now.value = new Date();
  }, 1000);
  universeRefreshTimer = window.setInterval(() => {
    loadUniverse();
  }, 120000);

  // ?birth=YYYY-MM-DD-HH-{nam|nu} — kabala-compatible URL share contract.
  // If URL has a valid birth slug and no active person is set, create an
  // ephemeral URL-driven person and activate it.
  const urlBirth = applyBirthFromUrlOnMount();
  if (urlBirth) {
    urlBirthBanner.value = urlBirth;
  }

  void (async () => {
    await loadUniverse();
    await bootstrapPersonalProfile();
  })();
});

onBeforeUnmount(() => {
  window.removeEventListener("yi-nav-tab", onNavTab);
  window.clearInterval(clockTimer);
  window.clearInterval(universeRefreshTimer);
});
</script>

<template>
  <main class="app-shell">
    <aside class="system-rail" aria-label="Hệ thống">
      <div class="brand-mark">YC</div>
      <button class="icon-button active" title="Trạng thái vũ trụ" aria-label="Trạng thái vũ trụ">
        <Activity :size="20" />
      </button>
      <button class="icon-button" title="Dữ liệu phản hồi" aria-label="Dữ liệu phản hồi">
        <Database :size="20" />
      </button>
      <button class="icon-button" title="An toàn" aria-label="An toàn">
        <ShieldCheck :size="20" />
      </button>
    </aside>

    <section class="workspace">
      <header class="topbar-v2">
        <div class="topbar-brand">
          <div class="brand-glyph">
            <SchoolIcon name="chronos" :size="22" />
          </div>
          <div class="topbar-brand-text">
            <h1>YI-CHRONOS</h1>
            <p>
              Hệ mô hình hóa trạng thái thời gian
              <span v-if="rulesetPill" class="ruleset-pill">{{ rulesetPill }}</span>
            </p>
          </div>
        </div>

        <div class="topbar-clocks" aria-label="Đồng hồ thời gian thực">
          <div class="clock-chip">
            <span>Khu vực</span>
            <select v-model="selectedTimeZone" class="clock-tz-select">
              <option v-for="zone in timeZoneOptions" :key="zone" :value="zone">{{ zone }}</option>
            </select>
            <strong>{{ selectedClock }}</strong>
          </div>
          <div class="clock-chip secondary">
            <span>Hà Nội</span>
            <strong>{{ hanoiClock }}</strong>
          </div>
          <div class="clock-chip secondary">
            <span>UTC</span>
            <strong>{{ utcClock }}</strong>
          </div>
        </div>

        <div class="topbar-actions">
          <UserBadge />
          <button class="refresh-button" type="button" @click="loadUniverse" :title="loadingUniverse ? 'Đang tải dữ liệu vũ trụ' : 'Tải lại dữ liệu vũ trụ'">
            <RotateCcw :size="16" :class="{ spinning: loadingUniverse }" />
            <span>{{ loadingUniverse ? "Đang tải" : "Làm mới" }}</span>
          </button>
          <button v-if="isOwner" class="diag-button" type="button" @click="copyDiagnostics" title="Copy thông tin debug (owner only)">
            ⚙
          </button>
        </div>
      </header>

      <!-- ?birth= URL banner -->
      <div
        v-if="urlBirthBanner && !urlBirthBannerDismissed"
        class="url-birth-banner"
        role="status"
        aria-live="polite"
      >
        <span class="url-birth-icon">🔗</span>
        <p>
          Đã đọc sinh thần từ URL —
          <b>{{ urlBirthBanner.birthDatetimeLocal.slice(0, 10) }}</b>
          lúc <b>{{ urlBirthBanner.birthDatetimeLocal.slice(11, 16) }}</b>
          <span v-if="urlBirthBanner.gender">· TA {{ urlBirthBanner.gender }}</span>.
          Đã tạo Person tạm "Khách (từ URL)" làm active. Đổi tên / lưu vào profile ở
          tab <em>Dữ liệu › Hồ sơ</em> nếu muốn giữ.
        </p>
        <button class="url-birth-dismiss" type="button" @click="urlBirthBannerDismissed = true" aria-label="Đóng">×</button>
      </div>

      <!-- ⭐ Quick Tasks — 3 tác vụ nhanh đầu trang -->
      <QuickTasksPanel @open-tab="(t) => { activeMainTab = t === 'wiki' ? 'wiki' : t; }" />

      <section class="main-tabs" aria-label="Điều hướng chính">
        <NavDropdown
          v-for="g in NAV_GROUPS"
          :key="g.label"
          :group="g"
          :active="activeMainTab"
          @select="activeMainTab = $event"
        />
        <NavDropdown
          v-if="isOwner"
          :group="NAV_DEV"
          :active="activeMainTab"
          @select="activeMainTab = $event"
        />
      </section>

      <p v-if="error" class="status-message error">{{ error }}</p>
      <p v-if="feedbackStatus" class="status-message success">{{ feedbackStatus }}</p>

      <!-- Tab 1: Hồ sơ — unified entity management (Persons/Families/Orgs/Events) -->
      <section v-if="activeMainTab === 'my-publications'" class="single-column" aria-label="Hồ sơ kết quả">
        <MyPublicationsPanel />
      </section>

      <section v-if="activeMainTab === 'profiles'" class="single-column" aria-label="Hồ sơ thực thể">
        <TabIntro
          icon="profiles"
          title="Hồ sơ — quản lý 4 loại thực thể"
          purpose="Đây là nơi anh nhập dữ liệu một lần và dùng cho mọi trường phái. Có 4 loại: Người (mọi cá nhân có ngày sinh), Gia đình (ghép nhiều người + ngày cưới), Tổ chức (công ty/đội nhóm), và Sự kiện (fact đã xảy ra để đối chiếu kết quả các trường phái)."
          :steps="[
            'Thêm Bản thân (role Bản thân) trước — đây là gốc cho mọi trường phái.',
            'Bấm Chọn để đánh dấu \'active person\' — các tab sau sẽ tự pickup.',
            'Sau đó thêm vợ/chồng/con/đồng nghiệp, tạo Gia đình ghép họ lại.',
            'Khi có sự kiện đã xảy ra (chuyển việc, kết hôn, mất mát...), ghi vào Sự kiện với outcome để engine có baseline đối chiếu.'
          ]"
        />
        <ProfilesPanel />
      </section>

      <!-- Tab 2: Vũ trụ hiện tại — physics + cosmic real-time, no school overlay -->
      <div v-else-if="activeMainTab === 'universe'">
        <TabIntro
          icon="universe"
          title="Vũ trụ hiện tại — trạng thái thực thời gian thực"
          purpose="Tầng quan sát hiện tại: thiên văn NASA/JPL, địa từ NOAA, lịch âm, tiết khí và bản đồ sao tropical được tách thành từng khối rõ ràng."
          :steps="[
            'Trên: không gian 3D + bảng chỉ số nhanh.',
            'Giữa: bản đồ sao phương Tây dạng chart wheel chuyên biệt.',
            'Dưới: lớp Tử Vi biểu tượng tách riêng khỏi thiên văn vật lý.'
          ]"
        />
        <div class="universe-dashboard">
          <section class="core-stage universe-stage" aria-label="Trực quan lõi vũ trụ" style="position: relative;">
            <UniverseCore
              :universe="universe"
              :planet-positions="planetPositions"
              :selected-time-zone="selectedTimeZone"
              :now="now"
              :natal-data="natalData"
            />
            <div style="position:absolute; top:14px; left:50%; transform:translateX(-50%); z-index:6; display:flex; align-items:center; gap:10px; flex-wrap:wrap; justify-content:center; max-width:92%;">
              <button
                type="button"
                :disabled="natalLoading"
                @click="natalData ? clearNatal() : loadNatal()"
                style="border:1px solid rgba(232,168,56,0.55); background:rgba(18,14,8,0.74); color:#ffd98a; border-radius:999px; padding:7px 16px; font-size:13px; font-weight:700; cursor:pointer; backdrop-filter:blur(4px);"
              >
                {{ natalLoading ? "Đang dựng lá số…" : natalData ? "× Tắt lá số" : "✦ Lá số trên nền vũ trụ" }}
              </button>
              <span v-if="natalError" style="color:#f0897c; font-size:12px; background:rgba(18,14,8,0.7); padding:3px 8px; border-radius:6px;">{{ natalError }}</span>
            </div>
          </section>
          <section class="universe-weather" aria-label="Trạng thái vũ trụ">
            <EnergyWeatherPanel :universe="universe" :loading="loadingUniverse" />
          </section>
          <SkyChartPanel class="universe-sky" />
          <ZiweiOrbitPanel class="universe-ziwei" :universe="universe" :ruleset-meta="activeRuleset" />
        </div>
      </div>

      <!-- Tab 3: Chiêm tinh phương Tây — Western school only -->
      <section v-else-if="activeMainTab === 'western'" class="single-column" aria-label="Chiêm tinh phương Tây">
        <TabIntro
          icon="western"
          title="Chiêm tinh phương Tây — 7 công cụ neo theo lá số sinh"
          purpose="Hoàn toàn dùng tropical zodiac + ephemeris JPL DE440s. Mỗi panel dưới đây trả lời 1 câu hỏi cụ thể về thời gian cuộc đời anh, neo theo ngày-giờ-vĩ-kinh độ sinh."
          :steps="[
            'Bản đồ mốc lớn: Saturn return, Uranus opposition, Pluto square — các mốc cuộc đời quan trọng.',
            'Lịch quá cảnh: hành tinh chậm chạm vào lá số sinh — ngày nào có biến động cấu trúc.',
            'Solar Returns: lá số sinh nhật mỗi năm — chủ đề năm đang sống.',
            'Progressions, Lunar Returns, Solar Arc, Eclipse activations: các kỹ thuật cổ điển bổ sung.'
          ]"
          warning="Mọi panel đều state-mapping, KHÔNG phải lời tiên tri định mệnh."
        />
        <LifeTimelinePanel />
        <TransitTimelinePanel />
        <SolarReturnsPanel />
        <ProgressionsPanel />
        <LunarReturnsPanel />
        <SolarArcPanel />
        <EclipsesPanel />
      </section>

      <!-- Tab 4: Mai Hoa Dịch Số — Eastern Yi school (NNTT + narrative + diep + natal quẻ) -->
      <section v-else-if="activeMainTab === 'maihoa'" class="single-column" aria-label="Mai Hoa Dịch Số">
        <TabIntro
          icon="maihoa"
          title="Mai Hoa Dịch Số 梅花易數 — Thiệu Khang Tiết (1011-1077)"
          purpose="⚡ Cải tiến 2026-05-15: panel gieo quẻ chuẩn Mai Hoa (Niên-Nguyệt-Nhật-Thời) + Ngoạn Pháp triết lý + 8 quẻ mnemonic + Thể-Dụng phân tích + Quái Khí Vượng/Suy + Save Prediction. Theo nguyên văn sách Thiệu, công thức (Y+M+D) mod 8 → quẻ trên, (Y+M+D+H) mod 8 → quẻ dưới, mod 6 → động hào. 3 quẻ chuẩn: Chính + Hỗ + Biến."
          :steps="[
            'Block trên: triết lý Ngoạn Pháp — TÂM là gốc (Mai Hoa trang 38).',
            'Mnemonic bar: 8 quẻ với hình (☰...) + tên cách nhớ.',
            'Form gieo: chọn năm-chi/tháng/ngày/giờ-chi. Mặc định = hiện tại.',
            'Gieo + lưu Prediction → có tâm note để review sau 7 ngày.',
            'Phía dưới: Timeline narrative + Diệp + Quẻ bản mệnh (giữ nguyên).'
          ]"
        />
        <LuuVanDashboard />

        <details>
          <summary style="cursor: pointer; color: #c4b5fd; padding: 0.4rem 0; font-size: 0.9rem; border-top: 1px solid rgba(196,181,253,0.2); margin-top: 1rem;">
            📅 Timeline 12 Lưu Nguyệt × 3 năm — so sánh paradigm các năm
          </summary>
          <LuuNguyetTimeline />
        </details>

        <details>
          <summary style="cursor: pointer; color: #34d399; padding: 0.4rem 0; font-size: 0.9rem; border-top: 1px solid rgba(52,211,153,0.2); margin-top: 1rem;">
            📓 Nhật ký vận — gắn việc thực × 7 quẻ (+ LLM đọc lại)
          </summary>
          <NhatKyVanPanel />
        </details>

        <MaiHoaCastPanel />

        <h3 style="color: #fcd34d; font-size: 0.95rem; margin-top: 1.5rem; border-top: 1px solid rgba(252,211,77,0.25); padding-top: 0.75rem;">
          📜 Tra cứu 64 quẻ Kinh Dịch (Trình Di + Chu Hy nguyên văn)
        </h3>
        <details>
          <summary style="cursor: pointer; color: #fcd34d; padding: 0.4rem 0; font-size: 0.85rem;">
            Bấm để mở bảng 8×8 — duyệt + đọc trực tiếp 1 quẻ, không cần gieo
          </summary>
          <KinhDichBrowser />
        </details>

        <details>
          <summary style="cursor: pointer; color: #a78bfa; padding: 0.4rem 0; font-size: 0.85rem;">
            🕸️ Cross-ref Graph — mạng 64 quẻ + cặp đối ngẫu + tâm pháp
          </summary>
          <KinhDichGraph />
        </details>

        <details>
          <summary style="cursor: pointer; color: #34d399; padding: 0.4rem 0; font-size: 0.85rem;">
            🎴 Học 343 Hào — Spaced Repetition (Anki-style)
          </summary>
          <HaoSpacedRepetition />
        </details>

        <h3 style="color: #c4b5fd; font-size: 0.9rem; margin-top: 1.5rem; border-top: 1px solid rgba(196,181,253,0.2); padding-top: 0.75rem;">
          🔗 Đối chiếu chéo nhiều cast (Cải tiến #4)
        </h3>
        <CrossCastPanel />

        <h3 style="color: #94a3b8; font-size: 0.85rem; margin-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.75rem;">
          📊 Phụ trợ — narrative timeline + diệp + quẻ bản mệnh (hệ thống cũ)
        </h3>
        <YiTimelineNarrativePanel :now="now" :selected-time-zone="selectedTimeZone" />
        <YiDiepPanel :now="now" :selected-time-zone="selectedTimeZone" />
        <PersonalQuaiPanel />
      </section>

      <!-- Tab 5: Lục Hào — coin-cast school (3D pad + result) -->
      <section v-else-if="activeMainTab === 'luc-hao'" class="maihoa-page" aria-label="Lục Hào">
        <TabIntro
          icon="luc-hao"
          title="Lục Hào — gieo quẻ cho câu hỏi cụ thể"
          purpose="Khác Mai Hoa, Lục Hào cần anh gieo cho 1 câu hỏi cụ thể. Hệ thống thu cử động chuột (thời gian giữ, đường di chuyển, nhịp) làm 'năng lượng gieo', kết hợp với thời điểm gieo để dựng quẻ chánh + quẻ biến + 6 hào động."
          :steps="[
            'Bước 1: chọn chủ đề câu hỏi (Gia đình / Sức khoẻ / Công việc / Tiền tài / Dự định / Nhập tay).',
            'Bước 2: nhập câu hỏi cụ thể (tuỳ chọn).',
            'Bước 3: nhắm mắt nghĩ về câu hỏi, giữ chuột vào ô gieo và rê tự nhiên 3-10 giây.',
            'Bước 4: thả tay — engine tự luận và mở trang Kết quả.'
          ]"
        />
        <MaiHoaClock3D
          :now="now"
          :selected-time-zone="selectedTimeZone"
          @cast-result="handleLucHaoCastResult"
          @open-result-page="activeMainTab = 'luc-hao-result'"
        />
      </section>

      <!-- Tab Liên Hoa — Liên Hoa Độn Pháp (separate school) -->
      <section v-else-if="activeMainTab === 'lien-hoa'" class="single-column" aria-label="Liên Hoa Độn Pháp">
        <TabIntro
          icon="lien-hoa"
          title="Liên Hoa Độn Pháp — gieo quẻ 5/9/13 không thời sự"
          purpose="Trường phái RIÊNG BIỆT với Mai Hoa. Liên Hoa cần anh chủ động đưa 2 số tâm ý (rút thăm hương, đếm lá, bốc số) — hệ thống tự dùng phép gia số [+4, +6, +4] sinh chuỗi Bản Quái Kiện 5, 9 hoặc 13 không thời sự liên hoàn. Mỗi không thời chứa Chánh + Hổ + Biến quái + lục thân tag toàn bộ 6 đơn quái."
          :steps="[
            'Bước 1: chọn giới tính (TA Nam / TA Nữ) — ảnh hưởng cách đọc lục thân.',
            'Bước 2: nhập 2 số tay Phải + tay Trái (rút thăm hương / đếm lá / bốc số ngẫu nhiên).',
            'Bước 3: nhập câu hỏi mưu cầu (tuỳ chọn) rồi bấm Gieo quẻ.',
            'Bước 4: xem Bản Quái Kiện — chú trọng Mệnh cung TA (Hổ quái) + phân bố chủ sự.',
            'Số đợt độn: hào 3/6 → 5 KTS · hào 4/1 → 9 KTS · hào 5/2 → 13 KTS.'
          ]"
        />
        <LienHoaPanel />
      </section>

      <!-- Tab: Bát Tự + Hà Lạc — Four Pillars + 2-hexagram personal fate -->
      <section v-else-if="activeMainTab === 'bat-tu'" class="single-column" aria-label="Bát Tự và Hà Lạc Lý Số">
        <TabIntro
          icon="bat-tu"
          title="Bát Tự — Tứ Trụ + Hà Lạc Lý Số (cross-module differentiator)"
          purpose="Bát Tự (Tử Bình) phân tích 4 trụ Năm/Tháng/Ngày/Giờ → Thiên Can + Địa Chi + Thập Thần + Ngũ Hành cân bằng. Hà Lạc Lý Số nối tiếp: từ Tứ Trụ suy ra 2 quẻ Kinh Dịch (Tiên thiên + Hậu thiên) + lộ trình 12 hào ~ 84-90 năm cuộc đời. Đây là feature differentiator quan trọng — Kabala.vn có nhắc nhưng không ship."
          :steps="[
            'Bước 1: ngày giờ sinh TỰ LẤY từ hồ sơ đang chọn (nhập 1 lần ở tab Hồ sơ) — đổi người bằng thanh 👤 Đang xem.',
            'Bước 2: chọn TA Nam / TA Nữ + múi giờ.',
            'Bước 3: bấm Luận — Bát Tự và Hà Lạc tính song song.',
            'Bước 4 (Bát Tự): xem 4 trụ + Nhật chủ (Day Master) + cân bằng Ngũ Hành.',
            'Bước 5 (Hà Lạc): xem Tiên thiên (cốt mệnh) + Hậu thiên (vận dụng) + chuỗi hào cuộc đời.',
            'Hào Nguyên đường = giai đoạn chủ chốt nhất của mỗi quẻ.'
          ]"
        />
        <BatTuPanel />
      </section>

      <!-- Tab: Tử Vi — Lá số đầy đủ + 14 chính tinh schema -->
      <section v-else-if="activeMainTab === 'tu-vi'" class="single-column" aria-label="Tử Vi lá số">
        <nav class="tuvi-school-tabs" aria-label="Ba trường phái Tử Vi">
          <button
            type="button"
            :class="{ active: activeTuViSchool === 'bac-phai' }"
            @click="activeTuViSchool = 'bac-phai'"
          >
            <span class="school-mark">🔮</span>
            <span>
              <b>Bắc Phái Đẩu Số</b>
              <small>14 chính tinh · lá số 12 cung · ảnh nhân cách sao</small>
            </span>
          </button>
          <button
            type="button"
            :class="{ active: activeTuViSchool === 'chieu-dom' }"
            @click="activeTuViSchool = 'chieu-dom'"
          >
            <span class="school-mark">📜</span>
            <span>
              <b>Chiếu Đởm Kinh</b>
              <small>18 phi tinh · pháp tượng · Nhập Cốt Tiên Kinh</small>
            </span>
          </button>
          <button
            type="button"
            :class="{ active: activeTuViSchool === 'dang-son' }"
            @click="activeTuViSchool = 'dang-son'"
          >
            <span class="school-mark">🔬</span>
            <span>
              <b>Đằng Sơn — Khoa Học</b>
              <small>tính được cái TÍNH · lá số 3D · video Đại Vận</small>
            </span>
          </button>
        </nav>

        <template v-if="activeTuViSchool === 'bac-phai'">
          <TabIntro
            icon="tu-vi"
            title="Bắc Phái Tử Vi Đẩu Số — An sao + 14 chính tinh"
            purpose="Trường phái chính để lập lá số cá nhân: 14 chính tinh + phụ tinh + sát tinh + Tứ Hóa đặt vào 12 cung. Mỹ thuật đi theo ngôn ngữ chân dung sao, cung vị và câu chuyện đời người."
            :steps="[
              'Bước 1: ngày giờ sinh + giới tính TỰ LẤY từ hồ sơ đang chọn (nhập 1 lần ở tab Hồ sơ).',
              'Bước 2: bấm An sao — engine tự convert Gregorian → âm lịch.',
              'Bước 3: xem lá số 4×4 với 12 cung. Mệnh có ★, Thân có 身.',
              'Bước 4: chính tinh (gold), phụ tinh (teal), sát tinh (đỏ); Tứ Hóa hiển thị badge L/Q/K/K.',
              'Bước 5: xem Đại Vận strip ở dưới — chu kỳ 10 năm.',
              'Bảng 14 chính tinh bên dưới là thư viện ảnh và schema tham chiếu của riêng Bắc Phái.'
            ]"
          />
          <TuViLaSoPanel @open-library-star="openLibraryStar" />

          <!-- Feature flagship cho bạn trẻ: Cung Phu Thê Bắc phái Trung Châu -->
          <h3 class="schema-divider">💑 Luận Cung Phu Thê — Bắc Phái Trung Châu</h3>
          <CungPhuTheBacPhaiPanel
            :birth-datetime-local="activeBirthDatetime"
            :gender="activePerson?.gender || 'nam'"
            :name="activePerson ? personLabel(activePerson) : ''"
            :person-key="activePerson?.person_key || ''"
          />

          <!-- Thư viện 14 chính tinh DỜI sang tab Thư viện (Anh chốt 2026-07-03:
               lá số chỉ giữ kết quả, kiến thức/ảnh sang thư viện độc lập). -->
          <button
            type="button"
            style="display:block;width:100%;margin-top:14px;padding:12px;border-radius:10px;
                   font-size:13.5px;font-weight:700;cursor:pointer;color:#b9d3ea;
                   background:rgba(143,176,208,0.12);border:1px solid rgba(143,176,208,0.35);"
            @click="activeMainTab = 'library'"
          >
            📚 Thư viện 14 chính tinh (ảnh · nghĩa · nguồn) → mở tab Thư viện
          </button>
        </template>

        <template v-else-if="activeTuViSchool === 'chieu-dom'">
          <TabIntro
            icon="tu-vi"
            title="Chiếu Đởm Kinh — 18 Phi Tinh + Nhập Cốt Tiên Kinh"
            purpose="Một kinh phái riêng trong Q4: không trộn với 14 chính tinh Bắc Phái. 18 Phi Tinh dùng quy tắc an sao và mỹ thuật pháp tượng riêng, thiên về lực bay qua cung vị, dấu hiệu, vật khí và phán đoán 4 chữ."
            :steps="[
              'Bước 1: đọc cảnh báo quy ước âm-dương đảo của Chiếu Đởm Kinh.',
              'Bước 2: xem 9 Dương tinh và 9 Âm tinh theo hệ 18 Phi Tinh.',
              'Bước 3: sao nào đã có ảnh sẽ hiện thumbnail WebP; bấm ảnh để mở bản gốc.',
              'Bước 4: xem 6 cách cục riêng của Chiếu Đởm Kinh.',
              'Bước 5: dùng Nhập Cốt Tiên Kinh như bảng tổng đoán nhanh 4 chữ cho từng sao.'
            ]"
          />
          <ChieuDomKinhPanel />
        </template>

        <template v-else-if="activeTuViSchool === 'dang-son'">
          <TabIntro
            icon="tu-vi"
            title="Đằng Sơn — Tử Vi Hoàn Toàn Khoa Học"
            purpose="Phái Tử Vi thứ 6 (khoa-học-hoá): lá số là HÀM TẤT ĐỊNH của thời điểm sinh. Mọi tầng — an sao, ngũ hành, Tứ Hóa, độ sáng, lưu niên — tính được tuyệt đối. Nhưng đó là cấu trúc TÍNH (bẩm phú), không phải MỆNH (động từ, việc vận hành). Đọc đồng dạng, KHÔNG bói. Tổ sư cận đại: TS. Đằng Sơn."
            :steps="[
              'Bước 1: chọn người ở Hồ sơ (cần ngày sinh).',
              'Bước 2: bấm Lập hồ sơ tính-được — engine tính 14 chính tinh + ngũ hành + Tứ Hóa + độ sáng.',
              'Bước 3: xem lá số trên nền vũ trụ THẬT (3D) — cái tính-được phủ lên thiên văn thật.',
              'Bước 4: xem video Đại Vận — lá số chuyển động qua thập niên (mệnh là động từ).'
            ]"
          />
          <DangSonPanel @go-universe="activeMainTab = 'universe'" />
        </template>
      </section>

      <!-- Tab Kỳ Môn Độn Giáp — trường phái thứ 6 -->
      <section v-else-if="activeMainTab === 'ky-mon'" class="single-column" aria-label="Kỳ Môn Độn Giáp">
        <TabIntro
          icon="ky-mon"
          title="Kỳ Môn Độn Giáp — Đế vương chi học"
          purpose="Môn cổ thuật phức tạp nhất Đông phương. Bàn 9 cung × 8 môn × 9 tinh × 8 thần phản chiếu cấu trúc năng lượng thời-không tại 1 thời điểm cụ thể. Tổ sư cận đại: Lưu Bá Ôn (1311-1375). Paradigm: ĐỌC ĐỒNG DẠNG, không predict."
          :steps="[
            'Bước 1: nhập thời gian khoảnh khắc anh muốn quan-sát (mặc định bây giờ).',
            'Bước 2: chọn phương pháp — Chabu (giờ, phổ thông) là default. Kim Hàm Ngọc Kính cho bàn theo ngày.',
            'Bước 3: bấm An cục — bàn 3×3 Lạc Thư hiện ra với 9 cung + môn/tinh/thần/thiên-địa bàn.',
            'Bước 4: đọc đồng dạng — bàn này phản chiếu khoảnh khắc anh hỏi, không predict tương lai.'
          ]"
        />
        <KyMonPanel />
      </section>

      <!-- Tab Hoàng Cực Kinh Thế — tầng thời cuộc + tra Thiết Bản (Thiệu Khang Tiết) -->
      <section v-else-if="activeMainTab === 'hoang-cuc'" class="single-column" aria-label="Hoàng Cực Kinh Thế">
        <TabIntro
          icon="hoang-cuc"
          title="Hoàng Cực Kinh Thế — tầng thời cuộc của Thiệu Khang Tiết"
          purpose="«Khoảng giữa THỂ và DỤNG, nơi biến đổi lưu hành — chính là nghiệp của thánh nhân» (Quan Vật Nội Thiên tr.144). Đặt một năm vào chu kỳ Nguyên-Hội-Vận-Thế 129.600 năm; máy đọc BIẾN (tiêu trưởng của thời), QUYỀN quyết định thuộc về người. Kèm tra cứu 10.907 điều văn Thiết Bản Thần Số."
          :steps="[
            'Bước 1: nhập năm muốn quan-sát (mặc định năm nay) — bấm Định vị.',
            'Bước 2: nhập năm sinh nếu muốn thấy đời mình trải trên những THẾ nào.',
            'Bước 3: đọc atoms trích từ chính sách 皇极经世书今说 (Diêm Tu Triện).',
            'Bước 4: tra điều văn Thiết Bản theo số hoặc tìm theo nội dung.'
          ]"
        />
        <HoangCucPanel />
      </section>

      <!-- Tab 6: Gia đạo — multi-actor household system -->
      <section v-else-if="activeMainTab === 'gieo-duyen'" class="single-column" aria-label="Gieo Duyên — đạo phu thê">
        <GieoDuyenPanel />
      </section>

      <section v-else-if="activeMainTab === 'family'" class="single-column" aria-label="Hệ thống gia đạo">
        <GiaDaoPanel />
        <TabIntro
          icon="family"
          title="Gia đạo — đa chủ thể"
          purpose="Một người không phải hòn đảo. Khi có vợ/chồng + con, năng lượng cộng hưởng. Hệ thống tính 4 layer: (1) Quẻ Gia Đạo từ ngày cưới, (2) Thái Tuế Nhập Quái — chi sinh các thành viên ánh vào lá số, (3) Số học Mai Hoa hợp nhất, (4) Element bridging — phát hiện ai làm cầu nối thông quan."
          :steps="[
            'Trước tiên: vào tab Hồ sơ thêm các thành viên + tạo Gia đình.',
            'Quay lại tab này, panel tự đọc gia đình anh đã tạo.',
            'Output: 4 layer phân tích cộng hưởng, giúp anh hiểu vai trò mỗi thành viên trong cấu trúc.'
          ]"
        />
        <FamilySystemPanel />
        <PersonalResonance
          :personal="personal"
          :profiles="profiles"
          :active-profile-id="activeProfileId"
          @submit-profile="handleProfileSubmit"
          @profile-select="onProfileSelect"
          @profile-create="onProfileCreate"
        />
        <FeedbackPanel
          :prompt="selectedPrompt"
          :disabled="!selectedPrompt"
          @submit-feedback="handleFeedbackSubmit"
        />
      </section>

      <!-- Tab 7: GPS hành động — prescriptive layer (EXPERIMENTAL) -->
      <section v-else-if="activeMainTab === 'gps'" class="single-column" aria-label="GPS hành động">
        <TabIntro
          icon="gps"
          title="GPS hành động — dự đoán pre-registered có thể kiểm chứng"
          purpose="Đây là tầng PRESCRIPTIVE duy nhất — engine đề xuất hành động cụ thể theo giờ + miền. Mỗi prediction được hash + lưu IMMUTABLE trước khi xảy ra (không sửa được sau). Sau khi ngày trôi qua, anh phản hồi đúng/sai để tích luỹ accuracy."
          :steps="[
            'Bước 1: nhập ngày giờ sinh + chọn ngày tương lai cần xem.',
            'Bước 2: bấm Preview — xem các trigger (giờ + miền + action) cho ngày đó.',
            'Bước 3: nếu muốn test, bấm Pre-register để khoá predictions immutable.',
            'Bước 4: sau khi ngày đã qua, mở lại panel và bấm Đúng/Sai/Một phần cho mỗi prediction.',
            'Bước 5: sau ≥30 datapoint, accuracy stats có ý nghĩa thống kê.'
          ]"
          warning="EXPERIMENTAL_MODE đang ON — chế độ single-user. Không công khai cho cộng đồng cho tới khi validate đủ N."
        />
        <GPSPanel />
      </section>

      <!-- Tab Sức Khỏe — Bát Tự × Đông y (2026-06-02) -->
      <section v-else-if="activeMainTab === 'health'" class="single-column" aria-label="Sức khỏe — Bát Tự × Đông y">
        <HealthPanel />
      </section>

      <section v-else-if="activeMainTab === 'lexicon'" class="single-column" aria-label="Lexicon — Dịch tự điển">
        <TabIntro
          icon="lexicon"
          title="YI-Lexicon — Dịch tự điển đa trường phái"
          purpose="Thư viện ánh xạ symbol → cosmology (Bát Quái, Ngũ Hành, Can-Chi…) trích xuất từ kho sách cổ. Tuyên ngôn: nghiên cứu đa trường phái độc lập, có đối chiếu chéo + tranh luận, khai mở dần điểm chung/riêng."
          :steps="[
            'Browse: tìm 1 concept (vd: lá, Càn, số 5) → xem mappings + source citation + page traceback.',
            'Duyệt mâu thuẫn: anh là arbiter — chọn primary, kept_all (đa phái valid), hoặc dismiss.',
            'Distill queue: LLM auto-extract đã merge YOLO → anh duyệt approve/reject để dạy lại lexicon.',
            'Reading plan: 6 tuần đọc tuần tự theo trường phái (Tier S+A → Bát Tự → Lục Hào → Mai/Liên Hoa → Tử Vi → Trạch nhật).'
          ]"
        />
        <LexiconPanel />
      </section>

      <section v-else-if="activeMainTab === 'research'" class="single-column" aria-label="AI Research Agent">
        <ResearchPanel />
      </section>

      <!-- Tab Thư viện: 2 sub-tab SONG SONG — 🔯 Tử Vi (sao/cung/cục) ⟷ 📚 Sách phục chế -->
      <section v-else-if="activeMainTab === 'library'" class="single-column" aria-label="Thư viện">
        <nav class="tuvi-school-tabs" aria-label="Thư viện: 2 mảng">
          <button type="button" :class="{ active: libSubTab === 'tu-vi' }" @click="libSubTab = 'tu-vi'">
            <span class="school-mark">🔯</span>
            <span><b>Tử Vi</b><small>sao · cung · cục · Thân-Mệnh · vòng sao</small></span>
          </button>
          <button type="button" :class="{ active: libSubTab === 'sach' }" @click="libSubTab = 'sach'">
            <span class="school-mark">📚</span>
            <span><b>Sách phục chế</b><small>corpus sách Việt Đông phương · search full-text</small></span>
          </button>
        </nav>

        <div v-show="libSubTab === 'tu-vi'">
          <h3 class="schema-divider">🔯 Thư viện Tử Vi (Bắc Phái) — 14 chính tinh · phụ tinh · Cục · Thân-Mệnh · vòng sao</h3>
          <ChinhTinhLibraryPanel ref="tuviLibRef" />
          <NguCucLibraryPanel />
          <ThanMenhLibraryPanel />
          <VongSaoLibraryPanel />
        </div>

        <div v-show="libSubTab === 'sach'">
          <TabIntro
            icon="lexicon"
            title="📚 Thư viện phục chế — Sách Việt Đông phương"
            purpose="Sách Tứ Trụ / Tử Vi / Chu Dịch / Bát Tự / Bốc Phệ tiếng Việt — đã phục chế từ PDF scan qua Tesseract OCR + Gemma 4 cleanup, hoặc trực tiếp text-layer qua MarkItDown. Tất cả publish-ready markdown, đọc trực tiếp trên web. Anh đọc, tham chiếu, search full-text trên toàn bộ corpus."
            :steps="[
              'Sidebar trái: 14+ sách grouped 8 categories (Kinh Điển / Tứ Trụ / Tử Vi / Bốc Phệ / Chu Dịch / Dịch Số / Chuyên Đề / Lịch).',
              'Click 1 sách → render markdown, paginate 20K chars/trang để load nhanh.',
              'Search bar: full-text trên 12.5M chars — gõ thuật ngữ (Thiên Can, Dụng Thần, Tả Phụ, ...) → click hit → mở đúng sách.',
              'Mỗi đêm sau khi pipeline phục chế xong thêm sách → CI deploy → auto hiện trên đây.'
            ]"
          />
          <RestoredLibrary />
        </div>
      </section>

      <section v-else-if="activeMainTab === 'wiki'" class="single-column" aria-label="Wiki Tổ sư - Đệ tử">
        <MasterView />
      </section>

      <section v-else-if="activeMainTab === 'publishing'" class="single-column" aria-label="Workspace dịch sách">
        <LibraryView
          v-if="!publishingSelectedBook"
          @open-book="openBookInWorkspace"
        />
        <PublishingWorkspace
          v-else
          :book-id="publishingSelectedBook"
          @back="backToLibrary"
        />
      </section>

      <section v-else-if="activeMainTab === 'settings'" class="single-column" aria-label="Cài đặt hệ thống">
        <SettingsPanel />
      </section>

      <section v-else-if="activeMainTab === 'admin'" class="single-column" aria-label="Admin dashboard">
        <AdminPanel />
      </section>

      <section v-else-if="activeMainTab === 'chan-dung'" class="single-column" aria-label="Chân Dung khách hàng">
        <ChanDungPanel @open-product="onOpenProduct" @open-page="onOpenPage" />
      </section>

      <section v-else-if="activeMainTab === 'hoi-hermes'" class="single-column" aria-label="Hỏi Hermes — Hội Đồng đa trường phái">
        <HoiHermesPanel />
      </section>

      <section v-else-if="activeMainTab === 'deep-reading'" class="single-column" aria-label="Luận Sâu Trọn Đời">
        <DeepReadingPanel />
      </section>

      <section v-else-if="activeMainTab === 'admin-hermes'" class="single-column" aria-label="Phòng Quản Trị Hermes">
        <HermesAdminPanel />
      </section>

      <section v-else-if="activeMainTab === 'atom-verify'" class="single-column" aria-label="Bàn duyệt Atoms">
        <AtomVerifyPanel />
      </section>

      <section v-else-if="activeMainTab === 'pytago'" class="maihoa-page" aria-label="Trang trường phái Pytago">
        <ThanSoPanel />
      </section>

      <section v-else class="maihoa-page" aria-label="Trang kết quả Lục Hào">
        <LucHaoResultPage :result="latestLucHaoResult" :meta="latestLucHaoMeta" />
      </section>
    </section>

    <!-- Floating Hermes chat — luôn hiện ở góc dưới phải mọi tab -->
    <YiHermesChat :active-tab="activeMainTab" />

    <!-- Global wiki popup — hiển thị khi click 1 thuật ngữ Tử Vi trong panel -->
    <WikiPopup />

    <!-- First-time profile setup — bắt user mới đăng ký nhập birth_datetime 1 lần -->
    <OnboardingModal />

    <!-- Reading comfort: global text-size + reading-theme control (floating) -->
    <ReadingControls />
  </main>
</template>
