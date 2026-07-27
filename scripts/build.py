# -*- coding: utf-8 -*-
r"""build.py — bento 课件构建入口
用法：python build.py decks\personal_skill.py
deck 文件需提供：TITLE / OUT_STEM / SLIDES（可选 AUTHOR / EVENT / MODIFIED）
"""
import importlib.util, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bento_lib import make_doc, emit  # noqa: E402


def load_deck(path):
    spec = importlib.util.spec_from_file_location("deck", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for k in ("TITLE", "OUT_STEM", "SLIDES"):
        assert hasattr(m, k), f"deck 文件缺 {k}"
    return m


if __name__ == "__main__":
    assert len(sys.argv) == 2, "用法：python build.py decks\\xxx.py"
    d = load_deck(sys.argv[1])
    doc = make_doc(
        d.TITLE, d.SLIDES,
        author=getattr(d, "AUTHOR", "AI 落地实践"),
        event=getattr(d, "EVENT", "高校 AI 素养培训"),
        modified=getattr(d, "MODIFIED", "2026-07-27T00:00:00.000Z"),
    )
    edit, play = emit(doc, d.OUT_STEM)
    print(f"\n可编辑版：{edit}\n放映版：  {play}")
