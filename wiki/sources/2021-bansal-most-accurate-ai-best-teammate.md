---
title: "Is the Most Accurate AI the Best Teammate? Optimizing AI for Teamwork"
authors: Bansal, Nushi, Kamar, Horvitz, Weld
year: 2021
url: https://doi.org/10.1609/aaai.v35i13.17359
doi: 10.1609/aaai.v35i13.17359
source_type: paper
publication_status: peer-reviewed
retrieved: 2026-08-31
drive_file_id: 1_obATMmrtmOhRQ5X-aLMIQekitwcKVdp
file_hash: e66fd9c026b99e68988c120492f70a334e5fbceec1176b639d3c8957fce81b93
---

# Is the Most Accurate AI the Best Teammate? Optimizing AI for Teamwork

**Citation.** Bansal, G., Nushi, B., Kamar, E., Horvitz, E., & Weld, D. S. (2021). Is the Most Accurate AI the Best Teammate? Optimizing AI for Teamwork. *Proceedings of the AAAI Conference on Artificial Intelligence, 35*(13), 11405–11414. https://doi.org/10.1609/aaai.v35i13.17359

**Summary.** Bansal et al. formulate AI-advised classification as a human-AI team in which a human either accepts a recommendation or solves the task, with team utility determined by decision quality, human effort, and mistake cost. Across synthetic and high-stakes classification datasets, training for expected team utility could outperform accuracy-optimized models on the team objective even when it sacrificed standalone model accuracy. The paper makes the objective-function point sharply: a system optimized for individual prediction can be misaligned with the combined system when human reliance and verification are endogenous.

## Key claims
- In the paper's accept-or-solve model, the threshold for accepting AI advice depends on human accuracy, the cost of human effort, and the cost of mistakes; AI performance outside the accept region does not contribute to realized team utility in the same way as performance inside it.
- With the authors' Scenario1 linear classifier, expected team utility increased from 0.524 under log-loss optimization to 0.606 under expected-utility optimization despite a 0.165 decrease in standalone accuracy; the result illustrates that the individual-accuracy optimum can differ from the modeled team-utility optimum.
- Across the reported datasets, higher expected utility did not consistently yield higher empirical utility, exposing a loss-metric mismatch rather than establishing a universally superior objective.
- The experiments use synthetic data plus German credit, FICO credit-risk, recidivism, and MIMIC-3 mortality-prediction datasets with linear and multilayer-perceptron classifiers; they are a model-based account of an advice-and-override workflow, not a field study of deployed human-AI teams.

## Evidence & limitations
- Peer-reviewed AAAI-21 proceedings paper (10 pages); the official AAAI landing page and Crossref record match the title, authors, 18 May 2021 publication date, venue, page range, and DOI.
- The ingested Drive PDF is a 10-page, 641,970-byte PDF with SHA-256 e66fd9c026b99e68988c120492f70a334e5fbceec1176b639d3c8957fce81b93; text extraction produced 49,368 characters with no model-directed prompt-injection language detected.
- The formal model assumes a rational user who trusts calibrated confidence and chooses only between accepting advice and solving the task; real workflows may include partial checking, explanation use, social incentives, unequal expertise, and organizational accountability.
- Expected-utility gains can diverge from empirical-utility gains, and the authors identify optimization difficulty and loss-metric mismatch; the results should not be read as evidence that deliberately less accurate AI is generally better for people.

## Feeds
- [[human-ai-collaboration]]
- [[human-ai-task-allocation]]
- [[automation-complacency]]
