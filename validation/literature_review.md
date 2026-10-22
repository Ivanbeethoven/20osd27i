# 初稿审阅：相关工作、引用与基线公平性

日期：2026-10-22。审阅者：literature 子任务。审阅范围：

- `BrewFS-OSDI-Research-Package/paper/sections/01-introduction.tex`
- `BrewFS-OSDI-Research-Package/paper/sections/02-motivation.tex`
- `BrewFS-OSDI-Research-Package/planning/01-research-outline.zh.md`
- `BrewFS-OSDI-Research-Package/planning/02-experiment-plan.zh.md`

本次只提出 findings，没有直接修改上述四个文件。行号对应审阅快照；后续改动后应以章节和原句为定位锚点。代码实现事实、官方投稿日期和排版规则由相应独立审计负责，本报告不把它们重新认定为已验证的运行事实。

## 结论

英文引言与动机已较好地收紧创新边界：没有宣称首个 agent FS，没有把 delta 写成字节级差分格式，没有用模型论文证明存储瓶颈，明确限定 lower 查询，并把组合收益写为待检验假设。现有 14 个引用 key 都能在 `paper/references.bib` 中解析，未发现虚构或错配引用。

**优先修正两个实验合同缺口：BranchFS 的持久性完成点；CVMFS/Nydus 从“可选提及”升级为至少一个核心强基线。** 另有三项中等优先级的精化建议。SWE-bench Pro 的现有文字没有写错版本，但可以利用已核实的发布信息把选择落实到具体候选。

## P1-1：BranchFS 的 fsync no-op 尚未进入比较合同

**位置：** experiment plan §4.1 B4（第 79 行）、E03（第 172–176 行）、E04、E10；outline 近邻表 BranchFS 行（第 38 行）。

**发现：** 当前文字只说固定 revision、共同操作与不同 commit 语义另列。E03 又统一测 `edit+durability completion`。这不足以防止运行者在所有系统上执行一次 `fsync()`，把返回时间直接视为等价持久化完成。BranchFS 论文明确说明其 ephemeral branch 的 `fsync` 是 no-op，持久性在 commit 阶段处理；论文也把 `branch()` syscall 标为未实现提案。[S1]

**为什么重要：** 如果 BrewFS 在 fsync 时等待远端对象/元数据，而 BranchFS 只确认可见写，吞吐和首次修改延迟比较就混入了放宽持久性的收益。反过来，BranchFS 的本地 commit 也不能自动视为与四节点对象存储相同的远端耐久性。只在 caption 写“不同语义”不能修复同一主图中的无效配对。

**建议落实：**

1. 在 B4 行明确注明 `ephemeral fsync = no-op; durability deferred to commit`，并固定实际代码 revision 后复核。
2. 分开两个 panel：共同的 ephemeral/visibility-only 工作区操作；已核实故障保证的完整持久化操作。后者必须计入实际 commit、数据和目录持久化，以及若服务合同要求的远端发布成本；不能在 commit 发起时停止计时。
3. 若 BranchFS 无法满足指定的远端或独立分支持久化合同，只把它留在明确标注的本地/ephemeral panel；耐久性主比较使用可以满足合同的基线。不要为凑同图暗中修改某一系统的保证。
4. 在所有 durable panel 写清完成后允许哪类故障、应保留什么状态，并用故障检查验证完成点，而不是仅信任 API 名称。
5. BrewFS 是否具备 commit-to-parent、兄弟分支失效或进程回滚，仍按实现边界单列；不要为了比较 BranchFS 自动补上这些承诺。

这里建议的是公平的测量合同，不是断言 BranchFS 的所有 commit 已经通过独立耐久性验证。

## P1-2：只读分发近邻已承认，但核心执行组仍可能完全跳过

**位置：** introduction 第 28–34 行；outline 近邻表 CVMFS/DADI/Nydus 行（第 44 行）；experiment plan B8（第 83 行）、E03、E05、E07、E13、最小证据门槛（第 344–352 行）。

**发现：** 引言明确说回答问题需要与 indexed/demand-loaded baselines 比较。实验计划却把 Nydus/CernVM-FS + upper 统一列为“可选”；E03 显式执行 B1/B2/B3/B4/B5，E05 只有内部 P0/P1/P2，E13 只有 B3/B5/完整系统。这样即使执行全部主实验，也可能没有一个成熟的远端 immutable lower 对照。

