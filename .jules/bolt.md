## 2025-06-03 - Nested MagicMock Requires Full Paths
**Learning:** When testing scripts in isolation and mocking missing dependencies with `sys.modules['module'] = MagicMock()`, if the codebase imports from deeply nested submodules (like `litellm.types.utils`), mocking just the top-level `litellm` package is insufficient and raises a `ModuleNotFoundError: No module named 'litellm.types'; 'litellm' is not a package` error.
**Action:** When creating scratchpad tests that use `sys.modules` mocks, ensure you mock every part of the nested import path required by the test environment.
