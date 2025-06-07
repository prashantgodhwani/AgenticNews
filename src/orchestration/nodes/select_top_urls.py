import os
import logging
import re
from models.state import GraphState
from services.llm import llm

def select_top_urls(state: GraphState) -> GraphState:
    logging.info("Selecting top URLs based on relevance.")
    news_query = state["news_query"]
    num_articles_tldr = state["num_articles_tldr"]
    
    # load all processed articles with full text but no summaries
    potential_articles = state["potential_articles_filtered"]

    # format the metadata
    formatted_metadata = "\n".join([f"{article['url']}\n{article['content']}\n" for article in potential_articles])

    prompt = f"""
    Based on the user news query:
    {news_query}

    Reply with a list of strings of exactly {num_articles_tldr} relevant urls.
    
    The goal is to retrieve **high-signal, technical or research-driven news articles** that highlight:
    - Architectural innovations (e.g., retrieval-augmented generation, MAP, ReAct)
    - New open-source releases or developer tools in the AI ecosystem
    - Experimental systems or real-world deployments of AI agents
    - Technical shifts in how AI is engineered, trained, deployed, or integrated
    - Large language models (LLMs) 
    - AI agents and agentic workflows 
    - AI development frameworks, toolkits, coding libraries, or systems infrastructure
    - Foundational model innovations and scaling techniques
    - Multi-agent collaboration and autonomous systems


    Don't add any urls that are not relevant or aren't listed specifically.  Do not include articles that talk about similar things.

    {formatted_metadata}
    """
    result = llm.invoke(prompt).content

    print(f"Result: {result}")

    # use regex to extract the urls as a list
    url_pattern = r'(https?://[^\s",]+)'

    # Find all URLs in the text
    urls = re.findall(url_pattern, result)

    # add the selected article metadata to the state
    tldr_articles = [article for article in potential_articles if article['url'] in urls]

    # tldr_articles = [article for article in potential_articles if article['url'] in urls]
    state["tldr_articles"] = tldr_articles

    logging.debug(f"Selected URLs: {urls}")
    logging.info("Top URL selection completed.")
    return state