"""
RitaDrishti-AI — News & Public Media Scraper
Fetches news articles, press releases, and public OSINT media feeds.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any


class NewsContentScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    def fetch_company_news(self, company_name: str) -> List[Dict[str, Any]]:
        """Fetches public news headlines and summaries via RSS/Search feeds."""
        query = company_name.replace(" ", "+")
        rss_url = f"https://news.google.com/rss/search?q={query}+trust+OR+lawsuit+OR+fraud&hl=en-US&gl=US&ceid=US:en"

        articles = []
        try:
            res = requests.get(rss_url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "xml")
                items = soup.find_all("item")

                for item in items[:8]:
                    headline = item.title.text if item.title else ""
                    link = item.link.text if item.link else ""
                    pub_date = item.pubDate.text if item.pubDate else ""
                    description = BeautifulSoup(item.description.text, "html.parser").text if item.description else ""

                    articles.append({
                        "company_name": company_name,
                        "headline": headline,
                        "source_url": link,
                        "publisher": "Google News RSS",
                        "summary": description[:300],
                        "publish_date": pub_date
                    })
        except Exception as e:
            print(f"[News Scraper Error]: {e}")

        return articles
