import sys
sys.path.insert(0, 'backend')

from config import VECTORSTORE_DIR, EMBEDDING_MODEL, TOP_K_RETRIEVAL
from models import QueryRequest, QueryResponse, Source
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load FAISS using config values
emb = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
db = FAISS.load_local(
    str(VECTORSTORE_DIR),
    emb,
    allow_dangerous_deserialization=True
)

# Simulate a real request using QueryRequest model
req = QueryRequest(
    query='dengue fever symptoms',
    lang_code='en',
    language_name='English'
)

# Search using TOP_K from config
results = db.similarity_search(req.query, k=TOP_K_RETRIEVAL)

# Build a QueryResponse using models.py
sources = [
    Source(
        source=d.metadata.get('source', '?'),
        page=d.metadata.get('page', 0),
        content=d.page_content[:200]
    )
    for d in results
]

response = QueryResponse(
    answer='Dengue symptoms include high fever...',
    triage_level='yellow',
    triage_override=False,
    sources=sources,
    latency_ms=980
)

print('Integration test: OK')
print(f'  Sources retrieved: {len(response.sources)}')
print(f'  First source:      {response.sources[0].source}')
print(f'  Triage level:      {response.triage_level}')
print(f'  Latency (ms):      {response.latency_ms}')
print()
print('config.py + models.py + FAISS all working together!')