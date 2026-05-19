/**
 * Pure builders for Lục Hào reporting derivations.
 *
 * Extracted from LucHaoResultPage.vue. Each function takes a `result`
 * object (the API response from /api/luc-hao/cast) and returns a value
 * suitable for direct rendering in the Vue template.
 */

/**
 * Build the Markdown export of a Lục Hào case.
 */
export function buildMarkdownReport(result) {
  if (!result) return "";
  const lines = [
    "# Báo cáo nghiệm Lục Hào",
    "",
    `- Câu hỏi: ${result.question_text}`,
    `- Kết luận: ${result.verdict.text} (${result.verdict.tag})`,
    `- Quẻ chủ: ${result.primary_hexagram.name_vi} (${result.primary_hexagram.binary})`,
    `- Quẻ biến: ${result.transformed_hexagram.name_vi} (${result.transformed_hexagram.binary})`,
    `- Hào động: ${result.moving_lines.join(", ") || "Không có"}`,
    `- Thế/Ứng: Hào ${result.the_line} / Hào ${result.ung_line}`,
    "",
    "## Phân tích hào động",
  ];
  (result.moving_line_analysis || []).forEach((row) => {
    lines.push(`- Hào ${row.line_position} · ${row.luc_than} · ${row.impact}`);
  });
  lines.push("", "## 6 hào chi tiết");
  (result.lines || []).forEach((line) => {
    lines.push(
      `- Hào ${line.line_position}: ${line.symbol}, ${line.branch}/${line.element}, ${line.luc_than}` +
        `${line.moving ? ", Động" : ", Tĩnh"}` +
        `${line.is_tuan_khong ? ", Tuần Không" : ""}` +
        `${line.is_month_break ? ", Nguyệt Phá" : ""}` +
        `${line.is_day_break ? ", Nhật Phá" : ""}`
    );
  });
  if (result.timing_prediction?.best_match) {
    lines.push("", "## Ứng kỳ dự đoán");
    lines.push(
      `- Nhịp độ: ${result.timing_prediction.pace_bucket}`,
      `- Đơn vị gợi ý: ${result.timing_prediction.timing_unit_hint}`,
      `- Mốc chính: D+${result.timing_prediction.best_match.offset_days} · ${result.timing_prediction.best_match.reason}`
    );
  }
  return lines.join("\n");
}

/**
 * Map Mai Hoa relation_tag → quick conclusion sentence.
 */
export function quickMaiHoaConclusion(env) {
  if (!env) return "Chưa đủ dữ liệu Mai Hoa để kết luận nhanh.";
  if (env.relation_tag === "supportive") return "Tốt: Dụng sinh Thể, bối cảnh đang trợ lực.";
  if (env.relation_tag === "controlling") return "Khá tốt: Thể khắc Dụng, chủ động kiểm soát được tình thế.";
  if (env.relation_tag === "pressure") return "Cần thận trọng: Dụng khắc Thể, ngoại cảnh tạo áp lực.";
  if (env.relation_tag === "draining") return "Chậm mà chắc: Thể sinh Dụng, có dấu hiệu hao lực.";
  return "Trung tính: Thế cân bằng, cần thêm tín hiệu xác nhận.";
}

/**
 * Compose the bullet list of integrated advice from a result payload.
 */
export function buildIntegratedAdvice(result) {
  if (!result) return [];
  const items = [];
  items.push(`Năng lượng tổng: ${result.energy_flow_summary}`);
  if (result.timing_prediction?.best_match) {
    const best = result.timing_prediction.best_match;
    items.push(
      `Ưu tiên thời điểm: D+${best.offset_days}${best.branch ? ` (ngày ${best.branch})` : ""} - ${best.reason}.`
    );
  }
  if (result.dung_than) {
    items.push(`Đối tượng quẻ: ${result.dung_than.luc_than} tại hào ${result.dung_than.line_position}.`);
  }
  if (result.hidden_line_candidates?.length) {
    items.push(
      `Có ${result.hidden_line_candidates.length} tín hiệu ẩn đồng lục thân, nên theo dõi thêm trước khi chốt quyết định lớn.`
    );
  }
  items.push(
    "Human Design / Pythagoras: lớp mở rộng v1 đang ở chế độ placeholder để không bỏ sót hướng phát triển."
  );
  return items;
}

/**
 * Map ruler confidence enum → label + CSS class.
 */
export function rulerConfidenceMeta(confidence) {
  if (confidence === "high") return { label: "Tin cậy cao", className: "confidence-high" };
  if (confidence === "medium") return { label: "Tin cậy trung bình", className: "confidence-medium" };
  if (confidence === "low") return { label: "Tin cậy thấp", className: "confidence-low" };
  return { label: "Chưa rõ", className: "confidence-unknown" };
}

/**
 * Build the timing-candidates list with stable keys for v-for.
 */
export function buildTimingCandidates(result) {
  const candidates = result?.timing_prediction?.candidates || [];
  return candidates.map((item, idx) => ({
    key: `${item.branch || "formula"}-${item.offset_days}-${idx}`,
    label: item.branch ? `Ngày ${item.branch}` : "Mốc công thức Mai Hoa",
    offset: item.offset_days,
    reason: item.reason,
  }));
}
