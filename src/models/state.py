from typing import TypedDict, Annotated, List, Optional

class GraphState(TypedDict):
    news_query: Annotated[str, "Input query to extract news search parameters from."]
    num_searches_remaining: Annotated[int, "Number of articles to search for."]
    tavily_params: Annotated[dict, "Structured argument for the Tavily News API."]
    past_searches: Annotated[List[dict], "List of search params already used."]
    articles_metadata: Annotated[list[dict], "Article metadata response from the Tavily News API"]
    scraped_urls: Annotated[List[str], "List of urls already scraped."]
    num_articles_tldr: Annotated[int, "Number of articles to create TL;DR for."]
    potential_articles: Annotated[List[dict[str, str]], "Article with full text to consider summarizing."]
    potential_articles_filtered: Annotated[List[dict[str, str]], "Filtered articles based on LLM scoring."]
    tldr_articles: Annotated[List[dict[str, str]], "Selected article TL;DRs."]
    formatted_results: Annotated[List[str], "Formatted results to display."]