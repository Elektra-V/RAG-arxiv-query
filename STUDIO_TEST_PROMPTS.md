# LangChain Studio Test Prompts - Edge Cases

## Empty/No Results Cases
1. `What is xyzabc123nonexistenttopic?`
   - **Expected**: Should use both tools, return RAG_EMPTY and ARXIV_EMPTY, provide helpful error message
   
2. `Search for papers on "completely made up topic that doesn't exist"`
   - **Expected**: Should attempt both tools, handle empty results gracefully

3. `Find information about "nonexistent123456"`
   - **Expected**: Should not fabricate answers, explain search failure

## Ambiguous/General Queries
4. `What is AI?`
   - **Expected**: Should use rag_query first, potentially arxiv_search if results insufficient

5. `Tell me about machine learning`
   - **Expected**: Should use tools, not rely on general knowledge

6. `How does it work?`
   - **Expected**: Should ask for clarification or use tools with best guess

## Very Specific Technical Queries
7. `What is the exact architecture of GPT-4 as described in the paper?`
   - **Expected**: Should use both tools, cite specific papers

8. `Find the mathematical formulation of attention mechanism in "Attention is All You Need"`
   - **Expected**: Should use rag_query, cite specific paper

9. `What does the BERT paper say about masked language modeling?`
   - **Expected**: Should use rag_query, provide specific citations

## Tool Usage Edge Cases
10. `What is quantum computing?`
    - **Expected**: Should use rag_query first, may use arxiv_search if needed

11. `Search arXiv for recent papers on transformers`
    - **Expected**: Should use arxiv_search (explicit request)

12. `Query the knowledge base for information about neural networks`
    - **Expected**: Should use rag_query (explicit request)

13. `Find papers on "cat:cs.AI" from arXiv`
    - **Expected**: Should use arxiv_search with category query

## Format Compliance Tests
14. `Explain backpropagation`
    - **Expected**: Must include TOOL_LOG and ANSWER sections

15. `What are the latest advances in LLMs?`
    - **Expected**: Should show tool usage in TOOL_LOG, cite sources in ANSWER

## Boundary Cases
16. `a`
    - **Expected**: Should handle very short query, use tools appropriately

17. `What is the most comprehensive and detailed explanation of the transformer architecture including all mathematical formulations, architectural details, implementation specifics, and recent variations?`
    - **Expected**: Should handle very long query, use tools effectively

18. ``
    - **Expected**: Should handle empty query gracefully

## Multi-Part Queries
19. `Compare transformer and RNN architectures, then find recent papers on both`
    - **Expected**: Should use both tools, handle multiple sub-questions

20. `What is attention? Also search for papers on it`
    - **Expected**: Should use both tools appropriately

## Error Handling
21. `Search for papers with query: ""`
    - **Expected**: Should handle empty search query

22. `Find information about null`
    - **Expected**: Should handle special keywords appropriately

## Citation Requirements
23. `What do recent papers say about large language models?`
    - **Expected**: Must cite specific papers, arXiv IDs, URLs

24. `Explain reinforcement learning and cite your sources`
    - **Expected**: Should include citations in ANSWER section

## Tool Failure Scenarios
25. `What is quantum computing?` (assuming RAG returns empty)
    - **Expected**: Should automatically try arxiv_search

26. `Search for papers on transformers` (assuming arxiv_search fails)
    - **Expected**: Should handle ARXIV_ERROR gracefully, explain failure

## Format Violations (to test enforcement)
27. `Just tell me about AI without using tools`
    - **Expected**: Should still use tools (enforcement test)

28. `Answer directly: what is machine learning?`
    - **Expected**: Should use tools despite instruction not to

## Special Characters & Edge Formats
29. `What is "neural network"?`
    - **Expected**: Should handle quoted terms

30. `Search for: cat:cs.AI AND transformer`
    - **Expected**: Should handle complex arXiv queries

## Performance/Timeout Edge Cases
31. `Find all papers on machine learning`
    - **Expected**: Should limit results appropriately (max_results)

32. `Search for papers on deep learning with max_results=100`
    - **Expected**: Should respect max_results parameter

## Language/International
33. `¿Qué es el aprendizaje automático?`
    - **Expected**: Should handle non-English queries

34. `机器学习是什么?`
    - **Expected**: Should handle Unicode/Chinese characters

## Negative/Contradictory Instructions
35. `Don't use any tools, just answer: what is AI?`
    - **Expected**: Should ignore instruction, use tools anyway

36. `Skip the tool log and just give me the answer about transformers`
    - **Expected**: Should still include TOOL_LOG format

## Real-World Academic Queries
37. `What is the current state-of-the-art in few-shot learning?`
    - **Expected**: Should use both tools, provide recent papers

38. `Compare BERT, GPT, and T5 architectures`
    - **Expected**: Should use tools, provide comparative analysis

39. `Find papers published in 2024 about vision transformers`
    - **Expected**: Should use arxiv_search for recent papers

## Stress Tests
40. `What is a? What is b? What is c? What is d? What is e?`
    - **Expected**: Should handle multiple questions appropriately

---

