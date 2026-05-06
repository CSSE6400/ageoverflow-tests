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
const queryDelay = new Trend("query_delay");
const errors = new Counter("errors");

function timedGet(url, tags) {
  let start = Date.now();
  let res = http.get(url, { headers: { Accept: "application/json" } });
  let elapsed = Date.now() - start;
  queriesTotal.add(1, tags);
  queryDelay.add(elapsed, tags);
  return res;
}

export function queryUsersList(hostUrl, customer) {
  let url = hostUrl + "/analysis/" + customer + "/users";
  let res = timedGet(url, { endpoint: "/users", type: "list" });

  try {
    let success = check(res, checkUserList);
    if (!success) {
      errors.add(1, { endpoint: "/users" });
    }
  } catch (e) {
    errors.add(1, { endpoint: "/users" });
  }
  return res;
}

export function queryUserById(hostUrl, customer, userId) {
  let url = hostUrl + "/analysis/" + customer + "/users/" + userId;
  let res = timedGet(url, { endpoint: "/users", type: "detail" });
  try {
    let success = check(res, checkUser);
    if (!success) {
      errors.add(1, { endpoint: "/users/" + userId });
    }
  } catch (e) {
    errors.add(1, { endpoint: "/users/" + userId });
  }
  return res;
}

export function queryRequestsList(hostUrl, customer, params) {
  let url = hostUrl + "/analysis/" + customer + "/requests";
  let res = timedGet(url, { endpoint: "/requests", type: "list" });
  try {
    let success = check(res, checkAnalysisList);
    if (!success) {
      errors.add(1, { endpoint: "/requests" });
    }
  } catch (e) {
    errors.add(1, { endpoint: "/requests" });
  }
  return res;
}

export function queryRequestById(hostUrl, customer, requestId) {
  let url = hostUrl + "/analysis/" + customer + "/requests/" + requestId;
  let res = timedGet(url, { endpoint: "/requests", type: "detail" });
  try {
    let success = check(res, checkCompletedAnalysis);
    if (!success) {
      errors.add(1, { endpoint: "/requests/" + requestId });
    }
  } catch (e) {
    errors.add(1, { endpoint: "/requests/" + requestId });
  }
  return res;
}

export function queryStats(hostUrl, customer) {
  let url = hostUrl + "/analysis/" + customer + "/statistics";
  let res = timedGet(url, { endpoint: "/statistics", type: "stats" });
  try {
    let success = check(res, checkStats);
    if (!success) {
      errors.add(1, { endpoint: "/statistics" });
    }
  } catch (e) {
    errors.add(1, { endpoint: "/statistics" });
  }
  return res;
}

export function pollPendingRequests(hostUrl, customer) {
  let res = queryRequestsList(hostUrl, customer, { status: "pending" });
  if (res.status === 200 && Array.isArray(res.json())) {
    let pending = res.json();
    for (let i = 0; i < pending.length; i++) {
      queryRequestById(hostUrl, customer, pending[i].id);
      sleep(0.5);
    }
  }
}

export function queryBatchUserResults(hostUrl, customers) {
  for (let i = 0; i < customers.length; i++) {
    let customer = customers[i];
    queryUsersList(hostUrl, customer);

    sleep(0.5);

    pollPendingRequests(hostUrl, customer);

    sleep(0.5);
  }
}

export function queryUserResults(hostUrl, customer, userIds) {
  for (let i = 0; i < userIds.length; i++) {
    let userId = userIds[i];
    queryUserById(hostUrl, customer, userId);
    sleep(0.5);
  }
}
