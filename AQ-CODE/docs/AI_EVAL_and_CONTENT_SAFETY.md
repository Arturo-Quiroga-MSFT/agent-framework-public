
Based on the documentation, here's the relationship between these two libraries:

## Relationship: Azure AI Evaluation Uses Azure AI Content Safety

**Azure AI Content Safety** (`azure-ai-contentsafety`) is the **foundational service library** that provides:
- Text Analysis API (sexual content, violence, hate, self-harm detection)
- Image Analysis API (same categories for images)
- Blocklist management for custom term screening
- Direct API access via `ContentSafetyClient`

**Azure AI Evaluation** (`azure-ai-evaluation`) is a **higher-level SDK for evaluating AI/LLM outputs** that:
- Provides evaluator classes like `RelevanceEvaluator`, `ViolenceEvaluator`, `GroundednessEvaluator`, etc.
- Includes simulators for generating synthetic test data (including adversarial scenarios)
- Orchestrates evaluations across datasets using the `evaluate()` function

### The Key Connection

The content safety evaluators in `azure-ai-evaluation` (like `ViolenceEvaluator`) **call the Azure AI Content Safety service under the hood**. Notice in the evaluation example:

```python
# Content Safety Evaluator requires an Azure AI project scope
azure_ai_project = {
    "subscription_id": ...,
    "resource_group_name": ...,
    "project_name": ...
}
violence_eval = ViolenceEvaluator(azure_ai_project)
```

This connects to the Content Safety service via your Azure AI project.

### When to Use Which

| Use Case | Library |
|----------|---------|
| Direct content moderation in your app (real-time) | `azure-ai-contentsafety` |
| Evaluating LLM outputs for quality & safety | `azure-ai-evaluation` |
| Custom blocklists & fine-grained control | `azure-ai-contentsafety` |
| Running batch evaluations on datasets | `azure-ai-evaluation` |
| Adversarial testing & red-teaming | `azure-ai-evaluation` (simulators) |

In short: **Azure AI Evaluation builds on top of Azure AI Content Safety** for its safety-related evaluators, while adding LLM-specific quality evaluators (relevance, groundedness, coherence) and testing infrastructure.