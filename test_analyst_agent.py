
from research_agent import search_web
from analyst_agent import analyze_research

topic = "AI applications in healthcare"

print("Step 1: Searching the web...")
sources = search_web(topic, max_results=5)

print("Sources found:", len(sources))

if sources:
    print("\nStep 2: Analyzing research results...")
    analysis = analyze_research(topic, sources)

    print("\n--- ANALYST REPORT ---\n")
    print(analysis)
else:
    print("No web results found. Check the internet and try again.")
