# 带人工复核的研究智能体示例 | Human-Review Research Agent

Follow a research draft from local evidence to an exportable report, with a visible human decision in between. This offline Python example retrieves relevant facts, builds a cited draft, records approval or rejection, and blocks export when approval is missing or the draft changes afterward.

从本地证据到可导出的研究草稿，中间必须经过人工决定。这个离线 Python 示例会检索相关事实、生成带来源标记的草稿、记录通过或退回，并在未获批准或批准后草稿被改动时阻止导出。

**Read in your language / 选择语言：** [完整中文说明](README.zh-CN.md) · [Full English guide](README.en.md)

## Try it / 立即试用

Python 3.9+; no model key or third-party packages. / Python 3.9+，无需模型密钥和第三方依赖。

```bash
python3 agent.py prepare --question "What is Example City planning for library hours?" \
  --corpus examples/facts.json --out /tmp/research-draft.json
python3 agent.py review /tmp/research-draft.json --decision approve --reviewer "Demo reviewer"
python3 agent.py export /tmp/research-draft.json --out /tmp/research-report.md
```

This is a workflow template, **not** a connected LLM service or a claim that an automatic draft is correct. / 这是工作流模板，**没有**接入大模型，也不保证自动草稿正确。

**License / 许可证：** [GPL-3.0-only](LICENSE). **Repository / 仓库：** [workstonedai-collab/human-review-research-agent](https://github.com/workstonedai-collab/human-review-research-agent).
