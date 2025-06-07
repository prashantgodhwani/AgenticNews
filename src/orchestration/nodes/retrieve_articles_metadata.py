import logging
from services.tavily_service import TavilyClient
import os
from models.state import GraphState

def retrieve_articles_metadata(state: GraphState) -> GraphState:
    logging.info("Retrieving articles metadata from Tavily API.")
    # parameters generated for the Tavily API
    tavily_params = state["tavily_params"]
    logging.debug(f"Tavily API Payload: {tavily_params}")

    # decrement the number of searches remaining
    state['num_searches_remaining'] -= 1

    try:
        # create a TavilyClient object
        tavily = TavilyClient(api_key=os.getenv('TAVILY_KEY'))

        # retreive the metadata of the new articles
        articles = tavily.search(**tavily_params)

        # append this search term to the past searches to avoid duplicates
        state['past_searches'].append(tavily_params)

        # load urls that have already been returned and scraped
        scraped_urls = state["scraped_urls"]

        # filter out articles that have already been scraped
        new_articles = []
        for article in articles['results']:
            if article['url'] not in scraped_urls and len(state['potential_articles']) + len(new_articles) < 10:
                new_articles.append(article)

        # reassign new articles to the state
        state["articles_metadata"] = new_articles

        logging.debug(f"Retrieved articles: {articles}")
        logging.debug(f"Filtered new articles: {new_articles}")

    # handle exceptions
    except Exception as e:
        logging.error(f"Error while retrieving articles metadata: {e}")
    logging.info("Articles metadata retrieval completed.")
    return state