import { describe, expect, it } from "vitest";
import { FOCUS_ROUTES, resolveFocusDestination } from "./focusRouting";

describe("resolveFocusDestination", () => {
  it("routes a direct category match to its configured destination", () => {
    expect(resolveFocusDestination("Thesis", "Deep work: literature review")).toBe("/research");
    expect(resolveFocusDestination("English", "Vocabulary review")).toBe("/vocabulary");
    expect(resolveFocusDestination("Reading", "Read 20 pages")).toBe("/reading");
  });

  it("routes InterviewPrep to DSA when the activity text names a DSA topic", () => {
    expect(resolveFocusDestination("InterviewPrep", "LeetCode: Two Sum")).toBe("/problems");
    expect(resolveFocusDestination("InterviewPrep", "Practice: sliding window patterns")).toBe(
      "/problems"
    );
    expect(resolveFocusDestination("InterviewPrep", "Binary search drills")).toBe("/problems");
  });

  it("falls back InterviewPrep to AI & ML when nothing DSA-specific matches", () => {
    expect(resolveFocusDestination("InterviewPrep", "ML System Design Review")).toBe("/concepts");
    expect(resolveFocusDestination("InterviewPrep", "Theory: Transformers")).toBe("/concepts");
  });

  it("is case-insensitive when matching activity markers", () => {
    expect(resolveFocusDestination("InterviewPrep", "LEETCODE session")).toBe("/problems");
  });

  it("returns null for a category with no configured route, rather than throwing", () => {
    expect(resolveFocusDestination("Prayer", "Maghrib")).toBeNull();
    expect(resolveFocusDestination("Recovery", "Nap")).toBeNull();
    expect(resolveFocusDestination("SomeUnknownCategory", "whatever")).toBeNull();
  });

  it("every route destination is a root-relative path", () => {
    for (const route of FOCUS_ROUTES) {
      expect(route.destination.startsWith("/")).toBe(true);
    }
  });
});
