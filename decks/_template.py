# -*- coding: utf-8 -*-
"""新课件模板：复制本文件改名，改 TITLE/OUT_STEM，往 SLIDES 里堆内容。
构建：python scripts\\build.py decks\\你的课件.py（import 路径由 build.py 准备）
"""
from bento_lib import (T, S, card, table, page_token, step_chain, slide,
                       CREAM, INK, DARK, IKB, IKB_LT, WHITE)

TITLE = "课件标题"
OUT_STEM = r"D:\AI数字素养培训方案\<课程目录>\bento\课件名"  # 产物路径（不带扩展名）

SLIDES = [
    # 封面（IKB 大字 + 奶油条 + 电影感动态背景；ambient 可选 blue/warm/dark，不想要就删掉）
    slide("s-cover", IKB, "none", "演讲者备注写在这里", [
        T("k1", 96, 56, 600, 26, "KICKER · 课程系列", 15, 600,
          "rgba(244,241,234,0.7)", ls=3),
        T("t1", 96, 240, 1088, 130, "主标题", 100, 900, CREAM, lh=1.05,
          fx={"enter": "fade-up", "order": 0}),
        S("bar", 96, 420, 320, 16, "rect", CREAM),
        T("sub", 96, 464, 1088, 40, "一句副标题", 24, 500,
          "rgba(244,241,234,0.85)", fx={"enter": "fade-up", "order": 1}),
    ], ambient="blue"),
    # 内容页（奶油底：kicker + 标题 + 三卡片）
    slide("s-cards", CREAM, "fade", "备注", [
        T("k2", 96, 56, 600, 24, "SECTION · 小节名", 14, 600,
          "rgba(26,26,24,0.5)", ls=3),
        T("t2", 96, 100, 900, 56, "页面标题", 40, 800, INK),
        *[e for i, (ct, cd) in enumerate([
            ("要点一", "说明文字"), ("要点二", "说明文字"), ("要点三", "说明文字")])
          for e in [
            card(96 + i * 371, 200, 346, 280, WHITE, "rgba(26,26,24,0.08)", 1),
            T(f"ct{i}", 96 + i * 371 + 28, 228, 290, 34, ct, 22, 800, INK),
            T(f"cd{i}", 96 + i * 371 + 28, 276, 290, 150, cd, 15, 500,
              "rgba(26,26,24,0.6)", lh=1.6)]],
        page_token(),
    ]),
    # 深色步骤链页（morph 示例：下一页 hl_idx 变化即滑动）
    slide("s-chain", DARK, "fade", "备注", [
        T("k3", 96, 100, 700, 24, "FLOW · 步骤", 14, 600,
          "rgba(244,241,234,0.55)", ls=3),
        T("t3", 96, 145, 1000, 56, "流程标题", 40, 800, CREAM),
        *step_chain(["第一步", "第二步", "第三步"], True, CREAM, CREAM,
                    "rgba(244,241,234,0.18)", hl_idx=0, hl_c=IKB_LT,
                    hl_op=0, enter=True),
        page_token("rgba(244,241,234,0.4)"),
    ]),
    slide("s-step1", DARK, "morph", "备注（链条收顶，高亮圈亮起）", [
        *step_chain(["第一步", "第二步", "第三步"], False, CREAM,
                    "rgba(244,241,234,0.75)", "rgba(244,241,234,0.18)",
                    hl_idx=0, hl_c=IKB_LT),
        T("k4", 96, 210, 600, 24, "STEP 01 · 第一步", 14, 600, IKB_LT, ls=3),
        T("t4", 96, 244, 1088, 56, "第一步讲什么", 38, 800, CREAM),
        page_token("rgba(244,241,234,0.4)"),
    ]),
]
