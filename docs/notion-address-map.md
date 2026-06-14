# Notion address map — research-wiki

Canonical Notion page/database IDs for the public research wiki. This is **machinery**
(addresses only), not content, so it belongs in the Git spine. The IDs are not secrets:
they are inert without the workspace OAuth grant.

This is a **snapshot**. The Notion **Agent Operating Guide** is canonical for live IDs and
run steps; if they ever diverge, the Guide wins and this file is updated to match.
Keep this in sync when pages/databases are added, moved, or renamed in Notion.
Last verified: 2026-06-14.

## Parent

| Artifact | Type | ID |
|---|---|---|
| research-wiki | page (root) | `368ccc4a-237c-80a8-a178-f6b0e3941270` |

## Operating-layer pages

| Page | ID |
|---|---|
| Schema (canonical contract — read first) | `36accc4a-237c-81a9-8de2-c667d2a95796` |
| Agent Operating Guide — LC / DC / Hermes | `36bccc4a-237c-813c-b884-c89702815b03` |
| Research Map / Overview | `37cccc4a-237c-81cc-b455-ff673f15e97c` |
| Index (public front door placeholder) | `36accc4a-237c-81b2-bce5-e7e9837d8f65` |
| System Docs / Archive | `36bccc4a-237c-812f-b653-e1038dfd8ea9` |
| SciAI Wiki Alignment Roadmap | `36fccc4a-237c-81ca-b432-d1292f981842` |
| Architecture Master Reference — frozen | `369ccc4a-237c-80a7-95dc-cc567e4278a3` |
| Setup Checklist — completed | `36accc4a-237c-8136-b223-ef319a4d9294` |

## Databases

| Database | Page ID | Data source (collection) |
|---|---|---|
| Sources | `0569f238-61a3-4705-9ae4-945a45acf7b1` | `2491c01c-8c1d-42b7-9272-ab235ea64586` |
| Concepts | `b5239ba5-7ecc-44f4-a300-4ec4b0f08cc3` | `f578eaf9-81bb-4668-8bdc-191fdea8e5f1` |
| Reviews | `09776168-d11e-4868-ab34-6ebe3b900cee` | `eb454605-2dea-4b8b-a173-407be60184ed` |
| Inbox | `cb35f9c7-0fd7-41b8-b32a-17784da9160c` | `56bea68b-7a43-4494-bf80-23f15202ef1c` |
| Log | `aff36f8c-2ce0-4d65-b9cb-fc392a3bf341` | `d1169e63-cf4d-4a9b-b8a8-139c78faab5c` |

## Prompt snippet pages (per-agent boot prompts)

| Page | ID |
|---|---|
| Hermes prompt snippet | `368ccc4a-237c-8065-8059-c86cd3db1898` |
| LC prompt snippet | `368ccc4a-237c-807d-85f4-d93763870786` |
| DC prompt snippet | `368ccc4a-237c-8094-8af8-db89ffa44d8b` |

## Write-boundary reminder

Per `OPERATING_MODEL.md`: NicholasJunior writes Inbox/Log/Review-drafts automatically;
Sources/Concepts/Schema/Research Map/Index are approval-gated; DC has no write path.
LC (Claude Code) holds the Notion MCP and performs approval-gated edits in human-directed
sessions.
