"""
Utility functions for the Business Intelligence Risk Assessment system.

This module contains helper functions and common utilities used across
the application for the 3-pass business intelligence system.
"""

import json
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate if a URL is properly formatted.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """Normalize URL by adding protocol if missing.
    
    Args:
        url: Raw URL input
        
    Returns:
        Normalized URL with proper protocol
    """
    if not url:
        return ""
    
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url


def save_analysis_results(results: Dict[str, Any], output_path: str) -> None:
    """Save business analysis results to a JSON file.
    
    Args:
        results: Dictionary containing analysis results
        output_path: Path to save the results file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        raise Exception(f"Failed to save results to {output_path}: {str(e)}")


def load_json_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in configuration file: {str(e)}")


def clean_business_text(text: str) -> str:
    """Clean and normalize business text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common unwanted patterns
    text = re.sub(r'^\s*\|.*?\|\s*$', '', text, flags=re.MULTILINE)  # Table separators
    text = re.sub(r'Cookie.*?Accept', '', text, flags=re.IGNORECASE)  # Cookie notices
    text = re.sub(r'JavaScript.*?enabled', '', text, flags=re.IGNORECASE)  # JS warnings
    
    return text


def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain name from URL.
    
    Args:
        url: Full URL
        
    Returns:
        Domain name or None if invalid
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain if domain else None
    except Exception:
        return None


def format_confidence_score(confidence: float) -> str:
    """Format confidence score for display.
    
    Args:
        confidence: Confidence score (0.0-1.0)
        
    Returns:
        Formatted confidence string
    """
    if confidence >= 0.9:
        return f"{confidence:.1%} (Very High)"
    elif confidence >= 0.7:
        return f"{confidence:.1%} (High)"  
    elif confidence >= 0.5:
        return f"{confidence:.1%} (Medium)"
    elif confidence >= 0.3:
        return f"{confidence:.1%} (Low)"
    else:
        return f"{confidence:.1%} (Very Low)"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix