# BrewFS 论文

论文源码仓库。入口是根目录 [main.tex](main.tex)，阅读版为 [main.pdf](main.pdf)。章节位于 `sections/`，正文所需图表保留在 `figures/`，可独立编译。

实验方案、Rust负载回放、数据分析、部署和实验结果统一在 [AX实验仓库](https://github.com/Ivanbeethoven/ax-multi-agent-experiments)。该仓库通过 `paper/` Git submodule 引用本仓库；实验入口是其中的 `paper-design/README.md`。

## 编译

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
python tools/validate_plan.py
```

也可用 `make` 或 `make paper`。校验脚本只检查论文文件、引用、RQ、官方样式和已有编译日志，不依赖实验仓库。GitHub Actions继续从根目录编译。

## 内容

- `sections/`：论文正文，包括原理、已完成负载观察和待执行实验设计。
- `figures/`：论文使用的最终图表；原始观测、统计和绘图脚本在实验仓库。
- `planning/`：研究大纲、术语与写作准则；实验操作计划已迁到实验仓库。
- `evidence/`、`references/`：实现审计、文献与设计依据。
- `validation/`：编译和审阅记录，历史记录中的旧路径只代表当时布局。
- `skills/osdi-systems-paper/`：论文写作指导。

三项机制独立可选：Overlay维护共享父状态和私有修改；Packed Metadata组织固定版本的元数据；对象粒度控制对象形成及可选后端布局。实验不能把它们当作必须依次开启的步骤。

这是内部研究稿。已有八次Agent任务的文件请求观察不代表BrewFS的性能结论；设计、源码审计、实测观察和待执行实验分别标明。
