"""
RitaDrishti-AI — Playwright Dynamic Complaint Scraper
Handles JavaScript-rendered dynamic complaint portals and consumer forums.
"""

import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright


class PlaywrightComplaintScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def scrape_complaints(self, target_company: str, target_url: str = None) -> List[Dict[str, Any]]:
        """Scrapes complaints from dynamic JS-heavy consumer portals."""
        if not target_url:
            target_url = f"https://www.consumeraffairs.com/search.html?q={target_company}"

        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            try:
                await page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)

                # Extract complaint cards
                cards = await page.query_selector_all(".rvw, .complaint-card, .search-result")

                for card in cards[:10]:
                    title_elem = await card.query_selector("h3, .rvw-title, .title")
                    desc_elem = await card.query_selector("p, .rvw-bd, .description")
                    status_elem = await card.query_selector(".status, .badge")

                    title = await title_elem.inner_text() if title_elem else "Consumer Complaint"
                    description = await desc_elem.inner_text() if desc_elem else ""
                    status = await status_elem.inner_text() if status_elem else "unresolved"

                    if description:
                        results.append({
                            "company_name": target_company,
                            "source": "ConsumerAffairs / Playwright",
                            "title": title.strip(),
                            "description": description.strip(),
                            "resolution_status": "resolved" if "resolved" in status.lower() else "unresolved",
                            "severity_level": "high" if any(w in description.lower() for w in ["scam", "stolen", "fraud", "court"]) else "medium"
                        })

            except Exception as e:
                print(f"[Playwright Scraper Error]: {e}")
            finally:
                await browser.close()

        return results


if __name__ == "__main__":
    scraper = PlaywrightComplaintScraper(headless=True)
    scraped = asyncio.run(scraper.scrape_complaints("Acme Cloud"))
    print(f"Scraped {len(scraped)} complaint records.")
