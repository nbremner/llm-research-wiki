---
title: "On Automated and Explainable Provenance of AI-Generated Code"
authors: Velasco, Alejandro; Wintersgill, Nathan; Stalnaker, Trevor; Chaparro, Oscar; Poshyvanyk, Denys
year: 2026
url: https://arxiv.org/abs/2608.02329
doi: 10.48550/arXiv.2608.02329
source_type: paper
publication_status: preprint
retrieved: 2026-09-22
human_reviewed: false
drive_file_id: 15D4Ft6bb2IaW3X3uIcBiAykYVb-4eVc5
file_hash: 3bd2aac57e2f9f29ca04734c6f0461f3ab680206cab42f3745683b69e657b351
---

# On Automated and Explainable Provenance of AI-Generated Code

**Citation.** Velasco, A., Wintersgill, N., Stalnaker, T., Chaparro, O., & Poshyvanyk, D. (2026). *On Automated and Explainable Provenance of AI-Generated Code* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2608.02329

**Summary.** This research vision proposes explainable provenance for AI-generated code: automated, post-hoc traceability from an output to contributing prompt components, training instances, corpus-level features, and model components. It frames provenance as needed by model developers, software practitioners, and compliance professionals, then outlines stakeholder research and technical approaches to make the resulting evidence actionable. The paper is a grant-grounded agenda rather than an evaluation of a completed end-to-end provenance system.

## Key claims
- A prior survey cited by the authors found that 89.7% of 574 software developers regularly use CodeGenAI tools, while 70.1% lack or do not have processes to document their use, creating traceability gaps.
- Explainable provenance has four proposed dimensions: prompt-to-output, instance-to-output, factor-to-output, and model-component-to-output traceability.
- Existing filtering, clone-detection, retrieval, and source-link approaches can flag or retrieve possible problems but do not provide an actionable causal explanation of why a particular generated output occurred.
- The proposed program combines stakeholder surveys and interviews with post-hoc techniques including prompt attribution, retrieval and membership inference, causal analysis of training-data factors, and model-internal interpretability methods.
- Provenance evidence for black-box models remains limited because inaccessible training data and uncertain ground truth make definitive attribution difficult; legal usefulness also requires interpretation beyond similarity scores or probabilistic inference.

## Evidence & limitations
- This six-page arXiv research vision synthesizes prior empirical studies and proposes future surveys, interviews, and technical development; it does not report a completed validation of the integrated framework.
- The reported developer-use and documentation figures are attributed to the authors' earlier survey, while other stakeholder findings are summarized from prior work rather than reanalyzed in this paper.
- The source is an arXiv v1 preprint dated 2026-08-03; no matching publisher DOI was found in the paper or by exact-title Crossref lookup.

## Feeds
- [[human-ai-agent-interaction-design]]
- [[responsible-ai-deployment]]
