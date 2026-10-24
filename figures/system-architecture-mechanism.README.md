# BrewFS 机制概览图

这版回应“更抽象、体现技术思路，但不能只剩简单概念框”的要求。三个可见机制分别是显式区间映射、联合元数据记录定位 frame、按对象持久保存的 B/q 布局。Agent 图标为原创矢量入口标记。

## 文件

- `system-architecture-mechanism.svg`：可编辑文本与图形，Arial / Arial Bold。
- `system-architecture-mechanism.pdf`：504 × 230 pt，7 英寸双栏宽，嵌入字体。
- `system-architecture-mechanism.png`：3× 预览。
- `system-architecture-mechanism.caption.tex`：配套技术图注。
- `../tools/draw_architecture_mechanism.py`：确定性生成脚本，图元使用稳定 id。
- `../validation/architecture-mechanism/figure-proof.pdf`：论文同款 USENIX 模板中的一页排版样张。

图面含 41 个标签、78 个空白分隔单词；文字 9.5–10.5 pt。子下标也不低于 9.5 pt。与 technical 版尺寸相同，去掉具体 KiB 数和多行分片阵列，补入 agent、Resolve、Range map 与共享对象身份连接。

## 生成来源

2026-10-23 先用内置 image_gen 生成抽象构图草稿，模型版本未由工具披露。完整提示词保存在 `../output/imagegen/architecture-abstract/prompt.txt`，原始参考图保存在同目录 `concept.png`。这份 AI 草稿只是构图参考。随后按论文与代码重画所有 SVG 图元、文字和线稿图标，并依据用户“太简单”的反馈补回最小机制结构。

原始工具文件：`C:/Users/HXY/.codex/generated_images/01a167df-efdf-7ce0-b642-5875424f60f9/exec-118cac51-80e3-4fd0-83db-b027255835c7.png`。

论文风格参考为用户提供的 Oxbow、Dingo、Umap、CoPilotIO 本地 PDF 及已提取系统图；最终文件没有嵌入这些论文的原图。

## 编辑与使用

修改 Python 中的标签/几何后运行该脚本，会同步导出 SVG、PDF、PNG 和 scene.json。支持运行环境为 Python + reportlab + svglib + pymupdf；字体路径按当前 Windows 工作区配置。普通标签由 live text 构成，带下标的标签由定位过的多段 live text 构成。

此版与图注组成一份作者审阅稿。主论文仍通过原 architecture.tex 引用原图；排版样张用于比较修改后的整体风格。审核记录见 `../validation/architecture-mechanism/review.md`。
