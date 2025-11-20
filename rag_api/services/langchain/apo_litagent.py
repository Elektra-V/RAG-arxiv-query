"""LitAgent implementation for automated prompt optimization with Agent-lightning."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from agentlightning import LitAgent, PromptTemplate, RolloutRawResult, TaskInput, NamedResources

from rag_api.clients.openai import get_openai_client
from rag_api.services.langchain.apo_agent import (
    _convert_langchain_tool_to_openai_function,
    _execute_tool,
)
from rag_api.services.langchain.tools import arxiv_search, rag_query
from rag_api.settings import get_settings

logger = logging.getLogger(__name__)


class RAGLitAgent(LitAgent):
    """LitAgent implementation for RAG agent with automated prompt optimization.
    
    This agent uses Agent-lightning's automated optimization to improve
    the system prompt through iterative training.
    """
    
    def training_rollout(
        self, 
        task: TaskInput, 
        rollout_id: str, 
        resources: NamedResources
    ) -> RolloutRawResult:
        """Execute a training rollout with the given prompt template.
        
        This method is called by Agent-lightning's Trainer during optimization.
        The Trainer will automatically vary the prompt template to find optimal prompts.
        
        Args:
            task: Task input containing the query and metadata
            rollout_id: Unique identifier for this rollout
            resources: Named resources including the prompt template to optimize
            
        Returns:
            RolloutRawResult with reward score (0.0 to 1.0)
        """
        settings = get_settings()
        client = get_openai_client()
        
        # Extract query from task
        # TaskInput can be a dict or have different structures
        if isinstance(task, dict):
            query = task.get('query', task.get('input', str(task)))
        elif hasattr(task, 'query'):
            query = task.query
        elif hasattr(task, 'input'):
            query = task.input
        else:
            query = str(task)
        
        # Get prompt template from resources
        # Agent-lightning will provide optimized prompts here
        prompt_template: PromptTemplate | None = None
        if resources and 'prompt' in resources:
            prompt_template = resources['prompt']
        elif resources and 'prompt_template' in resources:
            prompt_template = resources['prompt_template']
        elif resources:
            # Try to get first PromptTemplate resource
            for key, value in resources.items():
                if isinstance(value, PromptTemplate):
                    prompt_template = value
                    break
        
        # Fallback to baseline if no template provided
        if prompt_template is None:
            from rag_api.services.langchain.prompt_template import get_baseline_prompt_template
            baseline_prompt = get_baseline_prompt_template()
            prompt_template = PromptTemplate(template=baseline_prompt, engine='f-string')
        
        # Get the system prompt from template
        system_prompt = prompt_template.template if hasattr(prompt_template, 'template') else str(prompt_template)
        
        # Convert LangChain tools to OpenAI function schemas
        tools = [rag_query, arxiv_search]
        functions = [_convert_langchain_tool_to_openai_function(tool) for tool in tools]
        
        # Initialize conversation
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query}
        ]
        
        max_iterations = 10
        iteration = 0
        used_tools = []
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                # Call OpenAI with function calling
                response = client.chat.completions.create(
                    model=settings.openai_model,
                    messages=messages,
                    tools=functions,
                    tool_choice='auto',
                    temperature=0,
                )
                
                message = response.choices[0].message
                messages.append({
                    'role': message.role,
                    'content': message.content or '',
                    'tool_calls': [
                        {
                            'id': tc.id,
                            'type': tc.type,
                            'function': {
                                'name': tc.function.name,
                                'arguments': tc.function.arguments
                            }
                        } for tc in (message.tool_calls or [])
                    ] if message.tool_calls else None
                })
                
                # Track tool usage
                if message.tool_calls:
                    for tc in message.tool_calls:
                        tool_name = tc.function.name
                        if tool_name not in used_tools:
                            used_tools.append(tool_name)
                
                # If no tool calls, we're done
                if not message.tool_calls:
                    break
                
                # Execute tool calls
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # Execute tool
                    tool_result = _execute_tool(function_name, arguments)
                    
                    # Add tool result to messages
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': tool_result,
                        'name': function_name
                    })
            
            except Exception as e:
                logger.error(f"Error in rollout {rollout_id}: {e}", exc_info=True)
                # Return low reward for errors
                return 0.0
        
        # Extract final response
        final_response = messages[-1].get('content', '') if messages else ''
        
        # If last message was a tool call, get the assistant's final response
        if messages and messages[-1].get('role') == 'tool':
            try:
                response = client.chat.completions.create(
                    model=settings.openai_model,
                    messages=messages,
                    temperature=0,
                )
                final_response = response.choices[0].message.content or ''
            except Exception as e:
                logger.error(f"Error getting final response: {e}", exc_info=True)
        
        # Calculate reward score
        reward = self._calculate_reward(
            query=query,
            response=final_response,
            used_tools=used_tools,
            messages=messages,
            task=task
        )
        
        # Return reward (Agent-lightning will use this for optimization)
        return reward
    
    def _calculate_reward(
        self,
        query: str,
        response: str,
        used_tools: list[str],
        messages: list[dict],
        task: Any
    ) -> float:
        """Calculate reward score for the rollout.
        
        This is the same logic as rag_response_grader but adapted for LitAgent.
        """
        if not response:
            return 0.0
        
        score = 0.0
        
        # 1. Tool Usage (0.3 points)
        tool_usage_score = 0.0
        used_rag_query = 'rag_query' in used_tools
        used_arxiv_search = 'arxiv_search' in used_tools
        
        if used_rag_query or used_arxiv_search:
            tool_usage_score = 0.3
        
        score += tool_usage_score
        
        # 2. Output Format Compliance (0.2 points)
        format_score = 0.0
        has_tool_log = 'TOOL_LOG' in response.upper()
        has_answer = 'ANSWER:' in response.upper() or len(response) > 50
        
        if has_tool_log and has_answer:
            format_score = 0.2
        elif has_answer:
            format_score = 0.1
        
        score += format_score
        
        # 3. Response Completeness (0.3 points)
        completeness_score = 0.0
        response_lower = response.lower()
        
        error_indicators = ['error', 'failed', 'unable to', 'cannot', 'empty']
        has_errors = any(indicator in response_lower for indicator in error_indicators)
        
        if not has_errors and len(response) > 100:
            completeness_score = 0.3
        elif len(response) > 50:
            completeness_score = 0.15
        
        score += completeness_score
        
        # 4. Response Quality (0.2 points)
        quality_score = 0.0
        
        has_citations = any(
            keyword in response_lower
            for keyword in ['arxiv', 'paper', 'source', 'reference', 'http', 'doi']
        )
        
        has_content = not any(
            phrase in response_lower
            for phrase in ["i don't know", "i cannot", "no information", "unable to find"]
        )
        
        if has_citations and has_content:
            quality_score = 0.2
        elif has_content:
            quality_score = 0.1
        
        # Check expected output if provided in task
        if isinstance(task, dict) and 'expected_output_contains' in task:
            expected = task['expected_output_contains']
            if isinstance(expected, str):
                expected = [expected]
            found_expected = sum(1 for phrase in expected if phrase.lower() in response_lower)
            if found_expected > 0:
                quality_score = min(0.2, quality_score + (found_expected / len(expected)) * 0.1)
        
        score += quality_score
        
        return min(max(score, 0.0), 1.0)

