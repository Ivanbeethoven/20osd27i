# BrewFS — OSDI 论文研究准备包

版本：2026-10-24。工作标题：

**BrewFS: Delta-Based Multi-Agent Workspaces with Packed Metadata and Variable-Granularity Object Storage**

本包提供英文内部初稿、中文研究大纲、完整实验协议、文献核验记录、实现证据及可移植写作 skill。现已纳入 **8 个真实 Agent 任务、1,138,884 条 FUSE 请求的原始数据重分析**，位于论文 §2.3；Core 与 Exploratory 分开呈现。**E00–E16 系统实验仍处于规划阶段；没有据此宣称 BrewFS/RustFS 的性能、正确性或故障恢复收益。** 提议的机器、样本规模和参数也不是已部署环境。

本轮观测的统计口径、证据对应关系及复现命令见 [工作负载分析说明](experiments/agent-fuse-observations/README.md)。当前论文使用一张单栏三面板主图，由 `analyze.py` 流式统计、`plot_single_column.py` 绘制；`plot.py` 生成配套的方法、请求大小和时序诊断图。保留实际模型名 `deepseek-v4-flash`，并区分 FUSE 错误、进程退出码与基准任务评分。

论文与中文研究文档统一沿用[已确认术语表](planning/terminology.zh.md)：三项机制为基于增量状态的多智能体工作区、打包式元数据和可变粒度对象存储。**三者均为可选、可组合能力，不是必须依次开启的流程。** 普通卷提供公共文件与对象路径；增量工作区选择视图构成，打包式元数据选择不可变记录的组织与获取方式，对象粒度选择数据对象的形成及可选后端布局。

## 建议阅读顺序

1. [main.pdf](main.pdf)：可直接阅读的英文初稿；正式源码入口是仓库根目录的 [main.tex](main.tex)。正文依次为问题与动机、系统契约、增量工作区、打包式元数据、对象布局、实现状态、评估计划和相关工作。
2. `planning/01-research-outline.zh.md`：研究论点、贡献边界、章节及图表规划、评审风险与推进顺序。
3. `planning/02-experiment-plan.zh.md`：7 个 RQ、E00–E16 共 17 项实验、环境、基线、因果对照、指标、统计和失败处理。
4. [三项机制关系框架](planning/03-mechanism-relationships.zh.md)：依据作者 PPT 与当前代码说明各机制启用、省略和组合时的行为。
5. 当前原理审计：[工作区](evidence/principles-code/workspaces.md)、[打包式元数据](evidence/principles-code/packed.md)、[对象粒度](evidence/principles-code/objects.md)，对应 BrewFS `242af5f`；[PPT 正文与讲稿](evidence/ppt-principles/slides.json)保留设计意图来源。`evidence/implementation_inventory.csv`、`evidence/source_evidence.md` 和 `evidence/current-head-audit.md` 保留历史检查点的证据，不替代当前审计。
6. `references/literature_matrix.md`：逐项核验真实相关工作及与本研究的重叠，不把概念相似误写成首创。

## 文件地图

| 目录 | 内容与用途 |
|---|---|
| 仓库根目录 | 唯一论文入口 `main.tex`、阅读版 `main.pdf`、`references.bib`、USENIX 样式及构建配置。 |
| `sections/`、`figures/` | 正式论文章节、架构图、访问路径图及工作负载图。 |
| `templates/usenix-official/` | 原样保留的官方 USENIX 示例及样式；论文自身使用独立标题和真实参考文献。 |
| `planning/` | 中文大纲、实验协议、三项可选机制关系框架、统一术语表、OSDI 风格研究和模板来源。 |
| `experiments/` | 17 项实验矩阵、agent 负载协议、13 项待完成实现门槛、未执行 manifest 示例、未来观测记录 schema、只有表头的度量模板。 |
| `references/` | 29 条书目的来源登记与比较矩阵。23 篇研究论文（含工作坊），6 项官方资料。 |
| `evidence/` | 当前 `principles-code/` 三项原理审计与 `ppt-principles/` 正文/讲稿，历史代码审计、实现清单、远端来源和验证记录。 |
| `skills/osdi-systems-paper/` | 独立撰写的可移植 OSDI 系统论文写作 skill；带英文改写、证据及实验、BrewFS 专用约束和来源说明。 |
| `validation/` | 审阅结论、语义核查和结构化验证记录，入口见 [检查记录说明](validation/README.md)。历史记录对应检查当时版本。 |
| `tools/validate_plan.py` | 只核验本准备包的一致性，不运行 BrewFS 或产生实验数据。 |