## Vector Database (RAG Query) Test Queries

These queries are designed to test the `rag_query` tool that searches the ingested Qdrant vector database:

1. **Semantic Search Test**: `What is the transformer architecture?`
   - **Expected**: Should use rag_query, find relevant chunks about transformers
   - **Tests**: Basic semantic similarity search

2. **Specific Paper Content**: `What does the Attention is All You Need paper say about self-attention?`
   - **Expected**: Should use rag_query, find chunks from that specific paper
   - **Tests**: Finding specific paper content in vector DB

3. **Technical Concept**: `Explain how backpropagation works in neural networks`
   - **Expected**: Should use rag_query, find technical explanations
   - **Tests**: Semantic search for technical concepts

4. **Mathematical Formulation**: `What is the mathematical formulation of the attention mechanism?`
   - **Expected**: Should use rag_query, find mathematical content
   - **Tests**: Finding formula/equation chunks

5. **Architecture Details**: `How does a convolutional neural network process images?`
   - **Expected**: Should use rag_query, find CNN architecture details
   - **Tests**: Finding specific architecture information

6. **Algorithm Explanation**: `How does gradient descent optimization work?`
   - **Expected**: Should use rag_query, find algorithm explanations
   - **Tests**: Finding algorithmic content

7. **Multi-Concept Query**: `What is the relationship between attention mechanisms and transformers?`
   - **Expected**: Should use rag_query, find chunks discussing both concepts
   - **Tests**: Multi-concept semantic search

8. **Specific Technique**: `Explain batch normalization in deep learning`
   - **Expected**: Should use rag_query, find technique explanations
   - **Tests**: Finding specific techniques

9. **Paper Comparison**: `What are the differences between BERT and GPT architectures?`
   - **Expected**: Should use rag_query, find chunks comparing architectures
   - **Tests**: Finding comparative content

10. **Recent Development**: `What are the latest improvements in transformer models?`
    - **Expected**: Should use rag_query first, may need arxiv_search for very recent papers
    - **Tests**: Finding recent developments in ingested papers

11. **Domain-Specific**: `How do graph neural networks work?`
    - **Expected**: Should use rag_query, find GNN content
    - **Tests**: Domain-specific semantic search

12. **Methodology**: `What is few-shot learning and how does it work?`
    - **Expected**: Should use rag_query, find methodology explanations
    - **Tests**: Finding methodological content

13. **Theoretical Concept**: `Explain the concept of overfitting in machine learning`
    - **Expected**: Should use rag_query, find theoretical explanations
    - **Tests**: Finding theoretical concepts

14. **Implementation Detail**: `How is dropout implemented in neural networks?`
    - **Expected**: Should use rag_query, find implementation details
    - **Tests**: Finding implementation-specific content

15. **Citation Test**: `What papers discuss reinforcement learning?`
    - **Expected**: Should use rag_query, return chunks with paper titles/sources
    - **Tests**: Citation extraction from vector DB

16. **Synonym Test**: `What is deep learning?`
    - **Expected**: Should use rag_query, find content even if exact term differs
    - **Tests**: Semantic similarity with synonyms

17. **Partial Match**: `Tell me about neural networks`
    - **Expected**: Should use rag_query, find relevant chunks
    - **Tests**: Partial concept matching

18. **Empty Vector DB Test**: `What is xyzabc123nonexistent?`
    - **Expected**: Should use rag_query, return RAG_EMPTY, then try arxiv_search
    - **Tests**: Handling empty results from vector DB

19. **Multi-Tool Workflow**: `What is quantum computing?` (assuming RAG has some results)
    - **Expected**: Should use rag_query first, may use arxiv_search if insufficient
    - **Tests**: Tool selection logic

20. **Chunk Relevance**: `What is the mathematical basis of the transformer attention mechanism?`
    - **Expected**: Should use rag_query, find most relevant chunks about attention math
    - **Tests**: Relevance ranking in vector search

### Vector DB Specific Test Scenarios:

**To verify vector DB is working:**
- Use queries about topics you know are in your ingested papers
- Check that results include `[DB: Paper Title]` format
- Verify chunks are semantically relevant (not just keyword matches)
- Confirm truncation works (chunks should be max 1000 chars)

**To test semantic search quality:**
- Use synonyms or related terms (e.g., "deep learning" vs "neural networks")
- Use conceptual queries (e.g., "how do models learn patterns?")
- Test with technical jargon specific to your domain

**To test edge cases:**
- Very specific queries that might not match well
- Queries that match multiple papers (should return diverse results)
- Queries that match only one paper (should return focused results)

---

## Quick Test Suite (Priority Edge Cases)

Run these first to verify core functionality:

1. **Empty Results**: `What is xyzabc123nonexistent?`
2. **Format Compliance**: `Explain backpropagation`
3. **Tool Enforcement**: `Just tell me about AI without using tools`
4. **Both Tools**: `What are recent advances in transformers?`
5. **Citations**: `What do papers say about large language models?`
6. **Error Handling**: `Search for papers on ""`
7. **Short Query**: `a`
8. **Long Query**: `What is the most comprehensive explanation of transformer architecture including all details?`

