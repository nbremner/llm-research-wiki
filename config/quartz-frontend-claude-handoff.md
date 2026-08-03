# Public Research Wiki — Quartz 5 Implementation Handoff

> **For Claude:** Implement this plan end-to-end. Do not stop at scaffolding or a written proposal. Build locally, run the tests and production build, deploy to GitHub Pages, and verify the live site. If repository names or the final domain differ from the defaults below, change them consistently before building.

## Goal

Build a public Quartz 5 reading surface for Nicholas Bremner’s research wiki and host it on GitHub Pages.

The frontend must remain a replaceable presentation adapter. The canonical research model and Markdown stay in `nbremner/llm-research-wiki`; Quartz must not become a second editable wiki.

## Confirmed product decisions

1. The product is a **public research wiki** hosted on GitHub Pages.
2. The publication boundary is exactly:
   - `wiki/overview.md`, rendered as the site homepage;
   - the map pages `wiki/topic-map.md`, `wiki/open-questions.md`, `wiki/research-gaps.md`, `wiki/watchlist.md` (split out of `overview.md` on 2026-08-01; the homepage links them);
   - `wiki/topics/*.md`;
   - `wiki/sources/*.md`.
3. Do not publish `wiki/schema.md`, workflow docs, skills, scripts, tests, config, runtime state, raw PDFs, or other repository files.
4. Remove `drive_file_id` and `file_hash` from rendered/public frontmatter without deleting them from the canonical source files.
5. Use the proposed information architecture and page-type-aware three-column layout.
6. Start with the minimum useful Quartz plugin set. Do not add semantic search, generated related links, MCP, `llms-full.txt`, comments, encrypted pages, tag pages, recent notes, social-image generation, or Git-derived created/modified dates.
7. Keep customization shallow: YAML configuration first, small SCSS second, a small TypeScript layout override only where path-aware conditions require it. Do not edit Quartz core or carry a patch-package fork.

## Current source context

- Canonical repository: `https://github.com/nbremner/llm-research-wiki`
- Visibility: public
- Canonical branch: `main`
- Canonical content root: `wiki/`
- Wiki contract: `wiki/schema.md` — read it, but do not publish it
- Existing graph lint command:

  ```bash
  python scripts/research-wiki-tools/graph_lint.py --wiki-dir wiki --fail-on High
  ```

- Source records may contain operational frontmatter:

  ```yaml
  drive_file_id: ...
  file_hash: ...
  ```

- Topic and source links use Obsidian shortest-path wikilinks such as `[[construct-validity]]` and `[[2026-putka-indexing-ai-impact-onet]]`.
- `wiki/overview.md` was revised pre-launch (commit `e088c4a`, 2026-07-29) to describe the wiki plainly as public; no conflicting statement remains.

## Target architecture

Use a separate frontend repository.

- Default frontend repository: `nbremner/ai-workforce-transformation-wiki`
- Default Pages URL: `https://nbremner.github.io/ai-workforce-transformation-wiki/`
- Default production branch: `main`
- Quartz upstream: `https://github.com/jackyzha0/quartz`, branch `v5`
- Quartz v5 was pre-release/branch-based when this plan was written. Pin the exact upstream commit used and record it; do not build from a floating branch in CI.
- Node: pin Node 25 and commit `package-lock.json` and `quartz.lock.json`. (Originally Node 22; updated 2026-07-28 to match the local toolchain — Quartz 5.0.0 requires only `node >=22`.)

Conceptual flow:

```text
nbremner/llm-research-wiki@main
  wiki/overview.md
  wiki/topics/*.md
  wiki/sources/*.md
          │
          │ read-only checkout
          ▼
prepare-content script
  allowlist paths
  overview.md -> content/index.md
  strip drive_file_id + file_hash
  preserve all other frontmatter/body content
          │
          ▼
Quartz 5 build
          │
          ▼
public/ artifact
          │
          ▼
GitHub Pages
```

Generated content and `public/` are build artifacts. Do not commit them.

---

## Task 1 — Preflight and initialize the frontend repository

### Objective

Create a separate Quartz 5 repository while preserving a clean path for upstream upgrades.

### Steps

