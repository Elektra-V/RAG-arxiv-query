"""LitAgent implementation for automated prompt optimization."""

from __future__ import annotations

import json
import logging
from typing import Any

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
    """LitAgent for RAG agent with automated prompt optimization."""
    
    def training_rollout(
        self, 
        task: TaskInput, 
        rollout_id: str, 
        resources: NamedResources
    ) -> RolloutRawResult:
        """Execute training rollout with given prompt template."""
        settings = get_settings()
        client = get_openai_client()
        
        if isinstance(task, dict):
            query = task.get('query', task.get('input', str(task)))
        elif hasattr(task, 'query'):
            query = task.query
        elif hasattr(task, 'input'):
            query = task.input
        else:
            query = str(task)
        
        prompt_template: PromptTemplate | None = None
        if resources and 'prompt' in resources:
            prompt_template = resources['prompt']
        elif resources and 'prompt_template' in resources:
            prompt_template = resources['prompt_template']
        elif resources:
            for key, value in resources.items():
                if isinstance(value, PromptTemplate):
                    prompt_template = value
                    break
        
        if prompt_template is None:
            from rag_api.services.langchain.prompt_template import get_baseline_prompt_template
            baseline_prompt = get_baseline_prompt_template()
            prompt_template = PromptTemplate(template=baseline_prompt, engine='f-string')
        
        system_prompt = prompt_template.template if hasattr(prompt_template, 'template') else str(prompt_template)
        
        tools = [rag_query, arxiv_search]
        functions = [_convert_langchain_tool_to_openai_function(tool) for tool in tools]
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query}
        ]
        
        max_iterations = 10
        iteration = 0
        used_tools = []
        tool_sequence = []
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
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
                            'function': {'name': tc.function.name, 'arguments': tc.function.arguments}
                        } for tc in (message.tool_calls or [])
                    ] if message.tool_calls else None
                })
                
                if message.tool_calls:
                    for tc in message.tool_calls:
                        tool_name = tc.function.name
                        if tool_name not in used_tools:
                            used_tools.append(tool_name)
                        if tool_name in ['rag_query', 'arxiv_search']:
                            tool_sequence.append(tool_name)
                
                if not message.tool_calls:
                    break
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    tool_result = _execute_tool(function_name, arguments)
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': tool_result,
                        'name': function_name
                    })
            
            except Exception as e:
                logger.error(f"Error in rollout {rollout_id}: {e}", exc_info=True)
                return 0.0
        
        final_response = messages[-1].get('content', '') if messages else ''
        
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
        
        reward = self._calculate_reward(
            query=query,
            response=final_response,
            used_tools=used_tools,
            tool_sequence=tool_sequence,
            messages=messages,
            task=task
        )
        
        return reward
    
    def _calculate_reward(
        self,
        query: str,
        response: str,
        used_tools: list[str],
        tool_sequence: list[str],
        messages: list[dict],
        task: Any
    ) -> float:
        """Calculate reward score with emphasis on intelligent tool selection."""
        if not response:
            return 0.0
        
        score = 0.0
        
        used_rag_query = 'rag_query' in used_tools
        used_arxiv_search = 'arxiv_search' in used_tools
        first_tool = tool_sequence[0] if tool_sequence else None
        
        # Check if query is invalid (gibberish)
        query_lower = query.lower()
        is_invalid_query = isinstance(task, dict) and task.get('is_invalid', False)
        response_lower = response.lower()
        
        # Detect gibberish patterns
        gibberish_patterns = [
            len(query_lower) < 3,
            query_lower.isdigit(),
            all(not c.isalnum() for c in query_lower),
            query_lower in ['asdfghjkl', 'qwertyuiop', '123456789', 'xyzabc123', 'fghjklmnbvcxz'],
            len(set(query_lower)) < 3 and len(query_lower) > 5,
            'xyzabc123' in query_lower,
            'nonexistent123456' in query_lower,
            bool(query_lower.count('123') > 1 and len(query_lower) < 20),
        ]
        
        detected_invalid = any(gibberish_patterns) or is_invalid_query
        
        # Reward rejecting invalid queries without tool usage
        if detected_invalid:
            if not used_rag_query and not used_arxiv_search:
                score += 0.5
                if 'invalid' in response_lower or 'valid query' in response_lower:
                    score += 0.3
            else:
                score -= 0.5
            return min(max(score, 0.0), 1.0)
        
        # Base score for using tools (only for valid queries)
        if used_rag_query or used_arxiv_search:
            score += 0.3
        
        # Intelligent tool selection bonus
        if isinstance(task, dict) and 'intelligent_choice' in task:
            expected_first = task['intelligent_choice']
            if expected_first == 'arxiv_search_first' and first_tool == 'arxiv_search':
                score += 0.15  # Reward intelligent exception
            elif expected_first == 'rag_query_first' and first_tool == 'rag_query':
                score += 0.1  # Reward cost-effective choice
            elif expected_first == 'arxiv_search_first' and first_tool == 'rag_query':
                score -= 0.1  # Penalize missing intelligent exception
            elif expected_first == 'rag_query_first' and first_tool == 'arxiv_search':
                score -= 0.05  # Small penalty for unnecessary cost
        
        # Check query keywords for intelligent decision-making
        query_lower = query.lower()
        should_use_arxiv_first = any(
            keyword in query_lower 
            for keyword in ['recent', 'latest', 'new', 'newest', 'search arxiv', '2024', '2023', 'published in']
        )
        
        if should_use_arxiv_first and first_tool == 'arxiv_search':
            score += 0.1  # Reward intelligent decision-making
        elif should_use_arxiv_first and first_tool == 'rag_query':
            score -= 0.05  # Small penalty for missing context
        
        # Output format compliance
        has_tool_log = 'TOOL_LOG' in response.upper()
        has_answer = 'ANSWER:' in response.upper() or len(response) > 50
        
        if has_tool_log and has_answer:
            score += 0.2
        elif has_answer:
            score += 0.1
        
        # Response completeness
        response_lower = response.lower()
        error_indicators = ['error', 'failed', 'unable to', 'cannot', 'empty']
        has_errors = any(indicator in response_lower for indicator in error_indicators)
        
        if not has_errors and len(response) > 100:
            score += 0.3
        elif len(response) > 50:
            score += 0.15
        
        # Response quality
        has_citations = any(
            keyword in response_lower
            for keyword in ['arxiv', 'paper', 'source', 'reference', 'http', 'doi']
        )
        
        has_content = not any(
            phrase in response_lower
            for phrase in ["i don't know", "i cannot", "no information", "unable to find"]
        )
        
        if has_citations and has_content:
            score += 0.2
        elif has_content:
            score += 0.1
        
        if isinstance(task, dict) and 'expected_output_contains' in task:
            expected = task['expected_output_contains']
            if isinstance(expected, str):
                expected = [expected]
            found_expected = sum(1 for phrase in expected if phrase.lower() in response_lower)
            if found_expected > 0:
                score = min(1.0, score + (found_expected / len(expected)) * 0.1)
        
        return min(max(score, 0.0), 1.0)
