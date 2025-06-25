"""
Professional AI service with proper context management, error handling, and performance optimization.
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
import os
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import tiktoken

from core.database_layer import db_manager, Section, Project

logger = logging.getLogger(__name__)

@dataclass
class AIRequest:
    """Structured AI request with context."""
    prompt: str
    context: Dict[str, Any]
    max_tokens: int = 1000
    temperature: float = 0.7
    model: str = "gpt-4o-mini"
    stream: bool = False
    user_id: str = ""
    project_id: str = ""

@dataclass
class AIResponse:
    """Structured AI response with metadata."""
    content: str
    model: str
    tokens_used: int
    cost_estimate: float
    processing_time: float
    context_preserved: bool
    error: Optional[str] = None

class ContextManager:
    """Advanced context management for AI conversations."""

    def __init__(self):
        self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        self.max_context_tokens = 8000  # Reserve space for response

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoding.encode(text))

    def build_context_window(self, 
                           current_prompt: str,
                           project_id: str,
                           section_id: Optional[str] = None,
                           include_history: bool = True) -> str:
        """Build optimized context window for AI request."""

        context_parts = []
        token_count = 0

        # Add current prompt (highest priority)
        prompt_tokens = self.count_tokens(current_prompt)
        if prompt_tokens > self.max_context_tokens:
            # Truncate if too long
            current_prompt = self._truncate_to_tokens(current_prompt, self.max_context_tokens)
            prompt_tokens = self.count_tokens(current_prompt)

        context_parts.append(current_prompt)
        token_count += prompt_tokens

        if include_history and token_count < self.max_context_tokens:
            # Add relevant project context
            project_context = self._get_project_context(project_id, section_id)
            project_tokens = self.count_tokens(project_context)

            if token_count + project_tokens <= self.max_context_tokens:
                context_parts.insert(0, project_context)
                token_count += project_tokens

        return "\n\n".join(context_parts)

    def _get_project_context(self, project_id: str, section_id: Optional[str] = None) -> str:
        """Get relevant project context for AI request."""
        with db_manager.get_session() as session:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return ""

            context_parts = [
                f"Project: {project.title}",
                f"Type: {project.project_type}",
                f"Style: {project.style}",
                f"Description: {project.description}"
            ]

            # Add related sections if space allows
            sections = session.query(Section).filter_by(project_id=project_id).order_by(Section.order_index).all()

            for section in sections[:3]:  # Limit to first 3 sections
                if section.id != section_id and section.content:
                    # Add summary of other sections
                    content_preview = section.content[:200] + "..." if len(section.content) > 200 else section.content
                    context_parts.append(f"Section '{section.title}': {content_preview}")

            return "\n".join(context_parts)

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text

        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)

class AIServicePool:
    """Pool of AI service connections with load balancing."""

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_client = None
        self.context_manager = ContextManager()
        self.request_queue = asyncio.Queue()
        self.active_requests = 0
        self.max_concurrent_requests = 5
        self._initialized = False

    def _ensure_initialized(self):
        """Ensure the service is properly initialized."""
        if self._initialized:
            return

        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OpenAI API key is required. Please configure it in the Secrets tab.")

        self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        self._initialized = True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process AI request with retry logic and error handling."""
        start_time = datetime.now()

        try:
            # Ensure service is initialized
            self._ensure_initialized()
            # Build context window
            context_prompt = self.context_manager.build_context_window(
                request.prompt,
                request.project_id,
                include_history=True
            )

            # Count tokens for cost estimation
            input_tokens = self.context_manager.count_tokens(context_prompt)

            # Make API call
            response = await self.openai_client.chat.completions.create(
                model=request.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(request.context)
                    },
                    {
                        "role": "user",
                        "content": context_prompt
                    }
                ],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                user=request.user_id[:64] if request.user_id else "anonymous"  # OpenAI user ID limit
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            # Calculate costs (approximate)
            total_tokens = input_tokens + response.usage.completion_tokens
            cost_estimate = self._calculate_cost(request.model, total_tokens)

            # Track usage in database
            if request.user_id and request.project_id:
                db_manager.track_ai_usage(
                    user_id=request.user_id,
                    project_id=request.project_id,
                    prompt_tokens=input_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    cost_estimate=f"${cost_estimate:.4f}",
                    model_used=request.model
                )

            return AIResponse(
                content=response.choices[0].message.content,
                model=request.model,
                tokens_used=total_tokens,
                cost_estimate=cost_estimate,
                processing_time=processing_time,
                context_preserved=True
            )

        except Exception as e:
            logger.error(f"AI request failed: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()

            return AIResponse(
                content="I apologize, but I encountered an error processing your request. Please try again.",
                model=request.model,
                tokens_used=0,
                cost_estimate=0.0,
                processing_time=processing_time,
                context_preserved=False,
                error=str(e)
            )

    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt based on context."""
        style = context.get('style', 'Standard')
        project_type = context.get('project_type', 'Article académique')
        discipline = context.get('discipline', 'Sciences sociales')

        system_prompts = {
            'Standard': f"You are an expert academic writing assistant specializing in {discipline}. Write clear, precise, and well-structured {project_type} content.",
            'Académique': f"You are a formal academic writing expert in {discipline}. Use specialized terminology and rigorous academic style for {project_type}.",
            'CRÉSUS-NAKAMOTO': f"You are an analytical academic writer specializing in conceptual tensions and historical perspectives in {discipline}. Create sophisticated {project_type} content.",
            'AcademicWritingCrypto': f"You are a technical academic writing expert in crypto-ethnography and socio-technical analysis. Focus on blockchain and decentralized systems in {project_type}."
        }

        return system_prompts.get(style, system_prompts['Standard'])

    def _calculate_cost(self, model: str, total_tokens: int) -> float:
        """Calculate approximate cost for API usage."""
        # OpenAI pricing (approximate, as of 2024)
        pricing = {
            'gpt-4o': 0.005 / 1000,  # $0.005 per 1K tokens
            'gpt-4o-mini': 0.00015 / 1000,  # $0.00015 per 1K tokens
            'gpt-3.5-turbo': 0.002 / 1000,  # $0.002 per 1K tokens
        }

        rate = pricing.get(model, 0.005 / 1000)
        return total_tokens * rate

class ProfessionalAIService:
    """Professional AI service with proper architecture."""

    def __init__(self):
        self.service_pool = None
        self.usage_tracker = {}

    def _ensure_service_pool(self):
        """Ensure service pool is initialized."""
        if self.service_pool is None:
            self.service_pool = AIServicePool()

    async def generate_content(self,
                             prompt: str,
                             context: Dict[str, Any],
                             user_id: str,
                             project_id: str = "",
                             **kwargs) -> AIResponse:
        """Generate academic content with full context awareness."""

        try:
            # Ensure service pool is available
            self._ensure_service_pool()

            request = AIRequest(
                prompt=prompt,
                context=context,
                user_id=user_id,
                project_id=project_id,
                **kwargs
            )

            # Track usage
            self._track_usage(user_id)

            # Process request
            response = await self.service_pool.process_request(request)
        except ValueError as e:
            # Return graceful error response for API key issues
            return AIResponse(
                content="AI service is not available. Please configure the OpenAI API key in the Secrets tab.",
                model=kwargs.get('model', 'gpt-4o-mini'),
                tokens_used=0,
                cost_estimate=0.0,
                processing_time=0.0,
                context_preserved=False,
                error=str(e)
            )

        # Log for monitoring
        logger.info(f"AI request processed for user {user_id}: {response.tokens_used} tokens, ${response.cost_estimate:.4f}")

        return response

    async def analyze_text(self,
                          text: str,
                          analysis_type: str,
                          context: Dict[str, Any],
                          user_id: str) -> AIResponse:
        """Analyze text with specific analysis type."""

        analysis_prompts = {
            'structure': "Analyze the structure and organization of this academic text. Identify strengths and weaknesses.",
            'style': "Analyze the writing style and academic tone. Suggest improvements for clarity and precision.",
            'coherence': "Evaluate the logical flow and coherence of arguments. Identify gaps or inconsistencies.",
            'citations': "Review the use of citations and references. Suggest where additional sources are needed."
        }

        base_prompt = analysis_prompts.get(analysis_type, analysis_prompts['structure'])
        full_prompt = f"{base_prompt}\n\nText to analyze:\n{text}"

        return await self.generate_content(
            prompt=full_prompt,
            context=context,
            user_id=user_id,
            temperature=0.3  # Lower temperature for analysis
        )

    def _track_usage(self, user_id: str):
        """Track user API usage for monitoring and billing."""
        today = datetime.now().date()
        key = f"{user_id}:{today}"

        if key not in self.usage_tracker:
            self.usage_tracker[key] = 0

        self.usage_tracker[key] += 1

    def get_usage_stats(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get usage statistics for a user."""
        stats = {}
        today = datetime.now().date()

        for i in range(days):
            date = today - timedelta(days=i)
            key = f"{user_id}:{date}"
            stats[str(date)] = self.usage_tracker.get(key, 0)

        return {
            'daily_usage': stats,
            'total_requests': sum(stats.values()),
            'average_per_day': sum(stats.values()) / days
        }

# Global AI service instance - now safe to initialize
ai_service = ProfessionalAIService()

# Legacy function for backward compatibility
async def call_ai_safe(prompt: str, max_tokens: int = 1000, temperature: float = 0.7, 
                      model: str = "gpt-4o-mini", use_cache: bool = False) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    try:
        response = await ai_service.generate_content(
            prompt=prompt,
            context={'style': 'Standard', 'project_type': 'Article académique'},
            user_id="legacy",
            max_tokens=max_tokens,
            temperature=temperature,
            model=model
        )

        return {
            "text": response.content,
            "source": "ai_generated",
            "model": response.model,
            "tokens": response.tokens_used,
            "cost": response.cost_estimate
        }
    except Exception as e:
        logger.error(f"Legacy AI call failed: {e}")
        return {
            "text": "An error occurred while generating content.",
            "source": "error",
            "error": str(e)
        }

def generate_academic_text(prompt: str, style: str = "Standard", length: int = 1000) -> Dict[str, Any]:
    """Synchronous wrapper for backward compatibility."""
    try:
        import asyncio

        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async function
        result = loop.run_until_complete(
            call_ai_safe(prompt=prompt, max_tokens=length, temperature=0.7)
        )

        return result

    except Exception as e:
        logger.error(f"Sync AI call failed: {e}")
        return {
            "text": "An error occurred while generating content.",
            "source": "error",
            "error": str(e)
        }