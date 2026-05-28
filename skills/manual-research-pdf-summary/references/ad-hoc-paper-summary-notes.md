# Ad-hoc paper summary notes

Use these notes when the user asks for a quick paper summary rather than a full research-wiki dry-run/apply workflow.

## Pattern from session: "Summarize the paper on effect sizes"

When the user refers to a paper by topic/title fragment and there is prior research-wiki/backlog context:

1. First identify the intended paper from session/search/local triage artifacts if available.
2. State the interpretation briefly in the answer (e.g., "I interpreted this as Bosco et al. (2015), _Correlational Effect Size Benchmarks_").
3. Do not force the full Candidate Source Summary structure unless the user asked to process it into the wiki.
4. Give a substantive research summary: thesis, method, key numeric findings, implications, limitations, and why it matters for Nicholas's work.
5. If the PDF/text is available locally, extract/read enough text to ground key claims. If extraction dependencies are missing, use an available lightweight extractor or install a small Python parser as needed; capture the successful extraction path only if it generalizes.

## Source note: Bosco et al. (2015), Correlational Effect Size Benchmarks

Citation: Bosco, F. A., Aguinis, H., Singh, K., Field, J. G., & Pierce, C. A. (2015). _Correlational Effect Size Benchmarks_. Journal of Applied Psychology, 100(2), 431–449. DOI: 10.1037/a0038047.

Core thesis: Cohen's conventional correlation benchmarks (.10 small, .30 medium, .50 large) are a poor universal fit for applied psychology. Effect-size interpretation should be empirically benchmarked and context-specific.

Key empirical base:
- 147,328 correlations from 1,660 articles in Journal of Applied Psychology and Personnel Psychology, 1980–2010.
- Correlations were coded using a hierarchical variable taxonomy.
- Analyses used absolute correlations and examined omnibus and relation-type-specific distributions.

Key findings:
- Omnibus median |r| ≈ .16.
- Omnibus center tertile / medium empirical range ≈ |r| .09 to .26.
- Cohen's .30 corresponds to roughly the 73rd percentile; .50 to roughly the 90th percentile.
- Cohen-style medium classifications overlap very poorly with the empirical center tertile: 0% under cutoff interpretation, 8.21% under centroid interpretation.
- Benchmarks vary sharply by relation type: attitude–attitude and attitude–intention relations are stronger; attitude–behavior and intention–behavior relations are lower.
- Behavior-prediction contexts often make |r| around .25 relatively strong, even though Cohen would not treat it as medium/large under generic thresholds.

Useful implications for Nicholas's work:
- For I/O literature extraction and nomological-network tooling, relationship-strength labels need domain/relation-type context.
- Avoid flattening edges into generic small/medium/large labels without reference populations.
- Useful for research-wiki claims involving construct validity, criterion-related validity, power analysis, practical significance, and field-relative interpretation.

Limitations:
- Only two elite applied psychology journals.
- Only correlations reported in tables/matrices.
- Focuses on r, not d or other effect-size metrics.
- Includes many correlation-matrix associations not necessarily hypothesized relationships.
- Context-specific benchmarking is valuable but can become relativistic if the reference class is chosen too narrowly.
