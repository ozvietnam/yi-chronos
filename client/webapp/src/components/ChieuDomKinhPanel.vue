<script setup>
/**
 * Chiếu Đởm Kinh panel — kinh phái khác Tử Vi Đẩu Số chính thống.
 * 18 Phi Tinh + 12 cung × 18 sao matrix + cách cục mới + Nhập Cốt Tiên Kinh tổng đoán.
 * Source: Q4 p0269-p0300 (Phase A thâm nhuần 2026-05-20)
 */
import { computed, ref, onMounted } from "vue";
import { activePerson } from "../stores/userDataStore.js";

const cdkChart = ref(null);
const phiTinh18 = ref(null);
const phiTinhCards = ref([]);
const cachCuc = ref(null);
const nhapCot = ref(null);
const loading = ref(false);
const error = ref("");
const activeStarId = ref(null);
const selectedArtCard = ref(null);
const selectedBranch = ref(null);

const BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];

// ─── Branch info Việt thuần (dạy người mới) ──────────────────────────────────
const BRANCH_INFO = {
  "Tý":   { conGiap: "Chuột",  gio: "23h00 – 01h00 (nửa đêm)",   phuongVi: "Bắc",        ngu_hanh: "Thủy", am_duong: "Dương", y_nghia: "Khởi đầu chu kỳ. Lúc trời đất nghỉ ngơi tuyệt đối, hạt giống đang ngủ chờ nảy mầm." },
  "Sửu":  { conGiap: "Trâu",   gio: "01h00 – 03h00 (gần sáng)",  phuongVi: "Bắc-Đông Bắc", ngu_hanh: "Thổ", am_duong: "Âm",    y_nghia: "Giai đoạn nuôi dưỡng trong đất. Hạt giống nằm trong lòng đất, chờ vươn lên." },
  "Dần":  { conGiap: "Hổ",     gio: "03h00 – 05h00 (rạng đông)", phuongVi: "Đông-Đông Bắc", ngu_hanh: "Mộc", am_duong: "Dương", y_nghia: "Mầm cây nhú lên. Năng lượng mãnh liệt như con hổ vươn vai sau giấc ngủ dài." },
  "Mão":  { conGiap: "Mèo (TQ: Thỏ)", gio: "05h00 – 07h00 (sáng sớm)", phuongVi: "Đông", ngu_hanh: "Mộc", am_duong: "Âm",   y_nghia: "Mặt trời mọc, cây cối đâm chồi. Mềm mại nhưng kiên trì, như thỏ/mèo." },
  "Thìn": { conGiap: "Rồng",   gio: "07h00 – 09h00 (đầu ngày)",  phuongVi: "Đông-Đông Nam", ngu_hanh: "Thổ", am_duong: "Dương", y_nghia: "Sương tan, rồng cuộn mây. Lúc tích tụ năng lượng để bay cao." },
  "Tỵ":   { conGiap: "Rắn",    gio: "09h00 – 11h00 (giữa sáng)", phuongVi: "Nam-Đông Nam", ngu_hanh: "Hỏa", am_duong: "Âm",    y_nghia: "Mặt trời lên cao, rắn ra khỏi hang sưởi ấm. Thông minh, biến hóa." },
  "Ngọ":  { conGiap: "Ngựa",   gio: "11h00 – 13h00 (giữa trưa)", phuongVi: "Nam",        ngu_hanh: "Hỏa", am_duong: "Dương",  y_nghia: "Đỉnh cao của Dương. Mặt trời chính ngọ, ngựa phi nước đại — năng lượng tột bậc." },
  "Mùi":  { conGiap: "Dê",     gio: "13h00 – 15h00 (xế trưa)",   phuongVi: "Nam-Tây Nam", ngu_hanh: "Thổ", am_duong: "Âm",     y_nghia: "Dê ăn cỏ ngon. Lúc thư thái sau bữa trưa, hài lòng với những gì có." },
  "Thân": { conGiap: "Khỉ",    gio: "15h00 – 17h00 (xế chiều)",  phuongVi: "Tây-Tây Nam", ngu_hanh: "Kim", am_duong: "Dương", y_nghia: "Khỉ chuyền cành kiếm ăn. Tinh ranh, linh hoạt, biết tận dụng cơ hội." },
  "Dậu":  { conGiap: "Gà",     gio: "17h00 – 19h00 (chiều tà)",  phuongVi: "Tây",        ngu_hanh: "Kim", am_duong: "Âm",    y_nghia: "Gà về chuồng, gọi đàn. Lúc thu mình kết thúc một chu kỳ làm việc." },
  "Tuất": { conGiap: "Chó",    gio: "19h00 – 21h00 (chập tối)",  phuongVi: "Tây-Tây Bắc", ngu_hanh: "Thổ", am_duong: "Dương", y_nghia: "Chó canh nhà khi trời tối. Trung thành, cảnh giác trước những thay đổi." },
  "Hợi":  { conGiap: "Lợn",    gio: "21h00 – 23h00 (đêm khuya)", phuongVi: "Bắc-Tây Bắc", ngu_hanh: "Thủy", am_duong: "Âm",   y_nghia: "Lợn ngủ no nê. Lúc nghỉ ngơi, tích lũy cho chu kỳ mới — chuẩn bị về Tý." },
};

const CHART_STAR_ID = {
  "Tử": "tu",
  "Văn": "van",
  "Phúc": "phuc",
  "Lộc": "loc",
  "Ấn": "an",
  "Thọ": "tho",
  "Trượng": "truong",
  "Khố": "kho",
  "Không": "khong",
  "Diêu": "dieu",
  "Quý": "quy",
  "Loan": "hong",
  "Hồng": "hong",
  "Dị": "di",
  "Mao": "mao",
  "Hư": "hu",
  "Quán": "quan",
  "Hình": "hinh",
  "Nhận": "nhan",
  "Khốc": "khoc",
};

const NHAP_COT_STAR_NAME = {
  "Tử": "Tử Vi",
  "Hư": "Thiên Hư",
  "Quý": "Thiên Quý",
  "Ấn": "Thiên Ấn",
  "Thọ": "Thiên Thọ",
  "Không": "Thiên Hư",
  "Loan": "Hồng Loan",
  "Hồng": "Hồng Loan",
  "Khố": "Thiên Khố",
  "Quán": "Thiên Quán",
  "Văn": "Văn Xương",
  "Phúc": "Phúc Lộc",
  "Lộc": "Phúc Lộc",
  "Trượng": "Thiên Trượng",
  "Dị": "Thiên Dị",
  "Mao": "Mao Đầu",
  "Nhận": "Thiên Nhận (Kình Dương)",
  "Hình": "Thiên Hình",
  "Khốc": "Thiên Khốc",
  "Diêu": "Thiên Diêu",
};

const phiTinhCardsByStarId = computed(() => {
  return new Map(phiTinhCards.value.map((card) => [card.star_id, card]));
});

const nhapCotByStar = computed(() => {
  return new Map((nhapCot.value?.per_star_tong_doan || []).map((item) => [item.star, item]));
});

const cdkBranchMap = computed(() => {
  const map = new Map(BRANCHES.map((branch) => [branch, []]));
  for (const [star, branch] of Object.entries(cdkChart.value?.stars || {})) {
    if (!map.has(branch)) map.set(branch, []);
    map.get(branch).push({
      star,
      branch,
      art: chartArtFor(star),
      meaning: starMeaningFor(star, branch),
    });
  }
  return BRANCHES.map((branch) => ({
    branch,
    stars: map.get(branch) || [],
    isMenh: branch === cdkChart.value?.menh_branch,
  }));
});

const cdkMenhStars = computed(() => {
  const menh = cdkChart.value?.menh_branch;
  if (!menh) return [];
  return Object.entries(cdkChart.value?.stars || {})
    .filter(([, branch]) => branch === menh)
    .map(([star, branch]) => ({
      star,
      branch,
      art: chartArtFor(star),
      meaning: starMeaningFor(star, branch),
    }));
});

// ─── Clock map geometry — vòng tròn 12 địa chi ───────────────────────────────
// Quy ước la bàn Trung Hoa: Tý=12h (Bắc, top), Mão=3h (Đông, right),
// Ngọ=6h (Nam, bottom), Dậu=9h (Tây, left).
// Tam hợp 4 cục: Thân-Tý-Thìn (Thủy) · Hợi-Mão-Mùi (Mộc) · Dần-Ngọ-Tuất (Hỏa) · Tỵ-Dậu-Sửu (Kim).
const CLOCK_GEOMETRY = {
  cx: 240,
  cy: 240,
  nodeRadius: 38,  // mỗi địa chi node
  ringRadius: 188, // khoảng cách từ tâm tới node
  coreRadius: 96,  // core Mệnh giữa
};

const TAM_HOP_CUC = {
  "Thủy": ["Thân", "Tý", "Thìn"],
  "Mộc":  ["Hợi", "Mão", "Mùi"],
  "Hỏa":  ["Dần", "Ngọ", "Tuất"],
  "Kim":  ["Tỵ", "Dậu", "Sửu"],
};

function categoryToTone(category, isMenh) {
  if (isMenh) return "menh";
  if (!category) return "neutral";
  const c = String(category).toLowerCase();
  if (c.includes("cát") || c.includes("cat")) return "cat";
  if (c.includes("hung")) return "hung";
  if (c.includes("dương") || c.includes("duong")) return "duong";
  if (c.includes("âm") || c.includes("am")) return "am";
  return "neutral";
}

function polarToCartesian(angleDeg, radius) {
  const rad = (angleDeg - 90) * Math.PI / 180; // -90 to start from top
  return {
    x: CLOCK_GEOMETRY.cx + radius * Math.cos(rad),
    y: CLOCK_GEOMETRY.cy + radius * Math.sin(rad),
  };
}

