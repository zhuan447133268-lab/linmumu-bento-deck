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


# ---------- 幻灯片骨架 ----------
def slide(id, bg, transition, notes, elements):
    return {"id": id, "background": bg, "transition": transition,
            "notes": notes, "elements": elements}


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
