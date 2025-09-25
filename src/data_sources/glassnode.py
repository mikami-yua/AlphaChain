"""
Glassnode data source implementation
"""
import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.crypto_data import PriceData, MarketData, TechnicalIndicator, DataSource
from .base import BaseDataSource
from loguru import logger


class GlassnodeDataSource(BaseDataSource):
    """Glassnode API data source for on-chain analytics"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.glassnode.com"):
        super().__init__(api_key, base_url)
        self.headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to Glassnode API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        if params is None:
            params = {}
        
        try:
            async with self.session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Glassnode API error: {response.status} - {await response.text()}")
                    return {}
        except Exception as e:
            logger.error(f"Error making Glassnode request: {e}")
            return {}
    
    async def get_crypto_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for a cryptocurrency from Glassnode"""
        symbol = self._validate_symbol(symbol)
        
        # Glassnode uses different symbol format (e.g., BTC, ETH)
        glassnode_symbol = self._convert_to_glassnode_symbol(symbol)
        if not glassnode_symbol:
            logger.warning(f"Unsupported symbol {symbol} for Glassnode")
            return None
        
        endpoint = f"/v1/metrics/market/price_usd_close"
        params = {
            "a": glassnode_symbol,
            "f": "JSON",
            "timestamp_format": "unix"
        }
        
        data = await self._make_request(endpoint, params)
        
        if not data or not isinstance(data, list) or len(data) == 0:
            logger.warning(f"No price data found for {symbol} from Glassnode")
            return None
        
        # Get the latest price data
        latest_data = data[-1]
        
        return PriceData(
            symbol=symbol,
            price=float(latest_data["v"]),
            volume=0,  # Glassnode doesn't provide volume in price endpoint
            market_cap=None,
            timestamp=datetime.fromtimestamp(latest_data["t"]),
            source=DataSource.GLASSNODE
        )
    
    async def get_historical_prices(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PriceData]:
        """Get historical price data from Glassnode"""
        symbol = self._validate_symbol(symbol)
        glassnode_symbol = self._convert_to_glassnode_symbol(symbol)
        
        if not glassnode_symbol:
            logger.warning(f"Unsupported symbol {symbol} for Glassnode")
            return []
        
        endpoint = f"/v1/metrics/market/price_usd_close"
        params = {
            "a": glassnode_symbol,
            "f": "JSON",
            "timestamp_format": "unix",
            "s": int(start_date.timestamp()),
            "i": "24h"
        }
        
        data = await self._make_request(endpoint, params)
        
        if not data or not isinstance(data, list):
            logger.warning(f"No historical data found for {symbol} from Glassnode")
            return []
        
        prices = []
        for price_data in data:
            price_timestamp = datetime.fromtimestamp(price_data["t"])
            if start_date <= price_timestamp <= end_date:
                prices.append(PriceData(
                    symbol=symbol,
                    price=float(price_data["v"]),
                    volume=0,
                    market_cap=None,
                    timestamp=price_timestamp,
                    source=DataSource.GLASSNODE
                ))
        
        return prices
    
    async def get_technical_indicators(
        self, 
        symbol: str, 
        indicators: List[str]
    ) -> List[TechnicalIndicator]:
        """Get technical indicators from Glassnode (on-chain metrics)"""
        symbol = self._validate_symbol(symbol)
        glassnode_symbol = self._convert_to_glassnode_symbol(symbol)
        
        if not glassnode_symbol:
            logger.warning(f"Unsupported symbol {symbol} for Glassnode")
            return []
        
        technical_indicators = []
        
        # Map indicators to Glassnode metrics
        indicator_mapping = {
            "RSI": "market/market_cap_realized_usd",
            "MACD": "market/price_usd_close",
            "SMA_20": "market/price_usd_close",
            "SMA_50": "market/price_usd_close",
            "NVT": "market/market_cap_nvt",
            "MVRV": "market/market_cap_mvrv",
            "SOPR": "market/sopr",
            "Active_Addresses": "addresses/active_count",
            "Exchange_Flow": "transactions/transfers_volume_exchanges_entities"
        }
        
        for indicator in indicators:
            if indicator in indicator_mapping:
                endpoint = f"/v1/metrics/{indicator_mapping[indicator]}"
                params = {
                    "a": glassnode_symbol,
                    "f": "JSON",
                    "timestamp_format": "unix",
                    "i": "24h"
                }
                
                data = await self._make_request(endpoint, params)
                
                if data and isinstance(data, list) and len(data) > 0:
                    latest_value = data[-1]["v"]
                    signal = self._determine_onchain_signal(indicator, latest_value)
                    
                    technical_indicators.append(TechnicalIndicator(
                        name=indicator,
                        value=float(latest_value),
                        signal=signal,
                        timestamp=self._get_timestamp(),
                        source=DataSource.GLASSNODE
                    ))
        
        return technical_indicators
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get comprehensive market data from Glassnode"""
        symbol = self._validate_symbol(symbol)
        
        # Get price data
        price_data = await self.get_crypto_price(symbol)
        if not price_data:
            return None
        
        # Get on-chain indicators
        indicators = ["NVT", "MVRV", "SOPR", "Active_Addresses", "Exchange_Flow"]
        technical_indicators = await self.get_technical_indicators(symbol, indicators)
        
        # Get market sentiment from on-chain metrics
        sentiment_data = await self._get_market_sentiment(symbol)
        
        return MarketData(
            symbol=symbol,
            price_data=price_data,
            technical_indicators=technical_indicators,
            market_sentiment=sentiment_data.get("sentiment"),
            volatility=sentiment_data.get("volatility"),
            timestamp=self._get_timestamp(),
            source=DataSource.GLASSNODE
        )
    
    async def search_crypto(self, query: str) -> List[Dict[str, Any]]:
        """Search for cryptocurrencies on Glassnode"""
        # Glassnode supports limited cryptocurrencies
        supported_assets = ["BTC", "ETH", "LTC", "BCH", "XRP", "ADA", "DOT", "LINK", "UNI", "AAVE"]
        
        results = []
        query_upper = query.upper()
        
        for asset in supported_assets:
            if query_upper in asset or query_upper in asset:
                results.append({
                    "symbol": asset,
                    "name": asset,
                    "source": "glassnode"
                })
        
        return results
    
    def get_source_name(self) -> DataSource:
        """Get the data source name"""
        return DataSource.GLASSNODE
    
    def _convert_to_glassnode_symbol(self, symbol: str) -> Optional[str]:
        """Convert symbol to Glassnode format"""
        symbol_mapping = {
            "BTC": "BTC",
            "BITCOIN": "BTC",
            "ETH": "ETH",
            "ETHEREUM": "ETH",
            "LTC": "LTC",
            "LITECOIN": "LTC",
            "BCH": "BCH",
            "BITCOINCASH": "BCH",
            "XRP": "XRP",
            "RIPPLE": "XRP",
            "ADA": "ADA",
            "CARDANO": "ADA",
            "DOT": "DOT",
            "POLKADOT": "DOT",
            "LINK": "LINK",
            "CHAINLINK": "LINK",
            "UNI": "UNI",
            "UNISWAP": "UNI",
            "AAVE": "AAVE"
        }
        
        return symbol_mapping.get(symbol.upper())
    
    def _determine_onchain_signal(self, indicator_name: str, value: float) -> str:
        """Determine signal based on on-chain indicator value"""
        signal_rules = {
            "NVT": lambda v: "bearish" if v > 50 else "bullish" if v < 20 else "neutral",
            "MVRV": lambda v: "bearish" if v > 3 else "bullish" if v < 1 else "neutral",
            "SOPR": lambda v: "bearish" if v > 1.05 else "bullish" if v < 0.95 else "neutral",
            "Active_Addresses": lambda v: "bullish" if v > 0 else "bearish",
            "Exchange_Flow": lambda v: "bearish" if v > 0 else "bullish",  # Negative flow is bullish
        }
        
        rule = signal_rules.get(indicator_name)
        if rule:
            return rule(value)
        return "neutral"
    
    async def _get_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get market sentiment from on-chain metrics"""
        glassnode_symbol = self._convert_to_glassnode_symbol(symbol)
        if not glassnode_symbol:
            return {"sentiment": None, "volatility": None}
        
        # Get multiple metrics for sentiment analysis
        endpoints = [
            "/v1/metrics/market/sopr",
            "/v1/metrics/market/mvrv",
            "/v1/metrics/addresses/active_count"
        ]
        
        metrics = {}
        for endpoint in endpoints:
            params = {
                "a": glassnode_symbol,
                "f": "JSON",
                "timestamp_format": "unix",
                "i": "24h"
            }
            
            data = await self._make_request(endpoint, params)
            if data and isinstance(data, list) and len(data) > 0:
                metric_name = endpoint.split("/")[-1]
                metrics[metric_name] = data[-1]["v"]
        
        # Simple sentiment calculation
        sentiment = "neutral"
        if metrics:
            sopr = metrics.get("sopr", 1.0)
            mvrv = metrics.get("mvrv", 1.0)
            
            if sopr > 1.05 and mvrv > 2.0:
                sentiment = "bearish"
            elif sopr < 0.95 and mvrv < 1.5:
                sentiment = "bullish"
        
        return {
            "sentiment": sentiment,
            "volatility": None  # Glassnode doesn't provide volatility directly
        }
