import os
import requests
import logging
from typing import List, Dict, Any, Optional

class WebSearcher:
    """
    Searches the web using SerpAPI and returns structured, citable results.
    """

    def __init__(self, serpapi_api_key: Optional[str] = None, engine: str = "google"):
        """
        :param serpapi_api_key: API key for SerpAPI (or use SERPAPI_API_KEY environment variable)
        :param engine: Search engine type (default: 'google')
        """
        self.serpapi_api_key = serpapi_api_key or os.getenv("SERPAPI_API_KEY")
        if not self.serpapi_api_key:
            raise ValueError("You must provide a SerpAPI API key via argument or SERPAPI_API_KEY env variable.")
        self.engine = engine
        self.logger = logging.getLogger("WebSearcher")

    def search(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """
        Searches the web via SerpAPI.
        :param query: Query string to search.
        :param num_results: Number of top results to return.
        :return: List of result dicts, each with title, snippet, url, and citation info.
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")
        if not (1 <= num_results <= 10):
            raise ValueError("num_results must be between 1 and 10.")

        params = {
            "engine": self.engine,
            "q": query,
            "api_key": self.serpapi_api_key,
            "num": num_results,
            "hl": "en",
            "gl": "us",
        }

        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            self.logger.error(f"Web search failed: {e}")
            raise RuntimeError(f"Web search failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during web search: {e}")
            raise RuntimeError(f"Unexpected error during web search: {e}")

        organic = data.get("organic_results", [])
        results: List[Dict[str, Any]] = []

        for i, item in enumerate(organic[:num_results]):
            snippet = item.get("snippet") or item.get("content") or ""
            result = {
                "type": "web",
                "rank": i + 1,
                "title": item.get("title", ""),
                "text": snippet,
                "url": item.get("link", ""),
                "citation": {
                    "url": item.get("link", ""),
                    "title": item.get("title", ""),
                    "rank": i + 1
                }
            }
            results.append(result)

        if not results:
            self.logger.warning(f"No results found for query: '{query}'")

        return list(results)  # Return a shallow copy

