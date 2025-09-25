"""
Base data source interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.crypto_data import CryptoData, PriceData, MarketData, TechnicalIndicator, DataSource


class BaseDataSource(ABC):
    """Base class for all data sources"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    @abstractmethod
    async def get_crypto_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for a cryptocurrency"""
        pass
    
    @abstractmethod
    async def get_historical_prices(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PriceData]:
        """Get historical price data"""
        pass
    
    @abstractmethod
    async def get_technical_indicators(
        self, 
        symbol: str, 
        indicators: List[str]
    ) -> List[TechnicalIndicator]:
        """Get technical indicators for a symbol"""
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get comprehensive market data"""
        pass
    
    @abstractmethod
    async def search_crypto(self, query: str) -> List[Dict[str, Any]]:
        """Search for cryptocurrencies"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> DataSource:
        """Get the data source name"""
        pass
    
    async def close(self):
        """Close the data source connection"""
        if self.session:
            await self.session.close()
    
    def _validate_symbol(self, symbol: str) -> str:
        """Validate and normalize symbol format"""
        return symbol.upper().replace("-", "").replace("_", "")
    
    def _get_timestamp(self) -> datetime:
        """Get current timestamp"""
        return datetime.utcnow()
