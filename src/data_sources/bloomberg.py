"""
Bloomberg data source implementation
"""
import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.crypto_data import PriceData, MarketData, TechnicalIndicator, DataSource
from .base import BaseDataSource
from loguru import logger


class BloombergDataSource(BaseDataSource):
    """Bloomberg API data source"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.bloomberg.com"):
        super().__init__(api_key, base_url)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to Bloomberg API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Bloomberg API error: {response.status} - {await response.text()}")
                    return {}
        except Exception as e:
            logger.error(f"Error making Bloomberg request: {e}")
            return {}
    
    async def get_crypto_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for a cryptocurrency from Bloomberg"""
        symbol = self._validate_symbol(symbol)
        
        # Bloomberg API endpoint for crypto prices
        endpoint = f"/v1/marketdata/crypto/{symbol}/price"
        
        data = await self._make_request(endpoint)
        
        if not data or "price" not in data:
            logger.warning(f"No price data found for {symbol} from Bloomberg")
            return None
        
        return PriceData(
            symbol=symbol,
            price=float(data["price"]),
            volume=float(data.get("volume", 0)),
            market_cap=float(data.get("market_cap", 0)) if data.get("market_cap") else None,
            timestamp=self._get_timestamp(),
            source=DataSource.BLOOMBERG
        )
    
    async def get_historical_prices(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PriceData]:
        """Get historical price data from Bloomberg"""
        symbol = self._validate_symbol(symbol)
        
        endpoint = f"/v1/marketdata/crypto/{symbol}/historical"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "interval": "1d"
        }
        
        data = await self._make_request(endpoint, params)
        
        if not data or "prices" not in data:
            logger.warning(f"No historical data found for {symbol} from Bloomberg")
            return []
        
        prices = []
        for price_data in data["prices"]:
            prices.append(PriceData(
                symbol=symbol,
                price=float(price_data["price"]),
                volume=float(price_data.get("volume", 0)),
                market_cap=float(price_data.get("market_cap", 0)) if price_data.get("market_cap") else None,
                timestamp=datetime.fromisoformat(price_data["timestamp"]),
                source=DataSource.BLOOMBERG
            ))
        
        return prices
    
    async def get_technical_indicators(
        self, 
        symbol: str, 
        indicators: List[str]
    ) -> List[TechnicalIndicator]:
        """Get technical indicators from Bloomberg"""
        symbol = self._validate_symbol(symbol)
        
        endpoint = f"/v1/marketdata/crypto/{symbol}/technical"
        params = {"indicators": ",".join(indicators)}
        
        data = await self._make_request(endpoint, params)
        
        if not data or "indicators" not in data:
            logger.warning(f"No technical indicators found for {symbol} from Bloomberg")
            return []
        
        technical_indicators = []
        for indicator_data in data["indicators"]:
            # Determine signal based on indicator value
            signal = self._determine_signal(indicator_data["name"], indicator_data["value"])
            
            technical_indicators.append(TechnicalIndicator(
                name=indicator_data["name"],
                value=float(indicator_data["value"]),
                signal=signal,
                timestamp=self._get_timestamp(),
                source=DataSource.BLOOMBERG
            ))
        
        return technical_indicators
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get comprehensive market data from Bloomberg"""
        symbol = self._validate_symbol(symbol)
        
        # Get price data
        price_data = await self.get_crypto_price(symbol)
        if not price_data:
            return None
        
        # Get technical indicators
        indicators = ["RSI", "MACD", "SMA_20", "SMA_50", "BB_upper", "BB_lower"]
        technical_indicators = await self.get_technical_indicators(symbol, indicators)
        
        # Get market sentiment (if available)
        sentiment_endpoint = f"/v1/marketdata/crypto/{symbol}/sentiment"
        sentiment_data = await self._make_request(sentiment_endpoint)
        market_sentiment = sentiment_data.get("sentiment") if sentiment_data else None
        
        return MarketData(
            symbol=symbol,
            price_data=price_data,
            technical_indicators=technical_indicators,
            market_sentiment=market_sentiment,
            volatility=sentiment_data.get("volatility") if sentiment_data else None,
            timestamp=self._get_timestamp(),
            source=DataSource.BLOOMBERG
        )
    
    async def search_crypto(self, query: str) -> List[Dict[str, Any]]:
        """Search for cryptocurrencies on Bloomberg"""
        endpoint = "/v1/marketdata/crypto/search"
        params = {"query": query}
        
        data = await self._make_request(endpoint, params)
        
        if not data or "results" not in data:
            logger.warning(f"No search results found for '{query}' on Bloomberg")
            return []
        
        return data["results"]
    
    def get_source_name(self) -> DataSource:
        """Get the data source name"""
        return DataSource.BLOOMBERG
    
    def _determine_signal(self, indicator_name: str, value: float) -> str:
        """Determine signal based on indicator value"""
        signal_rules = {
            "RSI": lambda v: "bearish" if v > 70 else "bullish" if v < 30 else "neutral",
            "MACD": lambda v: "bullish" if v > 0 else "bearish",
            "SMA_20": lambda v: "bullish" if v > 0 else "bearish",  # Simplified
            "SMA_50": lambda v: "bullish" if v > 0 else "bearish",  # Simplified
        }
        
        rule = signal_rules.get(indicator_name)
        if rule:
            return rule(value)
        return "neutral"
