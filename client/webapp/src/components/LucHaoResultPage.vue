<script setup>
import { computed, ref, watch } from "vue";
import { getHexagramInterpretationV2, saveLucHaoCase, submitLucHaoFeedback } from "../lib/api";

const props = defineProps({
  result: {
    type: Object,
    default: null
  },
  meta: {
    type: Object,
    default: null
  }
});

const saveStatus = ref("");
const saveError = ref("");
const savedCaseId = ref("");
const feedbackStatus = ref("");
const feedbackError = ref("");
const activeInsightTab = ref("overview");
const interpretationV2 = ref(null);
const interpretationV2Error = ref("");
const feedbackForm = ref({
  result_enum: "matched",
  confidence_enum: "medium",
  event_summary: "",
  resolved_at_local: "",
  tags: ""
});

// Pure builders extracted to ../utils/lucHaoReport.js (covered by vitest).
import {
  buildIntegratedAdvice,
  buildMarkdownReport,
  buildTimingCandidates,
  quickMaiHoaConclusion as quickMaiHoaConclusionFn,
  rulerConfidenceMeta as rulerConfidenceMetaFn,
} from "../utils/lucHaoReport.js";

const markdownReport = computed(() => buildMarkdownReport(props.result));
const timingCandidates = computed(() => buildTimingCandidates(props.result));
const quickMaiHoaConclusion = computed(() =>
  quickMaiHoaConclusionFn(props.result?.mai_hoa_environment)
);
const integratedAdviceItems = computed(() => buildIntegratedAdvice(props.result));
const rulerConfidenceMeta = computed(() => {
  return rulerConfidenceMetaFn(props.result?.ruler_profile?.confidence);
});

// Label helpers extracted to ../utils/lucHaoLabels.js (see tests there).
import {
  coalitionLabel,
  conflictModeLabel,
  counterpartyRiskLabel,
  leverageLabel,
  pairDynamicsLabel,
  postureLabel,
  scopeGateLabel,
} from "../utils/lucHaoLabels.js";

async function loadInterpretationV2() {
  const kingWenIndex = props.result?.primary_hexagram?.king_wen_index;
  interpretationV2.value = null;
  interpretationV2Error.value = "";
  if (!kingWenIndex) return;
  try {
    const payload = await getHexagramInterpretationV2(kingWenIndex);
    interpretationV2.value = payload.status === "ok" ? payload.record : null;
  } catch (error) {
    interpretationV2Error.value = "Chưa tải được diễn giải 5 tầng.";
  }
}

watch(
  () => props.result?.primary_hexagram?.king_wen_index,
  () => {
    loadInterpretationV2();
  },
  { immediate: true }
);

async function onSaveCase() {
  if (!props.result || !props.meta) return;
  saveStatus.value = "";
  saveError.value = "";
  try {
    const payload = {
      question_text: props.meta.question_text || props.result.question_text,
      timezone: props.meta.timezone || "Asia/Ho_Chi_Minh",
      luc_hao_state: props.result,
      interaction_signal: props.meta.interaction_signal || {
        hold_duration_ms: 0,
        move_event_count: 0,
        path_length_px: 0,
        release_timestamp_ms: Date.now()
      }
    };
    const response = await saveLucHaoCase(payload);
    savedCaseId.value = response.case_id;
    saveStatus.value = `Đã lưu hồ sơ: ${response.case_id}`;
  } catch (error) {
    saveError.value = "Không lưu được hồ sơ nghiệm. Kiểm tra backend rồi thử lại.";
  }
}

async function onSubmitFeedback() {
  if (!savedCaseId.value) {
    feedbackError.value = "Hãy lưu hồ sơ trước rồi mới gửi phản hồi hậu nghiệm.";
    return;
  }
  feedbackStatus.value = "";
  feedbackError.value = "";
  try {
    const payload = {
      case_id: savedCaseId.value,
      result_enum: feedbackForm.value.result_enum,
      confidence_enum: feedbackForm.value.confidence_enum,
      event_summary: feedbackForm.value.event_summary,
      resolved_at_local: feedbackForm.value.resolved_at_local || null,
      tags: feedbackForm.value.tags
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)
    };
    const response = await submitLucHaoFeedback(payload);
    feedbackStatus.value = `Đã lưu phản hồi: ${response.feedback_id}`;
  } catch (error) {
    feedbackError.value = "Không lưu được phản hồi hậu nghiệm.";
  }
}

async function copyMarkdown() {
  if (!markdownReport.value) return;
  try {
    await navigator.clipboard.writeText(markdownReport.value);
    saveStatus.value = "Đã copy báo cáo Markdown.";
  } catch (error) {
    saveError.value = "Không copy được Markdown.";
  }
}

