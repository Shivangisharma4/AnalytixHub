"""
Base scraper class with common functionality for extracting features from todo list websites.
"""
import time
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup


@dataclass
class ServiceFeatures:
    """Data class to store extracted features"""
    name: str
    url: str
    free_tier: bool
    pricing: Optional[str]
    platforms: List[str]
    collaboration: bool
    reminders: bool
    due_dates: bool
    tags_labels: bool
    subtasks: bool
    attachments: bool
    offline_mode: bool
    calendar_view: bool
    integrations: bool
    api_available: bool
    additional_features: List[str]

    def to_dict(self):
        return asdict(self)


class BaseScraper(ABC):
    """Base class for all todo service scrapers"""

    def __init__(self, url: str, name: str):
        self.url = url
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    @abstractmethod
    def scrape(self) -> ServiceFeatures:
        """Main scraping method - must be implemented by subclasses"""
        pass

    def fetch_page(self, url: Optional[str] = None) -> BeautifulSoup:
        """Fetch and parse a webpage"""
        target_url = url or self.url
        try:
            response = self.session.get(target_url, timeout=15)
            response.raise_for_status()
            time.sleep(2)  # Be respectful to servers
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"Error fetching {target_url}: {e}")
            return BeautifulSoup("", 'lxml')

    def extract_platforms(self, soup: BeautifulSoup) -> List[str]:
        """Extract platform availability (web, iOS, Android, etc.)"""
        platforms = []
        page_text = soup.get_text().lower()

        platform_keywords = {
            'ios': ['ios', 'iphone', 'ipad', 'app store'],
            'android': ['android', 'google play', 'play store'],
            'web': ['web', 'browser', 'website'],
            'windows': ['windows', 'pc'],
            'mac': ['mac', 'macos', 'mac os'],
            'linux': ['linux']
        }

        for platform, keywords in platform_keywords.items():
            if any(keyword in page_text for keyword in keywords):
                platforms.append(platform)

        return platforms if platforms else ['web']

    def check_feature_mention(self, soup: BeautifulSoup, feature_keywords: List[str]) -> bool:
        """Check if a feature is mentioned on the page"""
        page_text = soup.get_text().lower()
        return any(keyword.lower() in page_text for keyword in feature_keywords)

    def extract_pricing(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract pricing information"""
        # Look for common pricing patterns
        page_text = soup.get_text()

        # Find dollar amounts per month
        import re
        prices = re.findall(r'\$(\d+(?:\.\d+)?)\s*(?:\/\s*month|per month|monthly)', page_text, re.IGNORECASE)

        if prices:
            return f"${min(float(p) for p in prices)}-${max(float(p) for p in prices)}/month"

        # Check for "free" mentions
        if 'free' in page_text.lower() or 'freemium' in page_text.lower():
            return "Free tier available"

        return None
