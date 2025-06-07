import os
import logging
from tavily import TavilyClient
from models.state import GraphState

def retrieve_articles_metadata(state: GraphState) -> GraphState:
    logging.info("Retrieving articles metadata from Tavily API.")
    tavily_params = state["tavily_params"]
    state['num_searches_remaining'] -= 1

    try:
        tavily = TavilyClient(api_key=os.getenv('TAVILY_KEY'))
        articles = tavily.search(**tavily_params)
        state['past_searches'].append(tavily_params)
        scraped_urls = state["scraped_urls"]
        new_articles = []
        for article in articles['results']:
            if article['url'] not in scraped_urls and len(state['potential_articles']) + len(new_articles) < 10:
                new_articles.append(article)
        state["articles_metadata"] = new_articles
        logging.debug(f"Retrieved articles: {articles}")
        logging.debug(f"Filtered new articles: {new_articles}")
    except Exception as e:
        logging.error(f"Error while retrieving articles metadata: {e}")
    logging.info("Articles metadata retrieval completed.")
    return state