function downloadMarkdown() {
  if (!markdownReport.value) return;
  const blob = new Blob([markdownReport.value], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `luc-hao-report-${Date.now()}.md`;
  link.click();
  URL.revokeObjectURL(url);
}
</script>

<template>
  <section class="luc-hao-page panel" aria-label="Trang kết quả Lục Hào">
    <div class="panel-title">
      <div>
        <h3>Kết quả Lục Hào chi tiết</h3>
        <small>Trang riêng để đọc nghiệm rõ ràng, không rối bố cục chính.</small>
      </div>
    </div>

    <div v-if="!result" class="empty-state">
      Chưa có dữ liệu. Hãy gieo tại tab <strong>Đồng hồ Mai Hoa 3D</strong> để tạo kết quả.
    </div>

    <template v-else>
      <div class="toolbar">
        <button type="button" @click="copyMarkdown">Copy Markdown</button>
        <button type="button" @click="downloadMarkdown">Tải .md cho khách</button>
        <button type="button" @click="onSaveCase">Lưu hồ sơ huấn luyện</button>
      </div>
      <p v-if="saveStatus" class="ok-msg">{{ saveStatus }}</p>
      <p v-if="saveError" class="err-msg">{{ saveError }}</p>

      <div class="result-header">
        <div>
          <span>Câu hỏi</span>
          <strong>{{ result.question_text }}</strong>
        </div>
        <div>
          <span>Kết luận</span>
          <strong>{{ result.verdict.text }}</strong>
        </div>
      </div>

      <div class="insight-tabs" aria-label="Tab kết quả đa tầng">
        <button type="button" :class="{ active: activeInsightTab === 'overview' }" @click="activeInsightTab = 'overview'">
          Tab 1 - Tổng quan (Mai Hoa)
        </button>
        <button type="button" :class="{ active: activeInsightTab === 'detail' }" @click="activeInsightTab = 'detail'">
          Tab 2 - Chi tiết (Lục Hào)
        </button>
        <button type="button" :class="{ active: activeInsightTab === 'advice' }" @click="activeInsightTab = 'advice'">
          Tab 3 - Lời khuyên
        </button>
        <button type="button" :class="{ active: activeInsightTab === 'jingfang' }" @click="activeInsightTab = 'jingfang'" v-if="result.jingfang_scaffold">
          Tab 4 - 京房 (8 Cung · Nạp Giáp · Phục Thần)
        </button>
      </div>

      <div v-if="activeInsightTab === 'overview'" class="analysis-block">
        <h4>Tổng quan nhanh theo Mai Hoa</h4>
        <div class="timing-summary">
          <article class="best">
            <span>Kết luận nhanh Tốt/Xấu</span>
            <strong>{{ quickMaiHoaConclusion }}</strong>
          </article>
          <article v-if="result.mai_hoa_environment">
            <span>Quẻ môi trường</span>
            <strong>{{ result.mai_hoa_environment.upper_trigram }} / {{ result.mai_hoa_environment.lower_trigram }}</strong>
          </article>
          <article v-if="result.mai_hoa_environment">
            <span>Quan hệ ngũ hành</span>
            <strong>{{ result.mai_hoa_environment.relation }}</strong>
          </article>
        </div>
      </div>

      <div v-if="activeInsightTab === 'detail'" class="result-grid">
        <article>
          <span>Quẻ chủ</span>
          <strong>{{ result.primary_hexagram.name_vi }} ({{ result.primary_hexagram.binary }})</strong>
        </article>
        <article>
          <span>Quẻ biến</span>
          <strong>{{ result.transformed_hexagram.name_vi }} ({{ result.transformed_hexagram.binary }})</strong>
        </article>
        <article>
          <span>Hào động</span>
          <strong>{{ result.moving_lines.join(", ") || "Không có" }}</strong>
        </article>
        <article>
          <span>Thế / Ứng</span>
          <strong>Hào {{ result.the_line }} / Hào {{ result.ung_line }}</strong>
        </article>
      </div>

      <div v-if="activeInsightTab === 'detail' && result.mai_hoa_environment" class="analysis-block">
        <h4>Dòng chảy năng lượng (Mai Hoa gốc + Lục Hào)</h4>
        <div class="fusion-box">
          <p class="fusion-summary">{{ result.energy_flow_summary }}</p>
          <div class="fusion-grid">
            <div>
              <span>Quẻ môi trường</span>
              <strong>{{ result.mai_hoa_environment.upper_trigram }} / {{ result.mai_hoa_environment.lower_trigram }}</strong>
            </div>
            <div>
              <span>Quan hệ ngũ hành</span>
              <strong>{{ result.mai_hoa_environment.relation }}</strong>
            </div>
            <div>
              <span>Hào động môi trường</span>
              <strong>Hào {{ result.mai_hoa_environment.moving_line_num }}</strong>
            </div>
            <div>
              <span>Kết luận chi tiết</span>
              <strong>{{ result.verdict.text }}</strong>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeInsightTab === 'detail'" class="analysis-block">
        <h4>Phân tích hào động</h4>
        <ul>
          <li v-for="row in result.moving_line_analysis" :key="row.line_position">
            Hào {{ row.line_position }} · {{ row.luc_than }} · {{ row.impact }}
          </li>
        </ul>
      </div>

      <div v-if="activeInsightTab === 'detail' && result.ruler_profile" class="analysis-block">
        <h4>Ruler đang dùng</h4>
        <div class="timing-candidate-list">
          <div class="timing-head">
            {{ result.ruler_profile.id }} · confidence: {{ result.ruler_profile.confidence }}
            <span :class="['confidence-pill', rulerConfidenceMeta.className]">{{ rulerConfidenceMeta.label }}</span>
          </div>
          <div class="timing-row">
            <strong>Context</strong>
            <small>{{ result.ruler_profile.layers?.context }}</small>
          </div>
          <div class="timing-row">
            <strong>Process</strong>
            <small>{{ result.ruler_profile.layers?.process }}</small>
          </div>
          <div class="timing-row">
            <strong>Timing</strong>
            <small>{{ result.ruler_profile.layers?.timing }}</small>
          </div>
          <div class="timing-row">
            <strong>Action</strong>
            <small>{{ result.ruler_profile.layers?.action }}</small>
          </div>
          <div class="timing-row">
            <strong>Decision quality</strong>
            <small>{{ result.ruler_profile.decision_quality || "mixed" }}</small>
          </div>
          <div class="timing-row">
            <strong>Strategy mode</strong>
            <small>{{ result.ruler_profile.strategy_mode || "stabilize" }}</small>
          </div>
          <div class="timing-row">
            <strong>Posture mode</strong>
            <small>{{ postureLabel(result.ruler_profile.posture_mode || "stabilize") }}</small>
          </div>
          <div class="timing-row">
            <strong>Leverage mode</strong>
            <small>{{ leverageLabel(result.ruler_profile.leverage_mode || "normal") }}</small>
          </div>
          <div class="timing-row">
            <strong>Coalition strength</strong>
            <small>{{ coalitionLabel(result.ruler_profile.coalition_strength || "medium") }}</small>
          </div>
          <div class="timing-row">
            <strong>Conflict mode</strong>
            <small>{{ conflictModeLabel(result.ruler_profile.conflict_mode || "negotiate_first") }}</small>
          </div>
          <div class="timing-row">
            <strong>Counterparty risk</strong>
            <small>{{ counterpartyRiskLabel(result.ruler_profile.counterparty_risk || "normal_watch") }}</small>
          </div>
          <div class="timing-row">
            <strong>Scope gate</strong>
            <small>{{ scopeGateLabel(result.ruler_profile.scope_gate || "small_ok_big_wait") }}</small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.triple_condition_check">
            <strong>Triple condition check</strong>
            <small>
              Thiên thời: {{ result.ruler_profile.triple_condition_check.timing_ready ? "đạt" : "chưa" }} ·
              Địa lợi: {{ result.ruler_profile.triple_condition_check.resource_ready ? "đạt" : "chưa" }} ·
              Nhân hòa: {{ result.ruler_profile.triple_condition_check.social_ready ? "đạt" : "chưa" }} ·
              Điểm {{ result.ruler_profile.triple_condition_check.score }} ·
              {{
                result.ruler_profile.triple_condition_check.allow_execute
                  ? "Cho phép execute"
                  : "Chưa nên execute"
              }}
            </small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.one_line_verdict">
            <strong>One-line verdict</strong>
            <small>{{ result.ruler_profile.one_line_verdict }}</small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.tradeoff_hint">
            <strong>Tradeoff hint</strong>
            <small>{{ result.ruler_profile.tradeoff_hint }}</small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.evidence_gate">
            <strong>Evidence gate</strong>
            <small>
              {{
                result.ruler_profile.evidence_gate.status === "ready"
                  ? "Đủ bằng chứng"
                  : "Thiếu bằng chứng"
              }}
              · {{ result.ruler_profile.evidence_gate.note }}
            </small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.context_trigram_roles">
            <strong>Vai trò quẻ thượng/hạ</strong>
            <small>
              Thượng {{ result.ruler_profile.context_trigram_roles.upper_trigram?.name }}:
              {{ result.ruler_profile.context_trigram_roles.upper_trigram?.role }} ·
              Hạ {{ result.ruler_profile.context_trigram_roles.lower_trigram?.name }}:
              {{ result.ruler_profile.context_trigram_roles.lower_trigram?.role }}
            </small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.pair_dynamics">
            <strong>Pair dynamics</strong>
            <small>{{ pairDynamicsLabel(result.ruler_profile.pair_dynamics) }}</small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.timing_dual_view">
            <strong>Timing dual view</strong>
            <small>
              Forward: {{ result.ruler_profile.timing_dual_view.forward_offsets?.join(", ") || "-" }} ·
              Reverse check: {{ result.ruler_profile.timing_dual_view.reverse_check_offsets?.join(", ") || "-" }}
            </small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.virtue_anchor">
            <strong>Virtue anchor</strong>
            <small>{{ result.ruler_profile.virtue_anchor }}</small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.reverse_probe">
            <strong>Reverse probe</strong>
            <small>
              Mốc chính D+{{ result.ruler_profile.reverse_probe.best_offset_days }} ·
              Kiểm lại: {{ result.ruler_profile.reverse_probe.check_offsets?.join(", ") }} ·
              {{ result.ruler_profile.reverse_probe.note }}
            </small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.staged_plan">
            <strong>Staged plan</strong>
            <small>
              Prepare: {{ result.ruler_profile.staged_plan.prepare }}<br />
              Trigger: {{ result.ruler_profile.staged_plan.trigger }}<br />
              Push: {{ result.ruler_profile.staged_plan.push }}
            </small>
          </div>
          <div class="timing-row" v-if="result.ruler_profile.recovery_cycle">
            <strong>Recovery cycle</strong>
            <small>
              {{
                result.ruler_profile.recovery_cycle.is_recovery_case
                  ? "Case phục hồi"
                  : "Case thường"
              }}
              <template v-if="result.ruler_profile.recovery_cycle.reentry_window?.length">
                · Re-entry: {{ result.ruler_profile.recovery_cycle.reentry_window.join(", ") }}
              </template>
              · {{ result.ruler_profile.recovery_cycle.note }}
            </small>
          </div>
          <div class="timing-row">
            <strong>Ghi chú</strong>
            <small>{{ result.ruler_profile.notes }}</small>
          </div>
        </div>
      </div>

      <div v-if="activeInsightTab === 'detail' && result.timing_prediction" class="analysis-block">
        <h4>Ứng kỳ dự đoán (3 tầng)</h4>
        <div class="timing-summary">
          <article>
            <span>Nhịp độ sự việc</span>
            <strong>{{ result.timing_prediction.pace_bucket }}</strong>
          </article>
          <article>
            <span>Đơn vị thời gian gợi ý</span>
            <strong>{{ result.timing_prediction.timing_unit_hint }}</strong>
          </article>
          <article>
            <span>Dụng thần</span>
            <strong>{{ result.dung_than?.luc_than }} · {{ result.dung_than?.branch }} (Hào {{ result.dung_than?.line_position }})</strong>
          </article>
          <article class="best">
            <span>Mốc ưu tiên</span>
            <strong>
              D+{{ result.timing_prediction.best_match.offset_days }}
              <template v-if="result.timing_prediction.best_match.branch">
                · Ngày {{ result.timing_prediction.best_match.branch }}
              </template>
            </strong>
            <small>{{ result.timing_prediction.best_match.reason }}</small>
          </article>
        </div>

        <div class="timing-candidate-list">
          <div class="timing-head">Các mốc ứng viên theo phễu lọc</div>
          <div v-for="item in timingCandidates" :key="item.key" class="timing-row">
            <strong>{{ item.label }}</strong>
            <span>D+{{ item.offset }}</span>
            <small>{{ item.reason }}</small>
          </div>
        </div>
      </div>

      <div v-if="activeInsightTab === 'detail'" class="analysis-block">
        <h4>6 hào chi tiết</h4>
        <div class="line-table">
          <div class="line-head">Hào</div>
          <div class="line-head">Ký hiệu</div>
          <div class="line-head">Chi / Hành</div>
          <div class="line-head">Lục thân</div>
          <div class="line-head">Trạng thái</div>

          <template v-for="line in result.lines" :key="line.line_position">
            <div>{{ line.line_position }}</div>
            <div>{{ line.symbol }}</div>
            <div>{{ line.branch }} / {{ line.element }}</div>
            <div>{{ line.luc_than }}</div>
            <div>
              <span v-if="line.moving">Động</span>
              <span v-else>Tĩnh</span>
              <span v-if="line.is_tuan_khong"> · Tuần Không</span>
              <span v-if="line.is_month_break"> · Nguyệt Phá</span>
              <span v-if="line.is_day_break"> · Nhật Phá</span>
            </div>
          </template>
        </div>
      </div>

      <div v-if="activeInsightTab === 'advice'" class="analysis-block">
        <h4>Lời khuyên hợp nhất</h4>
        <div class="fusion-box">
          <p class="fusion-summary">
            Gộp Mai Hoa + Lục Hào + Ứng kỳ để ra khuyến nghị hành động có thứ tự ưu tiên.
          </p>
          <ul>
            <li v-for="(item, idx) in integratedAdviceItems" :key="`advice-${idx}`">{{ item }}</li>
          </ul>
          <div class="timing-candidate-list">
            <div class="timing-head">Lời khuyên hành động theo nhịp</div>
            <div class="timing-row">
              <strong>Nên làm ngay</strong>
              <small>Thao tác nhỏ, rủi ro thấp, theo đúng mốc ứng kỳ ưu tiên.</small>
            </div>
            <div class="timing-row">
              <strong>Nên hoãn</strong>
              <small>Việc lớn nếu hào đang phá/không hoặc bối cảnh hao lực.</small>
            </div>
            <div class="timing-row">
              <strong>Nên tránh</strong>
              <small>Quyết định all-in khi chưa có thêm xác thực thực tế.</small>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeInsightTab === 'advice'" class="analysis-block">
        <h4>Diễn giải 5 tầng (Tam Thiên v2)</h4>
        <p v-if="interpretationV2Error" class="err-msg">{{ interpretationV2Error }}</p>
        <div v-else-if="interpretationV2" class="timing-candidate-list">
          <div class="timing-head">
            Quẻ {{ interpretationV2.name_vi }} · #{{ interpretationV2.king_wen_index }}
          </div>
          <div class="timing-row">
            <strong>Thế gian sự vụ</strong>
            <small>{{ interpretationV2.the_gian_su_vu }}</small>
          </div>
          <div class="timing-row">
            <strong>Nhập thế</strong>
            <small>{{ interpretationV2.nhap_the }}</small>
          </div>
          <div class="timing-row">
            <strong>Xuất thế</strong>
            <small>{{ interpretationV2.xuat_the }}</small>
          </div>
          <div class="timing-row">
            <strong>Thế gian vận</strong>
            <small>{{ interpretationV2.the_gian_van }}</small>
          </div>
          <div class="timing-row">
            <strong>An bài thế sự</strong>
            <small>{{ interpretationV2.an_bai_the_su }}</small>
          </div>
        </div>
      </div>

      <div class="analysis-block">
        <h4>Phản hồi hậu nghiệm (đúng/sai để huấn luyện LLM)</h4>
        <div class="feedback-grid">
          <label>
            Kết quả thực tế
            <select v-model="feedbackForm.result_enum">
              <option value="matched">Đúng</option>
              <option value="partly">Đúng một phần</option>
              <option value="false">Sai</option>
              <option value="unknown">Chưa rõ</option>
            </select>
          </label>
          <label>
            Mức tin cậy
            <select v-model="feedbackForm.confidence_enum">
              <option value="high">Cao</option>
              <option value="medium">Trung bình</option>
              <option value="low">Thấp</option>
              <option value="unsure">Chưa chắc</option>
            </select>
          </label>
          <label>
            Thời điểm ngã ngũ
            <input v-model="feedbackForm.resolved_at_local" type="datetime-local" />
          </label>
          <label>
            Tags (phẩy ngăn cách)
            <input v-model="feedbackForm.tags" placeholder="hợp đồng, tài chính, chậm tiến độ" />
          </label>
          <label class="full">
            Tóm tắt diễn biến thực tế
            <textarea v-model="feedbackForm.event_summary" rows="3" placeholder="Mô tả sự việc để đối chiếu nghiệm..." />
          </label>
        </div>
        <button type="button" class="submit-feedback-btn" @click="onSubmitFeedback">Gửi phản hồi hậu nghiệm</button>
        <p v-if="feedbackStatus" class="ok-msg">{{ feedbackStatus }}</p>
        <p v-if="feedbackError" class="err-msg">{{ feedbackError }}</p>
      </div>

      <!-- Tab 4 — 京房 scaffold (8 Cung · Nạp Giáp · Lục thân theo Cung · Phục thần) -->
      <div v-if="activeInsightTab === 'jingfang' && result.jingfang_scaffold" class="analysis-block jingfang-block">
        <h3>京房 — Tầng sâu Kinh Phòng</h3>
        <p class="jf-intro">
          Đây là tầng <b>京房 易</b> — phân loại quẻ theo <b>8 cung</b>, gán <b>Nạp Giáp</b> (Thiên Can + Địa Chi)
          cho từng hào, từ đó tính <b>Lục thân theo cung</b> (TA = nguyên tố cung). <b>Phục thần</b> là các lục thân
          vắng mặt trong quẻ Chánh, tra ngược về <em>thuần quẻ</em> của cung — đây là yếu tố quyết định nhiều
          phán đoán sâu trong Văn Vương dòng Kinh Phòng.
        </p>

        <div class="jf-summary">
          <div class="jf-cell">
            <span>Cung</span>
            <strong>{{ result.jingfang_scaffold.palace_trigram }}</strong>
            <small>{{ result.jingfang_scaffold.palace_position_name }} · {{ result.jingfang_scaffold.palace_element }}</small>
          </div>
          <div class="jf-cell">
            <span>Thế hào</span>
            <strong>Hào {{ result.jingfang_scaffold.shih_yao_position }}</strong>
          </div>
          <div class="jf-cell">
            <span>Ứng hào</span>
            <strong>Hào {{ result.jingfang_scaffold.ying_yao_position }}</strong>
          </div>
          <div class="jf-cell">
            <span>Thân hào</span>
            <strong>Hào {{ result.jingfang_scaffold.shen_yao_position }}</strong>
          </div>
        </div>

        <!-- 28-tú primary mansion card -->
        <div v-if="result.jingfang_scaffold.primary_xiu" class="xiu-card" :data-quadrant="result.jingfang_scaffold.primary_xiu.quadrant">
          <div class="xiu-head">
            <div class="xiu-glyph">{{ result.jingfang_scaffold.primary_xiu.name_cn }}</div>
            <div class="xiu-info">
              <h6>28-tú chủ quẻ — {{ result.jingfang_scaffold.primary_xiu.name_vi }} ({{ result.jingfang_scaffold.primary_xiu.name_cn }})</h6>
              <p class="xiu-meta">
                <span class="xiu-pill quadrant">{{ result.jingfang_scaffold.primary_xiu.quadrant }} phương</span>
                <span class="xiu-pill spirit">{{ result.jingfang_scaffold.primary_xiu.spirit }}</span>
                <span class="xiu-pill element">{{ result.jingfang_scaffold.primary_xiu.element_7yao }}</span>
                <span class="xiu-pill animal">Totem: {{ result.jingfang_scaffold.primary_xiu.animal }}</span>
              </p>
            </div>
          </div>
        </div>

        <h4>Nạp Giáp — Lục thân theo cung (TA = {{ result.jingfang_scaffold.palace_element }})</h4>
        <table class="jf-table">
          <thead>
            <tr>
              <th>Hào</th><th>Thiên Can</th><th>Địa Chi</th><th>Ngũ hành</th><th>Lục thân</th><th>Đặc biệt</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="y in [...result.jingfang_scaffold.najia_per_yao].reverse()"
                :key="y.yao_position"
                :class="{
                  'jf-shih': y.yao_position === result.jingfang_scaffold.shih_yao_position,
                  'jf-ying': y.yao_position === result.jingfang_scaffold.ying_yao_position,
                }">
              <td>Hào {{ y.yao_position }}</td>
              <td>{{ y.stem }}</td>
              <td>{{ y.branch }}</td>
              <td>{{ y.element }}</td>
              <td><b>{{ y.luc_than }}</b></td>
              <td>
                <span v-if="y.yao_position === result.jingfang_scaffold.shih_yao_position" class="tag-shih">世 Thế</span>
                <span v-if="y.yao_position === result.jingfang_scaffold.ying_yao_position" class="tag-ying">應 Ứng</span>
                <span v-if="y.yao_position === result.jingfang_scaffold.shen_yao_position" class="tag-shen">身 Thân</span>
              </td>
            </tr>
          </tbody>
        </table>

        <h4>伏神 (Phục thần) — Lục thân ẩn</h4>
        <div v-if="!result.jingfang_scaffold.hidden_lines.length" class="jf-empty">
          Quẻ Chánh hiển hiện đầy đủ 5 lục thân — không có Phục thần.
        </div>
        <ul v-else class="jf-fushen">
          <li v-for="h in result.jingfang_scaffold.hidden_lines" :key="h.luc_than" class="jf-fushen-card">
            <div class="jf-fushen-head">
              <strong>{{ h.luc_than }}</strong>
              <span class="jf-fushen-meta">{{ h.stem }} {{ h.branch }} ({{ h.element }})</span>
            </div>
            <p class="jf-fushen-note">
              Ẩn dưới <b>hào {{ h.visible_yao_position }}</b>
              (hào hiện là <em>{{ h.visible_yao_luc_than }}</em>).
              Trích từ thuần quẻ cung {{ result.jingfang_scaffold.palace_trigram }}.
            </p>
          </li>
        </ul>
      </div>
    </template>
  </section>
