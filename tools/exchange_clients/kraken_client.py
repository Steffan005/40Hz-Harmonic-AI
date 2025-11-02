#!/usr/bin/env python3
"""
Unity Kraken API Client

Unified interface for Kraken API with 10x leverage support.
Ported from APEX trading system with Unity enhancements.

Wisdom: Kraken is the deep ocean of crypto exchanges. Navigate with care.
Leverage is a double-edged sword—it magnifies both gains and losses.
Use it with respect, or it will consume you.

Author: Dr. Claude Summers, Crypto Trading Architect
Date: October 16, 2025
"""

import os
import time
import krakenex
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Ticker:
    """Real-time ticker data"""
    symbol: str
    last: float
    bid: float
    ask: float
    volume_24h: float
    timestamp: str


@dataclass
class OrderBook:
    """Order book snapshot"""
    symbol: str
    bids: List[tuple]  # [(price, size), ...]
    asks: List[tuple]  # [(price, size), ...]
    timestamp: str


@dataclass
class Balance:
    """Account balance"""
    currency: str
    available: float
    held: float
    total: float


@dataclass
class Position:
    """Open position (margin trading)"""
    position_id: str
    symbol: str
    side: str  # 'long' or 'short'
    size: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_pct: float
    leverage: float
    timestamp: str


class KrakenClient:
    """
    Kraken API Client

    Provides unified interface for:
    - Market data (ticker, order book, OHLCV)
    - Account info (balances, positions)
    - Order management (market, limit, margin orders)
    - 10x leverage support (via margin trading)

    Wisdom: Kraken has one of the most robust APIs in crypto.
    It rewards patience and punishes haste. Always check response errors.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv('KRAKEN_API_KEY')
        self.api_secret = api_secret or os.getenv('KRAKEN_SECRET_KEY')

        if not self.api_key or not self.api_secret:
            raise ValueError("Kraken API credentials required (env: KRAKEN_API_KEY, KRAKEN_SECRET_KEY)")

        # Initialize krakenex
        self.kraken = krakenex.API()
        self.kraken.key = self.api_key
        self.kraken.secret = self.api_secret

        # Rate limiting (Kraken: 15-20 req/sec, but be conservative)
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 5 requests per second

        # Pair mapping (Kraken uses different symbols)
        self.pair_map = {
            'BTC-USD': 'XXBTZUSD',
            'ETH-USD': 'XETHZUSD',
            'SOL-USD': 'SOLUSD',
            'AVAX-USD': 'AVAXUSD',
            'ADA-USD': 'ADAUSD',
        }

        print(f"✅ Kraken client initialized")

    def _normalize_pair(self, symbol: str) -> str:
        """Convert standard symbol to Kraken format"""
        return self.pair_map.get(symbol, symbol)

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def get_ticker(self, symbol: str) -> Ticker:
        """
        Get current ticker data

        Args:
            symbol: Trading pair (e.g., 'BTC-USD')
        """
        self._rate_limit()

        kraken_pair = self._normalize_pair(symbol)

        response = self.kraken.query_public('Ticker', {'pair': kraken_pair})

        if response.get('error'):
            raise Exception(f"Kraken ticker error: {response['error']}")

        data = response['result'][kraken_pair]

        return Ticker(
            symbol=symbol,
            last=float(data['c'][0]),  # Last trade price
            bid=float(data['b'][0]),   # Best bid
            ask=float(data['a'][0]),   # Best ask
            volume_24h=float(data['v'][1]),  # 24h volume
            timestamp=datetime.now().isoformat()
        )

    def get_order_book(self, symbol: str, limit: int = 10) -> OrderBook:
        """
        Get order book snapshot

        Args:
            symbol: Trading pair
            limit: Number of levels (max 500)
        """
        self._rate_limit()

        kraken_pair = self._normalize_pair(symbol)

        response = self.kraken.query_public('Depth', {
            'pair': kraken_pair,
            'count': limit
        })

        if response.get('error'):
            raise Exception(f"Kraken order book error: {response['error']}")

        data = response['result'][kraken_pair]

        # Convert to (price, size) tuples
        bids = [(float(bid[0]), float(bid[1])) for bid in data['bids']]
        asks = [(float(ask[0]), float(ask[1])) for ask in data['asks']]

        return OrderBook(
            symbol=symbol,
            bids=bids,
            asks=asks,
            timestamp=datetime.now().isoformat()
        )

    def get_balance(self, currency: Optional[str] = None) -> Dict[str, Balance]:
        """
        Get account balances

        Args:
            currency: Optional currency filter (e.g., 'USD', 'BTC')
        """
        self._rate_limit()

        response = self.kraken.query_private('Balance')

        if response.get('error'):
            raise Exception(f"Kraken balance error: {response['error']}")

        balances = {}

        for kraken_currency, amount in response['result'].items():
            # Normalize currency names (Kraken uses prefixes like 'ZUSD', 'XXBT')
            curr = kraken_currency.replace('Z', '').replace('X', '')

            if currency and curr != currency:
                continue

            amount_float = float(amount)

            balances[curr] = Balance(
                currency=curr,
                available=amount_float,  # Simplified (Kraken doesn't separate held)
                held=0.0,
                total=amount_float
            )

        return balances

    def get_candles(
        self,
        symbol: str,
        interval: int = 5  # Minutes: 1, 5, 15, 30, 60, 240, 1440
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV candles

        Args:
            symbol: Trading pair
            interval: Candle interval in minutes
        """
        self._rate_limit()

        kraken_pair = self._normalize_pair(symbol)

        response = self.kraken.query_public('OHLC', {
            'pair': kraken_pair,
            'interval': interval
        })

        if response.get('error'):
            raise Exception(f"Kraken OHLC error: {response['error']}")

        candles = []
        for candle in response['result'][kraken_pair]:
            candles.append({
                'timestamp': int(candle[0]),
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[6])
            })

        return candles

    def get_open_positions(self) -> List[Position]:
        """
        Get open margin positions

        Returns positions with P&L calculations
        """
        self._rate_limit()

        response = self.kraken.query_private('OpenPositions')

        if response.get('error'):
            raise Exception(f"Kraken positions error: {response['error']}")

        positions = []

        for position_id, pos_data in response.get('result', {}).items():
            # Calculate P&L
            entry_price = float(pos_data.get('cost', 0)) / float(pos_data.get('vol', 1))
            current_price = float(pos_data.get('value', 0)) / float(pos_data.get('vol', 1))
            pnl = float(pos_data.get('net', 0))
            pnl_pct = (pnl / float(pos_data.get('cost', 1))) * 100

            positions.append(Position(
                position_id=position_id,
                symbol=pos_data.get('pair', ''),
                side='long' if float(pos_data.get('vol', 0)) > 0 else 'short',
                size=abs(float(pos_data.get('vol', 0))),
                entry_price=entry_price,
                current_price=current_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                leverage=float(pos_data.get('leverage', 1)),
                timestamp=datetime.now().isoformat()
            ))

        return positions

    def place_market_order(
        self,
        symbol: str,
        side: str,  # 'buy' or 'sell'
        amount: float,
        leverage: int = 1
    ) -> Dict[str, Any]:
        """
        Place market order

        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Amount in base currency
            leverage: Leverage (1-10)
        """
        self._rate_limit()

        kraken_pair = self._normalize_pair(symbol)

        order_params = {
            'pair': kraken_pair,
            'type': side,
            'ordertype': 'market',
            'volume': str(amount)
        }

        if leverage > 1:
            order_params['leverage'] = str(leverage)

        print(f"🎯 Placing {side.upper()} market order: {amount} {symbol} (leverage: {leverage}x)")

        response = self.kraken.query_private('AddOrder', order_params)

        if response.get('error'):
            raise Exception(f"Kraken order error: {response['error']}")

        return {
            'order_id': response['result']['txid'][0] if 'txid' in response['result'] else None,
            'symbol': symbol,
            'side': side,
            'type': 'market',
            'amount': amount,
            'leverage': leverage,
            'status': 'placed',
            'timestamp': datetime.now().isoformat()
        }

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        leverage: int = 1
    ) -> Dict[str, Any]:
        """
        Place limit order

        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Amount in base currency
            price: Limit price
            leverage: Leverage (1-10)
        """
        self._rate_limit()

        kraken_pair = self._normalize_pair(symbol)

        order_params = {
            'pair': kraken_pair,
            'type': side,
            'ordertype': 'limit',
            'price': str(price),
            'volume': str(amount)
        }

        if leverage > 1:
            order_params['leverage'] = str(leverage)

        print(f"🎯 Placing {side.upper()} limit order: {amount} {symbol} @ ${price} (leverage: {leverage}x)")

        response = self.kraken.query_private('AddOrder', order_params)

        if response.get('error'):
            raise Exception(f"Kraken order error: {response['error']}")

        return {
            'order_id': response['result']['txid'][0] if 'txid' in response['result'] else None,
            'symbol': symbol,
            'side': side,
            'type': 'limit',
            'amount': amount,
            'price': price,
            'leverage': leverage,
            'status': 'placed',
            'timestamp': datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            'exchange': 'Kraken',
            'api_key': self.api_key[:8] + '...' if self.api_key else None,
            'rate_limit': f"{1/self.min_request_interval:.0f} req/sec",
            'supported_pairs': list(self.pair_map.keys()),
            'max_leverage': 10
        }


