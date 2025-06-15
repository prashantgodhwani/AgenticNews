import logging
import asyncio
from models.state import GraphState
from services.llm import llm_g15

async def summarize_articles_parallel(state: GraphState) -> GraphState:
    logging.info("Starting parallel summarization of articles.")
    tldr_articles = state["potential_articles"]

    prompt = """
    Create a * bulleted summarizing tldr for the article:
    {text}
      
    Be sure to follow the following format exaxtly with nothing else:
    * use bullet points for each sentence
    """

    async def summarize(article):
        text = article["text"]
        title = article["title"]
        url = article["url"]
        logging.debug(f"Summarizing article: {url}")
        # Run the blocking call in a thread
        result = await asyncio.to_thread(llm_g15.invoke, prompt.format(title=title, url=url, text=text))
        article["summary"] = result.content
        return article

    tasks = [summarize(article) for article in tldr_articles]
    tldr_articles = await asyncio.gather(*tasks)
    state["tldr_articles"] = tldr_articles

    logging.info("Article summarization completed.")
    return state