const cdkClockMap = computed(() => {
  const menh = cdkChart.value?.menh_branch;
  const starsByBranch = new Map(BRANCHES.map((b) => [b, []]));
  for (const [star, branch] of Object.entries(cdkChart.value?.stars || {})) {
    if (!starsByBranch.has(branch)) starsByBranch.set(branch, []);
    starsByBranch.get(branch).push({
      star,
      branch,
      art: chartArtFor(star),
      meaning: starMeaningFor(star, branch),
    });
  }

  // Find which Tam hợp cục contains Mệnh
  let menhTamHopCuc = null;
  let menhTamHopBranches = [];
  for (const [cucName, branches] of Object.entries(TAM_HOP_CUC)) {
    if (branches.includes(menh)) {
      menhTamHopCuc = cucName;
      menhTamHopBranches = branches;
      break;
    }
  }
  // Xung chiếu = opposite chi (180°)
  const menhIndex = BRANCHES.indexOf(menh);
  const xungChieuBranch = menhIndex >= 0 ? BRANCHES[(menhIndex + 6) % 12] : null;

  // Build 12 nodes
  const nodes = BRANCHES.map((branch, i) => {
    const angle = i * 30; // start Tý at top (i=0), clockwise
    const pos = polarToCartesian(angle, CLOCK_GEOMETRY.ringRadius);
    const stars = starsByBranch.get(branch) || [];
    const isMenh = branch === menh;
    const isTamHopWithMenh = !isMenh && menhTamHopBranches.includes(branch);
    const isXungChieu = branch === xungChieuBranch;
    // Determine tone — Mệnh > dominant star category
    let tone = "neutral";
    if (isMenh) tone = "menh";
    else if (stars.length) {
      // Pick dominant category from stars at this branch (hung > âm > dương > cát > other)
      const priority = { hung: 4, "âm": 3, "dương": 2, "cát": 1 };
      const sorted = [...stars].sort((a, b) => (priority[b.meaning?.category] || 0) - (priority[a.meaning?.category] || 0));
      tone = categoryToTone(sorted[0]?.meaning?.category, false);
    }
    return {
      branch,
      angle,
      x: pos.x,
      y: pos.y,
      stars,
      isMenh,
      isTamHopWithMenh,
      isXungChieu,
      tone,
    };
  });

  // Build tam hợp triangle polygon points (3 chi nodes connected)
  let tamHopPoints = "";
  if (menhTamHopBranches.length === 3) {
    const triPositions = menhTamHopBranches.map((b) => {
      const i = BRANCHES.indexOf(b);
      return polarToCartesian(i * 30, CLOCK_GEOMETRY.ringRadius);
    });
    tamHopPoints = triPositions.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
  }

  // Xung chiếu line endpoints
  let xungChieuLine = null;
  if (menh && xungChieuBranch) {
    const menhIdx = BRANCHES.indexOf(menh);
    const xungIdx = BRANCHES.indexOf(xungChieuBranch);
    const p1 = polarToCartesian(menhIdx * 30, CLOCK_GEOMETRY.ringRadius);
    const p2 = polarToCartesian(xungIdx * 30, CLOCK_GEOMETRY.ringRadius);
    xungChieuLine = { x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y };
  }

  return {
    nodes,
    menhTamHopCuc,
    menhTamHopBranches,
    xungChieuBranch,
    tamHopPoints,
    xungChieuLine,
    geometry: CLOCK_GEOMETRY,
  };
});

async function fetchJsonOrNull(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const text = await response.text();
    if (!response.ok || !text) return null;
    return JSON.parse(text);
  } catch (err) {
    console.warn("Cannot load Chiếu Đởm Kinh payload:", url, err);
    return null;
  }
}

function phiTinhArtFor(star) {
  const card = phiTinhCardsByStarId.value.get(star?.id);
  return card?.image ? card : null;
}

function chartArtFor(starName) {
  const starId = CHART_STAR_ID[starName];
  if (!starId) return null;
  const card = phiTinhCardsByStarId.value.get(starId);
  return card?.image ? card : null;
}

function schemaMeaningFor(star) {
  const item = nhapCotByStar.value.get(NHAP_COT_STAR_NAME[star?.name_vi] || star?.name_vi);
  return {
    category: item?.category || "",
    summary: item?.verdict_summary || "Đang chờ tổng đoán Nhập Cốt cho sao này.",
    hyCung: item?.hy_cung || star?.an_position_mieu || [],
  };
}

function starMeaningFor(starName, branch) {
  const lookupName = NHAP_COT_STAR_NAME[starName] || starName;
  const item = nhapCotByStar.value.get(lookupName);
  const isHy = item?.hy_cung?.includes(branch) || false;
  return {
    lookupName,
    category: item?.category || "chưa phân loại",
    isHy,
    status: item ? (isHy ? "Hỷ cung" : "Không thuộc hỷ cung") : "Chưa có tổng đoán",
    summary: item?.verdict_summary || "Chưa có câu tổng đoán trong Nhập Cốt Tiên Kinh.",
    source: item?.source_ref || "",
  };
}

async function loadAll() {
  loading.value = true;
  error.value = "";
  const person = activePerson.value;
  const genderText = String(person?.gender || person?.gender_optional || "nam").toLowerCase();
  const chartPayload = person?.person_key
    ? { person_key: person.person_key }
    : person?.birth_datetime_local
      ? {
          birth_datetime_local: person.birth_datetime_local,
          timezone: person.timezone || "Asia/Ho_Chi_Minh",
          gender: genderText.includes("nữ") || genderText.includes("nu") ? "nữ" : "nam",
          name: person.name || person.label || "Người",
        }
      : null;
  try {
    const [chart, phi, cards, cach, ncot] = await Promise.all([
      chartPayload ? fetchJsonOrNull("/api/tu-vi/q4/chieu-dom-kinh/cast", {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify(chartPayload)
      }) : Promise.resolve(null),
      fetchJsonOrNull("/api/tu-vi/q4/chieu-dom-kinh-phi-tinh"),
      fetchJsonOrNull("/oracle-cards/chieu-dom-kinh/18-phi-tinh/cards.json"),
      fetchJsonOrNull("/api/tu-vi/q4/chieu-dom-kinh-cach-cuc"),
      fetchJsonOrNull("/api/tu-vi/q4/nhap-cot-tien-kinh"),
    ]);
    if (chart && chart.status === "ok") cdkChart.value = chart;
    if (phi?.status === "ok") phiTinh18.value = phi;
    if (cards?.cards) phiTinhCards.value = cards.cards;
    if (cach?.status === "ok") cachCuc.value = cach;
    if (ncot?.status === "ok") nhapCot.value = ncot;
  } catch (e) {
    error.value = String(e.message || e);
  } finally {
    loading.value = false;
  }
}

// Section labels cho deep interpretation từ DeepSeek
const DEEP_SECTION_LABELS = {
  ban_chat_cung: '1️⃣ Bản chất cung — năng lượng nền',
  sao_thu_cung: '2️⃣ Phi Tinh đóng tại đây',
  quan_he_voi_menh: '3️⃣ Quan hệ với Mệnh CDK',
  ap_dung_doi_song: '4️⃣ Áp dụng vào đời sống',
  loi_khuyen: '5️⃣ Lời khuyên cụ thể',
};

