from config import load_env
import asyncio
from utils import logging
from orchestration import workflow
from orchestration.nodes import (
    retrieve_articles_metadata,
    filter_articles_with_llm,
    generate_tavily_params,
    select_top_urls,
    retrieve_articles_text,
    summarize_articles
    )

async def run_workflow(query: str, num_searches_remaining: int = 5, num_articles_tldr: int = 5):
    """Run the LangGraph workflow and display results."""
    initial_state = {
        "news_query": query,
        "num_searches_remaining": num_searches_remaining,
        "newsapi_params": {},
        "past_searches": [],
        "articles_metadata": [],
        "scraped_urls": [],
        "num_articles_tldr": num_articles_tldr,
        "potential_articles": [],
        "potential_articles_filtered": [],
        "tldr_articles": [],
        "formatted_results": "No articles with text found."
    }
    try:
        app = workflow.build_workflow(generate_tavily_params.generate_tavily_params, 
                                      retrieve_articles_metadata.retrieve_articles_metadata, 
                                      filter_articles_with_llm.filter_articles_with_llm, 
                                      select_top_urls.select_top_urls,
                                      retrieve_articles_text.retrieve_articles_text,
                                      summarize_articles.summarize_articles_parallel).compile()
        result = await app.ainvoke(initial_state, {"recursion_limit": 50})
        
        return result["formatted_results"]
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def main():
    load_env()
    logging.setup_logging()
    query = "Latest Tech news in LLMs, AI Agents, AI tools, AI frameworks, Foundational Models"
    results = asyncio.run(run_workflow(query))
    
    # Save the results to a file
    output_file = "ai_news_results.txt"
    with open(output_file, "w") as file:
        file.write(results)
    
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()