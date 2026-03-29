import sys

sys.path.insert(0, "backend")
from rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

queries = [
    "How to prevent catching a cold?",
    "How does common cold spread?",
]

for q in queries:
    print(f"\nQuery: {q}")
    r = pipeline.ask(q)
    print(f"Answer: {r['answer']}")
    print(f"Sources: {[s['source'] for s in r['sources']]}")
    print("-" * 50)
