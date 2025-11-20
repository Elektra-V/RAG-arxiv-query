"""Agent-lightning rollout function and grader for APO training."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from agentlightning import PromptTemplate

# Note: Agent-lightning 0.1.2 uses LitAgent pattern, not @rollout decorator
# This function works standalone for evaluation

from rag_api.clients.openai import get_openai_client
from rag_api.services.langchain.tools import arxiv_search, rag_query
from rag_api.settings import get_settings

logger = logging.getLogger(__name__)


def _convert_langchain_tool_to_openai_function(tool) -> Dict[str, Any]:
    """Convert a LangChain tool to OpenAI function calling schema.
    
    Args:
        tool: LangChain tool instance
        
    Returns:
        OpenAI function schema dict
    """
    # Try to get the tool's input schema
    try:
        # LangChain tools have args_schema or can be converted
        if hasattr(tool, 'args_schema') and tool.args_schema:
            tool_schema = tool.args_schema.schema()
        elif hasattr(tool, 'input_schema'):
            tool_schema = tool.input_schema.schema()
        else:
            # Fallback: use tool's JSON schema method if available
            tool_schema = tool.json_schema() if hasattr(tool, 'json_schema') else {}
    except Exception:
        tool_schema = {}
    
    # Extract parameter properties from schema
    properties = {}
    required = []
    
    if 'properties' in tool_schema:
        properties = tool_schema['properties']
        required = tool_schema.get('required', [])
    
    # If no schema, infer from tool name and description
    if not properties:
        # Default for rag_query
        if tool.name == 'rag_query':
            properties = {
                'query': {
                    'type': 'string',
                    'description': 'Search query for the RAG knowledge base'
                }
            }
            required = ['query']
        # Default for arxiv_search
        elif tool.name == 'arxiv_search':
            properties = {
                'query': {
                    'type': 'string',
                    'description': 'Search query for arXiv (e.g., "quantum computing", "cat:cs.AI")'
                },
                'max_results': {
                    'type': 'integer',
                    'description': 'Maximum number of papers to return (default: 5)',
                    'default': 5
                }
            }
            required = ['query']
    
    # Get description
    description = tool.description if hasattr(tool, 'description') and tool.description else f'Tool: {tool.name}'
    
    return {
        'type': 'function',
        'function': {
            'name': tool.name,
            'description': description,
            'parameters': {
                'type': 'object',
                'properties': properties,
                'required': required
            }
        }
    }


def _execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool by name with given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments to pass to the tool
        
    Returns:
        Tool execution result as string
    """
    if tool_name == 'rag_query':
        return rag_query.invoke(arguments)
    elif tool_name == 'arxiv_search':
        return arxiv_search.invoke(arguments)
    else:
        return f"ERROR: Unknown tool '{tool_name}'"


def rag_agent_rollout(task: Dict[str, Any], prompt_template: PromptTemplate) -> Dict[str, Any]:
    """Rollout function for RAG agent using OpenAI function calling.
    
    This function executes the agent with the given prompt template and returns
    the conversation history and final response for evaluation.
    
    Args:
        task: Task dict with 'query' and optionally 'expected_output', 'expected_tool_usage', etc.
        prompt_template: Agent-lightning PromptTemplate (optimized or baseline)
        
    Returns:
        Dict with 'messages' (conversation history) and 'response' (final answer)
    """
    settings = get_settings()
    client = get_openai_client()
    
    # Get the prompt from template
    # PromptTemplate has 'template' field, not 'prompt'
    system_prompt = prompt_template.template if hasattr(prompt_template, 'template') else str(prompt_template)
    
    # Convert LangChain tools to OpenAI function schemas
    tools = [rag_query, arxiv_search]
    functions = [_convert_langchain_tool_to_openai_function(tool) for tool in tools]
    function_map = {tool.name: tool for tool in tools}
    
    # Initialize conversation
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': task['query']}
    ]
    
    max_iterations = 10  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
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
    
    # Extract final response
    final_response = messages[-1].get('content', '') if messages else ''
    
    # If last message was a tool call, get the assistant's final response
    if messages and messages[-1].get('role') == 'tool':
        # Make one more call to get final answer
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0,
        )
        final_response = response.choices[0].message.content or ''
        messages.append({
            'role': 'assistant',
            'content': final_response
        })
    
    return {
        'messages': messages,
        'response': final_response,
        'task': task
    }


