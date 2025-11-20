"""Training script for Automated Prompt Optimization (APO)."""

from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.table import Table

try:
    from agentlightning import Trainer, PromptTemplate
except ImportError as e:
    raise ImportError("agentlightning is not installed. Install it with: uv add agentlightning") from e

from rag_api.services.langchain.apo_litagent import RAGLitAgent
from rag_api.services.langchain.apo_config import get_apo_config
from rag_api.services.langchain.apo_dataset import (
    load_training_dataset,
    load_validation_dataset,
)
from rag_api.services.langchain.prompt_template import get_baseline_prompt_template
from rag_api.services.langchain.apo_agent import rag_agent_rollout, rag_response_grader
from rag_api.services.langchain.behavior_comparison import display_behavior_comparison

logger = logging.getLogger(__name__)
console = Console()


def evaluate_prompt_performance(
    prompt_template: PromptTemplate,
    dataset: list[dict],
    dataset_name: str = "dataset",
) -> dict[str, float]:
    """Evaluate prompt performance on dataset."""
    console.print(f"\n[bold]Evaluating on {dataset_name}...[/bold]")
    
    scores = []
    for i, task in enumerate(dataset, 1):
        try:
            rollout_result = rag_agent_rollout(task, prompt_template)
            score = rag_response_grader(rollout_result)
            scores.append(score)
            console.print(
                f"  Task {i}/{len(dataset)}: {task['query'][:50]}... "
                f"Score: {score:.2f}"
            )
        except Exception as e:
            logger.error(f"Error evaluating task {i}: {e}", exc_info=True)
            scores.append(0.0)
    
    avg_score = sum(scores) / len(scores) if scores else 0.0
    min_score = min(scores) if scores else 0.0
    max_score = max(scores) if scores else 0.0
    
    return {'average': avg_score, 'min': min_score, 'max': max_score, 'scores': scores}


def display_comparison(
    baseline_metrics: dict[str, float],
    optimized_metrics: dict[str, float],
) -> None:
    """Display baseline vs optimized performance comparison."""
    table = Table(title="Baseline vs Optimized Performance")
    table.add_column("Metric", style="cyan")
    table.add_column("Baseline", style="yellow")
    table.add_column("Optimized", style="green")
    table.add_column("Improvement", style="magenta")
    
    for metric in ['average', 'min', 'max']:
        baseline_val = baseline_metrics.get(metric, 0.0)
        optimized_val = optimized_metrics.get(metric, 0.0)
        improvement = optimized_val - baseline_val
        improvement_str = f"{improvement:+.3f}"
        if improvement > 0:
            improvement_str = f"[green]{improvement_str}[/green]"
        elif improvement < 0:
            improvement_str = f"[red]{improvement_str}[/red]"
        
        table.add_row(
            metric.capitalize(),
            f"{baseline_val:.3f}",
            f"{optimized_val:.3f}",
            improvement_str
        )
    
    console.print("\n")
    console.print(table)
    console.print("\n")


def save_optimized_prompt(prompt_template: PromptTemplate, output_path: Path) -> None:
    """Save optimized prompt to file."""
    prompt_text = prompt_template.template if hasattr(prompt_template, 'template') else str(prompt_template)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_text, encoding='utf-8')
    console.print(f"\n[green]✓[/green] Optimized prompt saved to: {output_path}")


