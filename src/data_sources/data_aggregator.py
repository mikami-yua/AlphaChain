"""
Data aggregator for combining data from multiple sources
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.crypto_data import CryptoData, PriceData, MarketData, DataSource
from .bloomberg import BloombergDataSource
from .tradingview import TradingViewDataSource
from .glassnode import GlassnodeDataSource
from .defillama import DefiLlamaDataSource
from loguru import logger


class DataAggregator:
    """Aggregates data from multiple sources"""
    
    def __init__(self, config):
        self.config = config
        self.sources = {}
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize data sources based on configuration"""
        # Bloomberg
        if self.config.bloomberg_api_key:
            self.sources[DataSource.BLOOMBERG] = BloombergDataSource(
                api_key=self.config.bloomberg_api_key,
                base_url=self.config.bloomberg_base_url
            )
        
        # TradingView
        if self.config.tradingview_username and self.config.tradingview_password:
            self.sources[DataSource.TRADINGVIEW] = TradingViewDataSource(
                username=self.config.tradingview_username,
                password=self.config.tradingview_password
            )
        
        # Glassnode
        if self.config.glassnode_api_key:
            self.sources[DataSource.GLASSNODE] = GlassnodeDataSource(
                api_key=self.config.glassnode_api_key,
                base_url=self.config.glassnode_base_url
            )
        
        # DefiLlama (no API key required)
        self.sources[DataSource.DEFILLAMA] = DefiLlamaDataSource(
            base_url=self.config.defillama_base_url
        )
        
        logger.info(f"Initialized {len(self.sources)} data sources: {list(self.sources.keys())}")
    
    async def get_crypto_data(self, symbol: str) -> Optional[CryptoData]:
        """Get comprehensive crypto data from all available sources"""
        symbol = symbol.upper()
        
        # Collect data from all sources in parallel
        tasks = []
        for source in self.sources.values():
            tasks.append(source.get_market_data(symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        market_data_list = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error getting data from source {i}: {result}")
                continue
            
            if result:
                market_data_list.append(result)
        
        if not market_data_list:
            logger.warning(f"No market data found for {symbol}")
            return None
        
        # Aggregate the data
        return self._aggregate_market_data(symbol, market_data_list)
    
    async def get_price_data(self, symbol: str) -> List[PriceData]:
        """Get price data from all sources"""
        symbol = symbol.upper()
        
        tasks = []
        for source in self.sources.values():
            tasks.append(source.get_crypto_price(symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        price_data_list = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error getting price from source {i}: {result}")
                continue
            
            if result:
                price_data_list.append(result)
        
        return price_data_list
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PriceData]:
        """Get historical data from all sources"""
        symbol = symbol.upper()
        
        tasks = []
        for source in self.sources.values():
            tasks.append(source.get_historical_prices(symbol, start_date, end_date))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_historical_data = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error getting historical data from source {i}: {result}")
                continue
            
            if result:
                all_historical_data.extend(result)
        
        # Sort by timestamp
        all_historical_data.sort(key=lambda x: x.timestamp)
        
        return all_historical_data
    
    async def search_crypto(self, query: str) -> Dict[DataSource, List[Dict[str, Any]]]:
        """Search for cryptocurrencies across all sources"""
        tasks = []
        source_names = []
        
        for source_name, source in self.sources.items():
            tasks.append(source.search_crypto(query))
            source_names.append(source_name)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        search_results = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error searching in source {source_names[i]}: {result}")
                search_results[source_names[i]] = []
            else:
                search_results[source_names[i]] = result
        
        return search_results
    
    def _aggregate_market_data(self, symbol: str, market_data_list: List[MarketData]) -> CryptoData:
        """Aggregate market data from multiple sources"""
        if not market_data_list:
            return None
        
        # Use the most recent data as base
        latest_market_data = max(market_data_list, key=lambda x: x.timestamp)
        
        # Aggregate technical indicators from all sources
        all_indicators = []
        for market_data in market_data_list:
            all_indicators.extend(market_data.technical_indicators)
        
        # Remove duplicates and keep the most recent
        unique_indicators = {}
        for indicator in all_indicators:
            key = indicator.name
            if key not in unique_indicators or indicator.timestamp > unique_indicators[key].timestamp:
                unique_indicators[key] = indicator
        
        # Update the latest market data with aggregated indicators
        latest_market_data.technical_indicators = list(unique_indicators.values())
        
        # Calculate aggregated sentiment
        sentiments = [md.market_sentiment for md in market_data_list if md.market_sentiment]
        aggregated_sentiment = self._calculate_aggregated_sentiment(sentiments)
        
        # Create comprehensive crypto data
        crypto_data = CryptoData(
            symbol=symbol,
            name=symbol,  # Could be enhanced with name mapping
            market_data=market_data_list,
            fundamental_data=self._extract_fundamental_data(market_data_list),
            news_sentiment=aggregated_sentiment,
            last_updated=datetime.utcnow()
        )
        
        return crypto_data
    
    def _calculate_aggregated_sentiment(self, sentiments: List[str]) -> Optional[str]:
        """Calculate aggregated sentiment from multiple sources"""
        if not sentiments:
            return None
        
        sentiment_scores = {
            "bullish": 1,
            "bearish": -1,
            "neutral": 0
        }
        
        total_score = sum(sentiment_scores.get(s, 0) for s in sentiments)
        avg_score = total_score / len(sentiments)
        
        if avg_score > 0.3:
            return "bullish"
        elif avg_score < -0.3:
            return "bearish"
        else:
            return "neutral"
    
    def _extract_fundamental_data(self, market_data_list: List[MarketData]) -> Dict[str, Any]:
        """Extract fundamental data from market data"""
        fundamental_data = {}
        
        for market_data in market_data_list:
            if market_data.price_data.market_cap:
                fundamental_data["market_cap"] = market_data.price_data.market_cap
            
            if market_data.volatility:
                fundamental_data["volatility"] = market_data.volatility
            
            # Add source-specific fundamental data
            if market_data.source == DataSource.GLASSNODE:
                fundamental_data["on_chain_metrics"] = True
            elif market_data.source == DataSource.DEFILLAMA:
                fundamental_data["defi_metrics"] = True
        
        return fundamental_data
    
    async def close(self):
        """Close all data source connections"""
        for source in self.sources.values():
            await source.close()
        
        logger.info("All data source connections closed")
    
    def get_available_sources(self) -> List[DataSource]:
        """Get list of available data sources"""
        return list(self.sources.keys())
    
    def get_source_status(self) -> Dict[DataSource, bool]:
        """Get status of all data sources"""
        status = {}
        for source_name, source in self.sources.items():
            # Simple check - if source is initialized, consider it available
            status[source_name] = source is not None
        return status
