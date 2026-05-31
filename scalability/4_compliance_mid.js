import { sleep } from "k6";
import { submitter } from "./workflows/submitter.js";
import {
  queryRequestsList,
  queryStats,
  queryBatchUserResults,
} from "./workflows/querier.js";

const BASE_URL = __ENV.TEST_HOST;

export let options = {
  scenarios: {
    submitters: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "2m", target: 5 }, // ramp up to 5 VUs, at ~10s/iteration -> 6 iterations per minute per VU, so 6 * 5 * 2 = 60 iterations (POST + poll GET) in the first 2 minute
        { duration: "3m", target: 50 }, // ramp up to 50 VUs, so 6 * 50 * 3 = 900 iterations in the next 3 minutes
        { duration: "2m", target: 10 }, // ramp down to 10 VUs, so 6 * 10 * 2 = 120 iterations in the next 2 minutes
        { duration: "3m", target: 2 }, // ramp down to 2 VUs, so 6 * 2 * 3 = 36 iterations in the last 3 minutes
      ],
      exec: "submitRequests",
    },
    readers: {
      executor: "ramping-vus",
      startVUs: 0,
      startTime: "1m",
      stages: [
        { duration: "2m", target: 3 },
        { duration: "3m", target: 15 },
        { duration: "2m", target: 15 },
        { duration: "3m", target: 3 },
      ],
      exec: "readResults",
    },
    auditors: {
      executor: "constant-vus",
      startTime: "1m",
      vus: 5,
      duration: "10m",
      exec: "auditBatch",
    },
  },
};

export function setup() {
  let customers = [];
  let userIds = [];
  for (let i = 0; i < 15; i++) customers.push(crypto.randomUUID());
  for (let i = 0; i < 60; i++) userIds.push(crypto.randomUUID());
  return {
    customers: customers,
    userIds: userIds,
    tag: "compliance_mid",
    generator: "normal",
    urgentRatio: 0.15,
  };
}

export function submitRequests(data) {
  submitter(data);
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

export function auditBatch(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;
  let batch = data.customers.slice(0, 5);
  queryBatchUserResults(host, batch);
  sleep(5);
}
