
import logging
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import GEMINI_API_KEY, MODEL_ID
from research_agent import search_web
from analyst_agent import analyze_research
from decision_agent import make_decision

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("research_system")

app = FastAPI(
    title="Autonomous Multi-Agent Research & Decision System",
    description=(
        "AI-powered system with web research, "
        "analysis, and decision-making agents."
    ),
    version="2.0.0",
)


# -----------------------------
# Request and response models
# -----------------------------

class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    audience: str = "General audience"
    detail_level: str = "medium"


class Source(BaseModel):
    title: str
    url: str
    snippet: str = ""


class ResearchResponse(BaseModel):
    topic: str
    report: str
    analysis: str
    decision: str
    sources: list[Source]
    model: str
    elapsed_seconds: float


# -----------------------------
# Basic endpoints
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Autonomous Multi-Agent Research System is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "api_key_configured": bool(GEMINI_API_KEY),
        "model": MODEL_ID,
        "web_research_enabled": True,
        "agents": [
            "Research Agent",
            "Analyst Agent",
            "Decision Agent",
        ],
    }


# -----------------------------
# Report generation
# -----------------------------

def generate_report(
    topic: str,
    audience: str,
    detail_level: str,
    sources: list[dict],
) -> str:
    """
    Generate the main research report using the existing
    Gemini REST API configuration.
    """

    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is missing. Check your .env file.",
        )

    source_context = "\n\n".join(
        (
            f"Title: {item['title']}\n"
            f"URL: {item['url']}\n"
            f"Summary: {item['snippet']}"
        )
        for item in sources
    )

    if not source_context:
        source_context = "No web search results were available."

    prompt = f"""
Create a structured research report.

Topic: {topic}
Audience: {audience}
Detail level: {detail_level}

Available web research:
{source_context}

Include these sections:
1. Executive Summary
2. Background and Key Concepts
3. Important Findings
4. Benefits and Opportunities
5. Risks and Limitations
6. Practical Recommendations
7. Sources
8. Conclusion

Rules:
- Use the supplied results as supporting information.
- Do not invent facts, statistics, or URLs.
- Distinguish source-supported findings from general knowledge.
- State limitations where evidence is insufficient.
- Do not claim that full webpages were verified.
"""

    from config import GEMINI_API_URL, REQUEST_TIMEOUT_SECONDS
    import requests

    try:
        response = requests.post(
            GEMINI_API_URL,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "systemInstruction": {
                    "parts": [{
                        "text": (
                            "You are a careful AI research assistant. "
                            "Produce structured, evidence-aware reports."
                        )
                    }]
                },
                "contents": [{
                    "role": "user",
                    "parts": [{"text": prompt}],
                }],
                "generationConfig": {"maxOutputTokens": 1800},
            },
            timeout=(10, REQUEST_TIMEOUT_SECONDS),
        )

        if response.status_code in (401, 403):
            raise HTTPException(
                status_code=502,
                detail="Gemini authentication failed. Check API access.",
            )

        if response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Gemini quota reached. Please retry later.",
            )

        if response.status_code == 503:
            raise HTTPException(
                status_code=503,
                detail="Gemini is temporarily unavailable. Retry later.",
            )

        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            raise HTTPException(
                status_code=502,
                detail="Gemini returned no report.",
            )

        parts = candidates[0].get("content", {}).get("parts", [])
        report = "\n".join(
            part["text"]
            for part in parts
            if isinstance(part.get("text"), str)
        ).strip()

        if not report:
            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty report.",
            )

        return report

    except HTTPException:
        raise
    except requests.Timeout:
        logger.exception("Report generation timed out.")
        raise HTTPException(
            status_code=504,
            detail="Report generation timed out. Please retry.",
        )
    except requests.RequestException:
        logger.exception("Report generation failed.")
        raise HTTPException(
            status_code=502,
            detail="Could not connect to Gemini.",
        )
    except (ValueError, KeyError, IndexError):
        logger.exception("Invalid report response.")
        raise HTTPException(
            status_code=502,
            detail="Gemini returned an invalid report response.",
        )


# -----------------------------
# Complete multi-agent workflow
# -----------------------------

@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    start_time = time.perf_counter()
    topic = request.topic.strip()

    logger.info("Starting multi-agent workflow: %s", topic)

    # Agent 1: Research
    try:
        web_results = search_web(topic, max_results=5)
    except Exception:
        logger.exception("Research Agent failed.")
        web_results = []

    sources = []

    for item in web_results:
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        snippet = str(item.get("snippet", "")).strip()

        if title and url.startswith(("https://", "http://")):
            sources.append({
                "title": title,
                "url": url,
                "snippet": snippet,
            })

    logger.info("Research Agent collected %d sources", len(sources))

    # Agent 2: Generate the research report
    report = generate_report(
        topic=topic,
        audience=request.audience,
        detail_level=request.detail_level,
        sources=sources,
    )

    # Agent 3: Analyze the research
    analysis = analyze_research(topic, sources)

    if not analysis or "Analysis unavailable" in analysis:
        logger.warning("Analyst Agent could not complete analysis.")
        analysis = (
            "Analysis could not be completed. "
            "Review the research report and available sources manually."
        )

    # Agent 4: Produce an evidence-based decision
    decision = make_decision(
        topic=topic,
        analysis=analysis,
        sources=sources,
    )

    elapsed = round(time.perf_counter() - start_time, 2)

    logger.info(
        "Multi-agent workflow completed in %s seconds",
        elapsed,
    )

    return ResearchResponse(
        topic=topic,
        report=report,
        analysis=analysis,
        decision=decision,
        sources=[Source(**item) for item in sources],
        model=MODEL_ID,
        elapsed_seconds=elapsed,
    )
