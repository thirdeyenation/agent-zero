import unittest
import sys
from unittest.mock import MagicMock

# Mock problematic dependencies required by vector_db.py
sys.modules['langchain_community'] = MagicMock()
sys.modules['langchain_community.vectorstores'] = MagicMock()
sys.modules['langchain_community.vectorstores.utils'] = MagicMock()
sys.modules['langchain_community.docstore.in_memory'] = MagicMock()
sys.modules['langchain.embeddings'] = MagicMock()
sys.modules['langchain'] = MagicMock()
sys.modules['langchain.prompts'] = MagicMock()
sys.modules['langchain.schema'] = MagicMock()
sys.modules['langchain.embeddings.base'] = MagicMock()
sys.modules['langchain.storage'] = MagicMock()
sys.modules['langchain_core'] = MagicMock()
sys.modules['langchain_core.prompts'] = MagicMock()
sys.modules['langchain_core.documents'] = MagicMock()
sys.modules['langchain_core.language_models'] = MagicMock()
sys.modules['langchain_core.language_models.chat_models'] = MagicMock()
sys.modules['langchain_core.language_models.llms'] = MagicMock()
sys.modules['langchain_core.messages'] = MagicMock()
sys.modules['langchain_core.outputs'] = MagicMock()
sys.modules['langchain_core.outputs.chat_generation'] = MagicMock()
sys.modules['langchain_core.callbacks'] = MagicMock()
sys.modules['langchain_core.callbacks.manager'] = MagicMock()
sys.modules['faiss'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['litellm'] = MagicMock()
sys.modules['litellm.types'] = MagicMock()
sys.modules['litellm.types.utils'] = MagicMock()
sys.modules['jinja2'] = MagicMock()
sys.modules['playwright'] = MagicMock()
sys.modules['playwright.async_api'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['anthropic'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['dotenv.parser'] = MagicMock()
sys.modules['aiohttp'] = MagicMock()
sys.modules['cryptography'] = MagicMock()
sys.modules['cryptography.hazmat'] = MagicMock()
sys.modules['cryptography.hazmat.primitives'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.asymmetric'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.serialization'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.hashes'] = MagicMock()
sys.modules['nest_asyncio'] = MagicMock()
sys.modules['psutil'] = MagicMock()
sys.modules['GitPython'] = MagicMock()
sys.modules['git'] = MagicMock()
sys.modules['giturlparse'] = MagicMock()
sys.modules['kokoro'] = MagicMock()
sys.modules['soundfile'] = MagicMock()
sys.modules['whisper'] = MagicMock()
sys.modules['browser_use'] = MagicMock()
sys.modules['html2text'] = MagicMock()
sys.modules['bs4'] = MagicMock()
sys.modules['markdownify'] = MagicMock()
sys.modules['unstructured'] = MagicMock()
sys.modules['webcolors'] = MagicMock()
sys.modules['fastmcp'] = MagicMock()
sys.modules['pymupdf'] = MagicMock()
sys.modules['boto3'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['tiktoken'] = MagicMock()
sys.modules['watchdog'] = MagicMock()
sys.modules['watchdog.observers'] = MagicMock()
sys.modules['watchdog.events'] = MagicMock()

from helpers.vector_db import get_comparator, SafeNames
from helpers.files import evaluate_text_conditions

class TestSimpleEvalSandbox(unittest.TestCase):

    def test_safe_names_missing_key(self):
        data = {"area": "main"}
        safe = SafeNames(data)
        self.assertEqual(safe["area"], "main")
        self.assertIsNone(safe["nonexistent"])
        self.assertNotIn("nonexistent", data) # original not mutated

    def test_comparator_simple_equality(self):
        comp = get_comparator("area == 'main'")
        self.assertTrue(comp({"area": "main"}))
        self.assertFalse(comp({"area": "fragments"}))

    def test_comparator_missing_key_falsy(self):
        comp = get_comparator("not knowledge_source")
        self.assertTrue(comp({"area": "main"})) # key missing -> None -> not None -> True
        self.assertFalse(comp({"knowledge_source": True}))

    def test_dangerous_functions_blocked(self):
        comp = get_comparator("__import__('os').system('echo pwned')")
        self.assertFalse(comp({"area": "main"})) # should fail safely

    def test_safe_functions_work(self):
        comp = get_comparator("len(str(area)) > 0")
        self.assertTrue(comp({"area": "main"}))

    def test_evaluate_text_conditions_truthiness(self):
        template = "{{ if agent_profiles }}Has profiles{{ endif }}"
        # truthy
        res = evaluate_text_conditions(template, agent_profiles=["profile1"])
        self.assertEqual(res, "Has profiles")
        # falsy
        res = evaluate_text_conditions(template, agent_profiles=[])
        self.assertEqual(res, "")

    def test_evaluate_text_conditions_rejects_functions(self):
        # Even safe functions should be rejected in template conditions
        template = "{{ if len(agent_profiles) > 0 }}Has profiles{{ endif }}"
        res = evaluate_text_conditions(template, agent_profiles=["profile1"])
        # Because functions={} raises an exception on eval, it leaves the block un-modified.
        self.assertEqual(res, template)

if __name__ == '__main__':
    unittest.main()
