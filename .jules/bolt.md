# Bolt Journal

## 2024-05-25 - [Setup]
**Learning:** Initializing journal.
**Action:** Ready to measure and optimize.
## 2024-10-20 - [Blocking Async Calls]
 **Learning:** In async API handlers inheriting from helpers.api.ApiHandler, using synchronous blocking operations like `time.sleep()` halts the entire asyncio event loop, causing severe performance degradation.
 **Action:** Always replace synchronous `time.sleep()` with `await asyncio.sleep()` inside async methods to ensure concurrent execution paths are not blocked.
