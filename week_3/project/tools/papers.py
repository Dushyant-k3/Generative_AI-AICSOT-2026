import requests

def paper_search(query: str, limit: int = 5) -> dict:
    """Search the Hugging Face Papers API for academic research."""
    try:
        
        url = "https://huggingface.co/api/papers"
        params = {"q": query}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        
        items = data if isinstance(data, list) else data.get("papers", [])
        
        papers_list = []
        for paper in items[:limit]:
            arxiv_id = paper.get("id")
            papers_list.append({
                "arxiv_id": arxiv_id,
                "title": paper.get("title", "Unknown Title"),
                "abstract": paper.get("summary", "No abstract available."),
                "url": f"https://huggingface.co/papers/{arxiv_id}"
            })
            
        return {"papers": papers_list}
    except Exception as e:
        return {"error": str(e)}

def read_paper(arxiv_id: str) -> dict:
    """Read the metadata and markdown content of an academic paper."""
    try:
        
        meta_url = f"https://huggingface.co/api/papers/{arxiv_id}"
        meta_response = requests.get(meta_url)
        meta_response.raise_for_status()
        metadata = meta_response.json()
        
        # 2. Grab the actual markdown text of the paper
        md_url = f"https://huggingface.co/api/papers/{arxiv_id}.md"
        md_response = requests.get(md_url)
        
        if md_response.status_code == 200:
            content = md_response.text
        else:
            
            content = metadata.get("summary", "Markdown content not found.")
            
        return {
            "arxiv_id": arxiv_id,
            "title": metadata.get("title", "Unknown Title"),
            "abstract": metadata.get("summary", "No abstract available."),
            "content": content[:12000], # Truncated to protect the AI's context limit
            "url": f"https://huggingface.co/papers/{arxiv_id}"
        }
    except Exception as e:
        return {"error": str(e)}