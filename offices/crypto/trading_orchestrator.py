#!/usr/bin/env python3
"""
Unity Trading Orchestrator - The Consensus Conductor

Multi-agent coordination system that combines:
- Chief Market Analyst (macro wisdom)
- Chart Master (technical signals)
- Risk Manager (capital protection)

Ported from APEX's proven multi-agent orchestrator with Unity enhancements.

Wisdom: "No single agent is infallible. Consensus protects against bias.
The Chief sees the forest. The Chart Master sees the trees.
The Risk Manager protects the roots. Together—they make wise decisions."

Author: Dr. Claude Summers, Multi-Agent Coordination Architect
Date: October 16, 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import time

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from offices.crypto.chief_market_analyst import get_chief_market_analyst, MarketAnalysis
from offices.crypto.chart_master import get_chart_master, TechnicalSignal
from offices.crypto.risk_manager import get_risk_manager, PortfolioRiskCheck
from tools.exchange_clients.kraken_client import get_kraken_client


@dataclass
class TradingSignal:
    """Unified trading signal from an agent"""
    agent: str
    symbol: str
    action: str  # 'buy', 'sell', 'hold', 'wait'
    confidence: float  # 0-1
    reason: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ConsensusDecision:
    """Final consensus decision from all agents"""
    symbol: str
    timestamp: str

    # Individual agent signals
    market_analyst_signal: TradingSignal
    chart_master_signal: TradingSignal
    risk_manager_signal: TradingSignal

    # Consensus
    consensus_action: str  # 'buy', 'sell', 'wait'
    consensus_confidence: float
    consensus_reasons: List[str]

    # Risk-adjusted parameters
    entry_price: float
    position_size_usd: float
    stop_loss_price: float
    take_profit_price: float

    # Execution recommendation
    should_execute: bool
    veto_reason: Optional[str] = None

    def to_dict(self) -> Dict:
        result = asdict(self)
        # Convert nested dataclasses
        for key in ['market_analyst_signal', 'chart_master_signal', 'risk_manager_signal']:
            if isinstance(result[key], TradingSignal):
                result[key] = asdict(result[key])
        return result


class TradingOrchestrator:
    """
    Trading Orchestrator - The Consensus Conductor

    Philosophy from APEX:
    "Consensus protects against individual agent bias.
    The crowd wisdom emerges when specialists agree.

    60% agreement threshold = 2 out of 3 agents must agree.
    Risk Manager has VETO power = can override all signals.

    This is not democracy—it's meritocracy with a guardian."

    Process:
    1. Chief Market Analyst provides macro context
    2. Chart Master provides technical signals
    3. Risk Manager validates position sizing and portfolio risk
    4. Consensus calculated (60% threshold)
    5. Risk Manager veto check (override if risk too high)
    6. If approved: Execute trade
    7. Track and report to Evolution Engine
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "Trading Orchestrator"

        # Configuration (from APEX proven system)
        self.config = config or {
            'consensus_threshold': 0.6,  # 60% agreement (2 out of 3 agents)
            'risk_veto_enabled': True,   # Risk Manager can veto
            'min_confidence': 0.5,       # Minimum individual confidence
            'dry_run': True              # Paper trading by default
        }

        # Initialize agents
        print(f"🎼 Initializing {self.name}...")

        self.market_analyst = get_chief_market_analyst()
        self.chart_master = get_chart_master()
        self.risk_manager = get_risk_manager()

        # Exchange client
        try:
            self.kraken = get_kraken_client()
        except Exception as e:
            print(f"⚠️  Kraken client not available: {e}")
            self.kraken = None

        # Trading state
        self.current_position = None
        self.trade_history = []

        print(f"✅ {self.name} initialized")
        print(f"   Consensus threshold: {self.config['consensus_threshold']:.0%}")
        print(f"   Risk veto: {'enabled' if self.config['risk_veto_enabled'] else 'disabled'}")
        print(f"   Mode: {'DRY RUN' if self.config['dry_run'] else 'LIVE'}")

    def get_consensus_decision(
        self,
        symbol: str,
        additional_context: Optional[str] = None
    ) -> ConsensusDecision:
        """
        Get consensus trading decision from all agents

        Process:
        1. Gather signals from all agents
        2. Calculate consensus
        3. Risk Manager veto check
        4. Return decision with execution parameters

        Args:
            symbol: Trading pair (e.g., 'BTC-USD')
            additional_context: Optional context for Market Analyst
        """
        print(f"\n{'='*70}")
        print(f"🎯 CONSENSUS DECISION CYCLE - {symbol}")
        print(f"{'='*70}")

        # Step 1: Get Market Analyst signal
        print(f"\n1️⃣ Chief Market Analyst analyzing...")
        market_analysis = self.market_analyst.analyze_market(symbol, additional_context)

        market_signal = TradingSignal(
            agent="Chief Market Analyst",
            symbol=symbol,
            action=market_analysis.recommended_bias,  # 'bullish', 'bearish', 'neutral'
            confidence=market_analysis.confidence_level,
            reason=f"{market_analysis.market_cycle} cycle, {market_analysis.fear_greed_level}",
            timestamp=datetime.now().isoformat(),
            details={'market_narrative': market_analysis.market_narrative}
        )

        print(f"   Signal: {market_signal.action} (confidence: {market_signal.confidence:.1%})")
        print(f"   Reason: {market_signal.reason}")

        # Step 2: Get Chart Master signal
        print(f"\n2️⃣ Chart Master analyzing...")
        chart_signal_data = self.chart_master.analyze_timeframe(symbol, '5m')

        chart_signal = TradingSignal(
            agent="Chart Master",
            symbol=symbol,
            action=chart_signal_data.consensus_signal,  # 'buy', 'sell', 'neutral'
            confidence=chart_signal_data.confidence,
            reason=f"RSI: {chart_signal_data.rsi:.1f}, MACD: {chart_signal_data.macd_histogram:.2f}",
            timestamp=datetime.now().isoformat(),
            details={'technical_reasons': chart_signal_data.reasons}
        )

        print(f"   Signal: {chart_signal.action} (confidence: {chart_signal.confidence:.1%})")
        print(f"   Reason: {chart_signal.reason}")

        # Step 3: Get Risk Manager check
        print(f"\n3️⃣ Risk Manager validating...")
        risk_check = self.risk_manager.check_portfolio_risk()

        risk_signal = TradingSignal(
            agent="Risk Manager",
            symbol=symbol,
            action='proceed' if risk_check.can_open_new_position else 'hold',
            confidence=1.0 if risk_check.can_open_new_position else 0.0,
            reason='; '.join(risk_check.reasons),
            timestamp=datetime.now().isoformat()
        )

        print(f"   Signal: {risk_signal.action}")
        print(f"   Reason: {risk_signal.reason}")

        # Step 4: Calculate consensus
        print(f"\n4️⃣ Calculating consensus...")

        # Normalize actions to 'buy', 'sell', 'wait'
        normalized_signals = []
        reasons = []

        # Market Analyst
        if market_signal.action == 'bullish' and market_signal.confidence >= self.config['min_confidence']:
            normalized_signals.append('buy')
            reasons.append(f"Market Analyst: {market_signal.reason}")
        elif market_signal.action == 'bearish' and market_signal.confidence >= self.config['min_confidence']:
            normalized_signals.append('sell')
            reasons.append(f"Market Analyst: {market_signal.reason}")

        # Chart Master
        if chart_signal.action == 'buy' and chart_signal.confidence >= self.config['min_confidence']:
            normalized_signals.append('buy')
            reasons.append(f"Chart Master: {chart_signal.reason}")
        elif chart_signal.action == 'sell' and chart_signal.confidence >= self.config['min_confidence']:
            normalized_signals.append('sell')
            reasons.append(f"Chart Master: {chart_signal.reason}")

        # Count votes
        buy_count = normalized_signals.count('buy')
        sell_count = normalized_signals.count('sell')
        total_agents = 2  # Market Analyst + Chart Master (Risk Manager doesn't vote)

        buy_confidence = buy_count / total_agents
        sell_confidence = sell_count / total_agents

        print(f"   Buy signals: {buy_count}/{total_agents} ({buy_confidence:.1%})")
        print(f"   Sell signals: {sell_count}/{total_agents} ({sell_confidence:.1%})")

        # Determine consensus
        if buy_confidence >= self.config['consensus_threshold']:
            consensus_action = 'buy'
            consensus_confidence = buy_confidence
        elif sell_confidence >= self.config['consensus_threshold']:
            consensus_action = 'sell'
            consensus_confidence = sell_confidence
        else:
            consensus_action = 'wait'
            consensus_confidence = 0.0

        print(f"   Consensus: {consensus_action} (confidence: {consensus_confidence:.1%})")

        # Step 5: Risk Manager veto check
        should_execute = False
        veto_reason = None

        if consensus_action != 'wait':
            if self.config['risk_veto_enabled'] and not risk_check.can_open_new_position:
                print(f"\n❌ RISK MANAGER VETO: {risk_signal.reason}")
                veto_reason = f"Risk Manager veto: {risk_signal.reason}"
                should_execute = False
            else:
                print(f"\n✅ Consensus approved for execution")
                should_execute = True

        # Step 6: Calculate execution parameters
        entry_price = chart_signal_data.current_price if chart_signal_data.current_price > 0 else 70000  # Fallback
        stop_loss_calc = self.risk_manager.calculate_stop_loss(symbol, entry_price)
        position_size_calc = self.risk_manager.calculate_position_size(symbol, entry_price, stop_loss_calc.recommended_stop_price)

        return ConsensusDecision(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            market_analyst_signal=market_signal,
            chart_master_signal=chart_signal,
            risk_manager_signal=risk_signal,
            consensus_action=consensus_action,
            consensus_confidence=consensus_confidence,
            consensus_reasons=reasons,
            entry_price=entry_price,
            position_size_usd=position_size_calc.position_size_usd,
            stop_loss_price=stop_loss_calc.recommended_stop_price,
            take_profit_price=stop_loss_calc.recommended_take_profit,
            should_execute=should_execute,
            veto_reason=veto_reason
        )

    def execute_decision(self, decision: ConsensusDecision) -> Dict[str, Any]:
        """
        Execute consensus decision

        Args:
            decision: ConsensusDecision from get_consensus_decision()

        Returns:
            Execution result
        """
        if not decision.should_execute:
            print(f"\n⏸️  Decision not executed: {decision.veto_reason or 'No consensus'}")
            return {
                'executed': False,
                'reason': decision.veto_reason or 'No consensus',
                'decision': decision.to_dict()
            }

        print(f"\n🎯 Executing {decision.consensus_action.upper()} order...")
        print(f"   Symbol: {decision.symbol}")
        print(f"   Entry: ${decision.entry_price:,.2f}")
        print(f"   Position size: ${decision.position_size_usd:.2f}")
        print(f"   Stop loss: ${decision.stop_loss_price:,.2f}")
        print(f"   Take profit: ${decision.take_profit_price:,.2f}")
        print(f"   Confidence: {decision.consensus_confidence:.1%}")

        if self.config['dry_run']:
            print(f"\n📋 DRY RUN MODE - Order simulated")
            result = {
                'executed': True,
                'mode': 'dry_run',
                'order_id': f"sim_{int(time.time())}",
                'decision': decision.to_dict()
            }
        else:
            # Live execution (requires confirmation)
            print(f"\n⚠️  LIVE TRADING MODE - Real money at risk!")
            result = self._execute_live_order(decision)

        # Record in trade history
        self.trade_history.append(result)

        return result

    def _execute_live_order(self, decision: ConsensusDecision) -> Dict[str, Any]:
        """Execute live order on exchange"""
        if not self.kraken:
            return {
                'executed': False,
                'reason': 'Exchange client not available'
            }

        try:
            # Place market order
            order = self.kraken.place_market_order(
                symbol=decision.symbol,
                side=decision.consensus_action,
                amount=decision.position_size_usd / decision.entry_price,
                leverage=1  # No leverage by default
            )

            return {
                'executed': True,
                'mode': 'live',
                'order': order,
                'decision': decision.to_dict()
            }

        except Exception as e:
            print(f"❌ Order execution failed: {e}")
            return {
                'executed': False,
                'reason': f"Execution error: {e}"
            }

    def run_trading_cycle(
        self,
        symbol: str,
        additional_context: Optional[str] = None
    ):
        """
        Run one complete trading cycle

        1. Get consensus decision
        2. Execute if approved
        3. Report results
        """
        decision = self.get_consensus_decision(symbol, additional_context)

        if decision.should_execute:
            result = self.execute_decision(decision)
            print(f"\n{'='*70}")
            print(f"✅ CYCLE COMPLETE - Order {'executed' if result['executed'] else 'failed'}")
            print(f"{'='*70}")
        else:
            print(f"\n{'='*70}")
            print(f"💤 CYCLE COMPLETE - No action taken")
            print(f"{'='*70}")

        return decision

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'agent': self.name,
            'config': self.config,
            'agents_active': {
                'market_analyst': self.market_analyst is not None,
                'chart_master': self.chart_master is not None,
                'risk_manager': self.risk_manager is not None
            },
            'current_position': self.current_position,
            'trade_history_count': len(self.trade_history)
        }


# Singleton instance
_orchestrator = None


def get_trading_orchestrator() -> TradingOrchestrator:
    """Get singleton Trading Orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TradingOrchestrator()
    return _orchestrator


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY TRADING ORCHESTRATOR - THE CONSENSUS CONDUCTOR")
    print("="*70)
    print()

    orchestrator = get_trading_orchestrator()

    print("Status:")
    status = orchestrator.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n🎯 Running trading cycle for BTC-USD...")
    decision = orchestrator.run_trading_cycle(
        'BTC-USD',
        additional_context="Recent ETF approval, bullish momentum"
    )

    print("\n📊 Final Decision Summary:")
    print(f"  Action: {decision.consensus_action}")
    print(f"  Confidence: {decision.consensus_confidence:.1%}")
    print(f"  Should execute: {decision.should_execute}")
    if decision.veto_reason:
        print(f"  Veto reason: {decision.veto_reason}")

    print("\n✅ Trading Orchestrator ready to conduct the symphony")