当前架构图只保留 `figures/system-architecture-editable.{svg,pdf,png}` 及生成脚本。
淘汰的架构图、绘图草稿、旧主图、通用起始模板和渲染缓存已清理；历史版本可从 Git 提交
`5994769` 恢复。旧打包校验清单已失效并删除，当前一致性以验证脚本和 Git 提交为准。

仓库仅维护命名研究稿，章节位于 `sections/`，统一从根目录构建。名称切换预览及旧的
`paper/` 构建转发目录已移除；正式投稿仍需作者完成独立的匿名审查。

## 当前最重要的研究判断

三项机制分别解决工作区视图维护、不可变元数据访问、对象请求与字节搬运成本。增量工作区可使用原生下层，Packed 可独立只读使用，普通 flat 卷可独立配置对象路径。组合研究需要核验所选入口、接口和代价；架构上可选不意味着当前所有入口都已支持全部组合，也不预设组合收益相乘。

- OverlayFS、DeltaFS、BranchFS 和不可变按需加载系统已经覆盖大量相邻思想。“agent + COW”或“元数据放在对象存储”不足以构成新颖性。
- 打包式元数据的下层查询独立性主张限定于共享只读下层的查询路径；私有上层和控制状态仍可访问元数据库。应与等记录内容、等缓存预算的 immutable sorted-KV，以及至少一种成熟 lazy lower 比较。
- 对象粒度分层写作 `g → L_o → 请求范围 → (B,q)`：`g` 是客户端 Block 大小，控制普通路径的对象形成；`L_o` 是含适用压缩和成帧的最终上传对象长度；`B` 是持久化的纠删码编码块大小，`q` 是受编码几何约束的物理校验／读取粒度。它们不等同于文件长度、应用请求、Packed 数据帧或 S3 Range。固定 data/parity 数时，名义冗余比不因改变 B 自动降低。
- 普通路径当前默认 `g=4 MiB`、Chunk 为 64 MiB，并提供固定配置；PPT 的 1/4/8/16 MiB 是客户端粒度研究档位，不是已实现的在线动态选档。自动提示策略只按 `L_o` 请求 B，可能与后端默认 B 相同。先证明实际对象形成、请求流及持久化布局的差异，再讨论收益。

## 正式实验前的优先门槛

当前原理审计固定 BrewFS `242af5f7e9bba7afc0c61778f1084fcb20e083a0`，源码只读快照为相邻目录 `../brewfs-principles-242af5f`。旧 `source_evidence.md` / `implementation_inventory.csv` 固定研究检查点 `518e7cc39b2ff0b421ecf0f656de6d468cacb9b8`；`current-head-audit.md` 记录先前上游 `f80e7148c82e9f1ef235ab19318b89cb41a093a2` 的审计，文件名不表示它仍是当前 HEAD。RustFS 后端扩展依据独立研究 fork `cc4926fac1107aee76540f28bf22dbd47fcbca24`，不推定当前上游或任意 S3 服务支持同一扩展。正式实验必须重新生成 manifest。

1. 核验每项实验选用的挂载入口与开启的机制。普通 flat、默认后端布局和独立 Packed 读取均是有效研究配置；只有在测试相应组合时，才要求补通 Entity S3 配置、快照构建器及 strict durable create-only PUT 的布局提示，并保留 conditional-create/412 语义。
2. 记录实际最终上传对象长度。Entity 挂载的 MAX_WRITE 为 1 MiB，当前直接上传形成的上层对象不能触发自动提示策略的“大于 1 MiB”分支。不能用大逻辑文件冒充大上传对象；聚合是尚未实现的新设计。
3. 为 q 的不同写入处理创建内容一致、标识隔离的新对象集，验证实际 `(B,q)`、eligibility 与 framing。改变开关不会重写已有对象。当前自动提示策略与默认 B 还可能完全相同。
4. 将固定客户端 `g`、范围读取／整对象获取、缓存、SingleFlight、后端 B/q、write-budget release 和 shared-bytes reply 分开控制。`g` 对比创建独立数据集，不能直接更改已有数据的解释几何；Entity 上层的完整对象校验也必须计入实际读取代价。
5. 在同一路径中完成合法消融适配器，再运行 E11。不要把 ordinary VFS 与 Entity 的差异视为单一机制开关。
6. 对 fresh-only Entity 的生命周期、恢复和回收实验遵守实现门槛；完整目录接口 4,096 entries、owner census 256/store 等当前限制必须进入 workload 筛查。

