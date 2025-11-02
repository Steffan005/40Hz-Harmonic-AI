#!/usr/bin/env python3
"""
Unity Sentiment Analyst - The Social Intelligence Specialist

Social media sentiment analysis agent that monitors:
- Twitter/X crypto sentiment (bullish/bearish ratio)
- Discord community health (engagement, toxicity)
- Reddit discussion volume (r/cryptocurrency, r/bitcoin, etc.)
- Telegram group activity
- Fear & Greed Index
- Google Trends (search volume spikes)

Philosophy: "Markets are made of people, and people have emotions. Fear and greed
drive 90% of market moves. The analyst reads the crowd's psychology—not to follow
it, but to exploit it. When everyone is fearful, be greedy. When everyone is greedy,
be fearful. Social sentiment is a contrarian indicator."

This agent uses NLP to analyze social media sentiment and provide intelligence
on crowd psychology.

Author: Dr. Claude Summers, Social Intelligence Architect
Date: October 16, 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import time
import json
import random

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class SocialSentiment:
    """Social media sentiment snapshot"""
    platform: str  # 'twitter', 'reddit', 'discord', 'telegram'
    token: str
    timestamp: str

    # Sentiment metrics
    total_mentions: int
    bullish_mentions: int
    bearish_mentions: int
    neutral_mentions: int

    # Sentiment score (-100 to +100)
    sentiment_score: float

    # Engagement
    avg_engagement: float  # likes, retweets, replies per post
    influencer_mentions: int  # mentions by accounts with >10k followers

    # Trending
    mention_change_24h_pct: float
    is_trending: bool

    # Classification
    overall_sentiment: str  # 'extremely_bullish', 'bullish', 'neutral', 'bearish', 'extremely_bearish'


@dataclass
class FearGreedIndex:
    """Crypto Fear & Greed Index snapshot"""
    timestamp: str
    index_value: int  # 0-100
    classification: str  # 'extreme_fear', 'fear', 'neutral', 'greed', 'extreme_greed'

    # Components (what drives the index)
    volatility_score: int
    market_momentum_score: int
    social_media_score: int
    dominance_score: int  # Bitcoin dominance
    trends_score: int  # Google Trends

    # Interpretation
    contrarian_signal: str  # 'buy', 'sell', 'hold'
    confidence: float
    reasons: List[str]
    wisdom_insight: str


@dataclass
class TrendingTopic:
    """Trending crypto topic on social media"""
    topic: str
    platform: str
    timestamp: str

    # Metrics
    mentions_24h: int
    mention_growth_pct: float
    peak_hour: str

    # Related tokens
    related_tokens: List[str]

    # Sentiment
    overall_sentiment: str
    sentiment_score: float

    # Classification
    trend_type: str  # 'organic', 'coordinated', 'bot_driven'
    authenticity_score: float  # 0-1 (1 = genuine, 0 = bot farm)

    # Actionable
    actionable: bool
    reasons: List[str]


@dataclass
class CommunityHealth:
    """Discord/Telegram community health analysis"""
    community_name: str
    platform: str
    token: str
    timestamp: str

    # Size metrics
    total_members: int
    active_members_24h: int
    new_members_7d: int
    member_growth_rate_pct: float

    # Engagement
    messages_per_day: int
    avg_response_time_minutes: float

    # Sentiment
    toxicity_score: float  # 0-1 (0 = healthy, 1 = toxic)
    spam_score: float  # 0-1 (0 = clean, 1 = spam)
    overall_sentiment: str

    # Health score (0-100)
    health_score: float

    # Classification
    community_type: str  # 'organic', 'cult', 'paid_shills', 'dead'
    red_flags: List[str]
    green_flags: List[str]

    wisdom_insight: str


class SentimentAnalyst:
    """
    Sentiment Analyst - The Social Intelligence Specialist

    Philosophy:
    "Markets are emotional. When Bitcoin pumps, Twitter erupts with laser eyes
    and moon emojis. When it dumps, the timeline fills with despair and capitulation.

    The analyst reads this emotion—not to follow the crowd, but to fade it:

    Contrarian Wisdom:
    - Extreme greed (>80 index) = tops form here, prepare to sell
    - Extreme fear (<20 index) = bottoms form here, time to buy
    - Everyone bullish = distribution phase, whales selling to retail
    - Everyone bearish = accumulation phase, whales buying from weak hands

    Social Media Truth:
    - Organic trends = genuine interest, potential opportunity
    - Bot-driven trends = pump & dump, avoid
    - Influencer shilling = paid promotion, red flag
    - Community toxicity = project problems, warning

    The analyst does not follow the crowd. The analyst exploits the crowd's
    psychology for profit."

    Key Metrics:
    1. Fear & Greed Index (0-100)
       - <25 = Extreme Fear → BUY signal
       - 25-45 = Fear → Accumulate
       - 45-55 = Neutral → Hold
       - 55-75 = Greed → Caution
       - >75 = Extreme Greed → SELL signal

    2. Social Sentiment Score (-100 to +100)
       - <-50 = Extremely bearish (contrarian BUY)
       - -50 to -20 = Bearish (accumulate)
       - -20 to +20 = Neutral (hold)
       - +20 to +50 = Bullish (take profit)
       - >+50 = Extremely bullish (contrarian SELL)

    3. Community Health Score (0-100)
       - <30 = Toxic/dead, avoid
       - 30-50 = Concerning, monitor
       - 50-70 = Healthy, safe
       - >70 = Thriving, bullish

    Data Sources (simulated for demo, real integration requires API keys):
    - Twitter API v2
    - Reddit API (PRAW)
    - Discord webhooks
    - Alternative.me Fear & Greed API (free)
    - LunarCrush (social metrics)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "Sentiment Analyst"

        # Configuration
        self.config = config or {
            'contrarian_mode': True,  # Fade extreme sentiment
            'min_authenticity_score': 0.6,  # Filter bot-driven trends
            'alert_on_extreme_sentiment': True,
            'sentiment_update_interval_seconds': 600  # 10 minutes
        }

        print(f"📊 Initializing {self.name}...")

        # Historical data storage
        self.sentiment_history = []
        self.history_file = Path(__file__).parent.parent.parent / "logs" / "crypto" / "sentiment_history.json"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"✅ {self.name} initialized")
        print(f"   Contrarian mode: {'enabled' if self.config['contrarian_mode'] else 'disabled'}")
        print(f"   Monitoring: Twitter, Reddit, Discord, Fear & Greed Index")

    def get_fear_greed_index(self) -> FearGreedIndex:
        """
        Get current Crypto Fear & Greed Index

        In production, would query alternative.me API:
        https://api.alternative.me/fng/
        """
        print(f"\n📊 Fetching Fear & Greed Index...")

        # Simulate index value (0-100)
        # In real version, fetch from API
        index_value = random.randint(15, 85)

        # Classify
        if index_value < 25:
            classification = 'extreme_fear'
            contrarian_signal = 'buy'
            confidence = 0.85
            reasons = [
                'Extreme fear = market bottom forming',
                'Retail capitulating, whales accumulating',
                'Best buying opportunities occur here',
                'History shows this is entry zone'
            ]
            wisdom = "Extreme fear is the best time to buy. When blood is in the streets, be greedy."

        elif index_value < 45:
            classification = 'fear'
            contrarian_signal = 'buy'
            confidence = 0.65
            reasons = [
                'Fear phase = accumulation opportunity',
                'Market sentiment oversold',
                'Risk/reward favors buyers'
            ]
            wisdom = "Fear is rational in bear markets—but also presents opportunity for the patient."

        elif index_value < 55:
            classification = 'neutral'
            contrarian_signal = 'hold'
            confidence = 0.5
            reasons = [
                'Neutral sentiment = no strong signal',
                'Market in equilibrium',
                'Wait for clearer trend'
            ]
            wisdom = "Neutral markets are boring—but boring is often profitable for holders."

        elif index_value < 75:
            classification = 'greed'
            contrarian_signal = 'sell'
            confidence = 0.65
            reasons = [
                'Greed phase = distribution starting',
                'Smart money taking profits',
                'Risk increasing as retail FOMOs in',
                'Consider reducing exposure'
            ]
            wisdom = "Greed is when you should be cautious. Take profits before the crowd realizes the top."

        else:
            classification = 'extreme_greed'
            contrarian_signal = 'sell'
            confidence = 0.85
            reasons = [
                'Extreme greed = market top forming',
                'Everyone is bullish = contrarian sell signal',
                'Retail euphoria peaks at tops',
                'Whales distributing to late buyers'
            ]
            wisdom = "Extreme greed marks tops. When your Uber driver gives you crypto tips, it's time to sell."

        index = FearGreedIndex(
            timestamp=datetime.now().isoformat(),
            index_value=index_value,
            classification=classification,
            volatility_score=random.randint(0, 100),
            market_momentum_score=random.randint(0, 100),
            social_media_score=random.randint(0, 100),
            dominance_score=random.randint(0, 100),
            trends_score=random.randint(0, 100),
            contrarian_signal=contrarian_signal,
            confidence=confidence,
            reasons=reasons,
            wisdom_insight=wisdom
        )

        print(f"   Index: {index_value}/100")
        print(f"   Classification: {classification.upper()}")
        print(f"   Contrarian signal: {contrarian_signal.upper()}")
        print(f"   Wisdom: {wisdom}")

        return index

    def analyze_social_sentiment(
        self,
        token: str,
        platform: str = 'twitter'
    ) -> SocialSentiment:
        """
        Analyze social media sentiment for a token

        In production, would use Twitter API, Reddit API, etc.
        """
        print(f"\n📊 Analyzing {platform} sentiment for {token}...")

        # Simulate social data
        total_mentions = random.randint(1000, 50000)
        bullish_ratio = random.uniform(0.2, 0.8)

        bullish = int(total_mentions * bullish_ratio)
        bearish = int(total_mentions * (0.3 * (1 - bullish_ratio)))
        neutral = total_mentions - bullish - bearish

        # Calculate sentiment score (-100 to +100)
        sentiment_score = ((bullish - bearish) / total_mentions) * 100

        # Classify
        if sentiment_score > 50:
            overall = 'extremely_bullish'
        elif sentiment_score > 20:
            overall = 'bullish'
        elif sentiment_score > -20:
            overall = 'neutral'
        elif sentiment_score > -50:
            overall = 'bearish'
        else:
            overall = 'extremely_bearish'

        sentiment = SocialSentiment(
            platform=platform,
            token=token,
            timestamp=datetime.now().isoformat(),
            total_mentions=total_mentions,
            bullish_mentions=bullish,
            bearish_mentions=bearish,
            neutral_mentions=neutral,
            sentiment_score=sentiment_score,
            avg_engagement=random.uniform(10, 500),
            influencer_mentions=random.randint(0, 20),
            mention_change_24h_pct=random.uniform(-50, 200),
            is_trending=sentiment_score > 30 or total_mentions > 30000,
            overall_sentiment=overall
        )

        print(f"   Mentions: {total_mentions:,}")
        print(f"   Bullish: {bullish:,} | Bearish: {bearish:,}")
        print(f"   Sentiment score: {sentiment_score:.1f}")
        print(f"   Overall: {overall.upper()}")

        return sentiment

    def detect_trending_topics(
        self,
        platform: str = 'twitter'
    ) -> List[TrendingTopic]:
        """
        Detect trending crypto topics

        Filter out bot-driven pump campaigns
        """
        print(f"\n📊 Detecting trending topics on {platform}...")

        # Simulate trending topics
        topics = [
            {
                'topic': '#Bitcoin',
                'mentions': 150000,
                'growth': 25.5,
                'tokens': ['BTC'],
                'sentiment_score': 35.2,
                'authenticity': 0.95  # Organic
            },
            {
                'topic': '#AltcoinSeason',
                'mentions': 85000,
                'growth': 180.3,
                'tokens': ['ETH', 'SOL', 'MATIC'],
                'sentiment_score': 62.5,
                'authenticity': 0.72  # Some bot activity
            },
            {
                'topic': '#MemeCoin',
                'mentions': 200000,
                'growth': 450.8,
                'tokens': ['DOGE', 'SHIB', 'PEPE'],
                'sentiment_score': 88.9,
                'authenticity': 0.35  # Likely coordinated pump
            }
        ]

        trending_list = []

        for t in topics:
            # Determine trend type
            if t['authenticity'] > 0.8:
                trend_type = 'organic'
                actionable = True
                reasons = [
                    'High authenticity score (>0.8)',
                    'Genuine community interest',
                    'Potential real catalyst'
                ]
            elif t['authenticity'] > 0.6:
                trend_type = 'coordinated'
                actionable = True if t['sentiment_score'] < 70 else False
                reasons = [
                    'Moderate authenticity (0.6-0.8)',
                    'Some coordinated activity detected',
                    'Monitor before acting' if actionable else 'Likely pump campaign'
                ]
            else:
                trend_type = 'bot_driven'
                actionable = False
                reasons = [
                    'Low authenticity (<0.6)',
                    'Bot farm detected',
                    'Pump & dump warning—avoid'
                ]

            # Sentiment classification
            if t['sentiment_score'] > 70:
                overall_sentiment = 'extremely_bullish'
            elif t['sentiment_score'] > 40:
                overall_sentiment = 'bullish'
            else:
                overall_sentiment = 'neutral'

            topic = TrendingTopic(
                topic=t['topic'],
                platform=platform,
                timestamp=datetime.now().isoformat(),
                mentions_24h=t['mentions'],
                mention_growth_pct=t['growth'],
                peak_hour='14:00 UTC',
                related_tokens=t['tokens'],
                overall_sentiment=overall_sentiment,
                sentiment_score=t['sentiment_score'],
                trend_type=trend_type,
                authenticity_score=t['authenticity'],
                actionable=actionable,
                reasons=reasons
            )

            trending_list.append(topic)

            print(f"\n   Topic: {t['topic']}")
            print(f"   Mentions: {t['mentions']:,} (+{t['growth']:.1f}%)")
            print(f"   Authenticity: {t['authenticity']:.2f}")
            print(f"   Type: {trend_type}")
            print(f"   Actionable: {'YES' if actionable else 'NO'}")

        return trending_list

    def analyze_community_health(
        self,
        community_name: str,
        token: str,
        platform: str = 'discord'
    ) -> CommunityHealth:
        """
        Analyze Discord/Telegram community health

        Red flags: High toxicity, spam, paid shills
        Green flags: Organic growth, engagement, low toxicity
        """
        print(f"\n📊 Analyzing {community_name} community health...")

        # Simulate community data
        total_members = random.randint(5000, 100000)
        active_ratio = random.uniform(0.05, 0.25)
        active_24h = int(total_members * active_ratio)

        toxicity = random.uniform(0.1, 0.8)
        spam = random.uniform(0.05, 0.6)

        # Calculate health score
        health_score = 100 * (1 - toxicity) * (1 - spam) * (active_ratio * 4)
        health_score = min(100, max(0, health_score))

        # Classify
        if health_score > 70:
            community_type = 'organic'
            red_flags = []
            green_flags = [
                'High engagement',
                'Low toxicity',
                'Organic growth',
                'Active development discussion'
            ]
            wisdom = "Healthy community = strong project foundation. Good sign for long-term hold."

        elif health_score > 50:
            community_type = 'organic'
            red_flags = ['Moderate spam detected']
            green_flags = ['Decent engagement', 'Growing membership']
            wisdom = "Decent community health. Monitor for improvement or decline."

        elif health_score > 30:
            community_type = 'cult'
            red_flags = [
                'High toxicity toward critics',
                'Echo chamber behavior',
                'Cult-like devotion to token'
            ]
            green_flags = []
            wisdom = "Cult-like community is a red flag. Dissent is silenced—beware."

        else:
            community_type = 'paid_shills' if spam > 0.5 else 'dead'
            red_flags = [
                'Very high toxicity' if toxicity > 0.6 else 'Low engagement',
                'Spam/bot activity' if spam > 0.5 else 'Dead community',
                'Possible paid shills' if spam > 0.5 else 'Project likely abandoned'
            ]
            green_flags = []
            wisdom = "Toxic or dead community = avoid this project entirely."

        # Determine sentiment
        if toxicity < 0.3 and active_ratio > 0.15:
            overall_sentiment = 'positive'
        elif toxicity > 0.6 or active_ratio < 0.05:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'mixed'

        health = CommunityHealth(
            community_name=community_name,
            platform=platform,
            token=token,
            timestamp=datetime.now().isoformat(),
            total_members=total_members,
            active_members_24h=active_24h,
            new_members_7d=random.randint(100, 5000),
            member_growth_rate_pct=random.uniform(-5, 25),
            messages_per_day=random.randint(100, 10000),
            avg_response_time_minutes=random.uniform(2, 60),
            toxicity_score=toxicity,
            spam_score=spam,
            overall_sentiment=overall_sentiment,
            health_score=health_score,
            community_type=community_type,
            red_flags=red_flags,
            green_flags=green_flags,
            wisdom_insight=wisdom
        )

        print(f"   Members: {total_members:,}")
        print(f"   Active (24h): {active_24h:,} ({active_ratio*100:.1f}%)")
        print(f"   Toxicity: {toxicity:.2f}")
        print(f"   Spam: {spam:.2f}")
        print(f"   Health score: {health_score:.1f}/100")
        print(f"   Type: {community_type}")
        print(f"   Wisdom: {wisdom}")

        return health

    def get_status(self) -> Dict[str, Any]:
        """Get analyst status"""
        return {
            'agent': self.name,
            'philosophy': 'Markets are emotion—exploit fear and greed with contrarian wisdom',
            'platforms_monitored': ['Twitter', 'Reddit', 'Discord', 'Telegram'],
            'contrarian_mode': self.config['contrarian_mode'],
            'config': self.config,
            'wisdom': 'When everyone is fearful, be greedy. When everyone is greedy, be fearful. Social sentiment is a contrarian indicator.'
        }


