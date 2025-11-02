#!/usr/bin/env python3
"""
Unity DeFi Strategist - The Yield Farming Optimization Specialist

DeFi protocol analysis agent that evaluates:
- Yield farming opportunities (APY vs APR, real vs nominal yields)
- Impermanent loss calculations (LP pair risk)
- Protocol risk assessment (audits, TVL, smart contract age)
- Stablecoin yield strategies (low-risk passive income)
- Leverage strategies (borrowed yields, liquidation risk)

Philosophy: "DeFi promises high yields—but every yield comes with risk. The strategist
calculates true returns after fees, IL, and taxes. Most 'high APY' farms are temporary
tokens dumping on liquidity providers. The strategist finds REAL yield—sustainable,
protocol-backed, audited strategies that compound wealth without rekt-ing your capital."

Author: Dr. Claude Summers, DeFi Strategy Architect
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
import math

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class YieldOpportunity:
    """Yield farming opportunity analysis"""
    opportunity_id: str
    protocol: str
    blockchain: str
    pool_name: str  # "ETH-USDC LP", "USDC Lending", etc.

    # Yield metrics
    apy_nominal: float  # Advertised APY
    apy_real: float     # After IL, fees, token emissions
    apr_base: float     # Base trading fees APR
    apr_rewards: float  # Token rewards APR

    # Risk metrics
    tvl_usd: float
    smart_contract_risk: str  # 'low', 'medium', 'high'
    audit_status: str  # 'audited', 'unaudited', 'multiple_audits'
    protocol_age_days: int
    impermanent_loss_risk: str  # 'none', 'low', 'medium', 'high'

    # Calculations
    estimated_daily_yield_usd: float
    estimated_annual_yield_usd: float
    breakeven_days: Optional[int]  # Days to recover IL

    # Classification
    strategy_type: str  # 'stablecoin', 'bluechip_lp', 'altcoin_lp', 'lending', 'leveraged'
    risk_level: str  # 'conservative', 'moderate', 'aggressive', 'degen'

    # Recommendation
    recommended_action: str  # 'enter', 'monitor', 'avoid'
    confidence: float
    reasons: List[str]
    wisdom_insight: str


@dataclass
class ImpermanentLossCalculation:
    """Impermanent loss calculation for LP pairs"""
    pool_name: str
    token_a: str
    token_b: str
    timestamp: str

    # Initial state
    initial_price_ratio: float
    initial_value_usd: float

    # Current state
    current_price_ratio: float
    price_change_pct: float

    # IL calculation
    impermanent_loss_pct: float
    impermanent_loss_usd: float

    # Trading fees earned
    trading_fees_earned_usd: float

    # Net result
    net_profit_loss_usd: float
    net_profit_loss_pct: float

    # Breakeven
    fees_needed_to_recover_il: float
    days_to_breakeven: Optional[float]

    wisdom_insight: str


@dataclass
class ProtocolRiskAssessment:
    """DeFi protocol risk assessment"""
    protocol: str
    blockchain: str
    timestamp: str

    # Protocol metrics
    tvl_usd: float
    protocol_age_days: int
    number_of_audits: int
    audit_firms: List[str]

    # Smart contract risk
    contract_verified: bool
    proxy_contract: bool  # Upgradeable (higher risk)
    timelock_enabled: bool  # Admin key protection
    multisig_required: bool

    # Historical risk
    past_exploits: int
    past_exploit_total_loss_usd: float
    bugs_reported: int
    bug_bounty_program: bool

    # Risk score (0-100, higher = safer)
    risk_score: float

    # Classification
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    red_flags: List[str]
    green_flags: List[str]

    # Recommendation
    recommended_exposure_pct: float  # Max % of portfolio to allocate
    reasons: List[str]
    wisdom_insight: str


@dataclass
class LeverageStrategy:
    """Leveraged yield farming strategy analysis"""
    strategy_name: str
    protocol: str
    blockchain: str

    # Leverage details
    leverage_ratio: float  # 2x, 3x, 5x, etc.
    borrow_asset: str
    borrow_rate_apr: float
    supply_asset: str
    supply_rate_apr: float

    # Net yield
    leveraged_apy: float
    net_apy_after_borrow: float

    # Risk metrics
    liquidation_price: float
    current_price: float
    liquidation_buffer_pct: float  # How far from liquidation

    health_factor: float  # >1.0 = safe, <1.0 = liquidation risk

    # Recommendation
    risk_level: str  # 'moderate', 'high', 'extreme'
    recommended_action: str
    confidence: float
    reasons: List[str]
    wisdom_insight: str


class DeFiStrategist:
    """
    DeFi Strategist - The Yield Farming Optimization Specialist

    Philosophy:
    "DeFi is a permissionless casino where the house edge can work FOR you
    or AGAINST you—depending on whether you understand the math.

    The strategist calculates:
    1. True APY (not marketing hype)
    2. Impermanent loss (the silent killer of LP profits)
    3. Smart contract risk (code is law, but bugs are real)
    4. Token emission sustainability (farm tokens dump 99% of the time)

    DeFi Strategy Hierarchy (risk vs reward):
    1. Stablecoin lending (USDC/USDT on Aave/Compound) = 3-8% APY, low risk
    2. Blue-chip LP (ETH-USDC on Uniswap) = 10-20% APY, moderate IL risk
    3. Alt-coin LP (SOL-USDC) = 20-50% APY, high IL risk
    4. Leveraged strategies (borrow + supply) = 30-100% APY, liquidation risk
    5. Degen farms (new tokens) = 1000% APY, 99% chance of rug pull

    The strategist prefers REAL YIELD:
    - Trading fees (sustainable)
    - Protocol revenue share (sustainable)
    - Token emissions (NOT sustainable, tokens dump)

    The strategist avoids:
    - New protocols (<3 months old)
    - Unaudited contracts
    - Anonymous teams
    - Ponzi-nomics (9000% APY = exit liquidity trap)"

    Key Formulas:
    1. Impermanent Loss = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
    2. Net Yield = APY - IL% - Gas Fees - Slippage
    3. Leveraged Yield = (Supply APY × Leverage) - (Borrow APY × (Leverage - 1))
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "DeFi Strategist"

        # Configuration
        self.config = config or {
            'min_protocol_age_days': 90,  # 3 months minimum
            'min_tvl_usd': 10000000,  # $10M minimum TVL
            'require_audit': True,
            'max_leverage': 3.0,  # 3x max leverage
            'max_il_risk': 'medium',  # Avoid high IL pairs
            'target_apy': 15.0  # Target 15% APY
        }

        print(f"💰 Initializing {self.name}...")

        # Known DeFi protocols (simplified)
        self.protocols = {
            'aave': {
                'name': 'Aave',
                'blockchain': 'ethereum',
                'tvl': 10000000000,  # $10B
                'age_days': 1500,
                'audits': ['Trail of Bits', 'OpenZeppelin', 'Consensys'],
                'risk_score': 95
            },
            'uniswap': {
                'name': 'Uniswap',
                'blockchain': 'ethereum',
                'tvl': 5000000000,
                'age_days': 1800,
                'audits': ['Trail of Bits'],
                'risk_score': 90
            },
            'curve': {
                'name': 'Curve Finance',
                'blockchain': 'ethereum',
                'tvl': 3000000000,
                'age_days': 1400,
                'audits': ['Trail of Bits', 'Quantstamp'],
                'risk_score': 88
            }
        }

        print(f"✅ {self.name} initialized")
        print(f"   Tracking {len(self.protocols)} major DeFi protocols")
        print(f"   Min TVL: ${self.config['min_tvl_usd']:,.0f}")
        print(f"   Require audit: {self.config['require_audit']}")

    def evaluate_yield_opportunity(
        self,
        protocol: str,
        pool_name: str,
        apy_nominal: float,
        tvl_usd: float,
        strategy_type: str = 'bluechip_lp'
    ) -> YieldOpportunity:
        """
        Evaluate a yield farming opportunity

        Args:
            protocol: Protocol name (aave, uniswap, curve, etc.)
            pool_name: Pool identifier (ETH-USDC LP, USDC Lending, etc.)
            apy_nominal: Advertised APY
            tvl_usd: Total Value Locked
            strategy_type: 'stablecoin', 'bluechip_lp', 'altcoin_lp', 'lending', 'leveraged'
        """
        print(f"\n💰 Evaluating {pool_name} on {protocol}...")

        # Get protocol data
        protocol_data = self.protocols.get(protocol.lower(), {
            'age_days': 60,
            'audits': [],
            'risk_score': 40
        })

        # Determine risk factors
        if protocol_data['age_days'] < self.config['min_protocol_age_days']:
            sc_risk = 'high'
        elif protocol_data['age_days'] < 180:
            sc_risk = 'medium'
        else:
            sc_risk = 'low'

        audit_status = 'multiple_audits' if len(protocol_data.get('audits', [])) > 1 else 'audited' if len(protocol_data.get('audits', [])) == 1 else 'unaudited'

        # IL risk based on strategy type
        il_risk_map = {
            'stablecoin': 'none',
            'bluechip_lp': 'low',
            'altcoin_lp': 'high',
            'lending': 'none',
            'leveraged': 'medium'
        }
        il_risk = il_risk_map.get(strategy_type, 'medium')

        # Calculate real APY (discount for token emissions, IL, etc.)
        if strategy_type == 'stablecoin':
            # Stablecoins have no IL, minimal risk
            apy_real = apy_nominal * 0.95  # 5% haircut for gas/fees
            apr_base = apy_nominal
            apr_rewards = 0
        elif strategy_type == 'bluechip_lp':
            # Blue-chip LPs have moderate IL
            apy_real = apy_nominal * 0.7  # 30% haircut for IL + token dump
            apr_base = apy_nominal * 0.4
            apr_rewards = apy_nominal * 0.6
        elif strategy_type == 'altcoin_lp':
            # Alt LPs have high IL
            apy_real = apy_nominal * 0.5  # 50% haircut for high IL + dump
            apr_base = apy_nominal * 0.3
            apr_rewards = apy_nominal * 0.7
        elif strategy_type == 'lending':
            # Lending has no IL, low risk
            apy_real = apy_nominal * 0.97
            apr_base = apy_nominal
            apr_rewards = 0
        else:
            apy_real = apy_nominal * 0.8
            apr_base = apy_nominal * 0.5
            apr_rewards = apy_nominal * 0.5

        # Risk level
        if strategy_type == 'stablecoin' or strategy_type == 'lending':
            risk_level = 'conservative'
        elif strategy_type == 'bluechip_lp':
            risk_level = 'moderate'
        elif strategy_type == 'altcoin_lp':
            risk_level = 'aggressive'
        else:
            risk_level = 'degen'

        # Calculate daily/annual yields (assume $10k investment)
        investment = 10000
        daily_yield = (apy_real / 100 / 365) * investment
        annual_yield = (apy_real / 100) * investment

        # Determine recommendation
        reasons = []
        confidence = 0.0

        if tvl_usd >= self.config['min_tvl_usd']:
            reasons.append(f"TVL ${tvl_usd/1e6:.1f}M exceeds minimum")
            confidence += 0.25

        if protocol_data['age_days'] >= self.config['min_protocol_age_days']:
            reasons.append(f"Protocol age {protocol_data['age_days']} days is mature")
            confidence += 0.25

        if audit_status != 'unaudited':
            reasons.append(f"Protocol is {audit_status}")
            confidence += 0.2

        if apy_real >= self.config['target_apy']:
            reasons.append(f"Real APY {apy_real:.1f}% meets target")
            confidence += 0.3
        else:
            reasons.append(f"⚠️ Real APY {apy_real:.1f}% below {self.config['target_apy']}% target")

        # Wisdom
        if strategy_type == 'stablecoin':
            wisdom = "Stablecoin yields are boring—but boring makes money. This is the foundation of DeFi wealth."
        elif strategy_type == 'bluechip_lp':
            wisdom = "Blue-chip LPs offer balanced risk/reward. Watch for IL when markets get volatile."
        elif strategy_type == 'altcoin_lp':
            wisdom = "Alt-coin LPs are high risk. IL will hurt when tokens diverge. Only for degen mode."
        else:
            wisdom = "High yield usually means high risk. Know what you're getting into."

        # Recommendation
        if confidence >= 0.7:
            recommended = 'enter'
        elif confidence >= 0.5:
            recommended = 'monitor'
        else:
            recommended = 'avoid'
            reasons.append('Risk factors too high')

        opportunity = YieldOpportunity(
            opportunity_id=f"yield_{protocol}_{int(time.time())}",
            protocol=protocol,
            blockchain=protocol_data.get('name', protocol),
            pool_name=pool_name,
            apy_nominal=apy_nominal,
            apy_real=apy_real,
            apr_base=apr_base,
            apr_rewards=apr_rewards,
            tvl_usd=tvl_usd,
            smart_contract_risk=sc_risk,
            audit_status=audit_status,
            protocol_age_days=protocol_data['age_days'],
            impermanent_loss_risk=il_risk,
            estimated_daily_yield_usd=daily_yield,
            estimated_annual_yield_usd=annual_yield,
            breakeven_days=None,
            strategy_type=strategy_type,
            risk_level=risk_level,
            recommended_action=recommended,
            confidence=confidence,
            reasons=reasons,
            wisdom_insight=wisdom
        )

        print(f"   APY (nominal): {apy_nominal:.1f}%")
        print(f"   APY (real): {apy_real:.1f}%")
        print(f"   Risk level: {risk_level}")
        print(f"   Recommendation: {recommended.upper()}")
        print(f"   Wisdom: {wisdom}")

        return opportunity

    def calculate_impermanent_loss(
        self,
        pool_name: str,
        token_a: str,
        token_b: str,
        initial_ratio: float,
        current_ratio: float,
        initial_value_usd: float,
        daily_fee_rate: float = 0.0003  # 0.03% daily fees
    ) -> ImpermanentLossCalculation:
        """
        Calculate impermanent loss for an LP position

        Formula: IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1

        Args:
            initial_ratio: Initial price ratio (token_a / token_b)
            current_ratio: Current price ratio
            initial_value_usd: Initial LP value
            daily_fee_rate: Daily trading fee rate
        """
        print(f"\n💰 Calculating IL for {pool_name}...")

        # Calculate price change
        price_multiplier = current_ratio / initial_ratio
        price_change_pct = (price_multiplier - 1) * 100

        # Impermanent Loss formula
        # IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
        il_multiplier = 2 * math.sqrt(price_multiplier) / (1 + price_multiplier) - 1
        il_pct = il_multiplier * 100
        il_usd = il_multiplier * initial_value_usd

        # Assume 30 days holding, calculate fees earned
        days_held = 30
        trading_fees = initial_value_usd * daily_fee_rate * days_held

        # Net result
        net_usd = trading_fees + il_usd  # IL is negative
        net_pct = (net_usd / initial_value_usd) * 100

        # Breakeven calculation
        fees_to_recover = abs(il_usd)
        if daily_fee_rate > 0:
            days_to_breakeven = fees_to_recover / (initial_value_usd * daily_fee_rate)
        else:
            days_to_breakeven = None

        # Wisdom
        if il_pct < -5:
            wisdom = f"IL of {abs(il_pct):.1f}% is significant. You'd be better off just holding. LPing is not free money."
        elif il_pct < -2:
            wisdom = f"IL of {abs(il_pct):.1f}% is moderate. Trading fees should compensate over time."
        elif il_pct < -0.5:
            wisdom = f"IL of {abs(il_pct):.1f}% is minimal. Low volatility pairs work well for LPs."
        else:
            wisdom = "Negligible IL—stablecoin pairs are safe for LPs."

        calc = ImpermanentLossCalculation(
            pool_name=pool_name,
            token_a=token_a,
            token_b=token_b,
            timestamp=datetime.now().isoformat(),
            initial_price_ratio=initial_ratio,
            initial_value_usd=initial_value_usd,
            current_price_ratio=current_ratio,
            price_change_pct=price_change_pct,
            impermanent_loss_pct=il_pct,
            impermanent_loss_usd=il_usd,
            trading_fees_earned_usd=trading_fees,
            net_profit_loss_usd=net_usd,
            net_profit_loss_pct=net_pct,
            fees_needed_to_recover_il=fees_to_recover,
            days_to_breakeven=days_to_breakeven,
            wisdom_insight=wisdom
        )

        print(f"   Price change: {price_change_pct:+.1f}%")
        print(f"   IL: {il_pct:.2f}% (${il_usd:+,.2f})")
        print(f"   Fees earned: ${trading_fees:,.2f}")
        print(f"   Net: ${net_usd:+,.2f} ({net_pct:+.2f}%)")
        if days_to_breakeven:
            print(f"   Breakeven: {days_to_breakeven:.0f} days")
        print(f"   Wisdom: {wisdom}")

        return calc

    def get_status(self) -> Dict[str, Any]:
        """Get strategist status"""
        return {
            'agent': self.name,
            'philosophy': 'True yield > token emissions. Audited protocols > degen farms. Math > marketing.',
            'protocols_tracked': len(self.protocols),
            'config': self.config,
            'wisdom': 'DeFi promises high yields—but every yield comes with risk. Calculate true returns after IL, fees, and token dumps.'
        }


