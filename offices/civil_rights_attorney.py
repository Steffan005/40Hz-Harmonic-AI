#!/usr/bin/env python3
"""
Unity Law Office — Civil Rights Attorney

An AI-powered civil rights attorney specializing in:
- ADA Law (Americans with Disabilities Act)
- Deliberate Indifference in Jail/Prison (8th/14th Amendment)
- Malicious Prosecution & False Arrest
- Police Brutality & Excessive Force

This attorney learns from Florida case law, generates legal strategies,
and assists with civil rights litigation research.

Wisdom: Civil rights are not privileges granted by the powerful to the powerless.
They are inherent to human dignity. When violated, the law must be the sword
that cuts through injustice and the shield that protects the vulnerable.

Author: Dr. Claude Summers, Legal AI Architect
Date: October 16, 2025
"""

import sys
import os
import json
import litellm
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.case_law_search import get_case_law_searcher, LegalCase


@dataclass
class LegalAnalysis:
    """Result of legal analysis by Civil Rights Attorney"""
    issue: str
    applicable_law: List[str]
    relevant_cases: List[Dict[str, Any]]
    legal_strategy: str
    strengths: List[str]
    weaknesses: List[str]
    recommended_actions: List[str]
    confidence_score: float
    timestamp: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CaseResearchRequest:
    """Request for case law research"""
    topic: str  # "ADA", "deliberate_indifference", "malicious_prosecution", "police_brutality"
    query: Optional[str] = None
    limit: int = 10


