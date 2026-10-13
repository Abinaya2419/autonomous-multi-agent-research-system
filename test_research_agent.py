
from research_agent import search_web

topic = "Artificial intelligence applications in healthcare"

print("Searching the web...")
results = search_web(topic, max_results=5)

if results:
    for index, item in enumerate(results, start=1):
        print(f"\n{index}. {item['title']}")
        print("URL:", item["url"])
        print("Summary:", item["snippet"])
else:
    print("No results found. Check internet connection and retry.")
