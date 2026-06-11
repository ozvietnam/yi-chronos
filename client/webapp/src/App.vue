<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { Activity, Database, RotateCcw, Send, ShieldCheck } from "lucide-vue-next";
import SchoolIcon from "./components/SchoolIcon.vue";
import UserBadge from "./components/UserBadge.vue";
import OnboardingModal from "./components/OnboardingModal.vue";
import AdminPanel from "./components/AdminPanel.vue";
import MyPublicationsPanel from "./components/MyPublicationsPanel.vue";
import WikiPopup from "./components/WikiPopup.vue";
import { isOwner } from "./stores/authStore.js";
import { activePerson, activeBirthDatetime } from "./stores/userDataStore.js";
import ReadingControls from "./components/ReadingControls.vue";
import { useReadingPrefs } from "./composables/useReadingPrefs.js";
import UniverseCore from "./components/UniverseCore.vue";
import MaiHoaClock3D from "./components/MaiHoaClock3D.vue";
import LucHaoResultPage from "./components/LucHaoResultPage.vue";
import PytagoEnergyPage from "./components/PytagoEnergyPage.vue";
import ThanSoPanel from "./components/ThanSoPanel.vue";
import EnergyWeatherPanel from "./components/EnergyWeatherPanel.vue";
import PersonalResonance from "./components/PersonalResonance.vue";
import FeedbackPanel from "./components/FeedbackPanel.vue";
import ZiweiOrbitPanel from "./components/ZiweiOrbitPanel.vue";
import SkyChartPanel from "./components/SkyChartPanel.vue";
import LifeTimelinePanel from "./components/LifeTimelinePanel.vue";
import TransitTimelinePanel from "./components/TransitTimelinePanel.vue";
import SolarReturnsPanel from "./components/SolarReturnsPanel.vue";
import ProgressionsPanel from "./components/ProgressionsPanel.vue";
import LunarReturnsPanel from "./components/LunarReturnsPanel.vue";
import SolarArcPanel from "./components/SolarArcPanel.vue";
import EclipsesPanel from "./components/EclipsesPanel.vue";
import YiTimelineNarrativePanel from "./components/YiTimelineNarrativePanel.vue";
import YiDiepPanel from "./components/YiDiepPanel.vue";
import PersonalQuaiPanel from "./components/PersonalQuaiPanel.vue";
import GPSPanel from "./components/GPSPanel.vue";
import FamilySystemPanel from "./components/FamilySystemPanel.vue";
import ProfilesPanel from "./components/ProfilesPanel.vue";
import TabIntro from "./components/TabIntro.vue";
import LienHoaPanel from "./components/LienHoaPanel.vue";
import BatTuPanel from "./components/BatTuPanel.vue";
import HealthPanel from "./components/HealthPanel.vue";
import KyMonPanel from "./components/KyMonPanel.vue";
import HoangCucPanel from "./components/HoangCucPanel.vue";
import ChinhTinhGallery from "./components/ChinhTinhGallery.vue";
import TuViLaSoPanel from "./components/TuViLaSoPanel.vue";
import CungPhuTheBacPhaiPanel from "./components/CungPhuTheBacPhaiPanel.vue";
import ChieuDomKinhPanel from "./components/ChieuDomKinhPanel.vue";
import YiHermesChat from "./components/YiHermesChat.vue";
import LexiconPanel from "./components/LexiconPanel.vue";
import SettingsPanel from "./components/SettingsPanel.vue";
import ResearchPanel from "./components/ResearchPanel.vue";
import MasterView from "./components/wiki/MasterView.vue";
import QuickTasksPanel from "./components/QuickTasksPanel.vue";
import MaiHoaCastPanel from "./components/wiki/MaiHoaCastPanel.vue";
import KinhDichBrowser from "./components/wiki/KinhDichBrowser.vue";
import KinhDichGraph from "./components/wiki/KinhDichGraph.vue";
import HaoSpacedRepetition from "./components/wiki/HaoSpacedRepetition.vue";
import LuuVanDashboard from "./components/wiki/LuuVanDashboard.vue";
import NhatKyVanPanel from "./components/wiki/NhatKyVanPanel.vue";
import LuuNguyetTimeline from "./components/wiki/LuuNguyetTimeline.vue";
import RestoredLibrary from "./components/library/RestoredLibrary.vue";
// DailyHexagramPanel: DEPRECATED 2026-05-27 đêm — paradigm SAI (horoscope-style).
// Thay bằng LuuVanDashboard (7 vòng quẻ đúng paradigm Khang Tiết).
// import DailyHexagramPanel from "./components/wiki/DailyHexagramPanel.vue";
import CrossCastPanel from "./components/wiki/CrossCastPanel.vue";
import PublishingWorkspace from "./components/publishing/PublishingWorkspace.vue";
import LibraryView from "./components/publishing/LibraryView.vue";
import { applyBirthFromUrlOnMount } from "./composables/useBirthShare.js";
import { getActiveRuleset, getPlanetPositions, getUniverseNow, submitFeedback, submitPersonalProfile } from "./lib/api";
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
const activeRuleset = ref(null);
const now = ref(new Date());
const selectedTimeZone = ref("Asia/Ho_Chi_Minh");
const activeMainTab = ref("profiles");
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

