# 编译检查与仓库同步

检查日期：2026-10-24。入口为根目录 `main.tex` 和 `anonymous-preview.tex`。

## 编译与静态检查

使用本机 TeX Live 2026，分别执行：

```text
latexmk -g -xelatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
latexmk -g -xelatex -interaction=nonstopmode -halt-on-error -file-line-error anonymous-preview.tex
python tools/validate_plan.py
git diff --cached --check -- . ':(exclude)*.svg' ':(exclude)validation/**/*.txt'
```

两次编译均退出 0，BibTeX 和 XeLaTeX 依赖规则收敛。两份 PDF 均为 13 页，
正文结束于第 11 页，参考文献从第 11 页开始，页面尺寸为 US Letter（612 × 792 pt）。

- 每份最终日志均为 0 Overfull、22 Underfull hbox、1 Underfull vbox。
- 没有未解析的交叉引用或文献引用、缺字、LaTeX/包警告或致命错误。
- 每份 PDF 的 14 个字体资源均已嵌入；未发现文字超出 PDF 页面边界。
- 项目验证通过：29 条书目、27 条被引条目、17 项计划实验、7 个研究问题，官方样式哈希一致。
- 从 Git 暂存区导出源码、样式、文献及图件，在没有预先生成的 PDF、BBL、AUX 的目录中
  重新构建两个入口，均成功。逐页比较抽取文本和渲染像素，与根目录交付 PDF 完全一致，
  见 `indexed-build-check.json`。

## 视觉核验

用 Poppler `pdftoppm -r 110 -png` 渲染两份 PDF 的全部页面，查看全部页面联系表，
并放大核对命名稿第 2 页观测图、第 4 页表格与架构图、第 6 页查询路径及成本公式。
未发现图文裁切、元素重叠、缺字或公式越界。Underfull 提示对应双栏正文的松排和浮动体周边间距；
本轮不为消除提示而压缩字号、修改页边距或改写论文正文。

## 本轮整理

- 更新根目录说明中当前观测图的生成脚本，并将观测章节编号同步为 §2.3。
- 为 `validation/` 下可重建的逐页 PNG、抽取文本和 PPT 渲染目录添加 Git 忽略规则；
  原文件保留在本地，审核报告、联系表、源图和正式图件仍可入库。
- 将此前尚未提交的论文、图件、规划文档及实验工具作为当前工作状态同步；
  本轮验证范围为论文构建与项目一致性，没有执行回放器测试或系统性能实验。

编译输出见 `main-build.txt`、`anonymous-build.txt`，结构和字体检查见 `pdf-inspection.json`，
项目检查见 `package-validation.json`。本轮页面渲染保存在被忽略的 `build/compile-check-2026-10-24/`。
Git 空白检查覆盖源码与文档；生成的 SVG 路径和原始构建日志含有生成器输出的行尾空格，
为保留原始产物及其已有哈希记录，未改写这些文件，并在空白检查中明确排除。
匿名文件仍是仓库定义的名称切换预览；本轮没有进行正式投稿的匿名性或文献事实审查。
