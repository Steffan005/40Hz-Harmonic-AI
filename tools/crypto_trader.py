"""
CRYPTO TRADING OFFICE - REAL MARKET INTELLIGENCE
Phase 14.1: Integration with multiple exchanges via ccxt
Provides LIVE price data, technical analysis, and orderbook depth
"""

import ccxt
from typing import Dict, List, Optional
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CryptoTrader:
    """
    Real-time cryptocurrency market analysis and trading intelligence
    Connects to major exchanges: Binance, Coinbase, Kraken
    Provides technical indicators (RSI, SMA, MACD)
    """

    def __init__(self):
        """Initialize connections to major crypto exchanges"""
        self.exchanges = {
            'binance': ccxt.binance({
                'enableRateLimit': True,
                'timeout': 30000,
            }),
            'coinbase': ccxt.coinbase({
                'enableRateLimit': True,
                'timeout': 30000,
            }),
            'kraken': ccxt.kraken({
                'enableRateLimit': True,
                'timeout': 30000,
            })
        }

        logger.info("🔥 Crypto Trading Office initialized with 3 exchanges")

    def get_price(self, symbol: str, exchange: str = 'binance') -> Dict:
        """
        Get current price for a cryptocurrency pair

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT', 'ETH/USD')
            exchange: Exchange to query (binance, coinbase, kraken)

        Returns:
            Dict with price, volume, change data
        """
        try:
            if exchange not in self.exchanges:
                raise ValueError(f"Unknown exchange: {exchange}")

            ticker = self.exchanges[exchange].fetch_ticker(symbol)

            return {
                'symbol': symbol,
                'exchange': exchange,
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume_24h': ticker['baseVolume'],
                'change_24h_pct': ticker['percentage'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'timestamp': ticker['timestamp'],
                'datetime': ticker['datetime']
            }
        except Exception as e:
            logger.error(f"Error fetching price for {symbol} on {exchange}: {e}")
            return {
                'error': str(e),
                'symbol': symbol,
                'exchange': exchange
            }

    def get_orderbook(self, symbol: str, exchange: str = 'binance', depth: int = 20) -> Dict:
        """
        Get orderbook depth (bids/asks)

        Args:
            symbol: Trading pair
            exchange: Exchange to query
            depth: Number of levels to retrieve

        Returns:
            Dict with bids, asks, spread
        """
        try:
            if exchange not in self.exchanges:
                raise ValueError(f"Unknown exchange: {exchange}")

            orderbook = self.exchanges[exchange].fetch_order_book(symbol, limit=depth)

            bids = orderbook['bids'][:depth]  # [[price, amount], ...]
            asks = orderbook['asks'][:depth]

            # Calculate spread
            best_bid = bids[0][0] if bids else 0
            best_ask = asks[0][0] if asks else 0
            spread = best_ask - best_bid if best_bid and best_ask else 0
            spread_pct = (spread / best_ask * 100) if best_ask else 0

            return {
                'symbol': symbol,
                'exchange': exchange,
                'bids': bids,
                'asks': asks,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': spread,
                'spread_pct': spread_pct,
                'timestamp': orderbook['timestamp'],
                'datetime': orderbook['datetime']
            }
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol} on {exchange}: {e}")
            return {
                'error': str(e),
                'symbol': symbol,
                'exchange': exchange
            }

    def technical_analysis(self, symbol: str, timeframe: str = '1h', exchange: str = 'binance') -> Dict:
        """
        Calculate technical indicators (RSI, SMA, EMA, MACD)

        Args:
            symbol: Trading pair
            timeframe: Candlestick interval ('1m', '5m', '15m', '1h', '4h', '1d')
            exchange: Exchange to query

        Returns:
            Dict with technical indicators and trend analysis
        """
        try:
            if exchange not in self.exchanges:
                raise ValueError(f"Unknown exchange: {exchange}")

            # Fetch OHLCV data (100 candles for indicator calculation)
            ohlcv = self.exchanges[exchange].fetch_ohlcv(symbol, timeframe, limit=100)

            if not ohlcv or len(ohlcv) < 50:
                return {'error': 'Insufficient data for technical analysis'}

            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Calculate Simple Moving Averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()

            # Calculate Exponential Moving Averages
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

            # Calculate RSI (Relative Strength Index)
            df['rsi'] = self._calculate_rsi(df['close'])

            # Calculate MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']

            # Get latest values
            latest = df.iloc[-1]

            # Determine trend
            trend = 'bullish' if latest['sma_20'] > latest['sma_50'] else 'bearish'
            macd_signal = 'bullish' if latest['macd'] > latest['macd_signal'] else 'bearish'

            # RSI interpretation
            rsi_value = latest['rsi']
            if rsi_value > 70:
                rsi_signal = 'overbought'
            elif rsi_value < 30:
                rsi_signal = 'oversold'
            else:
                rsi_signal = 'neutral'

            return {
                'symbol': symbol,
                'exchange': exchange,
                'timeframe': timeframe,
                'current_price': latest['close'],
                'sma_20': latest['sma_20'],
                'sma_50': latest['sma_50'],
                'ema_12': latest['ema_12'],
                'ema_26': latest['ema_26'],
                'rsi': rsi_value,
                'rsi_signal': rsi_signal,
                'macd': latest['macd'],
                'macd_signal': latest['macd_signal'],
                'macd_histogram': latest['macd_histogram'],
                'macd_signal_name': macd_signal,
                'trend': trend,
                'volume': latest['volume'],
                'timestamp': int(latest['timestamp']),
                'datetime': str(latest['datetime'])
            }
        except Exception as e:
            logger.error(f"Error in technical analysis for {symbol} on {exchange}: {e}")
            return {
                'error': str(e),
                'symbol': symbol,
                'exchange': exchange
            }

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index)

        Args:
            prices: Series of closing prices
            period: RSI period (default 14)

        Returns:
            Series of RSI values
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Avoid division by zero
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def compare_exchanges(self, symbol: str) -> Dict:
        """
        Compare prices across all exchanges for arbitrage opportunities

        Args:
            symbol: Trading pair

        Returns:
            Dict with prices from all exchanges and arbitrage data
        """
        prices = {}

        for exchange_name in self.exchanges.keys():
            try:
                ticker = self.exchanges[exchange_name].fetch_ticker(symbol)
                prices[exchange_name] = {
                    'price': ticker['last'],
                    'volume': ticker['baseVolume']
                }
            except Exception as e:
                logger.warning(f"Could not fetch {symbol} from {exchange_name}: {e}")
                prices[exchange_name] = {'error': str(e)}

        # Find arbitrage opportunities
        valid_prices = {k: v['price'] for k, v in prices.items() if 'price' in v}

        if len(valid_prices) >= 2:
            min_exchange = min(valid_prices, key=valid_prices.get)
            max_exchange = max(valid_prices, key=valid_prices.get)
            min_price = valid_prices[min_exchange]
            max_price = valid_prices[max_exchange]

            arbitrage_pct = ((max_price - min_price) / min_price) * 100

            return {
                'symbol': symbol,
                'prices': prices,
                'arbitrage': {
                    'opportunity': arbitrage_pct > 0.5,  # Profitable if > 0.5% (covers fees)
                    'buy_from': min_exchange,
                    'sell_to': max_exchange,
                    'buy_price': min_price,
                    'sell_price': max_price,
                    'profit_pct': arbitrage_pct
                }
            }
        else:
            return {
                'symbol': symbol,
                'prices': prices,
                'arbitrage': {'opportunity': False, 'reason': 'Insufficient data'}
            }

    def get_trending_coins(self, exchange: str = 'binance', limit: int = 10) -> List[Dict]:
        """
        Get top trending cryptocurrencies by 24h volume

        Args:
            exchange: Exchange to query
            limit: Number of coins to return

        Returns:
            List of dicts with coin data sorted by volume
        """
        try:
            if exchange not in self.exchanges:
                raise ValueError(f"Unknown exchange: {exchange}")

            # Fetch all tickers
            tickers = self.exchanges[exchange].fetch_tickers()

            # Filter USDT pairs and sort by volume
            usdt_pairs = {}
            for symbol, ticker in tickers.items():
                if '/USDT' in symbol and ticker['quoteVolume']:
                    usdt_pairs[symbol] = {
                        'symbol': symbol,
                        'price': ticker['last'],
                        'change_24h': ticker['percentage'],
                        'volume_24h': ticker['quoteVolume'],
                        'high_24h': ticker['high'],
                        'low_24h': ticker['low']
                    }

            # Sort by volume and return top N
            trending = sorted(
                usdt_pairs.values(),
                key=lambda x: x['volume_24h'],
                reverse=True
            )[:limit]

            return trending
        except Exception as e:
            logger.error(f"Error fetching trending coins from {exchange}: {e}")
            return [{'error': str(e)}]


# Singleton instance
crypto_trader = CryptoTrader()
