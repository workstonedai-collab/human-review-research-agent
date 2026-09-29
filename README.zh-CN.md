# 带人工复核的研究智能体示例

研究类自动化最需要让人看清楚三件事：**用了哪些证据、草稿处于什么状态、谁在什么版本上作了决定**。这个最小示例把流程拆成“检索本地事实 → 生成带来源标记的草稿 → 人工批准或退回 → 导出”。未获批准不能导出；批准后改动草稿，也必须重新复核。

[English guide](README.en.md) · [双语首页](README.md)

## 这是什么

- 一个不依赖模型 API 的离线工作流模板，可直接运行与测试。
- 一个可替换的检索和成稿骨架：实际项目可接本地检索器、模型或编辑界面。
- 一个明确的人工复核门：决定记录了复核人、意见、时间和草稿摘要值。

它**不是**完整研究产品，没有联网搜索、模型推理、自动事实核查、身份认证或真正的发布接口。示例中的英文城市、事实和 `example.*` 地址全是虚构演示内容。

## 30 秒走完流程

需要 Python 3.9 或更新版本，无第三方依赖。在本文件夹执行：

```bash
# 1. 用本地事实库生成草稿
python3 agent.py prepare \
  --question "What is Example City planning for library hours?" \
  --corpus examples/facts.json --out /tmp/research-draft.json

# 2. 人工打开 /tmp/research-draft.json，核对事实、引用和措辞
# 3. 人工选择批准或退回
python3 agent.py review /tmp/research-draft.json \
  --decision approve --reviewer "Demo reviewer"

# 4. 只有批准后的当前版本可导出到本地文件
python3 agent.py export /tmp/research-draft.json --out /tmp/research-report.md
```

若需要退回，使用 `--decision reject --comment "需要补充来源"`。退回后可编辑草稿，再由人重新执行 `review`。`reviewer` 是示例输入，不经过身份验证；真实系统应连接自己的登录和审计机制。

## 输入与状态

事实库是本地 JSON 数组，每条需有 `id`、`title`、`statement` 和 HTTPS `source_url`。参考 [虚构事实库](examples/facts.json)。`prepare` 用问题与标题、陈述中的词项重合度挑选最多三条事实，然后只把被选事实写入草稿；找不到匹配证据时停止，不编造答案。

输出状态文件包含：

| 字段 | 说明 |
| --- | --- |
| `question` | 用户的问题 |
| `facts` | 本轮选中的事实及来源地址 |
| `draft` | 带 `[source:id]` 标记的段落与待核实提示 |
| `stage` | `needs_review`、`rejected` 或 `approved` |
| `review` | 复核决定、复核人、意见、时间和草稿 SHA-256 |

`export` 会重新计算问题、事实和草稿的摘要值；如果批准后任意一项改变，就拒绝导出。这个机制展示“批准绑定具体版本”的做法，但 JSON 状态文件本身**不防恶意篡改**，不能替代生产审计日志或数字签名。

## 接入自己的智能体

1. 用自己的检索器替换 `prepare` 中的简单词项匹配，并让每个事实保留可核对的来源 ID。
2. 用模型或模板替换草稿生成，但保留来源标记、证据不足时停止的规则。
3. 把 `review` 命令换成真实人员登录后的复核界面；退回时收集具体修改意见。
4. 把 `export` 的检查放在真正的导出或发布动作**之前**，并让批准记录绑定草稿版本。
5. 对真实业务增加事实核验、引用有效性、敏感信息和权限检查；这些都超出本示例范围。

运行 `python3 -m unittest discover -s tests -v` 可看到未批准、退回、批准后改稿等关键门禁的测试。命令成功返回 `0`，输入或流程错误返回 `2`。所有动作都只读写本地文件，不会自动发布到网络。

## 隐私与发布边界

仓库不包含真实研究材料、知识库结构、内部接口、模型密钥或业务流程配置。示例事实全部是虚构的；将来接入真实数据时，请勿把状态文件、人工意见或模型请求日志提交到公开仓库。

这是独立项目，不继承原业务仓库历史。代码采用 [GPL-3.0-only 许可证](LICENSE)；公开仓库位于 [workstonedai-collab/human-review-research-agent](https://github.com/workstonedai-collab/human-review-research-agent)。
