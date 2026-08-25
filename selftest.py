# -*- coding: utf-8 -*-
"""Plugin self-test: run with any Python 3.x:  python selftest.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nodes

rows = nodes._load_rows(nodes.DEFAULT_CSV_PATH)
print("total rows:", len(rows))
assert len(rows) == 226, len(rows)

node = nodes.TextureReplaceSheetLoader()
for idx in (1, 16, 40, 49, 138, 226):
    out = node.load(nodes.DEFAULT_CSV_PATH, idx, "error")
    print(idx, "->", out[1], "|", out[2], "| W:", out[3], "H:", out[4], "| row_count:", out[6])

for idx, ew, eh in ((16, 20, 16), (49, 40, 1400), (55, 144, 38), (155, 24, 40), (1, 20, 20)):
    out = node.load(nodes.DEFAULT_CSV_PATH, idx, "error")
    assert out[3] == ew and out[4] == eh, (idx, out[3], out[4])
print("size checks OK")

try:
    node.load(nodes.DEFAULT_CSV_PATH, 99999, "error")
    raise SystemExit("missing index did not raise (unexpected)")
except ValueError as e:
    print("missing ->", e)

out = node.load(nodes.DEFAULT_CSV_PATH, 99999, "empty")
print("empty mode ->", out)
assert out[1:] == ("", "", 0, 0, "", 226)
print("ALL TESTS PASSED")
