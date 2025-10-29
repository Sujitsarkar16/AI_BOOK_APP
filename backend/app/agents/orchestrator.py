"""
Book Generation Orchestrator - Coordinates all agents
"""
from typing import Dict, List, Optional, Callable
from autogen import GroupChat
from autogen.agentchat import AssistantAgent
from app.agents.ideation_agent import create_ideation_agent
from app.agents.research_agent import create_research_agent, perform_research
from app.agents.outline_agent import create_outline_agent
from app.agents.writing_agent import create_writing_agent
from app.agents.content_agent import create_content_agent
from app.agents.editor_agent import create_editor_agent
from app.agents.format_agent import FormatAgent
from app.services.rag_service import rag_service
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class BookGenerationOrchestrator:
    """Orchestrates multi-agent book generation"""
    
    def __init__(self, websocket_callback: Optional[Callable] = None):
        """
        Initialize orchestrator
        
        Args:
            websocket_callback: Optional callback for sending WebSocket updates
        """
        self.websocket_callback = websocket_callback
        
        # Create agents
        self.ideation_agent = create_ideation_agent()
        self.research_agent = create_research_agent()
        self.outline_agent = create_outline_agent()
        self.writing_agent = create_writing_agent()
        self.content_agent = create_content_agent()
        self.editor_agent = create_editor_agent()
        self.format_agent = FormatAgent()
        
        # Create group chat
        self.agents = [
            self.ideation_agent,
            self.research_agent,
            self.outline_agent,
            self.writing_agent,
            self.content_agent,
            self.editor_agent,
        ]
    
    def _send_update(self, message_type: str, data: dict):
        """Send WebSocket update if callback is available"""
        if self.websocket_callback:
            self.websocket_callback({'type': message_type, 'data': data})
    
    def _update_agent_status(self, agent_name: str, status: str, task: Optional[str] = None):
        """Update agent status via WebSocket"""
        self._send_update('agent_status', {
            'agent_name': agent_name,
            'status': status,
            'current_task': task
        })
    
    async def ideate(self, book_config: dict) -> dict:
        """
        Ideation phase - refine book concept
        
        Args:
            book_config: Book configuration
            
        Returns:
            Refined book concept
        """
        self._update_agent_status('ideation_agent', 'active', 'Refining book concept')
        
        prompt = f"""
        Refine and expand this book concept:
        
        Title/Idea: {book_config.get('book_idea')}
        Description: {book_config.get('description', '')}
        Genre: {book_config.get('genre')}
        Target Audience: {book_config.get('target_audience', '')}
        
        Provide:
        1. Refined core concept
        2. Unique angles and perspectives
        3. Structure suggestions
        4. Why this resonates with the target audience
        """
        
        # Use simple LLM call (GroupChat can be complex for single-agent tasks)
        result = await self._simple_llm_call(self.ideation_agent, prompt)
        
        self._update_agent_status('ideation_agent', 'idle')
        
        return result
    
    async def research(self, book_id: int, topic: str) -> dict:
        """
        Research phase - gather information
        
        Args:
            book_id: Book ID
            topic: Research topic
            
        Returns:
            Research summary
        """
        self._update_agent_status('research_agent', 'active', f'Researching: {topic}')
        
        # Perform web research
        research_results = perform_research(book_id, topic)
        
        self._update_agent_status('research_agent', 'idle')
        
        return research_results
    
    async def create_outline(self, book_config: dict, chapters_count: int, refined_concept: str) -> List[dict]:
        """
        Outline phase - create chapter structure
        
        Args:
            book_config: Book configuration
            chapters_count: Number of chapters
            refined_concept: Refined book concept
            
        Returns:
            List of chapter outlines
        """
        self._update_agent_status('outline_agent', 'active', 'Creating book structure')
        
        prompt = f"""
        Create a detailed outline for a book with {chapters_count} chapters.
        
        Book Title/Idea: {book_config.get('book_idea')}
        Refined Concept: {refined_concept}
        Genre: {book_config.get('genre')}
        Target Audience: {book_config.get('target_audience', '')}
        Tone: {book_config.get('tone')}
        
        Provide:
        1. Chapter titles (compelling and specific)
        2. Brief description for each chapter
        3. Logical flow between chapters
        
        Format as a numbered list.
        """
        
        result = await self._simple_llm_call(self.outline_agent, prompt)
        
        self._update_agent_status('outline_agent', 'idle')
        
        return result
    
    async def generate_chapter(
        self, 
        book_id: int, 
        chapter_outline: dict, 
        book_config: dict,
        context: Optional[str] = None
    ) -> str:
        """
        Generate a single chapter through all agent stages
        
        Args:
            book_id: Book ID
            chapter_outline: Chapter outline dict
            book_config: Book configuration
            context: Additional context from RAG
            
        Returns:
            Final formatted chapter content
        """
        chapter_title = chapter_outline.get('title', 'Untitled')
        word_count_goal = book_config.get('words_per_chapter', 2500)
        
        # 1. Writing Agent
        self._update_agent_status('writing_agent', 'active', f'Writing: {chapter_title}')
        
        writing_prompt = f"""
        Write a comprehensive chapter for this book.
        
        Chapter Title: {chapter_title}
        Chapter Description: {chapter_outline.get('description', '')}
        Target Word Count: {word_count_goal}
        Tone: {book_config.get('tone')}
        Genre: {book_config.get('genre')}
        
        Use markdown format with headings, lists, and emphasis.
        Write engaging, informative content suitable for {book_config.get('target_audience', 'general readers')}.
        
        Additional Context:
        {context or 'No additional context provided.'}
        
        Begin writing the chapter now.
        """
        
        draft_content = await self._simple_llm_call(self.writing_agent, writing_prompt)
        
        # 2. Content Agent
        self._update_agent_status('content_agent', 'active', f'Enhancing: {chapter_title}')
        
        content_prompt = f"""
        Enhance this chapter draft by adding:
        1. Concrete examples and case studies
        2. Relevant statistics or data points
        3. Better transitions between sections
        4. Actionable takeaways
        5. Depth to complex topics
        
        Original Chapter:
        {draft_content}
        
        Provide the enhanced version:
        """
        
        enhanced_content = await self._simple_llm_call(self.content_agent, content_prompt)
        
        # 3. Editor Agent
        self._update_agent_status('editor_agent', 'active', f'Editing: {chapter_title}')
        
        editor_prompt = f"""
        Edit this chapter for grammar, clarity, style, and consistency.
        Maintain the tone: {book_config.get('tone')}
        
        Chapter to edit:
        {enhanced_content}
        
        Provide the edited version:
        """
        
        edited_content = await self._simple_llm_call(self.editor_agent, editor_prompt)
        
        # 4. Format Agent
        self._update_agent_status('format_agent', 'active', f'Formatting: {chapter_title}')
        
        formatted_content = self.format_agent.format_chapter(edited_content)
        
        self._update_agent_status('format_agent', 'idle')
        
        return formatted_content
    
    async def handle_chat_request(self, book_id: int, user_message: str, context: dict) -> str:
        """
        Handle user chat requests for modifications
        
        Args:
            book_id: Book ID
            user_message: User's request
            context: Current book/chapter context
            
        Returns:
            Response from agents
        """
        # Use ideation agent for chat responses
        prompt = f"""
        User Request: {user_message}
        
        Context:
        {context}
        
        Provide a helpful response about what you'll do to address this request.
        """
        
        self._update_agent_status('ideation_agent', 'active', 'Processing user request')
        
        response = await self._simple_llm_call(self.ideation_agent, prompt)
        
        self._update_agent_status('ideation_agent', 'idle')
        
        return response
    
    async def _simple_llm_call(self, agent, prompt: str) -> str:
        """Make a simple LLM call using Gemini API"""
        logger.info(f"Agent {agent.name} called with prompt: {prompt[:100]}...")
        
        try:
            # Get the agent's system message for context
            system_message = ""
            if hasattr(agent, 'system_message'):
                system_message = agent.system_message
            
            # Combine system message with user prompt
            full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
            
            # Use direct Gemini API call (similar to books.py approach)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(full_prompt)
            
            if response and response.text:
                logger.info(f"Agent {agent.name} response received")
                return response.text
            else:
                logger.warning(f"No response from agent {agent.name}")
                return f"Error: No response from {agent.name}"
                
        except Exception as e:
            logger.error(f"Error in LLM call for {agent.name}: {e}", exc_info=True)
            raise