**为什么重要：** CVMFS 已有只读 catalogs 和按需内容获取，Nydus 已将元数据与数据 blobs 分开并实现 lazy loading。[S2][S3] 只比较远端 mutable KV 或已经预置到本地的 OverlayFS，不能充分支持 Packed lower 相对这些成熟技术的端到端价值。内部 sorted-KV 对照可以识别布局因素，但不能代替真实系统的缓存、启动和分发路径。

**建议落实：**

- B8 改为“至少一个可行的成熟 lazy immutable lower + writable upper；另一个为可选扩展”。E00 先验证实际可挂载和共同操作范围。
- 将选定 B8 纳入 E03 的冷/热首次就绪、E05/E06 的 lookup/readdir+stat 与缓存、E07 的构建摊销，并在 E13 选择一小组具代表性的共同任务比较。无须为所有微基准强制两套系统。
- 统一输入树、常用属性、数据内容、网络、内存和本地磁盘缓存预算；记录 RAFS/EROFS/FUSE 或 CVMFS catalog 版本、压缩、预取、bootstrap/catalog 下载、upper 持久性。
- 如有具体无法部署或语义不匹配的障碍，保存证据并说明被排除的范围，收缩相关结论；不能因其不方便安装而仍声称已经与成熟 immutable distribution systems 公平比较。
- 最小证据门槛中显式写入这个基线要求，避免 B8 在执行期间悄然消失。

## P2-1：SWE-bench Pro 版本方向正确，建议给出可执行的固定候选

**位置：** experiment plan §5.2（第 117 行）、环境字段（第 63–64 行）、E13 质量控制。

**现状判断：** “一个固定公开版本与数据 revision”是正确表述，文稿没有误称全部 Pro 都有 731 个任务。这是通过项，不是事实错误。

**仍可改进：** 本次重新打开官方 README 和 release commit，核实 **V2 / 2.0.0 于 2026-09-22 发布；default/test 为 642 个任务，hard 为 51 个任务，v1 为原始 731 个任务**。可将以下内容写为“正式实验的建议候选，实际执行前再次核验”，而非已执行环境：[S4][S5]

```yaml
dataset_id: ScaleAI/SWE-bench_Pro
dataset_version: 2.0.0
dataset_config: default
dataset_split: test
candidate_dataset_revision: 2d52cb3df914a3fcf80c7f66738b3a88ae37fc50
selected_task_manifest: null
harness_commit: null
container_digests: null
```

不要把 `default` 当成稳定版本标识；revision 和实例 manifest 必须同时固定。V2 应使用匹配的 `docker_image` 和 verifier/任务目录，不能无意复用 v1 的 legacy image tag。建议 E13 补充：agent 阶段和 fresh-sandbox grading 分开；gold patch、隐藏 verifier 和测试答案不能进入 agent 的可见工作区。原版 golden/reference 和 empty-patch 检查只在独立验证阶段使用。[S4][S6]

SWE-bench Pro V2 的 642 是总体公开任务数，不是本计划实际执行任务数；正式表格应报告筛选后的数量。Multi-SWE-bench 当前计划只写所选子集，没有混用 2,132/8 与早期 1,632/7 的统计，这是通过项。

## P2-2：少数动机句仍把待验证负载写成经验事实

**位置：** outline 第 9 行“多个编码智能体经常需要从相同仓库和依赖环境出发”；引言逐段安排第 105 行“反复读取目录与少量数据”。

**发现：** 英文 motivation 已把高共享、稀疏修改明确写成假设，但中文写作提纲里的“经常”“少量数据”可能在作者后续重写时重新变成未经测量的领域事实。SWE-agent/OpenHands 可以支持导航、编辑和工具执行的存在，不支持这些访问频率、字节比例或跨任务共享率。

**建议：** 改成场景限定，例如“本研究考虑从同一仓库版本和依赖环境创建多个独立任务的部署”，并注明反复元数据访问和局部读取由 RQ1 的实测决定。英文首段当前的条件性推导可以保留。

## P2-3：元数据服务的 per-file 依赖应限定为明确的比较配置

**位置：** introduction 第 17–18 行；outline Packed Metadata 行第 26 行。

**发现：** 引言的 `can ... depend on per-file queries` 已使用条件性语气，不属于严重错误；motivation 第 38–40 行也正确承认分区、批量和缓存。但中文表格仍容易被抽取为“既有基线都逐文件回访元数据库”。

**建议：** 把被测对象写清楚：`a per-entry KV baseline under cache misses` 或“所选择的逐条 KV 元数据配置”，而不是泛指 conventional mutable metadata services。若在引言保留比较性事实，可就近引用 TableFS/IndexFS，并继续说明实际代价要包含缓存与批处理。不要据 TableFS（本地元数据表）推导所有网络 MDS 的请求次数。

