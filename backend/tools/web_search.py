"""Busca web via DuckDuckGo (biblioteca ddgs, sem chave de API)."""
try: from ddgs import DDGS
except ImportError: from duckduckgo_search import DDGS
def search(query: str, n: int = 5):
    with DDGS() as d:
        return [{"title": r["title"], "url": r["href"], "snippet": r["body"]} for r in d.text(query, max_results=n)]
