#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Client for XRP Trading Bot v3.0
Provides a unified interface for interacting with the Kraken API with enhanced error handling,
rate limiting, and caching capabilities.
"""

import os
import json
import time
import logging
import hashlib
import hmac
import base64
import urllib.parse
import requests
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from functools import wraps

class APIRateLimiter:
    """
    Rate limiter for API requests to prevent hitting rate limits.
    """
    
    def __init__(self, max_requests_per_second: float = 1.0, max_requests_per_minute: int = 15):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests_per_second: Maximum requests per second
            max_requests_per_minute: Maximum requests per minute
        """
        self.max_requests_per_second = max_requests_per_second
        self.max_requests_per_minute = max_requests_per_minute
        self.request_timestamps = []
        self.last_request_time = 0
        self.logger = logging.getLogger('api_rate_limiter')
    
    def wait_if_needed(self):
        """
        Wait if necessary to comply with rate limits.
        """
        current_time = time.time()
        
        # Check requests per second limit
        time_since_last_request = current_time - self.last_request_time
        min_interval = 1.0 / self.max_requests_per_second
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f} seconds")
            time.sleep(sleep_time)
        
        # Check requests per minute limit
        self.request_timestamps = [ts for ts in self.request_timestamps 
                                 if ts > current_time - 60]
        
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            oldest_timestamp = self.request_timestamps[0]
            sleep_time = 60 - (current_time - oldest_timestamp)
            if sleep_time > 0:
                self.logger.warning(f"Minute rate limit reached: sleeping for {sleep_time:.3f} seconds")
                time.sleep(sleep_time)
        
        # Update state
        self.last_request_time = time.time()
        self.request_timestamps.append(self.last_request_time)


