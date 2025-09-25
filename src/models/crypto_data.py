"""
Crypto data models and structures
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class DataSource(str, Enum):
    """Data source enumeration"""
    BLOOMBERG = "bloomberg"
    TRADINGVIEW = "tradingview"
    GLASSNODE = "glassnode"
    DEFILLAMA = "defillama"


class PriceData(BaseModel):
    """Price data structure"""
    symbol: str
    price: float
    volume: float
    market_cap: Optional[float] = None
    timestamp: datetime
    source: DataSource
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TechnicalIndicator(BaseModel):
    """Technical indicator data"""
    name: str
    value: float
    signal: str  # "bullish", "bearish", "neutral"
    timestamp: datetime
    source: DataSource


class MarketData(BaseModel):
    """Market data structure"""
    symbol: str
    price_data: PriceData
    technical_indicators: List[TechnicalIndicator] = []
    market_sentiment: Optional[str] = None
    volatility: Optional[float] = None
    timestamp: datetime
    source: DataSource


class CryptoData(BaseModel):
    """Main crypto data structure"""
    symbol: str
    name: str
    market_data: List[MarketData]
    fundamental_data: Dict[str, Any] = {}
    news_sentiment: Optional[str] = None
    last_updated: datetime
    
    def get_latest_price(self) -> Optional[float]:
        """Get the latest price from market data"""
        if not self.market_data:
            return None
        return self.market_data[-1].price_data.price
    
    def get_price_change_24h(self) -> Optional[float]:
        """Calculate 24h price change percentage"""
        if len(self.market_data) < 2:
            return None
        
        current_price = self.market_data[-1].price_data.price
        previous_price = self.market_data[-2].price_data.price
        
        return ((current_price - previous_price) / previous_price) * 100
    
    def get_technical_signal(self, indicator_name: str) -> Optional[str]:
        """Get technical signal for specific indicator"""
        for market_data in self.market_data:
            for indicator in market_data.technical_indicators:
                if indicator.name == indicator_name:
                    return indicator.signal
        return None
