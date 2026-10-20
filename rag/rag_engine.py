"""
UtilPulse Command Centre — Resilient RAG Engine
================================================
Retrieval-Augmented Generation engine that indexes knowledge base documents
into ChromaDB and retrieves relevant context for user queries.
Includes multi-tier embedding fallback (SentenceTransformer -> ONNX Default -> Keyword/BM25)
to guarantee high reliability across environments.
"""

import os
import re
from config import KNOWLEDGE_BASE_DIR, CHROMA_DIR


class RAGEngine:
    """Manages knowledge base indexing and retrieval with fallback resilience."""

    def __init__(self):
        self.chroma_available = False
        self.collection = None
        self.fallback_chunks = []

        # 1. Load raw markdown chunks for fallback
        self._load_fallback_chunks()

        # 2. Attempt ChromaDB initialization
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            # Try Sentence Transformers first, then fallback to ONNX Default
            try:
                import sentence_transformers
                self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            except Exception:
                # Default ONNX embedding function requires only onnxruntime
                self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

            self.client = chromadb.PersistentClient(path=CHROMA_DIR)
            self.collection = self.client.get_or_create_collection(
                name="water_utility_knowledge",
                embedding_function=self.embedding_fn,
            )
            self.chroma_available = True

            if self.collection.count() == 0:
                self._index_knowledge_base()

        except Exception:
            # Fallback mode active: direct semantic keyword matching
            self.chroma_available = False

    def _load_fallback_chunks(self):
        """Pre-loads text chunks into memory for fallback retrieval."""
        if not os.path.isdir(KNOWLEDGE_BASE_DIR):
            return

        for filename in sorted(os.listdir(KNOWLEDGE_BASE_DIR)):
            if not filename.lower().endswith(".md"):
                continue
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as fh:
                    text = fh.read()
                chunks = self._chunk_text(text, max_chunk_size=1000)
                for idx, chunk in enumerate(chunks):
                    if len(chunk.strip()) >= 50:
                        self.fallback_chunks.append({
                            "source": filename,
                            "index": idx,
                            "text": chunk.strip()
                        })
            except Exception:
                pass

    def _index_knowledge_base(self):
        """Indexes all knowledge base documents into ChromaDB."""
        if not self.chroma_available or self.collection is None:
            return

        documents = []
        metadatas = []
        ids = []

        for item in self.fallback_chunks:
            doc_id = f"{os.path.splitext(item['source'])[0]}_chunk_{item['index']}"
            documents.append(item["text"])
            metadatas.append({"source": item["source"], "chunk_index": item["index"]})
            ids.append(doc_id)

        if documents:
            batch_size = 200
            for start in range(0, len(documents), batch_size):
                end = start + batch_size
                self.collection.add(
                    documents=documents[start:end],
                    metadatas=metadatas[start:end],
                    ids=ids[start:end],
                )

    def _chunk_text(self, text, max_chunk_size=1000):
        """Splits text into coherent sections by markdown headers and paragraphs."""
        header_pattern = re.compile(r"(?=^## )", re.MULTILINE)
        sections = header_pattern.split(text)

        chunks = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            if len(section) <= max_chunk_size:
                chunks.append(section)
            else:
                paragraphs = re.split(r"\n\n+", section)
                current_chunk = ""
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    if current_chunk and (len(current_chunk) + len(para) + 2) > max_chunk_size:
                        chunks.append(current_chunk)
                        current_chunk = para
                    else:
                        current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para

                if current_chunk:
                    chunks.append(current_chunk)

        return chunks

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieves top_k relevant context chunks for the user's query."""
        if not query or not query.strip():
            return ""

        # 1. Attempt ChromaDB vector retrieval
        if self.chroma_available and self.collection and self.collection.count() > 0:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=min(top_k, self.collection.count())
                )
                documents = results.get("documents", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]

                if documents:
                    context_parts = []
                    for doc, meta in zip(documents, metadatas):
                        source = meta.get("source", "knowledge_base")
                        context_parts.append(f"[Source: {source}]\n{doc}")
                    return "\n\n---\n\n".join(context_parts)
            except Exception:
                pass

        # 2. Fallback: Keyword relevance scoring across pre-loaded chunks
        return self._fallback_retrieve(query, top_k=top_k)

    def _fallback_retrieve(self, query: str, top_k: int = 3) -> str:
        """Keyword overlap matching against knowledge base documents."""
        if not self.fallback_chunks:
            return ""

        query_terms = set(re.findall(r"\w+", query.lower()))
        stopwords = {"what", "is", "the", "in", "of", "and", "to", "for", "a", "an", "show", "me", "how", "why"}
        meaningful_terms = query_terms - stopwords
        if not meaningful_terms:
            meaningful_terms = query_terms

        scored_chunks = []
        for item in self.fallback_chunks:
            text_lower = item["text"].lower()
            score = sum(text_lower.count(term) for term in meaningful_terms)
            if score > 0:
                scored_chunks.append((score, item))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_items = [item for _, item in scored_chunks[:top_k]]

        if not top_items:
            top_items = self.fallback_chunks[:2]

        context_parts = []
        for item in top_items:
            context_parts.append(f"[Source: {item['source']}]\n{item['text']}")

        return "\n\n---\n\n".join(context_parts)
