import { sleep } from "k6";
import { submitter } from "./workflows/submitter.js";
import {
  pollPendingRequests,
  queryBatchUserResults,
  queryUserResults,
  queryRequestsList,
} from "./workflows/querier.js";

const BASE_URL = __ENV.TEST_HOST;

export let options = {
  scenarios: {
    submitters: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "1m", target: 5 }, // ramp up to 5 VUs, at ~10s/iteration -> 6 iterations per minute per VU, so 6 * 5 * 1 = 30 iterations (POST + poll GET) in the first minute
        { duration: "2m", target: 40 }, // ramp up to 40 VUs, so 6 * 40 * 2 = 480 iterations in the next 2 minutes
        { duration: "2m", target: 40 }, // stay at 40 VUs, so 6 * 40 * 2 = 480 iterations in the next 2 minutes
        { duration: "1m", target: 2 }, // ramp down to 2 VUs, so 6 * 2 * 1 = 12 iterations in the last minute
      ],
      exec: "submitRequests",
    },
    readers: {
      executor: "ramping-vus",
      startVUs: 0,
      startTime: "1m",
      stages: [
        { duration: "1m", target: 5 },
        { duration: "4m", target: 60 },
        { duration: "4m", target: 60 },
        { duration: "1m", target: 10 },
      ],
      exec: "readResults",
    },
    auditors: {
      executor: "ramping-vus",
      startVUs: 0,
      startTime: "1m",
      stages: [
        { duration: "2m", target: 5 },
        { duration: "4m", target: 15 },
        { duration: "3m", target: 15 },
        { duration: "1m", target: 1 },
      ],
      exec: "auditBatch",
    },
  },
};

export function setup() {
  let customers = [];
  let userIds = [];
  for (let i = 0; i < 20; i++) customers.push(crypto.randomUUID());
  for (let i = 0; i < 70; i++) userIds.push(crypto.randomUUID());
  return {
    customers: customers,
    userIds: userIds,
    tag: "compliance_peak",
    generator: "heavy",
    urgentRatio: 0.3,
  };
}

export function submitRequests(data) {
  submitter(data);
  sleep(10);
}

export function readResults(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;
  let customer =
    data.customers[Math.floor(Math.random() * data.customers.length)];

  queryRequestsList(host, customer);
  sleep(10);
}

export function auditBatch(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;

  // Batch queries across all clients
  queryBatchUserResults(host, data.customers);
  sleep(1);

  // Per-user queries
  let customer =
    data.customers[Math.floor(Math.random() * data.customers.length)];
  for (let i = 0; i < data.customers.length; i++) {
    customer = data.customers[i];
    queryUserResults(host, customer, data.userIds);
    sleep(1);
  }
  sleep(1);
}
