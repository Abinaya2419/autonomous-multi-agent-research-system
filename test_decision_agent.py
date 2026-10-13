
from research_agent import search_web
from analyst_agent import analyze_research
from decision_agent import make_decision

topic = "AI applications in healthcare"

print("Step 1: Researching the topic...")
sources = search_web(topic, max_results=5)
print("Sources found:", len(sources))

if not sources:
    print("No sources found. Check your internet connection.")
else:
    print("\nStep 2: Analyzing the research...")
    analysis = analyze_research(topic, sources)

    if not analysis or "Analysis unavailable" in analysis:
        print("Analysis failed. Check the Analyst Agent.")
    else:
        print("\nStep 3: Making a decision...")
        decision = make_decision(topic, analysis, sources)

        print("\n--- FINAL DECISION REPORT ---\n")
        print(decision)
