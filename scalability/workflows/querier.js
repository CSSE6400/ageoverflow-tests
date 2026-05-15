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

function timedGet(url, tags, params) {
  if (params) {
    let query = Object.entries(params)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join("&");
    url = url + "?" + query;
  }
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

  let users = null;
  try {
    let success = check(res, checkUserList);
    if (success) {
      users = res.json();
    } else {
      errors.add(1, { endpoint: "/users" });
    }
  } catch (e) {
    errors.add(1, { endpoint: "/users" });
  }
  return { res: res, users: users };
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
  let res = timedGet(url, { endpoint: "/requests", type: "list" }, params);
  let items = null;
  try {
    let success = check(res, checkAnalysisList);
    if (success) {
      items = res.json();
    } else {
      errors.add(1, { endpoint: "/requests" });
    }
  } catch (e) {
    errors.add(1, { endpoint: "/requests" });
  }
  return { res: res, items: items };
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
  let result = queryRequestsList(hostUrl, customer, { status: "pending" });
  if (result.items) {
    for (let i = 0; i < result.items.length; i++) {
      queryRequestById(hostUrl, customer, result.items[i].id);
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

export function queryUserResults(hostUrl, customer, maxUsers) {
  let res = queryUsersList(hostUrl, customer);
  let users = res.users;
  if (!users) {
    return;
  }
  let limit = maxUsers || users.length;
  for (let i = 0; i < Math.min(users.length, limit); i++) {
    queryUserById(hostUrl, customer, users[i].id);
    sleep(0.5);
  }
}
