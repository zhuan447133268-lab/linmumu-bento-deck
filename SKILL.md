---
name: bento-deck
description: 生成 bento 单文件可编辑课件/PPT（IKB 克莱因蓝风格，成品自带中文编辑器+morph 动画+演讲者备注）。当用户说"做个PPT""做个课件""帮我做幻灯片/演示文稿""写个培训课件""做个deck"，或要把内容做成发给别人、对方还能改的演示文件时，必须使用本技能。即使用户只说"帮我准备个分享""把这个大纲做成能讲的"，也应主动使用。也用于迭代已有 bento 课件（改 decks/*.py 重新构建）。Use when the user asks for a slide deck, presentation, PPT, or courseware as an editable single-file HTML.
---

# bento-deck · 单文件可编辑课件生成

生成 `.bento.html`：一个自带查看/演示/**编辑器**的单文件课件（收到的人双击就能改内容）。基于 nyblnet/bento 官方壳与格式（MIT），样式系统是我们的。

## 第 0 步：管线选择（先判断，拿不准就反问）

| 需求特征 | 走哪条 |
|---|---|
| 默认；要发给老师/学员、对方可能要改；要演讲者备注；培训课件 | **本技能（bento）** |
| 对外展示、要视觉冲击力、瑞士排版/杂志风/WebGL 背景、章节幕封 | 改走 **guizang-ppt-skill** |
| 同一份内容两个出口都要 | 先 bento（快），再排期瑞士版（慢工） |

## 工作流（5 步，缺一不可）

1. **需求确认**。必有：主题 + 受众。缺了反问，不瞎猜。加分项：时长/页数、现成素材（大纲/旧课件/文档）、要不要对方可编辑、风格偏好（不说 = 默认 IKB 奶油风）。
2. **内容稿过目**。先出页纲（每页：标题+要点+版式选择+备注思路）给用户确认，**再动手写 deck 文件**。有现成素材时先提取（按客观事实，不编造内容）。
3. **构建**。复制 `decks/_template.py` 为 `decks/<topic>.py`，改 `TITLE`/`OUT_STEM`（产物路径指向课程目录），往 `SLIDES` 堆页，然后：
   ```
   python C:\Users\dfjq\.claude\skills\bento-deck\scripts\build.py C:\Users\dfjq\.claude\skills\bento-deck\decks\<topic>.py
   ```
   产物自动出双版本：`xxx.bento.html`（可编辑）+ `xxx.play.bento.html`（readonly 放映）。构建脚本自带回读校验，报错先读断言信息。
4. **截图抽验**（不可省）：
   ```
   python C:\Users\dfjq\.claude\skills\bento-deck\scripts\verify_shots.py <放映版路径> <总页数> [抽验页码,逗号分隔] [输出目录]
   ```
   必看：封面、含 morph 链的页、表格页、末页。发现溢出/重叠/跑版 → 改 deck 文件重建。
5. **交付**。给：双版本文件路径 + 抽验截图 + 一句话使用说明（可编辑版发给对方能改；放映版双击直接演示；← → 翻页）。迭代 = 改 deck 文件重跑第 3-4 步。

## deck 文件结构（数据即内容）

deck 文件是纯 Python 数据：`TITLE` / `OUT_STEM` / `SLIDES`（可选 `AUTHOR`/`EVENT`/`MODIFIED`）。每页：

```python
slide("s-id", 底色, 切换效果, 演讲者备注, [元素...])
```

- 底色：`CREAM`（奶油，内容页）/ `DARK`（深色 statement 页）/ `IKB`（克莱因蓝，封面收尾）
- 切换：`none`/`fade`/`morph` —— **写在"到达页"上**
- 元素：`T()`文本 / `S()`形状 / `card()`圆角卡 / `table()`表格 / `page_token()`动态页码 / `step_chain()`步骤链
- 每页必写演讲者备注（第 3 参数）——它随文件走，演示视图可见

## step_chain：招牌 morph 组件

同一套 labels 在多页复用 → 共享 id → morph 自动生效：

- `hl_idx` 变化（高亮哪一步）→ 高亮圈**滑动**
- `big=True`（幕封大版）↔ `False`（顶部迷你版）→ 链条**收放**
- 深浅页描边配色不同 → **渐变色**过渡
- 经典结构（看 `decks/personal_skill.py` 06→09 页）：幕封大链(hl_op=0 隐身) → 迷你链+hl亮起 → 内容页 hl 逐步右移

一套幻灯片里**只能用一条链**（内部 id 固定：cline/n1../l1../hl）。

## 坑（踩过的，别再踩）

1. `<` 会转义成 `\u003c`（`splice()` 统一处理）——**别手改产物文件里的 JSON 块**，要改就改 deck 文件重建
2. 页码用 `page_token()` 动态令牌，内置 Reveal 页码已默认关闭（`slideNumber:false`），别两个都开
3. morph 靠**同 id 逐字符一致**；不同 id = 直接切换不动画
4. `T()` 的 html 只认内联白名单（b/i/u/s/code/br/span），块级标签被过滤
5. 深底 accent 用 `IKB_LT`（#7AA5FF），`IKB`（#002FA7）在深底上看不清
6. 版式规矩：边距 96px（内容 x≤1184）；kicker 14px 字距 3；页标题 38-40px/800；封面 100px/900；三卡 x=96/467/838 宽 346

## 样式令牌（bento_lib 常量，别临场发明新色）

`CREAM #F4F1EA` · `INK #1A1A18` · `DARK #17171C` · `IKB #002FA7` · `IKB_LT #7AA5FF` · `FONT`（system-ui+雅黑+PingFang）

## 路径

- 引擎：`scripts/bento_lib.py`（样式+组件+splice 校验）、`scripts/build.py`、`scripts/verify_shots.py`
- 模板：`decks/_template.py`
- 官方壳：`scripts/shell/`（删了自动重下）
- 样式细则与组件 API：同目录 `README.md`
- bento 官方格式规范（全字段）：https://bento.page/agents.md