# Singleton instance
_client = None


def get_kraken_client() -> KrakenClient:
    """Get singleton Kraken client"""
    global _client
    if _client is None:
        _client = KrakenClient()
    return _client


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY KRAKEN CLIENT TEST")
    print("="*70)
    print()

    # Initialize client
    client = get_kraken_client()

    print("Status:")
    status = client.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n🧪 Testing ticker...")
    try:
        ticker = client.get_ticker('BTC-USD')
        print(f"  BTC-USD: ${ticker.last:,.2f}")
        print(f"  Bid: ${ticker.bid:,.2f}")
        print(f"  Ask: ${ticker.ask:,.2f}")
        print(f"  24h Volume: {ticker.volume_24h:,.2f}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n🧪 Testing order book...")
    try:
        book = client.get_order_book('BTC-USD', limit=5)
        print(f"  Top 5 bids:")
        for price, size in book.bids[:5]:
            print(f"    ${price:,.2f} x {size:.8f}")
        print(f"  Top 5 asks:")
        for price, size in book.asks[:5]:
            print(f"    ${price:,.2f} x {size:.8f}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n🧪 Testing balance...")
    try:
        balances = client.get_balance()
        for currency, balance in list(balances.items())[:5]:
            print(f"  {currency}: {balance.total:.8f}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n🧪 Testing candles...")
    try:
        candles = client.get_candles('BTC-USD', interval=5)
        print(f"  Fetched {len(candles)} 5-minute candles")
        if candles:
            latest = candles[-1]
            print(f"  Latest: O:{latest['open']:.2f} H:{latest['high']:.2f} L:{latest['low']:.2f} C:{latest['close']:.2f}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n✅ Kraken client test complete")