细节、成功判据及可削弱主张的结果见 `experiments/implementation-backlog.csv` 和实验协议。

## 实验资源与最低闭环规模

T0 是一台 Linux 主机加四个独立测试 drive 的功能/物理机制台架。T1 建议申请 **2 台客户端 + 1 台元数据服务器 + 4 台存储服务器**，25 GbE，先验证 2+2 EC；硬件型号和软件版本在获得资源后固定。四服务器拓扑不能直接继承仅适用于全部在线 shard 本地的 batch-pread 优化。

核心闭环计划为 **20 个分层任务 × 3 个系统条件 × 3 次重复 = 180 runs**；扩展为 60 个任务时是 540 runs。主要三条件是同后端对象文件系统、至少一种成熟 lazy lower 加 writable upper、以及完整系统。大范围并发扫描优先用冻结回放。样本量、时限和正式任务清单在 pilot 后、查看处理效果前冻结；失败和超时进入主要完成率/吞吐统计。

## 真实文献与阅读深度

所有 BibTeX 条目都有可核对的主来源。会议、年份、DOI、正式发表与预印本/工作坊身份分别记录；具体阅读范围在 `source_registry.csv` 中。MesaFS 已核验书目信息，但本轮全文访问受阻，因此不依据它的摘要宣称具体技术差异。矩阵也列出须继续补读的 HMFS。**书目存在与全文深入比较是两种证据，不能互相替代。**

SWE-bench Pro 和 JuiceFS 分别引用官方数据集及架构文档，没有虚构论文。Pro V2 revision 是执行前筛查的候选，未暗示已经下载或运行。

## 构建与复核

需要 Python 3，以及含 `xelatex`、`latexmk`、BibTeX、USENIX 所需常用包、TikZ、`xurl` 的 TeX 环境。样式已附，无须在线下载模板。源码使用数值引用的 `plain` 样式；XeLaTeX 使用根目录的 `usenix2019_v3_xetex.sty` 兼容副本，官方样式文件保持原样。在仓库根目录运行：

```bash
latexmk -xelatex main.tex
python3 tools/validate_plan.py
```

根目录的 `make` 或 `make paper` 构建正式稿，PDF 输出到根目录；`make clean` 清理 LaTeX 中间文件。验证脚本检查条目/引用、实验/RQ 覆盖、未执行状态、样式哈希和可用的编译日志；它不检查系统性能或证明语义正确。历史 PDF 页数、字体及视觉检查保留在 `validation/`，其结论对应各自检查时的版本。

## 写作 skill 与投稿边界

调查采用可复查的 GitHub 仓库星标及内容适用性；仓库星标不是某个 skill 的安装数，也不能证明“全网最流行”。新 skill 综合了 OSDI 官方规则、实际论文结构、科学写作与系统论文写作参考，未直接搬运上游整套技能。

可移植 skill 已通过结构和相对链接检查。平台自动审批拒绝了向受保护 Skills 目录写入，因此 skill 本身**没有完成在线安装**；本包交付的是源码，不声称已经安装。研究准备包已提交并推送到私有仓库。

按 [OSDI 2027 CFP](https://www.usenix.org/conference/osdi27/call-for-papers) 与 [作者要求](https://www.usenix.org/conference/osdi27/requirements-authors)，正文最多 12 页、参考文献另计，双盲审稿，公开项目需处理识别信息。官方同时限制全部或大部分由 AI 生成的投稿。本稿仅供研究和作者讨论；正式投稿需要作者基于真实实现和实验主导实质性重写、审定与匿名处理。编译成功不等于证据齐备或投稿资格已经满足。
