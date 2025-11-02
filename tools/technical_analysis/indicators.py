#!/usr/bin/env python3
"""
Unity Technical Analysis Indicators

Proven indicators ported from APEX trading system.
Includes: RSI, MACD, EMA, Bollinger Bands, ATR, and more.

Wisdom: Technical indicators are not crystal balls—they are lenses.
They reveal patterns in the chaos. But remember: the map is not the territory.
Every indicator lags. Every signal can fail. Use them with wisdom, not blind faith.

Author: Dr. Claude Summers, Technical Analysis Architect
Date: October 16, 2025
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RSIResult:
    """RSI calculation result"""
    rsi: float
    is_oversold: bool  # RSI < 30
    is_overbought: bool  # RSI > 70
    signal: str  # 'buy', 'sell', 'neutral'
    strength: float  # 0-1


@dataclass
class MACDResult:
    """MACD calculation result"""
    macd_line: float
    signal_line: float
    histogram: float
    signal: str  # 'buy', 'sell', 'neutral'
    strength: float


@dataclass
class BollingerBandsResult:
    """Bollinger Bands result"""
    upper_band: float
    middle_band: float  # SMA
    lower_band: float
    current_price: float
    percent_b: float  # Position within bands (0-1)
    bandwidth: float  # Width of bands
    signal: str


class TechnicalIndicators:
    """
    Technical Analysis Indicators Library

    Provides battle-tested indicators from APEX trading system:
    - RSI (Relative Strength Index) - Mean reversion
    - MACD (Moving Average Convergence Divergence) - Trend following
    - EMA (Exponential Moving Average) - Smoothing
    - Bollinger Bands - Volatility
    - ATR (Average True Range) - Volatility measurement

    All methods use numpy for performance.
    """

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> float:
        """
        Calculate Exponential Moving Average

        Args:
            prices: Price series (oldest to newest)
            period: EMA period

        Returns:
            Current EMA value
        """
        if len(prices) < period:
            return np.mean(prices) if prices else 0.0

        prices_array = np.array(prices)
        multiplier = 2 / (period + 1)

        # Start with first price
        ema = [prices_array[0]]

        # Calculate EMA iteratively
        for price in prices_array[1:]:
            ema.append((price * multiplier) + (ema[-1] * (1 - multiplier)))

        return ema[-1]

    @staticmethod
    def calculate_rsi(
        prices: List[float],
        period: int = 14,
        oversold_threshold: float = 30,
        overbought_threshold: float = 70
    ) -> RSIResult:
        """
        Calculate Relative Strength Index (RSI)

        Proven mean reversion indicator from APEX system.

        Args:
            prices: Price series (oldest to newest)
            period: RSI period (default 14)
            oversold_threshold: Buy signal threshold (default 30)
            overbought_threshold: Sell signal threshold (default 70)

        Returns:
            RSIResult with value, signals, and strength

        Wisdom: "Markets oscillate. When fear is extreme (RSI < 30), buy.
        When greed is extreme (RSI > 70), sell. The pendulum always swings back."
        """
        if len(prices) < period + 1:
            return RSIResult(
                rsi=50,  # Neutral
                is_oversold=False,
                is_overbought=False,
                signal='neutral',
                strength=0.0
            )

        prices_array = np.array(prices)
        deltas = np.diff(prices_array)

        # Separate gains and losses
        gains = deltas.copy()
        losses = deltas.copy()
        gains[gains < 0] = 0
        losses[losses > 0] = 0
        losses = np.abs(losses)

        # Calculate average gains and losses
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # Determine signals
        is_oversold = rsi < oversold_threshold
        is_overbought = rsi > overbought_threshold

        if is_oversold:
            signal = 'buy'
            strength = (oversold_threshold - rsi) / oversold_threshold
        elif is_overbought:
            signal = 'sell'
            strength = (rsi - overbought_threshold) / (100 - overbought_threshold)
        else:
            signal = 'neutral'
            strength = 0.0

        return RSIResult(
            rsi=rsi,
            is_oversold=is_oversold,
            is_overbought=is_overbought,
            signal=signal,
            strength=min(strength, 1.0)
        )

    @staticmethod
    def calculate_macd(
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> MACDResult:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Proven trend-following indicator from APEX system.

        Args:
            prices: Price series (oldest to newest)
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line EMA period (default 9)

        Returns:
            MACDResult with line, signal, histogram, and trading signal

        Wisdom: "Trends are your friend until they end. MACD captures momentum.
        When histogram turns positive and MACD is above zero—ride the bull.
        When it turns negative—the bear awakens."
        """
        if len(prices) < slow_period:
            return MACDResult(
                macd_line=0,
                signal_line=0,
                histogram=0,
                signal='neutral',
                strength=0.0
            )

        # Calculate fast and slow EMAs
        fast_ema = TechnicalIndicators.calculate_ema(prices, fast_period)
        slow_ema = TechnicalIndicators.calculate_ema(prices, slow_period)

        macd_line = fast_ema - slow_ema

        # Signal line (EMA of MACD - simplified for single point)
        # In production, would maintain MACD history for proper EMA
        signal_line = macd_line * 0.8  # Approximation

        histogram = macd_line - signal_line

        # Determine signal
        if histogram > 0 and macd_line > 0:
            signal = 'buy'
            strength = min(abs(histogram) / 100, 1.0)
        elif histogram < 0 and macd_line < 0:
            signal = 'sell'
            strength = min(abs(histogram) / 100, 1.0)
        else:
            signal = 'neutral'
            strength = 0.0

        return MACDResult(
            macd_line=macd_line,
            signal_line=signal_line,
            histogram=histogram,
            signal=signal,
            strength=strength
        )

    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """
        Calculate Simple Moving Average

        Args:
            prices: Price series
            period: SMA period
        """
        if len(prices) < period:
            return np.mean(prices) if prices else 0.0

        return np.mean(prices[-period:])

    @staticmethod
    def calculate_bollinger_bands(
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> BollingerBandsResult:
        """
        Calculate Bollinger Bands

        Args:
            prices: Price series
            period: Moving average period (default 20)
            std_dev: Standard deviation multiplier (default 2.0)

        Returns:
            BollingerBandsResult with upper/middle/lower bands and signals

        Wisdom: "Bollinger Bands measure volatility. When bands squeeze tight,
        expect an explosion. When price touches lower band—oversold.
        Upper band—overbought. But remember: trending markets walk the bands."
        """
        if len(prices) < period:
            current_price = prices[-1] if prices else 0.0
            return BollingerBandsResult(
                upper_band=current_price,
                middle_band=current_price,
                lower_band=current_price,
                current_price=current_price,
                percent_b=0.5,
                bandwidth=0.0,
                signal='neutral'
            )

        prices_array = np.array(prices[-period:])

        # Middle band = SMA
        middle_band = np.mean(prices_array)

        # Calculate standard deviation
        std = np.std(prices_array)

        # Upper and lower bands
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)

        current_price = prices[-1]

        # %B = (price - lower) / (upper - lower)
        bandwidth = upper_band - lower_band
        if bandwidth > 0:
            percent_b = (current_price - lower_band) / bandwidth
        else:
            percent_b = 0.5

        # Determine signal
        if current_price <= lower_band:
            signal = 'buy'  # Oversold
        elif current_price >= upper_band:
            signal = 'sell'  # Overbought
        else:
            signal = 'neutral'

        return BollingerBandsResult(
            upper_band=upper_band,
            middle_band=middle_band,
            lower_band=lower_band,
            current_price=current_price,
            percent_b=percent_b,
            bandwidth=bandwidth,
            signal=signal
        )

    @staticmethod
    def calculate_atr(
        high_prices: List[float],
        low_prices: List[float],
        close_prices: List[float],
        period: int = 14
    ) -> float:
        """
        Calculate Average True Range (ATR)

        Measures volatility - used for stop-loss placement.

        Args:
            high_prices: High prices
            low_prices: Low prices
            close_prices: Close prices
            period: ATR period (default 14)

        Returns:
            Current ATR value

        Wisdom: "ATR measures market breath. In calm markets, ATR is small.
        In chaos, ATR explodes. Use 2x ATR for stop losses—it respects
        the market's natural volatility."
        """
        if len(high_prices) < period or len(low_prices) < period or len(close_prices) < period:
            return 0.0

        true_ranges = []

        for i in range(1, len(high_prices)):
            high_low = high_prices[i] - low_prices[i]
            high_close = abs(high_prices[i] - close_prices[i - 1])
            low_close = abs(low_prices[i] - close_prices[i - 1])

            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)

        # Calculate average
        atr = np.mean(true_ranges[-period:])

        return atr

    @staticmethod
    def calculate_momentum(prices: List[float], period: int = 10) -> float:
        """
        Calculate momentum (rate of change)

        Args:
            prices: Price series
            period: Lookback period

        Returns:
            Momentum value (percent change)
        """
        if len(prices) < period + 1:
            return 0.0

        current_price = prices[-1]
        past_price = prices[-period - 1]

        if past_price == 0:
            return 0.0

        momentum = ((current_price - past_price) / past_price) * 100

        return momentum


