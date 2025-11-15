#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Real-world data source testing script

This script tests data fetching capabilities from various data sources
with real API calls (not mocked).

Usage:
    # From project root directory
    python -m src.data_sources.test_data_sources
    
    # Or from src/data_sources directory
    python test_data_sources.py
    
    # Test specific data source
    python -m src.data_sources.test_data_sources --source defillama
    
    # Test specific symbol
    python -m src.data_sources.test_data_sources --symbol BTC
    
    # Test with specific data source and symbol
    python -m src.data_sources.test_data_sources --source defillama --symbol BTC
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Add project root to path to import config
# Calculate project root: from src/data_sources/test_data_sources.py -> project root
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

# Verify project root exists and contains config.py
if not (project_root / "config.py").exists():
    print(f"Error: Cannot find config.py in project root: {project_root}")
    print(f"Current file location: {current_file}")
    print(f"Please run from project root using: python -m src.data_sources.test_data_sources")
    sys.exit(1)

try:
    from config import settings
except ImportError as e:
    print(f"Error importing config: {e}")
    print("\nPlease install dependencies:")
    print("  pip install -r requirements.txt")
    print("\nOr install pydantic-settings directly:")
    print("  pip install pydantic-settings")
    sys.exit(1)

from src.data_sources.defillama import DefiLlamaDataSource
from src.data_sources.tradingview import TradingViewDataSource
from src.data_sources.glassnode import GlassnodeDataSource
from src.data_sources.bloomberg import BloombergDataSource
from src.data_sources.data_aggregator import DataAggregator
from src.models.crypto_data import DataSource
from loguru import logger


