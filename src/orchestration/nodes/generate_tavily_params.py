from typing import Dict
import logging
from models.state import GraphState
from models.tavily import TavilyApiParams
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from services.llm import llm

def generate_tavily_params(state: GraphState) -> GraphState:
    logging.info("Starting to generate Tavily API parameters.")
    from random import sample, shuffle

    # initialize parser to define the structure of the response
    parser = JsonOutputParser(pydantic_object=TavilyApiParams)

    # retrieve today's date
    today_date = datetime.now().strftime("%Y-%m-%d")

    # retrieve list of past search params
    past_searches = state["past_searches"]

    # retrieve number of searches remaining
    num_searches_remaining = state["num_searches_remaining"]

    # retrieve the user's query
    news_query = state["news_query"]

    template = """
        Today is {today_date}.

        You are an AI news curator specializing in cutting-edge developments for software engineers. Create optimized Tavily API parameters based on this query:
        {news_query}

        **SEARCH STRATEGY - Generate Smarter Keywords:**
        Analyze the user query and create targeted search terms using technical synonyms, brand names + generic terms, and emerging AI terminology. Focus on terms that capture recent developments software engineers need to know.

        **Focus on**:
        - **LLM & Model Innovations**: New architectures, training techniques, fine-tuning methods, prompt engineering, RLHF, constitutional AI
        - **AI Engineering Frameworks**: LangChain, LlamaIndex, Haystack, AutoGen, CrewAI, Semantic Kernel, LiteLLM updates and new releases
        - **Developer Tools & Platforms**: Cursor AI, GitHub Copilot, Replit Agent, Claude Dev, OpenAI DevDay, Anthropic releases, coding assistants
        - **Integration Protocols**: Model Context Protocol (MCP), Agent-to-Agent (A2A), OpenAI plugins, function calling, tool use improvements
        - **Architectural innovations in AI**: retrieval-augmented generation (RAG), ReAct patterns, Multi-Agent Patterns (MAP), Tree of Thoughts, Chain of Thought evolution
        - **Open-source releases**: Hugging Face model releases, new transformers, diffusion models, speech/vision models, developer tools in the AI ecosystem
        - **Infrastructure & Deployment**: AI model serving, optimization, quantization, deployment frameworks, model hosting
        - **Experimental systems or real-world deployments of AI agents**: autonomous coding, automated testing, AI-powered development workflows
        - **Technical shifts in AI engineering, training, deployment, or integration**: MLOps, AI engineering best practices
        - **Foundational model innovations and scaling techniques**: distributed training, model compression, efficiency improvements
        - **Multi-agent collaboration and autonomous systems**: agent frameworks, orchestration, team-based AI systems

        **SEARCH OPTIMIZATION TECHNIQUES:**
        - **CRITICAL: Keep queries under 400 characters total**
        - Use 3-5 key technical terms max per query
        - Prioritize most specific/unique terms over generic ones
        - Use abbreviations when possible (LLM vs "large language model")
        - Focus on brand names OR generic terms, not both in same query
        - Skip connecting words like "and", "or", "the" when possible

        **Avoid**:
        - Pure business or finance news unless it explicitly impacts development or adoption of AI tools and platforms
        - Articles focused on ethics, policy, regulation, or general public reactions
        - Generic AI hype without technical substance
        - Social media reactions or opinion pieces

        **PAST SEARCH ANALYSIS:**
        These searches have already been made - avoid duplication and broaden approach:
        {past_searches}

        **ADAPTIVE SEARCH STRATEGY:**
        - Remaining searches: {num_searches_remaining}
        - If > 3 searches left: Use focused, specific queries (50-150 chars) with basic search depth
        - If ≤ 3 searches left: Broader terms (150-250 chars), consider advanced search depth  
        - If this is your last search: Use comprehensive search with 30-day time range, advanced depth, and up to 400 characters with multiple key terms

        **QUERY CONSTRUCTION EXAMPLES (Under 400 chars):**
        Instead of: "new AI tools" → Use: "AI development tools 2024 LangChain AutoGen updates" (50 chars)
        Instead of: "LLM news" → Use: "LLM fine-tuning RLHF constitutional AI 2024" (43 chars)  
        Instead of: "AI frameworks" → Use: "AI agent frameworks ReAct RAG deployment" (41 chars)
        Instead of: "coding assistants" → Use: "Cursor AI GitHub Copilot coding assistant updates" (49 chars)

        **CHARACTER COUNT STRATEGY:**
        - Target 50-200 characters for focused searches
        - Use 300-400 characters only for final comprehensive search
        - Prioritize technical terms that yield specific results

        {format_instructions}

        Generate search terms that AI engineers actively use when staying current with cutting-edge developments. **REMEMBER: Query must be under 400 characters.**
    """

    # create a prompt template to merge the query, today's date, and the format instructions
    prompt_template = PromptTemplate(
        template=template,
        input_variables=["today_date", "news_query", "past_searches", "num_searches_remaining"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # create prompt chain template
    chain = prompt_template | llm | parser

    # invoke the chain with the news api query
    result = chain.invoke({
    "today_date": today_date,
    "news_query": news_query,
    "past_searches": past_searches,
    "num_searches_remaining": num_searches_remaining
   })

    # update the state
    state["tavily_params"] = result
    logging.debug(f"Search Parameters Generated: {result}")
    logging.debug(f"Number of searches remaining: {num_searches_remaining}")
    logging.info("Tavily API parameters generated successfully.")
    return state