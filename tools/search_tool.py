import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def search_web(query: str, max_results: int = 5):

    if not TAVILY_API_KEY:
        raise ValueError(
            "TAVILY_API_KEY is missing from the .env file."
        )

    client = TavilyClient(
        api_key=TAVILY_API_KEY
    )

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
        include_raw_content=False
    )

    results = []

    for item in response.get("results", []):

        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": item.get("score", 0)
            }
        )

    return results