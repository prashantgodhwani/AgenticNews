import os
from dotenv import load_dotenv
from getpass import getpass

def load_env():
    if os.path.exists(".env"):
        load_dotenv()
    else:
        os.environ["NEWSAPI_KEY"] = getpass("Enter your News API key: ")
        os.environ["GOOGLE_API_KEY"] = getpass("Enter your Google API key: ")
        os.environ["LANGSMITH_API_KEY"] = getpass("Enter your LangSmith API key: ")
        os.environ["TAVILY_KEY"] = getpass("Enter your Tavily API key: ")