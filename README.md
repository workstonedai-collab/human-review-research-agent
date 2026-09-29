# 带人工复核的研究智能体示例 | Human-Review Research Agent

研究草稿若要进入报告，团队需要回答：依据来自哪里、谁看过、批准的是哪一版？这个可运行的离线示例把**本地证据检索、带来源标记的草稿、人工批准或退回、导出门禁**串成一条可观察的流程。没有批准，或批准后内容发生变化，都不能导出。

Before a research draft becomes a report, a team needs to know where its evidence came from, who reviewed it, and which version was approved. This runnable offline example connects **local fact retrieval, a cited draft, human approval or rejection, and an export gate**. Export is blocked without approval or after approved content changes.

**Read in your language / 选择语言：** [完整中文说明](README.zh-CN.md) · [Full English guide](README.en.md)

## 看得见的人工复核 / A visible human checkpoint

| 中文 | English |
| --- | --- |
| **草稿有据可查：**从虚构的本地事实库挑选相关内容，在草稿中保留 `[source:id]` 标记；找不到相关事实就停止。 | **Trace the draft:** select relevant facts from a fictional local corpus, keep `[source:id]` markers, and stop when no matching evidence is found. |
| **决定绑定版本：**人工记录批准或退回；导出时重新检查问题、事实和草稿，批准后改动会要求重新复核。 | **Bind approval to a version:** record approve/reject decisions and recheck the question, facts, and draft before export. Changes require another review. |
| **方便改造成自己的流程：**检索、成稿与复核界面都可替换；示例无需模型密钥或第三方依赖。 | **Adapt the workflow:** replace retrieval, drafting, and the review interface for your system; the example needs no model key or third-party packages. |

适合研究工具原型、人工复核流程演示和导出门禁测试。示例没有联网搜索、自动事实核查、身份认证或在线发布；真实使用须补齐这些能力。 / Use it to prototype research workflows and test an export gate. It has no web search, automatic fact checking, reviewer authentication, or online publishing.

## Try it / 立即试用

Python 3.9+; no model key or third-party packages. / Python 3.9+，无需模型密钥和第三方依赖。

```bash
python3 agent.py prepare --question "What is Example City planning for library hours?" \
  --corpus examples/facts.json --out /tmp/research-draft.json
python3 agent.py review /tmp/research-draft.json --decision approve --reviewer "Demo reviewer"
python3 agent.py export /tmp/research-draft.json --out /tmp/research-report.md
```

执行后会得到带 `[source:...]` 标记和复核人记录的本地 Markdown 报告。试着在 `review` 前运行 `export`，或批准后修改草稿，导出都会被阻止。 / The result is a local Markdown report with `[source:...]` references and a reviewer record. Try exporting before review or changing the draft after approval: both attempts are blocked.

This is a workflow template, **not** a connected LLM service or a claim that an automatic draft is correct. / 这是工作流模板，**没有**接入大模型，也不保证自动草稿正确。

**License / 许可证：** [GPL-3.0-only](LICENSE). **Repository / 仓库：** [workstonedai-collab/human-review-research-agent](https://github.com/workstonedai-collab/human-review-research-agent).
