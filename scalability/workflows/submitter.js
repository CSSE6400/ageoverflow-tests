import http from "k6/http";
import { check, sleep } from "k6";
import { Counter, Trend } from "k6/metrics";
import { checkAnalysis, checkCompletedAnalysis } from "../checks/analysis.js";
import { ignoreCheck } from "../checks/util.js";
import { getPhotos } from "../data/photo.js";

const BASE_URL = __ENV.TEST_HOST;

const errors = new Counter("errors");
const jobCreated = new Counter("jobs_created");
const analysesAttempted = new Counter("analyses_attempted");
const analysesCompleted = new Counter("analyses_completed");
const analysesCorrect = new Counter("analyses_correct");
const completionDelay = new Trend("completion_delay");

export function submitter(data, timeout = 60) {
  const startTime = Date.now();
  analysesAttempted.add(1, { tag: data.tag });

  let host = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;
  let customer =
    data.customers[Math.floor(Math.random() * data.customers.length)];
  let userId = data.userIds[Math.floor(Math.random() * data.userIds.length)];

  let url = host + "/analysis/" + customer + "/requests";

  // Submit a new analysis POST request
  let photoData = getPhotos(data.generator || "normal");
  let urgent = Math.random() < (data.urgentRatio || 0.05);

  let payload = JSON.stringify({
    user_id: userId,
    photos: photoData.payloads,
    urgent: urgent,
  });

  let res = http.post(url, payload, {
    headers: { "Content-Type": "application/json", Accept: "application/json" },
  });

  // Check if the request was accepted and extract the request ID
  try {
    let success = check(res, checkAnalysis, { endpoint: "/analyses" });
    if (success) {
      jobCreated.add(1, { endpoint: "/analyses", tag: data.tag });
    } else {
      errors.add(1, { endpoint: "/analyses", tag: data.tag });
      return;
    }
  } catch (e) {
    console.log(e.message);
    errors.add(1, { endpoint: "/analyses", tag: data.tag });
    return;
  }

  let requestId = res.json().id;

  // Wait for expected processing time before polling
  let initialWait = photoData.expectedDelay || 5;
  sleep(initialWait);
  timeout -= initialWait;

  // Check if completed
  while (timeout > 0) {
    let analysis = http.get(url + "/" + requestId, {
      headers: { Accept: "application/json" },
    });

    let completed = ignoreCheck(analysis, checkCompletedAnalysis);
    if (completed && analysis.json().status !== "pending") {
      let endTime = Date.now();
      let timeDifference = (endTime - startTime) / 1000;
      analysesCompleted.add(1, { tag: data.tag });
      completionDelay.add(timeDifference, { tag: data.tag });

      if (
        analysis.json().result &&
        analysis.json().result.checksum === photoData.checksum
      ) {
        analysesCorrect.add(1, { tag: data.tag });
      }
      return;
    }

    timeout -= 5;
    sleep(5);
  }
}
