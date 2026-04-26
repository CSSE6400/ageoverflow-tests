export function ignoreCheck(obj, checks, tags) {
    for (let i = 0; i < checks.length; i++) {
        const check = checks[i];
        if (!check(obj)) {
            return false;
        }
    }
    return true;
}