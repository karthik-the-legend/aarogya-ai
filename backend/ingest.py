# ================================================================
# backend\ingest.py
# Reads all PDFs in data\, chunks them, embeds each chunk,
# stores in FAISS index on disk.
# Run command: python backend\ingest.py
# ================================================================

import sys
import time
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Import everything from config.py
from config import DATA_DIR, VECTORSTORE_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL


def load_documents():
    """
    Load every PDF from DATA_DIR using LangChain's DirectoryLoader.
    Each page of each PDF becomes one Document object.
    Document.metadata contains:
      - source: full file path (e.g. data/01_who_dengue.pdf)
      - page:   page number (0-indexed)
    """
    print(f"\n[1/4] Loading PDFs from: {DATA_DIR}")

    pdf_files = list(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        print("ERROR: No PDFs found in data\\ folder!")
        print("  Go back to Day 2 and download the 12 PDFs first.")
        sys.exit(1)

    print(f"  Found {len(pdf_files)} PDF files:")
    for f in sorted(pdf_files):
        print(f"    ✓ {f.name}")

    loader = DirectoryLoader(
        str(DATA_DIR), glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True
    )
    docs = loader.load()
    print(f"  Loaded {len(docs)} total pages")
    return docs


def chunk_documents(docs):
    """
    Split each document into overlapping chunks.
    RecursiveCharacterTextSplitter tries to split on:
      1. Paragraph breaks (\\n\\n)  ← preferred
      2. Single newlines (\\n)
      3. Full stop + space (". ")
      4. Space (" ")               ← last resort
    chunk_size uses word count (not characters) because
    words give more stable chunk sizes across PDFs.
    """
    print(
        f"\n[2/4] Splitting into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})..."
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=lambda text: len(text.split()),
        separators=["\n\n", "\n", ". ", " "],
    )

    chunks = splitter.split_documents(docs)
    print(f"  Created {len(chunks)} chunks from {len(docs)} pages")
    print(f"  Average ~{len(docs)//max(len(chunks),1)} pages per chunk")

    print("\n  SAMPLE CHUNK (first chunk):")
    print(f"    Source: {chunks[0].metadata.get('source','?')}")
    print(f"    Page:   {chunks[0].metadata.get('page','?')}")
    print(f"    Text:   {chunks[0].page_content[:200]}...")
    return chunks


def build_faiss_index(chunks):
    """
    Embed all chunks and build the FAISS vector index.
      Step 1: Download embedding model (once, ~120MB)
      Step 2: Convert each chunk text into a 384-dim float array
      Step 3: Store all vectors in an IndexFlatL2 FAISS index
      Step 4: Save to vectorstore\\ folder on disk
    normalize_embeddings=True normalises vectors to unit length
    so cosine similarity works correctly via dot product.
    """
    print(f"\n[3/4] Loading embedding model: {EMBEDDING_MODEL}")
    print("  (First run downloads ~120MB — takes 1-2 min)")

    t_start = time.time()

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print(f"\n[4/4] Building FAISS index for {len(chunks)} chunks...")
    print("  This embeds every chunk — takes ~2-5 minutes on CPU")

    vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)

    vectorstore.save_local(str(VECTORSTORE_DIR))

    elapsed = round(time.time() - t_start, 1)
    print(f"\n  ✓ FAISS index saved to: {VECTORSTORE_DIR}")
    print(f"  ✓ Time taken:           {elapsed} seconds")
    print(f"  ✓ Vectors stored:       {len(chunks)}")
    print(f"  ✓ Dimensions per vector: 384")


if __name__ == "__main__":
    print("=" * 55)
    print("  Aarogya AI — Building Medical Knowledge Index")
    print("=" * 55)

    documents = load_documents()
    chunks = chunk_documents(documents)
    build_faiss_index(chunks)

    print("\n" + "=" * 55)
    print("  DONE. Run next: python backend\\test_faiss.py")
    print("=" * 55)
