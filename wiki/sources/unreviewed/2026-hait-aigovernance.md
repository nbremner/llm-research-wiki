---
title: "AIGovernance: Statistical Auditing and Governance Reporting for Employment AI Systems"
authors: Hait, Subir
year: 2026
url: https://cran.r-project.org/package=AIGovernance
doi: 10.32614/CRAN.package.AIGovernance
source_type: other
publication_status: other
retrieved: 2026-09-26
human_reviewed: false
drive_file_id: 1vxudf4SAMUcj6DiC5cmCyCWXALdYVM3U
file_hash: 2c4c2cff1de5351699107bb5a5949256d91af20b1933699848db70d1d1239ae1
---

# AIGovernance: Statistical Auditing and Governance Reporting for Employment AI Systems

**Citation.** Hait, S. (2026). *AIGovernance: Statistical Auditing and Governance Reporting for Employment AI Systems* (R package version 0.1.0). CRAN. https://doi.org/10.32614/CRAN.package.AIGovernance

**Summary.** AIGovernance is an R package for statistical auditing, risk documentation, and governance reporting for employment and hiring AI systems. It implements EEOC four-fifths adverse-impact calculations, NYC Local Law 144 bias-audit statistics and disclosure tables, a NIST AI RMF checklist, optional EU AI Act risk classification, and report generation; it explicitly does not provide legal advice or certify compliance.

## Key claims
- The package computes group selection rates, adverse-impact ratios relative to a reference group, two-proportion Z tests, Fisher exact-test p-values, and small-sample warnings; it flags an adverse-impact ratio below 0.80 under the EEOC four-fifths rule.
- Its NYC Local Law 144 module uses the most-selected category as the default denominator, produces race/ethnicity and sex impact-ratio tables, and formats a public-disclosure table.
- Its NIST AI RMF module records checklist responses for GOVERN, MAP, MEASURE, and MANAGE functions and reports completion scores and GREEN, AMBER, or RED verdict labels.

## Evidence & limitations
- This is public software documentation for version 0.1.0, not an empirical validation study of the package, its thresholds, or the governance outcomes of using it.
- The included hiring dataset is synthetic and illustrative; the package warns that the four-fifths rule is a rule of thumb rather than a bright-line legal standard and that small samples reduce reliability.
- Public provenance is the CRAN package landing page and its registered package DOI; the ingested PDF is the 12-page reference manual dated 2026-05-27.

## Feeds
- [[responsible-ai-deployment]]
- [[algorithmic-assessment]]
