#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify project setup
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test config
        from config import settings
        print("✓ Config imported successfully")
        
        # Test models
        from src.models.crypto_data import CryptoData, PriceData, MarketData
        from src.models.trading_signal import TradingSignal, SignalType
        print("✓ Models imported successfully")
        
        # Test data sources
        from src.data_sources.base import BaseDataSource
        from src.data_sources.bloomberg import BloombergDataSource
        from src.data_sources.tradingview import TradingViewDataSource
        from src.data_sources.glassnode import GlassnodeDataSource
        from src.data_sources.defillama import DefiLlamaDataSource
        from src.data_sources.data_aggregator import DataAggregator
        print("✓ Data sources imported successfully")
        
        # Test agents
        from src.agents.crypto_agent import CryptoAgent
        print("✓ Agents imported successfully")
        
        # Test utils
        from src.utils.helpers import format_price, validate_symbol
        print("✓ Utils imported successfully")
        
        print("\n🎉 All imports successful! Project structure is correct.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration"""
    try:
        from config import settings
        print(f"\nConfiguration test:")
        print(f"✓ OpenAI API Key configured: {'Yes' if settings.openai_api_key else 'No'}")
        print(f"✓ Bloomberg API Key configured: {'Yes' if settings.bloomberg_api_key else 'No'}")
        print(f"✓ TradingView credentials configured: {'Yes' if settings.tradingview_username else 'No'}")
        print(f"✓ Glassnode API Key configured: {'Yes' if settings.glassnode_api_key else 'No'}")
        print(f"✓ Database URL: {settings.database_url}")
        print(f"✓ Log level: {settings.log_level}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_data_models():
    """Test data models"""
    try:
        from src.models.crypto_data import PriceData, DataSource
        from datetime import datetime
        
        # Test PriceData creation
        price = PriceData(
            symbol="BTC",
            price=50000.0,
            volume=1000000.0,
            timestamp=datetime.utcnow(),
            source=DataSource.DEFILLAMA
        )
        
        print(f"\nData model test:")
        print(f"✓ PriceData created: {price.symbol} @ ${price.price}")
        return True
    except Exception as e:
        print(f"❌ Data model error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("AlphaChain - Project Setup Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Data Model Test", test_data_models)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Project is ready to use.")
        print("\nNext steps:")
        print("1. Copy env.example to .env and configure API keys")
        print("2. Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
