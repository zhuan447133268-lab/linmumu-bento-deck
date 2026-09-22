# -*- coding: utf-8 -*-
"""
bento_lib — bento/slides 课件生成核心库（林木木课件工坊 · bento 出口）

样式系统：奶油底 CREAM / 墨 INK / 深色 DARK / 克莱因蓝 IKB（与瑞士风课件同色相）
用法：decks/*.py 里只写内容（slides 数据），build.py 负责 splice+校验+出双版本。

硬规则（来自 bento 官方 format.md，违反即坏文件）：
  1. JSON 写入文件前，所有 < 转义为 <（本库 splice 内统一处理）
  2. 元素 id 即身份：morph 靠跨页同 id；生成器必须给确定性 id
  3. 新文档不写 docId / collab（App 首开自动铸造）
  4. 内置 Reveal 页码与 {{page}} 令牌二选一——本库默认关内置（slideNumber:false）
"""
import json, re, sys, urllib.request
from urllib.parse import quote
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ---------- 样式常量 ----------
CREAM = "#F4F1EA"   # 奶油底（浅色页）
INK = "#1A1A18"     # 墨（浅底正文）
DARK = "#17171C"    # 深色页底
IKB = "#002FA7"     # 克莱因蓝（浅底 accent）
IKB_LT = "#7AA5FF"  # 深底上的亮蓝（同色相高明度）
WHITE = "#FFFFFF"
FONT = "system-ui, 'Microsoft YaHei', 'PingFang SC', sans-serif"

PAGE_W, PAGE_H, MARGIN = 1280, 720, 96   # 画布与页边距（官方守护线：内容 x ≤ 1184）

SHELL_PATH = Path(__file__).parent / "shell" / "Bento_Slides.bento.html"
SHELL_URL = "https://bento.page/releases/slides/Bento_Slides.bento.html"


# ---------- 元素构建 ----------
def T(id, x, y, w, h, html, size, weight, color, align="left", valign="top",
      lh=1.2, fx=None, ls=None):
    """文本元素。html 支持内联 <b> <i> <br> <code> <span>（会被统一转义，放心写）。"""
    e = {"id": id, "type": "text", "x": x, "y": y, "w": w, "h": h,
         "rotation": 0, "opacity": 1, "html": html, "fontSize": size,
         "fontFamily": FONT, "fontWeight": weight, "color": color,
         "align": align, "valign": valign, "lineHeight": lh}
    if fx: e["fx"] = fx
    if ls: e["letterSpacing"] = ls
    return e


def S(id, x, y, w, h, shape, fill, stroke="none", sw=0, radius=0,
      fx=None, opacity=1, ss=None):
    """形状元素。shape: rect|ellipse|triangle|arrow|line|path。"""
    e = {"id": id, "type": "shape", "shape": shape, "x": x, "y": y, "w": w,
         "h": h, "rotation": 0, "opacity": opacity, "fill": fill,
         "stroke": stroke, "strokeWidth": sw, "radius": radius}
    if fx: e["fx"] = fx
    if ss: e["strokeStyle"] = ss
    return e


def card(x, y, w, h, fill, stroke="none", sw=0, radius=12, id=None):
    """圆角卡片底。id 缺省按坐标生成（确定性）。"""
    return S(id or f"c{x}_{y}", x, y, w, h, "rect", fill, stroke, sw, radius)


def table(id, x, y, w, h, header_cells, rows, col_weights,
          font_size=15, pad_y=10, header_bg=INK, accent=IKB):
    """表格元素。rows: [[cell, ...]]；cell 为 str 或 {"html","bold","align",...}。"""
    def norm(c):
        return {"html": c} if isinstance(c, str) else c
    return {
        "id": id, "type": "table", "x": x, "y": y, "w": w, "h": h,
        "rotation": 0, "opacity": 1, "header": True,
        "columns": [{"w": cw} for cw in col_weights],
        "rows": [{"cells": [norm(c) for c in r]}
                 for r in [header_cells] + rows],
        "style": {"headerBg": header_bg, "headerColor": CREAM,
                  "zebra": f"rgba(0,47,167,0.05)" if accent == IKB else "rgba(0,0,0,0.04)",
                  "borderColor": "rgba(26,26,24,0.12)", "borderWidth": 1,
                  "cellPadX": 18, "cellPadY": pad_y, "fontSize": font_size,
                  "color": INK, "radius": 10},
    }


def page_token(color="rgba(26,26,24,0.4)"):
    """右下角页码（动态令牌，页序变了自动重排）。"""
    return T("pg", 1090, 662, 94, 22, "{{page:2}} / {{pages:2}}", 12, 500,
             color, align="right")


