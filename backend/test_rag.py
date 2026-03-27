import sys
sys.path.insert(0, 'backend')

from rag_pipeline import RAGPipeline

print("Loading RAG pipeline...")
pipeline = RAGPipeline()

# Test 1: English query
print("\n--- TEST 1: English ---")
r = pipeline.ask("What are symptoms of dengue fever?", language="English")
print(f"Answer  : {r['answer'][:300]}")
print(f"Sources : {r['n_chunks']} chunks")
print(f"From    : {r['sources'][0]['source']}")

# Test 2: Hindi response
print("\n--- TEST 2: Hindi response ---")
r2 = pipeline.ask("What is malaria?", language="Hindi")
print(f"Answer  : {r2['answer'][:300]}")

# Test 3: Out of scope
print("\n--- TEST 3: Out of scope ---")
r3 = pipeline.ask("How to treat a broken leg?", language="English")
print(f"Answer  : {r3['answer'][:300]}")

print("\n✅ All RAG tests complete!")