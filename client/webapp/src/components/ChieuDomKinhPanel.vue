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
const cachCucEval = ref(null);  // personalized eval result for current lá số
const nhapCot = ref(null);
const loading = ref(false);
const error = ref("");
const activeStarId = ref(null);
const selectedArtCard = ref(null);
const selectedBranch = ref(null);

// ─── Tooltip glossary (mini, inline) ───────────────────────────────────────
const HV_GLOSSARY = {
  "Thiên La": "Lưới trời — 2 cung Thìn-Tỵ, đại diện cho ràng buộc từ trên xuống (sếp, luật pháp, định mệnh).",
  "Địa Võng": "Lưới đất — 2 cung Tuất-Hợi, đại diện cho ràng buộc từ dưới lên (gia đình, vật chất, sức khoẻ).",
  "Phú môn": "Cửa nhà giàu — vị trí phát đạt, nhưng trong Chiếu Đởm Kinh nghĩa là KỲ CÁCH: chính cái hung biến thành cát.",
  "Kình Dương": "Sao 'lưỡi dao mạnh' — chủ tính quyết liệt, cương cường, dễ va chạm. Còn gọi là Thiên Nhận.",
  "Thiên Nhận": "Sao Kình Dương — chủ tính sắc bén, dao găm, kỷ luật cứng.",
  "Thiên Hư": "Sao 'trống rỗng' — chủ sự hư huyễn, lo âu vô cớ. Còn gọi là Địa Không trong vài lưu phái.",
  "Địa Không": "Sao 'không vong' — chủ sự mất mát, đứt đoạn, ảo tưởng.",
  "Thân nịch giang hồ": "Thân chìm trong giang hồ — phiêu bạt không định cư.",
  "Tử đầu la võng": "Đầu con cạm lưới — Mệnh ở vùng Thiên La hoặc Địa Võng, hay bị bó buộc.",
  "Thân nhập bần dân": "Thân vào nhà bần hàn — Thân tọa Tỵ, lo lắng vợ con.",
  "Ma chúc vi mệnh": "Nến mài làm mệnh — Mệnh có Kình Dương, đời đa thành đa bại.",
  "Mệnh tọa phú môn": "Mệnh ngồi cửa nhà giàu — kỳ cách, hung-mà-không-hung, hết khổ tới sướng.",
  "Xà nhập long cung": "Rắn vào long cung — Mệnh Mão + giờ Mão, rule mạnh, tốt mọi mặt.",
  "Tam hợp": "3 cung cách nhau 120° cùng đồng nhịp với Mệnh.",
  "Xung chiếu": "Cung đối diện 180° với Mệnh — tạo áp lực ngược.",
  "Tứ Hóa": "4 dạng biến hóa của sao: Lộc (tài lộc), Quyền (quyền lực), Khoa (danh tiếng), Kỵ (cản trở).",
  "Đại Hạn": "Vận 10 năm — cung Mệnh xoay theo tuổi, vận khí mỗi giai đoạn khác.",
  "Lưu Niên": "Vận 1 năm — sao chạy qua cung mỗi năm cụ thể.",
  "Mệnh chủ": "Sao chủ của cung Mệnh theo bảng Phú Thái Vi Q2 — đại diện linh hồn cốt lõi.",
  "Thân chủ": "Sao chủ của cung Thân — đại diện hành động, biểu hiện ra đời.",
  "Hỷ cung": "Cung mà sao đặc biệt tốt, đắc địa.",
  "Thất vị": "Vị trí sao bị lạc nhà, không phát huy được sức.",
  "Cách cục": "Tổ hợp sao + cung tạo thành mẫu lá số có ý nghĩa đặc biệt.",
  "Kỳ cách": "Cách lạ — hung-mà-không-hung, ngoài quy luật bình thường.",
};

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

