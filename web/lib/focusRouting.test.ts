import { describe, expect, it } from "vitest";
import { FOCUS_ROUTES, resolveFocusDestination } from "./focusRouting";

describe("resolveFocusDestination", () => {
  it("routes a direct category match to its configured destination", () => {
    expect(resolveFocusDestination("Thesis", "Deep work: literature review")).toBe("/research");
    expect(resolveFocusDestination("English", "Vocabulary review")).toBe("/vocabulary");
    expect(resolveFocusDestination("Reading", "Read 20 pages")).toBe("/reading");
  });

  it("routes every real Thesis-track activity string to Thesis & Research", () => {
    // The real schedule's full Thesis-category set -- every wording of a
    // deep-research/writing/admin session, all of which belong on the
    // same page regardless of the specific wording.
    expect(
      resolveFocusDestination("Thesis", "Thesis — deep research / literature review — block 1")
    ).toBe("/research");
    expect(resolveFocusDestination("Thesis", "Thesis — implementation / experiments")).toBe(
      "/research"
    );
    expect(resolveFocusDestination("Thesis", "Buffer / thesis admin catch-up")).toBe("/research");
    expect(resolveFocusDestination("Thesis", "Thesis weekly review")).toBe("/research");
  });

  it("routes English Vocabulary but not English Grammar (no grammar page exists yet)", () => {
    expect(resolveFocusDestination("English", "📚 English Vocabulary")).toBe("/vocabulary");
    expect(resolveFocusDestination("English", "📚 English Grammar Learning")).toBeNull();
  });

  it("routes the real Reading activity string to the Reading Log", () => {
    expect(resolveFocusDestination("Reading", "📖 Reading")).toBe("/reading");
  });

  it("leaves the standalone Buffer category unmapped (not the same as Thesis's admin buffer)", () => {
    expect(resolveFocusDestination("Buffer", "Buffer / errands")).toBeNull();
    expect(resolveFocusDestination("Buffer", "Weekly review")).toBeNull();
  });

  it("routes every real Coding-track activity string to DSA Prep", () => {
    // The exact set scripts/restructure_workday.py and the live schedule
    // produce -- see lib/focusRouting.ts's comment for why keyword
    // matching on DSA topics (sliding window, graph, ...) doesn't work:
    // none of these strings contain any such keyword.
    expect(resolveFocusDestination("InterviewPrep", "💻 Interview Prep — Coding")).toBe("/problems");
    expect(resolveFocusDestination("InterviewPrep", "💻 Interview Prep — Coding (part 1)")).toBe(
      "/problems"
    );
    expect(
      resolveFocusDestination("InterviewPrep", "💻 Interview Prep — Timed Mock + Weak-Pattern Review")
    ).toBe("/problems");
  });

  it("routes every real Theory-track activity string to AI & ML", () => {
    expect(resolveFocusDestination("InterviewPrep", "💻 Interview Prep — Theory")).toBe("/concepts");
    expect(resolveFocusDestination("InterviewPrep", "💻 Interview Prep — Theory (part 2)")).toBe(
      "/concepts"
    );
    expect(
      resolveFocusDestination("InterviewPrep", "💻 Interview Prep — Theory: ML System Design")
    ).toBe("/concepts");
    expect(
      resolveFocusDestination(
        "InterviewPrep",
        "💻 Interview Prep — Theory: ML Coding from scratch (numpy)"
      )
    ).toBe("/concepts");
  });

  it("is case-insensitive when matching activity markers", () => {
    expect(resolveFocusDestination("InterviewPrep", "THEORY session")).toBe("/concepts");
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
