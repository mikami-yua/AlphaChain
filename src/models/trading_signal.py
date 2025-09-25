"""
Trading signal models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SignalType(str, Enum):
    """Trading signal types"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


class SignalStrength(str, Enum):
    """Signal strength levels"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class TradingSignal(BaseModel):
    """Trading signal structure"""
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    confidence: float = Field(..., ge=0.0, le=1.0)
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    reasoning: str
    technical_indicators: Dict[str, Any] = {}
    fundamental_factors: Dict[str, Any] = {}
    timestamp: datetime
    source: str
    
    def is_buy_signal(self) -> bool:
        """Check if this is a buy signal"""
        return self.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]
    
    def is_sell_signal(self) -> bool:
        """Check if this is a sell signal"""
        return self.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]
    
    def is_hold_signal(self) -> bool:
        """Check if this is a hold signal"""
        return self.signal_type == SignalType.HOLD
