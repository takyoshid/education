export function initialState() {
  return { status: "idle", query: "", items: [], message: "" };
}

export function reduceSearch(state, event) {
  // START, RESOLVE, REJECT, RESETを扱う。event.requestIdより古い結果を無視すること。
  throw new Error("Not implemented");
}

export function normalizeQuery(value) {
  throw new Error("Not implemented");
}
