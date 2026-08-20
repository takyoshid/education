import test from "node:test";
import assert from "node:assert/strict";
import { initialState, normalizeQuery, reduceSearch } from "./search-state.js";

test("query is trimmed and internal whitespace is normalized", () => {
  assert.equal(normalizeQuery("  reliable   systems  "), "reliable systems");
});

test("start enters loading without stale items", () => {
  const state = reduceSearch({ ...initialState(), items: ["old"] }, { type: "START", query: "new", requestId: 2 });
  assert.deepEqual(state, { status: "loading", query: "new", items: [], message: "", requestId: 2 });
});

test("empty result has a distinct state", () => {
  const loading = reduceSearch(initialState(), { type: "START", query: "none", requestId: 1 });
  assert.equal(reduceSearch(loading, { type: "RESOLVE", items: [], requestId: 1 }).status, "empty");
});

test("stale response cannot overwrite newer request", () => {
  let state = reduceSearch(initialState(), { type: "START", query: "first", requestId: 1 });
  state = reduceSearch(state, { type: "START", query: "second", requestId: 2 });
  const stale = reduceSearch(state, { type: "RESOLVE", items: ["wrong"], requestId: 1 });
  assert.equal(stale, state);
});

test("failure removes technical details from user message", () => {
  const loading = reduceSearch(initialState(), { type: "START", query: "x", requestId: 1 });
  const failed = reduceSearch(loading, { type: "REJECT", requestId: 1 });
  assert.equal(failed.status, "error");
  assert.ok(failed.message.length > 0);
});
