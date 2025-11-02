#!/usr/bin/env python3
"""
Unity RAG Corpus Ingestion System

Embeds 1,000+ sources (PDF/MD/TXT) into FAISS vector database for long-term memory.
All offices can retrieve civic knowledge to ground their reasoning.

Usage:
    python tools/ingest_corpus.py --path "/path/to/UNITY_SOURCES" --chunk 1200 --overlap 200

Author: Dr. Claude Summers, Cosmic Orchestrator
Phase: 6 - Ontology & Ritual Engines
Date: October 16, 2025
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

import faiss
import numpy as np
import tiktoken

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import litellm
except ImportError:
    litellm = None


@dataclass
class Document:
    """A source document with metadata"""
    id: str
    path: str
    filename: str
    filetype: str
    content: str
    chunk_index: int
    total_chunks: int
    token_count: int
    created_at: str
    metadata: Dict


@dataclass
class EmbeddingRecord:
    """An embedded chunk with vector"""
    doc_id: str
    chunk_index: int
    text: str
    embedding: List[float]
    token_count: int
    created_at: str


class CorpusIngester:
    """
    RAG corpus ingestion system for Unity.

    Features:
    - Multi-format support (PDF, MD, TXT)
    - Token-aware chunking with overlap
    - FAISS vector database
    - Local embedding (via Ollama)
    - Metadata preservation
    - Progress tracking
    """

    def __init__(
        self,
        corpus_path: str,
        chunk_size: int = 1200,
        overlap: int = 200,
        embedding_model: str = "nomic-embed-text",
        index_path: str = "./data/rag/faiss_index.bin",
        metadata_path: str = "./data/rag/metadata.jsonl",
        encoding: str = "cl100k_base"
    ):
        self.corpus_path = Path(corpus_path)
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedding_model = embedding_model
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        # Create output directories
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize tokenizer
        self.tokenizer = tiktoken.get_encoding(encoding)

        # FAISS index (will be created on first embed)
        self.index = None
        self.dimension = 768  # Default for nomic-embed-text

        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_failed": 0,
            "chunks_created": 0,
            "chunks_embedded": 0,
            "total_tokens": 0,
            "start_time": None,
            "end_time": None
        }

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))

    def chunk_text(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Chunk text with token-aware splitting and overlap.

        Returns:
            List of (chunk_text, start_offset, end_offset)
        """
        tokens = self.tokenizer.encode(text)
        chunks = []

        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))

            # Decode chunk
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)

            chunks.append((chunk_text, start, end))

            # Move start forward with overlap
            start = end - self.overlap if end < len(tokens) else end

        return chunks

    def read_txt(self, path: Path) -> str:
        """Read TXT file"""
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def read_md(self, path: Path) -> str:
        """Read Markdown file"""
        return self.read_txt(path)  # Same as TXT

    def read_pdf(self, path: Path) -> str:
        """Read PDF file"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required for PDF reading")

        text_parts = []
        with open(path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        return "\n\n".join(text_parts)

    def read_file(self, path: Path) -> Optional[str]:
        """Read file content based on extension"""
        ext = path.suffix.lower()

        try:
            if ext == '.txt':
                return self.read_txt(path)
            elif ext == '.md':
                return self.read_md(path)
            elif ext == '.pdf':
                return self.read_pdf(path)
            else:
                print(f"⚠️  Unsupported file type: {ext} ({path.name})")
                return None
        except Exception as e:
            print(f"❌ Error reading {path.name}: {e}")
            return None

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding for text using local Ollama model.

        Uses nomic-embed-text by default (768-dim).
        """
        if litellm is None:
            # Fallback: random embedding for testing
            print("⚠️  LiteLLM not available, using random embeddings")
            return np.random.rand(self.dimension).astype('float32')

        try:
            response = litellm.embedding(
                model=f"ollama/{self.embedding_model}",
                input=[text]
            )

            # Extract embedding
            embedding = response.data[0]["embedding"]
            embedding_array = np.array(embedding, dtype='float32')

            # Update dimension if first embedding
            if self.index is None:
                self.dimension = len(embedding_array)

            return embedding_array

        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return None

    def create_index(self):
        """Create FAISS index"""
        self.index = faiss.IndexFlatL2(self.dimension)
        print(f"✅ Created FAISS index (dim={self.dimension})")

    def add_to_index(self, embeddings: np.ndarray):
        """Add embeddings to FAISS index"""
        if self.index is None:
            self.create_index()

        self.index.add(embeddings)

    def save_index(self):
        """Save FAISS index to disk"""
        if self.index is None:
            print("⚠️  No index to save")
            return

        faiss.write_index(self.index, str(self.index_path))
        print(f"✅ Saved FAISS index to {self.index_path}")

    def save_metadata(self, records: List[EmbeddingRecord]):
        """Save metadata to JSONL"""
        with open(self.metadata_path, 'a', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(asdict(record)) + '\n')

    def process_file(self, path: Path) -> List[Document]:
        """
        Process a single file into chunked documents.

        Returns:
            List of Document objects (one per chunk)
        """
        # Read content
        content = self.read_file(path)
        if content is None:
            self.stats["files_failed"] += 1
            return []

        # Chunk content
        chunks = self.chunk_text(content)

        # Create documents
        documents = []
        timestamp = datetime.now().isoformat()

        for idx, (chunk_text, start_offset, end_offset) in enumerate(chunks):
            doc_id = f"{path.stem}_{idx}_{int(time.time())}"
            token_count = self.count_tokens(chunk_text)

            doc = Document(
                id=doc_id,
                path=str(path),
                filename=path.name,
                filetype=path.suffix.lower(),
                content=chunk_text,
                chunk_index=idx,
                total_chunks=len(chunks),
                token_count=token_count,
                created_at=timestamp,
                metadata={
                    "start_offset": start_offset,
                    "end_offset": end_offset
                }
            )
            documents.append(doc)

        self.stats["files_processed"] += 1
        self.stats["chunks_created"] += len(documents)

        return documents

    def embed_documents(self, documents: List[Document]) -> List[EmbeddingRecord]:
        """
        Embed all documents and return records.

        Returns:
            List of EmbeddingRecord objects
        """
        records = []
        embeddings_list = []

        for doc in documents:
            embedding = self.get_embedding(doc.content)

            if embedding is None:
                print(f"⚠️  Failed to embed chunk {doc.chunk_index} of {doc.filename}")
                continue

            # Create record
            record = EmbeddingRecord(
                doc_id=doc.id,
                chunk_index=doc.chunk_index,
                text=doc.content,
                embedding=embedding.tolist(),
                token_count=doc.token_count,
                created_at=doc.created_at
            )
            records.append(record)
            embeddings_list.append(embedding)

            self.stats["chunks_embedded"] += 1
            self.stats["total_tokens"] += doc.token_count

        # Add to FAISS index
        if embeddings_list:
            embeddings_array = np.vstack(embeddings_list)
            self.add_to_index(embeddings_array)

        return records

    def ingest_corpus(self, max_files: Optional[int] = None):
        """
        Ingest entire corpus.

        Args:
            max_files: Maximum number of files to process (for testing)
        """
        self.stats["start_time"] = datetime.now().isoformat()

        # Find all files
        print(f"🔍 Scanning {self.corpus_path}...")

        all_files = []
        for ext in ['.txt', '.md', '.pdf']:
            all_files.extend(list(self.corpus_path.rglob(f'*{ext}')))

        print(f"📁 Found {len(all_files)} files")

        if max_files:
            all_files = all_files[:max_files]
            print(f"📊 Processing first {max_files} files (test mode)")

        # Process files
        print(f"⚙️  Processing files...")
        print(f"   Chunk size: {self.chunk_size} tokens")
        print(f"   Overlap: {self.overlap} tokens")
        print()

        for idx, file_path in enumerate(all_files, 1):
            print(f"[{idx}/{len(all_files)}] {file_path.name}...", end=' ')

            # Process file
            documents = self.process_file(file_path)

            if not documents:
                print("❌")
                continue

            # Embed documents
            records = self.embed_documents(documents)

            # Save metadata
            self.save_metadata(records)

            print(f"✅ ({len(documents)} chunks, {sum(d.token_count for d in documents)} tokens)")

        # Save index
        self.save_index()

        self.stats["end_time"] = datetime.now().isoformat()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print ingestion summary"""
        print()
        print("=" * 70)
        print("RAG CORPUS INGESTION COMPLETE")
        print("=" * 70)
        print(f"Files processed:    {self.stats['files_processed']}")
        print(f"Files failed:       {self.stats['files_failed']}")
        print(f"Chunks created:     {self.stats['chunks_created']}")
        print(f"Chunks embedded:    {self.stats['chunks_embedded']}")
        print(f"Total tokens:       {self.stats['total_tokens']:,}")
        print(f"Index path:         {self.index_path}")
        print(f"Metadata path:      {self.metadata_path}")

        if self.stats["start_time"] and self.stats["end_time"]:
            start = datetime.fromisoformat(self.stats["start_time"])
            end = datetime.fromisoformat(self.stats["end_time"])
            duration = (end - start).total_seconds()
            print(f"Duration:           {duration:.1f}s")

        print("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Unity RAG Corpus Ingestion")
    parser.add_argument('--path', required=True, help="Path to UNITY_SOURCES directory")
    parser.add_argument('--chunk', type=int, default=1200, help="Chunk size in tokens (default: 1200)")
    parser.add_argument('--overlap', type=int, default=200, help="Overlap in tokens (default: 200)")
    parser.add_argument('--model', default="nomic-embed-text", help="Embedding model (default: nomic-embed-text)")
    parser.add_argument('--index', default="./data/rag/faiss_index.bin", help="FAISS index output path")
    parser.add_argument('--metadata', default="./data/rag/metadata.jsonl", help="Metadata output path")
    parser.add_argument('--max-files', type=int, help="Max files to process (for testing)")

    args = parser.parse_args()

    # Check if corpus path exists
    corpus_path = Path(args.path)
    if not corpus_path.exists():
        print(f"❌ Corpus path does not exist: {corpus_path}")
        sys.exit(1)

    # Create ingester
    ingester = CorpusIngester(
        corpus_path=args.path,
        chunk_size=args.chunk,
        overlap=args.overlap,
        embedding_model=args.model,
        index_path=args.index,
        metadata_path=args.metadata
    )

    # Ingest corpus
    ingester.ingest_corpus(max_files=args.max_files)

    print()
    print("🌌 Unity RAG corpus ready for retrieval across all offices 🌌")


if __name__ == "__main__":
    main()
