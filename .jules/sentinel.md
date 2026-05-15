## 2024-05-15 - XSS in Modal Loading
**Vulnerability:** XSS vulnerability in modal content loading where `error.message` and `modalPath` were injected into the DOM using `innerHTML`.
**Learning:** Error messages from failed component imports can be manipulated to inject malicious scripts, and `modalPath` is user-controllable.
**Prevention:** Always use `textContent` instead of `innerHTML` when inserting dynamic data, especially error messages or paths, into the DOM to prevent XSS vulnerabilities.
