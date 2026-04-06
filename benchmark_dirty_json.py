import timeit
from helpers.dirty_json import DirtyJson
import json

test_json = '{"name": "bolt", "features": ["speed", "accuracy"], "active": true, "score": 99.9}'

def run_benchmark():
    # Use standard DirtyJson.parse_string (which now includes the optimization)
    optimized_time = timeit.timeit(lambda: DirtyJson.parse_string(test_json), number=10000)

    # Simulate old behavior by creating parser instance directly
    def old_behavior():
        parser = DirtyJson()
        return parser.parse(test_json)

    old_time = timeit.timeit(old_behavior, number=10000)

    print(f"Old approach time (10,000 runs): {old_time:.4f}s")
    print(f"Optimized approach time (10,000 runs): {optimized_time:.4f}s")
    if old_time > 0:
        print(f"Improvement: {old_time / optimized_time:.2f}x faster")

if __name__ == "__main__":
    run_benchmark()
