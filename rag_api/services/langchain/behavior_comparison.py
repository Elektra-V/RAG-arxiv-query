"""Compare baseline vs optimized agent behavior."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()


def analyze_tool_usage(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze tool usage from agent messages."""
    tool_sequence = []
    tool_details = {}
    
    for msg in messages:
        if msg.get('role') == 'assistant' and msg.get('tool_calls'):
            for tc in msg['tool_calls']:
                func_name = tc.get('function', {}).get('name', '')
                if func_name in ['rag_query', 'arxiv_search']:
                    tool_sequence.append(func_name)
                    if func_name not in tool_details:
                        tool_details[func_name] = {
                            'count': 0,
                            'queries': []
                        }
                    tool_details[func_name]['count'] += 1
                    # Extract query if available
                    try:
                        import json
                        args = json.loads(tc.get('function', {}).get('arguments', '{}'))
                        if 'query' in args:
                            tool_details[func_name]['queries'].append(args['query'])
                    except:
                        pass
    
    return {
        'sequence': tool_sequence,
        'first_tool': tool_sequence[0] if tool_sequence else None,
        'details': tool_details,
        'used_rag_query': 'rag_query' in tool_sequence,
        'used_arxiv_search': 'arxiv_search' in tool_sequence,
        'total_tools': len(tool_sequence)
    }


def is_intelligent_choice(query: str, first_tool: str | None) -> tuple[bool, str]:
    """Determine if tool choice was intelligent based on query."""
    query_lower = query.lower()
    
    # Keywords that suggest arxiv_search should be first
    arxiv_keywords = ['recent', 'latest', 'new', 'newest', 'search arxiv', '2024', '2023', 'published in']
    should_use_arxiv = any(kw in query_lower for kw in arxiv_keywords)
    
    if should_use_arxiv:
        if first_tool == 'arxiv_search':
            return True, "✓ Intelligent: Used arxiv_search first for 'recent/latest' query"
        else:
            return False, "⚠ Could use arxiv_search first for 'recent/latest' query"
    
    # General queries should use rag_query first (cost-effective)
    if first_tool == 'rag_query':
        return True, "✓ Cost-effective: Used rag_query first for general query"
    elif first_tool == 'arxiv_search':
        return False, "⚠ Could use rag_query first (cheaper) for general query"
    
    return False, "No tools used"


