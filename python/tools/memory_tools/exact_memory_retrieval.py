import json

def exact_memory_retrieval(memory_id):
    try:
        from a0.memory_tool import memory_load
        result = memory_load(query=memory_id, threshold=1, limit=1)
        if "No memories found for specified query" in result:
            return "Error: Memory not found for specified ID: " + memory_id
        else:
            return result
    except Exception as e:
        return f"Error: An error occurred during memory retrieval: {e}"

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        memory_id = sys.argv[1]
        result = exact_memory_retrieval(memory_id)
        print(result)
    else:
        print("Error: Memory ID not provided.")
