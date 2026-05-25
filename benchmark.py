import timeit

setup_code = """
input_str = '   \\n \\t  {"test": 123}'
chars = ['{', '[', '"']
"""

test_code_old = """
indices = [input_str.find(char) for char in chars if input_str.find(char) != -1]
min(indices) if indices else 0
"""

test_code_new = """
indices = [idx for char in chars if (idx := input_str.find(char)) != -1]
min(indices) if indices else 0
"""

print("Old:", timeit.timeit(test_code_old, setup=setup_code, number=1000000))
print("New:", timeit.timeit(test_code_new, setup=setup_code, number=1000000))
