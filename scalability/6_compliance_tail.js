import { sleep } from "k6";
import { submitter } from "./workflows/submitter.js";
import {
  pollPendingRequests,
  queryBatchUserResults,
  queryUserResults,
} from "./workflows/querier.js";
import { randomIntBetween } from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

const BASE_URL = __ENV.TEST_HOST;

export let options = {
  scenarios: {
    submitters: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "2m", target: 10 },
        { duration: "2m", target: 40 },
        { duration: "2m", target: 20 },
        { duration: "2m", target: 35 },
        { duration: "2m", target: 5 },
      ],
      exec: "submitRequests",
    },
    readers: {
      executor: "constant-vus",
      vus: 20,
      startTime: "1m",
      duration: "10m",
      exec: "readResults",
    },
    auditors: {
      executor: "constant-vus",
      vus: 8,
      startTime: "1m",
      duration: "10m",
      exec: "auditBatch",
    },
  },
};

export function setup() {
  let customers = [];
  let userIds = [];
  for (let i = 0; i < 20; i++) customers.push(crypto.randomUUID());
  for (let i = 0; i < 80; i++) userIds.push(crypto.randomUUID());
  return {
    customers: customers,
    userIds: userIds,
    tag: "compliance_tail",
    generator: "heavy",
    urgentRatio: 0.1,
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

  pollPendingRequests(host, customer);
  sleep(5);
}

export function auditBatch(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;

  // Moderate batch queries
  let batchSize = randomIntBetween(4, data.customers.length);
  let startIdx = Math.floor(
    Math.random() * (data.customers.length - batchSize),
  );
  let batch = data.customers.slice(startIdx, startIdx + batchSize);
  queryBatchUserResults(host, batch);
  sleep(1);

  // Per-user queries (moderate)
  let customer =
    data.customers[Math.floor(Math.random() * data.customers.length)];
  let userBatch = data.userIds.slice(
    0,
    randomIntBetween(3, data.userIds.length),
  );
  queryUserResults(host, customer, userBatch);
  sleep(5);
}
