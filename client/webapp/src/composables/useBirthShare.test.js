/**
 * Tests for useBirthShare — kabala-style ?birth= URL share contract.
 */

import { describe, expect, it } from "vitest";

import { encodeBirthSlug, parseBirthSlug } from "./useBirthShare.js";


describe("parseBirthSlug", () => {
  it("parses canonical kabala format YYYY-MM-DD-HH-nam", () => {
    expect(parseBirthSlug("1995-08-15-10-nam")).toEqual({
      birthDatetimeLocal: "1995-08-15T10:00:00",
      gender: "nam",
      source: "kabala",
    });
  });

  it("parses with female gender 'nu' (normalized to 'nữ')", () => {
    expect(parseBirthSlug("1990-12-31-23-nu")).toEqual({
      birthDatetimeLocal: "1990-12-31T23:00:00",
      gender: "nữ",
      source: "kabala",
    });
  });

  it("parses with female gender 'nữ' verbatim", () => {
    const result = parseBirthSlug("1990-12-31-23-nữ");
    expect(result?.gender).toBe("nữ");
  });

  it("parses without gender suffix (gender=null)", () => {
    expect(parseBirthSlug("2000-01-01-00")).toEqual({
      birthDatetimeLocal: "2000-01-01T00:00:00",
      gender: null,
      source: "kabala",
    });
  });

  it("handles single-digit month/day/hour", () => {
    expect(parseBirthSlug("1995-8-5-9-nam")).toEqual({
      birthDatetimeLocal: "1995-08-05T09:00:00",
      gender: "nam",
      source: "kabala",
    });
  });

  it("parses ISO datetime fallback", () => {
    expect(parseBirthSlug("1995-08-15T10:30:00")).toEqual({
      birthDatetimeLocal: "1995-08-15T10:30:00",
      gender: null,
      source: "iso",
    });
  });

  it("rejects empty / null", () => {
    expect(parseBirthSlug("")).toBeNull();
    expect(parseBirthSlug(null)).toBeNull();
    expect(parseBirthSlug(undefined)).toBeNull();
  });

  it("rejects malformed year", () => {
    expect(parseBirthSlug("95-08-15-10-nam")).toBeNull();
    expect(parseBirthSlug("19950-08-15-10-nam")).toBeNull();
  });

  it("rejects out-of-range month", () => {
    expect(parseBirthSlug("1995-13-15-10-nam")).toBeNull();
    expect(parseBirthSlug("1995-00-15-10-nam")).toBeNull();
  });

  it("rejects out-of-range hour", () => {
    expect(parseBirthSlug("1995-08-15-24-nam")).toBeNull();
  });

  it("rejects unknown gender token", () => {
    expect(parseBirthSlug("1995-08-15-10-male")).toBeNull();
    expect(parseBirthSlug("1995-08-15-10-xyz")).toBeNull();
  });

  it("rejects too few or too many segments", () => {
    expect(parseBirthSlug("1995-08-15")).toBeNull();
    expect(parseBirthSlug("1995-08-15-10-nam-extra")).toBeNull();
  });
});

describe("encodeBirthSlug", () => {
  it("encodes with male gender", () => {
    expect(encodeBirthSlug({
      birthDatetimeLocal: "1995-08-15T10:30:00",
      gender: "nam",
    })).toBe("1995-08-15-10-nam");
  });

  it("encodes with female gender as 'nu' (URL-safe ASCII)", () => {
    expect(encodeBirthSlug({
      birthDatetimeLocal: "1995-08-15T10:00:00",
      gender: "nữ",
    })).toBe("1995-08-15-10-nu");
  });

  it("encodes without gender", () => {
    expect(encodeBirthSlug({
      birthDatetimeLocal: "1995-08-15T10:00:00",
    })).toBe("1995-08-15-10");
  });

  it("returns null for malformed datetime", () => {
    expect(encodeBirthSlug({ birthDatetimeLocal: "" })).toBeNull();
    expect(encodeBirthSlug({ birthDatetimeLocal: "invalid" })).toBeNull();
    expect(encodeBirthSlug({})).toBeNull();
  });
});

describe("round-trip encode → parse", () => {
  it("preserves all fields for common cases", () => {
    const cases = [
      { birthDatetimeLocal: "1995-08-15T10:00:00", gender: "nam" },
      { birthDatetimeLocal: "2000-01-01T00:00:00", gender: "nữ" },
      { birthDatetimeLocal: "1985-12-31T23:00:00", gender: "nam" },
    ];
    for (const original of cases) {
      const slug = encodeBirthSlug(original);
      const parsed = parseBirthSlug(slug);
      expect(parsed.birthDatetimeLocal).toBe(original.birthDatetimeLocal);
      expect(parsed.gender).toBe(original.gender);
    }
  });
});