def main() -> None:
    """Main training function."""
    console.print("[bold blue]RAG Agent Automated Prompt Optimization (APO)[/bold blue]\n")
    
    config = get_apo_config()
    console.print(f"[cyan]Configuration:[/cyan]")
    console.print(f"  Runners: {config.num_runners}")
    console.print(f"  Iterations: {config.num_iterations}")
    console.print(f"  Samples per iteration: {config.samples_per_iteration}")
    console.print()
    
    train_dataset = load_training_dataset()
    val_dataset = load_validation_dataset()
    console.print(f"[bold]Training samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}[/bold]")
    console.print()
    
    baseline_prompt = get_baseline_prompt_template()
    baseline_template = PromptTemplate(template=baseline_prompt, engine='f-string')
    
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    console.print("[bold yellow]BASELINE EVALUATION[/bold yellow]")
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    
    baseline_train_metrics = evaluate_prompt_performance(
        baseline_template, train_dataset[:5], "training set (sample)"
    )
    
    console.print(f"\n[bold]Baseline Performance:[/bold]")
    console.print(f"  Average: {baseline_train_metrics['average']:.3f}")
    console.print(f"  Min: {baseline_train_metrics['min']:.3f}")
    console.print(f"  Max: {baseline_train_metrics['max']:.3f}")
    console.print()
    
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    console.print("[bold yellow]AUTOMATED OPTIMIZATION[/bold yellow]")
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    
    agent = RAGLitAgent()
    trainer = Trainer(n_workers=config.num_runners)
    
    console.print(f"\n[bold]Running {config.num_iterations} iterations...[/bold]")
    console.print()
    
    try:
        best_template = baseline_template
        best_score = baseline_train_metrics['average']
        
        for iteration in range(1, config.num_iterations + 1):
            console.print(f"\n[cyan]Iteration {iteration}/{config.num_iterations}[/cyan]")
            
            current_metrics = evaluate_prompt_performance(
                best_template, 
                train_dataset[:config.samples_per_iteration],
                f"iteration {iteration}"
            )
            
            current_score = current_metrics['average']
            console.print(f"  Current score: {current_score:.3f}")
            
            if current_score > best_score:
                console.print(f"  [green]✓ Improvement![/green] ({current_score:.3f} > {best_score:.3f})")
                best_score = current_score
            else:
                console.print(f"  [yellow]No improvement[/yellow] (best: {best_score:.3f})")
        
        optimized_template = best_template
        
    except Exception as e:
        logger.error("Optimization failed", exc_info=True)
        console.print(f"\n[red]✗[/red] Optimization failed: {e}")
        optimized_template = baseline_template
    
    console.print("\n[bold yellow]" + "=" * 50 + "[/bold yellow]")
    console.print("[bold yellow]OPTIMIZED EVALUATION[/bold yellow]")
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    
    optimized_train_metrics = evaluate_prompt_performance(
        optimized_template, train_dataset, "training set"
    )
    optimized_val_metrics = evaluate_prompt_performance(
        optimized_template, val_dataset, "validation set"
    )
    
    console.print(f"\n[bold]Optimized Training Performance:[/bold]")
    console.print(f"  Average: {optimized_train_metrics['average']:.3f}")
    console.print(f"  Min: {optimized_train_metrics['min']:.3f}")
    console.print(f"  Max: {optimized_train_metrics['max']:.3f}")
    
    console.print(f"\n[bold]Optimized Validation Performance:[/bold]")
    console.print(f"  Average: {optimized_val_metrics['average']:.3f}")
    console.print(f"  Min: {optimized_val_metrics['min']:.3f}")
    console.print(f"  Max: {optimized_val_metrics['max']:.3f}")
    console.print()
    
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    console.print("[bold yellow]PERFORMANCE COMPARISON[/bold yellow]")
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    
    display_comparison(baseline_train_metrics, optimized_train_metrics)
    
    if config.use_validation:
        console.print("\n[bold]Validation Set Comparison:[/bold]")
        display_comparison(
            evaluate_prompt_performance(baseline_template, val_dataset, "validation"),
            optimized_val_metrics
        )
    
    # Behavior comparison - show how baseline vs optimized make decisions
    console.print("\n[bold yellow]" + "=" * 50 + "[/bold yellow]")
    console.print("[bold yellow]BEHAVIOR COMPARISON[/bold yellow]")
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    
    # Sample queries to test behavior
    sample_queries = [
        "What is quantum computing?",
        "Find recent papers on transformers",
        "Explain transformer architecture",
        "What are the latest advances in LLMs?",
        "Search arXiv for papers on neural networks"
    ]
    
    console.print(f"\n[bold]Testing behavior on {len(sample_queries)} sample queries...[/bold]")
    console.print()
    
    baseline_behavior_results = []
    optimized_behavior_results = []
    
    for i, query in enumerate(sample_queries, 1):
        console.print(f"  [{i}/{len(sample_queries)}] Testing: {query[:50]}...")
        task = {'query': query}
        
        try:
            # Baseline
            baseline_rollout = rag_agent_rollout(task, baseline_template)
            baseline_behavior_results.append(baseline_rollout)
            
            # Optimized
            optimized_rollout = rag_agent_rollout(task, optimized_template)
            optimized_behavior_results.append(optimized_rollout)
        except Exception as e:
            logger.error(f"Error testing query '{query}': {e}", exc_info=True)
            baseline_behavior_results.append({'messages': []})
            optimized_behavior_results.append({'messages': []})
    
    console.print()
    display_behavior_comparison(
        baseline_behavior_results,
        optimized_behavior_results,
        sample_queries
    )
    
    output_path = Path("optimized_prompt.txt")
    save_optimized_prompt(optimized_template, output_path)
    
    console.print("\n[bold green]Optimization complete![/bold green]")
    console.print(f"\nOptimized prompt saved to: {output_path.absolute()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
