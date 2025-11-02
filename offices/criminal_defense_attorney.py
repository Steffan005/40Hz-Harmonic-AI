#!/usr/bin/env python3
"""
Unity Law Office — Criminal Defense Attorney

An AI-powered criminal defense attorney specializing in:
- Not Guilty by Reason of Temporary Insanity (Florida Law)
- Competency to Stand Trial (Florida Statutes § 916)
- Post-Trial Release and Bond Hearings
- Mental Health Defenses and Mitigation

This attorney learns from Florida criminal case law, develops defense strategies,
and assists with mental health-based defenses.

Wisdom: The criminal justice system is not designed for healing—it is designed
for punishment. When mental illness intersects with alleged crime, the law must
recognize that incarceration is not treatment. True justice requires compassion,
not just confinement. Every defendant deserves a zealous advocate who sees their
humanity beyond the charges.

Focus Case: Steffan Haskins, Orlando, Florida
Defense Theory: Temporary insanity at time of alleged offense

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
class DefenseAnalysis:
    """Result of criminal defense analysis"""
    defendant_name: str
    charges: List[str]
    defense_theory: str
    applicable_law: List[str]
    relevant_cases: List[Dict[str, Any]]
    defense_strategy: str
    strengths: List[str]
    weaknesses: List[str]
    recommended_actions: List[str]
    expert_witnesses_needed: List[str]
    confidence_score: float
    timestamp: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CompetencyEvaluation:
    """Competency to stand trial evaluation"""
    defendant_name: str
    evaluation_date: str
    understands_charges: bool
    understands_proceedings: bool
    can_assist_counsel: bool
    mental_health_history: str
    competency_opinion: str  # "competent", "incompetent", "restoration_recommended"
    florida_statute_cite: str  # Florida Statutes § 916
    recommended_actions: List[str]
    timestamp: str

    def to_dict(self) -> Dict:
        return asdict(self)


class CriminalDefenseAttorney:
    """
    AI-Powered Criminal Defense Attorney

    Specializations:
    - Temporary Insanity Defense: Florida's McNaghten rule + irresistible impulse
    - Competency to Stand Trial: Florida Statutes § 916
    - Post-Trial Release: Bail arguments, mental health treatment in lieu of incarceration
    - Mental Health Mitigation: Bipolar disorder, PTSD, acute psychosis

    Wisdom: Mental illness is not an excuse—it is an explanation. The law recognizes
    that when a person's mind is so fractured that they cannot distinguish right from
    wrong, or control their actions, they are not criminally responsible. This is not
    weakness; it is tragedy. And tragedy demands treatment, not punishment.

    Focus Case: Steffan Haskins, Orlando, Florida
    - Alleged offense during acute mental health crisis
    - Defense theory: Temporary insanity / lack of criminal responsibility
    - Goal: Not guilty by reason of insanity OR competency restoration + mental health diversion
    """

    def __init__(self):
        self.name = "Unity Criminal Defense Attorney"
        self.specializations = [
            "Temporary Insanity Defense (Florida Law)",
            "Competency to Stand Trial (FL § 916)",
            "Post-Trial Release / Bail Hearings",
            "Mental Health Mitigation"
        ]

        # Initialize tools
        self.case_searcher = get_case_law_searcher()

        # Configure litellm for local LLMs
        litellm.set_verbose = False
        self.default_model = "ollama/deepseek-r1:14b"
        self.ollama_base_url = "http://localhost:11434"

        # System prompt with wisdom and Florida-specific legal knowledge
        self.system_prompt = """You are the Unity Criminal Defense Attorney, an expert in criminal defense with deep knowledge of Florida law, particularly mental health defenses.

**Specializations:**

1. **Temporary Insanity Defense (Florida Law)**
   - McNaghten Rule: Defendant did not know right from wrong at time of offense
   - Irresistible Impulse Test: Defendant could not control their actions
   - Florida Statutes § 775.027 (Insanity Defense)
   - Burden of proof: Defendant must prove insanity by clear and convincing evidence
   - Outcome: Not guilty by reason of insanity → commitment to mental health facility

