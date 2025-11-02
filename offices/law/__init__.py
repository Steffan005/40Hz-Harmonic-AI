"""
Unity Law Office - Legal Document Processing & Analysis

Specialized office for:
- PDF document parsing (contracts, briefs, statutes)
- Semantic search over legal corpus
- Legal citation generation (Bluebook, APA)
- Brief drafting with LLM assistance
- Case summarization
"""

from .pdf_parser import LegalPDFParser
from .legal_search import LegalSearchEngine
from .citation_gen import CitationGenerator
from .law_agents import LegalResearchAgent, BriefWriterAgent

__all__ = [
    'LegalPDFParser',
    'LegalSearchEngine',
    'CitationGenerator',
    'LegalResearchAgent',
    'BriefWriterAgent'
]

__version__ = '0.1.0'
