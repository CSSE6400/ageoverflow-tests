import { sleep } from "k6";
import { submitter } from "./workflows/submitter.js";
import { queryBatchUserResults, queryStats } from "./workflows/querier.js";

const BASE_URL = __ENV.TEST_HOST;

export let options = {
  scenarios: {
    normal_submitters: {
      executor: "constant-vus",
      vus: 10,
      duration: "10m",
      exec: "submitNormal",
    },
    spike_submitters: {
      executor: "ramping-arrival-rate",
      startRate: 5,
      timeUnit: "1m",
      preAllocatedVUs: 3,
      maxVUS: 20,
      stages: [
        { duration: "2m", target: 10 },
        { duration: "3m", target: 40 },
        { duration: "3m", target: 40 },
        { duration: "2m", target: 10 },
      ],
      exec: "submitSpike",
    },
    eager_readers: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "2m", target: 5 },
        { duration: "3m", target: 30 },
        { duration: "3m", target: 30 },
        { duration: "2m", target: 5 },
      ],
      exec: "eagerRead",
    },
  },
};

export function setup() {
  let normalCustomers = [];
  let spikeCustomers = [];
  let userIds = [];
  for (let i = 0; i < 15; i++) normalCustomers.push(crypto.randomUUID());
  for (let i = 0; i < 4; i++) spikeCustomers.push(crypto.randomUUID());
  for (let i = 0; i < 200; i++) userIds.push(crypto.randomUUID());
  return {
    customers: normalCustomers.concat(spikeCustomers),
    normalCustomers: normalCustomers,
    spikeCustomers: spikeCustomers,
    userIds: userIds,
    tag: "compliance_early",
    generator: "normal",
    urgentRatio: 0.05,
    photoComplexity: 4,
  };
}

export function submitNormal(data) {
  let normalData = Object.assign({}, data, {
    customers: data.normalCustomers,
    tag: "compliance_early_normal",
    generator: "normal",
    urgentRatio: 0.05,
  });
  submitter(normalData);
  sleep(5);
}

export function submitSpike(data) {
  let spikeData = Object.assign({}, data, {
    customers: data.spikeCustomers,
    tag: "compliance_early_spike",
    generator: "heavy",
    urgentRatio: 0.8,
  });
  submitter(spikeData);
  sleep(15);
}

export function eagerRead(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;
  let customer =
    data.customers[Math.floor(Math.random() * data.customers.length)];

  // Auditor batch queries for users
  if (Math.random() < 0.3) {
    queryBatchUserResults(host, data.customers.slice(0, 5));
  }
  sleep(5);

  // Auditor batch queries from customers
  if (Math.random() < 0.3) {
    queryStats(host, customer);
  }
  sleep(5);
}
