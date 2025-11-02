#!/usr/bin/env python3
"""
Unity Chart Master - The Technical Analysis Wizard

Pure technical analysis specialist combining proven APEX strategies:
- MACD trend following (from APEX_MACD_STRATEGY)
- RSI mean reversion (from APEX_RSI_STRATEGY)
- Multi-timeframe analysis (1m, 5m, 15m, 1h, 4h, 1d)
- Bollinger Bands volatility
- Support/Resistance identification

The Chart Master doesn't care about news, narratives, or fundamentals.
IT READS THE CHART. PERIOD.

Wisdom: "The chart never lies. It is the truth written in price action.
Every candle is a battle between bulls and bears. Learn to read the war."

Author: Dr. Claude Summers, Technical Analysis Master
Date: October 16, 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.exchange_clients.kraken_client import get_kraken_client
from tools.technical_analysis.indicators import (
    TechnicalIndicators,
    RSIResult,
    MACDResult,
    BollingerBandsResult,
    analyze_entry_signal
)


@dataclass
class TechnicalSignal:
    """Pure technical trading signal"""
    symbol: str
    timestamp: str
    timeframe: str  # '1m', '5m', '15m', '1h', '4h', '1d'

    # Current price
    current_price: float

    # Indicator values
    rsi: float
    rsi_signal: str  # 'buy', 'sell', 'neutral'
    macd_histogram: float
    macd_signal: str
    bb_percent_b: float  # 0-1 (position in Bollinger Bands)
    bb_signal: str

    # Multi-indicator consensus
    consensus_signal: str  # 'buy', 'sell', 'neutral'
    consensus_strength: float  # 0-1

    # Support/Resistance
    support_levels: List[float]
    resistance_levels: List[float]

    # Signal reasons
    reasons: List[str]

    # Confidence
    confidence: float  # 0-1

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MultiTimeframeAnalysis:
    """Analysis across multiple timeframes"""
    symbol: str
    timestamp: str

    # Timeframe signals
    m1_signal: Optional[TechnicalSignal] = None
    m5_signal: Optional[TechnicalSignal] = None
    m15_signal: Optional[TechnicalSignal] = None
    h1_signal: Optional[TechnicalSignal] = None
    h4_signal: Optional[TechnicalSignal] = None
    d1_signal: Optional[TechnicalSignal] = None

    # Higher timeframe bias
    higher_tf_bias: str  # 'bullish', 'bearish', 'neutral'

    # Trade recommendation
    recommended_action: str  # 'buy', 'sell', 'wait'
    recommended_confidence: float

    # Wisdom
    technical_wisdom: str

    def to_dict(self) -> Dict:
        result = asdict(self)
        # Convert nested dataclasses
        for key in ['m1_signal', 'm5_signal', 'm15_signal', 'h1_signal', 'h4_signal', 'd1_signal']:
            if result[key] is not None:
                result[key] = result[key] if isinstance(result[key], dict) else asdict(result[key])
        return result


class ChartMaster:
    """
    Chart Master - Pure Technical Analysis Specialist

    Philosophy:
    "I don't care about the news. I don't care about fundamentals.
    I don't care about narratives. I READ THE CHART.

    The chart is price action. Price action is truth.
    Every indicator is a lens to see the battle between bulls and bears.

    My job: Identify the trend. Ride the momentum. Exit when it reverses.
    That's it. Nothing more. Nothing less."

    Proven Strategies (from APEX):
    1. MACD Trend Following - Ride the momentum
    2. RSI Mean Reversion - Buy oversold, sell overbought
    3. Bollinger Bands - Volatility breakouts
    4. Multi-timeframe Alignment - Higher TF confirms lower TF
    """

    def __init__(self):
        self.name = "Chart Master"
        self.specializations = [
            "MACD trend following",
            "RSI mean reversion",
            "Bollinger Bands volatility",
            "Multi-timeframe analysis",
            "Support/Resistance identification"
        ]

        # Technical indicators
        self.indicators = TechnicalIndicators()

        # Exchange client
        try:
            self.kraken = get_kraken_client()
        except Exception as e:
            print(f"⚠️  Kraken client not available: {e}")
            self.kraken = None

        # Timeframe configurations (minutes)
        self.timeframes = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }

        print(f"✅ {self.name} initialized")
        print(f"   Specializations: {len(self.specializations)}")

    def analyze_timeframe(
        self,
        symbol: str,
        timeframe: str = '5m'
    ) -> TechnicalSignal:
        """
        Analyze single timeframe with all indicators

        Args:
            symbol: Trading pair (e.g., 'BTC-USD')
            timeframe: '1m', '5m', '15m', '1h', '4h', '1d'
        """
        print(f"📊 Analyzing {symbol} on {timeframe}...")

        # Get candle data
        candles = self._get_candles(symbol, timeframe)

        if len(candles) < 30:
            return self._fallback_signal(symbol, timeframe, "Insufficient candle data")

        # Extract price arrays
        closes = [c['close'] for c in candles]
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        current_price = closes[-1]

        # Calculate all indicators
        rsi_result = self.indicators.calculate_rsi(closes)
        macd_result = self.indicators.calculate_macd(closes)
        bb_result = self.indicators.calculate_bollinger_bands(closes)

        # Support/Resistance (simple: recent swing lows/highs)
        support_levels = self._find_support(lows, current_price)
        resistance_levels = self._find_resistance(highs, current_price)

        # Collect signals and reasons
        signals = []
        reasons = []

        # RSI analysis
        if rsi_result.signal == 'buy':
            signals.append('buy')
            reasons.append(f"RSI oversold at {rsi_result.rsi:.1f}")
        elif rsi_result.signal == 'sell':
            signals.append('sell')
            reasons.append(f"RSI overbought at {rsi_result.rsi:.1f}")

        # MACD analysis
        if macd_result.signal == 'buy':
            signals.append('buy')
            reasons.append(f"MACD bullish (histogram: {macd_result.histogram:.2f})")
        elif macd_result.signal == 'sell':
            signals.append('sell')
            reasons.append(f"MACD bearish (histogram: {macd_result.histogram:.2f})")

        # Bollinger Bands
        if bb_result.signal == 'buy':
            signals.append('buy')
            reasons.append("Price at lower Bollinger Band")
        elif bb_result.signal == 'sell':
            signals.append('sell')
            reasons.append("Price at upper Bollinger Band")

        # Consensus calculation
        buy_count = signals.count('buy')
        sell_count = signals.count('sell')

        if buy_count > sell_count and buy_count >= 2:
            consensus = 'buy'
            strength = min(buy_count / 3, 1.0)
        elif sell_count > buy_count and sell_count >= 2:
            consensus = 'sell'
            strength = min(sell_count / 3, 1.0)
        else:
            consensus = 'neutral'
            strength = 0.0

        # Confidence based on agreement
        confidence = strength * 0.8  # Max 80% confidence from single timeframe

        return TechnicalSignal(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            timeframe=timeframe,
            current_price=current_price,
            rsi=rsi_result.rsi,
            rsi_signal=rsi_result.signal,
            macd_histogram=macd_result.histogram,
            macd_signal=macd_result.signal,
            bb_percent_b=bb_result.percent_b,
            bb_signal=bb_result.signal,
            consensus_signal=consensus,
            consensus_strength=strength,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            reasons=reasons,
            confidence=confidence
        )

    def multi_timeframe_analysis(
        self,
        symbol: str,
        timeframes: Optional[List[str]] = None
    ) -> MultiTimeframeAnalysis:
        """
        Analyze across multiple timeframes for alignment

        Wisdom: "The trend on the 1-day chart is LAW.
        The 4-hour chart is the judge.
        The 1-hour chart is the jury.
        The 5-minute chart is the trigger.

        When all align—THAT is the trade."

        Args:
            symbol: Trading pair
            timeframes: List of timeframes (default: ['5m', '15m', '1h', '4h', '1d'])
        """
        timeframes = timeframes or ['5m', '15m', '1h', '4h', '1d']

        print(f"\n🎯 Multi-timeframe analysis: {symbol}")
        print(f"   Timeframes: {', '.join(timeframes)}")

        signals = {}

        # Analyze each timeframe
        for tf in timeframes:
            try:
                signal = self.analyze_timeframe(symbol, tf)
                signals[tf] = signal
                print(f"   {tf}: {signal.consensus_signal} (conf: {signal.confidence:.1%})")
            except Exception as e:
                print(f"   ⚠️  {tf}: Error - {e}")
                signals[tf] = None

        # Determine higher timeframe bias (4h, 1d)
        higher_tf_signals = []
        for tf in ['4h', '1d']:
            if tf in signals and signals[tf]:
                higher_tf_signals.append(signals[tf].consensus_signal)

        buy_count_htf = higher_tf_signals.count('buy')
        sell_count_htf = higher_tf_signals.count('sell')

        if buy_count_htf > sell_count_htf:
            htf_bias = 'bullish'
        elif sell_count_htf > buy_count_htf:
            htf_bias = 'bearish'
        else:
            htf_bias = 'neutral'

        # Recommend action based on alignment
        # Best case: HTF bullish + lower TF buy signal
        lower_tf_buy = any(signals.get(tf) and signals[tf].consensus_signal == 'buy'
                          for tf in ['5m', '15m', '1h'])
        lower_tf_sell = any(signals.get(tf) and signals[tf].consensus_signal == 'sell'
                           for tf in ['5m', '15m', '1h'])

        if htf_bias == 'bullish' and lower_tf_buy:
            action = 'buy'
            confidence = 0.85
            wisdom = "Higher timeframe bullish, lower timeframe confirms—alignment achieved. The stars are aligned for entry."
        elif htf_bias == 'bearish' and lower_tf_sell:
            action = 'sell'
            confidence = 0.85
            wisdom = "Higher timeframe bearish, lower timeframe confirms—short opportunity present."
        elif htf_bias == 'bullish':
            action = 'wait'
            confidence = 0.5
            wisdom = "Higher timeframe bullish, but lower timeframe not aligned. Patience. Wait for the trigger."
        elif htf_bias == 'bearish':
            action = 'wait'
            confidence = 0.5
            wisdom = "Higher timeframe bearish. Stay defensive. No long entries."
        else:
            action = 'wait'
            confidence = 0.3
            wisdom = "No clear direction across timeframes. Choppy market. The chart is unclear—do not force trades."

        return MultiTimeframeAnalysis(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            m1_signal=signals.get('1m'),
            m5_signal=signals.get('5m'),
            m15_signal=signals.get('15m'),
            h1_signal=signals.get('1h'),
            h4_signal=signals.get('4h'),
            d1_signal=signals.get('1d'),
            higher_tf_bias=htf_bias,
            recommended_action=action,
            recommended_confidence=confidence,
            technical_wisdom=wisdom
        )

    def _get_candles(self, symbol: str, timeframe: str) -> List[Dict]:
        """Get OHLCV candles from Kraken"""
        if not self.kraken:
            return []

        interval_minutes = self.timeframes.get(timeframe, 5)

        try:
            candles = self.kraken.get_candles(symbol, interval=interval_minutes)
            return candles[-100:]  # Last 100 candles
        except Exception as e:
            print(f"⚠️  Candle fetch error: {e}")
            return []

    def _find_support(self, lows: List[float], current_price: float) -> List[float]:
        """Find support levels (simple: recent swing lows below current price)"""
        recent_lows = lows[-50:]  # Last 50 candles
        support = []

        # Find local minima
        for i in range(2, len(recent_lows) - 2):
            if (recent_lows[i] < recent_lows[i-1] and
                recent_lows[i] < recent_lows[i-2] and
                recent_lows[i] < recent_lows[i+1] and
                recent_lows[i] < recent_lows[i+2] and
                recent_lows[i] < current_price):
                support.append(recent_lows[i])

        # Return 3 strongest (lowest) levels
        support.sort()
        return support[:3]

    def _find_resistance(self, highs: List[float], current_price: float) -> List[float]:
        """Find resistance levels (simple: recent swing highs above current price)"""
        recent_highs = highs[-50:]
        resistance = []

        # Find local maxima
        for i in range(2, len(recent_highs) - 2):
            if (recent_highs[i] > recent_highs[i-1] and
                recent_highs[i] > recent_highs[i-2] and
                recent_highs[i] > recent_highs[i+1] and
                recent_highs[i] > recent_highs[i+2] and
                recent_highs[i] > current_price):
                resistance.append(recent_highs[i])

        # Return 3 strongest (highest) levels
        resistance.sort(reverse=True)
        return resistance[:3]

    def _fallback_signal(self, symbol: str, timeframe: str, reason: str) -> TechnicalSignal:
        """Fallback signal when analysis fails"""
        return TechnicalSignal(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            timeframe=timeframe,
            current_price=0.0,
            rsi=50.0,
            rsi_signal='neutral',
            macd_histogram=0.0,
            macd_signal='neutral',
            bb_percent_b=0.5,
            bb_signal='neutral',
            consensus_signal='neutral',
            consensus_strength=0.0,
            support_levels=[],
            resistance_levels=[],
            reasons=[reason],
            confidence=0.0
        )

    def get_status(self) -> Dict[str, Any]:
        """Get Chart Master status"""
        return {
            'agent': self.name,
            'specializations': self.specializations,
            'timeframes_supported': list(self.timeframes.keys()),
            'kraken_connected': self.kraken is not None
        }


# Singleton instance
_chart_master = None


def get_chart_master() -> ChartMaster:
    """Get singleton Chart Master"""
    global _chart_master
    if _chart_master is None:
        _chart_master = ChartMaster()
    return _chart_master


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY CHART MASTER - THE TECHNICAL WIZARD")
    print("="*70)
    print()

    chart_master = get_chart_master()

    print("Status:")
    status = chart_master.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n📊 Single Timeframe Analysis (5m)...")
    signal_5m = chart_master.analyze_timeframe('BTC-USD', '5m')
    print(f"  Signal: {signal_5m.consensus_signal}")
    print(f"  Confidence: {signal_5m.confidence:.1%}")
    print(f"  RSI: {signal_5m.rsi:.1f} ({signal_5m.rsi_signal})")
    print(f"  MACD: {signal_5m.macd_histogram:.2f} ({signal_5m.macd_signal})")
    print(f"  Reasons:")
    for reason in signal_5m.reasons:
        print(f"    - {reason}")

    print("\n🎯 Multi-Timeframe Analysis...")
    mtf = chart_master.multi_timeframe_analysis('BTC-USD', ['5m', '1h', '4h', '1d'])
    print(f"  Higher TF Bias: {mtf.higher_tf_bias}")
    print(f"  Recommended Action: {mtf.recommended_action}")
    print(f"  Confidence: {mtf.recommended_confidence:.1%}")
    print(f"  Wisdom: {mtf.technical_wisdom}")

    print("\n✅ Chart Master ready to read the charts")