# Singleton instance
_analyst = None


def get_sentiment_analyst() -> SentimentAnalyst:
    """Get singleton Sentiment Analyst"""
    global _analyst
    if _analyst is None:
        _analyst = SentimentAnalyst()
    return _analyst


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY SENTIMENT ANALYST - THE SOCIAL INTELLIGENCE SPECIALIST")
    print("="*70)
    print()

    analyst = get_sentiment_analyst()

    print("\nStatus:")
    status = analyst.get_status()
    for key, value in status.items():
        if key != 'wisdom':
            print(f"  {key}: {value}")

    print(f"\n💬 Wisdom: {status['wisdom']}")

    # Get Fear & Greed Index
    print("\n🌡️ FEAR & GREED INDEX:")
    print("="*70)
    fear_greed = analyst.get_fear_greed_index()

    # Analyze social sentiment
    print("\n\n📱 SOCIAL SENTIMENT ANALYSIS:")
    print("="*70)
    for token in ['BTC', 'ETH', 'SOL']:
        sentiment = analyst.analyze_social_sentiment(token, 'twitter')

    # Detect trending topics
    print("\n\n🔥 TRENDING TOPICS:")
    print("="*70)
    trending = analyst.detect_trending_topics('twitter')

    # Analyze community health
    print("\n\n👥 COMMUNITY HEALTH:")
    print("="*70)
    health1 = analyst.analyze_community_health('Bitcoin Maxis', 'BTC', 'discord')
    health2 = analyst.analyze_community_health('ShitCoin Moon', 'SHITCOIN', 'telegram')

    print("\n✅ Sentiment Analyst ready to read the crowd")
