#!/usr/bin/env python3
"""
Unity On-Chain Detective - The Blockchain Intelligence Specialist

Blockchain analysis agent that tracks:
- Whale wallet movements (large holders)
- Smart money flows (successful traders)
- Exchange inflows/outflows (accumulation vs distribution)
- Token holder concentration (decentralization metrics)
- Notable wallet addresses (VCs, institutions, founders)

Philosophy: "The blockchain never lies. Every transaction is recorded, immutable,
eternal. The detective reads the on-chain data like a book—and the book tells
the truth about who's buying, who's selling, and who's accumulating quietly
while retail panics."

This agent connects to blockchain explorers (Etherscan, Solscan, etc.) and
provides intelligence on smart money movements.

Author: Dr. Claude Summers, Blockchain Intelligence Architect
Date: October 16, 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import time
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class WalletActivity:
    """On-chain wallet activity"""
    wallet_address: str
    wallet_label: Optional[str]  # "Binance Hot Wallet", "Vitalik.eth", etc.
    wallet_type: str  # 'exchange', 'whale', 'smart_money', 'institution', 'unknown'

    # Activity
    transaction_hash: str
    timestamp: str
    action: str  # 'bought', 'sold', 'transferred'
    token: str
    amount: float
    amount_usd: float

    # Context
    from_address: str
    to_address: str
    gas_paid_eth: float

    # Significance
    significance: str  # 'high', 'medium', 'low'
    reasons: List[str]


@dataclass
class WhaleAlert:
    """Significant whale movement alert"""
    alert_id: str
    timestamp: str

    # Movement details
    token: str
    amount: float
    amount_usd: float
    from_wallet: str
    from_label: Optional[str]
    to_wallet: str
    to_label: Optional[str]

    # Classification
    movement_type: str  # 'accumulation', 'distribution', 'exchange_inflow', 'exchange_outflow', 'transfer'
    significance: str  # 'critical', 'high', 'medium'

    # Market context
    current_price_usd: float
    price_change_24h_pct: float

    # Interpretation
    bullish_bearish: str  # 'bullish', 'bearish', 'neutral'
    confidence: float
    reasons: List[str]

    wisdom_insight: str


@dataclass
class TokenHolderAnalysis:
    """Token holder concentration analysis"""
    token: str
    blockchain: str
    timestamp: str

    # Holder metrics
    total_holders: int
    top_10_holders_pct: float
    top_100_holders_pct: float

    # Exchange holdings
    exchange_holdings_pct: float
    known_exchanges: List[str]

    # Distribution score (0-100, higher = more decentralized)
    decentralization_score: float

    # Analysis
    concentration_level: str  # 'highly_concentrated', 'concentrated', 'distributed', 'highly_distributed'
    risks: List[str]
    opportunities: List[str]

    wisdom_insight: str


@dataclass
class SmartMoneyFlow:
    """Smart money accumulation/distribution tracking"""
    token: str
    timeframe: str  # '24h', '7d', '30d'
    timestamp: str

    # Flow metrics
    smart_money_inflow_usd: float
    smart_money_outflow_usd: float
    net_flow_usd: float

    # Whale activity
    whale_buyers: int
    whale_sellers: int
    net_whales: int  # buyers - sellers

    # Average transaction sizes
    avg_buy_size_usd: float
    avg_sell_size_usd: float

    # Sentiment
    smart_money_sentiment: str  # 'accumulating', 'distributing', 'neutral'
    confidence: float

    # Interpretation
    bullish_bearish: str
    reasons: List[str]
    wisdom_insight: str


class OnChainDetective:
    """
    On-Chain Detective - The Blockchain Intelligence Specialist

    Philosophy:
    "The blockchain is the ultimate source of truth. Unlike price charts,
    which can be manipulated by market makers, the blockchain records
    every transaction—immutable, permanent, undeniable.

    When a whale moves 10,000 BTC to Binance, the blockchain knows.
    When Vitalik sells ETH, the blockchain knows.
    When VCs quietly accumulate a new token, the blockchain knows.

    The detective reads these movements and interprets them:
    - Exchange inflows = potential selling pressure (bearish)
    - Exchange outflows = accumulation to cold storage (bullish)
    - Smart money buying = opportunity (bullish)
    - Smart money selling = warning (bearish)

    The detective does not trade on rumors. The detective trades on facts—
    facts written in code, broadcast to nodes, and confirmed by miners.

    This is intelligence. This is alpha."

    Key Concepts:
    1. Whale Wallets: Addresses holding >0.1% of token supply
    2. Smart Money: Wallets with proven profitable trading history
    3. Exchange Wallets: Known Binance, Coinbase, Kraken addresses
    4. Institutional Wallets: VCs, funds, company treasuries

    Data Sources (simulated for now, real integration requires API keys):
    - Etherscan API (Ethereum)
    - Solscan API (Solana)
    - BscScan API (Binance Smart Chain)
    - Whale Alert API
    - Nansen (paid service for smart money tracking)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "On-Chain Detective"

        # Configuration
        self.config = config or {
            'min_whale_threshold_usd': 100000,  # $100k minimum for whale status
            'smart_money_min_success_rate': 0.7,  # 70% profitable trades
            'alert_threshold_usd': 1000000,  # $1M+ transactions trigger alerts
            'update_interval_seconds': 300  # Check every 5 minutes
        }

        print(f"🔍 Initializing {self.name}...")

        # Known whale wallets (example addresses)
        self.known_whales = {
            'ethereum': [
                {
                    'address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
                    'label': 'Binance Hot Wallet',
                    'type': 'exchange'
                },
                {
                    'address': '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
                    'label': 'Vitalik.eth',
                    'type': 'whale'
                },
                {
                    'address': '0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503',
                    'label': 'Binance Cold Wallet',
                    'type': 'exchange'
                }
            ],
            'solana': [
                {
                    'address': '5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9',
                    'label': 'FTX Cold Wallet (defunct)',
                    'type': 'exchange'
                }
            ]
        }

        # Smart money wallets (proven profitable traders)
        self.smart_money_wallets = [
            {
                'address': '0xSmartTrader1',
                'label': 'Profitable DeFi Trader #1',
                'success_rate': 0.82,
                'total_profit_usd': 5000000
            },
            {
                'address': '0xSmartTrader2',
                'label': 'NFT Whale & Early Adopter',
                'success_rate': 0.75,
                'total_profit_usd': 8000000
            }
        ]

        # Recent alerts
        self.recent_alerts = []
        self.alerts_file = Path(__file__).parent.parent.parent / "logs" / "crypto" / "whale_alerts.json"
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"✅ {self.name} initialized")
        print(f"   Tracking {len(self.known_whales.get('ethereum', []))} Ethereum whales")
        print(f"   Tracking {len(self.smart_money_wallets)} smart money wallets")
        print(f"   Alert threshold: ${self.config['alert_threshold_usd']:,.0f}")

    def simulate_whale_movement(
        self,
        token: str,
        amount_usd: float,
        movement_type: str,
        blockchain: str = 'ethereum'
    ) -> WhaleAlert:
        """
        Simulate a whale movement (for demo purposes)

        In production, this would query Etherscan/Solscan APIs

        Args:
            token: Token symbol (BTC, ETH, SOL, etc.)
            amount_usd: Transaction value in USD
            movement_type: 'exchange_inflow', 'exchange_outflow', 'transfer'
            blockchain: 'ethereum', 'solana', 'bsc'
        """
        print(f"\n🔍 Simulating whale movement: {amount_usd:,.0f} USD {token}")

        # Select from/to based on movement type
        if movement_type == 'exchange_inflow':
            from_wallet = '0xWhale123...'
            from_label = 'Unknown Whale'
            to_wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'
            to_label = 'Binance Hot Wallet'
            bullish_bearish = 'bearish'
            reasons = [
                'Large transfer to exchange hot wallet',
                'Potential selling pressure incoming',
                'Whale may be preparing to sell'
            ]
            wisdom = "When whales move to exchanges, they often intend to sell. Watch for price impact."

        elif movement_type == 'exchange_outflow':
            from_wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'
            from_label = 'Binance Hot Wallet'
            to_wallet = '0xWhale456...'
            to_label = 'Unknown Whale'
            bullish_bearish = 'bullish'
            reasons = [
                'Large withdrawal from exchange to cold storage',
                'Accumulation behavior—holding long-term',
                'Reduced selling pressure on exchanges'
            ]
            wisdom = "When whales withdraw from exchanges, they're accumulating. This is bullish—they're not selling."

        else:  # transfer
            from_wallet = '0xWhale789...'
            from_label = 'Whale A'
            to_wallet = '0xWhale012...'
            to_label = 'Whale B'
            bullish_bearish = 'neutral'
            reasons = [
                'Whale-to-whale transfer',
                'No immediate market impact',
                'May be portfolio restructuring'
            ]
            wisdom = "Whale-to-whale transfers are often internal moves. Monitor for follow-up exchange deposits."

        # Calculate significance
        if amount_usd >= 10000000:
            significance = 'critical'
            confidence = 0.9
        elif amount_usd >= 1000000:
            significance = 'high'
            confidence = 0.75
        else:
            significance = 'medium'
            confidence = 0.6

        # Simulate current price context
        prices = {
            'BTC': 67500,
            'ETH': 3500,
            'SOL': 100,
            'MATIC': 0.75
        }
        current_price = prices.get(token, 100.0)

        alert = WhaleAlert(
            alert_id=f"whale_{token}_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            token=token,
            amount=amount_usd / current_price,
            amount_usd=amount_usd,
            from_wallet=from_wallet,
            from_label=from_label,
            to_wallet=to_wallet,
            to_label=to_label,
            movement_type=movement_type,
            significance=significance,
            current_price_usd=current_price,
            price_change_24h_pct=-2.5,  # Simulated
            bullish_bearish=bullish_bearish,
            confidence=confidence,
            reasons=reasons,
            wisdom_insight=wisdom
        )

        # Store alert
        self.recent_alerts.append(alert)
        self._save_alerts()

        print(f"   Movement: {movement_type}")
        print(f"   Amount: ${amount_usd:,.0f}")
        print(f"   Signal: {bullish_bearish.upper()}")
        print(f"   Wisdom: {wisdom}")

        return alert

    def analyze_token_holders(
        self,
        token: str,
        blockchain: str = 'ethereum'
    ) -> TokenHolderAnalysis:
        """
        Analyze token holder concentration

        In production, would query blockchain explorer APIs

        High concentration = risk (few holders control supply)
        Low concentration = decentralized (many holders)
        """
        print(f"\n🔍 Analyzing {token} holder distribution...")

        # Simulate holder data
        token_data = {
            'BTC': {
                'total_holders': 1000000,
                'top_10_pct': 5.2,
                'top_100_pct': 15.8,
                'exchange_pct': 12.5
            },
            'ETH': {
                'total_holders': 250000,
                'top_10_pct': 8.5,
                'top_100_pct': 25.2,
                'exchange_pct': 18.3
            },
            'SOL': {
                'total_holders': 150000,
                'top_10_pct': 12.8,
                'top_100_pct': 35.5,
                'exchange_pct': 22.1
            },
            'SHITCOIN': {
                'total_holders': 5000,
                'top_10_pct': 65.2,  # Highly concentrated!
                'top_100_pct': 88.5,
                'exchange_pct': 3.2
            }
        }

        data = token_data.get(token, token_data['ETH'])

        # Calculate decentralization score (0-100, higher = better)
        # Based on top holder concentration
        if data['top_10_pct'] < 5:
            decentral_score = 95
        elif data['top_10_pct'] < 10:
            decentral_score = 80
        elif data['top_10_pct'] < 20:
            decentral_score = 60
        elif data['top_10_pct'] < 40:
            decentral_score = 40
        else:
            decentral_score = 20

        # Concentration level
        if data['top_10_pct'] > 50:
            concentration = 'highly_concentrated'
            risks = [
                'Top 10 holders control >50% of supply',
                'High risk of coordinated sell-off',
                'Potential for market manipulation',
                'Low decentralization—avoid'
            ]
            opportunities = []
            wisdom = "When few wallets control most tokens, one whale can crash the price. This is a red flag."

        elif data['top_10_pct'] > 20:
            concentration = 'concentrated'
            risks = [
                'Top 10 holders have significant influence',
                'Moderate risk of large dumps',
                'Watch for insider selling'
            ]
            opportunities = [
                'If whales are accumulating, follow smart money'
            ]
            wisdom = "Moderate concentration is common. Monitor whale movements for early exit signals."

        elif data['top_10_pct'] > 10:
            concentration = 'distributed'
            risks = [
                'Some concentration risk remains'
            ]
            opportunities = [
                'Healthy distribution reduces manipulation risk',
                'More stable price action expected'
            ]
            wisdom = "Good distribution means retail has a voice. Whales matter less here."

        else:
            concentration = 'highly_distributed'
            risks = []
            opportunities = [
                'Excellent decentralization',
                'Low manipulation risk',
                'Community-driven price action'
            ]
            wisdom = "True decentralization—no single entity can move the market. Bitcoin-level distribution."

        analysis = TokenHolderAnalysis(
            token=token,
            blockchain=blockchain,
            timestamp=datetime.now().isoformat(),
            total_holders=data['total_holders'],
            top_10_holders_pct=data['top_10_pct'],
            top_100_holders_pct=data['top_100_pct'],
            exchange_holdings_pct=data['exchange_pct'],
            known_exchanges=['Binance', 'Coinbase', 'Kraken'],
            decentralization_score=decentral_score,
            concentration_level=concentration,
            risks=risks,
            opportunities=opportunities,
            wisdom_insight=wisdom
        )

        print(f"   Holders: {data['total_holders']:,}")
        print(f"   Top 10 control: {data['top_10_pct']:.1f}%")
        print(f"   Decentralization score: {decentral_score}/100")
        print(f"   Level: {concentration}")
        print(f"   Wisdom: {wisdom}")

        return analysis

    def track_smart_money_flow(
        self,
        token: str,
        timeframe: str = '24h'
    ) -> SmartMoneyFlow:
        """
        Track smart money accumulation/distribution

        Smart money = wallets with proven profitable trading history

        If smart money is accumulating → bullish signal
        If smart money is distributing → bearish signal
        """
        print(f"\n🔍 Tracking smart money flow for {token} ({timeframe})...")

        # Simulate smart money activity
        import random

        # Randomize for demo (in production, query real data)
        inflow = random.uniform(500000, 5000000)
        outflow = random.uniform(300000, 4000000)
        net_flow = inflow - outflow

        whale_buyers = random.randint(5, 20)
        whale_sellers = random.randint(3, 15)
        net_whales = whale_buyers - whale_sellers

        avg_buy = inflow / whale_buyers if whale_buyers > 0 else 0
        avg_sell = outflow / whale_sellers if whale_sellers > 0 else 0

        # Determine sentiment
        if net_flow > 1000000:
            sentiment = 'accumulating'
            bullish_bearish = 'bullish'
            confidence = 0.8
            reasons = [
                f'Net inflow: ${net_flow:,.0f} in {timeframe}',
                f'{net_whales} more buyers than sellers',
                'Smart money is accumulating—follow the whales',
                'Potential upward pressure building'
            ]
            wisdom = "When smart money buys, listen. They know something retail doesn't—yet."

        elif net_flow < -1000000:
            sentiment = 'distributing'
            bullish_bearish = 'bearish'
            confidence = 0.8
            reasons = [
                f'Net outflow: ${abs(net_flow):,.0f} in {timeframe}',
                f'{abs(net_whales)} more sellers than buyers',
                'Smart money is exiting—warning sign',
                'Potential downward pressure ahead'
            ]
            wisdom = "When smart money sells, take note. They're locking in profits—consider following."

        else:
            sentiment = 'neutral'
            bullish_bearish = 'neutral'
            confidence = 0.5
            reasons = [
                f'Balanced flow: ${abs(net_flow):,.0f} net',
                'No clear directional bias',
                'Monitor for trend development'
            ]
            wisdom = "Neutral flow means indecision. Wait for a clear signal before acting."

        flow = SmartMoneyFlow(
            token=token,
            timeframe=timeframe,
            timestamp=datetime.now().isoformat(),
            smart_money_inflow_usd=inflow,
            smart_money_outflow_usd=outflow,
            net_flow_usd=net_flow,
            whale_buyers=whale_buyers,
            whale_sellers=whale_sellers,
            net_whales=net_whales,
            avg_buy_size_usd=avg_buy,
            avg_sell_size_usd=avg_sell,
            smart_money_sentiment=sentiment,
            confidence=confidence,
            bullish_bearish=bullish_bearish,
            reasons=reasons,
            wisdom_insight=wisdom
        )

        print(f"   Inflow: ${inflow:,.0f}")
        print(f"   Outflow: ${outflow:,.0f}")
        print(f"   Net: ${net_flow:,.0f}")
        print(f"   Sentiment: {sentiment.upper()}")
        print(f"   Signal: {bullish_bearish.upper()}")
        print(f"   Wisdom: {wisdom}")

        return flow

    def _save_alerts(self):
        """Save recent alerts to disk"""
        try:
            # Keep only last 100 alerts
            recent = self.recent_alerts[-100:]
            with open(self.alerts_file, 'w') as f:
                json.dump([asdict(a) for a in recent], f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save alerts: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get detective status"""
        return {
            'agent': self.name,
            'philosophy': 'The blockchain never lies—every transaction is the truth',
            'known_whales': sum(len(v) for v in self.known_whales.values()),
            'smart_money_wallets': len(self.smart_money_wallets),
            'recent_alerts': len(self.recent_alerts),
            'config': self.config,
            'wisdom': 'When whales move, the detective knows. When smart money accumulates, the detective sees. The blockchain is the source of truth.'
        }


# Singleton instance
_detective = None


def get_onchain_detective() -> OnChainDetective:
    """Get singleton On-Chain Detective"""
    global _detective
    if _detective is None:
        _detective = OnChainDetective()
    return _detective


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY ON-CHAIN DETECTIVE - THE BLOCKCHAIN INTELLIGENCE SPECIALIST")
    print("="*70)
    print()

    detective = get_onchain_detective()

    print("\nStatus:")
    status = detective.get_status()
    for key, value in status.items():
        if key != 'wisdom':
            print(f"  {key}: {value}")

    print(f"\n💬 Wisdom: {status['wisdom']}")

    # Simulate whale movements
    print("\n🐋 SIMULATING WHALE MOVEMENTS:")
    print("="*70)

    # 1. Bearish: Whale moves BTC to exchange
    alert1 = detective.simulate_whale_movement(
        token='BTC',
        amount_usd=5000000,
        movement_type='exchange_inflow'
    )

    # 2. Bullish: Whale withdraws ETH from exchange
    alert2 = detective.simulate_whale_movement(
        token='ETH',
        amount_usd=3000000,
        movement_type='exchange_outflow'
    )

    # Analyze token holders
    print("\n\n📊 TOKEN HOLDER ANALYSIS:")
    print("="*70)

    for token in ['BTC', 'ETH', 'SHITCOIN']:
        analysis = detective.analyze_token_holders(token)
        print()

    # Track smart money
    print("\n\n💰 SMART MONEY FLOW TRACKING:")
    print("="*70)

    for token in ['BTC', 'ETH', 'SOL']:
        flow = detective.track_smart_money_flow(token, '24h')
        print()

    print("\n✅ On-Chain Detective ready to track the blockchain")
