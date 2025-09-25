#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Basic test script to verify project structure without LangChain dependencies
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test if basic modules can be imported"""
    try:
        print("Testing basic imports...")
        
        # Test config
        from config import settings
        print("✓ Config imported successfully")
        
        # Test models
        from src.models.crypto_data import CryptoData, PriceData, MarketData, DataSource
        from src.models.trading_signal import TradingSignal, SignalType, SignalStrength
        print("✓ Models imported successfully")
        
        # Test data sources (without LangChain dependencies)
        from src.data_sources.base import BaseDataSource
        from src.data_sources.bloomberg import BloombergDataSource
        from src.data_sources.tradingview import TradingViewDataSource
        from src.data_sources.glassnode import GlassnodeDataSource
        from src.data_sources.defillama import DefiLlamaDataSource
        from src.data_sources.data_aggregator import DataAggregator
        print("✓ Data sources imported successfully")
        
        # Test utils
        from src.utils.helpers import format_price, validate_symbol, calculate_percentage_change
        print("✓ Utils imported successfully")
        
        print("\n🎉 All basic imports successful! Project structure is correct.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_data_models():
    """Test data models functionality"""
    try:
        from src.models.crypto_data import PriceData, MarketData, DataSource
        from src.models.trading_signal import TradingSignal, SignalType, SignalStrength
        from datetime import datetime
        
        print("\nTesting data models...")
        
        # Test PriceData creation
        price = PriceData(
            symbol="BTC",
            price=50000.0,
            volume=1000000.0,
            timestamp=datetime.now(),
            source=DataSource.DEFILLAMA
        )
        print(f"✓ PriceData created: {price.symbol} @ ${price.price}")
        
        # Test TradingSignal creation
        signal = TradingSignal(
            symbol="BTC",
            signal_type=SignalType.BUY,
            strength=SignalStrength.STRONG,
            confidence=0.8,
            reasoning="Strong technical indicators",
            timestamp=datetime.now(),
            source="Test"
        )
        print(f"✓ TradingSignal created: {signal.signal_type} - {signal.strength}")
        
        # Test signal methods
        assert signal.is_buy_signal() == True
        assert signal.is_sell_signal() == False
        print("✓ TradingSignal methods working correctly")
        
        return True
    except Exception as e:
        print(f"❌ Data model error: {e}")
        return False

def test_utils():
    """Test utility functions"""
    try:
        from src.utils.helpers import format_price, validate_symbol, calculate_percentage_change
        
        print("\nTesting utility functions...")
        
        # Test format_price
        assert format_price(50000.0) == "$50,000.00"
        assert format_price(0.001) == "$0.00100000"
        print("✓ format_price working correctly")
        
        # Test validate_symbol
        assert validate_symbol("BTC") == True
        assert validate_symbol("") == False
        assert validate_symbol("A" * 20) == False
        print("✓ validate_symbol working correctly")
        
        # Test calculate_percentage_change
        assert calculate_percentage_change(100, 110) == 10.0
        assert calculate_percentage_change(100, 90) == -10.0
        print("✓ calculate_percentage_change working correctly")
        
        return True
    except Exception as e:
        print(f"❌ Utility function error: {e}")
        return False

def test_data_sources():
    """Test data source initialization"""
    try:
        from src.data_sources.defillama import DefiLlamaDataSource
        from src.data_sources.data_aggregator import DataAggregator
        from config import settings
        
        print("\nTesting data sources...")
        
        # Test DefiLlama (no API key required)
        defillama = DefiLlamaDataSource()
        assert defillama.get_source_name().value == "defillama"
        print("✓ DefiLlama data source initialized")
        
        # Test DataAggregator
        aggregator = DataAggregator(settings)
        available_sources = aggregator.get_available_sources()
        print(f"✓ DataAggregator initialized with sources: {[s.value for s in available_sources]}")
        
        return True
    except Exception as e:
        print(f"❌ Data source error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AlphaChain - Basic Project Setup Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Data Model Test", test_data_models),
        ("Utility Functions Test", test_utils),
        ("Data Sources Test", test_data_sources)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! Project structure is working.")
        print("\nProject features implemented:")
        print("✓ Data models for crypto data and trading signals")
        print("✓ Data source interfaces for Bloomberg, TradingView, Glassnode, DefiLlama")
        print("✓ Data aggregator for combining multiple sources")
        print("✓ Utility functions for data processing")
        print("✓ Configuration management")
        print("\nNext steps:")
        print("1. Install LangChain dependencies: pip install langchain langchain-openai")
        print("2. Copy env.example to .env and configure API keys")
        print("3. Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