</template>

<style scoped>
h3 {
  margin: 0;
  font-size: 16px;
}
.empty-state {
  border: 1px dashed #c3d7dd;
  border-radius: 8px;
  padding: 16px;
  color: #45656d;
  background: #f8fcfd;
}
.toolbar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.toolbar button,
.submit-feedback-btn {
  border: 1px solid #1f8a7f;
  border-radius: 8px;
  background: #0f766e;
  color: #f3fffd;
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}
.ok-msg {
  margin: 8px 0 0;
  color: #166534;
  background: #dcfce7;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 8px;
  font-size: 12px;
}
.err-msg {
  margin: 8px 0 0;
  color: #7f1d1d;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 8px;
  font-size: 12px;
}
.result-header {
  display: grid;
  gap: 10px;
  grid-template-columns: 1fr 1fr;
}
.result-header span,
.result-grid span {
  display: block;
  font-size: 12px;
  color: #5a747b;
  font-weight: 700;
}
.result-header strong,
.result-grid strong {
  display: block;
  margin-top: 4px;
  color: #0f3c43;
}
.result-grid {
  margin-top: 12px;
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.result-grid article {
  border: 1px solid #d7e8ec;
  border-radius: 8px;
  background: #fff;
  padding: 10px;
}
.analysis-block {
  margin-top: 14px;
}
.analysis-block h4 {
  margin: 0 0 8px;
  color: #13454e;
}
.insight-tabs {
  margin-top: 12px;
  display: inline-flex;
  gap: 8px;
  padding: 4px;
  border: 1px solid #d7e8ec;
  border-radius: 10px;
  background: #f8fcfd;
}
.insight-tabs button {
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 700;
  color: #32555d;
  background: transparent;
  cursor: pointer;
}
.insight-tabs button.active {
  border-color: #0f766e;
  background: #0f766e;
  color: #f2fffc;
}
.analysis-block ul {
  margin: 0;
  padding-left: 18px;
  color: #2f5962;
  line-height: 1.5;
}
.fusion-box {
  border: 1px solid #d7e8ec;
  border-radius: 8px;
  background: #f8fcfd;
  padding: 10px;
}
.fusion-summary {
  margin: 0 0 10px;
  color: #0f3c43;
  font-size: 13px;
  font-weight: 700;
}
.fusion-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}
.fusion-grid span,
.fusion-grid strong {
  display: block;
}
.fusion-grid span {
  font-size: 11px;
  color: #5d787f;
}
.fusion-grid strong {
  color: #123c44;
  font-size: 13px;
}
.feedback-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.feedback-grid label {
  display: block;
  font-size: 12px;
  color: #47666e;
  font-weight: 700;
}
.feedback-grid input,
.feedback-grid select,
.feedback-grid textarea {
  width: 100%;
  margin-top: 4px;
  border: 1px solid #c9dce2;
  border-radius: 8px;
  padding: 8px;
  font-size: 13px;
  font-family: inherit;
}
.feedback-grid .full {
  grid-column: 1 / -1;
}
.submit-feedback-btn {
  margin-top: 10px;
}
.line-table {
  display: grid;
  grid-template-columns: 52px 110px 140px 120px 1fr;
  border: 1px solid #d5e7eb;
  border-radius: 8px;
  overflow: hidden;
}
.line-table > div {
  padding: 8px;
  border-bottom: 1px solid #e3eef1;
  border-right: 1px solid #e3eef1;
  font-size: 13px;
  color: #244a52;
  background: #fff;
}
.line-table > div:nth-child(5n) {
  border-right: none;
}
.line-head {
  background: #edf7f9 !important;
  font-weight: 700;
}
.timing-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.timing-summary article {
  border: 1px solid #d7e8ec;
  border-radius: 8px;
  padding: 10px;
  background: #fff;
}
.timing-summary .best {
  grid-column: 1 / -1;
  background: #f0f9ff;
  border-color: #bae6fd;
}
.timing-summary span,
.timing-summary strong,
.timing-summary small {
  display: block;
}
.timing-summary span {
  font-size: 12px;
  color: #5a747b;
  font-weight: 700;
}
.timing-summary strong {
  margin-top: 4px;
  color: #0f3c43;
}
.timing-summary small {
  margin-top: 6px;
  color: #3f5f67;
  font-size: 12px;
}
.timing-candidate-list {
  margin-top: 10px;
  border: 1px solid #d7e8ec;
  border-radius: 8px;
  overflow: hidden;
}
.timing-head {
  background: #edf7f9;
  color: #1f4a53;
  font-size: 12px;
  font-weight: 700;
  padding: 8px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.timing-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px 10px;
  padding: 8px 10px;
  border-top: 1px solid #e3eef1;
  background: #fff;
}
.timing-row strong {
  color: #123c44;
  font-size: 13px;
}
.timing-row span {
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
}
.timing-row small {
  grid-column: 1 / -1;
  color: #49666d;
  font-size: 12px;
}

