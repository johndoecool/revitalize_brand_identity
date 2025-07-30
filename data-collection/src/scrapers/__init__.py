"""
Web Scraping Module

This module provides common web scraping functionality that can be used
across different collectors and data sources.
"""

from .web_scraper import WebScraper
from .social_media_scraper import SocialMediaScraper
from .scraper_config import ScraperConfig

__all__ = ['WebScraper', 'SocialMediaScraper', 'ScraperConfig'] 