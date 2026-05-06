import { sleep } from "k6";
import exec from "k6/execution";
import { submitter } from "./workflows/submitter.js";
import { queryUsersList, queryUserById } from "./workflows/querier.js";

const BASE_URL = __ENV.TEST_HOST;

export let options = {
  scenarios: {
    submitters: {
      executor: "constant-vus",
      vus: 10,
      duration: "2m",
      exec: "submitRequests",
    },
    auditors: {
      executor: "ramping-arrival-rate",
      startTime: "2m",
      startRate: 100,
      timeUnit: "1s",
      preAllocatedVUs: 200,
      maxVUs: 500,
      stages: [
        //  generate ~60k requests in the 2-minute sustained burst (500 req/s × 120s)
        { duration: "30s", target: 500 }, // ramp to 500 req/s
        { duration: "2m", target: 500 }, // sustain ~60k requests
        { duration: "30s", target: 10 }, // cool down
      ],
      exec: "auditorRead",
    },
  },
};

export function setup() {
  let customers = [];
  let userIds = [];
  for (let i = 0; i < 5; i++) customers.push(crypto.randomUUID());
  for (let i = 0; i < 50; i++) userIds.push(crypto.randomUUID());
  return {
    customers: customers,
    portalCustomer: customers[0],
    userIds: userIds,
    tag: "curiosity",
    generator: "normal",
    urgentRatio: 0.05,
  };
}

export function submitRequests(data) {
  // Propagate all user IDs to ensure each has data before auditor starts
  // Use modulo to loop back to the start if iterations exceed data length
  let idx = exec.scenario.iterationInTest % data.userIds.length;
  let scoped = Object.assign({}, data, {
    customers: [data.portalCustomer],
    userIds: [data.userIds[idx]],
  });
  submitter(scoped);
  sleep(5);
}

export function auditorRead(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;
  let customer = data.portalCustomer;

  // Query list of users for the customer
  queryUsersList(host, customer);
  sleep(1);

  // Query individual user results
  let userId = data.userIds[Math.floor(Math.random() * data.userIds.length)];
  queryUserById(host, customer, userId);
  sleep(1);
}
