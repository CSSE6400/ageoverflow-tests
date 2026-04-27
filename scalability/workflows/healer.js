import http from "k6/http";
import { check } from "k6";
import { Counter } from "k6/metrics";

import { checkHealth } from "../checks/health.js";

const BASE_URL = __ENV.TEST_HOST;

const errors = new Counter("heal_errors");
const attempted = new Counter("heal_attempted");

export function healer(data) {
    attempted.add(1);

    let host = BASE_URL.endsWith('/') ? BASE_URL.slice(0, -1) : BASE_URL;
    let url = host + '/health';
    let res = http.get(url, {headers: {"Content-Type": "application/json", "Accept": "application/json"}});
    try {
        check(res, checkHealth, { endpoint : "/health" });
    } catch (e) {
        errors.add(1, { endpoint : "/health" });
        return;
    }
}