1. Verify GitHub authentication and access to the canonical repository.
2. Confirm whether `nbremner/ai-workforce-transformation-wiki` already exists. Reuse it if it does; do not overwrite an existing repository.
3. Initialize from the Quartz `v5` branch, not Quartz 4.
4. Record the exact Quartz upstream commit in `UPSTREAM_QUARTZ.md`, together with:
   - upstream URL;
   - upstream branch;
   - pinned commit;
   - initialization date;
   - upgrade procedure.
5. Configure `upstream` to point to `jackyzha0/quartz` and `origin` to the frontend repository.
6. Use the Obsidian template and shortest-link resolution. Use a new/empty content strategy because content will be generated at build time.
7. Set `baseUrl` to `nbremner.github.io/ai-workforce-transformation-wiki` unless a different repo or custom domain is explicitly selected.
8. Add generated paths to `.gitignore`, including at minimum:

   ```gitignore
   content/
   public/
   .source-wiki/
   ```

9. Install dependencies and plugins, then run Quartz’s check command before customizing.

### Verification

```bash
node --version
npm --version
npm ci
npx quartz plugin install
npm run check
```

Expected: Node satisfies the pinned major, dependencies install from lockfiles, plugins resolve, and the untouched Quartz project passes its checks.

### Commit

```bash
git add .
git commit -m "chore: initialize Quartz 5 research wiki frontend"
```

---

## Task 2 — Make the canonical overview public-facing

### Objective

Remove the contradiction between the confirmed public product and the canonical overview.

### Repository

This task is performed in `nbremner/llm-research-wiki`, not the frontend repository.

### Files

- Modify: `wiki/overview.md`

### Requirements

1. ~~Revise the sentence saying the wiki is “not a public resource for others.”~~ Done (commit `e088c4a`, 2026-07-29).
2. Describe it plainly as a public research wiki at the intersection of AI workforce transformation and I-O psychology.
3. Preserve the central question and the synthesis/evidence distinction; the topic map, open questions, thin areas (research gaps), and watchlist now live on their own published map pages.
4. Do not rewrite the page into marketing copy.
5. Do not alter `wiki/schema.md` or the topic/source schema solely for Quartz.

### Verification

```bash
python scripts/research-wiki-tools/graph_lint.py --wiki-dir wiki --fail-on High
python -m pytest tests/ -q
```

Inspect the diff and confirm that only the intended overview language changed.

### Commit

```bash
git add wiki/overview.md
git commit -m "docs: describe research wiki as public"
git push origin main
```

Verify that local `HEAD` equals `origin/main` before continuing.

---

## Task 3 — Build a deterministic publication adapter

### Objective

Generate Quartz content from a read-only source checkout without creating a second editable corpus.

### Files in frontend repository

- Create: `scripts/prepare-content.mjs`
- Create: `scripts/verify-publication.mjs`
- Create: `tests/prepare-content.test.mjs`
- Create: `tests/fixtures/wiki/overview.md`
- Create: `tests/fixtures/wiki/topics/example-topic.md`
- Create: `tests/fixtures/wiki/sources/2026-example-source.md`
- Modify: `package.json`
- Modify: `.gitignore`

### Adapter contract

Implement `scripts/prepare-content.mjs` with explicit source and destination arguments, for example:

```bash
node scripts/prepare-content.mjs --source .source-wiki/wiki --dest content
```

The adapter must:

1. Delete and recreate the destination directory on each run.
2. Copy only:
   - `<source>/overview.md` to `<dest>/index.md`;
   - `<source>/topic-map.md`, `<source>/open-questions.md`, `<source>/research-gaps.md`, `<source>/watchlist.md` to `<dest>/`;
   - `<source>/topics/*.md` to `<dest>/topics/*.md`;
   - `<source>/sources/*.md` to `<dest>/sources/*.md`.
3. Ignore all other files and directories, even if later added under `wiki/`.
4. Reject symlinks and non-Markdown files inside the allowlisted inputs rather than following or publishing them.
5. Parse YAML frontmatter with the project’s `yaml` dependency.
6. Remove only `drive_file_id` and `file_hash` from frontmatter.
7. Preserve all other frontmatter keys and the Markdown body.
8. Preserve UTF-8 punctuation, long logical lines, headings, DOI URLs, tables, and Obsidian wikilinks.
9. Fail clearly if `overview.md`, `topics/`, or `sources/` is missing.
10. Fail clearly on malformed YAML instead of publishing partially transformed content.
11. Emit a concise manifest to stdout: source revision if available, number of topic files, number of source files, and destination path. Do not include private IDs or hashes.

