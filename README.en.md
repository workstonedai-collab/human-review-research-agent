# Human-Review Research Agent

Research automation should make three things visible: **which evidence was used, what state the draft is in, and who approved which version**. This runnable example separates local fact retrieval, a cited draft, a human approve/reject decision, and export. It blocks export without approval and requires a new review if the draft changes afterward.

[中文说明](README.zh-CN.md) · [Bilingual home](README.md)

## What this includes

- An offline workflow template that runs and tests without a model API.
- Replaceable retrieval and drafting steps for a real local search tool, model, or editor.
- A visible human gate recording reviewer, comment, time, and a draft digest.

It is **not** a complete research product. There is no web search, LLM reasoning, automatic fact checking, authenticated reviewer, or online publishing endpoint. The city, facts, and `example.*` URLs in the sample are fictional.

## Complete the flow in 30 seconds

Use Python 3.9 or newer; no third-party packages are needed. From this folder:

```bash
# 1. Prepare a draft from local facts
python3 agent.py prepare \
  --question "What is Example City planning for library hours?" \
  --corpus examples/facts.json --out /tmp/research-draft.json

# 2. A person opens /tmp/research-draft.json and checks facts, citations, and wording
# 3. That person approves or rejects the current version
python3 agent.py review /tmp/research-draft.json \
  --decision approve --reviewer "Demo reviewer"

# 4. Only the approved current version can be exported locally
python3 agent.py export /tmp/research-draft.json --out /tmp/research-report.md
```

To reject, use `--decision reject --comment "Add another source"`. A person can edit the rejected draft and run `review` again. The `reviewer` text is not authenticated; a real system needs its own login and audit trail.

## Input and state

The local corpus is a JSON array. Each fact needs `id`, `title`, `statement`, and an HTTPS `source_url`. See the [fictional corpus](examples/facts.json). `prepare` chooses at most three facts by token overlap between the question, titles, and statements. It drafts only from selected facts and stops when there is no matching evidence rather than inventing an answer.

The state file contains:

| Field | Meaning |
| --- | --- |
| `question` | The user's research question |
| `facts` | Selected facts with source URLs |
| `draft` | Sections with `[source:id]` references and an open-questions reminder |
| `stage` | `needs_review`, `rejected`, or `approved` |
| `review` | Decision, reviewer, comment, timestamp, and draft SHA-256 |

`export` recomputes a digest over the question, selected facts, and draft. A change to any of them after approval blocks export. This illustrates approval bound to a specific version. The JSON state file is **not tamper resistant** and does not replace a production audit log or digital signature.

## Adapt it for your own agent

1. Replace token matching in `prepare` with your retriever while retaining verifiable source IDs.
2. Replace draft generation with a model or template, while keeping citations and an evidence-insufficient stop.
3. Replace the `review` command with an authenticated human review interface and specific rejection feedback.
4. Keep the `export` check immediately before any real export or publishing action, bound to the approved draft version.
5. Add fact checking, citation validity, sensitive-data review, and rights checks for real use; they are outside this example.

Run `python3 -m unittest discover -s tests -v` to check the missing-approval, rejection, and post-approval-edit gates. Commands return `0` on success and `2` for input or workflow errors. All actions read and write local files only; nothing is published automatically.

## Privacy and release boundary

There are no real research materials, knowledge-base structures, internal APIs, model keys, or business workflow settings. All sample facts are fictional. If you later integrate real data, do not commit state files, human feedback, or model request logs to a public repository.

This standalone project has no business repository history. It is released under the [GPL-3.0-only license](LICENSE) at [workstonedai-collab/human-review-research-agent](https://github.com/workstonedai-collab/human-review-research-agent).
