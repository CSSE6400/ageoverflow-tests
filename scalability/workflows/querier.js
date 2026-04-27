import http from "k6/http";
import { check, sleep } from "k6";
import { Counter, Trend } from "k6/metrics";

import {
  checkUserList,
  checkUser,
  checkAnalysisList,
  checkStats,
  checkCompletedAnalysis,
} from "../checks/analysis.js";

const queriesTotal = new Counter("queries_total");
const queryLatency = new Trend("query_latency");
const errors = new Counter("errors");

function timedGet(url, tags) {
  let start = Date.now();
  let res = http.get(url, { headers: { Accept: "application/json" } });
  let elapsed = Date.now() - start;
  queriesTotal.add(1, tags);
  queryLatency.add(elapsed, tags);
  return res;
}

export function queryUsersList(hostUrl, customer) {
  let url = hostUrl + "/analysis/" + customer + "/users";
  let res = timedGet(url, { endpoint: "/users", type: "list" });
  check(res, checkUserList);
  return res;
}

export function queryRequestsList(hostUrl, customer, params) {
  let url = hostUrl + "/analysis/" + customer + "/requests";
  let res = timedGet(url, { endpoint: "/requests", type: "list" });
  check(res, checkAnalysisList);
  return res;
}

export function queryStats(hostUrl, customer) {
  let url = hostUrl + "/analysis/" + customer + "/statistics";
  let res = timedGet(url, { endpoint: "/statistics", type: "stats" });
  check(res, checkStats);
  return res;
}

export function queryBatchUserResults(hostUrl, customers) {
  for (let i = 0; i < customers.length; i++) {
    let customer = customers[i];
    queryUsersList(hostUrl, customer);
    queryRequestsList(hostUrl, customer);
    sleep(0.5);
  }
}
