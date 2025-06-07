from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from getpass import getpass

if os.path.exists(".env"):
    load_dotenv()
else:
    # ask for API keys
    os.environ["NEWSAPI_KEY"] = getpass("Enter your News API key: ")
    os.environ["GOOGLE_API_KEY"] = getpass("Enter your Google API key: ")
    os.environ["LANGSMITH_API_KEY"] = getpass("Enter your LangSmith API key: ")
    os.environ["TAVILY_KEY"] = getpass("Enter your Tavily API key: ")


# sets the OpenAI model to use and initialize model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=1.2)
llm_g15 = ChatGoogleGenerativeAI(model="gemini-1.5-flash")