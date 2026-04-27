import _ from "https://cdn.jsdelivr.net/npm/lodash@4.17.11/lodash.min.js";

export const checkAnalysis = {
  "POST returns 201": (r) => r.status === 201,
  "Response is JSON": (r) =>
    r.headers["Content-Type"].includes("application/json"),
  "Response is an object": (r) => _.isObject(r.json()),
  "has id": (r) => _.has(r.json(), "id"),
  "has updated_at": (r) => _.has(r.json(), "updated_at"),
  "has valid status": (r) =>
    ["pending", "success", "failed"].includes(r.json().status),
};

export const checkCompletedAnalysis = {
  "GET returns 200": (r) => r.status === 200,
  "status is not pending": (r) =>
    _.has(r.json(), "status") && r.json().status !== "pending",
  "has result.checksum": (r) =>
    _.has(r.json(), "result") && _.has(r.json().result, "checksum"),
  "has result.primary_generation": (r) =>
    _.has(r.json(), "result") && _.has(r.json().result, "primary_generation"),
  "has result.age": (r) =>
    _.has(r.json(), "result") && _.has(r.json().result, "age"),
  "has generations.alpha": (r) =>
    _.has(r.json(), "result") &&
    _.has(r.json().result, "generations") &&
    _.has(r.json().result.generations, "alpha"),
};

export const checkUserList = {
  "GET returns 200": (r) => r.status === 200,
  "is array": (r) => Array.isArray(r.json()),
};

export const checkUser = {
  "GET returns 200": (r) => r.status === 200,
  "has id": (r) => _.has(r.json(), "id"),
  "has results": (r) => Array.isArray(r.json().results),
};

export const checkAnalysisList = {
  "GET returns 200": (r) => r.status === 200,
  "is array": (r) => Array.isArray(r.json()),
};

export const checkStats = {
  "GET returns 200": (r) => r.status === 200,
  "has contents": (r) => _.has(r.json(), "contents"),
  "has total_requests": (r) => _.has(r.json().contents, "total_requests"),
  "has mean": (r) => _.has(r.json().contents, "mean"),
  "has buckets": (r) => _.has(r.json().contents, "buckets"),
};
