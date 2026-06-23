---
title: "Remote Labor Index: Measuring AI Automation of Remote Work"
authors: Mantas Mazeika, Alice Gatti, Cristina Menghini, Udari Madhushani Sehwag, Shivam Singhal, Yury Orlovskiy, Steven Basart, Manasi Sharma, Denis Peskoff, Elaine Lau, Jaehyuk Lim, Lachlan Carroll, Alice Blair, Vinaya Sivakumar, Sumana Basu, Brad Kenstler, Yuntao Ma, Julian Michael, Xiaoke Li, Oliver Ingebretsen, Aditya Mehta, Jean Mottola, John Teichmann, Kevin Yu, Zaina Shaik, Adam Khoja, Richard Ren, Jason Hausenloy, Long Phan, Ye Htet, Ankit Aich, Tahseen Rabbani, Vivswan Shah, Andriy Novykov, Felix Binder, Kirill Chugunov, Luis Ramirez, Matias Geralnik, Hernán Mesura, Dean Lee, Ed-Yeremai Hernandez Cardona, Annette Diamond, Summer Yue, Alexandr Wang, Bing Liu, Ernesto Hernandez, Dan Hendrycks
year: 2025
url: https://arxiv.org/abs/2510.26787
doi: 10.48550/arXiv.2510.26787
source_type: paper
publication_status: preprint
retrieved: 2026-06-16
drive_file_id: 1TBzD9Q9zuvt9Z5AWI2SSHpTqbiUuLfza
file_hash: 7bc1e50585429c83a93a8045fdaa654ba074c4fa3a35671613024de69c46d2ed
---

# Remote Labor Index: Measuring AI Automation of Remote Work

**Citation.** Mazeika, M., Gatti, A., Menghini, C., Madhushani Sehwag, U., Singhal, S., Orlovskiy, Y., Basart, S., Sharma, M., Peskoff, D., Lau, E., Lim, J., Carroll, L., Blair, A., Sivakumar, V., Basu, S., Kenstler, B., Ma, Y., Michael, J., Li, X., Ingebretsen, O., Mehta, A., Mottola, J., Teichmann, J., Yu, K., Shaik, Z., Khoja, A., Ren, R., Hausenloy, J., Phan, L., Htet, Y., Aich, A., Rabbani, T., Shah, V., Novykov, A., Binder, F., Chugunov, K., Ramirez, L., Geralnik, M., Mesura, H., Lee, D., Hernandez Cardona, E.-Y., Diamond, A., Yue, S., Wang, A., Liu, B., Hernandez, E., & Hendrycks, D. (2025). *Remote Labor Index: Measuring AI Automation of Remote Work*. arXiv. https://doi.org/10.48550/arXiv.2510.26787

**Summary.** This paper introduces the Remote Labor Index, a benchmark of 240 end-to-end remote freelance projects sourced from real professional work. It argues that existing AI benchmarks overstate economically meaningful automation because they often test narrower skills rather than complete deliverables. Across evaluated frontier agents, the best automation rate was 2.5%, meaning current agents completed very few projects at a level a reasonable client would accept. The benchmark is meant to track AI automation capacity against real remote-work deliverables, not merely model knowledge or isolated computer-use ability.

## Key claims

- RLI contains 240 projects across 23 Upwork subcategories, each composed of a brief, input files, and a human-produced gold-standard deliverable.
- The benchmark represents more than 6,000 hours of human work and more than $140,000 in reported project value; mean human completion time was 28.9 hours and median completion time was 11.5 hours.
- Automation rate is defined as the share of projects where human evaluators judge the AI deliverable to complete the project at least as well as the human deliverable, using a reasonable-client acceptance standard.
- Current evaluated AI agents performed near the floor: Manus achieved 2.5%, Grok 4 and Sonnet 4.5 achieved 2.1%, GPT-5 achieved 1.7%, ChatGPT agent achieved 1.3%, and Gemini 2.5 Pro achieved 0.8% automation.
- Pairwise Elo comparisons are used to detect relative model progress even when absolute automation remains low.
- Common failure modes included technical/file-integrity problems, incomplete or malformed deliverables, professional-quality gaps, and inconsistencies across generated artifacts.

## Evidence & limitations

- The strongest contribution is measurement design: real commissioned work, human gold-standard deliverables, manual evaluation, and an explicit client-acceptance criterion.
- The quantitative evaluation relies on a mostly private benchmark: 230 of 240 projects are withheld to protect PII and reduce contamination, with 10 public projects and evaluation-platform code released for qualitative inspection.
- RLI excludes some remote-work forms, including work requiring client interaction, team coordination, or unsupported file/rendering formats, so even a high RLI score would not imply full remote-labor automation.
- Human-reported cost and completion-time data are not inflation-adjusted and mostly reflect projects completed within the previous five years.
- The paper measures autonomous end-to-end project completion, not assisted productivity, within-job augmentation, employment effects, wages, or organizational adoption.

## Feeds

- [[automation-and-substitution]]
- [[work-redesign]]
- [[evidence-based-management]]
- [[human-ai-collaboration]]
