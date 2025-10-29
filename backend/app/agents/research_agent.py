"""
Research Agent - Gathers and organizes research materials
"""
from autogen import ConversableAgent
from app.core.llm_config import get_llm_config
from app.services.research_service import research_service
from app.services.rag_service import rag_service

llm_config = get_llm_config()


def create_research_agent(name: str = "research_agent"):
    """Create and return Research Agent"""
    
    system_message = """You are a research specialist focused on gathering credible, accurate information 
    from various sources. Your role is to find and organize relevant information for book content.
    
    You have access to web search capabilities and should:
    1. Search for relevant information based on the topic
    2. Extract and organize key information
    3. Identify credible sources
    4. Provide summaries of findings
    5. Note important statistics, facts, and examples
    
    Always prioritize accuracy and credibility in your research."""
    
    agent = ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    return agent


def perform_research(book_id: int, topic: str) -> dict:
    """
    Perform research for a topic and store in RAG
    
    Args:
        book_id: Book ID
        topic: Research topic
        
    Returns:
        Summary of research findings
    """
    # Search web
    search_results = research_service.search_web(topic, max_results=10)
    
    documents = []
    metadata = []
    sources = []
    
    for i, result in enumerate(search_results):
        snippet = result.get('snippet', '')
        documents.append(snippet)
        metadata.append({
            'url': result.get('url', ''),
            'title': result.get('title', ''),
            'source': 'web_search'
        })
        sources.append(result)
    
    # Add to RAG
    if documents:
        rag_service.add_documents(book_id, documents, metadata)
    
    return {
        'sources_found': len(sources),
        'sources': sources
    }