# ---------- 步骤链（morph 组件）----------
def step_chain(labels, big, stroke_c, label_c, line_c, hl_idx=None,
               hl_c=None, hl_op=1, enter=False):
    """一条步骤链：圆点 + 文字 + 可选高亮圈。
    跨页复用时保持 labels 一致 → 共享 id（cline/n1..nN/l1..lN/hl）→ morph 自动生效：
      - 高亮圈位置变化（hl_idx 不同）会滑动
      - 大版(big=True 居中) ↔ 迷你版(big=False 顶部) 会收放
      - 描边/文字颜色变化（深↔浅页）会渐变色
    """
    n = len(labels)
    cxs = [round(150 + i * (933 / (n - 1))) for i in range(n)]
    if big:
        cy, r, lab_y, lab_s = 368, 12, 408, 18
    else:
        cy, r, lab_y, lab_s = 108, 10, 136, 13
    els = [S("cline", cxs[0], cy + r - 1, cxs[-1] - cxs[0], 3 if big else 2,
             "line", line_c)]
    for i, cx in enumerate(cxs):
        fx = {"enter": "fade-up", "order": i} if enter else None
        els.append(S(f"n{i+1}", cx - r, cy, r * 2, r * 2, "ellipse",
                     "transparent", stroke_c, 2, fx=fx))
        els.append(T(f"l{i+1}", cx - 77, lab_y, 154, 30 if big else 24,
                     labels[i], lab_s, 700 if big else 600, label_c,
                     align="center"))
    if hl_idx is not None:
        rr = r + 6
        els.append(S("hl", cxs[hl_idx] - rr, cy - 6, rr * 2, rr * 2,
                     "ellipse", "transparent", hl_c, 3, opacity=hl_op))
    return els


# ---------- 电影感动态背景（ambient，零改壳）----------
# 用官方 image 元素 + data-URI 动画 SVG 实现 Kage 式电影感背景。
# 三款配色：blue(克莱因蓝) / warm(暖绘本) / dark(近黑深空蓝)。
# 背景 SVG 内嵌 SMIL 动画，不依赖外壳引擎，编辑版/放映版都能播。
def _svg_ambient(variant):
    palettes = {
        "blue": dict(c0="#1a4bd0", c1="#002FA7", c2="#001a63",
                     mote="rgba(220,232,255,", spot="#bcd2ff"),
        "warm": dict(c0="#ffd9a0", c1="#e8895a", c2="#7a3b1e",
                     mote="rgba(255,240,210,", spot="#ffe6c2"),
        "dark": dict(c0="#24407a", c1="#0e1830", c2="#05080f",
                     mote="rgba(180,200,255,", spot="#9fb8ff"),
    }
    p = palettes.get(variant, palettes["blue"])
    # 确定性漂浮光点（避免每次构建输出不同）
    seeds = [(120, 640, 40, -220, 9), (300, 700, 70, -260, 11),
             (520, 660, 30, -240, 8), (760, 710, 90, -280, 13),
             (980, 650, 50, -230, 10), (1140, 700, 60, -250, 12),
             (200, 560, -40, -210, 7), (640, 600, 20, -200, 9),
             (880, 580, -30, -220, 8), (420, 720, 55, -260, 12),
             (1060, 600, 45, -240, 10), (60, 600, 35, -200, 7),
             (700, 660, -50, -250, 11), (1180, 560, 25, -210, 9),
             (360, 620, 15, -230, 8)]
    motes = ""
    for i, (x, y, dx, dy, dur) in enumerate(seeds):
        r = 1.2 + (i % 3) * 0.6
        motes += (
            f"<circle cx='{x}' cy='{y}' r='{r:.1f}' fill='{p['mote']}0.55)'>"
            f"<animateTransform attributeName='transform' type='translate' "
            f"values='0 0;{dx} {dy}' dur='{dur}s' repeatCount='indefinite'/>"
            f"<animate attributeName='opacity' values='0;0.6;0' "
            f"dur='{dur}s' repeatCount='indefinite'/></circle>")
    spots = ""
    for j, (sx, sy, sr, so) in enumerate([(260, 200, 90, 0.16),
                                         (1010, 160, 70, 0.13),
                                         (640, 520, 120, 0.10)]):
        spots += (
            f"<circle cx='{sx}' cy='{sy}' r='{sr}' fill='{p['spot']}' "
            f"opacity='{so}'>"
            f"<animate attributeName='opacity' values='{so};{so*2.2:.2f};{so}' "
            f"dur='{7+j*2}s' repeatCount='indefinite'/>"
            f"<animateTransform attributeName='transform' type='translate' "
            f"values='0 0;12 -10;0 0' dur='{11+j*3}s' repeatCount='indefinite'/>"
            f"</circle>")
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1280 720' "
        f"preserveAspectRatio='xMidYMid slice'><defs>"
        f"<radialGradient id='g' cx='50%' cy='36%' r='80%'>"
        f"<stop offset='0%' stop-color='{p['c0']}'/>"
        f"<stop offset='58%' stop-color='{p['c1']}'/>"
        f"<stop offset='100%' stop-color='{p['c2']}'/></radialGradient>"
        f"<radialGradient id='vig' cx='50%' cy='50%' r='72%'>"
        f"<stop offset='55%' stop-color='#000' stop-opacity='0'/>"
        f"<stop offset='100%' stop-color='#000' stop-opacity='0.42'/>"
        f"</radialGradient>"
        f"<linearGradient id='scan' x1='0' y1='0' x2='1' y2='0'>"
        f"<stop offset='0%' stop-color='{p['spot']}' stop-opacity='0'/>"
        f"<stop offset='50%' stop-color='{p['spot']}' stop-opacity='0.5'/>"
        f"<stop offset='100%' stop-color='{p['spot']}' stop-opacity='0'/>"
        f"</linearGradient></defs>"
        f"<rect width='1280' height='720' fill='url(#g)'/>{spots}{motes}"
        f"<rect x='-300' y='-120' width='360' height='960' fill='url(#scan)' "
        f"transform='skewX(-18)'>"
        f"<animateTransform attributeName='transform' type='translate' "
        f"values='-200 0;1700 0' dur='9s' repeatCount='indefinite' additive='sum'/>"
        f"</rect>"
        f"<rect width='1280' height='720' fill='url(#vig)'/></svg>")
    return "data:image/svg+xml," + quote(svg, safe="")


