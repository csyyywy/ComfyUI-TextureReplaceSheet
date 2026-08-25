"""
TextureReplaceSheetLoader
=========================
ComfyUI 自定义节点：读取 texture-replace-sheet.csv，
按"序号"取出一行，并把"尺寸(宽×高)"拆成 width / height 两个输出。

用法：
    1. 把本文件夹放入 ComfyUI/custom_nodes/ 并重启 ComfyUI；
    2. 在节点菜单 "texture/replace" 分类下找到
       "Texture Replace Sheet Loader (CSV)"；
    3. 输入 序号 (index)，即可得到该行的贴图名称、对应内容、
       宽、高、英文提示词。
"""

import csv
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = str(PLUGIN_DIR / "texture-replace-sheet.csv")

# 缓存：{(真实路径, mtime_ns, size): rows}，CSV 修改后自动失效
_cache = {}


def _normalize_path(p):
    """把用户填的路径规范化；空字符串 / 相对路径回退到插件自带 CSV。"""
    p = str(p or "").strip().strip('"').strip("'")
    if not p:
        return DEFAULT_CSV_PATH
    path = Path(p).expanduser()
    if path.is_absolute():
        return str(path)
    # 相对路径优先相对插件目录解析，其次相对当前工作目录
    candidate = PLUGIN_DIR / p
    if candidate.exists():
        return str(candidate)
    return str(path)


def _parse_size(text):
    """把 '20x20' / '20×20' / '20*20' / '20' 解析成 (width, height)。"""
    text = (text or "").strip().lower().replace("×", "x").replace("*", "x")
    if not text:
        return 0, 0
    parts = [p.strip() for p in text.split("x") if p.strip()]
    try:
        if len(parts) == 1:
            v = int(parts[0])
            return v, v
        if len(parts) >= 2:
            return int(parts[0]), int(parts[1])
    except ValueError:
        pass
    return 0, 0


def _load_rows(csv_path):
    """读取 CSV 并返回按序号排序的行字典列表。带文件修改时间缓存。"""
    path = Path(csv_path)
    try:
        stat = path.stat()
    except OSError:
        raise ValueError(f"找不到 CSV 文件: {csv_path}")

    key = (str(path.resolve()), stat.st_mtime_ns, stat.st_size)
    if key in _cache:
        return _cache[key]

    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError(f"CSV 文件为空: {csv_path}")

        for raw in reader:
            if not raw or not any(cell.strip() for cell in raw):
                continue
            raw = (raw + [""] * 5)[:5]
            try:
                idx = int(str(raw[0]).strip())
            except ValueError:
                # 没有数字序号的行跳过（例如注释行）
                continue
            width, height = _parse_size(raw[3])
            rows.append({
                "index": idx,
                "texture_name": raw[1].strip(),
                "content": raw[2].strip(),
                "width": width,
                "height": height,
                "prompt": raw[4].strip(),
            })

    rows.sort(key=lambda r: r["index"])
    _cache[key] = rows
    return rows


class TextureReplaceSheetLoader:
    """按序号读取 texture-replace-sheet.csv 的一行，分辨率拆成宽/高。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "csv_path": (
                    "STRING",
                    {
                        "default": DEFAULT_CSV_PATH,
                        "multiline": False,
                        "tooltip": "CSV 文件路径；留空或填相对路径时使用插件自带的 texture-replace-sheet.csv",
                    },
                ),
                "index": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 999999,
                        "step": 1,
                        "tooltip": "序号：CSV 第一列的数字，例如 1、16、49",
                    },
                ),
                "on_missing": (
                    ["error", "empty"],
                    {
                        "default": "error",
                        "tooltip": "序号不存在时：error=抛出错误提示；empty=返回空值",
                    },
                ),
            },
        }

    RETURN_TYPES = ("INT", "STRING", "STRING", "INT", "INT", "STRING", "INT")
    RETURN_NAMES = (
        "index",
        "texture_name",
        "content",
        "width",
        "height",
        "prompt",
        "row_count",
    )
    FUNCTION = "load"
    CATEGORY = "texture/replace"

    def load(self, csv_path, index, on_missing="error"):
        rows = _load_rows(_normalize_path(csv_path))

        found = next((r for r in rows if r["index"] == index), None)
        if found is None:
            if on_missing == "empty":
                return (index, "", "", 0, 0, "", len(rows))
            if rows:
                lo, hi = rows[0]["index"], rows[-1]["index"]
                raise ValueError(
                    f"序号 {index} 在 CSV 中不存在：{csv_path} "
                    f"（有效范围 {lo}..{hi}，共 {len(rows)} 行）"
                )
            raise ValueError(f"CSV 中没有数据行: {csv_path}")

        return (
            found["index"],
            found["texture_name"],
            found["content"],
            found["width"],
            found["height"],
            found["prompt"],
            len(rows),
        )

    @classmethod
    def IS_CHANGED(cls, csv_path, index, on_missing="error"):
        """CSV 文件被修改时让 ComfyUI 重新执行本节点。"""
        try:
            return Path(_normalize_path(csv_path)).stat().st_mtime_ns
        except OSError:
            return 0


NODE_CLASS_MAPPINGS = {
    "TextureReplaceSheetLoader": TextureReplaceSheetLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextureReplaceSheetLoader": "Texture Replace Sheet Loader (CSV)",
}