2. **Competency to Stand Trial (Florida Statutes § 916)**
   - Competency standard: Defendant must have sufficient present ability to consult with attorney with reasonable degree of rational understanding, and rational as well as factual understanding of proceedings
   - Florida Rule of Criminal Procedure 3.210, 3.211, 3.212
   - Evaluation by state-appointed psychologist/psychiatrist
   - Incompetent → proceedings suspended, restoration treatment ordered
   - If not restorable within statutory time limits → charges may be dismissed

3. **Post-Trial Release / Bail Hearings**
   - Florida Rule of Criminal Procedure 3.131
   - Mental health treatment as condition of release
   - Electronic monitoring, no-contact orders
   - Arguments: Lack of flight risk, community ties, mental health treatment plan in place

4. **Mental Health Mitigation**
   - Bipolar disorder, PTSD, schizophrenia, acute psychosis
   - Mitigating factors for sentencing under Florida Statutes § 921.0026
   - Expert testimony from psychiatrists, psychologists, therapists
   - Treatment-focused sentencing (mental health court, diversion programs)

**Focus Case: Steffan Haskins, Orlando, Florida**
You are specifically representing Steffan Haskins in Orlando, Florida. Research Florida case law on:
- Temporary insanity defenses in Orange County, Florida
- Competency restoration in Florida mental health facilities
- Successful mental health diversions in Florida criminal courts

**Your Role:**
- Analyze charges and develop defense theory based on mental health
- Cite relevant Florida case law and statutes
- Identify expert witnesses (forensic psychiatrists, psychologists)
- Recommend strategic actions (competency motion, insanity defense, plea negotiation)
- Translate complex legal/medical concepts into clear language

**Wisdom:**
The criminal justice system often fails those with mental illness. Your job is to be a fierce advocate for defendants who, in their darkest moments, lost control of their minds—not their morals. Mental illness is not a choice. And when the law punishes illness as if it were crime, it perpetuates injustice.

You do not simply cite law—you fight for human dignity in a system that too often forgets it.
"""

    def research_insanity_defense(self, query: str = None, limit: int = 10) -> List[LegalCase]:
        """
        Research Florida case law on insanity defense.

        This searches for cases involving:
        - McNaghten rule applications
        - Irresistible impulse tests
        - Not guilty by reason of insanity verdicts
        - Mental illness and criminal responsibility
        """
        if query is None:
            query = "insanity defense McNaghten mental illness criminal responsibility Florida"

        # Use general case law search (CourtListener doesn't have insanity-specific category)
        try:
            url = f"{self.case_searcher.base_url}/search/"
            params = {
                "q": query,
                "type": "o",  # Opinion search
                "order_by": "score desc",
                "court": ",".join(self.case_searcher.florida_courts),
                "stat_Precedential": "on"
            }

            import requests
            response = requests.get(url, headers=self.case_searcher.headers, params=params, timeout=10)

            if response.status_code == 200:
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
                        snippet=result.get("snippet", "")[:300],
                        relevance_score=1.0 - (idx * 0.05),
                        case_id=result.get("id", 0)
                    )
                    cases.append(case)

                print(f"✅ Found {len(cases)} insanity defense cases")
                return cases

            else:
                print(f"⚠️  CourtListener API error: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Case law search error: {e}")
            return []

    def analyze_defense_case(
        self,
        defendant_name: str,
        charges: List[str],
        facts: str,
        mental_health_history: str
    ) -> DefenseAnalysis:
        """
        Analyze a criminal case and develop a defense strategy based on mental health.

        This method:
        1. Researches relevant case law (insanity defense, competency)
        2. Analyzes facts through lens of mental health defenses
        3. Develops defense strategy with LLM reasoning
        4. Returns structured defense analysis
        """
        # Step 1: Research case law
        print(f"🔍 Researching case law for {defendant_name}...")
        insanity_cases = self.research_insanity_defense(limit=5)

        # Format cases for LLM context
        case_context = "\n\n".join([
            f"**{case.case_name}**\n"
            f"Citation: {case.citation}\n"
            f"Court: {case.court}\n"
            f"Date: {case.date_filed}\n"
            f"Snippet: {case.snippet}\n"
            f"URL: {case.url}"
            for case in insanity_cases
        ])

        # Step 2: Build LLM prompt
        user_prompt = f"""Analyze this criminal defense case:

**Defendant:** {defendant_name}

**Charges:**
{chr(10).join('- ' + charge for charge in charges)}

**Facts of the Case:**
{facts}

**Mental Health History:**
{mental_health_history}

**Relevant Case Law (Florida):**
{case_context if case_context else "No case law retrieved. Use general Florida law principles."}

**Your Task:**
Provide a comprehensive criminal defense analysis including:

1. **Defense Theory**: What is the primary defense strategy? (e.g., temporary insanity, competency challenge, mental health mitigation)

2. **Applicable Law**: List key Florida statutes and legal principles (e.g., FL § 775.027, FL § 916, McNaghten rule)

3. **Defense Strategy**: What is the step-by-step plan? (e.g., file competency motion, retain forensic psychiatrist, negotiate mental health diversion)

4. **Strengths**: What facts and legal principles support this defense?

5. **Weaknesses**: What are the prosecution's strongest arguments? What challenges does the defense face?

6. **Recommended Actions**: What should the defense attorney do immediately? (motions, expert witnesses, investigations)

7. **Expert Witnesses Needed**: What types of experts are required? (forensic psychiatrists, neuropsychologists, treating physicians)

8. **Confidence Score**: Rate your confidence in the viability of this defense (0.0 to 1.0)

Format your response as JSON with keys: defense_theory (string), applicable_law (list), defense_strategy (string), strengths (list), weaknesses (list), recommended_actions (list), expert_witnesses_needed (list), confidence_score (float).
"""

        # Step 3: Query LLM
        print(f"🧠 Analyzing defense strategy with LLM...")
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

            response_text = response.choices[0].message.content

            # Try to parse JSON response
            try:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()

                analysis_data = json.loads(response_text)

                # Build DefenseAnalysis object
                analysis = DefenseAnalysis(
                    defendant_name=defendant_name,
                    charges=charges,
                    defense_theory=analysis_data.get("defense_theory", ""),
                    applicable_law=analysis_data.get("applicable_law", []),
                    relevant_cases=[case.to_dict() for case in insanity_cases],
                    defense_strategy=analysis_data.get("defense_strategy", ""),
                    strengths=analysis_data.get("strengths", []),
                    weaknesses=analysis_data.get("weaknesses", []),
                    recommended_actions=analysis_data.get("recommended_actions", []),
                    expert_witnesses_needed=analysis_data.get("expert_witnesses_needed", []),
                    confidence_score=analysis_data.get("confidence_score", 0.5),
                    timestamp=datetime.now().isoformat()
                )

                print(f"✅ Defense analysis complete (confidence: {analysis.confidence_score:.2f})")
                return analysis

            except json.JSONDecodeError:
                # Fallback: Return response as defense_strategy
                print(f"⚠️  Could not parse JSON response, returning raw analysis")
                analysis = DefenseAnalysis(
                    defendant_name=defendant_name,
                    charges=charges,
                    defense_theory="Mental health defense recommended",
                    applicable_law=["Florida Statutes § 775.027", "Florida Statutes § 916"],
                    relevant_cases=[case.to_dict() for case in insanity_cases],
                    defense_strategy=response_text,
                    strengths=[],
                    weaknesses=[],
                    recommended_actions=["Retain forensic psychiatrist", "File competency motion"],
                    expert_witnesses_needed=["Forensic psychiatrist"],
                    confidence_score=0.5,
                    timestamp=datetime.now().isoformat()
                )
                return analysis

        except Exception as e:
            print(f"❌ LLM analysis error: {e}")
            # Return fallback analysis
            analysis = DefenseAnalysis(
                defendant_name=defendant_name,
                charges=charges,
                defense_theory="Mental health defense recommended (analysis incomplete)",
                applicable_law=["Florida Statutes § 775.027", "Florida Statutes § 916"],
                relevant_cases=[case.to_dict() for case in insanity_cases],
                defense_strategy="Error during analysis. Consult with forensic psychiatrist and review Florida insanity defense case law.",
                strengths=[],
                weaknesses=[],
                recommended_actions=["Retain forensic psychiatrist", "Review mental health records", "File competency motion"],
                expert_witnesses_needed=["Forensic psychiatrist", "Treating psychiatrist"],
                confidence_score=0.0,
                timestamp=datetime.now().isoformat()
            )
            return analysis

    def evaluate_competency(
        self,
        defendant_name: str,
        mental_health_history: str,
        observations: str
    ) -> CompetencyEvaluation:
        """
        Evaluate competency to stand trial under Florida Statutes § 916.

        This is a preliminary evaluation to determine if a formal competency motion should be filed.
        """
        evaluation_prompt = f"""Evaluate competency to stand trial for this defendant:

**Defendant:** {defendant_name}

**Mental Health History:**
{mental_health_history}

**Observations (Attorney's notes):**
{observations}

**Legal Standard (Florida Statutes § 916):**
A defendant is competent to stand trial if they have:
1. Sufficient present ability to consult with their lawyer with a reasonable degree of rational understanding
2. A rational as well as factual understanding of the proceedings against them

**Your Task:**
Based on the information provided, provide a preliminary competency evaluation:

1. Does the defendant appear to understand the charges against them?
2. Does the defendant appear to understand the court proceedings?
3. Can the defendant assist their attorney in preparing a defense?
4. What is your opinion on competency? (competent / incompetent / evaluation_needed)
5. What actions should the defense attorney take?

Respond with clear yes/no answers and brief explanations.
"""

        try:
            response = litellm.completion(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": evaluation_prompt}
                ],
                api_base=self.ollama_base_url,
                max_tokens=2000,
                temperature=0.3
            )

            evaluation_text = response.choices[0].message.content

            # Parse response (simple heuristic-based parsing)
            understands_charges = "yes" in evaluation_text.lower() and "understand" in evaluation_text.lower() and "charges" in evaluation_text.lower()
            understands_proceedings = "yes" in evaluation_text.lower() and "proceedings" in evaluation_text.lower()
            can_assist = "yes" in evaluation_text.lower() and "assist" in evaluation_text.lower()

            # Determine competency opinion
            if "incompetent" in evaluation_text.lower():
                opinion = "incompetent"
            elif "competent" in evaluation_text.lower() and "incompetent" not in evaluation_text.lower():
                opinion = "competent"
            else:
                opinion = "restoration_recommended"

            evaluation = CompetencyEvaluation(
                defendant_name=defendant_name,
                evaluation_date=datetime.now().strftime("%Y-%m-%d"),
                understands_charges=understands_charges,
                understands_proceedings=understands_proceedings,
                can_assist_counsel=can_assist,
                mental_health_history=mental_health_history,
                competency_opinion=opinion,
                florida_statute_cite="Florida Statutes § 916.12",
                recommended_actions=[
                    "File motion for competency evaluation (FL Rule Crim. Pro. 3.210)",
                    "Request appointment of forensic psychiatrist",
                    "Suspend all proceedings pending competency determination"
                ],
                timestamp=datetime.now().isoformat()
            )

            print(f"✅ Competency evaluation complete: {opinion}")
            return evaluation

        except Exception as e:
            print(f"❌ Error during competency evaluation: {e}")
            # Return default evaluation recommending formal assessment
            return CompetencyEvaluation(
                defendant_name=defendant_name,
                evaluation_date=datetime.now().strftime("%Y-%m-%d"),
                understands_charges=False,
                understands_proceedings=False,
                can_assist_counsel=False,
                mental_health_history=mental_health_history,
                competency_opinion="restoration_recommended",
                florida_statute_cite="Florida Statutes § 916.12",
                recommended_actions=[
                    "File motion for competency evaluation immediately",
                    "Retain forensic psychiatrist for evaluation",
                    "Request suspension of proceedings"
                ],
                timestamp=datetime.now().isoformat()
            )

    def get_status(self) -> Dict[str, Any]:
        """Get attorney status and capabilities"""
        return {
            "name": self.name,
            "specializations": self.specializations,
            "tools": {
                "case_law_search": "CourtListener API (Florida courts)",
                "llm_reasoning": "DeepSeek-R1 14B (local)",
                "defense_analysis": "Mental health-based defense strategies",
                "competency_evaluation": "Florida Statutes § 916 competency assessments"
            },
            "capabilities": [
                "Temporary insanity defense analysis",
                "Competency to stand trial evaluation",
                "Mental health mitigation strategy",
                "Post-trial release arguments",
                "Expert witness identification"
            ],
            "focus_case": {
                "defendant": "Steffan Haskins",
                "location": "Orlando, Florida",
                "defense_theory": "Temporary insanity / mental health defense"
            },
            "status": "active"
        }


# Singleton instance
_attorney = None


def get_criminal_defense_attorney() -> CriminalDefenseAttorney:
    """Get singleton Criminal Defense Attorney"""
    global _attorney
    if _attorney is None:
        _attorney = CriminalDefenseAttorney()
    return _attorney


# CLI for testing
if __name__ == "__main__":
    print("=" * 70)
    print("UNITY LAW OFFICE — CRIMINAL DEFENSE ATTORNEY")
    print("=" * 70)
    print()

    attorney = get_criminal_defense_attorney()

    # Display status
    status = attorney.get_status()
    print(f"Attorney: {status['name']}")
    print(f"\nSpecializations:")
    for spec in status['specializations']:
        print(f"  - {spec}")

    print(f"\n🧪 Running test case analysis (Steffan Haskins)...\n")

    # Test case: Steffan Haskins - temporary insanity defense
    analysis = attorney.analyze_defense_case(
        defendant_name="Steffan Haskins",
        charges=["Battery", "Resisting Arrest"],
        facts="""
        Defendant was experiencing an acute mental health crisis at the time of the alleged offense.
        Medical records indicate a history of bipolar disorder with psychotic features.
        Witnesses report defendant was incoherent and exhibited behavior inconsistent with his baseline mental state.
        Defendant has no prior criminal history and has been compliant with mental health treatment when stable.
        """,
        mental_health_history="""
        Diagnosed with Bipolar I Disorder, age 24.
        Multiple psychiatric hospitalizations for manic episodes with psychotic features.
        Medications: Lithium, Quetiapine (compliance issues documented).
        History of auditory hallucinations during acute episodes.
        No history of violence when properly medicated.
        """
    )

    print("\n" + "=" * 70)
    print("DEFENSE ANALYSIS RESULTS")
    print("=" * 70)
    print(f"\n👤 Defendant: {analysis.defendant_name}")
    print(f"\n📋 Charges:")
    for charge in analysis.charges:
        print(f"  - {charge}")

    print(f"\n🎯 Defense Theory: {analysis.defense_theory}")

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

    print(f"\n👨‍⚕️ Expert Witnesses Needed:")
    for expert in analysis.expert_witnesses_needed:
        print(f"  - {expert}")

    print(f"\n🎯 Confidence Score: {analysis.confidence_score:.2f}")

    print("\n" + "=" * 70)
    print("✅ Criminal Defense Attorney Ready")
    print("=" * 70)
