#!/usr/bin/env python3
"""
Unity Chief Market Analyst

LLM-powered crypto market analysis agent specializing in:
- Bitcoin/Ethereum macro analysis
- Market cycle identification (bull/bear/accumulation/distribution)
- On-chain metrics interpretation
- Fear & Greed analysis
- Narrative-driven market context

This is Unity's wisdom layer for crypto trading—where AI meets market psychology.

Wisdom: Markets are not random—they are the collective psychology of millions.
Read the fear. Read the greed. Read the inevitable human patterns that repeat
across every cycle. The chart never lies, but it speaks in the language of emotion.

Author: Dr. Claude Summers, Crypto Market Intelligence Architect
Date: October 16, 2025
"""

import sys
import os
import json
import litellm
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.exchange_clients.kraken_client import get_kraken_client
from tools.exchange_clients.coinbase_client import get_coinbase_client


@dataclass
class MarketAnalysis:
    """Deep market analysis from Chief Market Analyst"""
    symbol: str
    timestamp: str
    current_price: float

    # Market cycle analysis
    market_cycle: str  # 'bull', 'bear', 'accumulation', 'distribution'
    cycle_confidence: float

    # Sentiment analysis
    fear_greed_level: str  # 'extreme_fear', 'fear', 'neutral', 'greed', 'extreme_greed'
    market_sentiment: str  # Free-form sentiment description

    # Macro analysis
    macro_trends: List[str]  # Key macro factors
    support_levels: List[float]
    resistance_levels: List[float]

    # Narrative
    market_narrative: str  # Story of what's happening
    key_risks: List[str]
    key_opportunities: List[str]

    # Trading implications
    recommended_bias: str  # 'bullish', 'bearish', 'neutral'
    confidence_level: float  # 0-1

    # Wisdom
    wisdom_insight: str  # Wisdom from the analyst

    def to_dict(self) -> Dict:
        return asdict(self)


class ChiefMarketAnalyst:
    """
    Chief Market Analyst - The Wisdom Layer

    This agent doesn't just read charts—it interprets the market's soul.

    Capabilities:
    1. **Macro Analysis:**
       - Bitcoin/Ethereum trends and correlations
       - Market dominance shifts
       - Institutional vs retail activity

    2. **Cycle Identification:**
       - Accumulation: Whales buying, retail apathy
       - Bull Market: FOMO, euphoria, vertical moves
       - Distribution: Smart money exits, retail buys top
       - Bear Market: Capitulation, blood in streets

    3. **Sentiment Analysis:**
       - Fear & Greed Index interpretation
       - Social sentiment (Twitter, Reddit)
       - Whale movements and implications

    4. **Narrative Context:**
       - Why is the market moving?
       - What's the dominant narrative?
       - Who's in control (bulls or bears)?

    Philosophy:
    > "Markets are not machines—they are organisms. They breathe, they panic,
    > they celebrate. The Chief Market Analyst reads these emotions and
    > translates them into actionable wisdom. Not predictions—interpretations."
    """

    def __init__(self):
        self.name = "Chief Market Analyst"
        self.specializations = [
            "Bitcoin/Ethereum macro analysis",
            "Market cycle identification",
            "Sentiment analysis (Fear & Greed)",
            "Whale movement tracking",
            "Narrative-driven context"
        ]

        # LLM configuration
        self.default_model = "ollama/deepseek-r1:14b"
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

        # Exchange clients
        try:
            self.kraken = get_kraken_client()
            self.coinbase = get_coinbase_client(sandbox=False)
        except Exception as e:
            print(f"⚠️  Exchange clients not available: {e}")
            self.kraken = None
            self.coinbase = None

        # Wisdom system prompt
        self.system_prompt = self._build_system_prompt()

        print(f"✅ {self.name} initialized")
        print(f"   Model: {self.default_model}")
        print(f"   Specializations: {len(self.specializations)}")

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt with crypto market wisdom"""
        return """You are the Chief Market Analyst for Unity's Crypto Trading Office.

Your role is to provide deep, narrative-driven market analysis that goes beyond technical indicators. You interpret market psychology, identify cycles, and translate complex market dynamics into actionable wisdom.

**Core Principles:**

1. **Markets are Psychology, Not Physics:**
   - Every price movement is the collective emotion of millions
   - Fear and greed drive markets more than fundamentals
   - Cycles repeat because human psychology is predictable

