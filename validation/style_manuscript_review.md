# BrewFS 英文初稿审阅

审阅日期：2026-10-22。使用 `skills/osdi-systems-paper/SKILL.md`，并按其中的 evidence、evaluation 与 BrewFS guardrails 检查。

审阅对象为 `BrewFS-OSDI-Research-Package/paper/main.tex`、十个 `sections/*.tex`、两幅图的源码、匿名名称预览入口，以及修订后的两份 `planning/*.zh.md`。未修改被审阅文件。本报告针对英文论证、证据状态、实验对照与术语；编译、页数、逐页视觉检查和最终字体检查由主作者工作流负责。本轮没有重新执行系统、重新测量或独立复现全部文献与源码结论。

## 总体判断

这份稿件已经是可以交付的**内部研究初稿**。标题的三项机制均在摘要中有准确对应，并在设计章节形成状态模型、读取或更新路径、适用条件、代价与实验之间的联系。摘要从共同基线和独立视图的需求出发，没有承诺未经测量的速度提升；`We present the design`、prototype components、remaining integration gates 和无新性能结果的声明共同界定了当前状态。

全文没有把 AX scaffold、源码中存在的机制、默认关闭的 q 或尚未接通的主工作区路径写成已经完成的端到端实验。§6–§8 特别保留了三个决定归因是否成立的事实：当前 auto 可能与默认 B 相同；Entity upper 的上传形成与完整对象校验限制布局收益；缓存、合并 GET、写预算和回复缓冲属于独立控制。它们应该保留，因为会直接改变实验解释。

稿件的主要结构是科学问题、模型和机制，而不是目录或函数清单。实现状态一节的细节较多，但多数直接解释实验资格，符合本阶段用途。当前可见的问题主要是两处符号精度，见下文；不需要重写总体论点。

## 本次应修正的两处表述

### M1. 参数对采用 `(B,q)`，避免 `B/q` 的除法含义

**位置：** `sections/06-layout.tex` 末段；`07-implementation.tex` 的实际对象布局；`08-evaluation.tex` 的 RQ4 表格与 automatic/default 对照；`09-related.tex` 的 Okapi 比较。

这些位置的 `B/q` 表示两个独立记录的布局参数，但数学中的 `$B/q$` 表示比值。尤其 `produce the same B/q, they are a no-treatment control` 如果按比值理解，会产生错误结论：64 KiB / 16 KiB 与 256 KiB / 64 KiB 的比值都为 4，实际编码和校验粒度却不同。

**建议：** 全部改为 `$(B,q)$`、`$B$ and $q$` 或 `the same persisted values of $B$ and $q$`。仅在真正讨论无量纲比值时使用 `B/q`。现有 q 覆盖帧数量公式、固定 `(d,p)` 的冗余比公式和选择器表格本身没有发现内部冲突。

### M2. 定义空间公式的计量范围和各项内容

**位置：** `sections/04-delta.tex` 最后三段，`M_total = M_S + Σ M_Δ_i + M_control`。

当前开头是 `expected space accounting`，但没有声明 M 是逻辑元数据字节、全部逻辑状态字节，还是后端物理占用。下一句只解释 upper records/mapping overhead，容易让读者把元数据模型理解成完整存储成本等式。

**建议：** 若本意是元数据共享模型，直接定义 live logical metadata bytes，并给出 lower metadata、每工作区 upper metadata 和 control metadata 的互斥计量范围。可以相应使用 `M_live-meta` 等明确下标。将 upper payload、EC/checksum/tail 开销、构建中间对象、待回收对象和缓存占用留在后续独立的物理空间与资源指标中。若希望公式覆盖完整物理空间，则必须相应扩充项与持久化层边界。

该修正并不否定 delta 的设计，只使公式与 §5 的带单位资源成本模型、§8 的实际空间计量一致。

## 核心实验与证据检查

