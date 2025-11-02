#!/usr/bin/env python3
"""
Unity Coinbase API Client

Unified interface for Coinbase Advanced Trade API.
Ported from APEX trading system with Unity enhancements.

Wisdom: The exchange is not just an API—it is a gateway to markets.
Respect the rate limits. Respect the latency. Respect the capital.

Author: Dr. Claude Summers, Crypto Trading Architect
Date: October 16, 2025
"""

import os
import time
import hashlib
import hmac
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


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


class CoinbaseClient:
    """
    Coinbase Advanced Trade API Client

    Provides unified interface for:
    - Market data (ticker, order book, candles)
    - Account info (balances, positions)
    - Order management (market, limit orders)

    Supports both live and sandbox modes.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        sandbox: bool = False
    ):
        self.api_key = api_key or os.getenv('COINBASE_API_KEY')
        self.api_secret = api_secret or os.getenv('COINBASE_API_SECRET')

        if not self.api_key or not self.api_secret:
            raise ValueError("Coinbase API credentials required (env: COINBASE_API_KEY, COINBASE_API_SECRET)")

        self.sandbox = sandbox
        self.base_url = "https://api.coinbase.com/v2" if not sandbox else "https://api-public.sandbox.coinbase.com/v2"

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second max

        print(f"✅ Coinbase client initialized ({'SANDBOX' if sandbox else 'LIVE'})")

    def _generate_signature(self, timestamp: str, method: str, request_path: str, body: str = ''):
        """Generate CB-ACCESS-SIGN header"""
        message = timestamp + method + request_path + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

        timestamp = str(int(time.time()))
        request_path = f"/v2{endpoint}"

        # Build request
        url = f"{self.base_url}{endpoint}"
        headers = {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': self._generate_signature(timestamp, method, request_path, ''),
            'CB-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }

        # Execute request
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=json_data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            self.last_request_time = time.time()

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Coinbase API error: {e}")
            return {'error': str(e)}

    def get_ticker(self, symbol: str) -> Ticker:
        """
        Get current ticker data

        Args:
            symbol: Trading pair (e.g., 'BTC-USD')
        """
        response = self._request('GET', f'/prices/{symbol}/spot')

        if 'error' in response:
            raise Exception(f"Failed to get ticker: {response['error']}")

        # Coinbase v2 API returns simplified data
        price = float(response.get('data', {}).get('amount', 0))

        return Ticker(
            symbol=symbol,
            last=price,
            bid=price * 0.999,  # Approximate bid
            ask=price * 1.001,  # Approximate ask
            volume_24h=0.0,  # Not available in v2
            timestamp=datetime.now().isoformat()
        )

    def get_order_book(self, symbol: str, limit: int = 10) -> OrderBook:
        """
        Get order book snapshot

        Note: Coinbase v2 doesn't provide order book data.
        This is a placeholder for Advanced Trade API migration.
        """
        # For now, return empty order book
        # In production, would use Advanced Trade API
        return OrderBook(
            symbol=symbol,
            bids=[],
            asks=[],
            timestamp=datetime.now().isoformat()
        )

    def get_balance(self, currency: Optional[str] = None) -> Dict[str, Balance]:
        """
        Get account balances

        Args:
            currency: Optional currency filter (e.g., 'USD', 'BTC')
        """
        response = self._request('GET', '/accounts')

        if 'error' in response:
            raise Exception(f"Failed to get balance: {response['error']}")

        balances = {}
        for account in response.get('data', []):
            curr = account.get('currency', {}).get('code', '')
            if currency and curr != currency:
                continue

            balance_amount = float(account.get('balance', {}).get('amount', 0))

            balances[curr] = Balance(
                currency=curr,
                available=balance_amount,
                held=0.0,
                total=balance_amount
            )

        return balances

    def place_market_order(
        self,
        symbol: str,
        side: str,  # 'buy' or 'sell'
        amount: float
    ) -> Dict[str, Any]:
        """
        Place market order

        Args:
            symbol: Trading pair (e.g., 'BTC-USD')
            side: 'buy' or 'sell'
            amount: Amount in base currency
        """
        print(f"🎯 Placing {side.upper()} market order: {amount} {symbol}")

        # Note: Actual order placement requires Advanced Trade API
        # This is placeholder logic
        return {
            'order_id': f"simulated_{int(time.time())}",
            'symbol': symbol,
            'side': side,
            'type': 'market',
            'amount': amount,
            'status': 'simulated',
            'timestamp': datetime.now().isoformat()
        }

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float
    ) -> Dict[str, Any]:
        """
        Place limit order

        Args:
            symbol: Trading pair (e.g., 'BTC-USD')
            side: 'buy' or 'sell'
            amount: Amount in base currency
            price: Limit price
        """
        print(f"🎯 Placing {side.upper()} limit order: {amount} {symbol} @ ${price}")

        # Note: Actual order placement requires Advanced Trade API
        return {
            'order_id': f"simulated_{int(time.time())}",
            'symbol': symbol,
            'side': side,
            'type': 'limit',
            'amount': amount,
            'price': price,
            'status': 'simulated',
            'timestamp': datetime.now().isoformat()
        }

    def get_candles(
        self,
        symbol: str,
        granularity: int = 300  # 5 minutes
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV candles

        Args:
            symbol: Trading pair
            granularity: Candle size in seconds (60, 300, 900, 3600, 21600, 86400)
        """
        # Coinbase v2 doesn't provide candles
        # Placeholder for Advanced Trade API
        return []

    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            'exchange': 'Coinbase',
            'mode': 'sandbox' if self.sandbox else 'live',
            'api_key': self.api_key[:8] + '...' if self.api_key else None,
            'base_url': self.base_url,
            'rate_limit': f"{1/self.min_request_interval:.0f} req/sec"
        }


# Singleton instance
_client = None


def get_coinbase_client(sandbox: bool = False) -> CoinbaseClient:
    """Get singleton Coinbase client"""
    global _client
    if _client is None or _client.sandbox != sandbox:
        _client = CoinbaseClient(sandbox=sandbox)
    return _client


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY COINBASE CLIENT TEST")
    print("="*70)
    print()

    # Initialize client
    client = get_coinbase_client(sandbox=True)

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
    except Exception as e:
        print(f"  Error: {e}")

    print("\n🧪 Testing balance...")
    try:
        balances = client.get_balance()
        for currency, balance in list(balances.items())[:5]:
            print(f"  {currency}: {balance.total:.8f}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n✅ Coinbase client test complete")