def display_behavior_comparison(
    baseline_results: List[Dict[str, Any]],
    optimized_results: List[Dict[str, Any]],
    queries: List[str],
    verbose: bool = False
) -> None:
    """Display comparison of baseline vs optimized behavior.
    
    If verbose=False (default), only show a concise summary table and key insights.
    """
    console.print("\n[bold yellow]" + "=" * 80 + "[/bold yellow]")
    console.print("[bold yellow]BASELINE vs OPTIMIZED BEHAVIOR COMPARISON[/bold yellow]")
    console.print("[bold yellow]" + "=" * 80 + "[/bold yellow]\n")
    
    # Analyze baseline behavior
    baseline_stats = {
        'rag_query_first': 0,
        'arxiv_search_first': 0,
        'intelligent_choices': 0,
        'total_queries': len(baseline_results)
    }
    
    optimized_stats = {
        'rag_query_first': 0,
        'arxiv_search_first': 0,
        'intelligent_choices': 0,
        'total_queries': len(optimized_results)
    }
    
    # Detailed per-query table (optional)
    if verbose:
        table = Table(title="Tool Selection Behavior", show_header=True, header_style="bold magenta")
        table.add_column("Query", style="cyan", width=40)
        table.add_column("Baseline First Tool", style="yellow", width=20)
        table.add_column("Optimized First Tool", style="green", width=20)
        table.add_column("Improvement", style="magenta", width=30)
    
    for i, query in enumerate(queries):
        baseline_msgs = baseline_results[i].get('messages', []) if i < len(baseline_results) else []
        optimized_msgs = optimized_results[i].get('messages', []) if i < len(optimized_results) else []
        
        baseline_usage = analyze_tool_usage(baseline_msgs)
        optimized_usage = analyze_tool_usage(optimized_msgs)
        
        baseline_first = baseline_usage['first_tool'] or "None"
        optimized_first = optimized_usage['first_tool'] or "None"
        
        # Track stats
        if baseline_first == 'rag_query':
            baseline_stats['rag_query_first'] += 1
        elif baseline_first == 'arxiv_search':
            baseline_stats['arxiv_search_first'] += 1
        
        if optimized_first == 'rag_query':
            optimized_stats['rag_query_first'] += 1
        elif optimized_first == 'arxiv_search':
            optimized_stats['arxiv_search_first'] += 1
        
        # Check intelligent choice
        baseline_intelligent, baseline_reason = is_intelligent_choice(query, baseline_first)
        optimized_intelligent, optimized_reason = is_intelligent_choice(query, optimized_first)
        
        if baseline_intelligent:
            baseline_stats['intelligent_choices'] += 1
        if optimized_intelligent:
            optimized_stats['intelligent_choices'] += 1
        
        # Determine improvement
        if optimized_intelligent and not baseline_intelligent:
            improvement = f"[green]✓ Learned intelligent choice[/green]"
        elif optimized_intelligent and baseline_intelligent:
            improvement = "[cyan]Both intelligent[/cyan]"
        elif not optimized_intelligent and baseline_intelligent:
            improvement = "[red]⚠ Regressed[/red]"
        else:
            improvement = "[yellow]No change[/yellow]"
        
        # Truncate query for display
        query_display = query[:37] + "..." if len(query) > 40 else query
        
        table.add_row(query_display, baseline_first, optimized_first, improvement)
    
    if verbose:
        console.print(table)
        console.print()
    
    # Summary statistics
    summary_table = Table(title="Behavior Summary", show_header=True, header_style="bold cyan")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Baseline", style="yellow")
    summary_table.add_column("Optimized", style="green")
    summary_table.add_column("Change", style="magenta")
    
    # Intelligent choices percentage
    baseline_int_pct = (baseline_stats['intelligent_choices'] / baseline_stats['total_queries'] * 100) if baseline_stats['total_queries'] > 0 else 0
    optimized_int_pct = (optimized_stats['intelligent_choices'] / optimized_stats['total_queries'] * 100) if optimized_stats['total_queries'] > 0 else 0
    int_change = optimized_int_pct - baseline_int_pct
    
    summary_table.add_row(
        "Intelligent Choices %",
        f"{baseline_int_pct:.1f}%",
        f"{optimized_int_pct:.1f}%",
        f"[green]{int_change:+.1f}%[/green]" if int_change > 0 else f"[red]{int_change:+.1f}%[/red]"
    )
    
    # rag_query first percentage (cost-effective)
    baseline_rag_pct = (baseline_stats['rag_query_first'] / baseline_stats['total_queries'] * 100) if baseline_stats['total_queries'] > 0 else 0
    optimized_rag_pct = (optimized_stats['rag_query_first'] / optimized_stats['total_queries'] * 100) if optimized_stats['total_queries'] > 0 else 0
    rag_change = optimized_rag_pct - baseline_rag_pct
    
    summary_table.add_row(
        "rag_query First % (Cost-effective)",
        f"{baseline_rag_pct:.1f}%",
        f"{optimized_rag_pct:.1f}%",
        f"[green]{rag_change:+.1f}%[/green]" if rag_change > 0 else f"[yellow]{rag_change:+.1f}%[/yellow]"
    )
    
    console.print(summary_table)
    console.print()
    
    # Key insights
    console.print("[bold]Key Insights:[/bold]")
    if optimized_int_pct > baseline_int_pct:
        console.print(f"  [green]✓[/green] Optimized prompt learned to make {int_change:.1f}% more intelligent tool choices")
    if optimized_rag_pct >= baseline_rag_pct:
        console.print(f"  [green]✓[/green] Still maintains cost-effectiveness ({optimized_rag_pct:.1f}% use rag_query first)")
    if optimized_int_pct > baseline_int_pct and optimized_rag_pct >= baseline_rag_pct * 0.9:
        console.print(f"  [green]✓[/green] Best of both worlds: More intelligent AND cost-effective!")
    
    console.print()