onMounted(() => {
  startReadingPrefs(); // apply saved reading theme + text scale to <html>
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
          <div>
            <h1>YI-CHRONOS</h1>
            <p>
              Hệ mô hình hóa trạng thái thời gian
              <span v-if="activeRuleset" class="ruleset-pill">
                {{ activeRuleset.ziwei_school }} · {{ activeRuleset.ziwei_ruleset_id }}
              </span>
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
        <div class="tab-group">
          <span class="tab-group-label">Dữ liệu</span>
          <button type="button" :class="{ active: activeMainTab === 'profiles' }"
            @click="activeMainTab = 'profiles'">
            <span class="tab-icon"><SchoolIcon name="profiles" /></span> Hồ sơ
          </button>
          <button type="button" :class="{ active: activeMainTab === 'my-publications' }"
            @click="activeMainTab = 'my-publications'"
            title="Hồ sơ kết quả: PDF, Word, MD đã sinh thành">
            <span class="tab-icon">📚</span> Kết quả
          </button>
        </div>
        <div class="tab-divider"></div>
        <div class="tab-group">
          <span class="tab-group-label">Trường phái</span>
          <button type="button" :class="{ active: activeMainTab === 'universe' }"
            @click="activeMainTab = 'universe'">
            <span class="tab-icon"><SchoolIcon name="universe" /></span> Vũ trụ hiện tại
          </button>
          <button type="button" :class="{ active: activeMainTab === 'western' }"
            @click="activeMainTab = 'western'">
            <span class="tab-icon"><SchoolIcon name="western" /></span> Chiêm tinh Tây
          </button>
          <button type="button" :class="{ active: activeMainTab === 'maihoa' }"
            @click="activeMainTab = 'maihoa'">
            <span class="tab-icon"><SchoolIcon name="maihoa" /></span> Mai Hoa
          </button>
          <button type="button" :class="{ active: activeMainTab === 'luc-hao' }"
            @click="activeMainTab = 'luc-hao'">
            <span class="tab-icon"><SchoolIcon name="luc-hao" /></span> Lục Hào
          </button>
          <button type="button" :class="{ active: activeMainTab === 'lien-hoa' }"
            @click="activeMainTab = 'lien-hoa'">
            <span class="tab-icon"><SchoolIcon name="lien-hoa" /></span> Liên Hoa
          </button>
          <button type="button" :class="{ active: activeMainTab === 'bat-tu' }"
            @click="activeMainTab = 'bat-tu'">
            <span class="tab-icon"><SchoolIcon name="bat-tu" /></span> Bát Tự
          </button>
          <button type="button" :class="{ active: activeMainTab === 'tu-vi' }"
            @click="activeMainTab = 'tu-vi'">
            <span class="tab-icon"><SchoolIcon name="tu-vi" /></span> Tử Vi
          </button>
          <button type="button" :class="{ active: activeMainTab === 'ky-mon' }"
            @click="activeMainTab = 'ky-mon'">
            <span class="tab-icon"><SchoolIcon name="ky-mon" /></span> Kỳ Môn
          </button>
          <button type="button" :class="{ active: activeMainTab === 'pytago' }"
            @click="activeMainTab = 'pytago'">
            <span class="tab-icon"><SchoolIcon name="pytago" /></span> Pytago
          </button>
          <button type="button" :class="{ active: activeMainTab === 'hoang-cuc' }"
            @click="activeMainTab = 'hoang-cuc'">
            <span class="tab-icon">🌌</span> Hoàng Cực
          </button>
        </div>
        <div class="tab-divider"></div>
        <div class="tab-group">
          <span class="tab-group-label">Tri thức</span>
          <button type="button" :class="{ active: activeMainTab === 'library' }"
            @click="activeMainTab = 'library'">
            <span class="tab-icon">📚</span> Thư viện
          </button>
        </div>
        <div class="tab-divider"></div>
        <div class="tab-group">
          <span class="tab-group-label">Tổng hợp</span>
          <button type="button" :class="{ active: activeMainTab === 'family' }"
            @click="activeMainTab = 'family'">
            <span class="tab-icon"><SchoolIcon name="family" /></span> Gia đạo
          </button>
          <button type="button" :class="{ active: activeMainTab === 'gps' }"
            @click="activeMainTab = 'gps'">
            <span class="tab-icon"><SchoolIcon name="gps" /></span> GPS
          </button>
          <button type="button" :class="{ active: activeMainTab === 'health' }"
            @click="activeMainTab = 'health'"
            title="Sức khỏe — Bát Tự × Đông y">
            <span class="tab-icon">🌿</span> Sức khỏe
          </button>
          <button type="button" :class="{ active: activeMainTab === 'settings' }"
            @click="activeMainTab = 'settings'">
            <span class="tab-icon">⚙️</span> Cài đặt
          </button>
        </div>
        <!-- Dev / Owner-only tabs — ẩn cho user thường, sẽ ẩn hết khi phổ biến rộng -->
        <template v-if="isOwner">
          <div class="tab-divider"></div>
          <div class="tab-group">
            <span class="tab-group-label">Kiến thức · Dev</span>
            <button type="button" :class="{ active: activeMainTab === 'lexicon' }"
              @click="activeMainTab = 'lexicon'">
              <span class="tab-icon"><SchoolIcon name="lexicon" /></span> Lexicon
            </button>
            <button type="button" :class="{ active: activeMainTab === 'research' }"
              @click="activeMainTab = 'research'">
              <span class="tab-icon">🔬</span> Research
            </button>
            <button type="button" :class="{ active: activeMainTab === 'wiki' }"
              @click="activeMainTab = 'wiki'">
              <span class="tab-icon">🌌</span> Wiki Tổ sư
            </button>
            <button type="button" :class="{ active: activeMainTab === 'publishing' }"
              @click="activeMainTab = 'publishing'">
              <span class="tab-icon">📖</span> Dịch sách
            </button>
            <button type="button" :class="{ active: activeMainTab === 'admin' }"
              @click="activeMainTab = 'admin'">
              <span class="tab-icon">👥</span> Admin
            </button>
          </div>
        </template>
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
          <section class="core-stage universe-stage" aria-label="Trực quan lõi vũ trụ">
            <UniverseCore
              :universe="universe"
              :planet-positions="planetPositions"
              :selected-time-zone="selectedTimeZone"
              :now="now"
            />
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
            'Bước 1: nhập sinh thần (datetime-local, có thể từ active person ở tab Hồ sơ).',
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
        <nav class="tuvi-school-tabs" aria-label="Hai trường phái Tử Vi">
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
        </nav>

        <template v-if="activeTuViSchool === 'bac-phai'">
          <TabIntro
            icon="tu-vi"
            title="Bắc Phái Tử Vi Đẩu Số — An sao + 14 chính tinh"
            purpose="Trường phái chính để lập lá số cá nhân: 14 chính tinh + phụ tinh + sát tinh + Tứ Hóa đặt vào 12 cung. Mỹ thuật đi theo ngôn ngữ chân dung sao, cung vị và câu chuyện đời người."
            :steps="[
              'Bước 1: nhập sinh thần (datetime-local) + giới tính.',
              'Bước 2: bấm An sao — engine tự convert Gregorian → âm lịch.',
              'Bước 3: xem lá số 4×4 với 12 cung. Mệnh có ★, Thân có 身.',
              'Bước 4: chính tinh (gold), phụ tinh (teal), sát tinh (đỏ); Tứ Hóa hiển thị badge L/Q/K/K.',
              'Bước 5: xem Đại Vận strip ở dưới — chu kỳ 10 năm.',
              'Bảng 14 chính tinh bên dưới là thư viện ảnh và schema tham chiếu của riêng Bắc Phái.'
            ]"
          />
          <TuViLaSoPanel />

          <!-- Feature flagship cho bạn trẻ: Cung Phu Thê Bắc phái Trung Châu -->
          <h3 class="schema-divider">💑 Luận Cung Phu Thê — Bắc Phái Trung Châu</h3>
          <CungPhuTheBacPhaiPanel
            :birth-datetime-local="activeBirthDatetime"
            :gender="activePerson?.gender || 'nam'"
            :name="activePerson?.name || ''"
            :person-key="activePerson?.person_key || ''"
          />

          <h3 class="schema-divider">📚 Bắc Phái — thư viện 14 chính tinh</h3>
          <ChinhTinhGallery />
        </template>

        <template v-else>
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
      <section v-else-if="activeMainTab === 'family'" class="single-column" aria-label="Hệ thống gia đạo">
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

      <!-- Tab Thư viện: phục chế sách Việt Đông phương (OCR + cleanup local) -->
      <section v-else-if="activeMainTab === 'library'" class="single-column" aria-label="Thư viện phục chế">
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

      <section v-else-if="activeMainTab === 'pytago'" class="maihoa-page" aria-label="Trang trường phái Pytago">
        <ThanSoPanel />
        <PytagoEnergyPage
          :luc-hao-result="latestLucHaoResult"
          :luc-hao-meta="latestLucHaoMeta"
          :universe-profile="activeUniverseProfile"
        />
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
