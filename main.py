#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crypto AI Agent - Main Entry Point
A LangChain-based AI agent for cryptocurrency analysis and trading
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import settings
from src.data_sources import DataAggregator
from src.agents import CryptoAgent
from loguru import logger


async def main():
    """Main function to run the crypto AI agent"""
    logger.info("Starting Crypto AI Agent...")
    
    try:
        # Initialize data aggregator
        logger.info("Initializing data sources...")
        data_aggregator = DataAggregator(settings)
        
        # Initialize AI agent
        logger.info("Initializing AI agent...")
        crypto_agent = CryptoAgent(settings, data_aggregator)
        
        # Example usage
        await run_example_analysis(crypto_agent)
        
    except Exception as e:
        logger.error(f"Error running crypto agent: {e}")
    finally:
        # Cleanup
        if 'data_aggregator' in locals():
            await data_aggregator.close()
        logger.info("Crypto AI Agent stopped")


async def run_example_analysis(crypto_agent: CryptoAgent):
    """Run example analysis"""
    logger.info("Running example analysis...")
    
    # Example 1: Analyze Bitcoin
    logger.info("Analyzing Bitcoin (BTC)...")
    btc_analysis = await crypto_agent.analyze_crypto("BTC", "comprehensive")
    logger.info(f"BTC Analysis: {btc_analysis}")
    
    # Example 2: Generate trading signal for Ethereum
    logger.info("Generating trading signal for Ethereum (ETH)...")
    eth_signal = await crypto_agent.generate_trading_signal("ETH")
    if eth_signal:
        logger.info(f"ETH Signal: {eth_signal.signal_type} - {eth_signal.reasoning}")
    
    # Example 3: Get market overview
    logger.info("Getting market overview...")
    market_overview = await crypto_agent.get_market_overview(["BTC", "ETH", "ADA"])
    logger.info(f"Market Overview: {market_overview}")
    
    # Example 4: Interactive chat
    logger.info("Starting interactive chat...")
    await interactive_chat(crypto_agent)


async def interactive_chat(crypto_agent: CryptoAgent):
    """Interactive chat with the AI agent"""
    logger.info("Interactive chat mode. Type 'quit' to exit.")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                logger.info("Exiting interactive chat...")
                break
            
            if not user_input:
                continue
            
            # Use the agent to respond
            response = await crypto_agent.agent_executor.ainvoke({"input": user_input})
            print(f"\nAI Agent: {response['output']}")
            
        except KeyboardInterrupt:
            logger.info("Chat interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            print(f"Error: {e}")


if __name__ == "__main__":
    # Configure logging
    logger.add(
        settings.log_file,
        level=settings.log_level,
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    # Run the main function
    asyncio.run(main())
