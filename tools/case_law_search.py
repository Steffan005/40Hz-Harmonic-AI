#!/usr/bin/env python3
"""
Unity Law Office — Case Law Search Tool
CourtListener API Integration for Florida Case Law Research

Focus Areas:
- ADA Law (Americans with Disabilities Act)
- Deliberate Indifference in Jails (8th/14th Amendment)
- Malicious Prosecution
- Police Brutality & Excessive Force

Author: Dr. Claude Summers, Legal AI Architect
Date: October 16, 2025
"""

import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# CourtListener API Configuration
COURTLISTENER_API_KEY = "0ca1bba3efb096b9f25152cf560976880a98e90b"
COURTLISTENER_BASE_URL = "https://www.courtlistener.com/api/rest/v3"


@dataclass
class LegalCase:
    """A single case from CourtListener"""
    case_name: str
    citation: str
    court: str
    date_filed: str
    url: str
    snippet: str
    relevance_score: float
    case_id: int

    def to_dict(self) -> Dict:
        return asdict(self)


class CaseLawSearcher:
    """
    Searches legal cases using CourtListener API.

    Wisdom: The law is not just statutes and precedent. It is the living
    embodiment of justice—or injustice. Every case represents a human being
    seeking dignity, protection, or vindication. Search with purpose.
    """

    def __init__(self, api_key: str = COURTLISTENER_API_KEY):
        self.api_key = api_key
        self.base_url = COURTLISTENER_BASE_URL
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

        # Florida court IDs (CourtListener uses these)
        self.florida_courts = [
            "fla",           # Florida Supreme Court
            "flaapp1",       # Florida 1st DCA
            "flaapp2",       # Florida 2nd DCA
            "flaapp3",       # Florida 3rd DCA
            "flaapp4",       # Florida 4th DCA
            "flaapp5",       # Florida 5th DCA
            "flam",          # Middle District of Florida
            "flan",          # Northern District of Florida
            "flas"           # Southern District of Florida
        ]

    def search_ada_cases(self, query: str = None, limit: int = 10) -> List[LegalCase]:
        """
        Search for ADA (Americans with Disabilities Act) cases in Florida.

        Focus: Title II (public services), Title III (public accommodations),
        reasonable accommodations, access barriers, discrimination.
        """
        if query is None:
            query = "Americans with Disabilities Act reasonable accommodation"

        full_query = f"{query} Florida"

        return self._search_cases(
            query=full_query,
            topic="ADA / Disability Rights",
            limit=limit
        )

    def search_deliberate_indifference_cases(self, query: str = None, limit: int = 10) -> List[LegalCase]:
        """
        Search for deliberate indifference cases (jail/prison conditions).

        Focus: Medical care, safety, sanitation, mental health, suicide prevention,
        Eighth Amendment (cruel and unusual punishment), Fourteenth Amendment (pretrial).

        Wisdom: Deliberate indifference is the gulf between knowing someone is suffering
        and choosing to do nothing. The law demands more than apathy.
        """
        if query is None:
            query = "deliberate indifference jail medical care Eighth Amendment"

        full_query = f"{query} Florida"

        return self._search_cases(
            query=full_query,
            topic="Jail Conditions / Deliberate Indifference",
            limit=limit
        )

    def search_malicious_prosecution_cases(self, query: str = None, limit: int = 10) -> List[LegalCase]:
        """
        Search for malicious prosecution cases.

        Focus: False arrest, fabricated evidence, prosecutorial misconduct,
        Fourth Amendment violations, qualified immunity.

        Wisdom: Malicious prosecution is the weaponization of the justice system
        against the innocent. It perverts the very purpose of law.
        """
        if query is None:
            query = "malicious prosecution false arrest fabricated evidence"

        full_query = f"{query} Florida"

        return self._search_cases(
            query=full_query,
            topic="Malicious Prosecution",
            limit=limit
        )

    def search_police_brutality_cases(self, query: str = None, limit: int = 10) -> List[LegalCase]:
        """
        Search for police brutality and excessive force cases.

        Focus: Excessive force, deadly force, officer-involved shootings,
        Fourth Amendment, qualified immunity, pattern and practice.

        Wisdom: Excessive force cases are not about hating police. They are about
        holding power accountable when it crushes the powerless.
        """
        if query is None:
            query = "excessive force police shooting Fourth Amendment"

        full_query = f"{query} Florida"

        return self._search_cases(
            query=full_query,
            topic="Police Brutality / Excessive Force",
            limit=limit
        )

    def _search_cases(self, query: str, topic: str, limit: int = 10) -> List[LegalCase]:
        """
        Internal method to search CourtListener API.

        Returns cases sorted by relevance, filtered to Florida courts.
        """
        try:
            # CourtListener search endpoint
            url = f"{self.base_url}/search/"

            params = {
                "q": query,
                "type": "o",  # Opinion search
                "order_by": "score desc",  # Relevance
                "court": ",".join(self.florida_courts),  # Florida courts only
                "stat_Precedential": "on"  # Precedential opinions only
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code != 200:
                print(f"⚠️  CourtListener API error: {response.status_code}")
                return []

            data = response.json()
            results = data.get("results", [])[:limit]

            cases = []
            for idx, result in enumerate(results):
                case = LegalCase(
                    case_name=result.get("caseName", "Unknown Case"),
                    citation=result.get("citation", [None])[0] if result.get("citation") else "No citation",
                    court=result.get("court", "Unknown Court"),
                    date_filed=result.get("dateFiled", "Unknown Date"),
                    url=f"https://www.courtlistener.com{result.get('absolute_url', '')}",
                    snippet=result.get("snippet", "")[:300],  # First 300 chars
                    relevance_score=1.0 - (idx * 0.05),  # Decay by position
                    case_id=result.get("id", 0)
                )
                cases.append(case)

            print(f"✅ Found {len(cases)} cases for topic: {topic}")
            return cases

        except Exception as e:
            print(f"❌ Case law search error: {e}")
            return []

    def get_case_details(self, case_id: int) -> Optional[Dict]:
        """
        Fetch full case details including opinion text.

        Use this to get the full text of a case for deeper analysis.
        """
        try:
            url = f"{self.base_url}/opinions/{case_id}/"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  Could not fetch case {case_id}: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error fetching case details: {e}")
            return None

    def search_by_citation(self, citation: str) -> Optional[LegalCase]:
        """
        Search for a specific case by citation (e.g., "42 U.S.C. § 1983").
        """
        try:
            url = f"{self.base_url}/search/"
            params = {
                "q": citation,
                "type": "o",
                "order_by": "score desc",
                "court": ",".join(self.florida_courts)
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                if results:
                    result = results[0]
                    return LegalCase(
                        case_name=result.get("caseName", "Unknown Case"),
                        citation=result.get("citation", [None])[0] if result.get("citation") else "No citation",
                        court=result.get("court", "Unknown Court"),
                        date_filed=result.get("dateFiled", "Unknown Date"),
                        url=f"https://www.courtlistener.com{result.get('absolute_url', '')}",
                        snippet=result.get("snippet", "")[:300],
                        relevance_score=1.0,
                        case_id=result.get("id", 0)
                    )

            return None

        except Exception as e:
            print(f"❌ Citation search error: {e}")
            return None


# Singleton instance
_searcher = None


def get_case_law_searcher() -> CaseLawSearcher:
    """Get singleton case law searcher"""
    global _searcher
    if _searcher is None:
        _searcher = CaseLawSearcher()
    return _searcher


# CLI for testing
if __name__ == "__main__":
    print("=" * 70)
    print("UNITY LAW OFFICE — CASE LAW SEARCH TOOL")
    print("=" * 70)
    print()

    searcher = get_case_law_searcher()

    print("🏛️  Testing ADA Case Search...")
    ada_cases = searcher.search_ada_cases(limit=3)
    for case in ada_cases:
        print(f"\n  {case.case_name}")
        print(f"  Citation: {case.citation}")
        print(f"  Court: {case.court}")
        print(f"  URL: {case.url}")

    print("\n" + "=" * 70)
    print("🔗 Testing Deliberate Indifference Search...")
    jail_cases = searcher.search_deliberate_indifference_cases(limit=3)
    for case in jail_cases:
        print(f"\n  {case.case_name}")
        print(f"  Citation: {case.citation}")

    print("\n" + "=" * 70)
    print("⚖️  Testing Malicious Prosecution Search...")
    malice_cases = searcher.search_malicious_prosecution_cases(limit=3)
    for case in malice_cases:
        print(f"\n  {case.case_name}")
        print(f"  Citation: {case.citation}")

    print("\n" + "=" * 70)
    print("👮 Testing Police Brutality Search...")
    force_cases = searcher.search_police_brutality_cases(limit=3)
    for case in force_cases:
        print(f"\n  {case.case_name}")
        print(f"  Citation: {case.citation}")

    print("\n" + "=" * 70)
    print("✅ Case Law Search Tool Ready")
    print("=" * 70)
