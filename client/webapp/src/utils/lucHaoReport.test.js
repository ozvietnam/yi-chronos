import { describe, expect, it } from "vitest";

import {
  buildIntegratedAdvice,
  buildMarkdownReport,
  buildTimingCandidates,
  quickMaiHoaConclusion,
  rulerConfidenceMeta,
} from "./lucHaoReport.js";

const sampleResult = {
  question_text: "Có nên ký hợp đồng?",
  verdict: { text: "Khả thi", tag: "feasible" },
  primary_hexagram: { name_vi: "Càn", binary: "111111" },
  transformed_hexagram: { name_vi: "Cấu", binary: "111110" },
  moving_lines: [1],
  the_line: 6,
  ung_line: 3,
  moving_line_analysis: [
    { line_position: 1, luc_than: "Tử", impact: "tăng" },
  ],
  lines: [
    {
      line_position: 1,
      symbol: "▬▬",
      branch: "Tý",
      element: "thủy",
      luc_than: "Tử",
      moving: true,
      is_tuan_khong: false,
      is_month_break: false,
      is_day_break: false,
    },
  ],
  timing_prediction: {
    pace_bucket: "trung bình",
    timing_unit_hint: "ngày",
    best_match: {
      offset_days: 7,
      branch: "Tỵ",
      reason: "trùng dụng thần",
    },
    candidates: [
      { branch: "Tỵ", offset_days: 7, reason: "trùng dụng thần" },
      { branch: null, offset_days: 14, reason: "công thức Mai Hoa" },
    ],
  },
  energy_flow_summary: "thuận",
  dung_than: { luc_than: "Tài", line_position: 3 },
  hidden_line_candidates: [{ line_position: 5 }],
};

describe("buildMarkdownReport", () => {
  it("returns empty string for null result", () => {
    expect(buildMarkdownReport(null)).toBe("");
  });
  it("starts with a top-level heading", () => {
    const md = buildMarkdownReport(sampleResult);
    expect(md.startsWith("# Báo cáo nghiệm Lục Hào")).toBe(true);
  });
  it("includes question text and verdict", () => {
    const md = buildMarkdownReport(sampleResult);
    expect(md).toContain("Có nên ký hợp đồng?");
    expect(md).toContain("Khả thi");
  });
  it("renders moving lines list", () => {
    const md = buildMarkdownReport(sampleResult);
    expect(md).toContain("## Phân tích hào động");
    expect(md).toContain("Hào 1");
  });
  it("renders 6-line detail with Động/Tĩnh tags", () => {
    const md = buildMarkdownReport(sampleResult);
    expect(md).toContain("## 6 hào chi tiết");
    expect(md).toContain("Động");
  });
  it("renders timing prediction when present", () => {
    const md = buildMarkdownReport(sampleResult);
    expect(md).toContain("## Ứng kỳ dự đoán");
    expect(md).toContain("D+7");
  });
  it("handles missing optional fields gracefully", () => {
    const partial = {
      ...sampleResult,
      moving_lines: [],
      moving_line_analysis: undefined,
      timing_prediction: null,
    };
    const md = buildMarkdownReport(partial);
    expect(md).toContain("Hào động: Không có");
    expect(md).not.toContain("## Ứng kỳ dự đoán");
  });
});

describe("quickMaiHoaConclusion", () => {
  it("returns sentence for each known relation_tag", () => {
    expect(quickMaiHoaConclusion({ relation_tag: "supportive" })).toContain("trợ lực");
    expect(quickMaiHoaConclusion({ relation_tag: "controlling" })).toContain("kiểm soát");
    expect(quickMaiHoaConclusion({ relation_tag: "pressure" })).toContain("áp lực");
    expect(quickMaiHoaConclusion({ relation_tag: "draining" })).toContain("hao lực");
  });
  it("returns neutral fallback for unknown tag", () => {
    expect(quickMaiHoaConclusion({ relation_tag: "anything" })).toContain("Trung tính");
  });
  it("explains absence of data", () => {
    expect(quickMaiHoaConclusion(null)).toContain("Chưa đủ dữ liệu");
  });
});

describe("buildIntegratedAdvice", () => {
  it("returns empty array for null", () => {
    expect(buildIntegratedAdvice(null)).toEqual([]);
  });
  it("includes energy + timing + dung_than + hidden_line items", () => {
    const items = buildIntegratedAdvice(sampleResult);
    expect(items.length).toBeGreaterThanOrEqual(4);
    expect(items.some((s) => s.includes("Năng lượng"))).toBe(true);
    expect(items.some((s) => s.includes("D+7"))).toBe(true);
    expect(items.some((s) => s.includes("Tài"))).toBe(true);
    expect(items.some((s) => s.includes("tín hiệu ẩn"))).toBe(true);
  });
});

describe("rulerConfidenceMeta", () => {
  it.each([
    ["high", "Tin cậy cao", "confidence-high"],
    ["medium", "Tin cậy trung bình", "confidence-medium"],
    ["low", "Tin cậy thấp", "confidence-low"],
  ])("%s → %s/%s", (input, label, className) => {
    const meta = rulerConfidenceMeta(input);
    expect(meta.label).toBe(label);
    expect(meta.className).toBe(className);
  });
  it("falls back for unknown", () => {
    expect(rulerConfidenceMeta(undefined).className).toBe("confidence-unknown");
  });
});

describe("buildTimingCandidates", () => {
  it("returns empty for missing predictions", () => {
    expect(buildTimingCandidates({})).toEqual([]);
    expect(buildTimingCandidates(null)).toEqual([]);
  });
  it("maps branch + formula candidates with stable keys", () => {
    const out = buildTimingCandidates(sampleResult);
    expect(out).toHaveLength(2);
    expect(out[0].label).toContain("Tỵ");
    expect(out[1].label).toContain("Mai Hoa");
    expect(new Set(out.map((c) => c.key)).size).toBe(out.length);
  });
});