// 18 sao của lá số user — sắp xếp đắc địa → thất vị, kèm verdict Nhập Cốt
const cdkNhapCotPersonalized = computed(() => {
  if (!cdkChart.value?.stars || !nhapCot.value?.per_star_tong_doan) return null;
  const ncByStar = new Map(
    (nhapCot.value.per_star_tong_doan || []).map((item) => [item.star, item])
  );
  const menh = cdkChart.value.menh_branch;
  const list = [];
  for (const [star, branch] of Object.entries(cdkChart.value.stars)) {
    const fullName = NHAP_COT_STAR_NAME[star] || star;
    const nc = ncByStar.get(fullName);
    const isHy = nc?.hy_cung?.includes(branch) || false;
    const isMenh = branch === menh;
    list.push({
      star_short: star,
      star_full: fullName,
      branch,
      isHy,
      isMenh,
      category: nc?.category || "?",
      hyCung: nc?.hy_cung || [],
      verdictSummary: nc?.verdict_summary || "Chưa có verdict trong Nhập Cốt.",
      verdictQuote: nc?.verdict_quote_hv || "",
      warning: nc?.warning || "",
      sourceRef: nc?.source_ref || "",
      art: chartArtFor(star),
    });
  }
  // Sort: Mệnh trước, rồi đắc-địa (hỷ), rồi thất-vị
  list.sort((a, b) => {
    if (a.isMenh !== b.isMenh) return a.isMenh ? -1 : 1;
    if (a.isHy !== b.isHy) return a.isHy ? -1 : 1;
    return a.star_full.localeCompare(b.star_full);
  });
  const hyCount = list.filter((s) => s.isHy).length;
  const menhStars = list.filter((s) => s.isMenh);
  return {
    list,
    total: list.length,
    hyCount,
    thatViCount: list.length - hyCount,
    menhStars,
    menhBranch: menh,
  };
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

const cdkClockCardGroups = computed(() => {
  return cdkClockMap.value.nodes
    .map((node) => {
      const artStars = node.stars.filter((star) => star.art);
      if (!artStars.length) return null;
      const rad = (node.angle - 90) * Math.PI / 180;
      const radiusPct = 45;
      const xPct = 50 + radiusPct * Math.cos(rad);
      const yPct = 50 + radiusPct * Math.sin(rad);
      const selected = (selectedBranch.value || cdkChart.value?.menh_branch) === node.branch;
      const horizontalAnchor = xPct < 24 ? "left" : xPct > 76 ? "right" : "center";
      const verticalAnchor = yPct < 18 ? "top" : yPct > 82 ? "bottom" : "middle";
      return {
        branch: node.branch,
        stars: artStars.slice(0, 3),
        extraCount: Math.max(0, artStars.length - 3),
        isSelected: selected,
        isMenh: node.isMenh,
        tone: node.tone,
        anchorClass: `anchor-${horizontalAnchor} anchor-${verticalAnchor}`,
        style: {
          left: `${xPct.toFixed(2)}%`,
          top: `${yPct.toFixed(2)}%`,
        },
      };
    })
    .filter(Boolean);
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
    const [chart, phi, cards, cach, ncot, cachEval] = await Promise.all([
      chartPayload ? fetchJsonOrNull("/api/tu-vi/q4/chieu-dom-kinh/cast", {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify(chartPayload)
      }) : Promise.resolve(null),
      fetchJsonOrNull("/api/tu-vi/q4/chieu-dom-kinh-phi-tinh"),
      fetchJsonOrNull("/oracle-cards/chieu-dom-kinh/18-phi-tinh/cards.json"),
      fetchJsonOrNull("/api/tu-vi/q4/chieu-dom-kinh-cach-cuc"),
      fetchJsonOrNull("/api/tu-vi/q4/nhap-cot-tien-kinh"),
      chartPayload ? fetchJsonOrNull("/api/tu-vi/q4/cdk/eval-cach-cuc", {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify(chartPayload)
      }) : Promise.resolve(null),
    ]);
    if (chart && chart.status === "ok") cdkChart.value = chart;
    if (phi?.status === "ok") phiTinh18.value = phi;
    if (cards?.cards) phiTinhCards.value = cards.cards;
    if (cach?.status === "ok") cachCuc.value = cach;
    if (ncot?.status === "ok") nhapCot.value = ncot;
    if (cachEval?.status === "ok") cachCucEval.value = cachEval;
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

// Wrap matching glossary terms with <abbr title="...">term</abbr> for hover tooltip
function renderWithTooltips(text) {
  if (!text) return '';
  let escaped = String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/_([^_]+)_/g, '<em>$1</em>');
  // Sort by length descending để match longer terms trước
  const terms = Object.keys(HV_GLOSSARY).sort((a, b) => b.length - a.length);
  for (const term of terms) {
    const note = HV_GLOSSARY[term].replace(/"/g, '&quot;');
    // Replace only first occurrence (case-sensitive) per term to avoid noise
    const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`(${escapedTerm})(?![^<]*>)`, '');  // not inside existing tag
    escaped = escaped.replace(re, `<abbr class="hv-tooltip" title="${note}">$1</abbr>`);
  }
  return escaped;
}

// Auto-load bulk cache 12 cung khi mount (populate cdkDeepInterp instant cho drawer)
async function tryLoadCachedBulk12Cung() {
  const person = activePerson.value;
  if (!person?.birth_datetime_local && !person?.person_key) return;
  try {
    const genderText = String(person?.gender || 'nam').toLowerCase();
    const payload = {
      force: false,
      ...(person.person_key
        ? { person_key: person.person_key }
        : {
            birth_datetime_local: person.birth_datetime_local,
            gender: genderText.includes('nữ') || genderText.includes('nu') ? 'nữ' : 'nam',
            timezone: person.timezone || 'Asia/Ho_Chi_Minh',
            name: person.name || 'Người',
          }),
    };
    const resp = await fetch('/api/tu-vi/q4/cdk/luan-toan-bo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    });
    if (!resp.ok) return;
    const data = await resp.json();
    if (data.status !== 'ok') return;
    // Only populate if all results from cache (don't trigger unintended gen)
    const allFromCache = (data.cached_count || 0) === 12 || (data.fresh_calls || 0) === 0;
    if (!allFromCache) return;
    const results = data.results || {};
    for (const [branch, sections] of Object.entries(results)) {
      const key = `${person.person_key || person.birth_datetime_local}_${branch}`;
      cdkDeepInterp.value[key] = {
        loading: false,
        error: null,
        data: {
          status: 'ok',
          branch,
          provider: data.provider,
          luan_cung_compact: sections,
          from_bulk: true,
        },
      };
    }
  } catch (e) { /* silent */ }
}

onMounted(async () => {
  await loadAll();
  await loadCdkDeepFeature();
  // Auto-load cached Đại Hạn + Lưu Niên + 12 cung bulk nếu đã có (instant render)
  tryLoadCachedDaiHan();
  tryLoadCachedLuuNien();
  tryLoadCachedBulk12Cung();
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
  // Lớp 3: ý nghĩa thực tế — PARADIGM ĐÚNG (giờ sinh = khoảnh khắc ĐỒNG DẠNG với bản chất, không phải giờ đỉnh năng lượng)
  if (relKey === "menh") {
    const HOUR_FEEL = {
      "Tý":   "Vào giờ này (nửa đêm), Anh thường tĩnh lặng, suy nghĩ sâu, có ý tưởng đột phá. Đây là lúc lý tưởng để Anh đọc, viết, hoặc thiền — KHÔNG phải lúc ép mình tỉnh táo làm việc nặng.",
      "Sửu":  "Vào giờ này (gần sáng), Anh có thể vẫn tỉnh táo trong khi người khác đã ngủ. Khoảnh khắc nuôi dưỡng nội tâm, không vội vàng.",
      "Dần":  "Vào giờ này (rạng đông), Anh thức dậy sớm với năng lượng mạnh, sẵn sàng bứt phá. Lúc tốt nhất để khởi động ngày, tập thể dục.",
      "Mão":  "Vào giờ này (sáng sớm), Anh tỉnh táo, sáng tạo, thích hợp cho công việc đòi hỏi suy luận tinh tế.",
      "Thìn": "Vào giờ này (đầu ngày), Anh tích tụ năng lượng để bùng nổ. Lúc lý tưởng cho họp hành, ra quyết định lớn.",
      "Tỵ":   "Vào giờ này (giữa sáng), Anh sắc bén, thông minh, biến hóa. Tốt cho thương lượng, đàm phán.",
      "Ngọ":  "Vào giờ này (chính ngọ), Anh ở đỉnh dương khí. Mạnh mẽ, quyết đoán nhưng cũng có thể nóng nảy nếu không kiềm chế.",
      "Mùi":  "Vào giờ này (xế trưa), Anh thư thái, hài lòng. Lúc lý tưởng để nghỉ ngơi ngắn, nạp lại năng lượng.",
      "Thân": "Vào giờ này (xế chiều), Anh linh hoạt, tinh ranh, biết tận dụng cơ hội. Tốt cho networking, kinh doanh.",
      "Dậu":  "Vào giờ này (chiều tà), Anh thường **mệt mỏi, muốn thu mình** — đúng với bản chất gà về chuồng. Sau bữa tối Anh dễ buồn ngủ luôn, không nên ép mình làm việc nặng. Là lúc tốt để kết thúc công việc, dọn dẹp, chuẩn bị nghỉ ngơi.",
      "Tuất": "Vào giờ này (chập tối), Anh cảnh giác, trung thành, muốn ở gần người thân. Lúc tốt cho gia đình.",
      "Hợi":  "Vào giờ này (đêm khuya), Anh muốn nghỉ ngơi sâu, tích lũy. Tránh các quyết định lớn vào giờ này — hãy ngủ ngon.",
    };
    const feel = HOUR_FEEL[branch] || `Vào giờ ${info.gio}, Anh sẽ cảm nhận năng lượng đặc trưng của ${info.conGiap}.`;
    out.push(
      `**Trong đời sống**: ${feel} ` +
      `Phương **${info.phuongVi}** là hướng hợp với bản mệnh — ưu tiên ngồi quay mặt về hướng này khi làm việc, ` +
      `hoặc đặt giường ngủ theo hướng đối lập để nghỉ ngơi tốt.`
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
const cdkUserRole = ref(null);  // 'owner' | 'user' | null

async function loadCdkDeepFeature() {
  try {
    const r = await fetch('/api/user/my-vip-features', { credentials: 'include' });
    if (!r.ok) return;
    const d = await r.json();
    // API returns { subscriptions: [...], catalog: [...] }
    const sub = (d.subscriptions || []).find((s) => s.feature_id === 'tu_vi_cdk_luan_cung');
    cdkDeepFeature.value = sub || null;
    // Also check if user is owner (always allowed) via separate field if present
    cdkUserRole.value = d.user_role || (d.role) || null;
  } catch (e) {
    console.warn('Cannot load VIP features:', e);
  }
}

// ───── BULK luận toàn bộ 12 cung (1 lần ~3-5 phút) ─────
const cdkBulkLoading = ref(false);
const cdkBulkError = ref(null);
const cdkBulkSummary = ref(null);

// ───── Đại Hạn 8 vòng — luận chi tiết 80 năm ─────
const cdkDaiHan = ref(null);       // {dai_han: {vong_1..8}, dai_han_cycles, ...}
const cdkDaiHanLoading = ref(false);
const cdkDaiHanError = ref(null);

// ───── Lưu Niên 10 năm ─────
const cdkLuuNien = ref(null);       // {luu_nien: {nam_2026..2035}, years, ...}
const cdkLuuNienLoading = ref(false);
const cdkLuuNienError = ref(null);

async function tryLoadCachedLuuNien() {
  const person = activePerson.value;
  if (!person?.birth_datetime_local && !person?.person_key) return;
  try {
    const genderText = String(person?.gender || 'nam').toLowerCase();
    const payload = {
      force: false,
      ...(person.person_key
        ? { person_key: person.person_key }
        : {
            birth_datetime_local: person.birth_datetime_local,
            gender: genderText.includes('nữ') || genderText.includes('nu') ? 'nữ' : 'nam',
            timezone: person.timezone || 'Asia/Ho_Chi_Minh',
            name: person.name || 'Người',
          }),
    };
    const resp = await fetch('/api/tu-vi/q4/cdk/luan-luu-nien', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    });
    if (!resp.ok) return;
    const data = await resp.json();
    if (data.status === 'ok' && data.from_cache) {
      cdkLuuNien.value = data;
    }
  } catch (e) { /* silent */ }
}

async function loadLuuNien(force = false) {
  const person = activePerson.value;
  if (!person?.birth_datetime_local && !person?.person_key) return;
  cdkLuuNienLoading.value = true;
  cdkLuuNienError.value = null;
  try {
    const genderText = String(person?.gender || 'nam').toLowerCase();
    const payload = {
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
    const resp = await fetch('/api/tu-vi/q4/cdk/luan-luu-nien', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    });
    let data;
    try { data = await resp.json(); }
    catch { cdkLuuNienError.value = `HTTP ${resp.status} ${resp.statusText}`; return; }
    if (!resp.ok) {
      cdkLuuNienError.value = `HTTP ${resp.status} — ${data?.detail || data?.message || '?'}`;
      return;
    }
    if (data.status === 'ok') {
      cdkLuuNien.value = data;
    } else {
      cdkLuuNienError.value = data.message || 'Lỗi không xác định';
    }
  } catch (e) {
    cdkLuuNienError.value = String(e.message || e);
  } finally {
    cdkLuuNienLoading.value = false;
    loadCdkDeepFeature();
  }
}

// Computed: 10 năm với content + is_current
const cdkLuuNienList = computed(() => {
  if (!cdkLuuNien.value) return null;
  const years = cdkLuuNien.value.years || [];
  const ln = cdkLuuNien.value.luu_nien || {};
  const thisYear = new Date().getFullYear();
  return years.map((y) => {
    const content = ln[`nam_${y.year}`] || {};
    return {
      ...y,
      tong_quan: content.tong_quan || '',
      co_hoi_thach_thuc: content.co_hoi_thach_thuc || '',
      loi_khuyen: content.loi_khuyen || '',
      isCurrent: y.year === thisYear,
    };
  });
});

// Selected year for drawer (default: current year)
const selectedLuuNien = ref(null);
function selectLuuNien(yearMeta) {
  selectedLuuNien.value = selectedLuuNien.value?.year === yearMeta.year ? null : yearMeta;
}

// Auto-load cached Đại Hạn nếu có (chạy free, GET endpoint)
async function tryLoadCachedDaiHan() {
  const person = activePerson.value;
  if (!person?.birth_datetime_local && !person?.person_key) return;
  try {
    const genderText = String(person?.gender || 'nam').toLowerCase();
    const payload = {
      force: false,  // chỉ load cache, không gen mới
      ...(person.person_key
        ? { person_key: person.person_key }
        : {
            birth_datetime_local: person.birth_datetime_local,
            gender: genderText.includes('nữ') || genderText.includes('nu') ? 'nữ' : 'nam',
            timezone: person.timezone || 'Asia/Ho_Chi_Minh',
            name: person.name || 'Người',
          }),
    };
    // Check cache trước qua HEAD-like: gọi với force=false, nếu cache có thì instant
    const resp = await fetch('/api/tu-vi/q4/cdk/luan-dai-han', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    });
    if (!resp.ok) return;
    const data = await resp.json();
    if (data.status === 'ok' && data.from_cache) {
      cdkDaiHan.value = data;
    }
  } catch (e) { /* silent — user click button if not cached */ }
}

async function loadDaiHan(force = false) {
  const person = activePerson.value;
  if (!person?.birth_datetime_local && !person?.person_key) return;
  cdkDaiHanLoading.value = true;
  cdkDaiHanError.value = null;
  try {
    const genderText = String(person?.gender || 'nam').toLowerCase();
    const payload = {
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
    const resp = await fetch('/api/tu-vi/q4/cdk/luan-dai-han', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    });
    let data;
    try { data = await resp.json(); }
    catch { cdkDaiHanError.value = `HTTP ${resp.status} ${resp.statusText}`; return; }
    if (!resp.ok) {
      cdkDaiHanError.value = `HTTP ${resp.status} — ${data?.detail || data?.message || '?'}`;
      return;
    }
    if (data.status === 'ok') {
      cdkDaiHan.value = data;
    } else {
      cdkDaiHanError.value = data.message || 'Lỗi không xác định';
    }
  } catch (e) {
    cdkDaiHanError.value = String(e.message || e);
  } finally {
    cdkDaiHanLoading.value = false;
    loadCdkDeepFeature();
  }
}

// Computed: 8 vòng với content + which is current
const cdkDaiHanList = computed(() => {
  if (!cdkDaiHan.value) return null;
  const cycles = cdkDaiHan.value.dai_han_cycles || [];
  const dh = cdkDaiHan.value.dai_han || {};
  // Compute current age
  const person = activePerson.value;
  let currentAge = null;
  if (person?.birth_datetime_local) {
    try {
      const born = new Date(person.birth_datetime_local);
      currentAge = new Date().getFullYear() - born.getFullYear();
    } catch {}
  }
  const menh = cdkDaiHan.value.menh_branch;
  return cycles.map((c) => {
    const content = dh[`vong_${c.cycle_index}`] || {};
    const isCurrent = currentAge !== null && c.start_age <= currentAge && currentAge <= c.end_age;
    const isMenhCycle = c.branch === menh;
    return {
      ...c,
      tong_quan: content.tong_quan || '',
      co_hoi_thach_thuc: content.co_hoi_thach_thuc || '',
      loi_khuyen: content.loi_khuyen || '',
      isCurrent,
      isMenhCycle,
    };
  });
});

// Branch của vòng đại hạn hiện tại (để highlight clock)
const currentDaiHanBranch = computed(() => {
  const list = cdkDaiHanList.value;
  if (!list) return null;
  return list.find((v) => v.isCurrent)?.branch || null;
});

async function loadDeepInterpAll(force = false) {
  const person = activePerson.value;
  if (!person?.birth_datetime_local && !person?.person_key) return;
  cdkBulkLoading.value = true;
  cdkBulkError.value = null;
  try {
    const genderText = String(person?.gender || 'nam').toLowerCase();
    const payload = {
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
    const resp = await fetch('/api/tu-vi/q4/cdk/luan-toan-bo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload),
    });
    // Robust parse: nếu HTTP error / non-JSON, hiện status code
    let data;
    try {
      data = await resp.json();
    } catch (parseErr) {
      const txt = await resp.text().catch(() => '');
      cdkBulkError.value = `HTTP ${resp.status} ${resp.statusText} — ${txt.slice(0, 200) || 'không nhận được response JSON'}`;
      return;
    }
    if (!resp.ok) {
      cdkBulkError.value = `HTTP ${resp.status} — ${data?.detail || data?.message || JSON.stringify(data).slice(0, 200)}`;
      return;
    }
    if (data.status === 'ok') {
      // Populate cdkDeepInterp cho 12 cung
      const results = data.results || {};
      for (const [branch, sections] of Object.entries(results)) {
        const key = `${person.person_key || person.birth_datetime_local}_${branch}`;
        cdkDeepInterp.value[key] = {
          loading: false,
          error: null,
          data: {
            status: 'ok',
            branch,
            provider: data.provider,
            luan_cung_compact: sections,
            from_bulk: true,
          },
        };
      }
      cdkBulkSummary.value = {
        fresh_calls: data.fresh_calls,
        cached_count: data.cached_count,
        provider: data.provider,
        tokens: data.tokens,
      };
    } else {
      cdkBulkError.value = data.message || 'Lỗi không xác định';
    }
  } catch (e) {
    cdkBulkError.value = String(e.message || e);
  } finally {
    cdkBulkLoading.value = false;
    loadCdkDeepFeature();
  }
}

// Legacy per-cung loader (giữ cho force-regen 1 cung)
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
      branch, force,
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
      credentials: 'include',
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
    loadCdkDeepFeature();
  }
}

function getDeepInterpSlot(branch) {
  const person = activePerson.value;
  const key = `${person?.person_key || person?.birth_datetime_local}_${branch}`;
  return cdkDeepInterp.value[key] || { loading: false, data: null, error: null };
}

const cdkDeepFeatureStatus = computed(() => {
  // Owner always allowed regardless of subscription
  if (cdkUserRole.value === 'owner') {
    return { allowed: true, label: '👑 Owner — không giới hạn', reason: 'owner' };
  }
  const sub = cdkDeepFeature.value;
  if (!sub) return { allowed: false, label: '🔒 Chưa cấp VIP1', reason: 'no_subscription' };
  if (!sub.enabled) return { allowed: false, label: '🔒 Bị tắt', reason: 'disabled' };
  // Check expiry
  if (sub.expires_at) {
    const now = Math.floor(Date.now() / 1000);
    if (now > sub.expires_at) return { allowed: false, label: '🔒 Đã hết hạn', reason: 'expired' };
  }
  // Check remaining uses
  if (sub.remaining_uses !== null && sub.remaining_uses !== undefined && sub.remaining_uses <= 0) {
    return { allowed: false, label: '🔒 Hết lượt', reason: 'no_uses_left' };
  }
  const remainingLabel = sub.remaining_uses == null ? '∞' : sub.remaining_uses;
  return {
    allowed: true,
    label: `✓ VIP1 — Còn ${remainingLabel} lượt`,
    reason: 'ok',
    remaining: sub.remaining_uses,
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
        <div class="cdk-clock-stage">
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
                        currentDaiHanBranch === node.branch && 'is-current-dai-han',
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
                    text-anchor="middle">{{ st.star }}<title>{{ st.star }} ({{ st.meaning.lookupName }}) — {{ st.meaning.isHy ? '✓ HỶ CUNG (đắc địa)' : '✗ thất vị' }}
Nhóm: {{ st.meaning.category }}
Verdict: {{ st.meaning.summary }}</title></text>
              <title>{{ node.branch }} — {{ BRANCH_INFO[node.branch]?.conGiap }} · {{ BRANCH_INFO[node.branch]?.gio }}{{ node.isMenh ? ' · MỆNH CDK' : node.isTamHopWithMenh ? ' · tam hợp với Mệnh' : node.isXungChieu ? ' · xung chiếu Mệnh' : '' }}</title>
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

          <div class="cdk-clock-card-layer" aria-label="Vòng thẻ bài Phi Tinh theo 12 địa chi">
            <div
              v-for="group in cdkClockCardGroups"
              :key="group.branch"
              :class="['cdk-clock-card-group', group.anchorClass, `tone-${group.tone}`, group.isSelected && 'is-selected', group.isMenh && 'is-menh']"
              :style="group.style"
              @click.stop="selectBranch(group.branch)"
            >
              <span class="cdk-clock-card-branch">{{ group.branch }}</span>
              <button
                v-for="st in group.stars"
                :key="`${group.branch}-${st.star}`"
                type="button"
                class="cdk-clock-mini-card"
                :aria-label="`Mở ảnh ${st.star} tại ${group.branch}`"
                @click.stop="openArtCard(st.art)"
              >
                <img :src="st.art.image" :alt="`Ảnh ${st.star}`" loading="lazy" />
                <span>{{ st.star }}</span>
              </button>
              <span v-if="group.extraCount" class="cdk-clock-card-extra">+{{ group.extraCount }}</span>
            </div>
          </div>
        </div>

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
              <div class="cdk-drawer-star-row">
                <article v-for="st in selectedBranchInfo.stars" :key="st.star" class="cdk-drawer-star">
                  <button
                    v-if="st.art"
                    type="button"
                    class="cdk-drawer-star-art"
                    :aria-label="`Mở ảnh ${st.star}`"
                    @click.stop="openArtCard(st.art)"
                  >
                    <img :src="st.art.image" :alt="`Ảnh ${st.star}`" loading="lazy" />
                  </button>
                  <div class="cdk-drawer-star-body">
                    <header>
                      <strong>{{ st.star }}</strong>
                      <span :class="['cdk-status-chip', st.meaning.isHy ? 'is-hy' : '']">{{ st.meaning.status }}</span>
                      <span class="cdk-cat-chip">{{ st.meaning.category }}</span>
                    </header>
                    <small>{{ st.meaning.summary }}</small>
                  </div>
                </article>
              </div>
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

              <!-- Per-cung loading (legacy single cung force-regen) -->
              <div v-if="getDeepInterpSlot(selectedBranchInfo.branch).loading" class="cdk-deep-loading">
                <span class="cdk-spinner"></span>
                Đang nhờ DeepSeek phân tích cung {{ selectedBranchInfo.branch }}...
              </div>
              <p v-else-if="getDeepInterpSlot(selectedBranchInfo.branch).error" class="cdk-deep-error">
                ⚠ {{ getDeepInterpSlot(selectedBranchInfo.branch).error }}
              </p>
              <div v-else-if="getDeepInterpSlot(selectedBranchInfo.branch).data" class="cdk-deep-content">
                <!-- Compact 3-section format (from bulk or cache) -->
                <template v-if="getDeepInterpSlot(selectedBranchInfo.branch).data.luan_cung_compact">
                  <div class="cdk-deep-section">
                    <h6>1️⃣ Bản chất cung & Quan hệ với Mệnh</h6>
                    <p v-html="renderMarkdownInline(getDeepInterpSlot(selectedBranchInfo.branch).data.luan_cung_compact.ban_chat_va_quan_he || '')"></p>
                  </div>
                  <div class="cdk-deep-section">
                    <h6>2️⃣ Phi Tinh đóng & Ý nghĩa</h6>
                    <p v-html="renderMarkdownInline(getDeepInterpSlot(selectedBranchInfo.branch).data.luan_cung_compact.sao_dong_y_nghia || '')"></p>
                  </div>
                  <div class="cdk-deep-section">
                    <h6>3️⃣ Áp dụng & Lời khuyên</h6>
                    <p v-html="renderMarkdownInline(getDeepInterpSlot(selectedBranchInfo.branch).data.luan_cung_compact.ap_dung_loi_khuyen || '')"></p>
                  </div>
                </template>
                <!-- Legacy 5-section format -->
                <template v-else>
                  <div v-for="(section, key) in getDeepInterpSlot(selectedBranchInfo.branch).data.luan_cung || {}" :key="key" class="cdk-deep-section">
                    <h6>{{ DEEP_SECTION_LABELS[key] || key }}</h6>
                    <p v-html="renderMarkdownInline(String(section))"></p>
                  </div>
                </template>
                <small class="cdk-deep-meta">
                  Provider: {{ getDeepInterpSlot(selectedBranchInfo.branch).data.provider }} ·
                  {{ getDeepInterpSlot(selectedBranchInfo.branch).data.from_bulk ? 'Đã luận cùng 12 cung' : 'Đã lưu wiki ✓' }}
                </small>
              </div>

              <!-- No data: show big bulk button -->
              <div v-else class="cdk-bulk-cta">
                <p class="cdk-bulk-explain">
                  💡 Để tiết kiệm thời gian, anh nên <b>luận TOÀN BỘ 12 cung trong 1 lần</b> (~3-5 phút).
                  Sau đó click chi nào cũng có sẵn luôn (cache vĩnh viễn).
                </p>
                <button type="button"
                        class="cdk-deep-btn cdk-bulk-btn"
                        :disabled="!cdkDeepFeatureStatus.allowed || cdkBulkLoading"
                        @click="loadDeepInterpAll(false)">
                  <span v-if="cdkBulkLoading">
                    <span class="cdk-spinner"></span>
                    Đang luận 12 cung song song bằng DeepSeek V4 Pro... (~3-5 phút)
                  </span>
                  <span v-else-if="cdkDeepFeatureStatus.allowed">
                    🚀 Luận TOÀN BỘ 12 cung CDK (1 lần · ~3-5 phút · tự lưu wiki)
                  </span>
                  <span v-else>🔒 {{ cdkDeepFeatureStatus.label }} — không thể luận sâu</span>
                </button>
                <p v-if="cdkBulkError" class="cdk-deep-error" style="margin-top: 8px;">
                  ⚠ {{ cdkBulkError }}
                </p>
                <p v-if="cdkBulkSummary" class="cdk-bulk-summary">
                  ✅ Vừa luận {{ cdkBulkSummary.fresh_calls }} cung mới
                  + {{ cdkBulkSummary.cached_count }} từ cache.
                  Tokens: {{ cdkBulkSummary.tokens?.prompt }} prompt + {{ cdkBulkSummary.tokens?.completion }} completion.
                </p>
              </div>
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
      <!-- Đại Hạn 8 vòng: bảng raw + button luận chi tiết -->
      <section class="cdk-dai-han-section">
        <header class="cdk-dh-head">
          <h4>⏳ Đại Hạn 8 vòng — 80 năm cuộc đời</h4>
          <span v-if="cdkDaiHan" class="cdk-vip-badge is-ok">✓ Đã luận sâu</span>
        </header>
        <p class="cdk-intro">
          Mỗi <abbr class="hv-tooltip" title="Vận 10 năm — cung Mệnh CDK xoay theo tuổi, vận khí mỗi giai đoạn khác nhau">đại hạn</abbr>
          dài 10 năm, đi qua 1 cung địa chi. Cung nào kích hoạt = các sao tại đó tác động vào vận khí giai đoạn ấy.
        </p>

        <!-- Bảng raw 8 vòng -->
        <div class="cdk-dh-cycles">
          <article v-for="c in cdkChart.dai_han_cycles" :key="c.cycle_index"
                   :class="['cdk-dh-cycle',
                            currentDaiHanBranch === c.branch && 'is-current',
                            c.branch === cdkChart.menh_branch && 'is-menh-cycle']">
            <span class="cdk-dh-idx">V{{ c.cycle_index }}</span>
            <div class="cdk-dh-meta">
              <strong>{{ c.branch }}</strong>
              <small>{{ c.start_age }}-{{ c.end_age }} tuổi</small>
            </div>
            <span v-if="currentDaiHanBranch === c.branch" class="cdk-dh-tag">⭐ Hiện tại</span>
            <span v-else-if="c.branch === cdkChart.menh_branch" class="cdk-dh-tag is-menh">Mệnh gốc</span>
          </article>
        </div>

        <!-- Đại Hạn detail (8 cards) -->
        <div v-if="cdkDaiHan && cdkDaiHanList" class="cdk-dh-details">
          <article v-for="v in cdkDaiHanList" :key="v.cycle_index"
                   :class="['cdk-dh-card', v.isCurrent && 'is-current']">
            <header>
              <h5>
                Vòng {{ v.cycle_index }} — Cung <b>{{ v.branch }}</b>
                <small>({{ v.start_age }}-{{ v.end_age }} tuổi)</small>
                <span v-if="v.isCurrent" class="cdk-current-badge">⭐ HIỆN TẠI</span>
                <span v-else-if="v.isMenhCycle" class="cdk-menh-cycle-badge">Mệnh gốc</span>
              </h5>
            </header>
            <div v-if="v.tong_quan" class="cdk-dh-section">
              <h6>1️⃣ Tổng quan giai đoạn</h6>
              <p v-html="renderWithTooltips(v.tong_quan)"></p>
            </div>
            <div v-if="v.co_hoi_thach_thuc" class="cdk-dh-section">
              <h6>2️⃣ Cơ hội & Thử thách</h6>
              <p v-html="renderWithTooltips(v.co_hoi_thach_thuc)"></p>
            </div>
            <div v-if="v.loi_khuyen" class="cdk-dh-section">
              <h6>3️⃣ Lời khuyên</h6>
              <p v-html="renderWithTooltips(v.loi_khuyen)"></p>
            </div>
          </article>
        </div>

        <!-- VIP button khi chưa có cache -->
        <div v-else class="cdk-dh-cta">
          <p class="cdk-bulk-explain">
            💡 Engine đã có 8 vòng đại hạn raw (cung + tuổi).
            Bấm bên dưới để DeepSeek V4 Pro luận sâu từng vòng — tổng quan + cơ hội + thử thách + lời khuyên.
          </p>
          <button type="button"
                  class="cdk-deep-btn cdk-bulk-btn"
                  :disabled="!cdkDeepFeatureStatus.allowed || cdkDaiHanLoading"
                  @click="loadDaiHan(false)">
            <span v-if="cdkDaiHanLoading">
              <span class="cdk-spinner"></span>
              Đang luận 8 vòng đại hạn... (~4-5 phút)
            </span>
            <span v-else-if="cdkDeepFeatureStatus.allowed">
              🌟 Luận sâu 8 vòng Đại Hạn (~5 phút · tự lưu wiki)
            </span>
            <span v-else>🔒 {{ cdkDeepFeatureStatus.label }}</span>
          </button>
          <p v-if="cdkDaiHanError" class="cdk-deep-error" style="margin-top: 8px;">
            ⚠ {{ cdkDaiHanError }}
          </p>
        </div>

        <button v-if="cdkDaiHan && cdkDeepFeatureStatus.allowed"
                type="button" class="cdk-deep-regen"
                @click="loadDaiHan(true)">
          🔄 Viết lại 8 vòng
        </button>
      </section>

      <!-- Lưu Niên 10 năm tới -->
      <section class="cdk-luu-nien-section">
        <header class="cdk-dh-head">
          <h4>📅 Lưu Niên — 10 năm tới (vận khí từng năm)</h4>
          <span v-if="cdkLuuNien" class="cdk-vip-badge is-ok">✓ Đã luận sâu</span>
        </header>
        <p class="cdk-intro">
          Mỗi năm có
          <abbr class="hv-tooltip" title="Sao Thái Tuế đại diện vận khí năm — chạy theo địa chi năm đó">lưu Thái Tuế</abbr>
          rơi vào 1 cung trên lá số. Kết hợp với
          <abbr class="hv-tooltip" title="Vận 10 năm đang chạy">đại hạn hiện tại</abbr>
          → cho ra vận khí năm cụ thể.
        </p>

        <!-- Bảng 10 năm clickable -->
        <div v-if="cdkLuuNienList" class="cdk-ln-grid">
          <article v-for="y in cdkLuuNienList" :key="y.year"
                   :class="['cdk-ln-chip',
                            y.isCurrent && 'is-current',
                            selectedLuuNien?.year === y.year && 'is-selected']"
                   @click="selectLuuNien(y)">
            <div class="cdk-ln-year">{{ y.year }}</div>
            <div class="cdk-ln-can-chi">{{ y.can_chi }}</div>
            <div class="cdk-ln-age">{{ y.age }} tuổi</div>
            <div class="cdk-ln-thai-tue">Thái Tuế: <b>{{ y.luu_thai_tue_branch }}</b></div>
            <span v-if="y.isCurrent" class="cdk-ln-tag">⭐ Hiện tại</span>
          </article>
        </div>

        <!-- Drawer detail năm được chọn (default = current year) -->
        <transition name="cdk-drawer">
          <article v-if="selectedLuuNien || (cdkLuuNienList && cdkLuuNienList.find((y) => y.isCurrent))"
                   :key="(selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.year"
                   class="cdk-ln-drawer">
            <header>
              <div>
                <h5>Năm {{ (selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.year }}
                  · <b>{{ (selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.can_chi }}</b>
                </h5>
                <small>
                  Tuổi {{ (selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.age }} ·
                  Thái Tuế cung {{ (selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.luu_thai_tue_branch }}
                </small>
              </div>
              <span v-if="(selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.isCurrent"
                    class="cdk-current-badge">⭐ NĂM HIỆN TẠI</span>
            </header>
            <div v-if="(selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.tong_quan" class="cdk-dh-section">
              <h6>1️⃣ Tổng quan năm</h6>
              <p v-html="renderWithTooltips((selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.tong_quan)"></p>
            </div>
            <div v-if="(selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.co_hoi_thach_thuc" class="cdk-dh-section">
              <h6>2️⃣ Cơ hội & Thử thách</h6>
              <p v-html="renderWithTooltips((selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.co_hoi_thach_thuc)"></p>
            </div>
            <div v-if="(selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.loi_khuyen" class="cdk-dh-section">
              <h6>3️⃣ Lời khuyên</h6>
              <p v-html="renderWithTooltips((selectedLuuNien || cdkLuuNienList?.find((y) => y.isCurrent))?.loi_khuyen)"></p>
            </div>
          </article>
        </transition>

        <!-- VIP button khi chưa có cache -->
        <div v-if="!cdkLuuNien" class="cdk-dh-cta">
          <p class="cdk-bulk-explain">
            💡 Engine đã tính sẵn can-chi + lưu Thái Tuế cho 10 năm.
            Bấm bên dưới để DeepSeek V4 Pro luận sâu từng năm cụ thể.
          </p>
          <button type="button"
                  class="cdk-deep-btn cdk-bulk-btn"
                  :disabled="!cdkDeepFeatureStatus.allowed || cdkLuuNienLoading"
                  @click="loadLuuNien(false)">
            <span v-if="cdkLuuNienLoading">
              <span class="cdk-spinner"></span>
              Đang luận 10 năm... (~5 phút)
            </span>
            <span v-else-if="cdkDeepFeatureStatus.allowed">
              📅 Luận sâu 10 năm Lưu Niên (~5 phút · tự lưu wiki)
            </span>
            <span v-else>🔒 {{ cdkDeepFeatureStatus.label }}</span>
          </button>
          <p v-if="cdkLuuNienError" class="cdk-deep-error" style="margin-top: 8px;">
            ⚠ {{ cdkLuuNienError }}
          </p>
        </div>

        <button v-if="cdkLuuNien && cdkDeepFeatureStatus.allowed"
                type="button" class="cdk-deep-regen"
                @click="loadLuuNien(true)">
          🔄 Viết lại 10 năm
        </button>
      </section>

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

    <!-- 6 cách cục — PERSONALIZED cho lá số -->
    <section v-if="cachCucEval || cachCuc" class="cdk-section">
      <h3>📐 6 Cách cục Chiếu Đởm Kinh — so khớp lá số của Anh</h3>
      <p class="cdk-intro" v-if="cachCucEval">
        💡 Engine đã kiểm tra <b>6 mẫu cách cục</b> trong Q4 với lá số Anh.
        <b v-if="cachCucEval.matched_count > 0" style="color: #fcd34d;">Trúng {{ cachCucEval.matched_count }} cách.</b>
        <span v-else>Không cách nào khớp — lá số Anh không rơi vào các pattern đặc thù này.</span>
      </p>

      <!-- Matched -->
      <div v-if="cachCucEval?.matched?.length" class="cdk-cach-group cdk-cach-group-matched">
        <h4>✅ Cách cục TRÚNG ({{ cachCucEval.matched.length }})</h4>
        <article v-for="c in cachCucEval.matched" :key="c.id"
                 class="cdk-cach-card is-matched"
                 :class="[`cdk-cach-${(c.polarity || 'cat').replaceAll('_', '-')}`, c.details?.ky_cach && 'is-ky-cach']">
          <header>
            <strong v-html="renderWithTooltips(c.name_vi)"></strong>
            <small class="cdk-zh">{{ c.name_zh }}</small>
            <span class="cdk-polarity-badge">{{ c.polarity }}</span>
            <span v-if="c.details?.ky_cach" class="cdk-ky-cach-badge">✨ KỲ CÁCH</span>
          </header>
          <p class="cdk-match-reason">
            <b>Vì sao trúng:</b> <span v-html="renderWithTooltips(c.reason)"></span>
          </p>
          <p class="cdk-lesson">📖 <span v-html="renderWithTooltips(c.lesson_short)"></span></p>
          <details>
            <summary>Câu kinh điển + paradigm note</summary>
            <em>« {{ c.source_quote_hv }} »</em>
            <p v-if="c.paradigm_note" class="cdk-paradigm">💡 {{ c.paradigm_note }}</p>
            <small>Nguồn: {{ c.source_ref }}</small>
          </details>
        </article>
      </div>

      <!-- Not matched (collapse) -->
      <details v-if="cachCucEval?.not_matched?.length" class="cdk-cach-not-matched">
        <summary>⚪ {{ cachCucEval.not_matched.length }} cách không trúng (xem chi tiết)</summary>
        <article v-for="c in cachCucEval.not_matched" :key="c.id"
                 class="cdk-cach-card is-not-matched"
                 :class="`cdk-cach-${(c.polarity || 'cat').replaceAll('_', '-')}`">
          <header>
            <strong v-html="renderWithTooltips(c.name_vi)"></strong>
            <small class="cdk-zh">{{ c.name_zh }}</small>
            <span class="cdk-polarity-badge">{{ c.polarity }}</span>
          </header>
          <p class="cdk-not-match-reason">⚪ {{ c.reason }}</p>
          <p class="cdk-lesson"><span v-html="renderWithTooltips(c.lesson_short)"></span></p>
        </article>
      </details>

      <!-- Fallback: render static if no eval -->
      <template v-else-if="!cachCucEval && cachCuc">
        <article v-for="c in cachCuc.cach_cuc" :key="c.id" class="cdk-cach-card"
                 :class="`cdk-cach-${c.polarity.replaceAll('_', '-')}`">
          <header>
            <strong>{{ c.name_vi }}</strong>
            <small class="cdk-zh">{{ c.name_zh }}</small>
            <span class="cdk-polarity-badge">{{ c.polarity }}</span>
          </header>
          <p class="cdk-lesson">{{ c.lesson_short }}</p>
        </article>
      </template>
    </section>

    <!-- Nhập Cốt Tiên Kinh — PERSONALIZED cho lá số -->
    <section v-if="cdkNhapCotPersonalized" class="cdk-section">
      <h3>📚 Nhập Cốt Tiên Kinh — 18 sao của lá số Anh</h3>
      <p class="cdk-intro">
        💡 <b>Phép tổng đoán 4-chữ</b> cho từng sao. Engine đã match 18 Phi Tinh của lá số Anh
        với verdict Q4 p0297:
        <b style="color: #5be5d3;">{{ cdkNhapCotPersonalized.hyCount }}/18 đắc hỷ cung</b>
        ·
        <b style="color: #fca5a5;">{{ cdkNhapCotPersonalized.thatViCount }}/18 thất vị</b>
        ·
        <b style="color: #fcd34d;">3 sao tại Mệnh {{ cdkNhapCotPersonalized.menhBranch }}</b>
      </p>
      <details>
        <summary>📖 Lời mở quyển (verbatim Q4 p0297 r005-r007)</summary>
        <em>« {{ nhapCot.intro_hv }} »</em>
        <p>{{ nhapCot.intro_meaning }}</p>
        <p class="cdk-paradigm">💡 Triết lý nền: từ <abbr class="hv-tooltip" title="Một mối khí ban đầu, chưa phân chia">nhất nguyên hỗn khí</abbr> → ngũ hành → tam tài → âm dương → cát hung. Tất cả 18 sao có cát có hung, mỗi cái đúng theo lẽ riêng.</p>
      </details>

      <div class="cdk-nhapcot-grid">
        <article v-for="s in cdkNhapCotPersonalized.list" :key="s.star_short"
                 :class="['cdk-nhapcot-card',
                          `cdk-tong-${s.category}`,
                          s.isMenh && 'is-menh',
                          s.isHy ? 'is-hy' : 'is-that-vi']">
          <header>
            <div class="cdk-nc-title">
              <button v-if="s.art" type="button" class="cdk-nc-art-btn"
                      :aria-label="`Mở ảnh ${s.star_short}`"
                      @click.stop="openArtCard(s.art)">
                <img :src="s.art.image" :alt="`Ảnh ${s.star_short}`" loading="lazy" />
              </button>
              <div>
                <strong>{{ s.star_short }}</strong>
                <small class="cdk-nc-full">{{ s.star_full }}</small>
              </div>
            </div>
            <div class="cdk-nc-tags">
              <span v-if="s.isMenh" class="cdk-nc-menh-badge">⭐ MỆNH</span>
              <span :class="['cdk-status-chip', s.isHy ? 'is-hy' : '']">
                {{ s.isHy ? '✓ Hỷ cung' : '✗ Thất vị' }}
              </span>
              <span class="cdk-cat-chip">{{ s.category }}</span>
            </div>
          </header>
          <p class="cdk-nc-position">
            Đang đóng tại cung <b>{{ s.branch }}</b>
            <span v-if="s.isHy" class="cdk-nc-hy-note">→ trong hỷ cung của sao này ({{ s.hyCung.join(', ') }})</span>
            <span v-else class="cdk-nc-tv-note">→ hỷ cung của sao là {{ s.hyCung.join(', ') || '(không có)' }}, không trùng {{ s.branch }}</span>
          </p>
          <p class="cdk-nc-verdict">📜 <span v-html="renderWithTooltips(s.verdictSummary)"></span></p>
          <details>
            <summary>Câu kinh điển (Hán-Việt) + cảnh báo</summary>
            <em>« {{ s.verdictQuote }} »</em>
            <p v-if="s.warning" class="cdk-warning-inline">⚠ {{ s.warning }}</p>
            <small>Nguồn: {{ s.sourceRef }}</small>
          </details>
        </article>
      </div>

      <!-- Ending paradigm -->
      <section v-if="nhapCot?.ending_paradigm" class="cdk-ending">
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
.cdk-clock-stage {
  position: relative;
  width: min(860px, 100%);
  aspect-ratio: 1;
  display: grid;
  place-items: center;
}
.cdk-clock-svg {
  width: min(520px, 62%);
  height: auto;
  display: block;
  position: relative;
  z-index: 1;
}
.cdk-clock-card-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2;
}
.cdk-clock-card-group {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px;
  border: 1px solid rgba(167, 139, 250, 0.18);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(2, 6, 23, 0.78), rgba(15, 23, 42, 0.52)),
    rgba(2, 6, 23, 0.58);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.28);
  pointer-events: auto;
  transform: translate(-50%, -50%);
  transition: opacity 160ms, transform 160ms, border-color 160ms, box-shadow 160ms;
}
.cdk-clock-card-group.anchor-left {
  transform: translate(0, -50%);
}
.cdk-clock-card-group.anchor-right {
  transform: translate(-100%, -50%);
}
.cdk-clock-card-group.anchor-center.anchor-top {
  transform: translate(-50%, 0);
}
.cdk-clock-card-group.anchor-center.anchor-bottom {
  transform: translate(-50%, -100%);
}
.cdk-clock-card-group.is-selected {
  border-color: rgba(252, 211, 77, 0.82);
  box-shadow: 0 0 26px rgba(252, 211, 77, 0.32);
  transform: translate(-50%, -50%) scale(1.06);
}
.cdk-clock-card-group.anchor-left.is-selected {
  transform: translate(0, -50%) scale(1.06);
}
.cdk-clock-card-group.anchor-right.is-selected {
  transform: translate(-100%, -50%) scale(1.06);
}
.cdk-clock-card-group.anchor-center.anchor-top.is-selected {
  transform: translate(-50%, 0) scale(1.06);
}
.cdk-clock-card-group.anchor-center.anchor-bottom.is-selected {
  transform: translate(-50%, -100%) scale(1.06);
}
.cdk-clock-card-branch {
  position: absolute;
  left: 6px;
  top: -18px;
  color: #f5e6b1;
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
  text-shadow: 0 1px 8px rgba(2, 6, 23, 0.8);
}
.cdk-clock-card-group.is-menh .cdk-clock-card-branch {
  color: #fcd34d;
}
.cdk-clock-mini-card {
  position: relative;
  width: clamp(48px, 6.6vw, 66px);
  aspect-ratio: 2 / 3;
  padding: 0;
  overflow: hidden;
  border: 1px solid rgba(245, 230, 177, 0.28);
  border-radius: 6px;
  background: rgba(2, 6, 23, 0.72);
  cursor: zoom-in;
}
.cdk-clock-mini-card img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}
.cdk-clock-mini-card span {
  position: absolute;
  left: 4px;
  right: 4px;
  bottom: 4px;
  padding: 2px 3px;
  border-radius: 4px;
  background: rgba(2, 6, 23, 0.78);
  color: #fcd34d;
  font-size: 10px;
  font-weight: 700;
  line-height: 1.1;
  text-align: center;
}
.cdk-clock-mini-card:hover {
  border-color: rgba(252, 211, 77, 0.82);
  transform: translateY(-2px);
}
.cdk-clock-card-extra {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(252, 211, 77, 0.16);
  color: #fcd34d;
  font-size: 12px;
  font-weight: 800;
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
.cdk-drawer-star-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  align-items: start;
}
.cdk-drawer-star {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 9px;
  align-items: start;
  padding: 10px;
  min-width: 0;
  background:
    linear-gradient(135deg, rgba(167, 139, 250, 0.08), rgba(2, 6, 23, 0.42)),
    rgba(2, 6, 23, 0.4);
  border: 1px solid rgba(167, 139, 250, 0.18);
  border-radius: 8px;
}
.cdk-drawer-star-art {
  width: 100%;
  aspect-ratio: 2 / 3;
  padding: 0;
  overflow: hidden;
  border: 1px solid rgba(252, 211, 77, 0.26);
  border-radius: 7px;
  background: rgba(2, 6, 23, 0.72);
  cursor: zoom-in;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.26);
}
.cdk-drawer-star-art img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}
.cdk-drawer-star-art:hover {
  border-color: rgba(252, 211, 77, 0.72);
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(252, 211, 77, 0.18);
}
.cdk-drawer-star-body {
  min-width: 0;
}
.cdk-drawer-star header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 5px;
  margin-bottom: 5px;
}
.cdk-drawer-star strong {
  width: 100%;
  color: #fcd34d;
  font-size: 14px;
  line-height: 1.15;
}
.cdk-drawer-star small {
  display: -webkit-box;
  overflow: hidden;
  color: rgba(230, 238, 245, 0.78);
  font-size: 11.5px;
  line-height: 1.42;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
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

/* Bulk CTA */
.cdk-bulk-cta {
  padding: 4px 2px;
}
.cdk-bulk-explain {
  margin: 0 0 12px;
  padding: 10px 12px;
  background: rgba(91, 229, 211, 0.06);
  border-left: 3px solid rgba(91, 229, 211, 0.4);
  border-radius: 0 6px 6px 0;
  color: rgba(230, 238, 245, 0.84);
  font-size: 12.5px;
  line-height: 1.55;
}
.cdk-bulk-explain b {
  color: #5be5d3;
}
.cdk-bulk-btn {
  font-size: 14px;
  padding: 14px;
}
.cdk-bulk-btn .cdk-spinner {
  margin-right: 8px;
}
.cdk-bulk-summary {
  margin-top: 10px;
  padding: 8px 12px;
  background: rgba(91, 229, 211, 0.1);
  border-radius: 6px;
  color: #5be5d3;
  font-size: 12px;
  text-align: center;
}

/* ─── Personalized cách cục ────────────────────────────────────────── */
.cdk-cach-group {
  margin-bottom: 18px;
}
.cdk-cach-group h4 {
  margin: 14px 0 10px;
  font-size: 14px;
  color: #5be5d3;
}
.cdk-cach-group-matched h4 {
  color: #fcd34d;
}
.cdk-cach-card.is-matched {
  border-left: 3px solid #fcd34d;
  background:
    linear-gradient(135deg, rgba(252, 211, 77, 0.06) 0%, rgba(2, 6, 23, 0.4) 100%),
    rgba(2, 6, 23, 0.5);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}
.cdk-cach-card.is-matched.is-ky-cach {
  border-left-color: #c4b5fd;
  background:
    linear-gradient(135deg, rgba(196, 181, 253, 0.08) 0%, rgba(2, 6, 23, 0.4) 100%),
    rgba(2, 6, 23, 0.5);
}
.cdk-ky-cach-badge {
  display: inline-block;
  padding: 3px 8px;
  margin-left: 8px;
  background: rgba(196, 181, 253, 0.22);
  color: #c4b5fd;
  border-radius: 11px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.cdk-match-reason {
  padding: 8px 10px;
  background: rgba(252, 211, 77, 0.08);
  border-left: 2px solid rgba(252, 211, 77, 0.4);
  border-radius: 0 6px 6px 0;
  color: rgba(230, 238, 245, 0.92);
  font-size: 12.5px;
  margin: 6px 0;
}
.cdk-match-reason b {
  color: #fcd34d;
}
.cdk-cach-not-matched {
  margin-top: 10px;
}
.cdk-cach-not-matched > summary {
  cursor: pointer;
  padding: 8px 12px;
  color: rgba(230, 238, 245, 0.66);
  font-size: 12.5px;
  background: rgba(2, 6, 23, 0.3);
  border-radius: 6px;
}
.cdk-cach-not-matched .cdk-cach-card.is-not-matched {
  opacity: 0.7;
  border-left: 2px dashed rgba(230, 238, 245, 0.16);
}
.cdk-not-match-reason {
  margin: 4px 0;
  color: rgba(230, 238, 245, 0.6);
  font-size: 11.5px;
  font-style: italic;
}

/* ─── HV tooltip (hover-show glossary) ────────────────────────────── */
.hv-tooltip {
  text-decoration: underline dotted rgba(91, 229, 211, 0.55);
  text-underline-offset: 3px;
  cursor: help;
  color: #5be5d3;
}
.hv-tooltip:hover {
  background: rgba(91, 229, 211, 0.12);
  border-radius: 2px;
}

/* ─── Nhập Cốt personalized grid ─────────────────────────────────────── */
.cdk-nhapcot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
  margin: 14px 0;
}
.cdk-nhapcot-card {
  padding: 12px 14px;
  background: rgba(2, 6, 23, 0.4);
  border: 1px solid rgba(230, 238, 245, 0.1);
  border-radius: 8px;
  transition: transform 160ms, border-color 160ms;
}
.cdk-nhapcot-card:hover {
  transform: translateY(-2px);
  border-color: rgba(252, 211, 77, 0.32);
}
.cdk-nhapcot-card.is-menh {
  border-color: #fcd34d;
  background:
    linear-gradient(135deg, rgba(252, 211, 77, 0.08) 0%, rgba(2, 6, 23, 0.4) 100%),
    rgba(2, 6, 23, 0.5);
  box-shadow: 0 4px 14px rgba(252, 211, 77, 0.18);
}
.cdk-nhapcot-card.is-hy {
  border-left: 3px solid #5be5d3;
}
.cdk-nhapcot-card.is-that-vi {
  border-left: 3px dashed rgba(248, 113, 113, 0.5);
}
.cdk-nhapcot-card header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}
.cdk-nc-title {
  display: flex;
  align-items: center;
  gap: 8px;
}
.cdk-nc-art-btn {
  width: 38px; height: 38px;
  padding: 0;
  border: 1px solid rgba(167, 139, 250, 0.25);
  border-radius: 6px;
  background: rgba(2, 6, 23, 0.55);
  cursor: pointer;
  overflow: hidden;
}
.cdk-nc-art-btn img {
  width: 100%; height: 100%; object-fit: cover;
}
.cdk-nhapcot-card strong {
  display: block;
  color: #fcd34d;
  font-size: 14px;
}
.cdk-nc-full {
  display: block;
  color: rgba(230, 238, 245, 0.6);
  font-size: 10.5px;
}
.cdk-nc-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: flex-start;
}
.cdk-nc-menh-badge {
  padding: 2px 6px;
  background: rgba(252, 211, 77, 0.22);
  color: #fcd34d;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
}
.cdk-nc-position {
  margin: 6px 0;
  font-size: 12px;
  color: rgba(230, 238, 245, 0.78);
}
.cdk-nc-position b {
  color: #fcd34d;
}
.cdk-nc-hy-note {
  display: block;
  color: #5be5d3;
  font-size: 11px;
  margin-top: 2px;
}
.cdk-nc-tv-note {
  display: block;
  color: rgba(248, 113, 113, 0.85);
  font-size: 11px;
  margin-top: 2px;
}
.cdk-nc-verdict {
  margin: 8px 0 4px;
  padding: 8px 10px;
  background: rgba(91, 229, 211, 0.05);
  border-radius: 6px;
  color: rgba(230, 238, 245, 0.92);
  font-size: 12.5px;
  line-height: 1.55;
}
.cdk-nhapcot-card details {
  margin-top: 8px;
  font-size: 11.5px;
}
.cdk-nhapcot-card details summary {
  cursor: pointer;
  color: rgba(167, 139, 250, 0.85);
}
.cdk-nhapcot-card details em {
  display: block;
  margin: 6px 0;
  color: rgba(230, 238, 245, 0.7);
  font-style: italic;
}
.cdk-warning-inline {
  color: #fca5a5;
  font-size: 11.5px;
  margin: 4px 0;
}