def rag_response_grader(rollout_result: Dict[str, Any]) -> float:
    """Grade the agent's response based on multiple criteria.
    
    Evaluation criteria:
    - Tool usage (did it use rag_query or arxiv_search?)
    - Response quality (relevance, accuracy, citations)
    - Output format compliance (TOOL_LOG structure)
    - Completeness (answered the question vs. empty/error)
    
    Args:
        rollout_result: Result from rag_agent_rollout containing messages and response
        
    Returns:
        Reward score from 0.0 to 1.0
    """
    messages = rollout_result.get('messages', [])
    response = rollout_result.get('response', '')
    task = rollout_result.get('task', {})
    
    if not response:
        return 0.0
    
    score = 0.0
    max_score = 1.0
    
    # 1. Tool Usage (0.3 points)
    tool_usage_score = 0.0
    used_rag_query = False
    used_arxiv_search = False
    
    for msg in messages:
        if msg.get('role') == 'assistant' and msg.get('tool_calls'):
            for tc in msg['tool_calls']:
                func_name = tc.get('function', {}).get('name', '')
                if func_name == 'rag_query':
                    used_rag_query = True
                elif func_name == 'arxiv_search':
                    used_arxiv_search = True
    
    # Must use at least one tool
    if used_rag_query or used_arxiv_search:
        tool_usage_score = 0.3
        # Bonus for using both tools appropriately
        if used_rag_query and used_arxiv_search:
            tool_usage_score = 0.3  # Same score, but indicates good workflow
    
    score += tool_usage_score
    
    # 2. Output Format Compliance (0.2 points)
    format_score = 0.0
    has_tool_log = 'TOOL_LOG' in response.upper()
    has_answer = 'ANSWER:' in response.upper() or len(response) > 50
    
    if has_tool_log and has_answer:
        format_score = 0.2
    elif has_answer:
        format_score = 0.1  # Partial credit for having an answer
    
    score += format_score
    
    # 3. Response Completeness (0.3 points)
    completeness_score = 0.0
    response_lower = response.lower()
    
    # Check for error indicators
    error_indicators = ['error', 'failed', 'unable to', 'cannot', 'empty']
    has_errors = any(indicator in response_lower for indicator in error_indicators)
    
    if not has_errors and len(response) > 100:
        completeness_score = 0.3
    elif len(response) > 50:
        completeness_score = 0.15
    
    score += completeness_score
    
    # 4. Response Quality (0.2 points)
    quality_score = 0.0
    
    # Check for citations/sources
    has_citations = any(
        keyword in response_lower
        for keyword in ['arxiv', 'paper', 'source', 'reference', 'http', 'doi']
    )
    
    # Check for relevant content (not just "I don't know")
    has_content = not any(
        phrase in response_lower
        for phrase in ["i don't know", "i cannot", "no information", "unable to find"]
    )
    
    if has_citations and has_content:
        quality_score = 0.2
    elif has_content:
        quality_score = 0.1
    
    # Check expected output if provided
    if 'expected_output_contains' in task:
        expected = task['expected_output_contains']
        if isinstance(expected, str):
            expected = [expected]
        found_expected = sum(1 for phrase in expected if phrase.lower() in response_lower)
        if found_expected > 0:
            quality_score = min(0.2, quality_score + (found_expected / len(expected)) * 0.1)
    
    score += quality_score
    
    # Ensure score is between 0.0 and 1.0
    return min(max(score, 0.0), 1.0)

