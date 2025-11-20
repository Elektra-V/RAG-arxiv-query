"""Agent-lightning rollout function and grader for APO training."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from agentlightning import PromptTemplate

from rag_api.clients.openai import get_openai_client
from rag_api.services.langchain.tools import arxiv_search, rag_query
from rag_api.settings import get_settings

logger = logging.getLogger(__name__)


def _convert_langchain_tool_to_openai_function(tool) -> Dict[str, Any]:
    """Convert LangChain tool to OpenAI function calling schema."""
    try:
        if hasattr(tool, 'args_schema') and tool.args_schema:
            tool_schema = tool.args_schema.schema()
        elif hasattr(tool, 'input_schema'):
            tool_schema = tool.input_schema.schema()
        else:
            tool_schema = tool.json_schema() if hasattr(tool, 'json_schema') else {}
    except Exception:
        tool_schema = {}
    
    properties = {}
    required = []
    
    if 'properties' in tool_schema:
        properties = tool_schema['properties']
        required = tool_schema.get('required', [])
    
    if not properties:
        if tool.name == 'rag_query':
            properties = {
                'query': {'type': 'string', 'description': 'Search query for the RAG knowledge base'}
            }
            required = ['query']
        elif tool.name == 'arxiv_search':
            properties = {
                'query': {'type': 'string', 'description': 'Search query for arXiv'},
                'max_results': {'type': 'integer', 'description': 'Maximum number of papers to return', 'default': 5}
            }
            required = ['query']
    
    description = tool.description if hasattr(tool, 'description') and tool.description else f'Tool: {tool.name}'
    
    return {
        'type': 'function',
        'function': {
            'name': tool.name,
            'description': description,
            'parameters': {'type': 'object', 'properties': properties, 'required': required}
        }
    }


def _execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute tool by name with given arguments."""
    if tool_name == 'rag_query':
        return rag_query.invoke(arguments)
    elif tool_name == 'arxiv_search':
        return arxiv_search.invoke(arguments)
    return f"ERROR: Unknown tool '{tool_name}'"


def rag_agent_rollout(task: Dict[str, Any], prompt_template: PromptTemplate) -> Dict[str, Any]:
    """Execute agent rollout with given prompt template."""
    settings = get_settings()
    client = get_openai_client()
    
    system_prompt = prompt_template.template if hasattr(prompt_template, 'template') else str(prompt_template)
    
    tools = [rag_query, arxiv_search]
    functions = [_convert_langchain_tool_to_openai_function(tool) for tool in tools]
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': task['query']}
    ]
    
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
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
    
    final_response = messages[-1].get('content', '') if messages else ''
    
    if messages and messages[-1].get('role') == 'tool':
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0,
        )
        final_response = response.choices[0].message.content or ''
        messages.append({'role': 'assistant', 'content': final_response})
    
    return {'messages': messages, 'response': final_response, 'task': task}


def rag_response_grader(rollout_result: Dict[str, Any]) -> float:
    """Grade agent response with emphasis on intelligent tool selection."""
    messages = rollout_result.get('messages', [])
    response = rollout_result.get('response', '')
    task = rollout_result.get('task', {})
    
    if not response:
        return 0.0
    
    score = 0.0
    
    # Extract tool usage order
    tool_sequence = []
    for msg in messages:
        if msg.get('role') == 'assistant' and msg.get('tool_calls'):
            for tc in msg['tool_calls']:
                func_name = tc.get('function', {}).get('name', '')
                if func_name in ['rag_query', 'arxiv_search']:
                    tool_sequence.append(func_name)
    
    used_rag_query = 'rag_query' in tool_sequence
    used_arxiv_search = 'arxiv_search' in tool_sequence
    first_tool = tool_sequence[0] if tool_sequence else None
    
    # Base score for using tools
    if used_rag_query or used_arxiv_search:
        score += 0.3
    
    # Intelligent tool selection bonus
    if 'intelligent_choice' in task:
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
    query = task.get('query', '').lower()
    should_use_arxiv_first = any(
        keyword in query 
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
    
    if 'expected_output_contains' in task:
        expected = task['expected_output_contains']
        if isinstance(expected, str):
            expected = [expected]
        found_expected = sum(1 for phrase in expected if phrase.lower() in response_lower)
        if found_expected > 0:
            score = min(1.0, score + (found_expected / len(expected)) * 0.1)
    
    return min(max(score, 0.0), 1.0)
