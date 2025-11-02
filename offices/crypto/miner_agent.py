#!/usr/bin/env python3
"""
Unity Miner Agent - The Mining Strategist

Blockchain mining opportunity evaluator that analyzes:
- GPU mining profitability (ETH variants, RVN, ERGO, etc.)
- CPU mining opportunities (Monero, etc.)
- Proof-of-Stake staking yields
- Cloud mining contract evaluation
- Hardware recommendations

Philosophy: "Mining is not magic—it is mathematics. Electricity cost versus
block reward. Hash rate versus difficulty. The miner calculates, and only
mines when the equation yields profit. Otherwise—buy the coin directly."

This agent does NOT mine—it EVALUATES mining opportunities and recommends
whether mining is more profitable than simply buying the asset.

Author: Dr. Claude Summers, Mining Economics Specialist
Date: October 16, 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import time
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class MiningHardware:
    """Mining hardware specification"""
    hardware_type: str  # 'GPU', 'CPU', 'ASIC'
    model: str
    hash_rate: float  # Hash/s (varies by algorithm)
    hash_rate_unit: str  # 'MH/s', 'GH/s', 'H/s'
    power_consumption_watts: int
    initial_cost_usd: float
    lifespan_months: int


@dataclass
class MiningOpportunity:
    """Mining profitability analysis for a specific coin"""
    opportunity_id: str
    coin_symbol: str
    coin_name: str
    algorithm: str  # 'Ethash', 'KawPow', 'RandomX', etc.

    # Network stats
    network_difficulty: float
    block_reward: float
    block_time_seconds: int
    current_price_usd: float

    # Profitability (daily basis)
    daily_revenue_usd: float
    daily_electricity_cost_usd: float
    daily_profit_usd: float
    daily_roi_pct: float

    # Annual projections
    annual_profit_usd: float
    payback_period_months: float

    # Hardware recommendation
    recommended_hardware: str
    required_hash_rate: float

    # Comparison
    buy_vs_mine_comparison: str  # "Mining 20% more profitable" or "Buy directly 35% better"

    # Risk factors
    difficulty_trend: str  # 'increasing', 'stable', 'decreasing'
    price_volatility: str  # 'low', 'medium', 'high'

    # Recommendation
    recommended_action: str  # 'mine', 'buy_directly', 'skip', 'stake_instead'
    confidence: float
    reasons: List[str]

    timestamp: str


@dataclass
class StakingOpportunity:
    """Proof-of-Stake staking opportunity"""
    opportunity_id: str
    coin_symbol: str
    coin_name: str
    blockchain: str

    # Staking parameters
    apy_pct: float
    min_stake_amount: float
    min_stake_amount_usd: float
    lock_period_days: int

    # Requirements
    validator_requirements: Optional[str]
    slashing_risk: str  # 'none', 'low', 'medium', 'high'

    # Profitability
    annual_yield_pct: float
    annual_yield_usd_per_1k: float

    # Recommendation
    recommended_action: str
    confidence: float
    reasons: List[str]

    timestamp: str


class MinerAgent:
    """
    Miner Agent - The Mining Strategist

    Philosophy:
    "Mining is a business, not a hobby. Every hash must pay for itself.

    The equation is simple:
    - Revenue = Hash Rate × Block Reward × Price
    - Cost = Power Consumption × Electricity Rate × Time
    - Profit = Revenue - Cost - Hardware Depreciation

    If Profit > 0 AND Profit > (Cost of Buying Coin Directly):
        → Mine
    Else:
        → Buy the coin directly

    The miner does not fall in love with hardware. The miner follows math.

    GPU mining died after Ethereum's merge (Sept 2022). Most GPU miners now:
    - Mine alt coins (RVN, ERGO, ETC, FLUX)
    - Convert to BTC/ETH
    - Hope for alt coin appreciation

    PoS staking is often better:
    - No electricity cost
    - No hardware wear
    - Passive yield (3-20% APY)
    - Examples: ETH 2.0, ADA, SOL, DOT

    This agent calculates—and tells you the truth."

    Supported Mining Algorithms:
    - GPU: KawPow (RVN), Autolykos (ERGO), Etchash (ETC)
    - CPU: RandomX (XMR - Monero)
    - PoS: Ethereum, Cardano, Solana, Polkadot
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "Miner Agent"

        # Configuration
        self.config = config or {
            'electricity_cost_per_kwh': 0.12,  # $0.12/kWh (US average)
            'min_daily_profit_usd': 2.0,       # Minimum $2/day profit
            'max_payback_months': 12,          # Hardware must pay back in 12 months
            'difficulty_increase_monthly_pct': 3.0,  # Assume 3% monthly difficulty increase
        }

        print(f"⛏️  Initializing {self.name}...")

        # Mining hardware database
        self.gpu_hardware = [
            MiningHardware('GPU', 'NVIDIA RTX 4090', 130, 'MH/s', 450, 1599, 36),
            MiningHardware('GPU', 'NVIDIA RTX 4080', 100, 'MH/s', 320, 1199, 36),
            MiningHardware('GPU', 'NVIDIA RTX 3090', 120, 'MH/s', 350, 1499, 24),
            MiningHardware('GPU', 'AMD RX 7900 XTX', 80, 'MH/s', 355, 999, 36),
            MiningHardware('GPU', 'AMD RX 6800 XT', 64, 'MH/s', 250, 649, 24)
        ]

        # Mineable coins (post-ETH merge)
        self.mineable_coins = {
            'RVN': {
                'name': 'Ravencoin',
                'algorithm': 'KawPow',
                'block_time': 60,
                'current_price': 0.02,  # Placeholder
                'network_hashrate_gh': 5000,  # 5 TH/s
                'block_reward': 2500,
                'gpu_friendly': True
            },
            'ERGO': {
                'name': 'Ergo',
                'algorithm': 'Autolykos',
                'block_time': 120,
                'current_price': 1.50,
                'network_hashrate_gh': 15000,
                'block_reward': 66,
                'gpu_friendly': True
            },
            'ETC': {
                'name': 'Ethereum Classic',
                'algorithm': 'Etchash',
                'block_time': 13,
                'current_price': 20.0,
                'network_hashrate_gh': 150000,
                'block_reward': 2.56,
                'gpu_friendly': True
            },
            'XMR': {
                'name': 'Monero',
                'algorithm': 'RandomX',
                'block_time': 120,
                'current_price': 150.0,
                'network_hashrate_gh': 3000,
                'block_reward': 0.6,
                'cpu_friendly': True,
                'gpu_friendly': False
            }
        }

        # Staking opportunities (PoS)
        self.staking_coins = {
            'ETH': {
                'name': 'Ethereum',
                'apy': 4.0,
                'min_stake': 32,
                'lock_period_days': 0,  # Can unstake anytime (post-Shapella)
                'slashing_risk': 'low',
                'current_price': 3500
            },
            'ADA': {
                'name': 'Cardano',
                'apy': 5.0,
                'min_stake': 10,
                'lock_period_days': 0,
                'slashing_risk': 'none',
                'current_price': 0.50
            },
            'SOL': {
                'name': 'Solana',
                'apy': 7.0,
                'min_stake': 0.01,
                'lock_period_days': 0,
                'slashing_risk': 'low',
                'current_price': 100
            },
            'DOT': {
                'name': 'Polkadot',
                'apy': 14.0,
                'min_stake': 120,
                'lock_period_days': 28,
                'slashing_risk': 'medium',
                'current_price': 7.0
            }
        }

        # Active evaluations
        self.evaluations_file = Path(__file__).parent.parent.parent / "logs" / "crypto" / "mining_evaluations.json"
        self.evaluations_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"✅ {self.name} initialized")
        print(f"   GPU mining algorithms: {len([c for c in self.mineable_coins.values() if c.get('gpu_friendly')])} coins")
        print(f"   PoS staking opportunities: {len(self.staking_coins)} coins")
        print(f"   Electricity cost: ${self.config['electricity_cost_per_kwh']:.3f}/kWh")

    def evaluate_gpu_mining(self, coin_symbol: str, hardware: MiningHardware) -> Optional[MiningOpportunity]:
        """
        Evaluate GPU mining profitability for a specific coin

        Formula:
        1. Calculate daily hash rate share: user_hashrate / network_hashrate
        2. Calculate daily blocks earned: share × (86400 / block_time)
        3. Calculate daily revenue: blocks × block_reward × price
        4. Calculate daily cost: (power_watts / 1000) × 24 × electricity_rate
        5. Calculate daily profit: revenue - cost
        6. Compare to buying coin directly
        """
        if coin_symbol not in self.mineable_coins:
            print(f"⚠️  {coin_symbol} not in mineable coins database")
            return None

        coin = self.mineable_coins[coin_symbol]

        if not coin.get('gpu_friendly', False):
            print(f"⚠️  {coin_symbol} is not GPU-friendly")
            return None

        print(f"\n⛏️  Evaluating {coin['name']} mining with {hardware.model}...")

        # User hash rate (convert to GH/s if needed)
        user_hash_rate_gh = hardware.hash_rate
        if hardware.hash_rate_unit == 'MH/s':
            user_hash_rate_gh = hardware.hash_rate / 1000

        # Network hash rate
        network_hash_rate_gh = coin['network_hashrate_gh']

        # Hash rate share
        hash_share = user_hash_rate_gh / network_hash_rate_gh

        # Daily blocks
        seconds_per_day = 86400
        blocks_per_day_network = seconds_per_day / coin['block_time']
        user_blocks_per_day = blocks_per_day_network * hash_share

        # Daily revenue
        daily_coins = user_blocks_per_day * coin['block_reward']
        daily_revenue_usd = daily_coins * coin['current_price']

        # Daily electricity cost
        daily_kwh = (hardware.power_consumption_watts / 1000) * 24
        daily_electricity_cost = daily_kwh * self.config['electricity_cost_per_kwh']

        # Daily profit
        daily_profit = daily_revenue_usd - daily_electricity_cost

        # Daily ROI (relative to hardware cost)
        daily_roi_pct = (daily_profit / hardware.initial_cost_usd) * 100 if hardware.initial_cost_usd > 0 else 0

        # Annual projections (accounting for difficulty increase)
        avg_monthly_multiplier = 1 - (self.config['difficulty_increase_monthly_pct'] / 100)
        annual_profit = sum(daily_profit * 30 * (avg_monthly_multiplier ** month) for month in range(12))

        # Payback period
        payback_months = hardware.initial_cost_usd / (daily_profit * 30) if daily_profit > 0 else 999

        # Compare to buying directly
        investment_amount = hardware.initial_cost_usd
        coins_if_bought_directly = investment_amount / coin['current_price']
        value_after_1_year_buy = coins_if_bought_directly * coin['current_price']  # Assumes flat price
        value_after_1_year_mine = annual_profit + (investment_amount * 0.3)  # Hardware retains ~30% value

        if value_after_1_year_mine > value_after_1_year_buy:
            buy_vs_mine = f"Mining {((value_after_1_year_mine / value_after_1_year_buy - 1) * 100):.0f}% more profitable"
        else:
            buy_vs_mine = f"Buy directly {((value_after_1_year_buy / value_after_1_year_mine - 1) * 100):.0f}% better"

        # Determine recommendation
        reasons = []
        confidence = 0.0

        if daily_profit >= self.config['min_daily_profit_usd']:
            reasons.append(f"Daily profit ${daily_profit:.2f} exceeds ${self.config['min_daily_profit_usd']:.2f} minimum")
            confidence += 0.3
        else:
            reasons.append(f"⚠️ Daily profit ${daily_profit:.2f} below ${self.config['min_daily_profit_usd']:.2f} minimum")

        if payback_months <= self.config['max_payback_months']:
            reasons.append(f"Payback {payback_months:.1f} months acceptable")
            confidence += 0.3
        else:
            reasons.append(f"⚠️ Payback {payback_months:.1f} months exceeds {self.config['max_payback_months']} month limit")

        if value_after_1_year_mine > value_after_1_year_buy:
            reasons.append(f"Mining more profitable than buying")
            confidence += 0.4
        else:
            reasons.append(f"⚠️ Buying coin directly is better ROI")
            confidence -= 0.3

        # Final recommendation
        if confidence >= 0.6 and daily_profit > 0:
            recommended_action = 'mine'
        elif daily_profit > 0:
            recommended_action = 'mine'  # Marginal but positive
        else:
            recommended_action = 'buy_directly'

        opportunity = MiningOpportunity(
            opportunity_id=f"mining_{coin_symbol}_{hardware.model.replace(' ', '_')}_{int(time.time())}",
            coin_symbol=coin_symbol,
            coin_name=coin['name'],
            algorithm=coin['algorithm'],
            network_difficulty=network_hash_rate_gh,
            block_reward=coin['block_reward'],
            block_time_seconds=coin['block_time'],
            current_price_usd=coin['current_price'],
            daily_revenue_usd=daily_revenue_usd,
            daily_electricity_cost_usd=daily_electricity_cost,
            daily_profit_usd=daily_profit,
            daily_roi_pct=daily_roi_pct,
            annual_profit_usd=annual_profit,
            payback_period_months=payback_months,
            recommended_hardware=f"{hardware.model} ({hardware.hash_rate} {hardware.hash_rate_unit})",
            required_hash_rate=user_hash_rate_gh,
            buy_vs_mine_comparison=buy_vs_mine,
            difficulty_trend='increasing',  # Most networks increase over time
            price_volatility='high',  # Crypto is volatile
            recommended_action=recommended_action,
            confidence=max(0.0, min(1.0, confidence)),
            reasons=reasons,
            timestamp=datetime.now().isoformat()
        )

        return opportunity

    def evaluate_all_gpu_mining(self) -> List[MiningOpportunity]:
        """Evaluate all GPU mining opportunities"""
        print(f"\n{'='*70}")
        print(f"⛏️  EVALUATING ALL GPU MINING OPPORTUNITIES")
        print(f"{'='*70}\n")

        opportunities = []

        # Test with RTX 4090 (best consumer GPU)
        hardware = self.gpu_hardware[0]  # RTX 4090

        for coin_symbol in ['RVN', 'ERGO', 'ETC']:
            opp = self.evaluate_gpu_mining(coin_symbol, hardware)
            if opp:
                opportunities.append(opp)
                time.sleep(0.2)

        # Sort by daily profit
        opportunities.sort(key=lambda x: x.daily_profit_usd, reverse=True)

        return opportunities

    def evaluate_staking(self, coin_symbol: str) -> Optional[StakingOpportunity]:
        """Evaluate PoS staking opportunity"""
        if coin_symbol not in self.staking_coins:
            return None

        coin = self.staking_coins[coin_symbol]

        print(f"\n🪙 Evaluating {coin['name']} staking...")

        # Calculate returns
        min_stake_amount = coin['min_stake']
        min_stake_usd = min_stake_amount * coin['current_price']
        annual_yield_pct = coin['apy']
        annual_yield_usd_per_1k = (annual_yield_pct / 100) * 1000

        # Evaluate
        reasons = []
        confidence = 0.0

        if coin['slashing_risk'] in ['none', 'low']:
            reasons.append(f"Low risk: {coin['slashing_risk']} slashing risk")
            confidence += 0.3

        if annual_yield_pct >= 5.0:
            reasons.append(f"Strong yield: {annual_yield_pct}% APY")
            confidence += 0.4
        elif annual_yield_pct >= 3.0:
            reasons.append(f"Moderate yield: {annual_yield_pct}% APY")
            confidence += 0.2

        if coin['lock_period_days'] == 0:
            reasons.append(f"No lock period—liquid staking")
            confidence += 0.3
        elif coin['lock_period_days'] <= 30:
            reasons.append(f"Short lock: {coin['lock_period_days']} days")
            confidence += 0.1

        # Recommendation
        if confidence >= 0.6:
            recommended_action = 'stake'
        elif confidence >= 0.4:
            recommended_action = 'consider'
        else:
            recommended_action = 'skip'

        opportunity = StakingOpportunity(
            opportunity_id=f"staking_{coin_symbol}_{int(time.time())}",
            coin_symbol=coin_symbol,
            coin_name=coin['name'],
            blockchain=coin['name'],
            apy_pct=annual_yield_pct,
            min_stake_amount=min_stake_amount,
            min_stake_amount_usd=min_stake_usd,
            lock_period_days=coin['lock_period_days'],
            validator_requirements=None,
            slashing_risk=coin['slashing_risk'],
            annual_yield_pct=annual_yield_pct,
            annual_yield_usd_per_1k=annual_yield_usd_per_1k,
            recommended_action=recommended_action,
            confidence=confidence,
            reasons=reasons,
            timestamp=datetime.now().isoformat()
        )

        return opportunity

    def evaluate_all_staking(self) -> List[StakingOpportunity]:
        """Evaluate all staking opportunities"""
        print(f"\n{'='*70}")
        print(f"🪙 EVALUATING ALL STAKING OPPORTUNITIES")
        print(f"{'='*70}\n")

        opportunities = []

        for coin_symbol in self.staking_coins.keys():
            opp = self.evaluate_staking(coin_symbol)
            if opp:
                opportunities.append(opp)

        # Sort by APY
        opportunities.sort(key=lambda x: x.apy_pct, reverse=True)

        return opportunities

    def get_status(self) -> Dict[str, Any]:
        """Get Miner Agent status"""
        return {
            'agent': self.name,
            'philosophy': 'Mining is mathematics—electricity cost versus block reward',
            'gpu_mineable_coins': len([c for c in self.mineable_coins.values() if c.get('gpu_friendly')]),
            'staking_opportunities': len(self.staking_coins),
            'config': self.config,
            'wisdom': 'The miner does not fall in love with hardware. The miner follows math.'
        }


