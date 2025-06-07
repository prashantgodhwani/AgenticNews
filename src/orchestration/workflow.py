from langgraph.graph import Graph, END
import logging
from models.state import GraphState

def format_results(state: GraphState) -> GraphState:
    logging.info("Formatting results for display.")
    # load a list of past search queries
    q = [newsapi_params["query"] for newsapi_params in state["past_searches"]]
    formatted_results = f"Here are the top {len(state['tldr_articles'])} articles based on search terms:\n{', '.join(q)}\n\n"
    formatted_results += f"News API Parameters:\n{state['past_searches']}\n\n"

    # load the summarized articles
    tldr_articles = state["tldr_articles"]

    # format article tl;dr summaries
    tldr_articles = "\n\n".join([f"{article['summary']}" for article in tldr_articles])

    # concatenate summaries to the formatted results
    formatted_results += tldr_articles

    state["formatted_results"] = formatted_results

    logging.info("Results formatting completed.")
    return state

def articles_text_decision(state: GraphState) -> str:
    logging.info("Making decision based on retrieved articles.")
    logging.debug(f"Potential articles: {len(state['potential_articles_filtered'])}, Articles needed: {state['num_articles_tldr']}")
    
    # If no searches remain and no articles are found, end the workflow
    if state["num_searches_remaining"] <= 0 and len(state["potential_articles_filtered"]) == 0:
        state["formatted_results"] = "No articles with text found."
        state["formatted_results"] += f"News API Parameters:\n{state['past_searches']}\n\n"
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