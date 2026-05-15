import { sleep } from "k6";
import { submitter } from "./workflows/submitter.js";
import {
  queryRequestsList,
  queryStats,
  queryRequestById,
} from "./workflows/querier.js";

const BASE_URL = __ENV.TEST_HOST;

export let options = {
  scenarios: {
    normal_submitters: {
      executor: "constant-vus",
      vus: 10,
      duration: "5m",
      exec: "submitRequests",
    },
    researcher: {
      executor: "constant-vus",
      vus: 4,
      startTime: "1m",
      duration: "5m",
      exec: "researchScan",
    },
  },
};

export function setup() {
  let customers = [];
  let userIds = [];
  for (let i = 0; i < 15; i++) customers.push(crypto.randomUUID());
  for (let i = 0; i < 100; i++) userIds.push(crypto.randomUUID());
  return {
    customers: customers,
    userIds: userIds,
    tag: "research",
    generator: "normal",
    urgentRatio: 0.05,
  };
}

export function submitRequests(data) {
  submitter(data);
  sleep(5);
}

export function researchScan(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;

  for (let i = 0; i < data.customers.length; i++) {
    let customer = data.customers[i];

    // Get all requests for this customer
    let res = queryRequestsList(host, customer);
    sleep(1);

    // Get stats
    queryStats(host, customer);
    sleep(1);

    // Query each request result for this customer
    if (res.items) {
      for (let j = 0; j < res.items.length; j++) {
        queryRequestById(host, customer, res.items[j].id);
        sleep(0.5);
      }
    }

    sleep(1);
  }
  sleep(5);
}