class DataSourceTester:
    """Test data sources with real API calls"""

    def __init__(self):
        self.results = {}
        self.test_symbols = ["BTC", "ETH", "BNB"]  # Default test symbols

    async def test_defillama(self, symbol: str = "BTC") -> dict:
        """Test DefiLlama data source"""
        print(f"\n{'=' * 60}")
        print(f"Testing DefiLlama Data Source")
        print(f"{'=' * 60}")

        result = {
            "source": "DefiLlama",
            "status": "unknown",
            "tests": {}
        }

        try:
            source = DefiLlamaDataSource()

            # Test 1: Get current price
            print(f"\n[Test 1] Getting current price for {symbol}...")
            try:
                price_data = await source.get_crypto_price(symbol)
                if price_data:
                    result["tests"]["get_price"] = {
                        "status": "success",
                        "data": {
                            "symbol": price_data.symbol,
                            "price": price_data.price,
                            "market_cap": price_data.market_cap,
                            "timestamp": price_data.timestamp.isoformat()
                        }
                    }
                    print(f"✓ Price: ${price_data.price:,.2f}")
                    if price_data.market_cap:
                        print(f"  Market Cap: ${price_data.market_cap:,.0f}")
                else:
                    result["tests"]["get_price"] = {"status": "failed", "error": "No data returned"}
                    print("✗ No price data returned")
            except Exception as e:
                result["tests"]["get_price"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            # Test 2: Get market data
            print(f"\n[Test 2] Getting market data for {symbol}...")
            try:
                market_data = await source.get_market_data(symbol)
                if market_data:
                    result["tests"]["get_market_data"] = {
                        "status": "success",
                        "data": {
                            "symbol": market_data.symbol,
                            "price": market_data.price,
                            "volume_24h": market_data.volume_24h,
                            "market_cap": market_data.market_cap,
                            "price_change_24h": market_data.price_change_24h
                        }
                    }
                    print(f"✓ Market Data retrieved")
                    print(f"  Price: ${market_data.price:,.2f}")
                    if market_data.volume_24h:
                        print(f"  24h Volume: ${market_data.volume_24h:,.0f}")
                    if market_data.price_change_24h:
                        print(f"  24h Change: {market_data.price_change_24h:.2f}%")
                else:
                    result["tests"]["get_market_data"] = {"status": "failed", "error": "No data returned"}
                    print("✗ No market data returned")
            except Exception as e:
                result["tests"]["get_market_data"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            # Test 3: Search crypto
            print(f"\n[Test 3] Searching for 'bitcoin'...")
            try:
                search_results = await source.search_crypto("bitcoin")
                if search_results:
                    result["tests"]["search"] = {
                        "status": "success",
                        "count": len(search_results),
                        "sample": search_results[:3] if len(search_results) > 3 else search_results
                    }
                    print(f"✓ Found {len(search_results)} results")
                    for item in search_results[:3]:
                        print(f"  - {item.get('name', 'N/A')} ({item.get('symbol', 'N/A')})")
                else:
                    result["tests"]["search"] = {"status": "failed", "error": "No results"}
                    print("✗ No search results")
            except Exception as e:
                result["tests"]["search"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            # Test 4: Get historical prices
            print(f"\n[Test 4] Getting historical prices (last 7 days)...")
            try:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=7)
                historical = await source.get_historical_prices(symbol, start_date, end_date)
                if historical:
                    result["tests"]["historical"] = {
                        "status": "success",
                        "count": len(historical),
                        "date_range": {
                            "start": start_date.isoformat(),
                            "end": end_date.isoformat()
                        }
                    }
                    print(f"✓ Retrieved {len(historical)} historical data points")
                    if historical:
                        print(f"  First: ${historical[0].price:,.2f} at {historical[0].timestamp}")
                        print(f"  Last: ${historical[-1].price:,.2f} at {historical[-1].timestamp}")
                else:
                    result["tests"]["historical"] = {"status": "failed", "error": "No data"}
                    print("✗ No historical data")
            except Exception as e:
                result["tests"]["historical"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            await source.close()
            result["status"] = "success"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"\n✗ DefiLlama test failed: {e}")

        return result

    async def test_tradingview(self, symbol: str = "BTC") -> dict:
        """Test TradingView data source"""
        print(f"\n{'=' * 60}")
        print(f"Testing TradingView Data Source")
        print(f"{'=' * 60}")

        result = {
            "source": "TradingView",
            "status": "unknown",
            "tests": {}
        }

        try:
            username = settings.tradingview_username
            password = settings.tradingview_password

            if not username or not password:
                print("⚠ TradingView credentials not configured")
                print("   Set TRADINGVIEW_USERNAME and TRADINGVIEW_PASSWORD in .env")
                result["status"] = "skipped"
                result["reason"] = "Credentials not configured"
                return result

            source = TradingViewDataSource(username=username, password=password)

            # Test 1: Get current price
            print(f"\n[Test 1] Getting current price for {symbol}...")
            try:
                price_data = await source.get_crypto_price(symbol)
                if price_data:
                    result["tests"]["get_price"] = {
                        "status": "success",
                        "data": {
                            "symbol": price_data.symbol,
                            "price": price_data.price,
                            "timestamp": price_data.timestamp.isoformat()
                        }
                    }
                    print(f"✓ Price: ${price_data.price:,.2f}")
                else:
                    result["tests"]["get_price"] = {"status": "failed", "error": "No data"}
                    print("✗ No price data returned")
            except Exception as e:
                result["tests"]["get_price"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            # Test 2: Search
            print(f"\n[Test 2] Searching for 'bitcoin'...")
            try:
                search_results = await source.search_crypto("bitcoin")
                if search_results:
                    result["tests"]["search"] = {
                        "status": "success",
                        "count": len(search_results)
                    }
                    print(f"✓ Found {len(search_results)} results")
                else:
                    result["tests"]["search"] = {"status": "failed", "error": "No results"}
                    print("✗ No search results")
            except Exception as e:
                result["tests"]["search"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            await source.close()
            result["status"] = "success"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"\n✗ TradingView test failed: {e}")

        return result

    async def test_glassnode(self, symbol: str = "BTC") -> dict:
        """Test Glassnode data source"""
        print(f"\n{'=' * 60}")
        print(f"Testing Glassnode Data Source")
        print(f"{'=' * 60}")

        result = {
            "source": "Glassnode",
            "status": "unknown",
            "tests": {}
        }

        try:
            api_key = settings.glassnode_api_key

            if not api_key:
                print("⚠ Glassnode API key not configured")
                print("   Set GLASSNODE_API_KEY in .env")
                result["status"] = "skipped"
                result["reason"] = "API key not configured"
                return result

            source = GlassnodeDataSource(api_key=api_key, base_url=settings.glassnode_base_url)

            # Test 1: Get market data
            print(f"\n[Test 1] Getting market data for {symbol}...")
            try:
                market_data = await source.get_market_data(symbol)
                if market_data:
                    result["tests"]["get_market_data"] = {
                        "status": "success",
                        "data": {
                            "symbol": market_data.symbol,
                            "price": market_data.price
                        }
                    }
                    print(f"✓ Market data retrieved")
                    print(f"  Price: ${market_data.price:,.2f}")
                else:
                    result["tests"]["get_market_data"] = {"status": "failed", "error": "No data"}
                    print("✗ No market data returned")
            except Exception as e:
                result["tests"]["get_market_data"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            await source.close()
            result["status"] = "success"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"\n✗ Glassnode test failed: {e}")

        return result

    async def test_bloomberg(self, symbol: str = "BTC") -> dict:
        """Test Bloomberg data source"""
        print(f"\n{'=' * 60}")
        print(f"Testing Bloomberg Data Source")
        print(f"{'=' * 60}")

        result = {
            "source": "Bloomberg",
            "status": "unknown",
            "tests": {}
        }

        try:
            api_key = settings.bloomberg_api_key

            if not api_key:
                print("⚠ Bloomberg API key not configured")
                print("   Set BLOOMBERG_API_KEY in .env")
                result["status"] = "skipped"
                result["reason"] = "API key not configured"
                return result

            source = BloombergDataSource(api_key=api_key, base_url=settings.bloomberg_base_url)

            # Test 1: Get market data
            print(f"\n[Test 1] Getting market data for {symbol}...")
            try:
                market_data = await source.get_market_data(symbol)
                if market_data:
                    result["tests"]["get_market_data"] = {
                        "status": "success",
                        "data": {
                            "symbol": market_data.symbol,
                            "price": market_data.price
                        }
                    }
                    print(f"✓ Market data retrieved")
                    print(f"  Price: ${market_data.price:,.2f}")
                else:
                    result["tests"]["get_market_data"] = {"status": "failed", "error": "No data"}
                    print("✗ No market data returned")
            except Exception as e:
                result["tests"]["get_market_data"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            await source.close()
            result["status"] = "success"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"\n✗ Bloomberg test failed: {e}")

        return result

    async def test_data_aggregator(self, symbol: str = "BTC") -> dict:
        """Test DataAggregator with all available sources"""
        print(f"\n{'=' * 60}")
        print(f"Testing Data Aggregator (All Sources)")
        print(f"{'=' * 60}")

        result = {
            "source": "DataAggregator",
            "status": "unknown",
            "tests": {}
        }

        try:
            aggregator = DataAggregator(settings)

            available_sources = aggregator.get_available_sources()
            print(f"\nAvailable data sources: {[s.value for s in available_sources]}")

            # Test 1: Get price data from all sources
            print(f"\n[Test 1] Getting price data for {symbol} from all sources...")
            try:
                price_data_list = await aggregator.get_price_data(symbol)
                if price_data_list:
                    result["tests"]["get_price_data"] = {
                        "status": "success",
                        "count": len(price_data_list),
                        "sources": [p.source.value for p in price_data_list],
                        "prices": [
                            {
                                "source": p.source.value,
                                "price": p.price,
                                "symbol": p.symbol
                            }
                            for p in price_data_list
                        ]
                    }
                    print(f"✓ Retrieved price data from {len(price_data_list)} sources:")
                    for price_data in price_data_list:
                        print(f"  - {price_data.source.value}: ${price_data.price:,.2f}")
                else:
                    result["tests"]["get_price_data"] = {"status": "failed", "error": "No data"}
                    print("✗ No price data from any source")
            except Exception as e:
                result["tests"]["get_price_data"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            # Test 2: Get comprehensive crypto data
            print(f"\n[Test 2] Getting comprehensive data for {symbol}...")
            try:
                crypto_data = await aggregator.get_crypto_data(symbol)
                if crypto_data:
                    result["tests"]["get_crypto_data"] = {
                        "status": "success",
                        "data": {
                            "symbol": crypto_data.symbol,
                            "price": crypto_data.price,
                            "volume_24h": crypto_data.volume_24h,
                            "market_cap": crypto_data.market_cap
                        }
                    }
                    print(f"✓ Comprehensive data retrieved")
                    print(f"  Symbol: {crypto_data.symbol}")
                    print(f"  Price: ${crypto_data.price:,.2f}")
                    if crypto_data.volume_24h:
                        print(f"  24h Volume: ${crypto_data.volume_24h:,.0f}")
                    if crypto_data.market_cap:
                        print(f"  Market Cap: ${crypto_data.market_cap:,.0f}")
                else:
                    result["tests"]["get_crypto_data"] = {"status": "failed", "error": "No data"}
                    print("✗ No comprehensive data")
            except Exception as e:
                result["tests"]["get_crypto_data"] = {"status": "error", "error": str(e)}
                print(f"✗ Error: {e}")

            # Cleanup
            for source in aggregator.sources.values():
                await source.close()

            result["status"] = "success"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"\n✗ DataAggregator test failed: {e}")

        return result

    def print_summary(self, results: List[dict]):
        """Print test summary"""
        print(f"\n{'=' * 60}")
        print("TEST SUMMARY")
        print(f"{'=' * 60}")

        total = len(results)
        success = sum(1 for r in results if r.get("status") == "success")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        failed = sum(1 for r in results if r.get("status") in ["error", "failed"])

        print(f"\nTotal Sources Tested: {total}")
        print(f"✓ Successful: {success}")
        print(f"⚠ Skipped: {skipped}")
        print(f"✗ Failed: {failed}")

        print(f"\n{'=' * 60}")
        print("DETAILED RESULTS")
        print(f"{'=' * 60}")

        for result in results:
            source_name = result.get("source", "Unknown")
            status = result.get("status", "unknown")

            status_symbol = {
                "success": "✓",
                "skipped": "⚠",
                "error": "✗",
                "failed": "✗"
            }.get(status, "?")

            print(f"\n{status_symbol} {source_name}: {status.upper()}")

            if result.get("reason"):
                print(f"   Reason: {result['reason']}")

            if result.get("error"):
                print(f"   Error: {result['error']}")

            if result.get("tests"):
                for test_name, test_result in result["tests"].items():
                    test_status = test_result.get("status", "unknown")
                    test_symbol = "✓" if test_status == "success" else "✗"
                    print(f"   {test_symbol} {test_name}: {test_status}")


async def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="Test data sources with real API calls")
    parser.add_argument("--source", choices=["defillama", "tradingview", "glassnode", "bloomberg", "aggregator", "all"],
                        default="all", help="Data source to test")
    parser.add_argument("--symbol", default="BTC", help="Cryptocurrency symbol to test")

    args = parser.parse_args()

    print("=" * 60)
    print("AlphaChain - Data Source Testing")
    print("=" * 60)
    print(f"Testing with symbol: {args.symbol}")
    print(f"Source: {args.source}")

    tester = DataSourceTester()
    results = []

    if args.source == "all" or args.source == "defillama":
        result = await tester.test_defillama(args.symbol)
        results.append(result)

    if args.source == "all" or args.source == "tradingview":
        result = await tester.test_tradingview(args.symbol)
        results.append(result)

    if args.source == "all" or args.source == "glassnode":
        result = await tester.test_glassnode(args.symbol)
        results.append(result)

    if args.source == "all" or args.source == "bloomberg":
        result = await tester.test_bloomberg(args.symbol)
        results.append(result)

    if args.source == "all" or args.source == "aggregator":
        result = await tester.test_data_aggregator(args.symbol)
        results.append(result)

    tester.print_summary(results)

    print(f"\n{'=' * 60}")
    print("Testing completed!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
