from typing import Dict
import os
import logging
from models.state import GraphState 
import requests
from bs4 import BeautifulSoup

def retrieve_articles_text(state: GraphState) -> GraphState:
    logging.info("Starting to retrieve article text via web scraping.")
    articles_metadata = state["tldr_articles"]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    potential_articles = []
    for article in articles_metadata:
        url = article['url']
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(strip=True)
            potential_articles.append({
                "title": article["title"],
                "url": url,
                "description": article["content"],
                "text": text,
                "publishedAt": article.get("published_date", "")
            })
            state["scraped_urls"].append(url)
        else:
            logging.warning(f"Failed to retrieve content for URL: {url}, Status Code: {response.status_code}")
    state["potential_articles"].extend(potential_articles)
    logging.info("Article text retrieval completed.")
    return state