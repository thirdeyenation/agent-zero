## 2024-05-24 - simpleeval Sandbox Escape (CVE-2026-32640)
**Vulnerability:** The `simpleeval` package used in the project allowed arbitrary function execution resulting in potential sandbox escapes or remote code injection during the evaluation of user inputs and template conditions.
**Learning:** Using `simple_eval()` without explicitly disabling `functions` allowed unintended function executions.
**Prevention:** Update `simpleeval` dependency to version >=1.0.5 and always use `SimpleEval(names=..., functions={}).eval(...)` to prevent code execution when only evaluating variables.