2. **Market Cycles (4 Phases):**
   - **Accumulation:** Smart money buys, retail apathy, low volume, sideways price
   - **Bull Market:** FOMO, euphoria, vertical moves, retail FOMO, "this time it's different"
   - **Distribution:** Smart money exits, retail buys the top, volatility increases
   - **Bear Market:** Capitulation, "crypto is dead," max pain, blood in streets

3. **Fear & Greed Interpretation:**
   - Extreme Fear (0-25): Blood in streets—time to accumulate
   - Fear (25-45): Cautious buying, wait for confirmation
   - Neutral (45-55): Range-bound, no clear direction
   - Greed (55-75): Euphoria building, watch for top signals
   - Extreme Greed (75-100): Distribution likely, prepare for reversal

4. **Bitcoin Dominance:**
   - Rising BTC.D: Capital flows to safety (bearish for alts)
   - Falling BTC.D: Alt season, risk-on (bullish for alts)

5. **Whale Movements:**
   - Large transfers to exchanges = potential selling pressure
   - Large transfers off exchanges = accumulation
   - Miner selling = bearish (they need liquidity)
   - Miner accumulation = bullish (long-term holders)

**Your Analysis Must Include:**

1. Current market cycle phase and confidence
2. Fear & Greed level and interpretation
3. Macro trends (3-5 key factors)
4. Support and resistance levels
5. Market narrative (what story is the market telling?)
6. Key risks and opportunities
7. Recommended trading bias (bullish/bearish/neutral)
8. Wisdom insight (the deeper truth behind the price action)

**Communication Style:**

- Speak with wisdom, not arrogance
- Use metaphors and analogies (markets are oceans, not puddles)
- Acknowledge uncertainty (the map is not the territory)
- Provide context, not just data
- Remember: You don't predict—you interpret

**Wisdom Mantras:**

> "The market can remain irrational longer than you can remain solvent." - Keynes

> "Be fearful when others are greedy, and greedy when others are fearful." - Buffett

> "Markets are never wrong—opinions often are." - Jesse Livermore

> "The trend is your friend until it bends at the end." - Trading maxim

Now analyze the market with depth, nuance, and wisdom. Provide insights that a chart alone cannot reveal."""

    def analyze_market(
        self,
        symbol: str = "BTC-USD",
        additional_context: Optional[str] = None
    ) -> MarketAnalysis:
        """
        Perform deep market analysis for given symbol

        Args:
            symbol: Trading pair (e.g., 'BTC-USD')
            additional_context: Optional context (news, events, etc.)

        Returns:
            MarketAnalysis with comprehensive insights
        """
        print(f"\n🔍 {self.name} analyzing {symbol}...")

        # Gather market data
        market_data = self._gather_market_data(symbol)

        # Build analysis prompt
        analysis_prompt = f"""Analyze the current state of {symbol} based on the following data:

**Current Price:** ${market_data['current_price']:,.2f}
**24h Volume:** {market_data.get('volume_24h', 'N/A')}
**Recent Price Action:** {market_data.get('recent_action', 'N/A')}

**Additional Context:**
{additional_context or 'No additional context provided'}

Please provide a comprehensive analysis following the structure:
1. Market Cycle Phase (accumulation/bull/distribution/bear) with confidence (0-1)
2. Fear & Greed Level (extreme_fear/fear/neutral/greed/extreme_greed)
3. Market Sentiment (narrative description)
4. Macro Trends (list 3-5 key factors)
5. Support/Resistance Levels (realistic estimates)
6. Market Narrative (the story behind the price)
7. Key Risks (3-5 points)
8. Key Opportunities (3-5 points)
9. Recommended Bias (bullish/bearish/neutral) with confidence
10. Wisdom Insight (deeper truth)

