"""
DefiLlama data source implementation
"""
import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.crypto_data import PriceData, MarketData, TechnicalIndicator, DataSource
from .base import BaseDataSource
from loguru import logger


class DefiLlamaDataSource(BaseDataSource):
    """DefiLlama API data source for DeFi and crypto data"""
    
    def __init__(self, base_url: str = "https://api.llama.fi"):
        super().__init__(None, base_url)
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CryptoAgent/1.0"
        }
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make request to DefiLlama API"""
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
                    logger.error(f"DefiLlama API error: {response.status} - {await response.text()}")
                    return {}
        except Exception as e:
            logger.error(f"Error making DefiLlama request: {e}")
            return {}
    
    async def get_crypto_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for a cryptocurrency from DefiLlama"""
        symbol = self._validate_symbol(symbol)
        
        # DefiLlama uses different symbol format
        defillama_symbol = self._convert_to_defillama_symbol(symbol)
        if not defillama_symbol:
            logger.warning(f"Unsupported symbol {symbol} for DefiLlama")
            return None
        
        endpoint = f"/prices/current/{defillama_symbol}"
        
        data = await self._make_request(endpoint)
        
        if not data or defillama_symbol not in data:
            logger.warning(f"No price data found for {symbol} from DefiLlama")
            return None
        
        price_info = data[defillama_symbol]
        
        return PriceData(
            symbol=symbol,
            price=float(price_info.get("price", 0)),
            volume=0,  # DefiLlama doesn't provide volume in price endpoint
            market_cap=float(price_info.get("market_cap", 0)) if price_info.get("market_cap") else None,
            timestamp=self._get_timestamp(),
            source=DataSource.DEFILLAMA
        )
    
    async def get_historical_prices(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PriceData]:
        """Get historical price data from DefiLlama"""
        symbol = self._validate_symbol(symbol)
        defillama_symbol = self._convert_to_defillama_symbol(symbol)
        
        if not defillama_symbol:
            logger.warning(f"Unsupported symbol {symbol} for DefiLlama")
            return []
        
        # Calculate days difference
        days = (end_date - start_date).days
        
        endpoint = f"/prices/historical/{defillama_symbol}"
        params = {
            "start": int(start_date.timestamp()),
            "end": int(end_date.timestamp())
        }
        
        data = await self._make_request(endpoint, params)
        
        if not data or "prices" not in data:
            logger.warning(f"No historical data found for {symbol} from DefiLlama")
            return []
        
        prices = []
        for price_data in data["prices"]:
            prices.append(PriceData(
                symbol=symbol,
                price=float(price_data["price"]),
                volume=0,
                market_cap=float(price_data.get("market_cap", 0)) if price_data.get("market_cap") else None,
                timestamp=datetime.fromtimestamp(price_data["timestamp"]),
                source=DataSource.DEFILLAMA
            ))
        
        return prices
    
    async def get_technical_indicators(
        self, 
        symbol: str, 
        indicators: List[str]
    ) -> List[TechnicalIndicator]:
        """Get technical indicators from DefiLlama (DeFi metrics)"""
        symbol = self._validate_symbol(symbol)
        defillama_symbol = self._convert_to_defillama_symbol(symbol)
        
        if not defillama_symbol:
            logger.warning(f"Unsupported symbol {symbol} for DefiLlama")
            return []
        
        technical_indicators = []
        
        # Get DeFi-specific metrics
        for indicator in indicators:
            if indicator in ["TVL", "Volume_24h", "Fees_24h", "Revenue_24h"]:
                endpoint = f"/protocols/{defillama_symbol}"
                
                data = await self._make_request(endpoint)
                
                if data and "tvl" in data:
                    value = self._extract_indicator_value(data, indicator)
                    if value is not None:
                        signal = self._determine_defi_signal(indicator, value)
                        
                        technical_indicators.append(TechnicalIndicator(
                            name=indicator,
                            value=float(value),
                            signal=signal,
                            timestamp=self._get_timestamp(),
                            source=DataSource.DEFILLAMA
                        ))
        
        return technical_indicators
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get comprehensive market data from DefiLlama"""
        symbol = self._validate_symbol(symbol)
        
        # Get price data
        price_data = await self.get_crypto_price(symbol)
        if not price_data:
            return None
        
        # Get DeFi indicators
        indicators = ["TVL", "Volume_24h", "Fees_24h", "Revenue_24h"]
        technical_indicators = await self.get_technical_indicators(symbol, indicators)
        
        # Get market sentiment from DeFi metrics
        sentiment_data = await self._get_defi_sentiment(symbol)
        
        return MarketData(
            symbol=symbol,
            price_data=price_data,
            technical_indicators=technical_indicators,
            market_sentiment=sentiment_data.get("sentiment"),
            volatility=sentiment_data.get("volatility"),
            timestamp=self._get_timestamp(),
            source=DataSource.DEFILLAMA
        )
    
    async def search_crypto(self, query: str) -> List[Dict[str, Any]]:
        """Search for cryptocurrencies on DefiLlama"""
        endpoint = "/protocols"
        
        data = await self._make_request(endpoint)
        
        if not data or not isinstance(data, list):
            logger.warning(f"No search results found for '{query}' on DefiLlama")
            return []
        
        results = []
        query_lower = query.lower()
        
        for protocol in data:
            if (query_lower in protocol.get("name", "").lower() or 
                query_lower in protocol.get("symbol", "").lower()):
                results.append({
                    "symbol": protocol.get("symbol", ""),
                    "name": protocol.get("name", ""),
                    "tvl": protocol.get("tvl", 0),
                    "source": "defillama"
                })
        
        # Sort by TVL (descending)
        results.sort(key=lambda x: x.get("tvl", 0), reverse=True)
        
        return results[:10]  # Return top 10 results
    
    def get_source_name(self) -> DataSource:
        """Get the data source name"""
        return DataSource.DEFILLAMA
    
    def _convert_to_defillama_symbol(self, symbol: str) -> Optional[str]:
        """Convert symbol to DefiLlama format"""
        symbol_mapping = {
            "BTC": "bitcoin",
            "BITCOIN": "bitcoin",
            "ETH": "ethereum",
            "ETHEREUM": "ethereum",
            "USDC": "usd-coin",
            "USDT": "tether",
            "DAI": "dai",
            "UNI": "uniswap",
            "UNISWAP": "uniswap",
            "AAVE": "aave",
            "COMP": "compound",
            "COMPOUND": "compound",
            "MKR": "maker",
            "MAKER": "maker",
            "YFI": "yearn-finance",
            "CRV": "curve-dao-token",
            "SUSHI": "sushi",
            "SUSHISWAP": "sushi",
            "1INCH": "1inch",
            "BAL": "balancer",
            "BALANCER": "balancer"
        }
        
        return symbol_mapping.get(symbol.upper())
    
    def _extract_indicator_value(self, data: Dict[str, Any], indicator: str) -> Optional[float]:
        """Extract indicator value from DefiLlama data"""
        if indicator == "TVL":
            return data.get("tvl", 0)
        elif indicator == "Volume_24h":
            return data.get("volume24h", 0)
        elif indicator == "Fees_24h":
            return data.get("fees24h", 0)
        elif indicator == "Revenue_24h":
            return data.get("revenue24h", 0)
        return None
    
    def _determine_defi_signal(self, indicator_name: str, value: float) -> str:
        """Determine signal based on DeFi indicator value"""
        signal_rules = {
            "TVL": lambda v: "bullish" if v > 1000000000 else "bearish" if v < 100000000 else "neutral",
            "Volume_24h": lambda v: "bullish" if v > 100000000 else "bearish" if v < 10000000 else "neutral",
            "Fees_24h": lambda v: "bullish" if v > 1000000 else "bearish" if v < 100000 else "neutral",
            "Revenue_24h": lambda v: "bullish" if v > 500000 else "bearish" if v < 50000 else "neutral",
        }
        
        rule = signal_rules.get(indicator_name)
        if rule:
            return rule(value)
        return "neutral"
    
    async def _get_defi_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get market sentiment from DeFi metrics"""
        defillama_symbol = self._convert_to_defillama_symbol(symbol)
        if not defillama_symbol:
            return {"sentiment": None, "volatility": None}
        
        # Get protocol data
        endpoint = f"/protocols/{defillama_symbol}"
        data = await self._make_request(endpoint)
        
        if not data:
            return {"sentiment": None, "volatility": None}
        
        # Simple sentiment calculation based on DeFi metrics
        sentiment = "neutral"
        tvl = data.get("tvl", 0)
        volume_24h = data.get("volume24h", 0)
        fees_24h = data.get("fees24h", 0)
        
        if tvl > 1000000000 and volume_24h > 100000000 and fees_24h > 1000000:
            sentiment = "bullish"
        elif tvl < 100000000 or volume_24h < 10000000 or fees_24h < 100000:
            sentiment = "bearish"
        
        return {
            "sentiment": sentiment,
            "volatility": None  # DefiLlama doesn't provide volatility directly
        }
