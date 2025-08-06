"""
Application settings and configuration management.

This module handles application configuration, environment variables,
and settings for different deployment environments.
"""

import os
from typing import Optional


class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        # API Keys
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.azure_openai_key: Optional[str] = os.getenv("AZURE_OPENAI_KEY")
        self.azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_cv_key: Optional[str] = os.getenv("AZURE_CV_KEY")
        self.azure_cv_endpoint: Optional[str] = os.getenv("AZURE_CV_ENDPOINT")
        
        # Application Settings
        self.app_title: str = os.getenv("APP_TITLE", "Business Intelligence Risk Assessment")
        self.debug_mode: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        
        # Scraping Settings
        self.max_scrape_timeout: int = int(os.getenv("MAX_SCRAPE_TIMEOUT", "30"))
        self.max_images_per_site: int = int(os.getenv("MAX_IMAGES_PER_SITE", "10"))
        
        # Image Analysis Settings
        self.max_images_for_analysis: int = int(os.getenv("MAX_IMAGES_FOR_ANALYSIS", "5"))
        self.min_image_size: int = int(os.getenv("MIN_IMAGE_SIZE", "100"))  # pixels
        
        # Model Settings
        self.llm_model: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.3"))


# Global settings instance
settings = Settings()