def ambient_bg(variant="blue"):
    """返回电影感动态背景的 data-URI（SMIL 动画 SVG）。"""
    return _svg_ambient(variant)


# ---------- 幻灯片骨架 ----------
def slide(id, bg, transition, notes, elements, ambient=None):
    els = list(elements)
    if ambient:
        els.insert(0, {
            "id": "amb-bg", "type": "image", "x": 0, "y": 0,
            "w": PAGE_W, "h": PAGE_H, "src": ambient_bg(ambient),
            "fit": "cover", "radius": 0, "rotation": 0, "opacity": 1,
            "fx": {"ambient": "kenburns", "ken": {"dir": "drift",
                                                  "scale": 1.06, "duration": 24}},
        })
        if ambient == "warm":
            els.insert(1, {"id": "amb-scrim", "type": "shape", "shape": "rect",
                           "x": 0, "y": 0, "w": PAGE_W, "h": PAGE_H,
                           "fill": "rgba(18,10,2,0.32)", "stroke": "none",
                           "radius": 0})
    return {"id": id, "background": bg, "transition": transition,
            "notes": notes, "elements": els}


def make_doc(title, slides, accent=IKB, author="AI 落地实践",
             event="高校 AI 素养培训", modified="2026-07-27T00:00:00.000Z"):
    return {
        "format": "bento/slides", "version": 1, "title": title,
        "size": {"width": PAGE_W, "height": PAGE_H},
        "theme": {"background": CREAM, "color": INK, "accent": accent,
                  "fontFamily": FONT},
        "meta": {"author": author, "event": event},
        "present": {"slideNumber": False},
        "slides": slides, "modified": modified,
    }


# ---------- splice（写文件 + 客观校验）----------
BLOCK_RE = re.compile(
    r'(<script type="application/bento\+json" id="bento-doc">)(.*?)(</script>)',
    re.S)


def ensure_shell():
    if SHELL_PATH.exists():
        return
    SHELL_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"下载官方壳 → {SHELL_PATH}")
    urllib.request.urlretrieve(SHELL_URL, SHELL_PATH)
    assert 'id="bento-doc"' in SHELL_PATH.read_text(encoding="utf-8"), "壳校验失败"


def splice(doc, out_path):
    """把 doc 写进壳的 #bento-doc 块，输出完整 .bento.html。回读校验。"""
    ensure_shell()
    shell = SHELL_PATH.read_text(encoding="utf-8")
    payload = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c")  # 铁律：物理杜绝 </script> 提前闭合
    new, n = BLOCK_RE.subn(lambda m: m.group(1) + payload + m.group(3),
                           shell, count=1)
    assert n == 1, "bento-doc 块替换失败（壳结构变了？）"
    new = re.sub(r"<title>.*?</title>",
                 f"<title>{doc['title']} — bento/slides</title>", new, count=1)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(new, encoding="utf-8")
    # 回读校验（客观事实，不猜）
    written = out_path.read_text(encoding="utf-8")
    assert written.count('id="bento-doc"') == 1
    block = BLOCK_RE.search(written).group(2)
    parsed = json.loads(block)
    assert len(parsed["slides"]) == len(doc["slides"]), "幻灯片数不一致"
    ids = [s["id"] for s in parsed["slides"]]
    assert len(set(ids)) == len(ids), f"幻灯片 id 重复: {ids}"
    print(f"OK {out_path}  {len(written)/1024:.0f} KB  slides={len(parsed['slides'])}")
    return out_path


def emit(doc, out_stem):
    """一键双版本：<stem>.bento.html（可编辑）+ <stem>.play.bento.html（放映）。"""
    edit = splice(doc, f"{out_stem}.bento.html")
    play = splice(dict(doc, readonly=True), f"{out_stem}.play.bento.html")
    return edit, play
