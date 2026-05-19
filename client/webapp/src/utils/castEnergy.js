/**
 * Pure cast-energy computation for Mai Hoa pointer-capture casting.
 *
 * Given the raw pointer signals collected during a "gieo" gesture
 * (duration in ms, total path length in pixels, number of pointer events),
 * derive:
 *   - emotionBpm: rough heart-rate analogue (events per minute), clamped
 *   - energyScore: 0..100 composite of path length and duration
 *
 * Extracted from MaiHoaClock3D.vue for testability + reuse.
 */

const BPM_MIN = 8;
const BPM_MAX = 220;
const ENERGY_PATH_REFERENCE_PX = 400;
const ENERGY_DURATION_REFERENCE_MS = 4000;
const ENERGY_PATH_WEIGHT = 60;
const ENERGY_DURATION_WEIGHT = 40;

/**
 * @param {{ durationMs: number, pathLengthPx: number, eventCount: number }} signal
 * @returns {{ durationMs: number, emotionBpm: number, energyScore: number }}
 */
export function computeCastEnergy({ durationMs, pathLengthPx, eventCount }) {
  const safeDuration = Math.max(durationMs, 1);

  const rawBpm = (eventCount / safeDuration) * 60000;
  const emotionBpm = Number.isFinite(rawBpm)
    ? Math.max(BPM_MIN, Math.min(Math.round(rawBpm), BPM_MAX))
    : 0;

  const pathComponent = (pathLengthPx / ENERGY_PATH_REFERENCE_PX) * ENERGY_PATH_WEIGHT;
  const durationComponent =
    (safeDuration / ENERGY_DURATION_REFERENCE_MS) * ENERGY_DURATION_WEIGHT;
  const rawEnergy = Math.round(Math.min(100, pathComponent + durationComponent));
  const energyScore = Math.max(1, rawEnergy);

  return {
    durationMs: Math.round(safeDuration),
    emotionBpm,
    energyScore,
  };
}

export const CAST_ENERGY_CONSTANTS = {
  BPM_MIN,
  BPM_MAX,
  ENERGY_PATH_REFERENCE_PX,
  ENERGY_DURATION_REFERENCE_MS,
  ENERGY_PATH_WEIGHT,
  ENERGY_DURATION_WEIGHT,
};