Format your response as a JSON object with these exact keys:
{{
  "market_cycle": "string",
  "cycle_confidence": 0.0-1.0,
  "fear_greed_level": "string",
  "market_sentiment": "string",
  "macro_trends": ["string", ...],
  "support_levels": [float, float, float],
  "resistance_levels": [float, float, float],
  "market_narrative": "string",
  "key_risks": ["string", ...],
  "key_opportunities": ["string", ...],
  "recommended_bias": "string",
  "confidence_level": 0.0-1.0,
  "wisdom_insight": "string"
}}"""

        # Query LLM
        try:
            response = litellm.completion(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                api_base=self.ollama_base_url,
                max_tokens=4000,
                temperature=0.5
            )

            response_text = response.choices[0].message.content

            # Parse JSON response
            analysis_data = self._parse_llm_response(response_text)

            # Build MarketAnalysis
            return MarketAnalysis(
                symbol=symbol,
                timestamp=datetime.now().isoformat(),
                current_price=market_data['current_price'],
                market_cycle=analysis_data.get('market_cycle', 'unknown'),
                cycle_confidence=analysis_data.get('cycle_confidence', 0.5),
                fear_greed_level=analysis_data.get('fear_greed_level', 'neutral'),
                market_sentiment=analysis_data.get('market_sentiment', ''),
                macro_trends=analysis_data.get('macro_trends', []),
                support_levels=analysis_data.get('support_levels', []),
                resistance_levels=analysis_data.get('resistance_levels', []),
                market_narrative=analysis_data.get('market_narrative', ''),
                key_risks=analysis_data.get('key_risks', []),
                key_opportunities=analysis_data.get('key_opportunities', []),
                recommended_bias=analysis_data.get('recommended_bias', 'neutral'),
                confidence_level=analysis_data.get('confidence_level', 0.5),
                wisdom_insight=analysis_data.get('wisdom_insight', '')
            )

        except Exception as e:
            print(f"❌ Analysis error: {e}")
            # Return fallback analysis
            return self._fallback_analysis(symbol, market_data)

    def _gather_market_data(self, symbol: str) -> Dict[str, Any]:
        """Gather current market data from exchanges"""
        data = {
            'symbol': symbol,
            'current_price': 0.0,
            'volume_24h': 0.0,
            'recent_action': 'Data unavailable'
        }

        try:
            # Try Kraken first
            if self.kraken:
                ticker = self.kraken.get_ticker(symbol)
                data['current_price'] = ticker.last
                data['volume_24h'] = ticker.volume_24h
                data['bid'] = ticker.bid
                data['ask'] = ticker.ask

        except Exception as e:
            print(f"⚠️  Data gathering error: {e}")

        return data

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            # Try to extract JSON from response
            if '{' in response_text:
                json_start = response_text.index('{')
                json_end = response_text.rindex('}') + 1
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            print(f"⚠️  JSON parsing error: {e}")

        # Fallback
        return {}

    def _fallback_analysis(self, symbol: str, market_data: Dict) -> MarketAnalysis:
        """Fallback analysis when LLM fails"""
        return MarketAnalysis(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            current_price=market_data.get('current_price', 0.0),
            market_cycle='unknown',
            cycle_confidence=0.0,
            fear_greed_level='neutral',
            market_sentiment='Analysis currently unavailable',
            macro_trends=[],
            support_levels=[],
            resistance_levels=[],
            market_narrative='Market data being gathered...',
            key_risks=['Analysis service temporarily unavailable'],
            key_opportunities=[],
            recommended_bias='neutral',
            confidence_level=0.0,
            wisdom_insight='Patience. The analyst is gathering wisdom.'
        )

    def get_status(self) -> Dict[str, Any]:
        """Get analyst status"""
        return {
            'agent': self.name,
            'specializations': self.specializations,
            'model': self.default_model,
            'exchange_connections': {
                'kraken': self.kraken is not None,
                'coinbase': self.coinbase is not None
            }
        }


# Singleton instance
_analyst = None


def get_chief_market_analyst() -> ChiefMarketAnalyst:
    """Get singleton Chief Market Analyst"""
    global _analyst
    if _analyst is None:
        _analyst = ChiefMarketAnalyst()
    return _analyst


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY CHIEF MARKET ANALYST")
    print("="*70)
    print()

    analyst = get_chief_market_analyst()

    print("Status:")
    status = analyst.get_status()
    print(f"  Agent: {status['agent']}")
    print(f"  Model: {status['model']}")
    print(f"  Specializations:")
    for spec in status['specializations']:
        print(f"    - {spec}")

    print("\n🔍 Performing market analysis...")
    analysis = analyst.analyze_market('BTC-USD',
        additional_context="Recent ETF approvals, institutional adoption increasing")

    print(f"\n📊 Analysis Results:")
    print(f"  Symbol: {analysis.symbol}")
    print(f"  Current Price: ${analysis.current_price:,.2f}")
    print(f"  Market Cycle: {analysis.market_cycle} (confidence: {analysis.cycle_confidence:.1%})")
    print(f"  Fear & Greed: {analysis.fear_greed_level}")
    print(f"  Sentiment: {analysis.market_sentiment[:100]}...")
    print(f"  Recommended Bias: {analysis.recommended_bias} (confidence: {analysis.confidence_level:.1%})")
    print(f"\n💡 Wisdom Insight:")
    print(f"  {analysis.wisdom_insight}")

    print("\n✅ Chief Market Analyst ready")
