# -*- coding: utf-8 -*-
"""Plugin self-test: run with any Python 3.x:  python selftest.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nodes

rows = nodes._load_rows(nodes.DEFAULT_CSV_PATH)
print("total rows:", len(rows))
assert len(rows) == 226, len(rows)

# 序号必须连续 1..226
expected = list(range(1, len(rows) + 1))
assert [r["index"] for r in rows] == expected, "index sequence mismatch"

node = nodes.TextureReplaceSheetLoader()
for idx in (1, 2, 49, 138, 226):
    out = node.load(nodes.DEFAULT_CSV_PATH, idx, "error")
    assert out[0] == idx
    assert out[1] and out[2] and out[5], (idx, out)
    assert out[3] > 0 and out[4] > 0, (idx, out[3], out[4])
    print(idx, "->", out[1], "|", out[2], "| W:", out[3], "H:", out[4], "| row_count:", out[6])

# 每一行的尺寸都要能解析出正数
bad = [r["index"] for r in rows if r["width"] <= 0 or r["height"] <= 0]
assert not bad, bad
print("all sizes parse OK")

# 越界序号：error / empty 两种模式
try:
    node.load(nodes.DEFAULT_CSV_PATH, 99999, "error")
    raise SystemExit("missing index did not raise (unexpected)")
except ValueError as e:
    print("missing ->", e)

out = node.load(nodes.DEFAULT_CSV_PATH, 99999, "empty")
assert out[1:] == ("", "", 0, 0, "", 226)
print("ALL TESTS PASSED")
