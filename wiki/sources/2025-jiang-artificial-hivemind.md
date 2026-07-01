---
title: "Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond)"
authors: Jiang, Chai, Li, Liu, Fok, Dziri, Tsvetkov, Sap, Albalak, Choi
year: 2025
url: https://arxiv.org/abs/2510.22954
doi: 10.48550/arXiv.2510.22954
source_type: paper
publication_status: peer-reviewed
retrieved: 2026-07-01
drive_file_id: 1ryqKW35C16vk_AQIj_9LcT84aYXbPSzV
file_hash: 2bccd95fd2e679b1d087568420729280336a9a6ca666eda9d3f18695543bb7ff
---

# Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond)

**Citation.** Jiang, L., Chai, Y., Li, M., Liu, M., Fok, R., Dziri, N., Tsvetkov, Y., Sap, M., Albalak, A., & Choi, Y. (2025). *Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond).* NeurIPS 2025. arXiv. https://arxiv.org/abs/2510.22954

**Summary.** Jiang and colleagues introduce INFINITY-CHAT, a dataset of 26,000 real-world open-ended user queries with a taxonomy of six top-level and 17 lower-level query categories. Using the dataset, they show an Artificial Hivemind effect: language models often repeat similar outputs within a model and converge on similar outputs across different models, especially in open-ended generation where many answers could be plausible. The paper also adds 31,250 human annotations and shows that language models, reward models, and LM judges are less calibrated to human ratings when annotators have idiosyncratic preferences, making the source useful for separating apparent output quality from pluralism, diversity, and human-specific value.

## Key claims
- INFINITY-CHAT contains 26,000 naturally occurring open-ended user queries, organized into a taxonomy with six top-level categories and 17 subcategories, to evaluate language-model behavior beyond narrow tasks with a single ground truth.
- The Artificial Hivemind effect appears in both intra-model repetition, where one model repeatedly produces similar responses, and inter-model homogeneity, where different model families generate strikingly similar responses to the same open-ended query.
- The paper's motivating example shows 25 models generating 50 responses each to “Write a metaphor about time,” with responses clustering primarily around “time is a river” and “time is a weaver” despite model and sampling diversity.
- Dense human annotation in INFINITY-CHAT includes 31,250 annotations, with 25 independent human annotations per example across absolute ratings and pairwise preferences, allowing the authors to examine collective and individual-specific preferences rather than only aggregate quality.
- State-of-the-art language models, reward models, and LM judges are less well calibrated to human ratings on generations that elicit divergent idiosyncratic annotator preferences, even when those responses have comparable overall quality.
- The paper argues that existing pluralistic-alignment work often relies on predefined diversity dimensions, while open-ended generation requires attention to individual-level variation that may not be captured by demographic, personality, or cultural categories.

## Evidence & limitations
- Evidence comes from a NeurIPS 2025 paper using the INFINITY-CHAT dataset, large-scale model generation, embedding-based similarity analyses, and human preference/quality annotation across open-ended prompts.
- The source is strongest as benchmark and diagnostic evidence about output homogeneity, mode collapse, and evaluation miscalibration in open-ended language-model tasks; it is not direct evidence about workplace deployment, job redesign, or employee outcomes.
- The Drive PDF exactly matched the public arXiv PDF by SHA-256, supporting arXiv as public provenance; the arXiv API was rate-limited during ingest, so title, authors, venue, date, abstract, and version were verified from the PDF and arXiv landing/PDF access rather than the API feed.
- Prompt-injection scan found no model-directed instructions to the ingesting agent; hits for “system prompt,” “AI assistant,” and “language model” were ordinary paper content, methods language, or references.

## Feeds
- [[ai-output-diversity]]
- [[ai-supported-knowledge-synthesis]]
- [[ai-mediated-choice-and-identity]]
