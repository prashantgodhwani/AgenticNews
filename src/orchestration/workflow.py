from langgraph.graph import Graph, END
import logging
from models.state import GraphState
from datetime import datetime

def format_results(state: GraphState) -> GraphState:
    import logging

    logging.info("Formatting results for display.")

    messages = []

    for article in state["tldr_articles"]:
        title = article.get("title", "Untitled")
        url = article.get("url", "")
        summary = article.get("summary", "").strip()

        # Construct message
        msg = f"{title}\n{datetime.now().strftime('%Y-%m-%d')}\n{url}\n"

        for line in summary.split("\n"):
            if line.strip():
                msg += f"{line.strip()}\n"

        # Truncate if needed (Telegram limit is 4096)
        if len(msg) > 4096:
            msg = msg[:4093] + "..."

        messages.append(msg)

    state["formatted_results"] = messages
    logging.info("Results formatting completed.")
    return state

def articles_text_decision(state: GraphState) -> str:
    logging.info("Making decision based on retrieved articles.")
    logging.debug(f"Potential articles: {len(state['potential_articles_filtered'])}, Articles needed: {state['num_articles_tldr']}")
    
    # If no searches remain and no articles are found, end the workflow
    if state["num_searches_remaining"] <= 0 and len(state["potential_articles_filtered"]) == 0:
        state["formatted_results"].append("No articles with text found.")
        state["formatted_results"].append(f"News API Parameters:\n{state['past_searches']}\n\n")
        return "END"
    
    # If enough articles are found, proceed to finalize top articles
    if len(state["potential_articles_filtered"]) >= state["num_articles_tldr"]:
        return "select_top_urls"
    
    # Otherwise, widen the search parameters (only if searches remain)
    if state["num_searches_remaining"] > 0:
        return "generate_tavily_params"
    
    # End if no searches remain
    return "END"

def build_workflow(generate_tavily_params, retrieve_articles_metadata, filter_articles_with_llm, select_top_urls, retrieve_articles_text, summarize_articles_parallel):
    
    workflow = Graph()
    workflow.set_entry_point("generate_tavily_params")
    workflow.add_node("generate_tavily_params", generate_tavily_params)
    workflow.add_node("retrieve_articles_metadata", retrieve_articles_metadata)
    workflow.add_node("filter_articles_with_llm", filter_articles_with_llm)
    workflow.add_node("select_top_urls", select_top_urls)
    workflow.add_node("retrieve_articles_text", retrieve_articles_text)
    workflow.add_node("summarize_articles_parallel", summarize_articles_parallel)
    workflow.add_node("format_results", format_results)


    workflow.add_edge("generate_tavily_params", "retrieve_articles_metadata")
    workflow.add_conditional_edges(
        "retrieve_articles_metadata",
        lambda state: "generate_tavily_params" if len(state["articles_metadata"]) == 0 and state["num_searches_remaining"] > 0 else "filter_articles_with_llm",
        {
            "generate_tavily_params": "generate_tavily_params",
            "filter_articles_with_llm": "filter_articles_with_llm"
        }
    )
    workflow.add_conditional_edges(
        "filter_articles_with_llm",
        articles_text_decision,
        {
            "generate_tavily_params": "generate_tavily_params",
            "select_top_urls": "select_top_urls",
            "END": END
        }
    )
    workflow.add_edge("select_top_urls", "retrieve_articles_text")
    workflow.add_edge("retrieve_articles_text", "summarize_articles_parallel")
    workflow.add_edge("summarize_articles_parallel", "format_results")
    workflow.add_edge("format_results", END)
    return workflow