#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to check which data sources work without API keys
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

async def test_defillama_no_api():
    """Test DefiLlama without API key"""
    try:
        from src.data_sources.defillama import DefiLlamaDataSource
        
        print("Testing DefiLlama (no API key required)...")
        defillama = DefiLlamaDataSource()
        
        # Test search functionality
        search_results = await defillama.search_crypto("bitcoin")
        print(f"✓ DefiLlama search works: Found {len(search_results)} results")
        
        # Test price data (this might fail due to API changes)
        try:
            price_data = await defillama.get_crypto_price("BTC")
            if price_data:
                print(f"✓ DefiLlama price data works: BTC @ ${price_data.price}")
            else:
                print("⚠ DefiLlama price data: No data returned")
        except Exception as e:
            print(f"⚠ DefiLlama price data failed: {e}")
        
        await defillama.close()
        return True
        
    except Exception as e:
        print(f"❌ DefiLlama test failed: {e}")
        return False

async def test_tradingview_no_api():
    """Test TradingView without API key"""
    try:
        from src.data_sources.tradingview import TradingViewDataSource
        
        print("\nTesting TradingView (no API key required)...")
        tradingview = TradingViewDataSource()  # No credentials
        
        # Test search functionality
        search_results = await tradingview.search_crypto("bitcoin")
        print(f"✓ TradingView search works: Found {len(search_results)} results")
        
        # Test price data
        try:
            price_data = await tradingview.get_crypto_price("BTC")
            if price_data:
                print(f"✓ TradingView price data works: BTC @ ${price_data.price}")
            else:
                print("⚠ TradingView price data: No data returned")
        except Exception as e:
            print(f"⚠ TradingView price data failed: {e}")
        
        await tradingview.close()
        return True
        
    except Exception as e:
        print(f"❌ TradingView test failed: {e}")
        return False

async def test_bloomberg_no_api():
    """Test Bloomberg without API key"""
    try:
        from src.data_sources.bloomberg import BloombergDataSource
        
        print("\nTesting Bloomberg (API key required)...")
        # This should fail without API key
        bloomberg = BloombergDataSource("")  # Empty API key
        
        search_results = await bloomberg.search_crypto("bitcoin")
        if search_results:
            print(f"✓ Bloomberg search works: Found {len(search_results)} results")
            return True
        else:
            print("⚠ Bloomberg requires API key")
            return False
        
    except Exception as e:
        print(f"❌ Bloomberg test failed: {e}")
        return False

async def test_glassnode_no_api():
    """Test Glassnode without API key"""
    try:
        from src.data_sources.glassnode import GlassnodeDataSource
        
        print("\nTesting Glassnode (API key required)...")
        # This should fail without API key
        glassnode = GlassnodeDataSource("")  # Empty API key
        
        search_results = await glassnode.search_crypto("bitcoin")
        if search_results:
            print(f"✓ Glassnode search works: Found {len(search_results)} results")
            return True
        else:
            print("⚠ Glassnode requires API key")
            return False
        
    except Exception as e:
        print(f"❌ Glassnode test failed: {e}")
        return False

async def test_public_apis():
    """Test some public APIs that don't require keys"""
    try:
        import aiohttp
        
        print("\nTesting public APIs...")
        
        # Test CoinGecko API (public)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd") as response:
                    if response.status == 200:
                        data = await response.json()
                        btc_price = data.get("bitcoin", {}).get("usd", 0)
                        print(f"✓ CoinGecko API works: BTC @ ${btc_price}")
                    else:
                        print(f"⚠ CoinGecko API error: {response.status}")
            except Exception as e:
                print(f"⚠ CoinGecko API failed: {e}")
            
            # Test CoinCap API (public)
            try:
                async with session.get("https://api.coincap.io/v2/assets/bitcoin") as response:
                    if response.status == 200:
                        data = await response.json()
                        btc_price = data.get("data", {}).get("priceUsd", 0)
                        print(f"✓ CoinCap API works: BTC @ ${float(btc_price):,.2f}")
                    else:
                        print(f"⚠ CoinCap API error: {response.status}")
            except Exception as e:
                print(f"⚠ CoinCap API failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Public APIs test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Data Sources - No API Key Required")
    print("=" * 60)
    
    tests = [
        ("DefiLlama", test_defillama_no_api),
        ("TradingView", test_tradingview_no_api),
        ("Bloomberg", test_bloomberg_no_api),
        ("Glassnode", test_glassnode_no_api),
        ("Public APIs", test_public_apis)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Testing {test_name}")
        print(f"{'-' * 40}")
        
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("SUMMARY - Data Sources Without API Keys")
    print("=" * 60)
    
    working_sources = []
    limited_sources = []
    requires_api = []
    
    for source, result in results.items():
        if result:
            working_sources.append(source)
        elif source in ["Bloomberg", "Glassnode"]:
            requires_api.append(source)
        else:
            limited_sources.append(source)
    
    print(f"\n✅ FULLY WORKING (No API key required):")
    for source in working_sources:
        print(f"   - {source}")
    
    print(f"\n⚠️  LIMITED FUNCTIONALITY:")
    for source in limited_sources:
        print(f"   - {source}")
    
    print(f"\n🔑 REQUIRES API KEY:")
    for source in requires_api:
        print(f"   - {source}")
    
    print(f"\n📊 RECOMMENDED PUBLIC ALTERNATIVES:")
    print("   - CoinGecko API (completely free)")
    print("   - CoinCap API (completely free)")
    print("   - CryptoCompare API (free tier)")
    print("   - Binance API (free, but rate limited)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