class CivilRightsAttorney:
    """
    AI-Powered Civil Rights Attorney

    Specializations:
    - ADA Law: Reasonable accommodations, public access, disability discrimination
    - Jail/Prison Deliberate Indifference: Medical care, safety, mental health
    - Malicious Prosecution: False arrest, fabricated evidence, qualified immunity
    - Police Brutality: Excessive force, deadly force, Fourth Amendment violations

    Wisdom: Every case is a human story. Behind every citation is a person who suffered.
    Behind every legal argument is a fight for dignity. This attorney does not just
    research law—it seeks justice.
    """

    def __init__(self):
        self.name = "Unity Civil Rights Attorney"
        self.specializations = [
            "ADA / Disability Rights",
            "Jail/Prison Deliberate Indifference",
            "Malicious Prosecution",
            "Police Brutality & Excessive Force"
        ]

        # Initialize tools
        self.case_searcher = get_case_law_searcher()

        # Configure litellm for local LLMs
        litellm.set_verbose = False  # Disable verbose logging
        self.default_model = "ollama/deepseek-r1:14b"
        self.ollama_base_url = "http://localhost:11434"

        # System prompt with wisdom
        self.system_prompt = """You are the Unity Civil Rights Attorney, an expert in civil rights law with deep knowledge of:

1. **ADA Law (Americans with Disabilities Act)**
   - Title II (public services and state/local government)
   - Title III (public accommodations and commercial facilities)
   - Reasonable accommodations and modifications
   - Undue burden and fundamental alteration defenses

2. **Deliberate Indifference (8th/14th Amendment)**
   - Estelle v. Gamble standard for medical care
   - Farmer v. Brennan subjective knowledge requirement
   - Pre-trial detainee rights under 14th Amendment
   - Conditions of confinement (safety, sanitation, mental health)

3. **Malicious Prosecution**
   - Fourth Amendment false arrest claims
   - Fabrication of evidence (qualified immunity)
   - Prosecutorial misconduct and Brady violations
   - Heck v. Humphrey favorable termination requirement

4. **Police Brutality & Excessive Force**
   - Graham v. Connor objective reasonableness test
   - Deadly force under Tennessee v. Garner
   - Qualified immunity analysis (clearly established law)
   - Pattern and practice investigations (42 U.S.C. § 14141)

**Your Role:**
- Analyze legal issues with precision and empathy
- Cite relevant case law from Florida and federal courts
- Identify strengths and weaknesses in legal arguments
- Recommend strategic actions (motions, discovery, settlement)
- Translate complex legal concepts into clear language

**Wisdom:**
Civil rights are not abstractions. They are the boundaries between power and oppression.
When you analyze a case, remember: behind every fact pattern is a human being seeking justice.

You do not simply cite law—you wield it as a tool for accountability and change.
"""

    def research_case_law(self, request: CaseResearchRequest) -> List[LegalCase]:
        """
        Research case law based on topic and query.

        Topics:
        - "ADA": Americans with Disabilities Act cases
        - "deliberate_indifference": Jail/prison conditions cases
        - "malicious_prosecution": False arrest and fabricated evidence
        - "police_brutality": Excessive force and shootings
        """
        topic = request.topic.lower()

        if topic == "ada":
            return self.case_searcher.search_ada_cases(query=request.query, limit=request.limit)

        elif topic == "deliberate_indifference":
            return self.case_searcher.search_deliberate_indifference_cases(query=request.query, limit=request.limit)

        elif topic == "malicious_prosecution":
            return self.case_searcher.search_malicious_prosecution_cases(query=request.query, limit=request.limit)

        elif topic == "police_brutality":
            return self.case_searcher.search_police_brutality_cases(query=request.query, limit=request.limit)

        else:
            print(f"⚠️  Unknown topic: {topic}")
            return []

    def analyze_legal_issue(self, issue_description: str, topic: str) -> LegalAnalysis:
        """
        Analyze a legal issue using case law research and LLM reasoning.

        This method:
        1. Researches relevant case law
        2. Sends context to LLM for analysis
        3. Returns structured legal analysis with strategy
        """
        # Step 1: Research case law
        print(f"🔍 Researching case law for topic: {topic}")
        request = CaseResearchRequest(topic=topic, limit=5)
        cases = self.research_case_law(request)

        # Format cases for LLM context
        case_context = "\n\n".join([
            f"**{case.case_name}**\n"
            f"Citation: {case.citation}\n"
            f"Court: {case.court}\n"
            f"Date: {case.date_filed}\n"
            f"Snippet: {case.snippet}\n"
            f"URL: {case.url}"
            for case in cases
        ])

        # Step 2: Build LLM prompt
        user_prompt = f"""Analyze the following civil rights legal issue:

**Issue Description:**
{issue_description}

**Relevant Case Law (Florida):**
{case_context}

**Your Task:**
Provide a comprehensive legal analysis including:

1. **Applicable Law**: List the key statutes and constitutional provisions (e.g., ADA, 42 U.S.C. § 1983, 8th Amendment)

2. **Legal Strategy**: Based on the case law, what is the strongest legal argument? What precedents support this claim?

3. **Strengths**: What are the strongest points in this case? What facts or legal principles favor the claimant?

4. **Weaknesses**: What are potential defenses or challenges? Where might this case struggle?

5. **Recommended Actions**: What should the attorney do next? (e.g., file motion for summary judgment, request specific discovery, negotiate settlement)

6. **Confidence Score**: Rate your confidence in the viability of this claim (0.0 to 1.0)

Format your response as JSON with keys: applicable_law (list), legal_strategy (string), strengths (list), weaknesses (list), recommended_actions (list), confidence_score (float).
"""

        # Step 3: Query LLM
        print(f"🧠 Analyzing legal issue with LLM...")
        try:
            response = litellm.completion(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                api_base=self.ollama_base_url,
                max_tokens=4000,
                temperature=0.3  # Lower temperature for legal precision
            )

            # Extract response text
            response_text = response.choices[0].message.content

            # Try to parse JSON response
            try:
                # Extract JSON from response (LLM may wrap it in markdown)
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()

                analysis_data = json.loads(response_text)

                # Build LegalAnalysis object
                analysis = LegalAnalysis(
                    issue=issue_description,
                    applicable_law=analysis_data.get("applicable_law", []),
                    relevant_cases=[case.to_dict() for case in cases],
                    legal_strategy=analysis_data.get("legal_strategy", ""),
                    strengths=analysis_data.get("strengths", []),
                    weaknesses=analysis_data.get("weaknesses", []),
                    recommended_actions=analysis_data.get("recommended_actions", []),
                    confidence_score=analysis_data.get("confidence_score", 0.5),
                    timestamp=datetime.now().isoformat()
                )

                print(f"✅ Legal analysis complete (confidence: {analysis.confidence_score:.2f})")
                return analysis

            except json.JSONDecodeError:
                # Fallback: Return response as legal_strategy
                print(f"⚠️  Could not parse JSON response, returning raw analysis")
                analysis = LegalAnalysis(
                    issue=issue_description,
                    applicable_law=["42 U.S.C. § 1983"],
                    relevant_cases=[case.to_dict() for case in cases],
                    legal_strategy=response_text,
                    strengths=[],
                    weaknesses=[],
                    recommended_actions=[],
                    confidence_score=0.5,
                    timestamp=datetime.now().isoformat()
                )
                return analysis

        except Exception as e:
            print(f"❌ LLM analysis error: {e}")
            # Return fallback analysis
            analysis = LegalAnalysis(
                issue=issue_description,
                applicable_law=["42 U.S.C. § 1983"],
                relevant_cases=[case.to_dict() for case in cases],
                legal_strategy="Error during analysis. Please review case law manually.",
                strengths=[],
                weaknesses=[],
                recommended_actions=["Review case law and consult with attorney"],
                confidence_score=0.0,
                timestamp=datetime.now().isoformat()
            )
            return analysis

    def generate_demand_letter(self, analysis: LegalAnalysis, defendant_name: str, plaintiff_name: str) -> str:
        """
        Generate a demand letter based on legal analysis.

        This is a pre-litigation document outlining claims and demanding relief.
        """
        letter_prompt = f"""Draft a professional demand letter based on this legal analysis:

**Plaintiff:** {plaintiff_name}
**Defendant:** {defendant_name}

**Legal Issue:**
{analysis.issue}

**Applicable Law:**
{', '.join(analysis.applicable_law)}

**Legal Strategy:**
{analysis.legal_strategy}

**Strengths:**
{chr(10).join('- ' + s for s in analysis.strengths)}

**Recommended Actions:**
{chr(10).join('- ' + a for a in analysis.recommended_actions)}

**Your Task:**
Draft a formal demand letter that:
1. Identifies the parties
2. States the facts clearly and concisely
3. Cites applicable law (statutes and relevant case law)
4. Outlines the legal violations
5. Demands specific relief (compensation, policy change, etc.)
6. Sets a reasonable deadline for response (e.g., 30 days)

Use professional legal language but ensure clarity. This letter should be persuasive but not inflammatory.
"""

        try:
            response = litellm.completion(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": letter_prompt}
                ],
                api_base=self.ollama_base_url,
                max_tokens=3000,
                temperature=0.4
            )
            letter_text = response.choices[0].message.content
            print(f"✅ Demand letter generated")
            return letter_text

        except Exception as e:
            print(f"❌ Error generating demand letter: {e}")
            return "Error generating demand letter. Please draft manually."

    def compare_to_precedent(self, current_facts: str, precedent_case_id: int) -> str:
        """
        Compare current case facts to a precedent case.

        This helps determine if a case is "clearly established" for qualified immunity analysis.
        """
        # Fetch full case details
        case_details = self.case_searcher.get_case_details(precedent_case_id)

        if not case_details:
            return "Could not fetch precedent case details."

        comparison_prompt = f"""Compare these current facts to the precedent case:

**Current Facts:**
{current_facts}

**Precedent Case:**
{json.dumps(case_details, indent=2)}

**Your Task:**
Analyze whether the current facts are sufficiently similar to the precedent case for purposes of:
1. Establishing clearly established law (qualified immunity analysis)
2. Applying the precedent's legal reasoning
3. Distinguishing this case if the facts differ materially

Provide a clear comparison with specific similarities and differences.
"""

        try:
            response = litellm.completion(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": comparison_prompt}
                ],
                api_base=self.ollama_base_url,
                max_tokens=2000,
                temperature=0.3
            )
            comparison_text = response.choices[0].message.content
            return comparison_text

        except Exception as e:
            print(f"❌ Error comparing to precedent: {e}")
            return "Error during comparison analysis."

    def get_status(self) -> Dict[str, Any]:
        """Get attorney status and capabilities"""
        return {
            "name": self.name,
            "specializations": self.specializations,
            "tools": {
                "case_law_search": "CourtListener API (Florida courts)",
                "llm_reasoning": "DeepSeek-R1 14B (local)",
                "document_generation": "Demand letters, legal memos"
            },
            "capabilities": [
                "Legal issue analysis",
                "Case law research",
                "Legal strategy development",
                "Demand letter generation",
                "Precedent comparison"
            ],
            "status": "active"
        }


