import { sleep } from "k6";
import { healer } from "./workflows/healer.js";

export const options = {
    scenarios: {
        generic: {
            executor: "ramping-vus",
            stages: [
                { duration: "1m", target: 10 },
            ],
            exec: 'generalSubmitter',
        },
    },
    tags: {
        scenario: "0_debug",
    },
    minIterationDuration: '10s'
};

export function setup() {
    return {};
}

export const MAX_ITERATIONS = 2;

export function generalSubmitter(data) {
    if (__ITER >= MAX_ITERATIONS) {
        return;
    }

    healer(data);
    sleep(10);
}