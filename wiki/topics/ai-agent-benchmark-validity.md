---
title: AI agent benchmark validity
status: active
updated: 2026-06-23
---

# AI agent benchmark validity

AI agent benchmark validity is the question of whether agent evaluations actually measure capabilities that matter for real work. The construct is not just model score; it is the evidence chain from benchmark task, to work activity, to domain context, to autonomy boundary, to the organizational claim someone wants to make from the result.

[[2026-wang-agent-development-real-world-work]] gives the wiki its first direct source on this measurement problem. By mapping 43 agent benchmarks and 72,342 task instances onto O*NET-derived work-domain and skill taxonomies, the paper shows that current benchmarks are not a neutral sample of work. They overrepresent programming-heavy computer and mathematical tasks while underrepresenting management, legal, interpersonal, and other work domains where labor and economic value are concentrated.

The source's most useful move is to separate coverage from realism and capability. A benchmark can cover many generic skills while still being narrow in occupational domain; it can look complex by task count while still missing the ambiguous objectives, long-horizon verification, interpersonal coordination, and context dependence that make real work hard. For this wiki, that means agent benchmark evidence should be read as task-sample evidence, not direct evidence of job-level automation, redesign readiness, or worker substitution.

The autonomy measure in [[2026-wang-agent-development-real-world-work]] also sharpens how to read agent progress. Autonomy is defined as the highest task complexity at which an agent maintains an acceptable success rate, which makes automation and augmentation scope-dependent rather than binary. An agent may autonomously complete a narrow subtask while still requiring human decomposition, verification, integration, and accountability across the broader workflow.

## Connections
- Connects to [[human-ai-task-taxonomy]] because benchmark validity depends on describing task domain, skill, complexity, authority, and auditability before interpreting an agent score.
- Connects to [[construct-validity]] because benchmark names and scores can become rhetorically useful while measuring a narrower or different construct than "real-world work capability."
- Connects to [[work-redesign]] because organizations should not redesign workflows from benchmark scores unless the benchmark samples the relevant work context, deliverable standard, and accountability conditions.
- Connects to [[automation-and-substitution]] because benchmark success is not labor-substitution evidence until it generalizes to end-to-end work under realistic quality, coordination, and oversight constraints.
- Connects to [[job-analysis]] because O*NET-style work taxonomies help locate benchmark tasks in real occupational domains before claims are made about jobs.

## Contradictions & open questions
- [[2026-wang-agent-development-real-world-work]] uses LLM-assisted mapping with strong but imperfect human agreement. The approach is scalable and useful, but benchmark-validity claims still depend on whether task descriptions contain enough context to infer the work domain and skill path correctly.
- Better benchmark representativeness may trade off against clean rewards. Programming and web tasks are overrepresented partly because they are easier to specify and verify; management, legal, interpersonal, and long-horizon work may be more socially important precisely because they are harder to benchmark.
- The wiki still needs field evidence connecting benchmark-validity improvements to better deployment decisions, not only better benchmark design.