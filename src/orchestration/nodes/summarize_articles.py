import logging
from models.state import GraphState
from services.llm import llm_g15

async def summarize_articles_parallel(state: GraphState) -> GraphState:
    logging.info("Starting parallel summarization of articles.")
    tldr_articles = state["potential_articles"]

    # prompt = """
    # Summarize the article text in a bulleted tl;dr. Each line should start with a hyphen -
    # {article_text}
    # """

    prompt = """
    Create a * bulleted summarizing tldr for the article:
    {text}
      
    Be sure to follow the following format exaxtly with nothing else:
    {title}
    {url}
    * tl;dr bulleted summary
    * use bullet points for each sentence
    """

    # iterate over the selected articles and collect summaries synchronously
    for i in range(len(tldr_articles)):
        article = tldr_articles[i]
        text = article["text"]
        title = article["title"]
        url = article["url"]
        logging.debug(f"Summarizing article {i+1}/{len(tldr_articles)}: {url}")
        # invoke the llm synchronously
        result = llm_g15.invoke(prompt.format(title=title, url=url, text=text))
        tldr_articles[i]["summary"] = result.content

    state["tldr_articles"] = tldr_articles

    logging.info("Article summarization completed.")
    return state