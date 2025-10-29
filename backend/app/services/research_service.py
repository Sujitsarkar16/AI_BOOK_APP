"""
Research service for web scraping and content extraction
"""
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for web research and content extraction"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search the web using DuckDuckGo
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results with title, url, and snippet
        """
        try:
            with DDGS() as ddgs:
                results = []
                for result in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', '')
                    })
                return results
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return []
    
    def extract_content(self, url: str) -> str:
        """
        Extract text content from a URL
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted text content
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 512) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens (approximate)
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Simple sentence-based chunking
        sentences = text.split('.')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size * 4:  # Rough estimate
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]


# Global instance
research_service = ResearchService()