Add package scripts:

```json
{
  "scripts": {
    "prepare:content": "node scripts/prepare-content.mjs --source .source-wiki/wiki --dest content",
    "verify:publication": "node scripts/verify-publication.mjs --content content --public public",
    "test:publication": "node --test tests/*.test.mjs"
  }
}
```

Merge these with existing Quartz scripts; do not replace the existing `check`, `test`, build, or plugin scripts.

### Tests

Write tests before the implementation. Cover:

1. `overview.md` becomes `index.md` and is not duplicated as `overview.md`.
2. Topic and source relative paths are preserved.
3. `drive_file_id` and `file_hash` are absent from generated frontmatter.
4. Other fields such as `title`, `authors`, `year`, `url`, `doi`, `source_type`, `publication_status`, `retrieved`, `status`, and `updated` survive.
5. Markdown bodies and wikilinks survive.
6. `schema.md` and an arbitrary extra directory are not copied.
7. Malformed frontmatter fails the build.
8. A symlink in an allowlisted directory fails the build.
9. A stale destination file disappears on the next run.

### Verification script

`scripts/verify-publication.mjs` must fail if:

- generated `content/` contains `schema.md` or anything outside `index.md`, `topics/*.md`, and `sources/*.md`;
- generated frontmatter contains `drive_file_id` or `file_hash`;
- `public/` contains rendered pages for excluded content;
- generated public HTML contains the literal keys `drive_file_id` or `file_hash`;
- the homepage, topic folder, source folder, or representative topic/source pages are absent.

Support a `--content-only` mode for the pre-build check. In that mode, validate generated `content/` and skip assertions that require `public/` to exist. The default mode must validate both `content/` and the completed `public/` artifact.

Do not use a fixed expected page count. Compute expectations from the allowlisted canonical inputs so the build remains correct as the wiki grows.

### Verification

```bash
npm run test:publication
npm run prepare:content
npm run verify:publication -- --content-only
```

### Commit

```bash
git add scripts tests package.json .gitignore
git commit -m "feat: add deterministic wiki publication adapter"
```

---

## Task 4 — Configure the minimum Quartz plugin set

### Objective

Provide a useful public reading surface without importing unrelated second-brain machinery.

### Files

- Modify: `quartz.config.yaml`
- Modify: `quartz.lock.json`
- Modify only if needed: `quartz.ts`

### Global configuration

Use:

- page title: `Nicholas Bremner — Research Wiki`;
- locale: `en-US`;
- correct GitHub Pages `baseUrl`;
- SPA navigation enabled;
- popovers enabled;
- analytics disabled for the initial release;
- shortest-path wikilink resolution;
- restrained light/dark theme with readable body typography.

### Enable

Enable only the plugins needed for:

- Obsidian-flavoured Markdown;
- GitHub-flavoured Markdown;
- wikilink crawling;
- description extraction if Quartz requires it;
- content pages;
- folder pages;
- explorer;
- full-text search;
- backlinks;
- table of contents;
- dark mode;
- reader mode;
- page/site title, article title, breadcrumbs, footer, and favicon as basic chrome;
- sitemap/content index, with RSS disabled unless it is required for the sitemap plugin;
- graph view, provisionally.

### Explicitly disable or omit

- created/modified date plugin;
- tag pages and tag list;
- recent notes;
- comments;
- encrypted pages;
- Canvas and Bases pages;
- citations unless the existing Markdown actually requires citation syntax;
- semantic search;
- generated related-note links;
- MCP;
- `llms.txt` and `llms-full.txt`;
- social/OpenGraph image generation;
- explicit-publish workflow;
- note-properties display unless required for a narrowly selected public metadata view;
- analytics.

Run plugin pruning after the config is stable and commit the updated lockfile.

### Verification

```bash
npx quartz plugin install --from-config
npx quartz plugin prune
npm run check
```

Expected: config resolves, unused plugins are pruned, and checks pass.

### Commit

```bash
git add quartz.config.yaml quartz.lock.json quartz.ts
git commit -m "feat: configure minimal Quartz research wiki"
```

---

## Task 5 — Implement the information architecture and layout

### Objective

Make the site navigate like a governed research synthesis system, not a chronological blog or generic tagged vault.

### Left column

Show:

1. Site title/home link.
2. Search.
3. Dark-mode and reader-mode controls in a compact toolbar.
4. Explorer with a deliberately shallow hierarchy:
   - Overview/Home;
   - Topics;
   - Sources.

Do not show schema, tags, recent posts, Canvas, Bases, or framework docs.

### Center column

Render canonical Markdown with minimal decoration.

- Homepage: the generated `index.md` from canonical `overview.md`.
- Topic pages: synthesis-first prose, connections, contradictions, and open questions.
- Source pages: citation, summary, key claims, evidence/limitations, and feeds.
- Do not duplicate the Markdown H1 with an unnecessary second title. If the article-title component duplicates the canonical H1, choose one title source consistently.
- Do not display Git-derived created/modified dates. The canonical `updated` field may remain in frontmatter but should not be turned into misleading history.

### Right column

- Homepage: no mostly empty local graph. A table of contents is acceptable if useful; otherwise keep the column quiet.
- Topic pages: local graph, table of contents, backlinks.
- Source pages: table of contents and backlinks; omit the graph.
- Folder pages: no graph; use the simplest readable folder listing.

Quartz’s built-in YAML conditions may not distinguish `topics/` from `sources/`. If they cannot, add the smallest possible `quartz.ts` layout override that checks the page slug/path. Do not create a custom plugin or edit Quartz core for this.

### Graph guardrail

The graph must represent existing curated wikilinks only. Do not inject embedding neighbours, co-occurrence links, or synthetic relationships. If the stock graph is not useful after live testing, demote or remove it rather than patching it heavily.

### Verification

Run a local server and inspect:

```bash
npm run prepare:content
npx quartz build --serve
```

Verify desktop, tablet, and mobile layouts for:

- `/`;
- `/topics/`;
- `/sources/`;
- `/topics/construct-validity`;
- `/sources/2026-putka-indexing-ai-impact-onet`.

Verify search, dark mode, reader mode, wikilink navigation, backlinks, table of contents, popovers, and browser back/forward navigation.

### Commit

```bash
git add quartz.config.yaml quartz.ts quartz.lock.json
git commit -m "feat: add research wiki navigation and page layouts"
```

---

## Task 6 — Add restrained visual styling

### Objective

Create a credible public research surface without turning the build into a branding project.

### Files

- Modify: `quartz/styles/custom.scss`
- Modify only if needed: theme colors/typography in `quartz.config.yaml`

### Requirements

1. Optimize for long-form reading.
2. Keep line length, heading hierarchy, lists, blockquotes, tables, and link contrast accessible in light and dark modes.
3. Give topic and source pages a subtle visual distinction using path/body classes if Quartz exposes them; do not add decorative cards to every section.
4. Keep the three-column layout calm and responsive.
5. Do not add animations beyond Quartz defaults.
6. Do not add a large hero, marketing CTA, comments, social counters, or decorative global graph.
7. Ensure keyboard focus states and color contrast remain visible.

### Verification

Inspect representative pages at desktop and mobile widths in both themes. Run the production build and browser console check; there should be no layout-breaking errors or failed asset requests.

### Commit

```bash
git add quartz/styles/custom.scss quartz.config.yaml
git commit -m "style: refine public research wiki reading experience"
```

---

## Task 7 — Add production checks and GitHub Pages deployment

### Objective

Build from canonical content, enforce the publication boundary, and deploy only a verified static artifact.

### Files

- Create: `.github/workflows/deploy.yml`
- Update: `README.md`

### Workflow triggers

Use:

- pushes to frontend `main`;
- `workflow_dispatch`;
- a scheduled rebuild every six hours at a non-round minute so canonical wiki changes reach the site without cross-repository secrets.

Do not add a cross-repository PAT for v1. Document that scheduled rebuilds create a bounded publication delay and that manual dispatch is available for immediate publication.

### Workflow sequence

1. Check out the frontend repository with full history.
2. Check out `nbremner/llm-research-wiki@main` read-only into `.source-wiki/`.
3. Set up Python 3.11.
4. Run canonical graph lint:

   ```bash
   python .source-wiki/scripts/research-wiki-tools/graph_lint.py \
     --wiki-dir .source-wiki/wiki \
     --fail-on High
   ```