/* ─── Đại Hạn 8 vòng section ──────────────────────────────────────── */
.cdk-dai-han-section {
  margin: 22px 0 14px;
  padding: 16px;
  background:
    linear-gradient(135deg, rgba(167, 139, 250, 0.05) 0%, rgba(2, 6, 23, 0.4) 100%),
    rgba(2, 6, 23, 0.3);
  border: 1px solid rgba(167, 139, 250, 0.22);
  border-radius: 10px;
}
.cdk-dh-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.cdk-dh-head h4 {
  margin: 0;
  color: #c4b5fd;
  font-size: 15px;
}
.cdk-dh-cycles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 6px;
  margin: 12px 0;
}
.cdk-dh-cycle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(2, 6, 23, 0.4);
  border: 1px solid rgba(230, 238, 245, 0.1);
  border-radius: 7px;
  font-size: 12px;
}
.cdk-dh-cycle.is-current {
  border-color: #fcd34d;
  background:
    linear-gradient(135deg, rgba(252, 211, 77, 0.12) 0%, rgba(2, 6, 23, 0.4) 100%);
  box-shadow: 0 0 14px rgba(252, 211, 77, 0.3);
  animation: cdk-cycle-pulse 2s ease-in-out infinite;
}
.cdk-dh-cycle.is-menh-cycle:not(.is-current) {
  border-color: rgba(252, 211, 77, 0.32);
  border-style: dashed;
}
@keyframes cdk-cycle-pulse {
  0%, 100% { box-shadow: 0 0 8px rgba(252, 211, 77, 0.25); }
  50% { box-shadow: 0 0 18px rgba(252, 211, 77, 0.5); }
}
.cdk-dh-idx {
  font-weight: 700;
  color: rgba(196, 181, 253, 0.85);
  font-size: 11px;
}
.cdk-dh-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.cdk-dh-meta strong {
  color: #fcd34d;
  font-size: 13px;
  line-height: 1.1;
}
.cdk-dh-meta small {
  color: rgba(230, 238, 245, 0.65);
  font-size: 10.5px;
}
.cdk-dh-tag {
  padding: 2px 7px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
  background: rgba(252, 211, 77, 0.22);
  color: #fcd34d;
}
.cdk-dh-tag.is-menh {
  background: rgba(252, 211, 77, 0.1);
  color: rgba(252, 211, 77, 0.7);
}

