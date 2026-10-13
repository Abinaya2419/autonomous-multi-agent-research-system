
import logging
import requests

from config import (
    GEMINI_API_KEY,
    GEMINI_API_URL,
    REQUEST_TIMEOUT_SECONDS,
)

logger = logging.getLogger("research_system.analyst")


def analyze_research(topic: str, sources: list[dict]) -> str:
    """
    Analyze web research results and identify key insights,
    benefits, risks, and evidence gaps.
    """

    if not sources:
        return (
            "Analysis could not be completed because no web "
            "research sources were available."
        )

    source_context = "\n\n".join(
        (
            f"Title: {item.get('title', '')}\n"
            f"URL: {item.get('url', '')}\n"
            f"Summary: {item.get('snippet', '')}"
        )
        for item in sources
    )

    prompt = f"""
Analyze the web research results for this topic:

{topic}

Research results:
{source_context}

Prepare an analysis with these sections:

1. Key Insights
2. Common Themes and Patterns
3. Benefits and Opportunities
4. Risks and Challenges
5. Evidence Gaps and Uncertainties
6. Practical Recommendations

Rules:
- Base your analysis on the supplied search results.
- Distinguish evidence from your own interpretation.
- Do not invent facts, statistics, or citations.
- Mention when the available evidence is insufficient.
- Do not claim that the full webpages were verified.
"""

    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "You are an analytical research assistant. "
                        "Evaluate evidence carefully and explain "
                        "uncertainties clearly."
                    )
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 1000,
        },
    }

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }

    if not GEMINI_API_KEY:
        return "Analysis unavailable: Gemini API key is missing."

    try:
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            json=payload,
            timeout=(10, REQUEST_TIMEOUT_SECONDS),
        )

        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return "Analysis unavailable: Gemini returned no results."

        parts = candidates[0].get("content", {}).get("parts", [])
        analysis = "\n".join(
            part["text"]
            for part in parts
            if isinstance(part.get("text"), str)
        ).strip()

        return analysis or "Analysis unavailable: empty response."

    except requests.RequestException:
        logger.exception("Analyst agent request failed.")
        return "Analysis unavailable because the AI service failed."

    except (ValueError, KeyError, IndexError):
        logger.exception("Invalid response from analyst model.")
        return "Analysis unavailable because the response was invalid."
