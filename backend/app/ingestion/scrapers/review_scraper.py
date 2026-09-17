"""
SentinelX Trust AI — Scrapy Review Spider
Fetches unstructured reviews, ratings, author names, and metadata from public web sources.
"""

import re
import json
from typing import Dict, List, Any
import scrapy


class PublicReviewSpider(scrapy.Spider):
    name = "public_reviews_spider"
    allowed_domains = ["trustpilot.com", "g2.com", "google.com"]

    def __init__(self, target_company: str = "", start_urls_list: List[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_company = target_company
        if start_urls_list:
            self.start_urls = start_urls_list
        else:
            self.start_urls = [
                f"https://www.trustpilot.com/review/{target_company}.com"
            ]

    def parse(self, response):
        """Parse review cards from public rating pages."""
        reviews = response.css("article.review-card, div.styles_cardWrapper__L2L_H")
        
        for review in reviews:
            raw_text = "".join(review.css("p.review-content__text, div.styles_text__ki4_V ::text").getall()).strip()
            rating_str = review.css("div.star-rating img::attr(alt), div.styles_reviewHeader__iU9Px::attr(data-service-review-rating)").get()
            reviewer_name = review.css("span.consumer-information__name, span.styles_consumerName__ZXAW6::text").get()
            review_date = review.css("time::attr(datetime)").get()

            rating = self._parse_rating(rating_str)

            if raw_text:
                yield {
                    "company_name": self.target_company,
                    "source": "Trustpilot",
                    "raw_text": raw_text,
                    "rating": rating,
                    "reviewer_name": reviewer_name.strip() if reviewer_name else "Anonymous",
                    "review_date": review_date,
                    "metadata": {
                        "url": response.url,
                        "scraped_via": "Scrapy PublicReviewSpider"
                    }
                }

    def _parse_rating(self, rating_str: str) -> float:
        """Helper to convert rating string to float."""
        if not rating_str:
            return 3.0
        match = re.search(r"(\d+(\.\d+)?)", rating_str)
        return float(match.group(1)) if match else 3.0
