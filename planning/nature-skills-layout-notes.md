# Nature skills：安装与布局使用记录

日期：2026-10-23。来源：https://github.com/Yuan1z0825/nature-skills 。安装后读取的 main revision：`c6ae86c742705fd968b13c79db1a8518a84089d4`（安装器使用 main 下载，revision 是随后查询值）。

通过官方 skill-installer helper 安装仓库 `skills/*/SKILL.md` 对应的 23 个技能到 `C:/Users/HXY/.codex/skills/`。安装的是技能文件，未执行仓库自带的 install.sh、自动更新脚本或配置外部 MCP/API 服务；这些可选依赖不属于本次完成范围。

本次使用 nature-writing 与其 nature-shared 依赖做论文布局，使用 PDF 技能验证导出。路由：manuscript / research / method + experiments / zh-to-en / generic，沿用 OSDI 目标。依据现有研究论点与实验矩阵组织，不生成实测结果。

交付：`paper-layout.tex` 与 4 页 `paper-layout.pdf`。内容包括 11.25 页正文预算与 0.75 页浮动余量、4 页评估预算、6 个主张的证据映射、6 个图号及 3 张表的用途、对照原则、分阶段实验与改稿顺序。正文先维持原结构，规划不等于已执行重构。

构建：在 planning 目录运行 `latexmk -xelatex -interaction=nonstopmode -halt-on-error paper-layout.tex`。已用 Windows XeLaTeX 编译并逐页查看 4 页渲染，无溢出或缺字；原主稿和匿名预览也重新编译，均为 13 页。

后续交付习惯：每次修改完成后重新编译论文并在 Codex 中打开 PDF，同时提供文件链接。
