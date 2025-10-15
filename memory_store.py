#!/usr/bin/env python3
"""
Fractal Memory Store - Maintains TOC index with summarized notes.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional


class MemoryStore:
    """
    Fractal memory with summarization on write.
    Maintains TOC (table of contents) index for efficient retrieval.
    """

    def __init__(self, state_dir: str = "./state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.toc_path = self.state_dir / "toc.jsonl"
        self.artifacts_dir = self.state_dir / "artifacts"
        self.artifacts_dir.mkdir(exist_ok=True)

        self.toc = []  # List of {id, title, note, embedding_path, timestamp}
        self._load_toc()

    def store(self, title: str, content: str, tags: List[str] = None) -> str:
        """
        Store content with automatic summarization.

        Args:
            title: Short title for the memory
            content: Full content (can be large)
            tags: Optional tags for categorization

        Returns:
            memory_id: Unique ID for retrieval
        """
        # Generate ID
        memory_id = hashlib.sha256(
            f"{title}_{time.time()}".encode()
        ).hexdigest()[:16]

        # Summarize content (≤120 tokens)
        summary = self._summarize(content)

        # Store full artifact
        artifact_path = self.artifacts_dir / f"{memory_id}.txt"
        with open(artifact_path, 'w') as f:
            f.write(content)

        # Add to TOC
        toc_entry = {
            "id": memory_id,
            "title": title,
            "note": summary,
            "artifact_path": str(artifact_path.relative_to(self.state_dir)),
            "tags": tags or [],
            "timestamp": time.time()
        }

        self.toc.append(toc_entry)
        self._append_to_toc(toc_entry)

        return memory_id

    def retrieve(self, memory_id: str) -> Optional[str]:
        """Retrieve full content by ID."""
        entry = next((e for e in self.toc if e["id"] == memory_id), None)
        if not entry:
            return None

        artifact_path = self.state_dir / entry["artifact_path"]
        if not artifact_path.exists():
            return None

        with open(artifact_path, 'r') as f:
            return f.read()

    def search_by_tag(self, tag: str) -> List[Dict]:
        """Search TOC entries by tag."""
        return [e for e in self.toc if tag in e.get("tags", [])]

    def get_toc(self, limit: int = 50) -> List[Dict]:
        """Get recent TOC entries (summaries only)."""
        return self.toc[-limit:]

    def _summarize(self, content: str, max_tokens: int = 120) -> str:
        """
        Generate ≤120 token summary of content.
        Simple implementation: take first ~480 chars (~120 tokens).
        """
        max_chars = max_tokens * 4  # Rough estimate: 4 chars/token
        if len(content) <= max_chars:
            return content

        # Truncate and add ellipsis
        return content[:max_chars] + "..."

    def _load_toc(self):
        """Load TOC from disk."""
        if not self.toc_path.exists():
            return

        with open(self.toc_path, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    self.toc.append(entry)

    def _append_to_toc(self, entry: Dict):
        """Append entry to TOC file."""
        with open(self.toc_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')


# Example
if __name__ == "__main__":
    store = MemoryStore()

    # Store some memories
    id1 = store.store(
        "Fibonacci Implementation",
        "def fib(n):\n    return n if n < 2 else fib(n-1) + fib(n-2)\n\nThis is a recursive implementation...",
        tags=["code", "algorithm"]
    )
    print(f"Stored memory: {id1}")

    # Retrieve
    content = store.retrieve(id1)
    print(f"Retrieved: {content[:50]}...")

    # Search by tag
    results = store.search_by_tag("code")
    print(f"Found {len(results)} code memories")

    # Get TOC
    toc = store.get_toc(limit=10)
    print(f"TOC has {len(toc)} entries")