| 检查点 | 当前稿件判断 |
|---|---|
| 强外部基线 | 已包含 full copy、reflink、OverlayFS、BranchFS、同后端对象文件系统和成熟 lazy immutable lower；没有以只战胜 full copy 作为充分证据。 |
| Packed 的布局控制 | 有 equivalent-record/cache 的 immutable sorted-KV，对逐文件 KV 的缓存能力也有公平约束；明确不把自行实现的控制冒称 DeltaFS。 |
| 本地与远端持久化 | 已明确分开 local workspace service 与 remote durable service，必要 checkpoint 成本进入比较；无法等价时分别报告。 |
| 组件因果归因 | 保留同一路径、同语义的 D/P/G 对照；合法全因子与嵌套设计有区分；ordinary VFS/Entity 切换不被当作单因素。 |
| 真实有效布局 | 按持久化 B 和 q 分组，auto/default 无处理差异可成为零效应对照；hint header 不作为实际布局证据。 |
| 完整任务 | replay 与 live agents 分工清楚，mount identity、工具输入、有效负载与输出质量均进入协议；明确失败不能作为快速成功。 |
| 正确性与故障 | 包含隐藏、覆盖、truncation、holes、rename/link、publication、integrity、repair 和 GC；fresh-only 与自动恢复界限正确。 |
| 不利条件与维护成本 | 构建、发布、重建、回收、修复、低局部性、高变化率和大顺序读都有安排。 |
| 执行规模 | 最小闭环核心为 20 tasks × 3 systems × 3 repeats = 180 runs；60-task 扩展为 540，明确没有把所有并发点自动展开。 |
| 统计单位 | 明确 run/task 而非请求为独立单位，并避免将同任务重复当独立二元样本；正式次数由 pilot 后冻结。 |

实验环境仍是申请资源，稿件采用 requested/proposed wording，没有声称已有七台机器或已完成 25 GbE 部署。实际 kernel、toolchain、对象布局和任务版本需在运行前冻结，作为规划阶段保留是合理的。

## 对上轮规划意见的复核

此前的六项规划意见已合理落实，无需再次提出为未解决问题：

- A1：构建摊销限定为相同单位的可加资源，并将并发 makespan 单列。
- A2：重复任务聚类与失败/超时进入主要完成统计，completed-only latency 明确为次要指标。
- A3：固定 B 敏感性与逐对象 policy efficacy 分开；新增策略需要独立调优后冻结并验证。
- A4：本地 overlay/reflink 与远端持久化服务分开，并明确 checkpoint 边界。
- A5：给出最小 180-run 核心、540-run 扩展和 pilot 驱动预算，广泛并发扫描优先 replay。
- A6：摘要与大纲明确 intended combined design / inspected components / integration gates。

## 值得做的三项改进

### I1. 将重复的状态提醒集中到一处，保留会改变读者判断的局部说明

Internal draft 的状态标签应保留。后续作者修订时，可把重复出现的 audit、integration obligation、not measured 表述收束到开篇状态段、§7 的小型状态表和必要局部限定。比如 q default-off、Entity upper whole-object integrity、directory/lifecycle limits 必须留在机制附近，因为它们决定代价或适用性；完整源码定位和每条检查过程放在 evidence ledger 即可。这样能增加解释设计理由的篇幅，也使正文更像论文而非审计报告。

### I2. 用一个贯穿的符号化访问例子说明三项设计的联系

现有 delta 修改示例、Packed 路径图和几何表分别清楚。可再用一小段把它们连起来：多个工作区读取同一只读 dependency entry，一个工作区改写局部区间；名称查询复用 packed lower，upper 只保留自己的映射，某一 lower frame 的读取在已持久化 `(B,q)` 下对应若干 shard intervals。只给逻辑流和符号，不填写测量值。这个例子应说明何时三项机制有关联，以及 full-object upper 校验何时切断这种联系。

### I3. 为明确命名但尚未进入 BibTeX 的实验来源补充出处

§8 已明确提及 SWE-bench Pro 与 JuiceFS，但当前 `references.bib` 没有对应来源。现有 `swebench2024` 是原始 SWE-bench 的出处，不能代替 Pro 的版本来源。建议在版本筛查时将官方 benchmark release/dataset 和 JuiceFS 官方架构或选定版本文档加入 source registry，并在相关句子引用。先保留已核验的官方来源；任务清单和 image digest 仍可标为运行前冻结。不需要为软件文档虚构会议论文。

## 格式与政策边界

源码采用官方 USENIX 样式、letterpaper/twocolumn/10pt 入口，未发现为压页数主动改变边距、行距的做法。`anonymous-preview.tex` 的注释明确表示仅名称切换预览，不能视为完整匿名检查。内部稿的现有命名与源码版本可保留用于研究追溯；未来投稿需要执行真正的匿名审阅。

本轮只确认这些代码与工作流表述；最终正文页数、图表字号、跨栏断行、引用解析、字体嵌入与每页视觉效果以主流程编译记录为准。投稿周期规则仍以 [OSDI 2027 CFP](https://www.usenix.org/conference/osdi27/call-for-papers) 和 [author requirements](https://www.usenix.org/conference/osdi27/requirements-authors) 为准。当前稿件适合以 internal research draft 交付，不能从编译成功推导为科学证据充分或可以直接投稿。