5. Set up pinned Node 25 with npm caching.
6. Cache Quartz plugins keyed by `quartz.lock.json`.
7. Run `npm ci`.
8. Run `npx quartz plugin install` from the lockfile.
9. Run publication-adapter tests.
10. Generate `content/` from `.source-wiki/wiki`.
11. Run the content-only publication-boundary verifier.
12. Run `npm run check`.
13. Run the Quartz production build.
14. Run the complete publication verifier against both `content/` and `public/`.
15. Upload `public/` with `actions/upload-pages-artifact`.
16. Deploy with `actions/deploy-pages`.

Use GitHub’s minimum required permissions:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

Use Pages concurrency so a stale deployment cannot race a newer one.

### README

Document:

- the adapter architecture;
- source and frontend repository responsibilities;
- local prerequisites;
- exact local test/build/serve commands;
- publication allowlist;
- stripped fields;
- GitHub Pages URL;
- scheduled rebuild behavior;
- Quartz upstream pin and upgrade procedure;
- explicit non-goals.

### Verification

Run the complete sequence locally before relying on CI:

```bash
npm ci
npx quartz plugin install
npm run test:publication
npm run prepare:content
npm run check
npx quartz build
npm run verify:publication
```

Push and watch the GitHub Actions job to completion. Do not report deployment success until the workflow is green and the Pages URL returns the built site.

### Commit

```bash
git add .github/workflows/deploy.yml README.md
git commit -m "ci: deploy verified research wiki to GitHub Pages"
git push origin main
```

---

## Task 8 — Verify the live product

### Objective

Prove that the public site works as a research wiki and that the publication boundary holds.

### Live acceptance checks

1. Homepage loads and reflects the public-facing canonical overview.
2. Explorer exposes only Overview, Topics, and Sources as the top-level knowledge hierarchy.
3. Topic and source folder pages work.
4. A representative topic page renders and its wikilinks resolve.
5. A representative source page renders and links back to its feeding topics.
6. Full-text search returns both topic and source results.
7. Backlinks work.
8. Topic pages show the local graph; source and homepage layouts do not show an unhelpful graph.
9. Table of contents works on long pages.
10. Dark mode and reader mode work.
11. Desktop, tablet, and mobile layouts are usable.
12. Browser console has no uncaught errors or repeated failed requests.
13. `schema.md` is not publicly routable or indexed.
14. No workflow docs, skills, tests, source code, raw documents, or repository internals are published.
15. Neither `drive_file_id` nor `file_hash` appears in generated HTML, search indexes, JavaScript data, sitemap output, or other public artifacts.
16. No semantic-search, MCP, comments, tag pages, recent notes, generated related links, or `llms-full.txt` endpoints were added.
17. GitHub Pages serves the correct base path and internal navigation does not drop the repository subpath.
18. The deployed artifact can be traced to the canonical source commit shown in the successful workflow run.

Use direct HTTP checks as well as a real browser. A successful build alone is insufficient.

### Final report

Return:

- live URL;
- frontend repository URL;
- canonical source commit used by the deployment;
- Quartz upstream commit pin;
- CI run URL/status;
- local test/check/build outputs;
- publication-boundary verification result;
- any intentional deviations from this plan;
- screenshots or concise notes for desktop and mobile verification.

---

## Non-goals and hard guardrails

Do not:

- move canonical Markdown into the frontend repository;
- maintain hand-edited public copies of topic or source pages;
- delete internal provenance fields from canonical files;
- publish `schema.md` or the operating machinery;
- modify the wiki schema to satisfy a frontend convention;
- rename `overview.md` in the canonical repository solely for Quartz;
- edit Quartz core;
- add a large graph patch;
- add embeddings or synthetic related-note links;
- add a vector store, RAG layer, MCP server, semantic search, or machine-readable full-corpus export;
- commit generated `content/` or `public/` output;
- introduce cross-repository credentials when public checkout plus scheduled rebuilds suffice;
- report success before live verification.

## Definition of done

The work is done only when:

1. the canonical overview is consistent with public publication;
2. the separate frontend repository is live on GitHub Pages;
3. only overview, topics, and sources are published;
4. internal provenance fields are absent from every public artifact;
5. search, wikilinks, backlinks, TOC, dark mode, reader mode, and the restrained page-aware graph layout work;
6. tests, Quartz checks, graph lint, production build, artifact verification, CI, and live browser checks all pass;
7. the implementation remains a shallow, upgradeable adapter over the canonical wiki.
