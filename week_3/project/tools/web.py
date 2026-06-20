"""
Web search and fetch tools — carry forward from Week 2.

Implement or copy from your week_2/project/:
  - web_search(query) — Serper
  - web_fetch(url) — requests + trafilatura/markdownify
"""

import os
import requests
import trafilatura

def search_web(query: str) -> dict:
    """Search Google using the Serper API."""
    try:
        api_key = os.environ.get("SERPER_API_KEY")
        if not api_key:
            return {"error": "SERPER_API_KEY is not set in .env"}
            
        url = "https://google.serper.dev/search"
        payload = {"q": query}
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        results = []
        for item in data.get("organic", [])[:5]:
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })
            
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

def read_page(url: str) -> dict:
    """Download and extract the main text of a webpage."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return {"error": f"Failed to download {url}"}
            
        text = trafilatura.extract(downloaded)
        if text is None:
            return {"error": "Failed to extract text from page."}
            
        
        return {"url": url, "content": text[:12000]}
    except Exception as e:
        return {"error": str(e)}