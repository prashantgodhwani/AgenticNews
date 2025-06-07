import logging
import json
from typing import List, Dict
from models.state import GraphState
from models.rated_content import RatedContent
from services.llm import llm
from langchain_core.output_parsers import JsonOutputParser


def filter_articles_with_llm(state: GraphState) -> GraphState:
    logging.info("Filtering articles using LLM with scoring.")
    potential_articles = state["articles_metadata"]
    num_articles_tldr = state["num_articles_tldr"]
    num_searches_remaining = state["num_searches_remaining"]

    # Format the metadata for the LLM
    formatted_metadata = "\n".join([
        f"Title: {article['title']}\nDescription: {article['content']}\nPublishedAt: {article.get('published_date', '')}\nURL: {article['url']}\n"
        for article in potential_articles
    ])

    parser = JsonOutputParser(pydantic_object=RatedContent)

    # LLM prompt to rate articles
    prompt = f"""
    You are tasked with evaluating the relevance of articles based on the following criteria:
    - Articles should focus on high-signal, technical, or research-driven topics.
    - Avoid generic or widely known topics that do not provide new insights.
    - Prioritize articles about:
        - Architectural innovations 
        - New open-source releases or developer tools in the AI ecosystem
        - Experimental systems or real-world deployments of AI agents
        - Technical shifts in AI engineering, training, deployment, or integration
        - Foundational model innovations and scaling techniques
        - Multi-agent collaboration and autonomous systems

    Here are the articles to evaluate:
    {formatted_metadata}

    Remaining search attempts: {num_searches_remaining}

    For each article, provide a relevance score between 0 and 10 (10 being the most relevant). 
    
    
    Format Instructions:
    {parser.get_format_instructions()}
    """

    # Invoke the LLM to rate articles
    result = parser.parse(llm.invoke(prompt).content)

    # Validate and parse the LLM response
    try:
        # Sort articles by score in descending order
        scored_articles = sorted(
            result, key=lambda x: x["score"], reverse=True
        )

        # Select the top N articles based on the number of TL;DRs required
        top_urls = [entry["url"] for entry in scored_articles[:num_articles_tldr]]

        # Filter the articles based on the selected top URLs 
        filtered_articles = [
            article for article in potential_articles if article["url"] in top_urls
        ]

        # Update the state with the filtered articles
        state["potential_articles_filtered"] += filtered_articles

        logging.debug(f"Top URLs selected: {top_urls}")
        logging.info("Article filtering with scoring completed.")
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing LLM response as JSON: {e}")
        # Fallback: Retain all articles if scoring fails
        state["potential_articles_filtered"] += potential_articles
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        # Fallback: Retain all articles if any other error occurs
        state["potential_articles_filtered"] += potential_articles

    return state