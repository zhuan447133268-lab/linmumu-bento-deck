# -*- coding: utf-8 -*-
"""verify_shots.py — 放映版截图抽验
用法：python verify_shots.py <放映版.bento.html路径> <总页数> [抽验页码逗号分隔] [输出目录]
示例：python verify_shots.py "D:\\...\\xxx.play.bento.html" 14 1,7,10 "D:\\...\\shots"
默认抽验：封面 + 中间页 + 末页
"""
import os, sys
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')


def main():
    play = Path(sys.argv[1]).resolve()
    pages = int(sys.argv[2])
    picks = ([int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3
             else sorted({1, max(1, pages // 2), pages}))
    out = Path(sys.argv[4] if len(sys.argv) > 4
               else play.parent / "shots")
    out.mkdir(parents=True, exist_ok=True)
    url = "file:///" + quote(str(play).replace("\\", "/"))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(url)
        pg.wait_for_timeout(4000)
        for i in range(1, pages + 1):
            if i in picks:
                pg.screenshot(path=str(out / f"verify-{i:02d}.png"))
                print(f"截 P{i}")
            if i < pages:
                pg.keyboard.press("ArrowRight")
                pg.wait_for_timeout(1400)
        b.close()
    print("抽验完成 ->", out)


if __name__ == "__main__":
    main()