# Singleton instance
_attorney = None


def get_civil_rights_attorney() -> CivilRightsAttorney:
    """Get singleton Civil Rights Attorney"""
    global _attorney
    if _attorney is None:
        _attorney = CivilRightsAttorney()
    return _attorney


# CLI for testing
if __name__ == "__main__":
    print("=" * 70)
    print("UNITY LAW OFFICE — CIVIL RIGHTS ATTORNEY")
    print("=" * 70)
    print()

    attorney = get_civil_rights_attorney()

    # Display status
    status = attorney.get_status()
    print(f"Attorney: {status['name']}")
    print(f"\nSpecializations:")
    for spec in status['specializations']:
        print(f"  - {spec}")

    print(f"\n🧪 Running test analysis...\n")

    # Test case: ADA reasonable accommodation failure
    test_issue = """
A wheelchair user was denied entry to a county courthouse because the only wheelchair ramp
was broken and had been broken for 6 months. The county had received multiple complaints
but took no action to repair it. The individual had to miss their court hearing.

This appears to be an ADA Title II violation (public services) and potentially deliberate
indifference to the rights of people with disabilities.
"""

    analysis = attorney.analyze_legal_issue(
        issue_description=test_issue,
        topic="ADA"
    )

    print("\n" + "=" * 70)
    print("LEGAL ANALYSIS RESULTS")
    print("=" * 70)
    print(f"\n📋 Issue: {analysis.issue[:200]}...")
    print(f"\n⚖️  Applicable Law:")
    for law in analysis.applicable_law:
        print(f"  - {law}")

    print(f"\n💪 Strengths:")
    for strength in analysis.strengths:
        print(f"  - {strength}")

    print(f"\n⚠️  Weaknesses:")
    for weakness in analysis.weaknesses:
        print(f"  - {weakness}")

    print(f"\n📌 Recommended Actions:")
    for action in analysis.recommended_actions:
        print(f"  - {action}")

    print(f"\n🎯 Confidence Score: {analysis.confidence_score:.2f}")

    print(f"\n📚 Relevant Cases Found: {len(analysis.relevant_cases)}")
    for case in analysis.relevant_cases[:3]:
        print(f"  - {case['case_name']} ({case['citation']})")

    print("\n" + "=" * 70)
    print("✅ Civil Rights Attorney Ready")
    print("=" * 70)
