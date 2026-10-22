# BrewFS — OSDI 论文研究准备包

版本：2026-10-23。工作标题：

**BrewFS: Delta-Based Multi-Agent Workspaces with Packed Metadata and Variable-Granularity Object Storage**

本包提供英文内部初稿、中文研究大纲、完整实验协议、文献核验记录、实现证据及可移植写作 skill。**实验全部处于规划阶段；没有本轮新测得的性能、正确性或故障恢复结果。** 提议的机器、样本规模和参数也不是已部署环境。

## 建议阅读顺序

1. `paper/main.pdf`：可直接阅读的英文初稿。正文依次为问题与动机、系统契约、Delta、Packed、对象布局、实现状态、评估计划和相关工作。
2. `planning/01-research-outline.zh.md`：研究论点、贡献边界、章节及图表规划、评审风险与推进顺序。
3. `planning/02-experiment-plan.zh.md`：7 个 RQ、E00–E16 共 17 项实验、环境、基线、因果对照、指标、统计和失败处理。
4. `evidence/implementation_inventory.csv`、`evidence/source_evidence.md` 和 `evidence/current-head-audit.md`：固定提交与当前上游 HEAD 的实现事实和边界；区分设计、代码存在、运行时接通与实测。
5. `references/literature_matrix.md`：逐项核验真实相关工作及与本研究的重叠，不把概念相似误写成首创。

## 文件地图

| 目录 | 内容与用途 |
|---|---|
| `paper/` | LaTeX 源码、两份 PDF、BibTeX、Makefile、TikZ 架构图与访问路径图。 |
| `paper/template/` | 原样保留的官方 USENIX 示例及样式；论文自身使用独立标题和真实参考文献。 |
| `planning/` | 中文大纲、实验协议、OSDI 风格研究、英文学术写作 skill 调查和模板来源。 |
| `experiments/` | 17 项实验矩阵、agent 负载协议、13 项待完成实现门槛、未执行 manifest 示例、未来观测记录 schema、只有表头的度量模板。 |
| `references/` | 29 条书目的来源登记与比较矩阵。23 篇研究论文（含工作坊），6 项官方资料。 |
| `evidence/` | 固定版本代码审计、实现清单、远端来源记录、skill 热度和验证/安装状态记录。 |
| `skills/osdi-systems-paper/` | 独立撰写的可移植 OSDI 系统论文写作 skill；带英文改写、证据及实验、BrewFS 专用约束和来源说明。 |
| `validation/` | 分工审阅记录、处理结果、最终格式与文件验证记录。早期审阅意见反映审阅当时状态，以 `review-resolution.md` 为准。 |
| `tools/validate_plan.py` | 只核验本准备包的一致性，不运行 BrewFS 或产生实验数据。 |
| `MANIFEST.sha256` | 打包时对包内文件计算的 SHA-256 清单。 |

`paper/anonymous-preview.pdf` 只是系统名切换和固定源码标识隐藏后的排版预览，**不是已经完成匿名审查的投稿版**。

## 当前最重要的研究判断

三项机制应围绕一个问题组织：共享不可变工作区基线、私有变化与局部对象访问如何共同降低维护和服务成本。需要证明这一组合在同一实际路径中成立，同时解释条件与代价。

- OverlayFS、DeltaFS、BranchFS 和不可变按需加载系统已经覆盖大量相邻思想。“agent + COW”或“元数据放在对象存储”不足以构成新颖性。
- Packed 的数据库绕行主张限定于共享只读 lower 的查询路径；私有 upper 和控制状态仍可访问元数据库。应与等记录内容、等缓存预算的 immutable sorted-KV，以及至少一种成熟 lazy lower 比较。
- 对象布局参数写作 `(B,q)`：`B` 是持久化的纠删编码块，`q` 是受编码几何约束的校验/读取量子。二者不能混同于应用请求、文件长度、压缩帧或 S3 Range。固定 data/parity 数时，名义冗余比不因改变 B 自动降低。
- 自动布局策略目前不等于自适应优化器。应先证明处理组对象实际具有不同的持久化布局，再讨论物理 I/O 和端到端收益。

## 正式实验前的优先门槛

当前克隆的上游 HEAD 是 BrewFS `f80e7148c82e9f1ef235ab19318b89cb41a093a2`；为了保持行级证据稳定，现有 source inventory 仍固定 research checkpoint `518e7cc39b2ff0b421ecf0f656de6d468cacb9b8`，RustFS research fork 为 `cc4926fac1107aee76540f28bf22dbd47fcbca24`。二者的差异记录在 `evidence/current-head-audit.md`，正式实验必须重新生成 manifest。

1. 核验所选挂载入口，分别接通 Entity S3 配置、Packed producer 和 strict durable create-only PUT 的 hint；保留 conditional-create/412 语义。
2. 记录实际最终对象大小。Entity 挂载的 MAX_WRITE 为 1 MiB，当前直接上传形成的 upper 对象不能触发 auto 的“大于 1 MiB”分支。不能用大逻辑文件冒充大上传对象；聚合是尚未实现的新设计。
3. 为 q 的不同写入处理创建内容一致、标识隔离的新对象集，验证实际 `(B,q)`、eligibility 与 framing。改变开关不会重写已有对象。当前 auto 与默认 B 还可能完全相同。
4. 分离 Range/完整对象读取、缓存、SingleFlight、write-budget release 和 shared-bytes reply。Entity upper 的完整对象校验也必须计入实际读取代价。
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

需要 Python 3，以及含 Windows `xelatex`、`latexmk`、BibTeX、USENIX 所需常用包、TikZ、`xurl` 的 TeX 环境。样式已附，无须在线下载模板。源码使用数值引用的 `plain` 样式；XeLaTeX 使用 `paper/usenix2019_v3_xetex.sty` 兼容副本，官方样式文件保持原样。

```bash
cd paper
latexmk -xelatex main.tex
latexmk -xelatex anonymous-preview.tex
cd ..
python3 tools/validate_plan.py
```

`make` 构建命名稿和匿名预览。`make clean` 清理 LaTeX 中间文件。验证脚本检查条目/引用、实验/RQ 覆盖、未执行状态、样式哈希和可用的编译日志；它不检查系统性能或证明语义正确。最终 PDF 页数、字体及视觉检查以 `validation/quality-report.md` 为准。

## 写作 skill 与投稿边界

调查采用可复查的 GitHub 仓库星标及内容适用性；仓库星标不是某个 skill 的安装数，也不能证明“全网最流行”。新 skill 综合了 OSDI 官方规则、实际论文结构、科学写作与系统论文写作参考，未直接搬运上游整套技能。

可移植 skill 已通过结构和相对链接检查。平台自动审批拒绝了向受保护 Skills 目录写入，因此 skill 本身**没有完成在线安装**；本包交付的是源码，不声称已经安装。研究准备包已提交并推送到私有仓库。

按 [OSDI 2027 CFP](https://www.usenix.org/conference/osdi27/call-for-papers) 与 [作者要求](https://www.usenix.org/conference/osdi27/requirements-authors)，正文最多 12 页、参考文献另计，双盲审稿，公开项目需处理识别信息。官方同时限制全部或大部分由 AI 生成的投稿。本稿仅供研究和作者讨论；正式投稿需要作者基于真实实现和实验主导实质性重写、审定与匿名处理。编译成功不等于证据齐备或投稿资格已经满足。
