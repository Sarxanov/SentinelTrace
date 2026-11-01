import { describe, expect, it } from "vitest";

function pageCount(total: number, pageSize: number) {
  return Math.max(1, Math.ceil(total / pageSize));
}

describe("events explorer pagination", () => {
  it("calculates a stable page count for empty and populated results", () => {
    expect(pageCount(0, 20)).toBe(1);
    expect(pageCount(41, 20)).toBe(3);
  });
});