# Singleton instance
_miner_agent = None


def get_miner_agent() -> MinerAgent:
    """Get singleton Miner Agent"""
    global _miner_agent
    if _miner_agent is None:
        _miner_agent = MinerAgent()
    return _miner_agent


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY MINER AGENT - THE MINING STRATEGIST")
    print("="*70)
    print()

    miner = get_miner_agent()

    print("\nStatus:")
    status = miner.get_status()
    for key, value in status.items():
        if key != 'wisdom':
            print(f"  {key}: {value}")

    print(f"\n💬 Wisdom: {status['wisdom']}")

    # Evaluate GPU mining
    mining_opps = miner.evaluate_all_gpu_mining()

    if mining_opps:
        print(f"\n⛏️  GPU MINING OPPORTUNITIES:")
        print(f"{'='*70}\n")

        for i, opp in enumerate(mining_opps, 1):
            print(f"{i}. {opp.coin_name} ({opp.coin_symbol}) - {opp.algorithm}")
            print(f"   Hardware: {opp.recommended_hardware}")
            print(f"   Daily revenue: ${opp.daily_revenue_usd:.2f}")
            print(f"   Daily electricity: ${opp.daily_electricity_cost_usd:.2f}")
            print(f"   Daily profit: ${opp.daily_profit_usd:.2f}")
            print(f"   Annual profit: ${opp.annual_profit_usd:.2f}")
            print(f"   Payback: {opp.payback_period_months:.1f} months")
            print(f"   {opp.buy_vs_mine_comparison}")
            print(f"   ✅ Recommendation: {opp.recommended_action.upper()} (confidence: {opp.confidence:.1%})")
            print()

    # Evaluate staking
    staking_opps = miner.evaluate_all_staking()

    if staking_opps:
        print(f"\n🪙 STAKING OPPORTUNITIES:")
        print(f"{'='*70}\n")

        for i, opp in enumerate(staking_opps, 1):
            print(f"{i}. {opp.coin_name} ({opp.coin_symbol})")
            print(f"   APY: {opp.apy_pct:.1f}%")
            print(f"   Min stake: {opp.min_stake_amount} {opp.coin_symbol} (${opp.min_stake_amount_usd:,.0f})")
            print(f"   Lock period: {opp.lock_period_days} days")
            print(f"   Slashing risk: {opp.slashing_risk}")
            print(f"   Yield per $1k: ${opp.annual_yield_usd_per_1k:.2f}/year")
            print(f"   ✅ Recommendation: {opp.recommended_action.upper()} (confidence: {opp.confidence:.1%})")
            print()

    print("\n💡 MINER AGENT WISDOM:")
    print("   GPU mining is mostly dead after Ethereum's merge (Sept 2022)")
    print("   Alt coins (RVN, ERGO, ETC) are mineable but low profit")
    print("   PoS staking is usually better: no electricity, no hardware wear")
    print("   If mining profit < buying directly → BUY THE COIN")
    print()
    print("✅ Miner Agent ready to evaluate opportunities")
