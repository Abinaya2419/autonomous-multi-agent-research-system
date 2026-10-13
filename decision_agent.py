
import logging
import requests

from config import (
    GEMINI_API_KEY,
    GEMINI_API_URL,
    REQUEST_TIMEOUT_SECONDS,
)

logger = logging.getLogger("research_system.decision")


def make_decision(
    topic: str,
    analysis: str,
    sources: list[dict],
) -> str:
    """
    Generate an evidence-based decision and recommendation
    using the research analysis and available sources.
    """

    if not analysis or "Analysis unavailable" in analysis:
        return (
            "Decision unavailable: valid research analysis "
            "is required before making a recommendation."
        )

    source_context = "\n".join(
        f"- {item.get('title', '')}: {item.get('url', '')}"
        for item in sources
        if item.get("title") and item.get("url")
    )

    prompt = f"""
You are the Decision Agent in an autonomous research system.

Research topic:
{topic}

Analysis from the Analyst Agent:
{analysis}

Available source references:
{source_context or "No source references available."}

Create a structured decision report with these sections:

1. Decision Summary
2. Recommended Option
3. Reasons for the Recommendation
4. Alternatives Considered
5. Risks and Mitigation
6. Confidence Level and Evidence Limitations
7. Action Plan

Rules:
- Base the decision on the supplied analysis and source references.
- Clearly distinguish verified information from assumptions.
- Do not invent facts, statistics, or source details.
- If the evidence is insufficient, state that clearly.
- Explain why the recommended option is preferable.
- Do not claim that you independently verified the full webpages.
- Make practical, actionable recommendations.
"""

    if not GEMINI_API_KEY or not GEMINI_API_URL:
        return "Decision unavailable: Gemini configuration is missing."

    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "You are a careful decision-support agent. "
                        "Compare alternatives, assess uncertainty, "
                        "and recommend practical actions based on evidence."
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
            "maxOutputTokens": 1200,
        },
    }

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }

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
            return "Decision unavailable: Gemini returned no results."

        parts = candidates[0].get("content", {}).get("parts", [])

        decision = "\n".join(
            part["text"]
            for part in parts
            if isinstance(part.get("text"), str)
        ).strip()

        return decision or "Decision unavailable: empty response."

    except requests.RequestException:
        logger.exception("Decision Agent request failed.")
        return "Decision unavailable because the AI service failed."

    except (ValueError, KeyError, IndexError):
        logger.exception("Invalid response from decision model.")
        return "Decision unavailable because the response was invalid."