# Singleton instance
_strategist = None


def get_defi_strategist() -> DeFiStrategist:
    """Get singleton DeFi Strategist"""
    global _strategist
    if _strategist is None:
        _strategist = DeFiStrategist()
    return _strategist


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY DEFI STRATEGIST - THE YIELD FARMING SPECIALIST")
    print("="*70)
    print()

    strategist = get_defi_strategist()

    print("\nStatus:")
    status = strategist.get_status()
    for key, value in status.items():
        if key != 'wisdom':
            print(f"  {key}: {value}")

    print(f"\n💬 Wisdom: {status['wisdom']}")

    # Evaluate yield opportunities
    print("\n\n💰 YIELD OPPORTUNITIES:")
    print("="*70)

    # 1. Conservative: Stablecoin lending
    opp1 = strategist.evaluate_yield_opportunity(
        protocol='aave',
        pool_name='USDC Lending',
        apy_nominal=5.5,
        tvl_usd=500000000,
        strategy_type='stablecoin'
    )

    # 2. Moderate: Blue-chip LP
    opp2 = strategist.evaluate_yield_opportunity(
        protocol='uniswap',
        pool_name='ETH-USDC LP',
        apy_nominal=25.0,
        tvl_usd=200000000,
        strategy_type='bluechip_lp'
    )

    # 3. Aggressive: Alt LP
    opp3 = strategist.evaluate_yield_opportunity(
        protocol='uniswap',
        pool_name='SOL-USDC LP',
        apy_nominal=60.0,
        tvl_usd=50000000,
        strategy_type='altcoin_lp'
    )

    # Calculate impermanent loss
    print("\n\n📉 IMPERMANENT LOSS CALCULATION:")
    print("="*70)

    # ETH doubled in price vs USDC
    il_calc = strategist.calculate_impermanent_loss(
        pool_name='ETH-USDC LP',
        token_a='ETH',
        token_b='USDC',
        initial_ratio=1.0,
        current_ratio=2.0,  # ETH 2x
        initial_value_usd=10000,
        daily_fee_rate=0.0005  # 0.05% daily
    )

    print("\n✅ DeFi Strategist ready to optimize yields")
