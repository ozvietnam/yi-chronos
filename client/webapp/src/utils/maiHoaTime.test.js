import { describe, expect, it } from "vitest";

import {
  EARTHLY_BRANCHES,
  TRIGRAM_BITS,
  TRIGRAM_BY_NUMBER,
  buildFormulaText,
  computeMaiHoaState,
  hourBranchNumber,
  safeMod,
  yearBranchNumber,
  zonedDateParts,
} from "./maiHoaTime.js";

describe("safeMod", () => {
  it("returns modulo when remainder is 0", () => {
    expect(safeMod(8, 8)).toBe(8);
    expect(safeMod(16, 8)).toBe(8);
    expect(safeMod(6, 6)).toBe(6);
  });
  it("returns normal remainder otherwise", () => {
    expect(safeMod(7, 8)).toBe(7);
    expect(safeMod(13, 8)).toBe(5);
    expect(safeMod(1, 6)).toBe(1);
  });
});

describe("EARTHLY_BRANCHES", () => {
  it("has all 12 branches in canonical order", () => {
    expect(EARTHLY_BRANCHES).toEqual([
      "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
      "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
    ]);
  });
});

describe("TRIGRAM_BY_NUMBER + TRIGRAM_BITS", () => {
  it("maps 8 trigrams in tiên-thiên order", () => {
    expect(TRIGRAM_BY_NUMBER[1]).toBe("Càn");
    expect(TRIGRAM_BY_NUMBER[8]).toBe("Khôn");
  });
  it("each trigram has 3 bits", () => {
    for (const name of Object.values(TRIGRAM_BY_NUMBER)) {
      expect(TRIGRAM_BITS[name]).toMatch(/^[01]{3}$/);
    }
  });
});

describe("yearBranchNumber", () => {
  it("returns 1 (Tý) for 1984 (Giáp Tý anchor)", () => {
    expect(yearBranchNumber(1984)).toBe(1);
  });
  it("returns 5 (Thìn) for 2024 (Giáp Thìn)", () => {
    expect(yearBranchNumber(2024)).toBe(5);
  });
  it("returns 7 (Ngọ) for 2026 (Bính Ngọ)", () => {
    expect(yearBranchNumber(2026)).toBe(7);
  });
  it("handles years before 1984 with proper modulo wrapping", () => {
    expect(yearBranchNumber(1983)).toBe(12);
    expect(yearBranchNumber(1972)).toBe(1);
  });
});

describe("hourBranchNumber", () => {
  it("Tý hour spans 23-00:59 → branch 1", () => {
    expect(hourBranchNumber(23)).toBe(1);
    expect(hourBranchNumber(0)).toBe(1);
  });
  it("Sửu = 1-3 → branch 2", () => {
    expect(hourBranchNumber(1)).toBe(2);
    expect(hourBranchNumber(2)).toBe(2);
  });
  it("Ngọ = 11-13 → branch 7", () => {
    expect(hourBranchNumber(11)).toBe(7);
    expect(hourBranchNumber(12)).toBe(7);
  });
  it("Hợi = 21-23 → branch 12", () => {
    expect(hourBranchNumber(21)).toBe(12);
    expect(hourBranchNumber(22)).toBe(12);
  });
});

describe("zonedDateParts", () => {
  it("decomposes a UTC date into local parts in Asia/Ho_Chi_Minh", () => {
    const dt = new Date("2026-05-11T03:00:00Z"); // 10:00 in Hanoi
    const parts = zonedDateParts(dt, "Asia/Ho_Chi_Minh");
    expect(parts.year).toBe(2026);
    expect(parts.month).toBe(5);
    expect(parts.day).toBe(11);
    expect(parts.hour).toBe(10);
  });
});

describe("computeMaiHoaState", () => {
  it("computes upper/lower/moving using Niên-Nguyệt-Nhật-Thời formula", () => {
    // 2026-05-11 10:00 Hanoi: yearNum=Ngọ=7, month=5, day=11, hour=10→Tỵ=6
    const dt = new Date("2026-05-11T03:00:00Z");
    const state = computeMaiHoaState(dt, "Asia/Ho_Chi_Minh");
    expect(state.yearNum).toBe(7);
    expect(state.monthNum).toBe(5);
    expect(state.dayNum).toBe(11);
    expect(state.hourNum).toBe(6);
    // upper = (7 + 5 + 11) % 8 = 23 % 8 = 7 → Cấn
    expect(state.upper).toBe(7);
    expect(state.upperTrigram).toBe("Cấn");
    // lower = (7+5+11+6) % 8 = 29 % 8 = 5 → Tốn
    expect(state.lower).toBe(5);
    expect(state.lowerTrigram).toBe("Tốn");
    // moving = 29 % 6 = 5
    expect(state.moving).toBe(5);
  });

  it("never returns trigram 0", () => {
    const dt = new Date("2024-01-01T00:00:00Z");
    const state = computeMaiHoaState(dt, "UTC");
    expect(state.upper).toBeGreaterThanOrEqual(1);
    expect(state.upper).toBeLessThanOrEqual(8);
    expect(state.lower).toBeGreaterThanOrEqual(1);
    expect(state.lower).toBeLessThanOrEqual(8);
    expect(state.moving).toBeGreaterThanOrEqual(1);
    expect(state.moving).toBeLessThanOrEqual(6);
  });

  it("hour branch label reflects hourNum index", () => {
    const dt = new Date("2026-05-11T03:00:00Z");
    const state = computeMaiHoaState(dt, "Asia/Ho_Chi_Minh");
    expect(state.hourBranch).toBe(EARTHLY_BRANCHES[state.hourNum - 1]);
  });
});

describe("buildFormulaText", () => {
  it("includes the three formula lines", () => {
    const state = computeMaiHoaState(
      new Date("2026-05-11T03:00:00Z"),
      "Asia/Ho_Chi_Minh"
    );
    const text = buildFormulaText(state);
    expect(text.upper).toMatch(/mod 8 = \d+/);
    expect(text.lower).toMatch(/mod 8 = \d+/);
    expect(text.moving).toMatch(/mod 6 = \d+/);
  });
});
