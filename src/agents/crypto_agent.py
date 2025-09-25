"""
Main Crypto AI Agent using LangChain
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage

from ..data_sources import DataAggregator
from ..models.crypto_data import CryptoData
from ..models.trading_signal import TradingSignal, SignalType, SignalStrength
from loguru import logger


class CryptoAgent:
    """Main AI Agent for crypto analysis and trading decisions"""
    
    def __init__(self, config, data_aggregator: DataAggregator):
        self.config = config
        self.data_aggregator = data_aggregator
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=config.openai_api_key
        )
        self.memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the AI agent"""
        tools = [
            Tool(
                name="get_crypto_data",
                description="Get comprehensive crypto data including price, technical indicators, and market sentiment",
                func=self._get_crypto_data_tool
            ),
            Tool(
                name="get_price_data",
                description="Get current price data for a cryptocurrency",
                func=self._get_price_data_tool
            ),
            Tool(
                name="get_historical_data",
                description="Get historical price data for analysis",
                func=self._get_historical_data_tool
            ),
            Tool(
                name="search_crypto",
                description="Search for cryptocurrencies by name or symbol",
                func=self._search_crypto_tool
            ),
            Tool(
                name="analyze_technical_indicators",
                description="Analyze technical indicators and generate trading signals",
                func=self._analyze_technical_indicators_tool
            ),
            Tool(
                name="assess_market_sentiment",
                description="Assess overall market sentiment and risk factors",
                func=self._assess_market_sentiment_tool
            )
        ]
        return tools
    
    def _create_agent(self):
        """Create the AI agent with prompt template"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert cryptocurrency trading AI agent with access to real-time market data from multiple sources including Bloomberg, TradingView, Glassnode, and DefiLlama.

Your primary responsibilities:
1. Analyze cryptocurrency market data and technical indicators
2. Generate trading signals based on comprehensive analysis
3. Assess market sentiment and risk factors
4. Provide investment recommendations with clear reasoning

Key analysis areas:
- Technical analysis using RSI, MACD, moving averages, Bollinger Bands
- On-chain metrics from Glassnode (NVT, MVRV, SOPR, active addresses)
- DeFi metrics from DefiLlama (TVL, volume, fees)
- Market sentiment and volatility analysis
- Risk assessment and position sizing recommendations

Always provide:
- Clear reasoning for your analysis
- Risk factors and potential downsides
- Confidence levels for your recommendations
- Specific entry/exit points when appropriate

Use the available tools to gather comprehensive data before making any recommendations."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return create_openai_tools_agent(self.llm, self.tools, prompt)
    
    async def analyze_crypto(self, symbol: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze a cryptocurrency and provide recommendations"""
        try:
            # Get comprehensive data
            crypto_data = await self.data_aggregator.get_crypto_data(symbol)
            if not crypto_data:
                return {"error": f"No data available for {symbol}"}
            
            # Generate analysis based on type
            if analysis_type == "comprehensive":
                return await self._comprehensive_analysis(crypto_data)
            elif analysis_type == "technical":
                return await self._technical_analysis(crypto_data)
            elif analysis_type == "fundamental":
                return await self._fundamental_analysis(crypto_data)
            else:
                return {"error": f"Unknown analysis type: {analysis_type}"}
                
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {"error": str(e)}
    
    async def generate_trading_signal(self, symbol: str) -> Optional[TradingSignal]:
        """Generate trading signal for a cryptocurrency"""
        try:
            crypto_data = await self.data_aggregator.get_crypto_data(symbol)
            if not crypto_data:
                return None
            
            # Use the agent to analyze and generate signal
            analysis_prompt = f"""
            Analyze {symbol} and generate a trading signal based on:
            1. Current price: {crypto_data.get_latest_price()}
            2. Technical indicators: {[ind.name for ind in crypto_data.market_data[-1].technical_indicators]}
            3. Market sentiment: {crypto_data.news_sentiment}
            4. Price change 24h: {crypto_data.get_price_change_24h()}
            
            Provide a clear BUY, SELL, or HOLD recommendation with confidence level and reasoning.
            """
            
            response = await self.agent_executor.ainvoke({"input": analysis_prompt})
            
            # Parse the response to create trading signal
            return self._parse_trading_signal(symbol, response["output"], crypto_data)
            
        except Exception as e:
            logger.error(f"Error generating trading signal for {symbol}: {e}")
            return None
    
    async def get_market_overview(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market overview for multiple cryptocurrencies"""
        try:
            overview = {
                "timestamp": datetime.utcnow(),
                "symbols": {},
                "market_summary": {}
            }
            
            # Analyze each symbol
            for symbol in symbols:
                crypto_data = await self.data_aggregator.get_crypto_data(symbol)
                if crypto_data:
                    overview["symbols"][symbol] = {
                        "price": crypto_data.get_latest_price(),
                        "change_24h": crypto_data.get_price_change_24h(),
                        "sentiment": crypto_data.news_sentiment,
                        "technical_signals": {
                            ind.name: ind.signal 
                            for ind in crypto_data.market_data[-1].technical_indicators
                        }
                    }
            
            # Generate market summary using AI
            summary_prompt = f"""
            Provide a market overview based on the following data:
            {overview['symbols']}
            
            Include:
            1. Overall market sentiment
            2. Key trends and patterns
            3. Risk factors to watch
            4. Top opportunities
            """
            
            response = await self.agent_executor.ainvoke({"input": summary_prompt})
            overview["market_summary"] = response["output"]
            
            return overview
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {"error": str(e)}
    
    # Tool functions for the agent
    def _get_crypto_data_tool(self, symbol: str) -> str:
        """Tool for getting crypto data"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            crypto_data = loop.run_until_complete(self.data_aggregator.get_crypto_data(symbol))
            loop.close()
            
            if crypto_data:
                return f"Data for {symbol}: Price={crypto_data.get_latest_price()}, Change24h={crypto_data.get_price_change_24h()}, Sentiment={crypto_data.news_sentiment}"
            else:
                return f"No data available for {symbol}"
        except Exception as e:
            return f"Error getting data for {symbol}: {str(e)}"
    
    def _get_price_data_tool(self, symbol: str) -> str:
        """Tool for getting price data"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            price_data = loop.run_until_complete(self.data_aggregator.get_price_data(symbol))
            loop.close()
            
            if price_data:
                return f"Price data for {symbol}: {[f'{p.price}@{p.timestamp}' for p in price_data]}"
            else:
                return f"No price data available for {symbol}"
        except Exception as e:
            return f"Error getting price data for {symbol}: {str(e)}"
    
    def _get_historical_data_tool(self, symbol: str) -> str:
        """Tool for getting historical data"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            historical_data = loop.run_until_complete(
                self.data_aggregator.get_historical_data(symbol, start_date, end_date)
            )
            loop.close()
            
            if historical_data:
                return f"Historical data for {symbol}: {len(historical_data)} data points from {start_date} to {end_date}"
            else:
                return f"No historical data available for {symbol}"
        except Exception as e:
            return f"Error getting historical data for {symbol}: {str(e)}"
    
    def _search_crypto_tool(self, query: str) -> str:
        """Tool for searching cryptocurrencies"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self.data_aggregator.search_crypto(query))
            loop.close()
            
            if results:
                return f"Search results for '{query}': {results}"
            else:
                return f"No results found for '{query}'"
        except Exception as e:
            return f"Error searching for '{query}': {str(e)}"
    
    def _analyze_technical_indicators_tool(self, symbol: str) -> str:
        """Tool for analyzing technical indicators"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            crypto_data = loop.run_until_complete(self.data_aggregator.get_crypto_data(symbol))
            loop.close()
            
            if crypto_data and crypto_data.market_data:
                indicators = crypto_data.market_data[-1].technical_indicators
                analysis = {}
                for ind in indicators:
                    analysis[ind.name] = f"{ind.value} ({ind.signal})"
                return f"Technical indicators for {symbol}: {analysis}"
            else:
                return f"No technical indicators available for {symbol}"
        except Exception as e:
            return f"Error analyzing technical indicators for {symbol}: {str(e)}"
    
    def _assess_market_sentiment_tool(self, symbol: str) -> str:
        """Tool for assessing market sentiment"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            crypto_data = loop.run_until_complete(self.data_aggregator.get_crypto_data(symbol))
            loop.close()
            
            if crypto_data:
                return f"Market sentiment for {symbol}: {crypto_data.news_sentiment}"
            else:
                return f"No sentiment data available for {symbol}"
        except Exception as e:
            return f"Error assessing market sentiment for {symbol}: {str(e)}"
    
    # Analysis methods
    async def _comprehensive_analysis(self, crypto_data: CryptoData) -> Dict[str, Any]:
        """Perform comprehensive analysis"""
        analysis = {
            "symbol": crypto_data.symbol,
            "timestamp": datetime.utcnow(),
            "price_analysis": {
                "current_price": crypto_data.get_latest_price(),
                "change_24h": crypto_data.get_price_change_24h(),
                "price_trend": "bullish" if crypto_data.get_price_change_24h() and crypto_data.get_price_change_24h() > 0 else "bearish"
            },
            "technical_analysis": {},
            "fundamental_analysis": {},
            "sentiment_analysis": {
                "overall_sentiment": crypto_data.news_sentiment,
                "sources_analyzed": len(crypto_data.market_data)
            },
            "recommendation": "HOLD"  # Default
        }
        
        # Technical analysis
        if crypto_data.market_data:
            latest_market_data = crypto_data.market_data[-1]
            for indicator in latest_market_data.technical_indicators:
                analysis["technical_analysis"][indicator.name] = {
                    "value": indicator.value,
                    "signal": indicator.signal
                }
        
        # Fundamental analysis
        analysis["fundamental_analysis"] = crypto_data.fundamental_data
        
        return analysis
    
    async def _technical_analysis(self, crypto_data: CryptoData) -> Dict[str, Any]:
        """Perform technical analysis only"""
        return await self._comprehensive_analysis(crypto_data)
    
    async def _fundamental_analysis(self, crypto_data: CryptoData) -> Dict[str, Any]:
        """Perform fundamental analysis only"""
        return await self._comprehensive_analysis(crypto_data)
    
    def _parse_trading_signal(self, symbol: str, response: str, crypto_data: CryptoData) -> TradingSignal:
        """Parse AI response into trading signal"""
        # Simple parsing - in production, this would be more sophisticated
        response_lower = response.lower()
        
        if "buy" in response_lower and "strong" in response_lower:
            signal_type = SignalType.STRONG_BUY
            strength = SignalStrength.VERY_STRONG
        elif "buy" in response_lower:
            signal_type = SignalType.BUY
            strength = SignalStrength.STRONG
        elif "sell" in response_lower and "strong" in response_lower:
            signal_type = SignalType.STRONG_SELL
            strength = SignalStrength.VERY_STRONG
        elif "sell" in response_lower:
            signal_type = SignalType.SELL
            strength = SignalStrength.STRONG
        else:
            signal_type = SignalType.HOLD
            strength = SignalStrength.MODERATE
        
        # Extract confidence from response (simplified)
        confidence = 0.8 if "high" in response_lower else 0.6 if "medium" in response_lower else 0.4
        
        return TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            reasoning=response,
            technical_indicators={ind.name: ind.signal for ind in crypto_data.market_data[-1].technical_indicators},
            fundamental_factors=crypto_data.fundamental_data,
            timestamp=datetime.utcnow(),
            source="AI_Agent"
        )
