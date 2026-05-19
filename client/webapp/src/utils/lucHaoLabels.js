/**
 * Pure label-mapping helpers for Lục Hào ruler-profile fields.
 *
 * Each helper returns a Vietnamese phrase for a given enum value.
 * Falls back to the input or a sensible default if the value is unknown.
 */

export function postureLabel(mode) {
  if (mode === "advance") return "Tiến công có kiểm soát";
  if (mode === "stabilize") return "Ổn định trận địa";
  if (mode === "hide_and_wait") return "Ẩn nhẫn chờ thời";
  return mode || "Ổn định trận địa";
}

export function leverageLabel(mode) {
  if (mode === "light") return "Đòn bẩy thấp (an toàn)";
  if (mode === "normal") return "Đòn bẩy vừa";
  if (mode === "high") return "Đòn bẩy cao (có điều kiện)";
  return mode || "Đòn bẩy vừa";
}

export function coalitionLabel(level) {
  if (level === "high") return "Hợp lực cao";
  if (level === "medium") return "Hợp lực trung bình";
  if (level === "low") return "Hợp lực thấp";
  return level || "Hợp lực trung bình";
}

export function conflictModeLabel(mode) {
  if (mode === "negotiate_first") return "Ưu tiên đàm phán trước";
  if (mode === "legal_last") return "Pháp lý là phương án cuối";
  return mode || "Ưu tiên đàm phán trước";
}

export function counterpartyRiskLabel(mode) {
  if (mode === "screen_required") return "Cần sàng lọc đối tác";
  if (mode === "normal_watch") return "Theo dõi rủi ro mức thường";
  return mode || "Theo dõi rủi ro mức thường";
}

export function scopeGateLabel(mode) {
  if (mode === "small_ok_big_wait") return "Việc nhỏ làm được, việc lớn nên chờ";
  if (mode === "small_big_ok") return "Việc nhỏ/lớn đều có thể triển khai";
  if (mode === "all_wait") return "Tạm hoãn toàn cục";
  return mode || "Việc nhỏ làm được, việc lớn nên chờ";
}

export function pairDynamicsLabel(mode) {
  if (mode === "thunder_wind") return "Sấm-Gió: động lực tăng tốc";
  if (mode === "water_fire") return "Nước-Lửa: xung lực đối nghịch cần cân bằng";
  if (mode === "mountain_lake") return "Núi-Đầm: dừng đúng lúc để thông khí";
  return "Cặp lực khác: cần quan sát thêm";
}
