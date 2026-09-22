---
title: "The Role Specialization Model (RSM): Coordinating LLM-Based Tools in Agentic Software Development - An Exploratory Case Study"
authors: Fernández-y-Fernández, Carlos Alberto; Aguilar-Cisneros, Jorge R.
year: 2026
url: https://arxiv.org/abs/2608.12311
doi: 10.48550/arXiv.2608.12311
source_type: paper
publication_status: preprint
retrieved: 2026-09-22
human_reviewed: false
drive_file_id: 1ki1lfEMeXQUVXZHP58ILabk1F6k8XL5F
file_hash: 098b13d34f2789315612cdb8bfe2d9916d0da727a5ebe9bcacb51c2a2468f02f
---

# The Role Specialization Model (RSM): Coordinating LLM-Based Tools in Agentic Software Development - An Exploratory Case Study

**Citation.** Fernández-y-Fernández, C. A. & Aguilar-Cisneros, J. R. (2026). *The Role Specialization Model (RSM): Coordinating LLM-Based Tools in Agentic Software Development - An Exploratory Case Study.* arXiv:2608.12311.

**Summary.** This exploratory single-case study proposes the Role Specialization Model (RSM), which assigns Architect, Analyst, and Specialist responsibilities to Antigravity, Gemini CLI, and Qwen Code in a Python climate-data-visualization project. The observed workflow found that functional overlap and context-switching costs shifted a planned refactoring task from Qwen Code to Gemini CLI, leaving the human developer responsible for coordination and approval. The authors report qualitative ISO/IEC 25010 assessments and argue that explicit role boundaries, prompt hardening, context management, and human verification remain necessary in multi-tool agentic development.

## Key claims
- In the reported case, role specialization coordinated complementary tool contributions, but absent scope boundaries, overlapping tool capabilities, and context-switching costs produced role drift that the human orchestrator had to manage.
- Antigravity produced six initial project files from a natural-language prompt, Gemini CLI generated data, performed architectural analysis and documentation work, and Qwen Code produced date validation and ten passing unit tests.
- The qualitative quality assessment judged functional suitability, maintainability, and flexibility high, while runtime-environment fragility limited reliability; the authors caution that the assessment is indicative rather than quantitative.
- Explicit negative constraints were required after Gemini CLI twice attempted unavailable internal-tool actions while generating a test dataset, and the authors frame prompt hardening and sandboxing as safeguards for agentic environments with tool access.
- The authors propose that a dedicated evaluator agent could reduce human orchestration load only if its known evaluation biases are mitigated through rubric design and calibration.

## Evidence & limitations
- Exploratory qualitative case study of one developer, one Python desktop application, and one tool configuration; the researcher who performed development also analyzed the case.
- Two of the three tools used Gemini backends, limiting ensemble diversity, and the workflow was executed once; results cannot establish generalizable effects across projects, developers, or toolsets.
- The ISO/IEC 25010 assessment was a first-author qualitative expert judgment rather than quantitative or tool-supported measurement.
- Public provenance was verified through the arXiv record and an exact SHA-256 match between the downloaded arXiv PDF and the ingested Drive PDF.

## Feeds
- [[agentic-organization-design]]
- [[human-ai-agent-interaction-design]]
