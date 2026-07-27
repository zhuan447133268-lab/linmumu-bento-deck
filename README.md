# bento-deck skill

> Claude Code skill：把课件内容生成 `.bento.html` —— 自带编辑器的单文件课件（IKB 克莱因蓝风格）
> 基于 [nyblnet/bento](https://github.com/nyblnet/bento)（MIT）官方壳与文档格式；样式系统与工作流为本仓库原创

## 是什么

一句话需求（"帮我做个 PPT，给 XX 讲 XX"）→ 双版本产物：

- `xxx.bento.html` —— 可编辑版：双击打开就是全中文编辑器（文本/形状/表格/图表/批注都能改），保存自写回文件
- `xxx.play.bento.html` —— 放映版：双击直接进演示，← → 翻页，morph 步骤链动画、演讲者备注内置

## 安装

```bash
# 整个目录放进 Claude skills 目录即完成安装
git clone https://github.com/zhuan447133268-lab/linmumu-bento-deck.git
# 或下载解压到：C:\Users\<你>\.claude\skills\bento-deck\
```

依赖：Python 3.10+；截图抽验需 `pip install playwright` + `playwright install chromium`（不装也能生成，只是没有抽验步骤）。官方壳首次构建时自动下载（也可预置在 `scripts/shell/`）。

## 用法

```
python scripts\build.py decks\<你的课件>.py        # 构建双版本（自带校验）
python scripts\verify_shots.py <放映版> <页数>     # 截图抽验
```

新课件从 `decks/_template.py` 抄：deck 文件是纯 Python 数据（`TITLE`/`OUT_STEM`/`SLIDES`），元素级 API 看 `bento_lib.py` 与 `SKILL.md`。

## 样式系统（IKB 克莱因蓝）

| 令牌 | 值 | 用途 |
|---|---|---|
| `CREAM` | `#F4F1EA` | 奶油底（内容页） |
| `INK` | `#1A1A18` | 墨（浅底正文） |
| `DARK` | `#17171C` | 深色页底 |
| `IKB` | `#002FA7` | 克莱因蓝（浅底 accent/封面） |
| `IKB_LT` | `#7AA5FF` | 亮蓝（深底 accent） |

版式：1280×720 画布、96px 边距、kicker 14px/ls3、页标题 38-40px/800、三卡 x=96/467/838 宽 346。

## 组件

- `T()` 文本 / `S()` 形状 / `card()` 圆角卡 / `table()` 表格 / `page_token()` 动态页码
- `step_chain(labels, big, ...)` —— 步骤链 morph 组件：多页共享 id，`hl_idx` 变化高亮圈滑动，`big` 切换幕封大版↔顶部迷你版，深浅页颜色渐变

## 目录

```
bento-deck/
├─ SKILL.md            # Claude skill 主文件（触发词+工作流+坑清单）
├─ README.md           # 本文件
├─ scripts/
│  ├─ bento_lib.py     # 核心库（样式+元素+组件+splice 校验）
│  ├─ build.py         # 构建 CLI（出双版本）
│  ├─ verify_shots.py  # 截图抽验
│  └─ shell/           # 官方壳缓存（gitignore，缺了自动下载）
└─ decks/
   ├─ _template.py     # 新课件模板
   └─ *.py             # 实际课件内容（gitignore，课件是私有内容）
```

## License & Credits

本仓库工作流与样式系统：MIT。bento 壳与格式：[nyblnet/bento](https://github.com/nyblnet/bento)，MIT。
视觉风格灵感参考 [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)（AGPL v3，本项目未使用其代码）。
