import logging
import aiohttp
from bs4 import BeautifulSoup
from models.state import GraphState
import asyncio

async def fetch_article(session, article, headers):
    url = article['url']
    try:
        async with session.get(url, headers=headers, timeout=15) as response:
            if response.status == 200:
                content = await response.read()
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(strip=True)
                return {
                    "title": article["title"],
                    "url": url,
                    "description": article["content"],
                    "text": text,
                    "publishedAt": article.get("published_date", "")
                }, url
            else:
                logging.warning(f"Failed to retrieve content for URL: {url}, Status Code: {response.status}")
                return None, url
    except Exception as e:
        logging.warning(f"Exception fetching {url}: {e}")
        return None, url

async def retrieve_articles_text(state: GraphState) -> GraphState:
    logging.info("Starting to retrieve article text via web scraping.")
    articles_metadata = state["tldr_articles"]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    potential_articles = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_article(session, article, headers) for article in articles_metadata]
        results = await asyncio.gather(*tasks)

    for article_dict, url in results:
        if article_dict:
            potential_articles.append(article_dict)
            state["scraped_urls"].append(url)

    state["potential_articles"].extend(potential_articles)
    logging.info("Article text retrieval completed.")
    return state