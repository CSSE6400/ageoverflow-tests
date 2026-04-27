import { sleep } from "k6";
import { submitter } from "./workflows/submitter.js";
import { queryRequestsList, queryStats } from "./workflows/querier.js";

const BASE_URL = __ENV.TEST_HOST;

export let options = {
  scenarios: {
    submitters: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "2m", target: 5 },
        { duration: "3m", target: 20 },
        { duration: "3m", target: 20 },
        { duration: "2m", target: 5 },
      ],
      exec: "submitRequests",
    },
    readers: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "2m", target: 3 },
        { duration: "3m", target: 10 },
        { duration: "3m", target: 10 },
        { duration: "2m", target: 3 },
      ],
      exec: "readResults",
    },
  },
};

export function setup() {
  let customers = [];
  let userIds = [];
  for (let i = 0; i < 10; i++) customers.push(crypto.randomUUID());
  for (let i = 0; i < 50; i++) userIds.push(crypto.randomUUID());
  return {
    customers: customers,
    userIds: userIds,
    tag: "normal",
    generator: "normal",
    urgentRatio: 0.05,
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
