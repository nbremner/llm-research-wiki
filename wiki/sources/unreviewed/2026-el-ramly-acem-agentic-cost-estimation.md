---
title: "ACEM: A Cost Estimation Model for Agentic Software Engineering"
authors: El-Ramly, Mohammad
year: 2026
url: https://arxiv.org/abs/2608.02582
doi: 10.48550/arXiv.2608.02582
source_type: paper
publication_status: preprint
retrieved: 2026-09-19
human_reviewed: false
drive_file_id: 1u5GYwnsI7sGCVNjIk58ADYBuSgd-KDKs
file_hash: 4ac8f9d06a23331fa33703498ceeadc41547e779a81684dcc4e89ba231ab5a1e
---

# ACEM: A Cost Estimation Model for Agentic Software Engineering

**Citation.** El-Ramly, M. (2026). *ACEM: A Cost Estimation Model for Agentic Software Engineering*. arXiv:2608.02582. https://doi.org/10.48550/arXiv.2608.02582

**Summary.** This preprint proposes ACEM, a cost-estimation framework for software-development workflows in which autonomous agents perform substantial implementation work while humans plan, specify, validate, and correct outputs. The framework represents total cost as LLM token consumption, human-in-the-loop (HITL) effort, and infrastructure cost, and proposes calibration methods rather than reporting validated project estimates. It maps familiar software-sizing measures to estimated token consumption and models retry overhead, context growth, and oversight intensity as agentic-work cost drivers.

## Key claims
- ACEM treats LLM token cost, HITL oversight and correction, and orchestration/tooling infrastructure as distinct additive dimensions of agentic software-development cost.
- The proposed Revision Factor represents token overhead from rejected outputs and retries, while the Context Factor represents growing token use as an agent's context accumulates.
- The proposed four-level HITL Intensity Score classifies the degree of human oversight required for a task, making review and correction effort visible in cost estimation.
- ACEM maps Use Case Points, Story Points, and Function Points to estimated token consumption so organizations can connect existing project-scoping data to agentic-work forecasts.

## Evidence & limitations
- This is a theoretical preprint with a specified model structure and calibration methodology, not an empirical validation against real project data; its constants remain symbolic pending calibration.
- The author identifies non-deterministic agent paths, retries, and varying correction needs as sources of cost variance, but does not test how accurately the proposed factors forecast deployed projects.
- The Drive PDF exactly matches the public arXiv v1 PDF by SHA-256; the arXiv API returned HTTP 406 during metadata lookup, so public provenance was verified through the stable arXiv record/PDF and exact binary match.

## Feeds
- [[agentic-delegation]]
- [[human-ai-task-allocation]]
