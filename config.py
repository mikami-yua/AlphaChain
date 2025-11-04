"""
Configuration management for Crypto AI Agent
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    
    # Bloomberg API Configuration
    bloomberg_api_key: Optional[str] = Field(None, env="BLOOMBERG_API_KEY")
    bloomberg_base_url: str = Field("https://api.bloomberg.com", env="BLOOMBERG_BASE_URL")
    
    # TradingView Configuration
    tradingview_username: Optional[str] = Field(None, env="TRADINGVIEW_USERNAME")
    tradingview_password: Optional[str] = Field(None, env="TRADINGVIEW_PASSWORD")
    
    # Glassnode API Configuration
    glassnode_api_key: Optional[str] = Field(None, env="GLASSNODE_API_KEY")
    glassnode_base_url: str = Field("https://api.glassnode.com", env="GLASSNODE_BASE_URL")
    
    # DefiLlama Configuration
    defillama_base_url: str = Field("https://api.llama.fi", env="DEFILLAMA_BASE_URL")
    
    # Database Configuration
    database_url: str = Field("sqlite:///./crypto_agent.db", env="DATABASE_URL")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/crypto_agent.log", env="LOG_FILE")
    
    # Trading Configuration
    trading_enabled: bool = Field(False, env="TRADING_ENABLED")
    risk_limit: float = Field(1000.0, env="RISK_LIMIT")
    max_position_size: float = Field(0.1, env="MAX_POSITION_SIZE")

    # Email Notification Configuration (163 Email)
    email_enabled: bool = Field(False, env="EMAIL_ENABLED")
    email_sender: Optional[str] = Field(None, env="EMAIL_SENDER")
    email_password: Optional[str] = Field(None, env="EMAIL_PASSWORD")
    email_sender_name: Optional[str] = Field(None, env="EMAIL_SENDER_NAME")
    email_use_ssl: bool = Field(True, env="EMAIL_USE_SSL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
