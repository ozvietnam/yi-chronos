import { describe, expect, it } from "vitest";

import {
  coalitionLabel,
  conflictModeLabel,
  counterpartyRiskLabel,
  leverageLabel,
  pairDynamicsLabel,
  postureLabel,
  scopeGateLabel,
} from "./lucHaoLabels.js";

describe("postureLabel", () => {
  it.each([
    ["advance", "Tiến công có kiểm soát"],
    ["stabilize", "Ổn định trận địa"],
    ["hide_and_wait", "Ẩn nhẫn chờ thời"],
  ])("%s → %s", (mode, expected) => {
    expect(postureLabel(mode)).toBe(expected);
  });
  it("falls back to default for unknown", () => {
    expect(postureLabel(undefined)).toBe("Ổn định trận địa");
  });
});

describe("leverageLabel", () => {
  it.each([
    ["light", "Đòn bẩy thấp (an toàn)"],
    ["normal", "Đòn bẩy vừa"],
    ["high", "Đòn bẩy cao (có điều kiện)"],
  ])("%s → %s", (mode, expected) => {
    expect(leverageLabel(mode)).toBe(expected);
  });
});

describe("coalitionLabel", () => {
  it("maps high/medium/low", () => {
    expect(coalitionLabel("high")).toBe("Hợp lực cao");
    expect(coalitionLabel("medium")).toBe("Hợp lực trung bình");
    expect(coalitionLabel("low")).toBe("Hợp lực thấp");
  });
});

describe("conflictModeLabel", () => {
  it("maps negotiate_first and legal_last", () => {
    expect(conflictModeLabel("negotiate_first")).toBe("Ưu tiên đàm phán trước");
    expect(conflictModeLabel("legal_last")).toBe("Pháp lý là phương án cuối");
  });
});

describe("counterpartyRiskLabel", () => {
  it("maps both risk levels", () => {
    expect(counterpartyRiskLabel("screen_required")).toBe("Cần sàng lọc đối tác");
    expect(counterpartyRiskLabel("normal_watch")).toBe("Theo dõi rủi ro mức thường");
  });
});

describe("scopeGateLabel", () => {
  it("maps three scope gates", () => {
    expect(scopeGateLabel("small_ok_big_wait")).toBe("Việc nhỏ làm được, việc lớn nên chờ");
    expect(scopeGateLabel("small_big_ok")).toBe("Việc nhỏ/lớn đều có thể triển khai");
    expect(scopeGateLabel("all_wait")).toBe("Tạm hoãn toàn cục");
  });
});

describe("pairDynamicsLabel", () => {
  it("maps thunder/wind, water/fire, mountain/lake", () => {
    expect(pairDynamicsLabel("thunder_wind")).toContain("Sấm-Gió");
    expect(pairDynamicsLabel("water_fire")).toContain("Nước-Lửa");
    expect(pairDynamicsLabel("mountain_lake")).toContain("Núi-Đầm");
  });
  it("returns generic phrase for unknown", () => {
    expect(pairDynamicsLabel("xyz")).toBe("Cặp lực khác: cần quan sát thêm");
  });
});

describe("contract: every helper falls back to a non-empty string", () => {
  const helpers = [
    postureLabel,
    leverageLabel,
    coalitionLabel,
    conflictModeLabel,
    counterpartyRiskLabel,
    scopeGateLabel,
    pairDynamicsLabel,
  ];
  it.each(helpers)("%s does not return empty for null", (fn) => {
    const out = fn(null);
    expect(typeof out).toBe("string");
    expect(out.length).toBeGreaterThan(0);
  });
});