## P3：新论文出版状态可以再精确一点

**位置：** outline 第 38–39 行、关键来源 [R2]/[R3]。

- BranchFS 写“预印本/工作坊”没有虚报为 ASPLOS 主会，但可更明确标为“Agentic OS Workshop at ASPLOS 2026”，链接固定 `v2`。
- YoloFS 已出现在 SOSP 2026 官方论文列表并具有正式 DOI；相关工作应写“SOSP 2026”，而不是只写“2026”或仅以预印本身份展示。[S7]
- `mesafs2026` 仅书目信息核实，`HMFS` 尚待补读的边界应继续保留；不要为了使 Related Work 更满而补出未经阅读的技术差异。

## 引用与创新边界的通过项

| 检查点 | 判定 | 依据 |
|---|---|---|
| “Delta”是否被误称为字节级差分创新 | 通过 | Introduction 第 47–49 行明确否定 byte-delta compression；outline 第 25 行及 experiment plan 第 315 行一致。 |
| 共享快照/private delta 是否被声称为首次 | 通过 | Introduction 第 24–34 行主动承认 OverlayFS、BranchFS、DeltaFS 和 immutable distribution。 |
| 元数据打包是否忽略 TableFS/IndexFS 等 | 通过 | Motivation 第 33–40 行引用范围与原文内容相符。 |
| “零 KV”是否外推为整个 FS 无数据库 | 通过 | Motivation 第 52–57 行及 E05 把 upper/control/lower 分开。 |
| B/q 是否被混同为降低 k/m 冗余比 | 通过 | Motivation 第 69–75 行保持 data/parity 比例，指出校验和 CPU 成本。 |
| 后端小 Range 是否直接当成物理读字节 | 通过 | Motivation 第 77–82 行与 E08/E09 明确追踪完整路径和 shard 字节。 |
| 三机制已获得端到端收益的暗示 | 基本通过 | Introduction 明说组件、假设和 integration gaps；outline E00 停止门槛明确。最终 design/implementation 章节需保持同样分层。 |
| SWE-bench Verified 是否作为模型前沿排名证据 | 通过 | 实验计划定位为固定 FS workload，保留测试质量与污染说明。 |
| 引文 key 完整性 | 通过 | 两个 tex 文件中 14 个不同 key 均能在 bibliography 找到。 |

## 主来源

- [S1] [BranchFS 作者全文 v2，§4、§6、§8](https://arxiv.org/html/2602.08199v2)。本次主要使用其关于 fsync 与实现状态的陈述；未复现其性能。
- [S2] [CernVM-FS 正式论文](https://doi.org/10.1088/1742-6596/331/4/042003)。目录 catalog 与按需分发的设计证据。
- [S3] [Nydus 官方 RAFS 文档](https://nydus.dev/docs/concepts/rafs/)。软件技术文档，不冒称同行评议论文。
- [S4] [SWE-bench Pro 官方 README](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro/blob/main/README.md)。访问日期 2026-10-22；动态页面。
- [S5] [SWE-bench Pro V2 固定发布 commit](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro/commit/2d52cb3df914a3fcf80c7f66738b3a88ae37fc50)。可用来固定发布数据及对应元数据。
- [S6] [官方 V2 harness README](https://github.com/scaleapi/SWE-bench_Pro-os/blob/main/v2/README.md)。使用前仍要固定 harness commit；不能把 `main` 当可复现版本。
- [S7] [SOSP 2026 官方 accepted papers](https://sigops.org/s/conferences/sosp/2026/accepted.html) 和 [YoloFS 最终作者稿](https://arxiv.org/html/2604.13536v5)。

## 审阅快照哈希

| 文件 | SHA-256 |
|---|---|
| `paper/sections/01-introduction.tex` | `8aed850b662b687f44db6a1d1eceac2683084c98daf8109fef14bdb5e53d9a81` |
| `paper/sections/02-motivation.tex` | `78a02e56be19fac84a4949dd664b1a1073d32636d72c971cb6b41fd085bc9707` |
| `planning/01-research-outline.zh.md` | `dd2ca00d4e9e2c1fa18659c933ca2502eb86a9ee76c0d8008ad7e01dfaf2ce6e` |
| `planning/02-experiment-plan.zh.md` | `3225781dbe3d787296b27ba514f204b44117b13fe45f4c53ffa90e3087db3671` |