// Render markdown inline (bold **text** + italic _text_)
function renderMarkdownInline(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/_([^_]+)_/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

onMounted(async () => {
  await loadAll();
  await loadCdkDeepFeature();
});

function toggleStar(id) {
  activeStarId.value = activeStarId.value === id ? null : id;
}

function openArtCard(card) {
  if (card) selectedArtCard.value = card;
}

// Click chi node → set selected (default = Mệnh)
function selectBranch(branch) {
  selectedBranch.value = selectedBranch.value === branch ? null : branch;
}

// Build static interpretation Việt thuần dựa vào branch + sao + relationship
function buildQuickInterpretation(branch, info, stars, relKey, menhTamHopCuc) {
  const out = [];
  // Lớp 1: bản chất chi
  if (relKey === "menh") {
    out.push(
      `**Mệnh CDK của Anh đóng tại ${branch} (${info.conGiap}, hành ${info.ngu_hanh}, ${info.am_duong}).** ` +
      `Điều này nghĩa là phần "lõi bản mệnh" của Anh thuộc về vùng năng lượng ${info.ngu_hanh}-${info.am_duong}, ` +
      `gắn với khoảnh khắc **${info.gio}** và phương **${info.phuongVi}**. ` +
      `Bản chất Anh mang nét: _${info.y_nghia.toLowerCase()}_`
    );
  } else if (relKey === "tam-hop") {
    out.push(
      `Cung **${branch} (${info.conGiap})** **tam hợp ${menhTamHopCuc} cục** với Mệnh CDK. ` +
      `Nghĩa là vùng năng lượng ở đây **đồng nhịp** với bản mệnh của Anh — ` +
      `khi Đại Hạn hoặc Lưu Niên đi qua ${branch}, các sao ở đây sẽ **hỗ trợ tăng cường** cho Mệnh.`
    );
  } else if (relKey === "xung-chieu") {
    out.push(
      `Cung **${branch} (${info.conGiap})** nằm **đối diện 180°** với Mệnh CDK — đây là cung **xung chiếu**. ` +
      `Khi Đại Hạn/Lưu Niên chạm tới đây, các sao tại ${branch} sẽ tạo **lực kéo ngược, áp lực đối kháng** với bản mệnh — ` +
      `Anh cần thận trọng những giai đoạn này.`
    );
  } else {
    out.push(
      `Cung **${branch} (${info.conGiap})** là vùng **phụ trợ** đối với Mệnh CDK của Anh. ` +
      `Năng lượng ${info.ngu_hanh}-${info.am_duong} ở đây chỉ kích hoạt mạnh khi Đại Hạn đi qua, ` +
      `bình thường nó "ngủ yên".`
    );
  }
  // Lớp 2: phân tích sao đang đóng
  if (stars.length === 0) {
    out.push(`Hiện tại không có Phi Tinh nào đóng tại ${branch} — vùng này yên tĩnh.`);
  } else {
    const namedStars = stars.map((s) => s.star).join(", ");
    const hyCount = stars.filter((s) => s.meaning.isHy).length;
    const hungCount = stars.filter((s) => /hung/i.test(s.meaning.category || "")).length;
    const amCount = stars.filter((s) => /âm/i.test(s.meaning.category || "")).length;
    let starsLine = `Có **${stars.length} Phi Tinh** đang đóng tại ${branch}: **${namedStars}**. `;
    if (relKey === "menh") {
      if (hyCount === stars.length) {
        starsLine += `Tuyệt vời — TẤT CẢ đều ở **hỷ cung** → Mệnh CDK của Anh rất đắc địa, lực vượng.`;
      } else if (hyCount === 0) {
        starsLine += `Đáng tiếc — KHÔNG sao nào ở hỷ cung của ${branch} (${stars.length}/${stars.length} thất vị). ` +
                     `Đây là dấu hiệu Mệnh CDK của Anh **khắc nghiệt**, đòi hỏi tu thân + kỷ luật.`;
      } else {
        starsLine += `${hyCount}/${stars.length} sao đắc hỷ cung — Mệnh phân lực, vừa thuận vừa nghịch.`;
      }
      if (hungCount >= 2) {
        starsLine += ` Có **${hungCount} sao thuộc nhóm hung** → khắc nghiệt thêm, nhưng cũng là lực rèn người.`;
      }
      if (amCount >= 1) {
        starsLine += ` Sao âm (${amCount}) tại Mệnh = chiều sâu nội tâm.`;
      }
    } else {
      starsLine += `Khi vận hạn chạm vào ${branch}, các sao này sẽ kích hoạt — ` +
                   `${hyCount}/${stars.length} đắc hỷ cung tại đây.`;
    }
    out.push(starsLine);
  }
  // Lớp 3: ý nghĩa thực tế
  if (relKey === "menh") {
    out.push(
      `**Trong đời sống**: vì ${info.conGiap} thuộc giờ **${info.gio}**, ` +
      `Anh có xu hướng năng lượng đạt đỉnh / có ý nghĩa quan trọng vào khoảng thời gian này trong ngày. ` +
      `Phương ${info.phuongVi} là hướng tốt cho công việc, nghỉ ngơi, hoặc kết nối quan trọng.`
    );
  }
  return out;
}

// Selected branch info — defaults to Mệnh CDK
const selectedBranchInfo = computed(() => {
  const branch = selectedBranch.value || cdkChart.value?.menh_branch;
  if (!branch) return null;
  const node = cdkClockMap.value?.nodes?.find((n) => n.branch === branch);
  const info = BRANCH_INFO[branch];
  if (!node || !info) return null;
  // Determine relationship with Mệnh
  let relationship = "Bình thường (không tương tác trực tiếp với Mệnh)";
  let relKey = "normal";
  if (node.isMenh) {
    relationship = "Đây chính là cung Mệnh CDK của Anh.";
    relKey = "menh";
  } else if (node.isTamHopWithMenh) {
    relationship = `Tam hợp ${cdkClockMap.value.menhTamHopCuc} cục với Mệnh — phối hợp tốt, hỗ trợ.`;
    relKey = "tam-hop";
  } else if (node.isXungChieu) {
    relationship = "Xung chiếu (đối diện 180°) với Mệnh — tạo áp lực, lực kéo ngược.";
    relKey = "xung-chieu";
  }
  const quickInterpretation = buildQuickInterpretation(
    branch, info, node.stars, relKey, cdkClockMap.value?.menhTamHopCuc
  );
  return {
    branch,
    ...info,
    stars: node.stars,
    isMenh: node.isMenh,
    relationship,
    relKey,
    quickInterpretation,
  };
});

// ─── Deep interpretation by DeepSeek (VIP) ─────────────────────────────────
const cdkDeepInterp = ref({});  // {branchKey: {loading, data, error}}
const cdkDeepFeature = ref(null);  // VIP feature status

async function loadCdkDeepFeature() {
  try {
    const r = await fetch('/api/user/my-vip-features');
    if (!r.ok) return;
    const d = await r.json();
    cdkDeepFeature.value = (d.features || []).find((f) => f.feature_id === 'tu_vi_cdk_luan_cung') || null;
  } catch (e) {
    console.warn('Cannot load VIP features:', e);
  }
}

async function loadDeepInterp(branch, force = false) {
  const person = activePerson.value;
  if (!person?.birth_datetime_local && !person?.person_key) return;
  const key = `${person.person_key || person.birth_datetime_local}_${branch}`;
  if (!cdkDeepInterp.value[key]) cdkDeepInterp.value[key] = { loading: false, data: null, error: null };
  const slot = cdkDeepInterp.value[key];
  slot.loading = true;
  slot.error = null;
  try {
    const genderText = String(person?.gender || 'nam').toLowerCase();
    const payload = {
      branch,
      force,
      ...(person.person_key
        ? { person_key: person.person_key }
        : {
            birth_datetime_local: person.birth_datetime_local,
            gender: genderText.includes('nữ') || genderText.includes('nu') ? 'nữ' : 'nam',
            timezone: person.timezone || 'Asia/Ho_Chi_Minh',
            name: person.name || 'Người',
          }),
    };
    const resp = await fetch('/api/tu-vi/q4/cdk/luan-cung', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (data.status === 'ok') {
      slot.data = data;
    } else {
      slot.error = data.message || 'Lỗi không xác định';
    }
  } catch (e) {
    slot.error = String(e.message || e);
  } finally {
    slot.loading = false;
    // Refresh VIP feature uses
    loadCdkDeepFeature();
  }
}

function getDeepInterpSlot(branch) {
  const person = activePerson.value;
  const key = `${person?.person_key || person?.birth_datetime_local}_${branch}`;
  return cdkDeepInterp.value[key] || { loading: false, data: null, error: null };
}

const cdkDeepFeatureStatus = computed(() => {
  const f = cdkDeepFeature.value;
  if (!f) return { allowed: false, label: '🔒 Chưa cấp VIP1', reason: 'no_data' };
  if (!f.has_subscription) return { allowed: false, label: '🔒 Cần VIP1', reason: 'no_subscription' };
  if (!f.allowed) return { allowed: false, label: `🔒 ${f.reason || 'Bị khóa'}`, reason: f.reason };
  return {
    allowed: true,
    label: `✓ VIP1 — Còn ${f.subscription?.remaining_uses ?? '∞'} lượt`,
    reason: 'ok',
    remaining: f.subscription?.remaining_uses,
  };
});
</script>

<template>
  <section class="cdk-panel">
    <header class="cdk-head">
      <h2>📜 Chiếu Đởm Kinh — Phái khác Tử Vi Đẩu Số</h2>
      <p class="cdk-sub">
        Kinh phái khác trong Q4 (p0269-p0300) — <b>18 Phi Tinh</b> (KHÁC 14 chính tinh chính thống) +
        convention âm-dương ĐẢO + an sao formula riêng.
      </p>
    </header>

    <p v-if="loading" class="cdk-loading">Đang tải...</p>
    <p v-if="error" class="cdk-error">⚠ {{ error }}</p>

    <!-- Anh's chart CDK -->
    <section v-if="cdkChart" class="cdk-chart">
      <h3>🌟 Lá số CDK của anh</h3>
      <div class="cdk-meta">
        <span><b>Mệnh CDK:</b> {{ cdkChart.menh_branch }}</span>
        <span><b>Năm:</b> {{ cdkChart.year_stem }} {{ cdkChart.year_branch }}</span>
        <span><b>Tháng âm:</b> {{ cdkChart.lunar_month }}</span>
        <span><b>Giờ:</b> {{ cdkChart.hour_branch }}</span>
      </div>
      <div class="cdk-chart-guide">
        <div>
          <b>1. An sao</b>
          <span>Engine đặt từng Phi Tinh vào một địa chi: ví dụ “Tử → Hợi” nghĩa là sao Tử đang đóng cung Hợi.</span>
        </div>
        <div>
          <b>2. Ảnh sao</b>
          <span>Ảnh là pháp tượng của sao, không phải ảnh cung. Sao nào đã vẽ sẽ hiện thumbnail; bấm để mở bản gốc.</span>
        </div>
        <div>
          <b>3. Luận nghĩa</b>
          <span>Đọc theo cặp “sao + cung đang đóng”, rồi đối chiếu Đại Hạn CDK bên dưới.</span>
        </div>
      </div>

      <div class="cdk-chart-core">
        <section class="cdk-menh-core">
          <span class="cdk-core-label">Mệnh CDK</span>
          <strong>{{ cdkChart.menh_branch }}</strong>
          <small>Điểm tụ bản mệnh trong hệ Chiếu Đởm Kinh</small>
        </section>
        <section class="cdk-menh-stars">
          <header>
            <span>Sao thủ Mệnh</span>
            <b>{{ cdkMenhStars.length }} sao</b>
          </header>
          <article v-for="item in cdkMenhStars" :key="item.star" class="cdk-menh-star">
            <button
              v-if="item.art"
              type="button"
              class="cdk-chart-art"
              :aria-label="`Mở ảnh ${item.star}`"
              @click.stop="openArtCard(item.art)"
            >
              <img :src="item.art.image" :alt="`Ảnh ${item.star}`" loading="lazy" />
            </button>
            <div>
              <h4>{{ item.star }} tại {{ item.branch }}</h4>
              <p>
                <span :class="['cdk-status-chip', item.meaning.isHy ? 'is-hy' : '']">{{ item.meaning.status }}</span>
                <span class="cdk-cat-chip">{{ item.meaning.category }}</span>
              </p>
              <small>{{ item.meaning.summary }}</small>
            </div>
          </article>
        </section>
      </div>

      <h4 class="cdk-map-title">
        Bản đồ 12 địa chi — Đồng hồ Phi Tinh
        <small v-if="cdkClockMap.menhTamHopCuc">
          · Tam hợp <b>{{ cdkClockMap.menhTamHopCuc }} cục</b> (Mệnh + {{ cdkClockMap.menhTamHopBranches.filter((b) => b !== cdkChart.menh_branch).join(' + ') }})
          <span v-if="cdkClockMap.xungChieuBranch"> · Xung chiếu: <b>{{ cdkClockMap.xungChieuBranch }}</b></span>
        </small>
      </h4>
      <div class="cdk-clock-wrap">
        <svg
          class="cdk-clock-svg"
          viewBox="0 0 480 480"
          xmlns="http://www.w3.org/2000/svg"
          role="img"
          aria-label="Bản đồ 12 địa chi Chiếu Đởm Kinh"
        >
          <!-- Outer ring + ticks -->
          <circle :cx="cdkClockMap.geometry.cx" :cy="cdkClockMap.geometry.cy" r="220"
                  class="cdk-clock-ring-outer" />
          <circle :cx="cdkClockMap.geometry.cx" :cy="cdkClockMap.geometry.cy"
                  :r="cdkClockMap.geometry.ringRadius" class="cdk-clock-ring-mid" />
          <circle :cx="cdkClockMap.geometry.cx" :cy="cdkClockMap.geometry.cy"
                  :r="cdkClockMap.geometry.coreRadius" class="cdk-clock-ring-inner" />

          <!-- Tam hợp triangle (Mệnh's cục) -->
          <polygon
            v-if="cdkClockMap.tamHopPoints"
            :points="cdkClockMap.tamHopPoints"
            class="cdk-clock-tam-hop"
          />

          <!-- Xung chiếu line -->
          <line
            v-if="cdkClockMap.xungChieuLine"
            :x1="cdkClockMap.xungChieuLine.x1"
            :y1="cdkClockMap.xungChieuLine.y1"
            :x2="cdkClockMap.xungChieuLine.x2"
            :y2="cdkClockMap.xungChieuLine.y2"
            class="cdk-clock-xung-chieu"
          />

          <!-- 12 chi nodes (clickable) -->
          <g v-for="node in cdkClockMap.nodes" :key="node.branch"
             :class="['cdk-clock-node', `tone-${node.tone}`,
                      node.isMenh && 'is-menh',
                      node.isTamHopWithMenh && 'is-tam-hop',
                      node.isXungChieu && 'is-xung-chieu',
                      (selectedBranch || cdkChart.menh_branch) === node.branch && 'is-selected']"
             @click="selectBranch(node.branch)"
             style="cursor: pointer;">
            <circle :cx="node.x" :cy="node.y" :r="cdkClockMap.geometry.nodeRadius"
                    class="cdk-clock-node-bg" />
            <text :x="node.x" :y="node.y - 12" class="cdk-clock-chi"
                  text-anchor="middle">{{ node.branch }}</text>
            <text v-if="node.isMenh" :x="node.x" :y="node.y - 26"
                  class="cdk-clock-menh-tag" text-anchor="middle">★ MỆNH</text>
            <text v-for="(st, idx) in node.stars" :key="st.star"
                  :x="node.x" :y="node.y + 4 + idx * 11"
                  class="cdk-clock-star-name"
                  :class="{'is-hy': st.meaning.isHy}"
                  text-anchor="middle">{{ st.star }}</text>
            <title>{{ node.branch }} — {{ BRANCH_INFO[node.branch]?.conGiap }} · {{ BRANCH_INFO[node.branch]?.gio }}{{ node.isMenh ? ' · MỆNH' : node.isTamHopWithMenh ? ' · tam hợp' : node.isXungChieu ? ' · xung chiếu' : '' }}</title>
          </g>

          <!-- Center: Mệnh info -->
          <g class="cdk-clock-center">
            <text :x="cdkClockMap.geometry.cx" :y="cdkClockMap.geometry.cy - 36"
                  class="cdk-clock-core-label" text-anchor="middle">MỆNH CDK</text>
            <text :x="cdkClockMap.geometry.cx" :y="cdkClockMap.geometry.cy + 8"
                  class="cdk-clock-core-branch" text-anchor="middle">{{ cdkChart.menh_branch }}</text>
            <text :x="cdkClockMap.geometry.cx" :y="cdkClockMap.geometry.cy + 36"
                  class="cdk-clock-core-stars" text-anchor="middle">
              {{ cdkMenhStars.map((s) => s.star).join(' · ') }}
            </text>
            <text :x="cdkClockMap.geometry.cx" :y="cdkClockMap.geometry.cy + 56"
                  class="cdk-clock-core-count" text-anchor="middle">
              {{ cdkMenhStars.length }} sao thủ
            </text>
          </g>
        </svg>

        <!-- Hint -->
        <p class="cdk-clock-hint">
          💡 Bấm vào bất kỳ con giáp nào để xem giải thích Việt thuần.
          Mặc định đang xem cung Mệnh ({{ cdkChart.menh_branch }}).
        </p>

        <!-- Legend -->
        <div class="cdk-clock-legend">
          <span class="leg-item tone-menh"><span class="dot"></span>Mệnh CDK</span>
          <span class="leg-item tone-tam-hop"><span class="dot"></span>Tam hợp với Mệnh</span>
          <span class="leg-item tone-xung-chieu"><span class="dot"></span>Xung chiếu (đối diện)</span>
          <span class="leg-item tone-cat"><span class="dot"></span>Cát</span>
          <span class="leg-item tone-hung"><span class="dot"></span>Hung</span>
          <span class="leg-item tone-am"><span class="dot"></span>Âm</span>
          <span class="leg-item tone-duong"><span class="dot"></span>Dương</span>
        </div>

        <!-- Drawer info Việt thuần -->
        <transition name="cdk-drawer">
          <article v-if="selectedBranchInfo" :key="selectedBranchInfo.branch"
                   :class="['cdk-branch-drawer', `rel-${selectedBranchInfo.relKey}`]">
            <header class="cdk-drawer-head">
              <div class="cdk-drawer-title">
                <span class="cdk-drawer-chi">{{ selectedBranchInfo.branch }}</span>
                <span class="cdk-drawer-con-giap">— {{ selectedBranchInfo.conGiap }}</span>
              </div>
              <span class="cdk-drawer-rel">{{ selectedBranchInfo.relationship }}</span>
            </header>
            <div class="cdk-drawer-grid">
              <div class="cdk-drawer-fact">
                <small>🕒 Giờ trong ngày</small>
                <b>{{ selectedBranchInfo.gio }}</b>
              </div>
              <div class="cdk-drawer-fact">
                <small>🧭 Phương vị</small>
                <b>{{ selectedBranchInfo.phuongVi }}</b>
              </div>
              <div class="cdk-drawer-fact">
                <small>☯ Ngũ hành · Âm-Dương</small>
                <b>{{ selectedBranchInfo.ngu_hanh }} · {{ selectedBranchInfo.am_duong }}</b>
              </div>
              <div class="cdk-drawer-fact cdk-drawer-meaning">
                <small>💭 Ý nghĩa khoảnh khắc</small>
                <b>{{ selectedBranchInfo.y_nghia }}</b>
              </div>
            </div>
            <div v-if="selectedBranchInfo.stars.length" class="cdk-drawer-stars">
              <h5>Phi Tinh đang đóng tại {{ selectedBranchInfo.branch }} ({{ selectedBranchInfo.stars.length }} sao)</h5>
              <article v-for="st in selectedBranchInfo.stars" :key="st.star" class="cdk-drawer-star">
                <header>
                  <strong>{{ st.star }}</strong>
                  <span :class="['cdk-status-chip', st.meaning.isHy ? 'is-hy' : '']">{{ st.meaning.status }}</span>
                  <span class="cdk-cat-chip">{{ st.meaning.category }}</span>
                </header>
                <small>{{ st.meaning.summary }}</small>
              </article>
            </div>
            <p v-else class="cdk-drawer-empty">Cung {{ selectedBranchInfo.branch }} không có Phi Tinh nào đóng — vùng "tĩnh" chỉ kích hoạt khi Đại Hạn chạm tới.</p>

            <!-- Quick interpretation (instant, free) -->
            <section v-if="selectedBranchInfo.quickInterpretation?.length" class="cdk-drawer-interp">
              <h5>📖 Nghĩa cung {{ selectedBranchInfo.branch }} cho Anh</h5>
              <p v-for="(para, i) in selectedBranchInfo.quickInterpretation" :key="i" v-html="renderMarkdownInline(para)"></p>
            </section>

            <!-- VIP Deep interpretation by DeepSeek V4 Pro -->
            <section class="cdk-drawer-deep">
              <header class="cdk-deep-head">
                <h5>🌟 Luận giải SÂU bởi DeepSeek V4 Pro</h5>
                <span :class="['cdk-vip-badge', cdkDeepFeatureStatus.allowed ? 'is-ok' : 'is-locked']">
                  {{ cdkDeepFeatureStatus.label }}
                </span>
              </header>
              <div v-if="getDeepInterpSlot(selectedBranchInfo.branch).loading" class="cdk-deep-loading">
                <span class="cdk-spinner"></span>
                Đang nhờ DeepSeek V4 Pro phân tích cung {{ selectedBranchInfo.branch }}... (60-90s)
              </div>
              <p v-else-if="getDeepInterpSlot(selectedBranchInfo.branch).error" class="cdk-deep-error">
                ⚠ {{ getDeepInterpSlot(selectedBranchInfo.branch).error }}
              </p>
              <div v-else-if="getDeepInterpSlot(selectedBranchInfo.branch).data" class="cdk-deep-content">
                <div v-for="(section, key) in getDeepInterpSlot(selectedBranchInfo.branch).data.luan_cung || {}" :key="key" class="cdk-deep-section">
                  <h6>{{ DEEP_SECTION_LABELS[key] || key }}</h6>
                  <p v-html="renderMarkdownInline(String(section))"></p>
                </div>
                <small class="cdk-deep-meta">
                  Provider: {{ getDeepInterpSlot(selectedBranchInfo.branch).data.provider }} ·
                  Đã tự lưu vào wiki ✓
                </small>
                <button v-if="cdkDeepFeatureStatus.allowed" type="button"
                        class="cdk-deep-regen"
                        @click="loadDeepInterp(selectedBranchInfo.branch, true)">
                  🔄 Viết lại
                </button>
              </div>
              <button v-else type="button"
                      class="cdk-deep-btn"
                      :disabled="!cdkDeepFeatureStatus.allowed"
                      @click="loadDeepInterp(selectedBranchInfo.branch)">
                <span v-if="cdkDeepFeatureStatus.allowed">🌟 Gọi DeepSeek V4 Pro luận sâu cung này (60-90s, tự lưu wiki)</span>
                <span v-else>🔒 {{ cdkDeepFeatureStatus.label }} — không thể luận sâu</span>
              </button>
            </section>
          </article>
        </transition>
      </div>

      <!-- Fallback 4×3 grid trong details (chi tiết từng cung) -->
      <details class="cdk-branch-detail">
        <summary>Chi tiết 12 địa chi (xem nâng cao)</summary>
        <div class="cdk-branch-map">
          <article
            v-for="cell in cdkBranchMap"
            :key="cell.branch"
            class="cdk-branch-cell"
            :class="{ 'is-menh': cell.isMenh }"
          >
            <header>
              <strong>{{ cell.branch }}</strong>
              <span v-if="cell.isMenh">Mệnh</span>
            </header>
            <div v-if="cell.stars.length" class="cdk-branch-stars">
              <button
                v-for="item in cell.stars"
                :key="item.star"
                type="button"
                class="cdk-branch-star"
                :class="{ 'has-art': item.art, 'is-hy': item.meaning.isHy }"
                @click.stop="item.art ? openArtCard(item.art) : null"
              >
                <img v-if="item.art" :src="item.art.image" :alt="`Ảnh ${item.star}`" loading="lazy" />
                <span>{{ item.star }}</span>
                <small>{{ item.meaning.isHy ? 'hỷ' : item.meaning.category }}</small>
              </button>
            </div>
            <p v-else>Chưa có Phi Tinh đóng</p>
          </article>
        </div>
      </details>

      <details class="cdk-raw-stars">
        <summary>Bảng sao → cung gốc</summary>
        <div class="cdk-stars-grid">
          <div v-for="(branch, star) in cdkChart.stars" :key="star" class="cdk-star-pos">
            <button
              v-if="chartArtFor(star)"
              type="button"
              class="cdk-chart-art"
              :aria-label="`Mở ảnh ${star}`"
              @click.stop="openArtCard(chartArtFor(star))"
            >
              <img :src="chartArtFor(star).image" :alt="`Ảnh ${star}`" loading="lazy" />
            </button>
            <span class="cdk-star-name">{{ star }}</span>
            <span class="cdk-star-branch">{{ branch }}</span>
          </div>
        </div>
      </details>
      <p v-if="phiTinhCards.length" class="cdk-chart-art-note">
        Lá số này hiện có ảnh minh họa cho
        <b>{{ Object.keys(cdkChart.stars || {}).filter((star) => chartArtFor(star)).length }}</b>
        sao trong bảng. Các sao còn lại sẽ tự hiện khi thợ vẽ đưa PNG đúng tên vào luồng sync.
      </p>
      <details class="cdk-dai-han">
        <summary>Đại Hạn CDK ({{ cdkChart.dai_han_cycles?.length }} cycles)</summary>
        <ul>
          <li v-for="c in cdkChart.dai_han_cycles" :key="c.cycle_index">
            Cycle {{ c.cycle_index }}: <b>{{ c.branch }}</b> (tuổi {{ c.start_age }}-{{ c.end_age }})
          </li>
        </ul>
      </details>
      <p class="cdk-paradigm-note">⚠ {{ cdkChart.paradigm_note }}</p>
    </section>

    <!-- 18 Phi Tinh schema -->
    <section v-if="phiTinh18" class="cdk-section">
      <h3>🌌 18 Phi Tinh — schema</h3>
      <p class="cdk-warning">{{ phiTinh18.warning_convention }}</p>
      <p v-if="phiTinhCards.length" class="cdk-art-status">
        Bộ ảnh Chiếu Đởm Kinh: <b>{{ phiTinhCards.filter((card) => card.image).length }}/18</b> thẻ đã web-ready.
        Ảnh nhỏ dùng WebP nhẹ; bấm ảnh để mở bản gốc.
      </p>
      <div class="cdk-tier-grid">
        <div class="cdk-tier cdk-tier-duong">
          <h4>9 Dương tinh</h4>
          <article v-for="s in phiTinh18.phi_tinh_9_duong" :key="s.id"
            class="cdk-phi-card cdk-phi-large" :class="{active: activeStarId === s.id}"
            @click="toggleStar(s.id)">
            <button
              v-if="phiTinhArtFor(s)"
              type="button"
              class="cdk-phi-art"
              :aria-label="`Mở ảnh ${s.name_vi}`"
              @click.stop="openArtCard(phiTinhArtFor(s))"
            >
              <img :src="phiTinhArtFor(s).image" :alt="`Ảnh ${s.name_vi}`" loading="lazy" />
            </button>
            <div class="cdk-phi-copy">
              <header>
                <strong>{{ s.name_vi }}</strong>
                <small>({{ s.name_zh }})</small>
              </header>
              <small>{{ s.ngu_hanh }} · {{ s.polarity }}</small>
              <p class="cdk-phi-summary">{{ schemaMeaningFor(s).summary }}</p>
              <p v-if="schemaMeaningFor(s).hyCung.length" class="cdk-phi-hy">
                <b>Hỷ:</b>
                <span v-for="c in schemaMeaningFor(s).hyCung" :key="c">{{ c }}</span>
              </p>
              <span v-if="schemaMeaningFor(s).category" class="cdk-phi-category">{{ schemaMeaningFor(s).category }}</span>
            </div>
            <div v-if="activeStarId === s.id" class="cdk-phi-detail">
              <p v-if="s.an_position_mieu"><b>Miếu vị:</b> {{ s.an_position_mieu.join(' · ') }}</p>
              <p v-if="s.an_position"><b>An tại:</b> {{ s.an_position }}</p>
              <p v-if="s.an_position_chinh"><b>Chính vị:</b> {{ s.an_position_chinh }}</p>
              <small>Nguồn: {{ s.source_ref }}</small>
            </div>
          </article>
        </div>
        <div class="cdk-tier cdk-tier-am">
          <h4>9 Âm tinh</h4>
          <article v-for="s in phiTinh18.phi_tinh_9_am" :key="s.id"
            class="cdk-phi-card cdk-phi-large cdk-phi-am" :class="{active: activeStarId === s.id}"
            @click="toggleStar(s.id)">
            <button
              v-if="phiTinhArtFor(s)"
              type="button"
              class="cdk-phi-art"
              :aria-label="`Mở ảnh ${s.name_vi}`"
              @click.stop="openArtCard(phiTinhArtFor(s))"
            >
              <img :src="phiTinhArtFor(s).image" :alt="`Ảnh ${s.name_vi}`" loading="lazy" />
            </button>
            <div class="cdk-phi-copy">
              <header>
                <strong>{{ s.name_vi }}</strong>
                <small>({{ s.name_zh }})</small>
              </header>
              <small>{{ s.ngu_hanh }} · {{ s.polarity }}</small>
              <p class="cdk-phi-summary">{{ schemaMeaningFor(s).summary }}</p>
              <p v-if="schemaMeaningFor(s).hyCung.length" class="cdk-phi-hy">
                <b>Hỷ:</b>
                <span v-for="c in schemaMeaningFor(s).hyCung" :key="c">{{ c }}</span>
              </p>
              <span v-if="schemaMeaningFor(s).category" class="cdk-phi-category">{{ schemaMeaningFor(s).category }}</span>
            </div>
            <div v-if="activeStarId === s.id" class="cdk-phi-detail">
              <p v-if="s.an_position_mieu"><b>Miếu vị:</b> {{ s.an_position_mieu.join(' · ') }}</p>
              <p v-if="s.an_position_chinh"><b>Chính vị:</b> {{ s.an_position_chinh }}</p>
              <small>Nguồn: {{ s.source_ref }}</small>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- 6 cách cục mới -->
    <section v-if="cachCuc" class="cdk-section">
      <h3>📐 6 Cách cục mới — Chiếu Đởm Kinh</h3>
      <article v-for="c in cachCuc.cach_cuc" :key="c.id" class="cdk-cach-card"
               :class="`cdk-cach-${c.polarity.replaceAll('_', '-')}`">
        <header>
          <strong>{{ c.name_vi }}</strong>
          <small class="cdk-zh">{{ c.name_zh }}</small>
          <span class="cdk-polarity-badge">{{ c.polarity }}</span>
        </header>
        <p class="cdk-lesson">{{ c.lesson_short }}</p>
        <details>
          <summary>Câu sách + paradigm</summary>
          <em>« {{ c.source_quote_hv }} »</em>
          <p v-if="c.paradigm_note" class="cdk-paradigm">💡 {{ c.paradigm_note }}</p>
          <small>Nguồn: {{ c.source_ref }}</small>
        </details>
      </article>
    </section>

    <!-- Nhập Cốt Tiên Kinh tổng đoán -->
    <section v-if="nhapCot" class="cdk-section">
      <h3>📚 Nhập Cốt Tiên Kinh — Tổng đoán 4-chữ</h3>
      <p class="cdk-intro">{{ nhapCot.subtitle_meaning }}</p>
      <details>
        <summary>Intro (verbatim Q4 p0297 r005-r007)</summary>
        <em>« {{ nhapCot.intro_hv }} »</em>
        <p>{{ nhapCot.intro_meaning }}</p>
      </details>
      <div class="cdk-tong-doan-grid">
        <article v-for="t in nhapCot.per_star_tong_doan" :key="t.star"
                 class="cdk-tong-doan-card" :class="`cdk-tong-${t.category}`">
          <header>
            <strong>{{ t.star }}</strong>
            <span class="cdk-cat-badge">{{ t.category }}</span>
          </header>
          <p class="cdk-tong-verdict">{{ t.verdict_summary }}</p>
          <p v-if="t.hy_cung" class="cdk-hy-cung">
            <b>Hỷ:</b>
            <span v-for="c in t.hy_cung" :key="c" class="cdk-hy-chip">{{ c }}</span>
          </p>
          <details>
            <summary>Verbatim</summary>
            <em>« {{ t.verdict_quote_hv }} »</em>
            <p v-if="t.warning" class="cdk-warning-inline">⚠ {{ t.warning }}</p>
            <small>{{ t.source_ref }}</small>
          </details>
        </article>
      </div>

      <!-- Ending paradigm -->
      <section v-if="nhapCot.ending_paradigm" class="cdk-ending">
        <h4>🔚 Paradigm kết quyển</h4>
        <blockquote>{{ nhapCot.ending_paradigm.source_quote_hv }}</blockquote>
        <p>{{ nhapCot.ending_paradigm.meaning }}</p>
        <p class="cdk-iron-rule">⚠ {{ nhapCot.ending_paradigm.iron_rule_note }}</p>
      </section>
    </section>

    <div v-if="selectedArtCard" class="cdk-art-lightbox" @click="selectedArtCard = null">
      <figure @click.stop>
        <button type="button" class="cdk-lightbox-close" @click="selectedArtCard = null">×</button>
        <img :src="selectedArtCard.full_image || selectedArtCard.image" :alt="selectedArtCard.title" />
        <figcaption>
          <b>{{ selectedArtCard.index }}. {{ selectedArtCard.title }} {{ selectedArtCard.name_zh }}</b>
          <span>{{ selectedArtCard.polarity }} · {{ selectedArtCard.element }} · {{ selectedArtCard.id }}</span>
        </figcaption>
      </figure>
    </div>
  </section>
</template>

<style scoped>
.cdk-panel {
  padding: 20px;
  background: linear-gradient(180deg, rgba(20, 30, 45, 0.95), rgba(15, 23, 42, 0.95));
  color: #e6eef5;
  border-radius: 10px;
  max-width: 1200px;
  margin: 0 auto;
}
.cdk-head h2 { color: #c4b5fd; margin: 0 0 6px; font-size: 22px; }
.cdk-sub { font-size: 13px; color: rgba(230, 238, 245, 0.78); line-height: 1.6; margin: 0 0 16px; }
.cdk-sub b { color: #fcd34d; }
.cdk-loading { text-align: center; padding: 20px; color: #a78bfa; }
.cdk-error { color: #f87171; padding: 12px; }

.cdk-chart {
  margin: 20px 0;
  padding: 16px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.08), rgba(20, 30, 45, 0.4));
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 8px;
}
.cdk-chart h3 { margin: 0 0 10px; color: #c4b5fd; font-size: 16px; }
.cdk-meta { display: flex; gap: 16px; flex-wrap: wrap; margin: 10px 0; font-size: 13px; }
.cdk-meta b { color: rgba(230, 238, 245, 0.55); margin-right: 4px; font-weight: 500; }
.cdk-chart-guide {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 12px 0;
}
.cdk-chart-guide div {
  padding: 10px 12px;
  background: rgba(2, 6, 23, 0.24);
  border: 1px solid rgba(167, 139, 250, 0.18);
  border-radius: 6px;
}
.cdk-chart-guide b {
  display: block;
  color: #f5e6b1;
  font-size: 12px;
  margin-bottom: 4px;
}
.cdk-chart-guide span {
  display: block;
  color: rgba(230, 238, 245, 0.68);
  font-size: 11.5px;
  line-height: 1.45;
}
.cdk-chart-core {
  display: grid;
  grid-template-columns: minmax(180px, 0.85fr) minmax(0, 2fr);
  gap: 12px;
  align-items: stretch;
  margin: 14px 0;
}
.cdk-menh-core {
  display: grid;
  place-items: center;
  align-content: center;
  min-height: 190px;
  padding: 18px;
  text-align: center;
  border: 1px solid rgba(252, 211, 77, 0.46);
  border-radius: 8px;
  background:
    radial-gradient(circle at center, rgba(252, 211, 77, 0.16), rgba(91, 229, 211, 0.04) 58%, rgba(2, 6, 23, 0.2)),
    rgba(2, 6, 23, 0.28);
}
.cdk-core-label {
  color: rgba(230, 238, 245, 0.58);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}
.cdk-menh-core strong {
  margin: 8px 0;
  color: #fcd34d;
  font-size: 56px;
  line-height: 1;
}
.cdk-menh-core small {
  max-width: 190px;
  color: rgba(230, 238, 245, 0.68);
  font-size: 12px;
  line-height: 1.45;
}
.cdk-menh-stars {
  padding: 12px;
  border: 1px solid rgba(167, 139, 250, 0.24);
  border-radius: 8px;
  background: rgba(2, 6, 23, 0.22);
}
.cdk-menh-stars > header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #f5e6b1;
  font-size: 13px;
  font-weight: 700;
}
.cdk-menh-stars > header b {
  color: #5be5d3;
  font-size: 12px;
}
.cdk-menh-star {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  padding: 10px 0;
  border-top: 1px solid rgba(230, 238, 245, 0.08);
}
.cdk-menh-star:first-of-type { border-top: 0; }
.cdk-menh-star h4 {
  margin: 0 0 5px;
  color: #fcd34d;
  font-size: 14px;
}
.cdk-menh-star p {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin: 0 0 6px;
}
.cdk-menh-star small {
  display: block;
  color: rgba(230, 238, 245, 0.74);
  font-size: 12px;
  line-height: 1.45;
}
.cdk-status-chip,
.cdk-cat-chip {
  display: inline-flex;
  align-items: center;
  min-height: 20px;
  padding: 2px 7px;
  border-radius: 4px;
  background: rgba(148, 163, 184, 0.14);
  color: rgba(230, 238, 245, 0.74);
  font-size: 11px;
  font-weight: 600;
}
.cdk-status-chip.is-hy {
  background: rgba(91, 229, 211, 0.14);
  color: #5be5d3;
}
.cdk-cat-chip {
  background: rgba(252, 211, 77, 0.12);
  color: #f5e6b1;
}
.cdk-map-title {
  margin: 20px 0 10px;
  color: #f5e6b1;
  font-size: 14px;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 10px;
}
.cdk-map-title small {
  color: rgba(230, 238, 245, 0.64);
  font-size: 12px;
  font-weight: 400;
}
.cdk-map-title small b {
  color: #fcd34d;
  font-weight: 600;
}

/* ─── CDK Clock Map (đồng hồ tròn 12 địa chi) ─────────────────────────── */
.cdk-clock-wrap {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  justify-items: center;
  margin: 14px 0 22px;
  padding: 18px;
  background:
    radial-gradient(circle at center, rgba(252, 211, 77, 0.05), rgba(2, 6, 23, 0.6) 70%),
    rgba(2, 6, 23, 0.3);
  border: 1px solid rgba(167, 139, 250, 0.16);
  border-radius: 12px;
}
.cdk-clock-svg {
  width: min(480px, 100%);
  height: auto;
  display: block;
}
.cdk-clock-ring-outer {
  fill: none;
  stroke: rgba(167, 139, 250, 0.16);
  stroke-width: 1;
  stroke-dasharray: 2 4;
}
.cdk-clock-ring-mid {
  fill: none;
  stroke: rgba(91, 229, 211, 0.14);
  stroke-width: 1;
}
.cdk-clock-ring-inner {
  fill: rgba(2, 6, 23, 0.55);
  stroke: rgba(252, 211, 77, 0.42);
  stroke-width: 1.5;
}

/* Tam hợp triangle — vàng nhạt soft */
.cdk-clock-tam-hop {
  fill: rgba(252, 211, 77, 0.07);
  stroke: rgba(252, 211, 77, 0.45);
  stroke-width: 1.5;
  stroke-dasharray: 6 4;
}
/* Xung chiếu — đỏ nhạt dashed */
.cdk-clock-xung-chieu {
  stroke: rgba(248, 113, 113, 0.5);
  stroke-width: 1.5;
  stroke-dasharray: 8 5;
}

/* 12 chi nodes */
.cdk-clock-node {
  cursor: default;
}
.cdk-clock-node-bg {
  fill: rgba(2, 6, 23, 0.7);
  stroke: rgba(230, 238, 245, 0.18);
  stroke-width: 1.5;
  transition: stroke 160ms, fill 160ms;
}
.cdk-clock-node.tone-cat .cdk-clock-node-bg {
  stroke: rgba(91, 229, 211, 0.6);
  fill: rgba(15, 76, 70, 0.32);
}
.cdk-clock-node.tone-hung .cdk-clock-node-bg {
  stroke: rgba(248, 113, 113, 0.6);
  fill: rgba(76, 20, 20, 0.32);
}
.cdk-clock-node.tone-am .cdk-clock-node-bg {
  stroke: rgba(196, 181, 253, 0.55);
  fill: rgba(46, 30, 76, 0.32);
}
.cdk-clock-node.tone-duong .cdk-clock-node-bg {
  stroke: rgba(252, 211, 77, 0.6);
  fill: rgba(76, 56, 16, 0.28);
}
.cdk-clock-node.tone-menh .cdk-clock-node-bg {
  stroke: #fcd34d;
  stroke-width: 2.5;
  fill: rgba(76, 56, 16, 0.5);
  filter: drop-shadow(0 0 6px rgba(252, 211, 77, 0.6));
}
.cdk-clock-node.is-tam-hop .cdk-clock-node-bg {
  stroke-dasharray: none;
}
.cdk-clock-node.is-xung-chieu .cdk-clock-node-bg {
  stroke-width: 2;
}

.cdk-clock-chi {
  font-size: 15px;
  font-weight: 700;
  fill: #f5e6b1;
  user-select: none;
}
.cdk-clock-node.tone-menh .cdk-clock-chi {
  fill: #fcd34d;
  font-size: 17px;
}
.cdk-clock-menh-tag {
  font-size: 8px;
  font-weight: 700;
  fill: #fcd34d;
  letter-spacing: 1px;
}
.cdk-clock-star-name {
  font-size: 10px;
  fill: rgba(230, 238, 245, 0.78);
  user-select: none;
}
.cdk-clock-star-name.is-hy {
  fill: #5be5d3;
  font-weight: 600;
}
.cdk-clock-node.tone-menh .cdk-clock-star-name {
  fill: #fcd34d;
  font-weight: 600;
}

/* Center: Mệnh info */
.cdk-clock-center { pointer-events: none; }
.cdk-clock-core-label {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  fill: rgba(230, 238, 245, 0.58);
}
.cdk-clock-core-branch {
  font-size: 36px;
  font-weight: 700;
  fill: #fcd34d;
}
.cdk-clock-core-stars {
  font-size: 12px;
  font-weight: 600;
  fill: #5be5d3;
}
.cdk-clock-core-count {
  font-size: 10px;
  fill: rgba(230, 238, 245, 0.6);
}

/* Legend below clock */
.cdk-clock-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px 16px;
  margin-top: 6px;
  padding: 0 10px;
}
.cdk-clock-legend .leg-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: rgba(230, 238, 245, 0.74);
}
.cdk-clock-legend .dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  border: 1px solid rgba(230, 238, 245, 0.18);
  background: rgba(2, 6, 23, 0.5);
}
.cdk-clock-legend .tone-menh .dot { background: #fcd34d; border-color: #fcd34d; }
.cdk-clock-legend .tone-tam-hop .dot { background: rgba(252, 211, 77, 0.4); border-color: rgba(252, 211, 77, 0.7); border-style: dashed; }
.cdk-clock-legend .tone-xung-chieu .dot { background: transparent; border-color: rgba(248, 113, 113, 0.7); border-style: dashed; }
.cdk-clock-legend .tone-cat .dot { background: rgba(91, 229, 211, 0.7); }
.cdk-clock-legend .tone-hung .dot { background: rgba(248, 113, 113, 0.7); }
.cdk-clock-legend .tone-am .dot { background: rgba(196, 181, 253, 0.7); }
.cdk-clock-legend .tone-duong .dot { background: rgba(252, 211, 77, 0.7); }

/* ─── Node hover + selected animation ────────────────────────────── */
.cdk-clock-node {
  transition: transform 220ms cubic-bezier(0.34, 1.56, 0.64, 1);
  transform-origin: center;
  transform-box: fill-box;
}
.cdk-clock-node:hover .cdk-clock-node-bg {
  stroke-width: 2.5;
  filter: drop-shadow(0 0 8px rgba(252, 211, 77, 0.4));
}
.cdk-clock-node:hover {
  transform: scale(1.08);
}
.cdk-clock-node.is-selected .cdk-clock-node-bg {
  stroke-width: 3.5;
  filter: drop-shadow(0 0 14px rgba(252, 211, 77, 0.85));
}
.cdk-clock-node.is-selected {
  transform: scale(1.12);
}
.cdk-clock-node.is-selected .cdk-clock-chi {
  fill: #fff;
}

/* Hint text */
.cdk-clock-hint {
  margin: 6px 0 0;
  text-align: center;
  font-size: 12px;
  color: rgba(252, 211, 77, 0.78);
  font-style: italic;
}

/* ─── Drawer info Việt thuần ────────────────────────────────── */
.cdk-branch-drawer {
  width: 100%;
  margin-top: 14px;
  padding: 16px 18px;
  border: 1px solid rgba(252, 211, 77, 0.32);
  border-radius: 12px;
  background:
    linear-gradient(135deg, rgba(252, 211, 77, 0.05) 0%, rgba(2, 6, 23, 0.4) 100%),
    rgba(2, 6, 23, 0.5);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
.cdk-branch-drawer.rel-menh {
  border-color: #fcd34d;
  box-shadow: 0 0 24px rgba(252, 211, 77, 0.35);
}
.cdk-branch-drawer.rel-tam-hop {
  border-color: rgba(252, 211, 77, 0.6);
  border-style: dashed;
}
.cdk-branch-drawer.rel-xung-chieu {
  border-color: rgba(248, 113, 113, 0.55);
  border-style: dashed;
  background:
    linear-gradient(135deg, rgba(248, 113, 113, 0.08) 0%, rgba(2, 6, 23, 0.4) 100%),
    rgba(2, 6, 23, 0.5);
}

.cdk-drawer-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(230, 238, 245, 0.1);
}
.cdk-drawer-title {
  display: flex;
  align-items: baseline;
  gap: 6px;
}
.cdk-drawer-chi {
  font-size: 28px;
  font-weight: 700;
  color: #fcd34d;
  line-height: 1;
}
.cdk-drawer-con-giap {
  font-size: 16px;
  color: #5be5d3;
  font-weight: 600;
}
.cdk-drawer-rel {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  background: rgba(167, 139, 250, 0.16);
  color: rgba(230, 238, 245, 0.86);
}
.cdk-branch-drawer.rel-menh .cdk-drawer-rel {
  background: rgba(252, 211, 77, 0.22);
  color: #fcd34d;
  font-weight: 600;
}
.cdk-branch-drawer.rel-tam-hop .cdk-drawer-rel {
  background: rgba(252, 211, 77, 0.14);
  color: #f5e6b1;
}
.cdk-branch-drawer.rel-xung-chieu .cdk-drawer-rel {
  background: rgba(248, 113, 113, 0.18);
  color: #fca5a5;
}

.cdk-drawer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}
.cdk-drawer-fact {
  padding: 10px 12px;
  background: rgba(2, 6, 23, 0.4);
  border: 1px solid rgba(230, 238, 245, 0.08);
  border-radius: 8px;
}
.cdk-drawer-fact small {
  display: block;
  color: rgba(230, 238, 245, 0.58);
  font-size: 11px;
  margin-bottom: 4px;
  letter-spacing: 0.3px;
}
.cdk-drawer-fact b {
  color: #f5e6b1;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.45;
}
.cdk-drawer-meaning {
  grid-column: 1 / -1;
}
.cdk-drawer-meaning b {
  color: rgba(230, 238, 245, 0.92);
  font-weight: 500;
  font-style: italic;
}

.cdk-drawer-stars h5 {
  margin: 0 0 10px;
  color: #fcd34d;
  font-size: 13px;
  font-weight: 700;
}
.cdk-drawer-star {
  padding: 10px 12px;
  margin-bottom: 8px;
  background: rgba(2, 6, 23, 0.4);
  border: 1px solid rgba(167, 139, 250, 0.18);
  border-radius: 8px;
}
.cdk-drawer-star header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.cdk-drawer-star strong {
  color: #fcd34d;
  font-size: 14px;
}
.cdk-drawer-star small {
  display: block;
  color: rgba(230, 238, 245, 0.78);
  font-size: 12px;
  line-height: 1.55;
}
.cdk-drawer-empty {
  margin: 0;
  padding: 10px;
  text-align: center;
  font-size: 12px;
  color: rgba(230, 238, 245, 0.6);
  font-style: italic;
}

/* ─── Quick interpretation (static) ──────────────────────────────── */
.cdk-drawer-interp {
  margin-top: 14px;
  padding: 14px 16px;
  background: rgba(91, 229, 211, 0.04);
  border-left: 3px solid rgba(91, 229, 211, 0.5);
  border-radius: 0 8px 8px 0;
}
.cdk-drawer-interp h5 {
  margin: 0 0 10px;
  color: #5be5d3;
  font-size: 13px;
  font-weight: 700;
}
.cdk-drawer-interp p {
  margin: 0 0 10px;
  color: rgba(230, 238, 245, 0.92);
  font-size: 13px;
  line-height: 1.65;
}
.cdk-drawer-interp p:last-child { margin-bottom: 0; }
.cdk-drawer-interp strong { color: #fcd34d; }
.cdk-drawer-interp em { color: #c4b5fd; font-style: italic; }

/* ─── Deep interpretation (VIP DeepSeek) ──────────────────────────── */
.cdk-drawer-deep {
  margin-top: 14px;
  padding: 14px 16px;
  background:
    linear-gradient(135deg, rgba(252, 211, 77, 0.05) 0%, rgba(167, 139, 250, 0.05) 100%),
    rgba(2, 6, 23, 0.4);
  border: 1px solid rgba(252, 211, 77, 0.22);
  border-radius: 10px;
}
.cdk-deep-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.cdk-deep-head h5 {
  margin: 0;
  color: #fcd34d;
  font-size: 13px;
  font-weight: 700;
}
.cdk-vip-badge {
  padding: 3px 9px;
  border-radius: 11px;
  font-size: 11px;
  font-weight: 600;
}
.cdk-vip-badge.is-ok {
  background: rgba(91, 229, 211, 0.18);
  color: #5be5d3;
}
.cdk-vip-badge.is-locked {
  background: rgba(167, 139, 250, 0.18);
  color: #c4b5fd;
}
.cdk-deep-btn {
  width: 100%;
  padding: 12px 14px;
  background: linear-gradient(135deg, #fcd34d 0%, #f59e0b 100%);
  color: #1f1306;
  font-weight: 700;
  font-size: 13px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 160ms, box-shadow 160ms;
}
.cdk-deep-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(252, 211, 77, 0.45);
}
.cdk-deep-btn:disabled {
  background: rgba(167, 139, 250, 0.18);
  color: rgba(230, 238, 245, 0.6);
  cursor: not-allowed;
}
.cdk-deep-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  color: #fcd34d;
  font-size: 13px;
}
.cdk-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(252, 211, 77, 0.3);
  border-top-color: #fcd34d;
  border-radius: 50%;
  animation: cdk-spin 0.8s linear infinite;
}
@keyframes cdk-spin {
  to { transform: rotate(360deg); }
}
.cdk-deep-error {
  margin: 0;
  padding: 10px;
  color: #fca5a5;
  background: rgba(248, 113, 113, 0.1);
  border-radius: 6px;
  font-size: 12px;
}
.cdk-deep-content { font-size: 13px; }
.cdk-deep-section {
  margin-bottom: 14px;
  padding: 10px 12px;
  background: rgba(2, 6, 23, 0.3);
  border-radius: 7px;
}
.cdk-deep-section h6 {
  margin: 0 0 6px;
  color: #fcd34d;
  font-size: 12px;
  font-weight: 700;
}
.cdk-deep-section p {
  margin: 0;
  color: rgba(230, 238, 245, 0.9);
  font-size: 13px;
  line-height: 1.65;
}
.cdk-deep-section strong { color: #fcd34d; }
.cdk-deep-section em { color: #c4b5fd; }
.cdk-deep-meta {
  display: block;
  margin-top: 8px;
  text-align: right;
  color: rgba(91, 229, 211, 0.75);
  font-size: 11px;
}
.cdk-deep-regen {
  display: block;
  margin: 10px 0 0;
  padding: 6px 14px;
  background: rgba(167, 139, 250, 0.15);
  color: #c4b5fd;
  border: 1px solid rgba(167, 139, 250, 0.32);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}
.cdk-deep-regen:hover {
  background: rgba(167, 139, 250, 0.28);
}

/* Animation drawer slide-in */
.cdk-drawer-enter-active,
.cdk-drawer-leave-active {
  transition: opacity 280ms ease, transform 280ms cubic-bezier(0.34, 1.4, 0.64, 1);
}
.cdk-drawer-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}
.cdk-drawer-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}

.cdk-branch-detail {
  margin-top: 6px;
}
.cdk-branch-detail > summary {
  color: rgba(167, 139, 250, 0.85);
  font-size: 12px;
  cursor: pointer;
  padding: 6px 0;
}

.cdk-branch-map {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}
.cdk-branch-cell {
  min-height: 104px;
  padding: 9px;
  border: 1px solid rgba(230, 238, 245, 0.08);
  border-radius: 7px;
  background: rgba(2, 6, 23, 0.22);
}
.cdk-branch-cell.is-menh {
  border-color: rgba(252, 211, 77, 0.54);
  background: rgba(252, 211, 77, 0.07);
}
.cdk-branch-cell header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 7px;
}
.cdk-branch-cell header strong {
  color: #f5e6b1;
  font-size: 14px;
}
.cdk-branch-cell header span {
  padding: 1px 6px;
  border-radius: 3px;
  background: rgba(252, 211, 77, 0.16);
  color: #fcd34d;
  font-size: 10.5px;
  font-weight: 700;
}
.cdk-branch-cell p {
  margin: 0;
  color: rgba(230, 238, 245, 0.42);
  font-size: 11.5px;
}
.cdk-branch-stars {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.cdk-branch-star {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 6px;
  min-height: 28px;
  width: 100%;
  padding: 4px 6px;
  border: 1px solid rgba(230, 238, 245, 0.08);
  border-radius: 4px;
  background: rgba(15, 23, 42, 0.74);
  color: rgba(230, 238, 245, 0.82);
  text-align: left;
}
.cdk-branch-star.has-art { cursor: zoom-in; }
.cdk-branch-star.is-hy { border-color: rgba(91, 229, 211, 0.3); }
.cdk-branch-star img {
  width: 22px;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  border-radius: 2px;
}
.cdk-branch-star span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #f5e6b1;
  font-size: 12px;
  font-weight: 700;
}
.cdk-branch-star small {
  color: #5be5d3;
  font-size: 10.5px;
}
.cdk-raw-stars {
  margin-top: 12px;
}
.cdk-raw-stars summary {
  cursor: pointer;
  color: rgba(230, 238, 245, 0.58);
  font-size: 12px;
}
.cdk-stars-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 6px; margin: 10px 0;
}
.cdk-star-pos {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.25);
  border-left: 2px solid #a78bfa;
  border-radius: 0 4px 4px 0;
  font-size: 12.5px;
}
.cdk-chart-art {
  width: 32px;
  aspect-ratio: 2 / 3;
  padding: 0;
  border: 1px solid rgba(245, 230, 177, 0.28);
  border-radius: 3px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.28);
  cursor: zoom-in;
}
.cdk-chart-art img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cdk-star-name { color: #f5e6b1; }
.cdk-star-branch { color: #5be5d3; font-weight: 600; }
.cdk-chart-art-note {
  margin: 8px 0 10px;
  color: rgba(230, 238, 245, 0.64);
  font-size: 12px;
}
.cdk-chart-art-note b { color: #fcd34d; }
.cdk-dai-han { margin: 10px 0; font-size: 12px; }
.cdk-dai-han summary { cursor: pointer; color: #fcd34d; }
.cdk-dai-han ul { margin: 6px 0 0 16px; padding: 0; }
.cdk-paradigm-note {
  font-size: 11.5px; color: rgba(230, 238, 245, 0.6);
  font-style: italic; margin: 10px 0 0;
  padding: 8px; background: rgba(167, 139, 250, 0.05);
  border-left: 2px solid #a78bfa;
}

.cdk-section { margin: 24px 0; }
.cdk-section h3 { color: #f5e6b1; font-size: 17px; margin: 0 0 10px; }

.cdk-warning {
  background: rgba(214, 90, 74, 0.1);
  border-left: 3px solid #d65a4a;
  padding: 8px 12px;
  font-size: 12px;
  color: #f5b08c;
  margin: 8px 0;
  border-radius: 0 4px 4px 0;
}
.cdk-art-status {
  margin: 10px 0 12px;
  padding: 9px 12px;
  background: rgba(91, 229, 211, 0.08);
  border-left: 3px solid #5be5d3;
  border-radius: 0 4px 4px 0;
  color: rgba(230, 238, 245, 0.76);
  font-size: 12px;
}
.cdk-art-status b { color: #fcd34d; }

.cdk-tier-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
@media (max-width: 768px) {
  .cdk-chart-guide,
  .cdk-chart-core,
  .cdk-tier-grid {
    grid-template-columns: 1fr;
  }
  .cdk-branch-map {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
.cdk-tier h4 { color: #fcd34d; font-size: 14px; margin: 0 0 10px; }
.cdk-phi-card {
  display: grid;
  grid-template-columns: minmax(112px, 0.36fr) minmax(0, 1fr);
  align-items: stretch;
  gap: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-left: 3px solid #c4b5fd;
  border-radius: 0 7px 7px 0;
  padding: 10px;
  margin: 8px 0;
  cursor: pointer;
  transition: background 0.15s;
}
.cdk-phi-card:hover { background: rgba(255, 255, 255, 0.06); }
.cdk-phi-card.active { background: rgba(232, 201, 90, 0.1); }
.cdk-phi-am { border-left-color: #f9a8d4; }
.cdk-phi-art {
  width: 100%;
  aspect-ratio: 2 / 3;
  padding: 0;
  overflow: hidden;
  border: 1px solid rgba(245, 230, 177, 0.32);
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.32);
  cursor: zoom-in;
}
.cdk-phi-art img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cdk-phi-copy {
  position: relative;
  min-width: 0;
  padding-right: 34px;
}
.cdk-phi-card header { display: flex; align-items: baseline; gap: 6px; margin-bottom: 2px; }
.cdk-phi-card strong { color: #f5e6b1; font-size: 16px; }
.cdk-phi-card header small { color: rgba(230, 238, 245, 0.55); font-size: 11px; }
.cdk-phi-copy > small { display: block; font-size: 11px; color: rgba(230, 238, 245, 0.6); margin-top: 2px; }
.cdk-phi-summary {
  margin: 8px 0 0;
  color: rgba(230, 238, 245, 0.8);
  font-size: 12.5px;
  line-height: 1.48;
}
.cdk-phi-hy {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 8px 0 0;
  color: rgba(230, 238, 245, 0.6);
  font-size: 11px;
}
.cdk-phi-hy b {
  color: rgba(230, 238, 245, 0.55);
  margin-right: 2px;
}
.cdk-phi-hy span {
  padding: 1px 6px;
  border-radius: 3px;
  background: rgba(91, 229, 211, 0.12);
  color: #5be5d3;
}
.cdk-phi-category {
  position: absolute;
  top: 0;
  right: 0;
  padding: 2px 7px;
  border-radius: 4px;
  background: rgba(252, 211, 77, 0.12);
  color: #f5e6b1;
  font-size: 10.5px;
  font-weight: 700;
}
.cdk-phi-detail {
  grid-column: 1 / -1;
  margin-top: 8px; padding: 8px;
  background: rgba(0, 0, 0, 0.2); border-radius: 4px;
  font-size: 12px; color: rgba(230, 238, 245, 0.82);
}
.cdk-phi-detail p { margin: 3px 0; }
.cdk-phi-detail b { color: #fcd34d; font-weight: 500; }

.cdk-cach-card {
  background: rgba(255, 255, 255, 0.03);
  border-left: 4px solid #94a3b8;
  border-radius: 0 6px 6px 0;
  padding: 12px 14px; margin: 8px 0;
}
.cdk-cach-cát { border-left-color: #5ab07a; }
.cdk-cach-hung { border-left-color: #d65a4a; }
.cdk-cach-kỳ-cách { border-left-color: #fbbf24; }
.cdk-cach-trung-tính { border-left-color: #94a3b8; }
.cdk-cach-card header { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
.cdk-cach-card strong { color: #f5e6b1; font-size: 14px; }
.cdk-zh { color: rgba(230, 238, 245, 0.5); font-size: 12px; }
.cdk-polarity-badge {
  font-size: 10.5px; padding: 2px 8px; border-radius: 3px;
  background: rgba(255, 255, 255, 0.08); color: #cbd5e1;
}
.cdk-lesson { margin: 6px 0; font-size: 13px; line-height: 1.55; color: rgba(230, 238, 245, 0.88); }
.cdk-cach-card details { margin-top: 8px; font-size: 12px; }
.cdk-cach-card summary { cursor: pointer; color: rgba(230, 238, 245, 0.55); }
.cdk-cach-card em { color: #f5e6b1; display: block; margin: 6px 0; font-style: italic; }
.cdk-paradigm { color: #c4b5fd; font-size: 11.5px; margin: 6px 0; font-style: italic; }

.cdk-intro { font-size: 13px; color: rgba(230, 238, 245, 0.78); margin: 0 0 12px; line-height: 1.55; }
.cdk-tong-doan-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 10px;
}
.cdk-tong-doan-card {
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-left: 3px solid #5be5d3;
  border-radius: 0 4px 4px 0;
  font-size: 12.5px;
}
.cdk-tong-cát { border-left-color: #5ab07a; }
.cdk-tong-hung { border-left-color: #d65a4a; }
.cdk-tong-âm { border-left-color: #f9a8d4; }
.cdk-tong-dương { border-left-color: #fcd34d; }
.cdk-tong-doan-card header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.cdk-tong-doan-card strong { color: #f5e6b1; font-size: 13px; }
.cdk-cat-badge {
  font-size: 10px; padding: 1px 6px; border-radius: 3px;
  background: rgba(255, 255, 255, 0.08); color: #cbd5e1;
}
.cdk-tong-verdict { margin: 6px 0; line-height: 1.5; color: rgba(230, 238, 245, 0.85); }
.cdk-hy-cung { font-size: 11px; margin: 6px 0; }
.cdk-hy-cung b { color: rgba(230, 238, 245, 0.55); margin-right: 4px; }
.cdk-hy-chip {
  display: inline-block;
  margin-right: 4px;
  padding: 1px 6px;
  background: rgba(91, 229, 211, 0.12);
  border-radius: 3px;
  color: #5be5d3;
}
.cdk-tong-doan-card details summary { font-size: 11px; color: rgba(230, 238, 245, 0.5); cursor: pointer; }
.cdk-tong-doan-card em { color: #f5e6b1; display: block; margin: 6px 0; font-style: italic; font-size: 12px; }
.cdk-warning-inline { color: #f5b08c; margin: 4px 0; font-size: 11px; }

.cdk-ending {
  margin: 16px 0;
  padding: 16px;
  background: rgba(167, 139, 250, 0.06);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 6px;
}
.cdk-ending h4 { color: #c4b5fd; margin: 0 0 8px; font-size: 14px; }
.cdk-ending blockquote {
  font-style: italic; color: #f5e6b1;
  border-left: 3px solid #fcd34d;
  padding: 6px 12px; margin: 8px 0;
}
.cdk-iron-rule {
  margin: 10px 0 0; padding: 8px 12px;
  background: rgba(232, 201, 90, 0.06);
  border-left: 2px solid #fcd34d;
  font-size: 12px; color: rgba(230, 238, 245, 0.85);
}
.cdk-art-lightbox {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(2, 6, 23, 0.86);
}
.cdk-art-lightbox figure {
  position: relative;
  width: min(92vw, 620px);
  max-height: 92vh;
  margin: 0;
  padding: 12px;
  background: #0f172a;
  border: 1px solid rgba(245, 230, 177, 0.34);
  border-radius: 8px;
  box-shadow: 0 22px 70px rgba(0, 0, 0, 0.5);
}
.cdk-art-lightbox img {
  display: block;
  width: 100%;
  max-height: 78vh;
  object-fit: contain;
  border-radius: 5px;
  background: #020617;
}
.cdk-art-lightbox figcaption {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-top: 10px;
  color: rgba(230, 238, 245, 0.72);
  font-size: 12px;
}
.cdk-art-lightbox figcaption b { color: #f5e6b1; }
.cdk-lightbox-close {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border: 1px solid rgba(230, 238, 245, 0.3);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.9);
  color: #e6eef5;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}
@media (max-width: 520px) {
  .cdk-art-lightbox { padding: 10px; }
  .cdk-art-lightbox figcaption { display: block; }
  .cdk-art-lightbox figcaption span { display: block; margin-top: 4px; }
  .cdk-phi-card {
    grid-template-columns: minmax(92px, 0.42fr) minmax(0, 1fr);
    gap: 10px;
    padding: 8px;
  }
  .cdk-phi-card strong {
    font-size: 14px;
  }
  .cdk-phi-summary {
    font-size: 11.5px;
    line-height: 1.42;
  }
}
</style>