.cdk-dh-details {
  margin: 16px 0 8px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
.cdk-dh-card {
  padding: 14px 16px;
  background: rgba(2, 6, 23, 0.45);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 9px;
}
.cdk-dh-card.is-current {
  border-color: #fcd34d;
  background:
    linear-gradient(135deg, rgba(252, 211, 77, 0.07) 0%, rgba(2, 6, 23, 0.45) 100%);
  box-shadow: 0 4px 18px rgba(252, 211, 77, 0.18);
}
.cdk-dh-card header h5 {
  margin: 0 0 10px;
  color: #fcd34d;
  font-size: 14px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}
.cdk-dh-card header h5 small {
  color: rgba(230, 238, 245, 0.6);
  font-weight: 400;
  font-size: 12px;
}
.cdk-current-badge {
  padding: 3px 8px;
  background: #fcd34d;
  color: #1f1306;
  border-radius: 10px;
  font-size: 10.5px;
  font-weight: 700;
}
.cdk-menh-cycle-badge {
  padding: 3px 8px;
  background: rgba(252, 211, 77, 0.18);
  color: #fcd34d;
  border-radius: 10px;
  font-size: 10.5px;
}
.cdk-dh-section {
  padding: 8px 10px;
  margin: 6px 0;
  background: rgba(2, 6, 23, 0.4);
  border-radius: 6px;
}
.cdk-dh-section h6 {
  margin: 0 0 6px;
  font-size: 12px;
  color: #5be5d3;
  font-weight: 700;
}
.cdk-dh-section p {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.6;
  color: rgba(230, 238, 245, 0.9);
}
.cdk-dh-cta {
  padding: 10px 0;
}

/* Clock node — vòng đại hạn hiện tại có pulse ring */
.cdk-clock-node.is-current-dai-han .cdk-clock-node-bg {
  animation: cdk-clock-pulse 2s ease-in-out infinite;
}
@keyframes cdk-clock-pulse {
  0%, 100% { filter: drop-shadow(0 0 4px rgba(196, 181, 253, 0.5)); }
  50% { filter: drop-shadow(0 0 14px rgba(196, 181, 253, 0.9)); }
}

/* ─── Lưu Niên section ──────────────────────────────────────────────── */
.cdk-luu-nien-section {
  margin: 14px 0;
  padding: 16px;
  background:
    linear-gradient(135deg, rgba(91, 229, 211, 0.05) 0%, rgba(2, 6, 23, 0.4) 100%),
    rgba(2, 6, 23, 0.3);
  border: 1px solid rgba(91, 229, 211, 0.22);
  border-radius: 10px;
}
.cdk-luu-nien-section .cdk-dh-head h4 {
  color: #5be5d3;
}
.cdk-ln-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(108px, 1fr));
  gap: 6px;
  margin: 12px 0;
}
.cdk-ln-chip {
  padding: 8px 9px;
  background: rgba(2, 6, 23, 0.45);
  border: 1px solid rgba(230, 238, 245, 0.1);
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
  position: relative;
  transition: transform 160ms, border-color 160ms;
}
.cdk-ln-chip:hover {
  transform: translateY(-2px);
  border-color: rgba(91, 229, 211, 0.45);
}
.cdk-ln-chip.is-current {
  border-color: #5be5d3;
  background:
    linear-gradient(135deg, rgba(91, 229, 211, 0.16) 0%, rgba(2, 6, 23, 0.45) 100%);
  box-shadow: 0 0 12px rgba(91, 229, 211, 0.32);
}
.cdk-ln-chip.is-selected {
  border-color: #fcd34d;
  box-shadow: 0 0 14px rgba(252, 211, 77, 0.45);
}
.cdk-ln-year {
  font-size: 16px;
  font-weight: 700;
  color: #fcd34d;
  line-height: 1.1;
}
.cdk-ln-can-chi {
  font-size: 11.5px;
  color: rgba(230, 238, 245, 0.86);
  margin-top: 2px;
}
.cdk-ln-age {
  font-size: 10.5px;
  color: rgba(230, 238, 245, 0.6);
  margin-top: 1px;
}
.cdk-ln-thai-tue {
  font-size: 10px;
  color: rgba(196, 181, 253, 0.85);
  margin-top: 3px;
}
.cdk-ln-thai-tue b {
  color: #c4b5fd;
}
.cdk-ln-tag {
  position: absolute;
  top: -8px;
  right: 4px;
  padding: 1px 6px;
  background: #5be5d3;
  color: #0f1a25;
  font-size: 9.5px;
  font-weight: 700;
  border-radius: 8px;
}
.cdk-ln-drawer {
  margin: 14px 0 8px;
  padding: 14px 16px;
  background: rgba(2, 6, 23, 0.55);
  border: 1px solid rgba(91, 229, 211, 0.32);
  border-radius: 10px;
}
.cdk-ln-drawer > header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(230, 238, 245, 0.1);
}
.cdk-ln-drawer h5 {
  margin: 0;
  color: #5be5d3;
  font-size: 15px;
}
.cdk-ln-drawer h5 b {
  color: #fcd34d;
}
.cdk-ln-drawer small {
  color: rgba(230, 238, 245, 0.6);
  font-size: 12px;
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
  .cdk-clock-stage {
    width: min(520px, 100%);
  }
  .cdk-clock-svg {
    width: min(480px, 100%);
  }
  .cdk-clock-card-layer {
    display: none;
  }
  .cdk-branch-map {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .cdk-drawer-star-row {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
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
  .cdk-drawer-stars {
    width: 100%;
  }
  .cdk-drawer-star-row {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    overscroll-behavior-x: contain;
    scroll-snap-type: x proximity;
    padding-bottom: 4px;
  }
  .cdk-drawer-star {
    flex: 0 0 146px;
    scroll-snap-align: start;
    padding: 8px;
  }
  .cdk-drawer-star header {
    gap: 5px;
  }
  .cdk-drawer-star strong {
    font-size: 13px;
  }
  .cdk-drawer-star small {
    font-size: 11.5px;
    line-height: 1.42;
  }
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
