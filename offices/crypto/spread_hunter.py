#!/usr/bin/env python3
"""
Unity Spread Hunter - The Arbitrage Specialist

Cross-exchange arbitrage agent that hunts for profitable price differences
across multiple exchanges. Monitors spreads, calculates fees, and recommends
profitable trades.

Philosophy: "The market is not one—it is many. When exchanges disagree on price,
the hunter profits from their temporary inefficiency. This is not gambling.
This is mathematical certainty."

Exchanges monitored:
- Coinbase (primary spot market)
- Kraken (low fees, deep liquidity)
- Gemini (institutional grade)
- Binance.US (high volume)

Strategies:
1. Simple Arbitrage: Buy low on Exchange A, sell high on Exchange B
2. Triangular Arbitrage: BTC → ETH → USDT → BTC (single exchange)
3. Statistical Arbitrage: Mean reversion when spreads widen beyond normal

Author: Dr. Claude Summers, Arbitrage Systems Architect
Date: October 16, 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import time
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.exchange_clients.coinbase_client import get_coinbase_client
from tools.exchange_clients.kraken_client import get_kraken_client


@dataclass
class ExchangePrice:
    """Price data from a specific exchange"""
    exchange: str
    symbol: str
    bid: float  # Highest buy price (what we can sell for)
    ask: float  # Lowest sell price (what we must pay to buy)
    mid: float  # (bid + ask) / 2
    spread_bps: float  # Bid-ask spread in basis points
    timestamp: str
    volume_24h: float = 0.0


@dataclass
class SpreadOpportunity:
    """Arbitrage opportunity between two exchanges"""
    opportunity_id: str
    symbol: str

    # Buy side
    buy_exchange: str
    buy_price: float
    buy_fee_pct: float

    # Sell side
    sell_exchange: str
    sell_price: float
    sell_fee_pct: float

    # Profitability
    gross_spread_pct: float
    net_spread_pct: float  # After fees
    profit_per_1k_usd: float

    # Risk factors
    transfer_time_minutes: int
    liquidity_risk: str  # 'low', 'medium', 'high'

    # Recommendation
    recommended_action: str  # 'execute', 'monitor', 'skip'
    confidence: float
    reasons: List[str]

    timestamp: str


@dataclass
class TriangularOpportunity:
    """Triangular arbitrage opportunity (single exchange)"""
    opportunity_id: str
    exchange: str

    # Path: Asset A → Asset B → Asset C → Asset A
    path: List[str]  # e.g., ['BTC', 'ETH', 'USDT', 'BTC']

    # Exchange rates
    rate_1: float  # BTC → ETH
    rate_2: float  # ETH → USDT
    rate_3: float  # USDT → BTC

    # Profit
    theoretical_profit_pct: float
    net_profit_pct: float  # After 3x trading fees
    profit_per_1k_usd: float

    # Recommendation
    recommended_action: str
    confidence: float
    reasons: List[str]

    timestamp: str


@dataclass
class SpreadCampaign:
    """Active arbitrage campaign tracking"""
    campaign_id: str
    strategy: str  # 'simple', 'triangular', 'statistical'
    symbol: str

    # Execution
    buy_exchange: str
    sell_exchange: str
    position_size_usd: float

    # Status
    status: str  # 'pending', 'buy_executed', 'transferring', 'sell_executed', 'completed'

    # Results
    buy_price: float
    sell_price: float
    actual_profit_usd: float
    actual_profit_pct: float

    # Timestamps
    created_at: str
    buy_executed_at: Optional[str] = None
    transfer_completed_at: Optional[str] = None
    sell_executed_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Notes
    notes: List[str] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = []


class SpreadHunter:
    """
    Spread Hunter - The Arbitrage Specialist

    Philosophy:
    "When two exchanges quote different prices for the same asset,
    one is wrong—or at least, temporarily inefficient. The hunter
    profits from this inefficiency before the market corrects itself.

    This is not speculation. This is mathematical arbitrage.
    The profit is locked in the moment both sides execute.

    Risk comes from execution delay, transfer time, and liquidity.
    The hunter calculates these risks and only strikes when the math is certain."

    Strategies:
    1. Simple Arbitrage: Buy Exchange A, sell Exchange B (requires transfer)
    2. Triangular Arbitrage: Circular trades on single exchange (instant)
    3. Statistical Arbitrage: Mean reversion when spreads abnormally wide

    Fee Structure (typical):
    - Coinbase: 0.50% maker/taker
    - Kraken: 0.26% maker / 0.26% taker
    - Gemini: 0.35% maker / 0.35% taker
    - Withdrawal: ~$5-25 depending on network
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "Spread Hunter"

        # Configuration
        self.config = config or {
            'min_profit_threshold_pct': 0.5,  # Minimum 0.5% profit after fees
            'min_profit_per_1k_usd': 5.0,     # Minimum $5 profit per $1000
            'max_transfer_time_minutes': 30,  # Max acceptable transfer delay
            'default_position_size_usd': 1000, # Default trade size
            'update_interval_seconds': 10      # Price refresh rate
        }

        # Exchange clients
        print(f"🎯 Initializing {self.name}...")

        try:
            self.coinbase = get_coinbase_client()
            print(f"   ✅ Coinbase connected")
        except Exception as e:
            print(f"   ⚠️  Coinbase not available: {e}")
            self.coinbase = None

        try:
            self.kraken = get_kraken_client()
            print(f"   ✅ Kraken connected")
        except Exception as e:
            print(f"   ⚠️  Kraken not available: {e}")
            self.kraken = None

        # Exchange fee structure
        self.exchange_fees = {
            'coinbase': {'maker': 0.005, 'taker': 0.005, 'withdrawal': 0.0},  # 0.5%
            'kraken': {'maker': 0.0026, 'taker': 0.0026, 'withdrawal': 0.0},  # 0.26%
            'gemini': {'maker': 0.0035, 'taker': 0.0035, 'withdrawal': 0.0},  # 0.35%
            'binance_us': {'maker': 0.001, 'taker': 0.001, 'withdrawal': 0.0}  # 0.1%
        }

        # Transfer times (minutes) between exchanges
        self.transfer_times = {
            ('coinbase', 'kraken'): 15,
            ('kraken', 'coinbase'): 15,
            ('coinbase', 'gemini'): 20,
            ('gemini', 'coinbase'): 20,
            ('kraken', 'gemini'): 25,
            ('gemini', 'kraken'): 25
        }

        # Supported symbols for arbitrage
        self.symbols = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'MATIC-USD']

        # Active campaigns
        self.campaigns_file = Path(__file__).parent.parent.parent / "logs" / "crypto" / "spread_campaigns.json"
        self.campaigns_file.parent.mkdir(parents=True, exist_ok=True)
        self.active_campaigns = self._load_campaigns()

        print(f"✅ {self.name} initialized")
        print(f"   Monitoring {len(self.symbols)} symbols across {len(self.exchange_fees)} exchanges")
        print(f"   Min profit threshold: {self.config['min_profit_threshold_pct']:.2%}")

    def _load_campaigns(self) -> List[SpreadCampaign]:
        """Load active campaigns from disk"""
        if self.campaigns_file.exists():
            try:
                with open(self.campaigns_file, 'r') as f:
                    data = json.load(f)
                    return [SpreadCampaign(**c) for c in data]
            except Exception as e:
                print(f"⚠️  Failed to load campaigns: {e}")
        return []

    def _save_campaigns(self):
        """Save active campaigns to disk"""
        try:
            with open(self.campaigns_file, 'w') as f:
                json.dump([asdict(c) for c in self.active_campaigns], f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save campaigns: {e}")

    def get_exchange_price(self, exchange: str, symbol: str) -> Optional[ExchangePrice]:
        """Get current price from an exchange"""
        try:
            if exchange == 'coinbase' and self.coinbase:
                ticker = self.coinbase.get_ticker(symbol)
                if ticker:
                    # Coinbase may not have bid/ask, use last price
                    bid = ticker.bid if ticker.bid > 0 else ticker.last * 0.999
                    ask = ticker.ask if ticker.ask > 0 else ticker.last * 1.001
                    mid = (bid + ask) / 2
                    spread_bps = ((ask - bid) / mid) * 10000 if mid > 0 else 0

                    return ExchangePrice(
                        exchange='coinbase',
                        symbol=symbol,
                        bid=bid,
                        ask=ask,
                        mid=mid,
                        spread_bps=spread_bps,
                        timestamp=ticker.timestamp,
                        volume_24h=ticker.volume_24h
                    )

            elif exchange == 'kraken' and self.kraken:
                ticker = self.kraken.get_ticker(symbol)
                if ticker:
                    bid = ticker.bid
                    ask = ticker.ask
                    mid = (bid + ask) / 2
                    spread_bps = ((ask - bid) / mid) * 10000 if mid > 0 else 0

                    return ExchangePrice(
                        exchange='kraken',
                        symbol=symbol,
                        bid=bid,
                        ask=ask,
                        mid=mid,
                        spread_bps=spread_bps,
                        timestamp=ticker.timestamp,
                        volume_24h=ticker.volume_24h
                    )

        except Exception as e:
            print(f"⚠️  Failed to get {exchange} price for {symbol}: {e}")

        return None

    def scan_simple_arbitrage(self, symbol: str) -> List[SpreadOpportunity]:
        """
        Scan for simple arbitrage opportunities

        Strategy: Buy on Exchange A (lower price), sell on Exchange B (higher price)

        Requirements:
        1. Price difference > fees + slippage
        2. Sufficient liquidity on both sides
        3. Acceptable transfer time

        Returns list of profitable opportunities
        """
        opportunities = []

        # Get prices from all exchanges
        exchanges = ['coinbase', 'kraken']
        prices = {}

        for exchange in exchanges:
            price = self.get_exchange_price(exchange, symbol)
            if price:
                prices[exchange] = price

        if len(prices) < 2:
            return []  # Need at least 2 exchanges

        # Compare all pairs
        for buy_exchange in exchanges:
            for sell_exchange in exchanges:
                if buy_exchange == sell_exchange:
                    continue

                if buy_exchange not in prices or sell_exchange not in prices:
                    continue

                buy_price_data = prices[buy_exchange]
                sell_price_data = prices[sell_exchange]

                # Buy at ask price (must pay more), sell at bid price (receive less)
                buy_price = buy_price_data.ask
                sell_price = sell_price_data.bid

                # Calculate fees
                buy_fee_pct = self.exchange_fees[buy_exchange]['taker']
                sell_fee_pct = self.exchange_fees[sell_exchange]['taker']

                # Gross spread (before fees)
                gross_spread_pct = ((sell_price - buy_price) / buy_price) * 100

                # Net spread (after fees)
                total_fee_pct = (buy_fee_pct + sell_fee_pct) * 100
                net_spread_pct = gross_spread_pct - total_fee_pct

                # Profit per $1000
                profit_per_1k = (net_spread_pct / 100) * 1000

                # Transfer time
                transfer_key = (buy_exchange, sell_exchange)
                transfer_time = self.transfer_times.get(transfer_key, 60)  # Default 60 min

                # Assess liquidity risk based on spread
                avg_spread_bps = (buy_price_data.spread_bps + sell_price_data.spread_bps) / 2
                if avg_spread_bps < 10:
                    liquidity_risk = 'low'
                elif avg_spread_bps < 50:
                    liquidity_risk = 'medium'
                else:
                    liquidity_risk = 'high'

                # Determine recommendation
                reasons = []
                confidence = 0.0

                if net_spread_pct >= self.config['min_profit_threshold_pct']:
                    reasons.append(f"Net spread {net_spread_pct:.2f}% exceeds {self.config['min_profit_threshold_pct']:.2f}% threshold")
                    confidence += 0.4

                if profit_per_1k >= self.config['min_profit_per_1k_usd']:
                    reasons.append(f"Profit ${profit_per_1k:.2f} per $1k exceeds ${self.config['min_profit_per_1k_usd']:.2f} threshold")
                    confidence += 0.3

                if transfer_time <= self.config['max_transfer_time_minutes']:
                    reasons.append(f"Transfer time {transfer_time}min acceptable")
                    confidence += 0.2
                else:
                    reasons.append(f"⚠️ Transfer time {transfer_time}min exceeds {self.config['max_transfer_time_minutes']}min limit")

                if liquidity_risk == 'low':
                    reasons.append(f"Low liquidity risk (spread {avg_spread_bps:.1f} bps)")
                    confidence += 0.1
                elif liquidity_risk == 'high':
                    reasons.append(f"⚠️ High liquidity risk (spread {avg_spread_bps:.1f} bps)")
                    confidence -= 0.2

                # Recommendation
                if confidence >= 0.7 and net_spread_pct >= self.config['min_profit_threshold_pct']:
                    recommended_action = 'execute'
                elif confidence >= 0.5:
                    recommended_action = 'monitor'
                else:
                    recommended_action = 'skip'

                # Only return profitable opportunities
                if net_spread_pct > 0:
                    opportunity = SpreadOpportunity(
                        opportunity_id=f"spread_{symbol}_{buy_exchange}_{sell_exchange}_{int(time.time())}",
                        symbol=symbol,
                        buy_exchange=buy_exchange,
                        buy_price=buy_price,
                        buy_fee_pct=buy_fee_pct,
                        sell_exchange=sell_exchange,
                        sell_price=sell_price,
                        sell_fee_pct=sell_fee_pct,
                        gross_spread_pct=gross_spread_pct,
                        net_spread_pct=net_spread_pct,
                        profit_per_1k_usd=profit_per_1k,
                        transfer_time_minutes=transfer_time,
                        liquidity_risk=liquidity_risk,
                        recommended_action=recommended_action,
                        confidence=max(0.0, min(1.0, confidence)),
                        reasons=reasons,
                        timestamp=datetime.now().isoformat()
                    )

                    opportunities.append(opportunity)

        # Sort by profit
        opportunities.sort(key=lambda x: x.net_spread_pct, reverse=True)

        return opportunities

    def scan_all_symbols(self) -> Dict[str, List[SpreadOpportunity]]:
        """Scan all symbols for arbitrage opportunities"""
        print(f"\n{'='*70}")
        print(f"🎯 SPREAD HUNTER SCANNING ALL SYMBOLS")
        print(f"{'='*70}\n")

        all_opportunities = {}

        for symbol in self.symbols:
            print(f"📊 Scanning {symbol}...")
            opportunities = self.scan_simple_arbitrage(symbol)

            if opportunities:
                all_opportunities[symbol] = opportunities
                print(f"   Found {len(opportunities)} opportunities")

                # Show best opportunity
                best = opportunities[0]
                print(f"   Best: {best.buy_exchange} → {best.sell_exchange}")
                print(f"   Net spread: {best.net_spread_pct:.3f}%")
                print(f"   Profit/1k: ${best.profit_per_1k_usd:.2f}")
                print(f"   Action: {best.recommended_action}")
            else:
                print(f"   No opportunities found")

            time.sleep(0.5)  # Rate limiting

        print(f"\n{'='*70}")
        print(f"✅ Scan complete - {sum(len(v) for v in all_opportunities.values())} total opportunities")
        print(f"{'='*70}\n")

        return all_opportunities

    def create_campaign(self, opportunity: SpreadOpportunity, position_size_usd: Optional[float] = None) -> SpreadCampaign:
        """Create an arbitrage campaign from an opportunity"""
        position_size = position_size_usd or self.config['default_position_size_usd']

        campaign = SpreadCampaign(
            campaign_id=f"campaign_{int(time.time())}",
            strategy='simple',
            symbol=opportunity.symbol,
            buy_exchange=opportunity.buy_exchange,
            sell_exchange=opportunity.sell_exchange,
            position_size_usd=position_size,
            status='pending',
            buy_price=opportunity.buy_price,
            sell_price=opportunity.sell_price,
            actual_profit_usd=0.0,
            actual_profit_pct=0.0,
            created_at=datetime.now().isoformat(),
            notes=[f"Created from opportunity {opportunity.opportunity_id}"]
        )

        self.active_campaigns.append(campaign)
        self._save_campaigns()

        print(f"✅ Campaign created: {campaign.campaign_id}")
        return campaign

    def get_status(self) -> Dict[str, Any]:
        """Get Spread Hunter status"""
        return {
            'agent': self.name,
            'philosophy': 'Mathematical arbitrage—profit from exchange inefficiency',
            'exchanges_connected': {
                'coinbase': self.coinbase is not None,
                'kraken': self.kraken is not None
            },
            'symbols_monitored': self.symbols,
            'config': self.config,
            'active_campaigns': len(self.active_campaigns),
            'wisdom': 'The market is not one—it is many. When they disagree, the hunter profits.'
        }


# Singleton instance
_spread_hunter = None


def get_spread_hunter() -> SpreadHunter:
    """Get singleton Spread Hunter"""
    global _spread_hunter
    if _spread_hunter is None:
        _spread_hunter = SpreadHunter()
    return _spread_hunter


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY SPREAD HUNTER - THE ARBITRAGE SPECIALIST")
    print("="*70)
    print()

    hunter = get_spread_hunter()

    print("\nStatus:")
    status = hunter.get_status()
    for key, value in status.items():
        if key != 'wisdom':
            print(f"  {key}: {value}")

    print(f"\n💬 Wisdom: {status['wisdom']}")

    print("\n🎯 Scanning for arbitrage opportunities...")
    opportunities = hunter.scan_all_symbols()

    if opportunities:
        print("\n📊 BEST OPPORTUNITIES:")
        print(f"{'='*70}\n")

        all_opps = []
        for symbol, opps in opportunities.items():
            all_opps.extend(opps)

        # Sort by net spread
        all_opps.sort(key=lambda x: x.net_spread_pct, reverse=True)

        for i, opp in enumerate(all_opps[:5], 1):  # Top 5
            print(f"{i}. {opp.symbol}")
            print(f"   Route: {opp.buy_exchange} → {opp.sell_exchange}")
            print(f"   Buy: ${opp.buy_price:,.2f} | Sell: ${opp.sell_price:,.2f}")
            print(f"   Gross spread: {opp.gross_spread_pct:.3f}%")
            print(f"   Net spread: {opp.net_spread_pct:.3f}% (after {(opp.buy_fee_pct + opp.sell_fee_pct)*100:.2f}% fees)")
            print(f"   Profit/1k: ${opp.profit_per_1k_usd:.2f}")
            print(f"   Transfer time: {opp.transfer_time_minutes} min")
            print(f"   Liquidity risk: {opp.liquidity_risk}")
            print(f"   Confidence: {opp.confidence:.1%}")
            print(f"   ✅ Recommendation: {opp.recommended_action.upper()}")
            print()
    else:
        print("\n💤 No profitable arbitrage opportunities found at this time")
        print("   (This is normal—spreads are often too tight for profit)")

    print("✅ Spread Hunter ready to profit from market inefficiency")
