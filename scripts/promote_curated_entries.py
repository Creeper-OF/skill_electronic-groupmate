#!/usr/bin/env python3
"""Promote a curated starter set into reviewed runtime meme libraries."""

from __future__ import annotations

import json
import pathlib
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
MEME_DIR = ROOT / "references" / "memes"
TODAY = "2026-06-10"
SOURCE_GENG = "https://github.com/MonloHua/geng-skill"
SOURCE_MOEGIRL = "https://zh.moegirl.org.cn/"


def entry(
    *,
    id: str,
    name: str,
    category: str,
    summary: str,
    keywords: list[str],
    trigger_contexts: list[str],
    suitable: list[str],
    unsuitable: list[str],
    example_usage: list[str],
    aliases: list[str] | None = None,
    source_circle: str = "Chinese internet",
    usage_style: list[str] | None = None,
    freshness: str = "recent",
    intensity: int = 2,
    risk: str = "low",
    requires_user_familiarity: bool = False,
    source_urls: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": id,
        "name": name,
        "aliases": aliases or [name],
        "category": category,
        "source_circle": source_circle,
        "summary": summary,
        "keywords": keywords,
        "trigger_contexts": trigger_contexts,
        "suitable": suitable,
        "unsuitable": unsuitable,
        "usage_style": usage_style or ["reaction_phrase", "paraphrase"],
        "freshness": freshness,
        "intensity": intensity,
        "risk": risk,
        "requires_user_familiarity": requires_user_familiarity,
        "example_usage": example_usage,
        "source_urls": source_urls or [SOURCE_GENG],
        "license_note": "候选资料参考 geng-skill、萌娘百科或公开社区用法；本条目为项目整理/改写，来源见 source_urls。",
        "review_status": "reviewed",
        "last_reviewed": TODAY,
    }
    if extra:
        data.update(extra)
    return data