# Convenience functions
def analyze_entry_signal(prices: List[float]) -> dict:
    """
    Comprehensive entry signal analysis

    Combines RSI + MACD + Bollinger Bands for consensus

    Returns:
        Dictionary with signal, confidence, and reasons
    """
    if len(prices) < 30:
        return {
            'signal': 'neutral',
            'confidence': 0.0,
            'reasons': ['Insufficient price data']
        }

    indicators = TechnicalIndicators()

    # Calculate indicators
    rsi = indicators.calculate_rsi(prices)
    macd = indicators.calculate_macd(prices)
    bb = indicators.calculate_bollinger_bands(prices)

    # Collect signals
    signals = []
    reasons = []

    if rsi.signal == 'buy':
        signals.append('buy')
        reasons.append(f"RSI oversold ({rsi.rsi:.1f})")

    if rsi.signal == 'sell':
        signals.append('sell')
        reasons.append(f"RSI overbought ({rsi.rsi:.1f})")

    if macd.signal == 'buy':
        signals.append('buy')
        reasons.append(f"MACD bullish (histogram: {macd.histogram:.2f})")

    if macd.signal == 'sell':
        signals.append('sell')
        reasons.append(f"MACD bearish (histogram: {macd.histogram:.2f})")

    if bb.signal == 'buy':
        signals.append('buy')
        reasons.append("Price at lower Bollinger Band")

    if bb.signal == 'sell':
        signals.append('sell')
        reasons.append("Price at upper Bollinger Band")

    # Calculate consensus
    buy_count = signals.count('buy')
    sell_count = signals.count('sell')

    if buy_count > sell_count and buy_count >= 2:
        final_signal = 'buy'
        confidence = min((buy_count / 3) * 0.8, 1.0)
    elif sell_count > buy_count and sell_count >= 2:
        final_signal = 'sell'
        confidence = min((sell_count / 3) * 0.8, 1.0)
    else:
        final_signal = 'neutral'
        confidence = 0.0

    return {
        'signal': final_signal,
        'confidence': confidence,
        'reasons': reasons,
        'rsi': rsi.rsi,
        'macd_histogram': macd.histogram,
        'bollinger_percent_b': bb.percent_b
    }


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY TECHNICAL INDICATORS TEST")
    print("="*70)
    print()

    # Test data: simulated BTC prices
    test_prices = [
        67000, 67500, 68000, 67800, 67200, 66800, 66500, 66000, 65500, 65200,
        65000, 64800, 64500, 64200, 63900, 63800, 63700, 64000, 64500, 65000,
        65500, 66000, 66500, 67000, 67500, 68000, 68500, 69000, 69500, 70000
    ]

    indicators = TechnicalIndicators()

    print("📊 Testing RSI...")
    rsi = indicators.calculate_rsi(test_prices)
    print(f"  RSI: {rsi.rsi:.2f}")
    print(f"  Signal: {rsi.signal}")
    print(f"  Strength: {rsi.strength:.2%}")
    print(f"  Oversold: {rsi.is_oversold}, Overbought: {rsi.is_overbought}")

    print("\n📈 Testing MACD...")
    macd = indicators.calculate_macd(test_prices)
    print(f"  MACD Line: {macd.macd_line:.2f}")
    print(f"  Signal Line: {macd.signal_line:.2f}")
    print(f"  Histogram: {macd.histogram:.2f}")
    print(f"  Signal: {macd.signal}")
    print(f"  Strength: {macd.strength:.2%}")

    print("\n📉 Testing Bollinger Bands...")
    bb = indicators.calculate_bollinger_bands(test_prices)
    print(f"  Upper Band: ${bb.upper_band:,.2f}")
    print(f"  Middle Band: ${bb.middle_band:,.2f}")
    print(f"  Lower Band: ${bb.lower_band:,.2f}")
    print(f"  Current Price: ${bb.current_price:,.2f}")
    print(f"  %B: {bb.percent_b:.2%}")
    print(f"  Signal: {bb.signal}")

    print("\n🎯 Testing Comprehensive Analysis...")
    analysis = analyze_entry_signal(test_prices)
    print(f"  Final Signal: {analysis['signal']}")
    print(f"  Confidence: {analysis['confidence']:.1%}")
    print(f"  Reasons:")
    for reason in analysis['reasons']:
        print(f"    - {reason}")

    print("\n✅ Technical indicators test complete")
