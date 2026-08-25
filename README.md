# ComfyUI-TextureReplaceSheet

一个 ComfyUI 自定义节点：读取 `texture-replace-sheet.csv`（贴图替换清单），
根据**序号**取出一行，并分别输出该行的各项内容，其中
**分辨率一列会被拆成 width（宽）和 height（高）两个独立输出**。

## 安装

1. 把整个 `ComfyUI-TextureReplaceSheet` 文件夹复制到你的 ComfyUI 目录下：
   ```
   ComfyUI/custom_nodes/ComfyUI-TextureReplaceSheet/
   ```
2. 重启 ComfyUI。
3. 在节点搜索框输入 `Texture Replace Sheet`，或到分类
   `texture/replace` 下找到 **Texture Replace Sheet Loader (CSV)**。

## 节点用法

| 输入 | 类型 | 说明 |
| --- | --- | --- |
| `csv_path` | STRING | CSV 路径。**留空/不填时默认使用插件自带的 `texture-replace-sheet.csv`**（即本文件夹里那份） |
| `index` | INT | 序号（CSV 第一列的数字，如 1、16、49、226） |
| `on_missing` | COMBO | 序号不存在时：`error` 报错提示有效范围；`empty` 返回空值 |

| 输出 | 类型 | 说明 |
| --- | --- | --- |
| `index` | INT | 命中的序号 |
| `texture_name` | STRING | 贴图名称（如 `Items/Materials/VoidOre.png`） |
| `content` | STRING | 对应内容/装备（如 `虚空矿石｜物品图标`） |
| `width` | INT | 分辨率**宽**（如 20x20 → 20） |
| `height` | INT | 分辨率**高**（如 20x20 → 20；40x1400 → 1400） |
| `prompt` | STRING | 英文生成提示词 |
| `row_count` | INT | CSV 数据总行数（便于校验/遍历） |

## 特性

- 内置 CSV：插件目录里已附带 `texture-replace-sheet.csv`（与本次需求同一份），开箱即用；
  你也可以把 `csv_path` 指向任意其他路径（含相对路径，会优先相对插件目录解析）。
- 修改 CSV 后无需重启：节点缓存按文件修改时间自动失效（`IS_CHANGED` 也会让 ComfyUI 重新执行）。
- 解析容错：尺寸支持 `20x20`、`20×20`、`20*20`、单独的 `20`（按正方形处理）；
  UTF-8 BOM、空行、非数字序号行都能正确处理。

## 示例

`examples/example_workflow.json` 是一个最小可用工作流（API 格式）。
用浏览器打开 ComfyUI → 菜单 Workflow → Open，或直接拖入画布即可加载。
节点 `index` 填 1 时输出第一行：
`VoidOre.png` / `虚空矿石｜物品图标` / 宽 20 / 高 20 / 对应英文提示词。
