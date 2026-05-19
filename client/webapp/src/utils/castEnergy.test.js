import { describe, expect, it } from "vitest";

import { CAST_ENERGY_CONSTANTS, computeCastEnergy } from "./castEnergy.js";

describe("computeCastEnergy", () => {
  it("returns durationMs rounded and >= 1", () => {
    const out = computeCastEnergy({ durationMs: 0, pathLengthPx: 0, eventCount: 0 });
    expect(out.durationMs).toBe(1);
  });

  it("clamps emotionBpm into [BPM_MIN, BPM_MAX]", () => {
    // Very high event rate → clamp to max.
    const fast = computeCastEnergy({ durationMs: 100, pathLengthPx: 0, eventCount: 1000 });
    expect(fast.emotionBpm).toBe(CAST_ENERGY_CONSTANTS.BPM_MAX);

    // Very low → clamp to min.
    const slow = computeCastEnergy({ durationMs: 60000, pathLengthPx: 0, eventCount: 1 });
    expect(slow.emotionBpm).toBe(CAST_ENERGY_CONSTANTS.BPM_MIN);
  });

  it("returns 0 emotionBpm when computation is non-finite", () => {
    const out = computeCastEnergy({ durationMs: 1, pathLengthPx: 0, eventCount: NaN });
    expect(out.emotionBpm).toBe(0);
  });

  it("computes a moderate-energy score from medium signals", () => {
    const out = computeCastEnergy({ durationMs: 2000, pathLengthPx: 200, eventCount: 30 });
    // pathComponent = (200/400)*60 = 30, durationComponent = (2000/4000)*40 = 20 → 50
    expect(out.energyScore).toBe(50);
  });

  it("clamps energyScore to 100 maximum", () => {
    const out = computeCastEnergy({ durationMs: 60000, pathLengthPx: 5000, eventCount: 50 });
    expect(out.energyScore).toBe(100);
  });

  it("never returns energyScore below 1", () => {
    const out = computeCastEnergy({ durationMs: 1, pathLengthPx: 0, eventCount: 0 });
    expect(out.energyScore).toBeGreaterThanOrEqual(1);
  });

  it("higher path length monotonically increases energy (within bounds)", () => {
    const a = computeCastEnergy({ durationMs: 2000, pathLengthPx: 100, eventCount: 30 });
    const b = computeCastEnergy({ durationMs: 2000, pathLengthPx: 300, eventCount: 30 });
    expect(b.energyScore).toBeGreaterThanOrEqual(a.energyScore);
  });

  it("longer duration monotonically increases energy (within bounds)", () => {
    const a = computeCastEnergy({ durationMs: 1000, pathLengthPx: 200, eventCount: 30 });
    const b = computeCastEnergy({ durationMs: 3000, pathLengthPx: 200, eventCount: 30 });
    expect(b.energyScore).toBeGreaterThanOrEqual(a.energyScore);
  });

  it("returns integer values for emotionBpm and energyScore", () => {
    const out = computeCastEnergy({ durationMs: 1500, pathLengthPx: 250, eventCount: 23 });
    expect(Number.isInteger(out.emotionBpm)).toBe(true);
    expect(Number.isInteger(out.energyScore)).toBe(true);
  });
});
