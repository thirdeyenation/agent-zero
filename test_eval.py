from simpleeval import SimpleEval
from collections import defaultdict
data = {"a": 1}
safe_data = defaultdict(lambda: None, data)
res1 = SimpleEval(names=safe_data, functions={"str": str, "int": int, "float": float, "bool": bool, "len": len}).eval("not b if b is not None else True")
print("res1", res1)
res2 = SimpleEval(names=safe_data, functions={"str": str, "int": int, "float": float, "bool": bool, "len": len}).eval("not a if a is not None else True")
print("res2", res2)
