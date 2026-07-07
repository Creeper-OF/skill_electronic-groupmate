# electronic-groupmate

一个中文 Codex Skill，目标是让 Codex 更像技术群里的正常群友：

- 先把正事干完，再看气氛玩不玩梗。
- 能用中文互联网梗、轻微吐槽、群聊语气和一点点嘴臭。
- 不强行每句话发病，也不把严肃问题当笑话。
- 会区分普通闲聊、技术排障、脏话、创意嘴炮和安全边界。

简单说：不是“随机热词生成器”，而是“知道什么时候闭嘴、什么时候说人话、什么时候补一句草”的 Skill。

## 现在有什么

- `SKILL.md`：Skill 入口和运行规则。
- `references/groupmate-voice.md`：群友感说话说明书。
- `references/router.md`：判断本轮该正经、口语化、玩梗还是嘴炮。
- `references/safety.md`：不该玩梗/不该嘴臭的场景。
- `references/profanity.md`：脏话使用说明书。
- `references/roastcraft.md`：有梗的压力式调侃和装怂机制。
- `references/persona-boundaries.md`：防止跑成电子女友、认爹、主仆、小弟或违法整活。
- `references/bot-runtime-prompt.md`：给普通群机器人后台直接粘贴的运行提示词。
- `references/memes/*.jsonl`：已审核的运行时梗库。
- `scripts/`：爬取候选、导入外部梗库、生成草稿、校验条目的工具脚本。

## 数据状态

当前正式运行库是小而精的 reviewed 版本，不是全量大库。爬取和分类过程中产生的原始数据默认放在仓库外：

```text
D:\Arduino\src\Skill\electronic-groupmate-crawl-data
```

正式 Skill 只带 `references/memes/*.jsonl` 里的 reviewed 条目，避免把 raw 数据和噪声一起塞进上下文。

## 本地校验

```powershell
python scripts/validate_meme_entries.py references/memes/*.jsonl
```

如果使用 Codex 的 skill-creator 校验脚本，可以像之前一样用独立 venv 跑：

```powershell
$env:PYTHONUTF8='1'
D:\DEV\electronic-groupmate-tools\.venv\Scripts\python.exe C:\Users\34773\.codex\skills\.system\skill-creator\scripts\quick_validate.py .
```

## 设计原则

1. 每轮判断，不是每轮玩梗。
2. 技术问题先解决问题，再制造节目效果。
3. 脏话和嘴炮是可选调料，不是默认人格。
4. 优先调侃 bug、配置、路径、场面，别攻击用户本人。
5. 用户认真时跟着认真，用户抽象时再适度抽象。

## 来源说明

候选资料可能参考萌娘百科、geng-skill、维基词典和公开社区用法。正式条目会尽量保留来源 URL，并以项目整理/改写后的结构化条目进入运行库。

代码按 MIT 许可证发布。数据条目请看 `DATA_NOTICE.md`。
