import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const DATA_JSON = join(ROOT, "data/tu_vi/chieu_dom_kinh_18_phi_tinh.json");
const SOURCE_ROOT = join(ROOT, "data/tu_vi/oracle_cards/chieu_dom_kinh_18_phi_tinh");
const SOURCE_GENERATED = join(SOURCE_ROOT, "generated_cards");
const SOURCE_WEB = join(SOURCE_ROOT, "web_ready");
const SOURCE_MANIFEST = join(SOURCE_ROOT, "cards.json");
const PUBLIC_ROOT = join(ROOT, "client/webapp/public/oracle-cards/chieu-dom-kinh/18-phi-tinh");
const PUBLIC_GENERATED = join(PUBLIC_ROOT, "generated_cards");
const PUBLIC_WEB = join(PUBLIC_ROOT, "web_ready");
const PUBLIC_MANIFEST = join(PUBLIC_ROOT, "cards.json");

const slugByStarId = {
  tu: "tu",
  van: "van",
  phuc: "phuc",
  loc: "loc",
  an: "an",
  tho: "tho",
  truong: "truong",
  kho: "kho",
  dieu: "dieu",
  quy: "quy",
  hong: "hong",
  di: "di",
  mao: "mao",
  hu: "hu",
  quan: "quan",
  hinh: "hinh",
  nhan: "nhan",
  khoc: "khoc",
};

const order = [
  "tu", "van", "phuc", "loc", "an", "tho", "truong", "kho", "dieu",
  "quy", "hong", "di", "mao", "hu", "quan", "hinh", "nhan", "khoc",
];

function ensureDir(path) {
  mkdirSync(path, { recursive: true });
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function cardId(starId) {
  const index = order.indexOf(starId) + 1;
  return `cdk_phi_${String(index).padStart(2, "0")}_${slugByStarId[starId]}`;
}

function findPng(id) {
  if (!existsSync(SOURCE_GENERATED)) return null;
  return readdirSync(SOURCE_GENERATED).find((file) => file.startsWith(`${id}__`) && file.endsWith(".png")) ?? null;
}

function webpName(id) {
  return `${id}.webp`;
}

function ensureWebp(id, pngFile) {
  const sourceWebp = join(SOURCE_WEB, webpName(id));
  if (existsSync(sourceWebp)) return sourceWebp;
  if (!pngFile) return null;

  ensureDir(SOURCE_WEB);
  const sourcePng = join(SOURCE_GENERATED, pngFile);
  try {
    execFileSync("cwebp", ["-q", "78", "-resize", "0", "1152", sourcePng, "-o", sourceWebp], {
      stdio: "ignore",
    });
    return sourceWebp;
  } catch {
    return null;
  }
}

function main() {
  ensureDir(PUBLIC_GENERATED);
  ensureDir(PUBLIC_WEB);

  const schema = readJson(DATA_JSON);
  const stars = [...schema.phi_tinh_9_duong, ...schema.phi_tinh_9_am];
  const cards = stars.map((star) => {
    const id = cardId(star.id);
    const pngFile = findPng(id);
    const webpPath = ensureWebp(id, pngFile);
    const publicPng = pngFile ? `${id}.png` : null;
    const publicWebp = webpPath ? webpName(id) : null;

    if (pngFile) {
      copyFileSync(join(SOURCE_GENERATED, pngFile), join(PUBLIC_GENERATED, publicPng));
    }
    if (webpPath) {
      copyFileSync(webpPath, join(PUBLIC_WEB, publicWebp));
    }

    return {
      id,
      star_id: star.id,
      index: order.indexOf(star.id) + 1,
      title: star.name_vi,
      name_zh: star.name_zh,
      polarity: star.polarity,
      element: star.ngu_hanh,
      image: publicWebp ? `/oracle-cards/chieu-dom-kinh/18-phi-tinh/web_ready/${publicWebp}` : null,
      full_image: publicPng ? `/oracle-cards/chieu-dom-kinh/18-phi-tinh/generated_cards/${publicPng}` : null,
      source_image: pngFile ? `generated_cards/${pngFile}` : null,
      web_ready_source: publicWebp ? `web_ready/${publicWebp}` : null,
      status: publicWebp ? "web_ready" : pngFile ? "generated" : "planned",
    };
  });

  const manifest = {
    deck_id: "chieu_dom_kinh_18_phi_tinh_v1",
    generated_at: new Date().toISOString(),
    source_schema: "data/tu_vi/chieu_dom_kinh_18_phi_tinh.json",
    public_base: "/oracle-cards/chieu-dom-kinh/18-phi-tinh",
    total_cards: cards.length,
    ready_cards: cards.filter((card) => card.status === "web_ready").length,
    cards,
  };

  writeFileSync(SOURCE_MANIFEST, `${JSON.stringify(manifest, null, 2)}\n`);
  writeFileSync(PUBLIC_MANIFEST, `${JSON.stringify(manifest, null, 2)}\n`);
  console.log(`Synced ${manifest.ready_cards}/${manifest.total_cards} Chiếu Đởm Kinh Phi Tinh cards.`);
}

main();
