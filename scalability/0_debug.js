import { sleep } from "k6";
import { submitter } from "./workflows/submitter.js";
import {
  queryRequestsList,
  queryUsersList,
  queryStats,
} from "./workflows/querier.js";

const BASE_URL = __ENV.TEST_HOST;

export let options = {
  scenarios: {
    smoke: {
      executor: "per-vu-iterations",
      vus: 2,
      iterations: 2,
      maxDuration: "60s",
    },
  },
  thresholds: {
    errors: ["count<1"],
  },
};

export function setup() {
  let customer = crypto.randomUUID();
  let userIds = [crypto.randomUUID(), crypto.randomUUID(), crypto.randomUUID()];
  return {
    customers: [customer],
    userIds: userIds,
    tag: "debug",
    generator: "quick",
    urgentRatio: 0.0,
  };
}

export default function (data) {
  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;

  submitter(data, 30);
  sleep(1);

  queryRequestsList(host, data.customers[0]);
  queryUsersList(host, data.customers[0]);
  queryStats(host, data.customers[0]);
}