class APICache:
    """
    Cache for API responses to reduce the number of requests.
    """
    
    def __init__(self, max_cache_size: int = 100, default_ttl_seconds: int = 60):
        """
        Initialize the API cache.
        
        Args:
            max_cache_size: Maximum number of responses to cache
            default_ttl_seconds: Default time-to-live for cached responses in seconds
        """
        self.cache = {}
        self.max_cache_size = max_cache_size
        self.default_ttl_seconds = default_ttl_seconds
        self.logger = logging.getLogger('api_cache')
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a response from the cache if it exists and is not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None if not found or expired
        """
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if entry['expires_at'] > time.time():
                self.logger.debug(f"Cache hit for {cache_key}")
                return entry['data']
            else:
                self.logger.debug(f"Cache expired for {cache_key}")
                del self.cache[cache_key]
        
        self.logger.debug(f"Cache miss for {cache_key}")
        return None
    
    def set(self, cache_key: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None):
        """
        Store a response in the cache.
        
        Args:
            cache_key: Cache key
            data: Response data to cache
            ttl_seconds: Time-to-live in seconds (uses default if None)
        """
        # Use default TTL if not specified
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl_seconds
        
        # Evict oldest entry if cache is full
        if len(self.cache) >= self.max_cache_size and cache_key not in self.cache:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['expires_at'])
            del self.cache[oldest_key]
            self.logger.debug(f"Cache full, evicted {oldest_key}")
        
        # Store in cache
        self.cache[cache_key] = {
            'data': data,
            'expires_at': time.time() + ttl_seconds,
            'created_at': time.time()
        }
        self.logger.debug(f"Cached response for {cache_key} (TTL: {ttl_seconds}s)")
    
    def invalidate(self, cache_key: str):
        """
        Invalidate a cached response.
        
        Args:
            cache_key: Cache key to invalidate
        """
        if cache_key in self.cache:
            del self.cache[cache_key]
            self.logger.debug(f"Invalidated cache for {cache_key}")
    
    def clear(self):
        """Clear the entire cache."""
        self.cache = {}
        self.logger.debug("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        current_time = time.time()
        active_entries = sum(1 for entry in self.cache.values() if entry['expires_at'] > current_time)
        
        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "expired_entries": len(self.cache) - active_entries,
            "max_size": self.max_cache_size,
            "utilization_percent": (len(self.cache) / self.max_cache_size) * 100 if self.max_cache_size > 0 else 0
        }


class KrakenClient:
    """
    Enhanced Kraken API client with error handling, rate limiting, and caching.
    """
    
    def __init__(self, api_key: str = "", api_secret: str = "", 
                config_path: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None,
                error_handler=None):
        """
        Initialize the Kraken API client.
        
        Args:
            api_key: Kraken API key
            api_secret: Kraken API secret
            config_path: Path to configuration file
            config: Configuration dictionary (overrides config_path if provided)
            error_handler: ErrorHandler instance for handling API errors
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.config = {}
        self.error_handler = error_handler
        self.logger = logging.getLogger('kraken_client')
        
        # API endpoints
        self.api_url = "https://api.kraken.com"
        self.api_version = "0"
        
        # Load configuration
        if config:
            self.config = config
        elif config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load API client config from {config_path}: {e}")
                self.config = {}
        
        # Initialize rate limiter
        rate_limit_config = self.config.get('rate_limits', {})
        self.rate_limiter = APIRateLimiter(
            max_requests_per_second=rate_limit_config.get('max_requests_per_second', 1.0),
            max_requests_per_minute=rate_limit_config.get('max_requests_per_minute', 15)
        )
        
        # Initialize cache
        cache_config = self.config.get('cache', {})
        self.cache = APICache(
            max_cache_size=cache_config.get('max_size', 100),
            default_ttl_seconds=cache_config.get('default_ttl_seconds', 60)
        )
        
        # Set default request timeout
        self.timeout = self.config.get('timeout_seconds', 30)
        
        # Track API call statistics
        self.api_calls = {
            'total': 0,
            'public': 0,
            'private': 0,
            'success': 0,
            'error': 0,
            'cached': 0
        }
        self.api_call_times = []
    
    def _get_nonce(self) -> str:
        """
        Generate a nonce for API requests.
        
        Returns:
            Nonce string
        """
        return str(int(time.time() * 1000))
    
    def _get_kraken_signature(self, urlpath: str, data: Dict[str, str], nonce: str) -> str:
        """
        Generate a signature for private API requests.
        
        Args:
            urlpath: API URL path
            data: Request data
            nonce: Request nonce
            
        Returns:
            Request signature
        """
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        signature = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())
        
        return sigdigest.decode()
    
    def _generate_cache_key(self, method: str, params: Dict[str, Any]) -> str:
        """
        Generate a cache key for an API request.
        
        Args:
            method: API method
            params: Request parameters
            
        Returns:
            Cache key string
        """
        # Sort params to ensure consistent keys
        sorted_params = json.dumps(params, sort_keys=True)
        return f"{method}:{sorted_params}"
    
    def _should_cache(self, method: str) -> bool:
        """
        Determine if a method's responses should be cached.
        
        Args:
            method: API method
            
        Returns:
            True if method should be cached, False otherwise
        """
        # Only cache public API methods that don't modify state
        cacheable_methods = [
            'Time', 'Assets', 'AssetPairs', 'Ticker', 'Depth', 'Trades', 'Spread', 'OHLC'
        ]
        
        return method in cacheable_methods
    
    def _get_cache_ttl(self, method: str) -> int:
        """
        Get the cache TTL for a method.
        
        Args:
            method: API method
            
        Returns:
            Cache TTL in seconds
        """
        # Different methods have different appropriate cache times
        ttl_map = {
            'Time': 60,
            'Assets': 3600,  # Assets rarely change
            'AssetPairs': 3600,  # Pairs rarely change
            'Ticker': 15,  # Ticker data changes frequently
            'Depth': 5,  # Order book changes very frequently
            'Trades': 30,
            'Spread': 5,
            'OHLC': 60
        }
        
        return ttl_map.get(method, self.cache.default_ttl_seconds)
    
    def _handle_api_error(self, method: str, params: Dict[str, Any], 
                         error_message: str, exception: Optional[Exception] = None) -> Dict[str, Any]:
        """
        Handle an API error using the error handler if available.
        
        Args:
            method: API method
            params: Request parameters
            error_message: Error message
            exception: Exception if available
            
        Returns:
            Error handling result
        """
        if self.error_handler:
            # Create safe params copy without API credentials
            safe_params = params.copy()
            if 'nonce' in safe_params:
                del safe_params['nonce']
            
            context = {
                "method": method,
                "params": safe_params
            }
            
            return self.error_handler.handle_error(
                error_type="kraken_api_error",
                error_message=error_message,
                exception=exception,
                severity="high",
                category="api",
                context=context,
                notify=True
            )
        else:
            self.logger.error(f"API error in {method}: {error_message}")
            if exception:
                self.logger.error(f"Exception: {exception}")
            return {"handled": False}
    
    def _update_api_stats(self, method: str, is_public: bool, 
                         success: bool, cached: bool, response_time: float):
        """
        Update API call statistics.
        
        Args:
            method: API method
            is_public: Whether it was a public API call
            success: Whether the call was successful
            cached: Whether the response was from cache
            response_time: Response time in seconds
        """
        self.api_calls['total'] += 1
        
        if is_public:
            self.api_calls['public'] += 1
        else:
            self.api_calls['private'] += 1
            
        if success:
            self.api_calls['success'] += 1
        else:
            self.api_calls['error'] += 1
            
        if cached:
            self.api_calls['cached'] += 1
            
        self.api_call_times.append(response_time)
        
        # Keep only the last 100 response times
        if len(self.api_call_times) > 100:
            self.api_call_times = self.api_call_times[-100:]
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get API call statistics.
        
        Returns:
            Dictionary with API call statistics
        """
        avg_response_time = sum(self.api_call_times) / len(self.api_call_times) if self.api_call_times else 0
        
        return {
            "calls": self.api_calls,
            "avg_response_time": avg_response_time,
            "cache_stats": self.cache.get_stats()
        }
    
    def query_public(self, method: str, params: Optional[Dict[str, Any]] = None, 
                   use_cache: bool = True) -> Dict[str, Any]:
        """
        Query public API endpoint.
        
        Args:
            method: API method
            params: Request parameters
            use_cache: Whether to use cache
            
        Returns:
            API response
        """
        if params is None:
            params = {}
            
        # Check cache if enabled
        if use_cache and self._should_cache(method):
            cache_key = self._generate_cache_key(method, params)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                self._update_api_stats(method, True, True, True, 0)
                return cached_response
        
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Build request
        url = f"{self.api_url}/{self.api_version}/public/{method}"
        
        # Track timing
        start_time = time.time()
        success = False
        cached = False
        
        try:
            response = requests.post(url, data=params, timeout=self.timeout)
            response_data = response.json()
            
            # Check for API errors
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self._handle_api_error(method, params, error_msg)
                success = False
            elif response_data.get('error'):
                error_msg = f"API error: {response_data['error']}"
                self._handle_api_error(method, params, error_msg)
                success = False
            else:
                success = True
                
                # Cache successful response if appropriate
                if use_cache and self._should_cache(method):
                    ttl = self._get_cache_ttl(method)
                    cache_key = self._generate_cache_key(method, params)
                    self.cache.set(cache_key, response_data, ttl)
            
            response_time = time.time() - start_time
            self._update_api_stats(method, True, success, cached, response_time)
            
            return response_data
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_api_stats(method, True, False, False, response_time)
            
            error_msg = f"Exception in public API call to {method}: {str(e)}"
            self._handle_api_error(method, params, error_msg, e)
            
            return {"error": [str(e)], "result": {}}
    
    def query_private(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query private API endpoint.
        
        Args:
            method: API method
            params: Request parameters
            
        Returns:
            API response
        """
        if not self.api_key or not self.api_secret:
            error_msg = "API key and secret required for private API calls"
            self._handle_api_error(method, params or {}, error_msg)
            return {"error": [error_msg], "result": {}}
            
        if params is None:
            params = {}
            
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Add nonce to parameters
        params['nonce'] = self._get_nonce()
        
        # Build request
        url = f"{self.api_url}/{self.api_version}/private/{method}"
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._get_kraken_signature(f"/{self.api_version}/private/{method}", params, params['nonce'])
        }
        
        # Track timing
        start_time = time.time()
        success = False
        
        try:
            response = requests.post(url, headers=headers, data=params, timeout=self.timeout)
            response_data = response.json()
            
            # Check for API errors
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self._handle_api_error(method, params, error_msg)
                success = False
            elif response_data.get('error'):
                error_msg = f"API error: {response_data['error']}"
                self._handle_api_error(method, params, error_msg)
                success = False
            else:
                success = True
            
            response_time = time.time() - start_time
            self._update_api_stats(method, False, success, False, response_time)
            
            return response_data
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_api_stats(method, False, False, False, response_time)
            
            error_msg = f"Exception in private API call to {method}: {str(e)}"
            self._handle_api_error(method, params, error_msg, e)
            
            return {"error": [str(e)], "result": {}}
    
    # Convenience methods for common API calls
    
    def get_server_time(self) -> Dict[str, Any]:
        """
        Get Kraken server time.
        
        Returns:
            Server time information
        """
        return self.query_public('Time')
    
    def get_asset_pairs(self, pair: Optional[str] = None) -> Dict[str, Any]:
        """
        Get asset pair information.
        
        Args:
            pair: Specific pair to get info for (optional)
            
        Returns:
            Asset pair information
        """
        params = {}
        if pair:
            params['pair'] = pair
        return self.query_public('AssetPairs', params)
    
    def get_ticker(self, pair: str) -> Dict[str, Any]:
        """
        Get ticker information.
        
        Args:
            pair: Asset pair
            
        Returns:
            Ticker information
        """
        return self.query_public('Ticker', {'pair': pair})
    
    def get_ohlc_data(self, pair: str, interval: int = 1, since: Optional[int] = None) -> Dict[str, Any]:
        """
        Get OHLC data.
        
        Args:
            pair: Asset pair
            interval: Time frame interval in minutes (1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
            since: Return committed OHLC data since given ID
            
        Returns:
            OHLC data
        """
        params = {'pair': pair, 'interval': interval}
        if since:
            params['since'] = since
        return self.query_public('OHLC', params)
    
    def get_order_book(self, pair: str, count: int = 100) -> Dict[str, Any]:
        """
        Get order book.
        
        Args:
            pair: Asset pair
            count: Maximum number of asks/bids
            
        Returns:
            Order book
        """
        return self.query_public('Depth', {'pair': pair, 'count': count})
    
    def get_recent_trades(self, pair: str, since: Optional[int] = None) -> Dict[str, Any]:
        """
        Get recent trades.
        
        Args:
            pair: Asset pair
            since: Return trade data since given ID
            
        Returns:
            Recent trades
        """
        params = {'pair': pair}
        if since:
            params['since'] = since
        return self.query_public('Trades', params)
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance.
        
        Returns:
            Account balance
        """
        return self.query_private('Balance')
    
    def get_trade_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """
        Get trade balance.
        
        Args:
            asset: Base asset to determine balance
            
        Returns:
            Trade balance
        """
        params = {}
        if asset:
            params['asset'] = asset
        return self.query_private('TradeBalance', params)
    
    def get_open_orders(self, trades: bool = False, userref: Optional[int] = None) -> Dict[str, Any]:
        """
        Get open orders.
        
        Args:
            trades: Whether to include trades
            userref: Restrict results to given user reference ID
            
        Returns:
            Open orders
        """
        params = {'trades': trades}
        if userref:
            params['userref'] = userref
        return self.query_private('OpenOrders', params)
    
    def get_closed_orders(self, trades: bool = False, userref: Optional[int] = None,
                        start: Optional[int] = None, end: Optional[int] = None,
                        ofs: Optional[int] = None, closetime: str = 'both') -> Dict[str, Any]:
        """
        Get closed orders.
        
        Args:
            trades: Whether to include trades
            userref: Restrict results to given user reference ID
            start: Starting unix timestamp or order tx ID
            end: Ending unix timestamp or order tx ID
            ofs: Result offset for pagination
            closetime: Which time to use (open, close, both)
            
        Returns:
            Closed orders
        """
        params = {'trades': trades, 'closetime': closetime}
        if userref:
            params['userref'] = userref
        if start:
            params['start'] = start
        if end:
            params['end'] = end
        if ofs:
            params['ofs'] = ofs
        return self.query_private('ClosedOrders', params)
    
    def query_orders_info(self, txid: Union[str, List[str]], trades: bool = False, 
                        userref: Optional[int] = None) -> Dict[str, Any]:
        """
        Query orders info.
        
        Args:
            txid: Transaction ID or list of transaction IDs
            trades: Whether to include trades
            userref: Restrict results to given user reference ID
            
        Returns:
            Orders information
        """
        if isinstance(txid, list):
            txid = ','.join(txid)
        
        params = {'txid': txid, 'trades': trades}
        if userref:
            params['userref'] = userref
        return self.query_private('QueryOrders', params)
    
    def get_trades_history(self, type: str = 'all', trades: bool = False,
                         start: Optional[int] = None, end: Optional[int] = None,
                         ofs: Optional[int] = None) -> Dict[str, Any]:
        """
        Get trades history.
        
        Args:
            type: Type of trade (all, any position, closed position, closing position, no position)
            trades: Whether to include trades
            start: Starting unix timestamp or trade tx ID
            end: Ending unix timestamp or trade tx ID
            ofs: Result offset for pagination
            
        Returns:
            Trades history
        """
        params = {'type': type, 'trades': trades}
        if start:
            params['start'] = start
        if end:
            params['end'] = end
        if ofs:
            params['ofs'] = ofs
        return self.query_private('TradesHistory', params)
    
    def query_trades_info(self, txid: Union[str, List[str]], trades: bool = False) -> Dict[str, Any]:
        """
        Query trades info.
        
        Args:
            txid: Transaction ID or list of transaction IDs
            trades: Whether to include trades
            
        Returns:
            Trades information
        """
        if isinstance(txid, list):
            txid = ','.join(txid)
        
        params = {'txid': txid, 'trades': trades}
        return self.query_private('QueryTrades', params)
    
    def place_order(self, pair: str, type: str, ordertype: str, volume: float,
                  price: Optional[float] = None, price2: Optional[float] = None,
                  leverage: Optional[float] = None, oflags: Optional[str] = None,
                  starttm: Optional[int] = None, expiretm: Optional[int] = None,
                  userref: Optional[int] = None, validate: bool = False) -> Dict[str, Any]:
        """
        Place a new order.
        
        Args:
            pair: Asset pair
            type: Type of order (buy/sell)
            ordertype: Order type (market/limit/stop-loss/take-profit/etc.)
            volume: Order volume in lots
            price: Price (optional depending on ordertype)
            price2: Secondary price (optional depending on ordertype)
            leverage: Amount of leverage desired (optional)
            oflags: Comma-delimited list of order flags (optional)
            starttm: Scheduled start time (optional)
            expiretm: Expiration time (optional)
            userref: User reference ID (optional)
            validate: Validate inputs only, don't place order
            
        Returns:
            Order placement result
        """
        params = {
            'pair': pair,
            'type': type,
            'ordertype': ordertype,
            'volume': str(volume),
            'validate': validate
        }
        
        if price:
            params['price'] = str(price)
        if price2:
            params['price2'] = str(price2)
        if leverage:
            params['leverage'] = str(leverage)
        if oflags:
            params['oflags'] = oflags
        if starttm:
            params['starttm'] = str(starttm)
        if expiretm:
            params['expiretm'] = str(expiretm)
        if userref:
            params['userref'] = str(userref)
        
        return self.query_private('AddOrder', params)
    
    def cancel_order(self, txid: str) -> Dict[str, Any]:
        """
        Cancel an open order.
        
        Args:
            txid: Transaction ID
            
        Returns:
            Cancellation result
        """
        return self.query_private('CancelOrder', {'txid': txid})
    
    def cancel_all_orders(self) -> Dict[str, Any]:
        """
        Cancel all open orders.
        
        Returns:
            Cancellation result
        """
        return self.query_private('CancelAll')


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example configuration
    config = {
        "rate_limits": {
            "max_requests_per_second": 1.0,
            "max_requests_per_minute": 15
        },
        "cache": {
            "max_size": 100,
            "default_ttl_seconds": 60
        },
        "timeout_seconds": 30
    }
    
    # Create API client
    client = KrakenClient(config=config)
    
    # Example public API call
    server_time = client.get_server_time()
    print(f"Server time: {json.dumps(server_time, indent=2)}")
    
    # Example asset pairs query
    pairs = client.get_asset_pairs("XRPGBP")
    print(f"XRPGBP pair info: {json.dumps(pairs, indent=2)}")
    
    # Example ticker query
    ticker = client.get_ticker("XRPGBP")
    print(f"XRPGBP ticker: {json.dumps(ticker, indent=2)}")
    
    # Get API stats
    stats = client.get_api_stats()
    print(f"API stats: {json.dumps(stats, indent=2)}")
