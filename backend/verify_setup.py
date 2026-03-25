import sys, os
from dotenv import load_dotenv
load_dotenv()

results = []

def test(name, fn):
    try:
        fn()
        results.append((name, True, ""))
        print(f"  ✓ {name}")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  ✗ {name}: {e}")

print("Running setup verification...\n")

test("Python 3.11",          lambda: (_ for _ in ()).throw(Exception("Need 3.11+")) if sys.version_info < (3,11) else None)
test("FastAPI import",       lambda: __import__('fastapi'))
test("LangChain import",     lambda: __import__('langchain'))
test("FAISS import",         lambda: __import__('faiss'))
test("Sentence Transformers",lambda: __import__('sentence_transformers'))
test("Whisper import",       lambda: __import__('whisper'))
test("Gemini API Key set",   lambda: (_ for _ in ()).throw(Exception("Key not found")) if not os.getenv('GEMINI_API_KEY') else None)
test("Google Translate",     lambda: __import__('deep_translator').GoogleTranslator(
                                 source='hi', target='en'
                             ).translate('नमस्ते'))

passed = sum(1 for _, ok, _ in results if ok)
print(f"\n{passed}/{len(results)} tests passed")

if passed == len(results):
    print("✅ Setup complete! Ready for Day 2.")
else:
    print("⚠️  Fix the failing tests before proceeding.")