CURATED = [
    entry(
        id="general-cat-meme",
        name="猫meme",
        category="general",
        aliases=["猫猫meme", "cat meme"],
        source_circle="Short-video / global meme community",
        summary="以猫为主角的表情包或短视频梗，常用于表达委屈、震惊、发呆、开心等情绪。",
        keywords=["猫", "表情包", "反应图", "可爱", "委屈"],
        trigger_contexts=["需要轻量反应", "用户发出可爱或离谱内容", "低风险闲聊"],
        suitable=["闲聊", "轻松吐槽", "表达无害情绪"],
        unsuitable=["正式文档", "严肃事故", "用户正在焦虑"],
        example_usage=["这日志看起来像猫meme，表面无辜，背地里把路径全吃了。"],
    ),
    entry(
        id="general-ordinary-person",
        name="普通人",
        category="general",
        summary="用来表达普通、自嘲或反讽的网络表达，常带摆烂和无奈感。",
        keywords=["普通", "自嘲", "摆烂", "无奈"],
        trigger_contexts=["用户自嘲", "能力或表现被拿来轻松比较", "低风险闲聊"],
        suitable=["自嘲", "轻松反讽", "降低姿态"],
        unsuitable=["攻击用户能力", "正式评价", "用户明显受挫"],
        example_usage=["我也是普通人，看到这种正则第一眼也会选择先沉默三秒。"],
    ),
    entry(
        id="general-dry-goods",
        name="干货",
        category="general",
        summary="指有价值、实用、少废话的信息或内容。",
        keywords=["实用", "有价值", "少废话", "信息密度"],
        trigger_contexts=["总结方案", "给出可执行步骤", "用户需要重点"],
        suitable=["技术说明", "教程总结", "信息筛选"],
        unsuitable=["纯闲聊硬装专业", "内容其实很水"],
        example_usage=["先上干货：问题在端口没放行，代码本身没炸。"],
        usage_style=["paraphrase"],
        intensity=1,
    ),
    entry(
        id="general-cheems",
        name="cheems",
        category="general",
        aliases=["芝士狗", "Cheems"],
        source_circle="Global meme / Chinese internet",
        summary="柴犬表情包形象，常用于委屈、怂、嘴硬或弱小但努力的语境。",
        keywords=["柴犬", "委屈", "嘴硬", "怂"],
        trigger_contexts=["自嘲", "轻微失败", "用户接受表情包语境"],
        suitable=["失败后装怂", "轻松自嘲", "缓和气氛"],
        unsuitable=["真实重大失败", "严肃道歉", "用户不熟悉表情包"],
        example_usage=["刚才判断错了，我现在像 cheems 一样缩回去重看日志。"],
        requires_user_familiarity=True,
    ),
    entry(
        id="general-hakimi",
        name="哈基米",
        category="general",
        summary="用来形容可爱、萌或让人心软的对象，常带撒娇和短视频语气。",
        keywords=["可爱", "萌", "心软", "短视频"],
        trigger_contexts=["用户展示可爱事物", "轻松夸赞", "非技术核心内容"],
        suitable=["闲聊", "夸可爱", "轻松反应"],
        unsuitable=["正式技术结论", "用户需要严肃帮助"],
        example_usage=["这个小动画按钮有点哈基米，能用，但别影响主流程。"],
        intensity=1,
    ),
    entry(
        id="general-snow-icecream-assassin",
        name="雪糕刺客",
        category="general",
        summary="指外表普通但价格或代价突然很高的东西，常用于调侃隐藏成本。",
        keywords=["隐藏成本", "价格离谱", "猝不及防", "成本"],
        trigger_contexts=["发现隐形成本", "依赖或服务价格高", "方案代价超预期"],
        suitable=["技术方案成本提醒", "轻松吐槽价格", "风险提示"],
        unsuitable=["真实财产损失", "正式报价文件"],
        example_usage=["这个云服务看着像普通依赖，账单一出来就是雪糕刺客。"],
        usage_style=["analogy", "paraphrase"],
    ),
    entry(
        id="general-elegant",
        name="优雅",
        category="general",
        aliases=["优雅，实在是太优雅了"],
        summary="用反差语气称赞或调侃某种混乱、粗暴但莫名有效的做法。",
        keywords=["反讽", "优雅", "混乱", "粗暴有效"],
        trigger_contexts=["方案很粗暴但能跑", "用户轻松接受调侃", "低风险已解决"],
        suitable=["轻微反讽", "调侃 workaround", "代码能跑但不漂亮"],
        unsuitable=["正式 code review 结论", "高风险系统"],
        example_usage=["这个修法能跑，但属于优雅，实在是太优雅了，后面最好重构一下。"],
        usage_style=["reaction_phrase", "paraphrase"],
    ),
    entry(
        id="general-macarthur-documentary",
        name="麦克阿瑟",
        category="general",
        aliases=["麦克阿瑟曾表示", "大型纪录片"],
        summary="用纪录片口吻或名人评价格式调侃某件事很离谱、很经典或值得记录。",
        keywords=["大型纪录片", "曾表示", "经典场面", "调侃"],
        trigger_contexts=["出现经典离谱场面", "用户接受抽象旁白", "问题已定位"],
        suitable=["总结反转", "调侃 bug 名场面", "闲聊"],
        unsuitable=["正式报告", "真实事故追责"],
        example_usage=["大型纪录片《一个空格引发的半小时排查》，麦克阿瑟看了都得沉默。"],
        requires_user_familiarity=True,
    ),
    entry(
        id="games-zero-frame-starter",
        name="零帧起手",
        category="games",
        summary="原指游戏中没有前摇、瞬间出手的招式，后引申为毫无预兆地开始行动。",
        keywords=["突然出手", "无前摇", "游戏术语", "抢先"],
        trigger_contexts=["程序或用户突然执行动作", "响应过快或无提示", "轻松类比"],
        suitable=["游戏语境", "技术流程突然触发", "形容无预警行为"],
        unsuitable=["真实攻击或安全事件", "用户不懂游戏梗"],
        example_usage=["这个脚本零帧起手，配置还没读完就开始连数据库了。"],
        usage_style=["analogy", "paraphrase"],
        requires_user_familiarity=True,
    ),
    entry(
        id="games-lao-liu",
        name="老六",
        category="games",
        summary="源自游戏语境，指不按常规套路、躲着阴人或出其不意的人或操作。",
        keywords=["偷袭", "阴人", "不按套路", "出其不意"],
        trigger_contexts=["隐藏问题突然出现", "配置项暗中影响结果", "用户熟悉游戏语境"],
        suitable=["调侃隐藏坑", "低风险排障", "游戏相关话题"],
        unsuitable=["攻击用户人格", "正式事故分析"],
        example_usage=["这个环境变量是真老六，平时不吭声，运行时直接改行为。"],
        usage_style=["analogy", "paraphrase"],
        requires_user_familiarity=True,
    ),
    entry(
        id="anime-chu-fanatic",
        name="厨",
        category="anime",
        aliases=["xx厨"],
        source_circle="ACGN / Japanese internet",
        summary="指对某作品、角色或事物极度狂热的人，中文网络中也可中性或自嘲使用。",
        keywords=["粉丝", "狂热", "推", "ACG"],
        trigger_contexts=["用户谈到强偏好", "ACG 语境", "自称或轻松调侃"],
        suitable=["自嘲式偏好", "圈内闲聊", "描述热爱"],
        unsuitable=["贬低用户爱好", "严肃争论", "陌生人标签化"],
        example_usage=["你这套主题配色一看就是深色模式厨，按钮都不肯亮一点。"],
        usage_style=["paraphrase"],
        requires_user_familiarity=True,
    ),
    entry(
        id="guichu-super-idol",
        name="热爱105℃的你",
        category="guichu",
        aliases=["Super Idol", "Super Idol的笑容"],
        source_circle="Chinese short video / Bilibili remix",
        summary="洗脑歌曲相关梗，常用于鬼畜、空耳、魔性循环或过度甜美的反差场景。",
        keywords=["Super Idol", "洗脑", "鬼畜", "循环"],
        trigger_contexts=["重复播放", "魔性循环", "用户熟悉 B 站鬼畜文化"],
        suitable=["调侃循环", "轻松吐槽魔性内容", "鬼畜语境"],
        unsuitable=["正式技术说明", "用户不熟悉老梗"],
        example_usage=["这个 watcher 一改文件就重跑，已经开始 Super Idol 循环了。"],
        usage_style=["analogy", "paraphrase"],
        requires_user_familiarity=True,
    ),
    entry(
        id="tuwei-background-fake",
        name="你这背景太假了",
        category="tuwei",
        summary="源自短视频评论语境，用来调侃画面或场景好到像假的，也可反向吐槽过于离谱。",
        keywords=["背景太假", "短视频", "反差", "离谱"],
        trigger_contexts=["视觉效果过于夸张", "界面或截图很像合成", "轻松评价"],
        suitable=["UI 截图调侃", "视觉效果闲聊", "短视频语境"],
        unsuitable=["正式设计评审", "用户认真求改稿"],
        example_usage=["这个渐变加阴影一上来，你这背景太假了，像模板站开了十倍美颜。"],
        requires_user_familiarity=True,
    ),
    entry(
        id="bad-memes-ji-ni-tai-mei",
        name="鸡你太美",
        category="bad_memes",
        aliases=["只因你太美", "蔡徐坤篮球"],
        source_circle="Chinese internet / Bilibili meme",
        summary="经典空耳和鬼畜化流行梗，因传播过度已经带有烂梗属性。",
        keywords=["只因你太美", "空耳", "烂梗", "鬼畜"],
        trigger_contexts=["用户明确接受烂梗", "需要故意老土或尴尬的节目效果", "低风险闲聊"],
        suitable=["烂梗模式", "抽象测试字符串", "用户主动提到相关梗"],
        unsuitable=["默认技术回答", "攻击具体真人", "正式内容"],
        example_usage=["这变量名再叫 `jntm` 就有点鸡你太美了，建议换个正常点的。"],
        usage_style=["reaction_phrase", "paraphrase"],
        freshness="stale",
        intensity=4,
        risk="medium",
        requires_user_familiarity=True,
    ),
    entry(
        id="roast-liu-huaqiang-watermelon",
        name="刘华强买瓜",
        category="roasts",
        aliases=["这瓜保熟吗"],
        source_circle="Chinese TV drama / internet meme",
        summary="用来调侃质疑、找茬或测试真假，语气像在问对方承诺是否靠谱。",
        keywords=["保熟吗", "质疑", "找茬", "测试真假"],
        trigger_contexts=["用户要求确认可靠性", "配置或结果需要验证", "熟人式调侃"],
        suitable=["轻松质疑方案", "提醒验证结果", "调侃承诺不可靠"],
        unsuitable=["真实威胁语境", "正式验收", "陌生用户"],
        example_usage=["你说这个脚本稳定？这脚本保熟吗，先跑一轮测试再说。"],
        usage_style=["structural_meme", "paraphrase"],
        risk="medium",
        requires_user_familiarity=True,
        extra={
            "roast_formula": "is_this_reliable_like_watermelon_check",
            "deescalation": "不是找茬，先验证一下更稳。",
            "target_policy": "claim_or_solution",
        },
    ),
    entry(
        id="roast-not-bro",
        name="不是哥们",
        category="roasts",
        aliases=["不是吧哥们", "等一下哥们"],
        source_circle="Chinese internet / group chat",
        summary="表达惊讶、无语或难以置信，适合熟人间轻度小怼。",
        keywords=["无语", "难绷", "你认真的吗", "小怼"],
        trigger_contexts=["用户做出离谱但低风险的操作", "轻松纠错", "熟人语气"],
        suitable=["轻度压力", "指出明显问题", "先纠错再解释"],
        unsuitable=["用户焦虑", "重大错误", "攻击用户智力"],
        example_usage=["不是哥们，你把 token 写进截图里发出来了，先撤回再说。"],
        usage_style=["reaction_phrase"],
        risk="medium",
        requires_user_familiarity=True,
        extra={
            "roast_formula": "not_bro_then_point_out_issue",
            "deescalation": "先别急，我说修法。",
            "target_policy": "operation_or_situation",
        },
    ),
    entry(
        id="roast-human-high-quality-male",
        name="人类高质量男性",
        category="roasts",
        summary="用来调侃自视甚高、包装过度或形式感太强的表达。",
        keywords=["自视甚高", "包装过度", "形式感", "反差"],
        trigger_contexts=["内容包装大于实际", "用户要求嘴炮风格", "低风险调侃"],
        suitable=["调侃过度营销", "吐槽浮夸介绍", "熟人语境"],
        unsuitable=["人身攻击", "正式评价个人", "陌生用户"],
        example_usage=["这个 README 标题写得像人类高质量男性，实际安装命令还没放。"],
        usage_style=["analogy", "paraphrase"],
        risk="medium",
        requires_user_familiarity=True,
        extra={
            "roast_formula": "overpackaged_thing_as_high_quality_persona",
            "deescalation": "包装可以留一点，但先把实用信息补上。",
            "target_policy": "content_or_presentation",
        },
    ),
]


def read_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: pathlib.Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in CURATED:
        grouped.setdefault(item["category"], []).append(item)

    for category, additions in sorted(grouped.items()):
        path = MEME_DIR / f"{category}.jsonl"
        existing = read_jsonl(path)
        by_id = {row["id"]: row for row in existing}
        for addition in additions:
            by_id[addition["id"]] = addition
        merged = list(by_id.values())
        write_jsonl(path, merged)
        print(f"{category}: {len(existing)} -> {len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
