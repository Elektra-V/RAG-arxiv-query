"""Training and validation datasets for APO."""

from __future__ import annotations

from typing import Dict, List


def load_training_dataset() -> List[Dict[str, any]]:
    """Return training dataset for APO."""
    return [
        {
            'query': 'What is quantum computing?',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['quantum', 'computing'],
            'quality_score': 0.9,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'Explain transformer architecture in deep learning',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['transformer', 'attention'],
            'quality_score': 0.9,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'How does reinforcement learning work?',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['reinforcement', 'learning', 'reward'],
            'quality_score': 0.9,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'What is the difference between supervised and unsupervised learning?',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['supervised', 'unsupervised'],
            'quality_score': 0.9,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'Explain gradient descent optimization',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['gradient', 'descent'],
            'quality_score': 0.85,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'How do convolutional neural networks process images?',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['convolutional', 'CNN', 'image'],
            'quality_score': 0.9,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'What is attention mechanism in neural networks?',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['attention', 'mechanism'],
            'quality_score': 0.9,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'Explain backpropagation algorithm',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['backpropagation', 'gradient'],
            'quality_score': 0.85,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'How does batch normalization improve training?',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['batch', 'normalization'],
            'quality_score': 0.85,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'What are the latest advances in large language models?',
            'expected_tool_usage': ['rag_query', 'arxiv_search'],
            'expected_output_contains': ['language model', 'LLM'],
            'quality_score': 0.85
        },
        {
            'query': 'Find papers on neural architecture search',
            'expected_tool_usage': ['rag_query', 'arxiv_search'],
            'expected_output_contains': ['neural', 'architecture'],
            'quality_score': 0.85
        },
        {
            'query': 'What are recent developments in computer vision?',
            'expected_tool_usage': ['rag_query', 'arxiv_search'],
            'expected_output_contains': ['vision', 'image'],
            'quality_score': 0.85
        },
        {
            'query': 'Search for papers on federated learning',
            'expected_tool_usage': ['rag_query', 'arxiv_search'],
            'expected_output_contains': ['federated'],
            'quality_score': 0.85
        },
        {
            'query': 'What are the applications of graph neural networks?',
            'expected_tool_usage': ['rag_query', 'arxiv_search'],
            'expected_output_contains': ['graph', 'neural network'],
            'quality_score': 0.85
        },
        {
            'query': 'What are the most recent papers on transformers published in 2024?',
            'expected_tool_usage': ['arxiv_search'],
            'expected_output_contains': ['transformer', '2024'],
            'quality_score': 0.9,
            'intelligent_choice': 'arxiv_search_first'
        },
        {
            'query': 'Find the latest research on large language models',
            'expected_tool_usage': ['arxiv_search'],
            'expected_output_contains': ['language model', 'LLM'],
            'quality_score': 0.9,
            'intelligent_choice': 'arxiv_search_first'
        },
        {
            'query': 'Search arXiv for papers on quantum computing',
            'expected_tool_usage': ['arxiv_search'],
            'expected_output_contains': ['quantum', 'computing'],
            'quality_score': 0.9,
            'intelligent_choice': 'arxiv_search_first'
        },
        {
            'query': 'What are new developments in neural architecture search?',
            'expected_tool_usage': ['arxiv_search'],
            'expected_output_contains': ['neural', 'architecture'],
            'quality_score': 0.85,
            'intelligent_choice': 'arxiv_search_first'
        },
        {
            'query': 'Find recent papers on few-shot learning',
            'expected_tool_usage': ['arxiv_search'],
            'expected_output_contains': ['few-shot', 'learning'],
            'quality_score': 0.85,
            'intelligent_choice': 'arxiv_search_first'
        },
        {
            'query': 'What are the newest papers on vision transformers?',
            'expected_tool_usage': ['arxiv_search'],
            'expected_output_contains': ['vision', 'transformer'],
            'quality_score': 0.85,
            'intelligent_choice': 'arxiv_search_first'
        }
    ]


def load_validation_dataset() -> List[Dict[str, any]]:
    """Return validation dataset for APO."""
    return [
        {
            'query': 'What is machine learning?',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['machine learning'],
            'quality_score': 0.9,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'Explain the concept of overfitting in machine learning',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['overfitting'],
            'quality_score': 0.9,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'What are the latest research papers on GPT models?',
            'expected_tool_usage': ['arxiv_search'],
            'expected_output_contains': ['GPT', 'language model'],
            'quality_score': 0.85,
            'intelligent_choice': 'arxiv_search_first'
        },
        {
            'query': 'How do variational autoencoders work?',
            'expected_tool_usage': ['rag_query'],
            'expected_output_contains': ['variational', 'autoencoder'],
            'quality_score': 0.85,
            'intelligent_choice': 'rag_query_first'
        },
        {
            'query': 'Search for papers on contrastive learning',
            'expected_tool_usage': ['arxiv_search'],
            'expected_output_contains': ['contrastive'],
            'quality_score': 0.85,
            'intelligent_choice': 'arxiv_search_first'
        }
    ]
