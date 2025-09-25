"""
TradingView data source implementation
"""
import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.crypto_data import PriceData, MarketData, TechnicalIndicator, DataSource
from .base import BaseDataSource
from loguru import logger


class TradingViewDataSource(BaseDataSource):
    """TradingView data source implementation"""
    
    def __init__(self, username: str = None, password: str = None, base_url: str = "https://scanner.tradingview.com"):
        super().__init__(None, base_url)
        self.username = username
        self.password = password
        self.session_token = None
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def _authenticate(self) -> bool:
        """Authenticate with TradingView"""
        if not self.username or not self.password:
            logger.warning("TradingView credentials not provided, using public endpoints")
            return True
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        auth_data = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json=auth_data,
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.session_token = data.get("token")
                    if self.session_token:
                        self.headers["Authorization"] = f"Bearer {self.session_token}"
                    return True
                else:
                    logger.error(f"TradingView authentication failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error authenticating with TradingView: {e}")
            return False
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make request to TradingView API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if data:
                async with self.session.post(url, json=data, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"TradingView API error: {response.status}")
                        return {}
            else:
                async with self.session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"TradingView API error: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error making TradingView request: {e}")
            return {}
    
    async def get_crypto_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for a cryptocurrency from TradingView"""
        symbol = self._validate_symbol(symbol)
        
        # TradingView uses different symbol format
        tv_symbol = f"BINANCE:{symbol}USDT"
        
        endpoint = "/crypto/scan"
        data = {
            "filter": [
                {"left": "name", "operation": "match", "right": symbol}
            ],
            "options": {
                "lang": "en"
            },
            "symbols": {
                "query": {"types": []},
                "tickers": [tv_symbol]
            },
            "columns": ["name", "close", "volume", "market_cap_basic"],
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
            "range": [0, 1]
        }
        
        response_data = await self._make_request(endpoint, data)
        
        if not response_data or "data" not in response_data or not response_data["data"]:
            logger.warning(f"No price data found for {symbol} from TradingView")
            return None
        
        crypto_data = response_data["data"][0]
        
        return PriceData(
            symbol=symbol,
            price=float(crypto_data.get("close", 0)),
            volume=float(crypto_data.get("volume", 0)),
            market_cap=float(crypto_data.get("market_cap_basic", 0)) if crypto_data.get("market_cap_basic") else None,
            timestamp=self._get_timestamp(),
            source=DataSource.TRADINGVIEW
        )
    
    async def get_historical_prices(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PriceData]:
        """Get historical price data from TradingView"""
        symbol = self._validate_symbol(symbol)
        tv_symbol = f"BINANCE:{symbol}USDT"
        
        # Calculate days difference
        days = (end_date - start_date).days
        
        endpoint = "/crypto/history"
        data = {
            "symbol": tv_symbol,
            "resolution": "1D",
            "from": int(start_date.timestamp()),
            "to": int(end_date.timestamp())
        }
        
        response_data = await self._make_request(endpoint, data)
        
        if not response_data or "c" not in response_data:
            logger.warning(f"No historical data found for {symbol} from TradingView")
            return []
        
        prices = []
        closes = response_data.get("c", [])
        volumes = response_data.get("v", [])
        timestamps = response_data.get("t", [])
        
        for i, (close, volume, timestamp) in enumerate(zip(closes, volumes, timestamps)):
            prices.append(PriceData(
                symbol=symbol,
                price=float(close),
                volume=float(volume),
                market_cap=None,
                timestamp=datetime.fromtimestamp(timestamp),
                source=DataSource.TRADINGVIEW
            ))
        
        return prices
    
    async def get_technical_indicators(
        self, 
        symbol: str, 
        indicators: List[str]
    ) -> List[TechnicalIndicator]:
        """Get technical indicators from TradingView"""
        symbol = self._validate_symbol(symbol)
        tv_symbol = f"BINANCE:{symbol}USDT"
        
        # Map common indicators to TradingView format
        indicator_mapping = {
            "RSI": "RSI",
            "MACD": "MACD",
            "SMA_20": "SMA",
            "SMA_50": "SMA",
            "BB_upper": "BB.upper",
            "BB_lower": "BB.lower"
        }
        
        endpoint = "/crypto/indicators"
        data = {
            "symbol": tv_symbol,
            "indicators": [indicator_mapping.get(ind, ind) for ind in indicators]
        }
        
        response_data = await self._make_request(endpoint, data)
        
        if not response_data or "indicators" not in response_data:
            logger.warning(f"No technical indicators found for {symbol} from TradingView")
            return []
        
        technical_indicators = []
        for indicator_name, indicator_data in response_data["indicators"].items():
            if indicator_data and "value" in indicator_data:
                signal = self._determine_signal(indicator_name, indicator_data["value"])
                
                technical_indicators.append(TechnicalIndicator(
                    name=indicator_name,
                    value=float(indicator_data["value"]),
                    signal=signal,
                    timestamp=self._get_timestamp(),
                    source=DataSource.TRADINGVIEW
                ))
        
        return technical_indicators
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get comprehensive market data from TradingView"""
        symbol = self._validate_symbol(symbol)
        
        # Get price data
        price_data = await self.get_crypto_price(symbol)
        if not price_data:
            return None
        
        # Get technical indicators
        indicators = ["RSI", "MACD", "SMA_20", "SMA_50", "BB_upper", "BB_lower"]
        technical_indicators = await self.get_technical_indicators(symbol, indicators)
        
        # Get market sentiment from TradingView
        sentiment_endpoint = "/crypto/sentiment"
        sentiment_data = await self._make_request(sentiment_endpoint, {"symbol": f"BINANCE:{symbol}USDT"})
        market_sentiment = sentiment_data.get("sentiment") if sentiment_data else None
        
        return MarketData(
            symbol=symbol,
            price_data=price_data,
            technical_indicators=technical_indicators,
            market_sentiment=market_sentiment,
            volatility=sentiment_data.get("volatility") if sentiment_data else None,
            timestamp=self._get_timestamp(),
            source=DataSource.TRADINGVIEW
        )
    
    async def search_crypto(self, query: str) -> List[Dict[str, Any]]:
        """Search for cryptocurrencies on TradingView"""
        endpoint = "/crypto/search"
        data = {"query": query}
        
        response_data = await self._make_request(endpoint, data)
        
        if not response_data or "results" not in response_data:
            logger.warning(f"No search results found for '{query}' on TradingView")
            return []
        
        return response_data["results"]
    
    def get_source_name(self) -> DataSource:
        """Get the data source name"""
        return DataSource.TRADINGVIEW
    
    def _determine_signal(self, indicator_name: str, value: float) -> str:
        """Determine signal based on indicator value"""
        signal_rules = {
            "RSI": lambda v: "bearish" if v > 70 else "bullish" if v < 30 else "neutral",
            "MACD": lambda v: "bullish" if v > 0 else "bearish",
            "SMA": lambda v: "bullish" if v > 0 else "bearish",  # Simplified
            "BB.upper": lambda v: "bearish",
            "BB.lower": lambda v: "bullish",
        }
        
        rule = signal_rules.get(indicator_name)
        if rule:
            return rule(value)
        return "neutral"
