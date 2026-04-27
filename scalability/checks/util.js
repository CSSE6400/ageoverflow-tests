import { check } from "k6";

export function ignoreCheck(response, checkFn) {
  try {
    return check(response, checkFn);
  } catch (e) {
    return false;
  }
}
