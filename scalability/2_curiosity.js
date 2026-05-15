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
        // generate ~60k requests in the 2-minute sustained burst (500 req/s × 120s)
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
    userIds: userIds,
    tag: "curiosity",
    generator: "normal",
    urgentRatio: 0.05,
  };
}

export function submitRequests(data) {
  submitter(data);
  sleep(5);
}

export function auditorRead(data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;
  let customer = data.customers[0];

  // Query list of users for the customer
  let res = queryUsersList(host, customer);
  sleep(1);

  // Query a random user discovered from the list endpoint
  if (res.users && res.users.length > 0) {
    let user = res.users[Math.floor(Math.random() * res.users.length)];
    queryUserById(host, customer, user.id);
  }
  sleep(1);
}
