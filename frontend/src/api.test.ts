import { describe, expect, it } from "vitest";
import { formatDetail } from "./api";

describe("formatDetail", () => {
  it("passes through plain string details", () => {
    expect(formatDetail("Email already registered")).toBe("Email already registered");
  });

  it("explains min-length issues with a friendly field label", () => {
    const detail = [
      {
        type: "string_too_short",
        loc: ["body", "company_name"],
        msg: "String should have at least 2 characters",
        ctx: { min_length: 2 },
      },
    ];
    expect(formatDetail(detail)).toBe("Company must be at least 2 characters");
  });

  it("explains invalid emails", () => {
    const detail = [
      { type: "value_error", loc: ["body", "email"], msg: "value is not a valid email address" },
    ];
    expect(formatDetail(detail)).toBe("Email must be a valid email address (e.g. you@company.com)");
  });

  it("joins multiple issues", () => {
    const detail = [
      { type: "value_error", loc: ["body", "email"], msg: "bad" },
      {
        type: "string_too_short",
        loc: ["body", "password"],
        msg: "short",
        ctx: { min_length: 8 },
      },
    ];
    expect(formatDetail(detail)).toBe(
      "Email must be a valid email address (e.g. you@company.com) · Password must be at least 8 characters",
    );
  });

  it("falls back for empty arrays and unknown shapes", () => {
    expect(formatDetail([])).toBe("Invalid request");
    expect(formatDetail(null)).toBe("Request failed");
    expect(formatDetail({ foo: "bar" })).toBe('{"foo":"bar"}');
  });
});
