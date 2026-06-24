# AI workforce impact measurement topic-assessment pattern

Use this reference when ingesting sources that measure AI workforce impact using observed usage traces, exposure/applicability scoring, O*NET/work-activity mappings, completion/scope measures, productivity proxies, or labor-market outcome claims.

## Core assessment

Do not flatten these sources into `task-level-ai-adoption` by default. If the source's central contribution is about **how AI impact is measured** — not merely where people use AI — assess whether it belongs in or should promote `ai-workforce-impact-measurement`.

Typical signals:

- The paper constructs an exposure, applicability, capability, productivity, or impact measure.
- The key move is a measurement chain: observed use → task/work-activity taxonomy → completion/scope/quality → occupation/job/workforce inference.
- The source explicitly cautions that a measured construct is narrower than realized productivity, wage change, labor demand, skill change, or job redesign.
- The source uses O*NET, SOC, job analysis, task decomposition, benchmark-to-work mappings, or other work taxonomies as a measurement spine.

## Default topic map

- **Create/update `ai-workforce-impact-measurement`** when the source helps define or critique the construct validity of AI workforce impact evidence.
- **Update `task-level-ai-adoption`** only for the observed-use portion: where workers actually use AI, at what task grain, and under what usage conditions.
- **Update `human-ai-task-taxonomy`** when the source distinguishes user goals, AI actions, authority, output, scope, auditability, human persona, or task context.
- **Update `automation-and-substitution`** when the source tempts automation/substitution claims or warns against them. Preserve the boundary: applicability/usefulness is not labor substitution.
- **Update `job-analysis`** when the source relies on O*NET, SOC, work activities, KSAOs, or other work-analysis structures. Surface both the utility and limits of static taxonomies.
- **Update `construct-validity`** if the source is primarily about whether the named impact construct is bounded, reliably measured, and linked to appropriate outcomes.

## Pitfalls

- Do not treat observed conversational use as organizational adoption.
- Do not treat AI applicability, exposure, or successful completion as productivity impact unless the source actually measures productivity.
- Do not convert AI-side task performance into job-level automation or headcount substitution.
- Do not let O*NET/SOC aggregation hide the connective tissue between tasks, accountability, coordination, and role-level work design.
- Do not overfit to one platform's traces. Enterprise copilots, embedded workflow automation, non-chat systems, avoided uses, and policy-constrained uses may be absent.

## Example from Tomlinson et al. (2025)

`[[2025-tomlinson-working-with-ai]]` was best handled by promoting `[[ai-workforce-impact-measurement]]` because the central contribution was not just Copilot adoption. The paper mapped 200k Bing Copilot conversations to O*NET intermediate work activities, separated user goals from AI actions, weighted activity maps by completion/feedback/scope, and built occupation-level AI applicability scores. The durable synthesis point was the measurement boundary: applicability locates where AI may touch work, but it does not establish realized productivity, job redesign, wages, staffing, or labor substitution.