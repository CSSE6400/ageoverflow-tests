import { sleep } from "k6";
import { submitter } from "./workflows/submitter.js";
import {
  queryRequestsList,
  queryStats,
  queryBatchUserResults,
  queryUserResults,
} from "./workflows/querier.js";
import { randomIntBetween } from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

const BASE_URL = __ENV.TEST_HOST;

export let options = {
  scenarios: {
    normal_submitters: {
      executor: "constant-vus",
      vus: 10,
      duration: "10m",
      exec: "submitNormal",
    },
    backlog_submitters: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "2m", target: 5 },
        { duration: "3m", target: 25 },
        { duration: "3m", target: 25 },
        { duration: "2m", target: 5 },
      ],
      exec: "submitBacklog",
    },
    moderate_readers: {
      executor: "constant-vus",
      vus: 10,
      startTime: "1m",
      duration: "10m",
      exec: "readResults",
    },
    heavy_auditors: {
      executor: "ramping-vus",
      startVUs: 0,
      startTime: "1m",
      stages: [
        { duration: "2m", target: 5 },
        { duration: "3m", target: 25 },
        { duration: "3m", target: 25 },
        { duration: "2m", target: 5 },
      ],
      exec: "heavyAudit",
    },
  },
};

export function setup() {
  let normalCustomers = [];
  let backlogCustomers = [];
  let userIds = [];
  for (let i = 0; i < 16; i++) normalCustomers.push(crypto.randomUUID());
  for (let i = 0; i < 4; i++) backlogCustomers.push(crypto.randomUUID());
  for (let i = 0; i < 100; i++) userIds.push(crypto.randomUUID());
  return {
    customers: normalCustomers.concat(backlogCustomers),
    normalCustomers: normalCustomers,
    backlogCustomers: backlogCustomers,
    userIds: userIds,
    tag: "auditing_bau",
    generator: "normal",
    urgentRatio: 0.02,
  };
}

export function submitNormal(data) {
  let normalData = Object.assign({}, data, {
    customers: data.normalCustomers,
    tag: "auditing_bau_normal",
    generator: "normal",
    urgentRatio: 0.02,
  });
  submitter(normalData);
  sleep(5);
}

export function submitBacklog(data) {
  let backlogData = Object.assign({}, data, {
    customers: data.backlogCustomers,
    tag: "auditing_bau_backlog",
    generator: "heavy",
    urgentRatio: 0.05,
  });
  submitter(backlogData);
  sleep(5);
}

export function readResults(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;
  let customer =
    data.customers[Math.floor(Math.random() * data.customers.length)];

  queryRequestsList(host, customer);
  sleep(1);
  queryStats(host, customer);
  sleep(5);
}

export function heavyAudit(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;

  // Large batch queries across all clients
  let batchSize = randomIntBetween(8, data.customers.length);
  let startIdx = Math.floor(
    Math.random() * Math.max(1, data.customers.length - batchSize),
  );
  let batch = data.customers.slice(startIdx, startIdx + batchSize);
  queryBatchUserResults(host, batch);
  sleep(1);

  // Large per-user queries
  let customer =
    data.customers[Math.floor(Math.random() * data.customers.length)];
  let userBatch = data.userIds.slice(
    0,
    randomIntBetween(5, data.userIds.length),
  );
  queryUserResults(host, customer, userBatch);
  sleep(5);
}