.confidence-pill {
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

.confidence-high {
  background: #dcfce7;
  border-color: #86efac;
  color: #166534;
}

.confidence-medium {
  background: #fef9c3;
  border-color: #fde047;
  color: #854d0e;
}

.confidence-low {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #991b1b;
}

.confidence-unknown {
  background: #e5e7eb;
  border-color: #d1d5db;
  color: #374151;
}
@media (max-width: 920px) {
  .result-header,
  .result-grid,
  .feedback-grid {
    grid-template-columns: 1fr;
  }
  .fusion-grid {
    grid-template-columns: 1fr;
  }
  .insight-tabs {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr;
  }
  .timing-summary {
    grid-template-columns: 1fr;
  }
  .line-table {
    grid-template-columns: 1fr;
  }
  .line-head {
    display: none;
  }
}

/* ── Tab 4 — 京房 scaffold ─────────────────────────────────────────────── */
.jingfang-block {
  background: rgba(91, 229, 211, 0.04);
  border: 1px solid rgba(91, 229, 211, 0.22);
  border-radius: 8px;
  padding: 16px 18px;
}
.jingfang-block h3 {
  margin: 0 0 8px 0;
  color: var(--accent-teal, #5be5d3);
  font-size: 16px;
}
.jingfang-block h4 {
  margin: 18px 0 8px 0;
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 700;
}
.jf-intro {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  margin: 0 0 12px 0;
  border-left: 3px solid rgba(91, 229, 211, 0.4);
  padding-left: 12px;
}
.jf-intro b { color: var(--accent-gold-soft, #f5e6b1); }
.jf-intro em { color: var(--accent-teal, #5be5d3); font-style: normal; }

.jf-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  padding: 10px;
  background: rgba(232, 201, 90, 0.06);
  border: 1px solid rgba(232, 201, 90, 0.22);
  border-radius: 6px;
}
.jf-cell { display: flex; flex-direction: column; gap: 2px; }
.jf-cell span {
  font-size: 10px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}
.jf-cell strong {
  font-size: 16px;
  color: var(--accent-gold-soft, #f5e6b1);
}
.jf-cell small {
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
}

.jf-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.jf-table th {
  text-align: left;
  padding: 6px 10px;
  font-size: 11px;
  color: var(--text-muted, rgba(230, 238, 245, 0.5));
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.jf-table td {
  padding: 6px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: var(--text-primary, #e6eef5);
}
.jf-table tr.jf-shih {
  background: rgba(232, 201, 90, 0.06);
}
.jf-table tr.jf-ying {
  background: rgba(91, 229, 211, 0.05);
}
.tag-shih, .tag-ying, .tag-shen {
  display: inline-block;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 3px;
  margin-right: 4px;
  font-weight: 700;
}
.tag-shih { background: rgba(232, 201, 90, 0.18); color: var(--accent-gold, #e8c95a); }
.tag-ying { background: rgba(91, 229, 211, 0.18); color: var(--accent-teal, #5be5d3); }
.tag-shen { background: rgba(214, 90, 120, 0.18); color: #d65a78; }

.jf-empty {
  font-size: 12.5px;
  color: var(--text-muted, rgba(230, 238, 245, 0.55));
  font-style: italic;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
}
.jf-fushen { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
.jf-fushen-card {
  background: rgba(214, 90, 74, 0.06);
  border-left: 3px solid #d65a4a;
  border-radius: 0 6px 6px 0;
  padding: 10px 12px;
}
.jf-fushen-head { display: flex; gap: 12px; align-items: baseline; flex-wrap: wrap; }
.jf-fushen-head strong {
  font-size: 14px;
  color: #f5b08c;
}
.jf-fushen-meta {
  font-size: 12px;
  color: var(--text-muted, rgba(230, 238, 245, 0.6));
  font-family: ui-monospace, monospace;
}
.jf-fushen-note {
  margin: 4px 0 0 0;
  font-size: 12.5px;
  line-height: 1.5;
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
}
.jf-fushen-note b { color: var(--accent-gold-soft, #f5e6b1); }
.jf-fushen-note em { color: var(--accent-teal, #5be5d3); font-style: normal; }

/* ── 28-tú card ─────────────────────────────────────────────────────────── */
.xiu-card {
  margin-top: 14px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-soft, rgba(255, 255, 255, 0.08));
  border-left: 3px solid var(--accent-gold, #e8c95a);
  border-radius: 6px;
}
.xiu-card[data-quadrant="Đông"] { border-left-color: #5ab07a; }
.xiu-card[data-quadrant="Bắc"]  { border-left-color: #5b8ee5; }
.xiu-card[data-quadrant="Tây"]  { border-left-color: #c0a878; }
.xiu-card[data-quadrant="Nam"]  { border-left-color: #d65a4a; }

.xiu-head { display: flex; gap: 14px; align-items: center; }
.xiu-glyph {
  font-size: 38px;
  font-family: "Noto Serif TC", "Noto Serif SC", serif;
  color: var(--accent-gold-soft, #f5e6b1);
  line-height: 1;
  min-width: 56px;
  text-align: center;
}
.xiu-info { flex: 1; }
.xiu-info h6 {
  margin: 0 0 6px 0;
  font-size: 13px;
  color: var(--accent-gold-soft, #f5e6b1);
  text-transform: none;
  letter-spacing: 0;
  font-weight: 700;
}
.xiu-meta { margin: 0; display: flex; gap: 6px; flex-wrap: wrap; }
.xiu-pill {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary, rgba(230, 238, 245, 0.78));
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.xiu-pill.quadrant { background: rgba(91, 229, 211, 0.1); color: var(--accent-teal, #5be5d3); border-color: rgba(91, 229, 211, 0.3); }
.xiu-pill.spirit   { background: rgba(232, 201, 90, 0.1); color: var(--accent-gold, #e8c95a); border-color: rgba(232, 201, 90, 0.3); }
.xiu-pill.element  { background: rgba(214, 90, 74, 0.08); color: #f5b08c; border-color: rgba(214, 90, 74, 0.25); }
.xiu-pill.animal   { background: rgba(90, 176, 122, 0.08); color: #88d39e; border-color: rgba(90, 176, 122, 0.25); }
</style>
