"""Training script for Automatic Prompt Optimization (APO).

This script evaluates prompt performance and can be used for manual prompt optimization.
Since Agent-lightning 0.1.2 uses a different API pattern, this provides a standalone
evaluation framework that can be extended with actual optimization algorithms.
"""

from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.table import Table

try:
    from agentlightning import Trainer, PromptTemplate
except ImportError as e:
    raise ImportError(
        "agentlightning is not installed. Install it with: uv add agentlightning"
    ) from e

from rag_api.services.langchain.apo_agent import rag_agent_rollout, rag_response_grader
from rag_api.services.langchain.apo_config import get_apo_config
from rag_api.services.langchain.apo_dataset import (
    load_training_dataset,
    load_validation_dataset,
)
from rag_api.services.langchain.prompt_template import (
    create_agentlightning_prompt_template,
    get_baseline_prompt_template,
)

logger = logging.getLogger(__name__)
console = Console()


def evaluate_prompt_performance(
    prompt_template: PromptTemplate,
    dataset: list[dict],
    dataset_name: str = "dataset",
) -> dict[str, float]:
    """Evaluate prompt performance on a dataset.
    
    Args:
        prompt_template: PromptTemplate to evaluate
        dataset: List of task dicts
        dataset_name: Name of the dataset for logging
        
    Returns:
        Dict with performance metrics
    """
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
    
    return {
        'average': avg_score,
        'min': min_score,
        'max': max_score,
        'scores': scores
    }


def display_comparison(
    baseline_metrics: dict[str, float],
    optimized_metrics: dict[str, float],
) -> None:
    """Display comparison table of baseline vs optimized performance.
    
    Args:
        baseline_metrics: Performance metrics for baseline prompt
        optimized_metrics: Performance metrics for optimized prompt
    """
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
    """Save optimized prompt to file.
    
    Args:
        prompt_template: Optimized PromptTemplate
        output_path: Path to save the prompt
    """
    prompt_text = prompt_template.template if hasattr(prompt_template, 'template') else str(prompt_template)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_text, encoding='utf-8')
    
    console.print(f"\n[green]✓[/green] Optimized prompt saved to: {output_path}")


def main() -> None:
    """Main training function.
    
    This script evaluates the baseline prompt performance.
    For full APO integration, you would need to:
    1. Subclass LitAgent from agentlightning
    2. Implement training_rollout method
    3. Use Trainer with the LitAgent instance
    """
    console.print("[bold blue]RAG Agent Prompt Evaluation[/bold blue]\n")
    console.print("[yellow]Note:[/yellow] This script evaluates prompt performance.")
    console.print("[yellow]For full APO, integrate with Agent-lightning's LitAgent pattern.[/yellow]\n")
    
    # Load configuration
    config = get_apo_config()
    console.print(f"[cyan]Configuration:[/cyan]")
    console.print(f"  Training samples: {len(load_training_dataset())}")
    console.print(f"  Validation samples: {len(load_validation_dataset())}")
    console.print()
    
    # Load datasets
    console.print("[bold]Loading datasets...[/bold]")
    train_dataset = load_training_dataset()
    val_dataset = load_validation_dataset()
    console.print(f"  Training samples: {len(train_dataset)}")
    console.print(f"  Validation samples: {len(val_dataset)}")
    console.print()
    
    # Create baseline prompt template
    console.print("[bold]Creating baseline prompt template...[/bold]")
    baseline_prompt = get_baseline_prompt_template()
    baseline_template = PromptTemplate(template=baseline_prompt, engine='f-string')
    console.print("[green]✓[/green] Baseline prompt created")
    console.print()
    
    # Evaluate baseline performance
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    console.print("[bold yellow]BASELINE EVALUATION[/bold yellow]")
    console.print("[bold yellow]" + "=" * 50 + "[/bold yellow]")
    
    baseline_train_metrics = evaluate_prompt_performance(
        baseline_template, train_dataset, "training set"
    )
    baseline_val_metrics = evaluate_prompt_performance(
        baseline_template, val_dataset, "validation set"
    )
    
    console.print(f"\n[bold]Baseline Training Performance:[/bold]")
    console.print(f"  Average: {baseline_train_metrics['average']:.3f}")
    console.print(f"  Min: {baseline_train_metrics['min']:.3f}")
    console.print(f"  Max: {baseline_train_metrics['max']:.3f}")
    
    console.print(f"\n[bold]Baseline Validation Performance:[/bold]")
    console.print(f"  Average: {baseline_val_metrics['average']:.3f}")
    console.print(f"  Min: {baseline_val_metrics['min']:.3f}")
    console.print(f"  Max: {baseline_val_metrics['max']:.3f}")
    console.print()
    
    # Save baseline for reference
    baseline_path = Path("baseline_prompt.txt")
    save_optimized_prompt(baseline_template, baseline_path)
    
    console.print("\n[bold green]Evaluation complete![/bold green]")
    console.print(f"\n[bold]Next Steps for Full APO:[/bold]")
    console.print("1. Review baseline performance metrics")
    console.print("2. Manually optimize prompt based on low-scoring tasks")
    console.print("3. Re-run evaluation to compare")
    console.print("4. For automated optimization, integrate with Agent-lightning's LitAgent pattern")
    console.print(f"\nBaseline prompt saved to: {baseline_path.absolute()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
