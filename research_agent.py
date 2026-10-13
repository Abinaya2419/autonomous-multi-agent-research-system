
import logging
from ddgs import DDGS

logger = logging.getLogger("research_system")


def search_web(topic: str, max_results: int = 5) -> list[dict]:
    """
    Search the web for a research topic.
    Returns a list of titles, URLs and snippets.
    """
    results = []

    try:
        with DDGS() as search:
            search_results = search.text(
                topic,
                max_results=max_results,
            )

            for item in search_results:
                title = item.get("title", "").strip()
                url = item.get("href", "").strip()
                snippet = item.get("body", "").strip()

                if title and url:
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                    })

    except Exception:
        logger.exception("Web research search failed.")

    return results