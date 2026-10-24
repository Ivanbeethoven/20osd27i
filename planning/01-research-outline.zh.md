# BrewFS：OSDI 论文研究定位与写作大纲

工作标题：**BrewFS: Delta-Based Multi-Agent Workspaces with Packed Metadata and Variable-Granularity Object Storage**

编制日期：2026-10-22；原理框架更新：2026-10-23。文档性质：研究筹划与作者内部初稿。性能结论尚待实验；本文件不构成投稿完成声明。目标暂按 OSDI 2027 Research Track 规划，实际投稿取决于实验与作者审阅是否完成。

## 1. 应当证明的中心论点

在本文选定的场景中，多个编码智能体从相同仓库和依赖环境出发，在互不干扰的目录视图中探索、编辑和测试；共享程度与修改稀疏性由 RQ1 测量。BrewFS 的研究问题是：**如何利用这些工作区的共同不可变状态，同时降低独立视图的维护成本、只读基线的元数据访问成本，以及对象存储局部访问的实际数据搬运成本？**

拟论证的系统观点是：在普通文件接口、元数据服务和对象数据路径之上，分别选择工作区视图、不可变元数据表示和对象粒度。启用增量工作区时，以固定共享不可变下层（shared immutable lower）与私有可写上层（private writable upper，简称私有上层）组合视图；基线可以采用原生目录层，也可以选择打包式元数据。Packed 可独立只读使用，不承担私有修改语义。普通 flat 卷也可独立配置客户端块大小 g 和兼容后端的布局提示。三项能力可以组合，但不是依次开启的前置步骤。

这不是已经由数据证明的性能结论。论文需要分别检验：共享比例与私有变化是否适合增量工作区，名称区间布局是否适合不可变记录读取，对象大小及后端布局是否适合实际访问。某项机制无益时可以省略或缩小其适用范围；组合效果须在明确的同一路径中验证，不能预设收益相乘。完整关系与省略后的行为见 [三项机制关系框架](03-mechanism-relationships.zh.md)。

### 建议用于摘要和引言的贡献表述

> BrewFS provides three optional mechanisms over a common file and object data path. Delta-based workspaces combine a pinned immutable baseline with private mutable state. Packed Metadata organizes immutable namespace records in bounded, directory-oriented pages and can serve a standalone reader or a workspace lower. Object-granularity choices control client block formation and optionally request a compatible backend layout after the finalized upload length is known. These mechanisms address different costs and may be used separately or composed where the selected runtime supports their contracts. The evaluation will establish their individual effects, composition costs, and limits rather than assuming that every deployment benefits from enabling all three.

这段是工作性摘要表达，最后一句需在真实实验完成后由作者改写为有范围、有度量依据的结果。不得填入推测的加速比。

## 2. 三项设计如何对应标题

| 标题关键词 | 精确定义 | 所针对的问题 | 必须提供的证据 |
|---|---|---|---|
| 基于增量状态的多智能体工作区（Delta-Based Multi-Agent Workspaces，简称增量工作区） | 共享不可变下层与私有上层组合成视图；增量状态可以保存被修改实体的当前状态与数据映射，不要求字段级或字节级差分编码 | 重复物化相同目录树及其元数据，工作区初始化与存储开销随副本数扩大 | 创建和首次可用时间、物化元数据条目、共享与私有字节、修改比例敏感性、语义检查 |
| 打包式元数据（Packed Metadata） | 将选定只读目录子树的完整元数据与访问结构组织为打包式不可变快照（packed immutable snapshot，简称 packed snapshot）；按名称区间联合组织目录项、常用属性及数据定位信息，用分层分页索引访问 | 只读小文件基线反复经过逐文件元数据库查询，访问相关信息分散 | lower-KV 请求计数、对象请求数/传输量、缓存命中、lookup/getattr/readdir/read 延迟、索引内存上界 |
| 可变粒度对象存储（Variable-Granularity Object Storage） | 选择客户端块大小 g 控制对象形成；在最终上传对象长度（finalized upload length，L_o）确定后，可选地请求布局提示（layout hint），由兼容后端验证和持久化纠删码编码块大小 B 及适用的物理校验／读取粒度 q | 应用请求、客户端块、上传对象、编码块与物理读取单元之间失配 | 固定 g 对照、实际对象长度/请求数、范围读取与整对象获取分离、持久化 B/q、读/写/修复各层字节、编码和校验 CPU |

“打包式元数据”不等于一个单独的元数据包；ReadGroup 是逻辑读取组，GroupMeta 是其中的组元数据页。快照可以覆盖选定目录子树，不必覆盖整个卷。“下层查询独立性”只指所支持的只读下层查找路径无需回访元数据库；工作区控制记录、私有上层和生命周期管理仍可能使用元数据库。中英文名称沿用[已确认术语表](terminology.zh.md)。

“可变粒度”不等于已实现在线学习或动态调参。普通路径默认 Chunk 为 64 MiB、g 为 4 MiB；当前提供固定配置，PPT 的 1/4/8/16 MiB 是待评估的客户端粒度档位。L_o 还受压缩、头部、尾段和对象形成路径影响。独立的自动提示策略（automatic hint policy）对 L_o > 1 MiB 请求 1 MiB B，对不大于该阈值的对象省略提示；这个规则在所审计 RustFS fork 中可能与默认 B 相同。B hint 与 q 各有默认关闭的后端兼容性开关；普通路径不启用它们仍可运行，现有代码不构成收益证据。详见 [当前对象层审计](../evidence/principles-code/objects.md)。

## 3. 创新边界：需要正面回应的近邻

| 已有工作 | 与本研究重叠之处 | BrewFS 应当具体解释的区别 | 对实验的要求 |
|---|---|---|---|
| Linux OverlayFS | upper/lower、覆盖、whiteout、目录合并 | 面向远端不可变快照的私有元数据/数据映射及 lower 访问结构；分层思想本身属于已有技术 | 采用预置基线的 OverlayFS 强对照；计入远端获取和持久化成本，分开报告本地最佳情形 |
| BranchFS（2026，预印本/工作坊） | 智能体探索、COW 工作区和分支生命周期 | BrewFS 的重点在共享基线的元数据读路径与对象后端布局；不要以“agent + COW”作为原创性 | 支持共同操作子集的工作区对照；不同 commit/merge/process 语义单列，不强行等价 |
| YoloFS（2026） | staging、快照、智能体文件系统 | 其主要研究问题是可见性、权限与纠错；BrewFS 研究资源和 I/O 成本 | 相关工作必须覆盖；是否性能比较取决于可比操作契约，不能据无比较就宣称更优 |
| DeltaFS（SC 2021） | 对象存储、私有命名空间、不可变日志、快照与增量 | 必须落到 directory-oriented 联合布局、按需分页读取、在线 writable upper 的语义与访问成本 | 优先评估真实实现可比性；必要时另设“不可变排序 KV 表”机制对照，明确它不是 DeltaFS 复现 |
| TableFS / IndexFS / LocoFS / InfiniFS | 元数据组织、索引、分区与缓存 | 打包式不可变快照作为下层，把特定不可变子树的必要信息置于对象存储；与可变全局元数据库的职责不同 | 同资源 mutable-KV 对照；统一值内容和缓存预算，避免将缓存优势当成布局优势 |
| Mantle（SOSP 2025）及较新的元数据系统 | 云对象存储上的层次元数据管理 | 区分存储服务的目录索引、元数据引擎与 BrewFS 的只读文件系统快照格式 | 逐项说明服务边界；不能只用十年前系统论证新颖性 |
| Okapi（OSDI 2025） | 解耦存储布局决策 | Okapi 区分 striping 与 redundancy grouping；BrewFS 分别讨论客户端对象形成 g、最终上传对象长度、编码块大小 B 与物理校验／读取粒度 q，不能混称同一“解耦” | 同可靠性几何下测量；保留数据、校验、repair 成本，不只看吞吐 |
| CernVM-FS / DADI / Nydus | 不可变目录、镜像/快照索引与按需拉取 | 说明 BrewFS 的工作区视图和文件系统数据映射如何使用共享快照，哪些能力其实已有 | 至少讨论镜像分发、只读 lower 与可写工作区之间的差别；不把冷启动问题全部归于复制 |

本表是研究定位，不是竞品能力的完整清单。详细原文证据与出版状态见 `references/literature_matrix.md`。截至本次核验，**不能主张“首次将快照、私有增量或对象元数据用于智能体文件系统”**。[R1–R6]

## 4. 实现证据分层

使用以下四类标签管理每个主张，而不是把整个项目归为“已实现”：

- **规范约定（Specified）**：规格写清楚了预期行为，尚不能证明代码或运行结果。
- **源码存在（Implemented）**：固定提交中有实现及可追溯入口；不等于当前运行配置已启用。
- **接入可运行（Integrated）**：特定 build/config/mount 路径能完成操作，需保留 smoke 日志。
- **实测支持（Measured）**：有可重现配置、原始数据和分析，能支持限定的结果主张。

本轮原理更新依据作者 PPT 和 BrewFS `242af5f7e9bba7afc0c61778f1084fcb20e083a0` 源码快照，没有运行 BrewFS 挂载或性能测试。8 个真实 Agent 任务、1,138,884 条 FUSE 请求的已有重分析只支持已报告的负载结构观察，不支持系统收益。历史 `518e7cc` inventory 与先前 `f80e714` 审计保留其原始版本边界；RustFS 扩展仍限定于研究 fork `cc4926fac110`。

关键边界如下：

1. `workspace-v1`、`workspace-entity-v1`、打包式不可变快照的只读挂载与 Native Base 是不同入口。Entity 直达专用 namespace/data 路径，不能和常规 VFS 路径互换后声称“仅切换增量工作区机制”。
2. Entity 的 direct I/O、TTL=0、写回限制和 chunk 几何，与 legacy/flat 不同。Entity 仍是显式选择的实验路径，不宣称生产可用或完整 POSIX。
3. q 开关默认为 false；开关打开也不保证 q 小于 shard。必须记录每个对象的实际布局以及适用条件。
4. 普通 VFS 的布局提示模式还会改变整对象获取的请求合并和 LRU/SingleFlight 策略；写预算释放及共享回复是该 VFS 中另外保留的优化，没有布局提示门控。实验必须固定或分别控制这些因素；Entity 不走这些普通 VFS 路径。
5. AX 目录提供集成约定与部署脚手架。只有确认任务、子进程、依赖目录均实际访问目标 mount，才能称为 AX+BrewFS 端到端实验。
6. 先前 DSH `0.1.5-rc.1` + `deepseek-v4-flash` 的 WSL passthrough 记录可用于形成工作负载假设；它不是 BrewFS/RustFS 性能数据。退出码 0 也不是 SWE-bench 问题解决成功。
7. **组合接线尚未完整证明**：`src/cli/entity_mount.rs` 构造 `S3Config` 时未传递普通 CLI 的 `rustfs_ec_block_size_hint`；`packed_v3_snapshot_fixture.rs` 的 S3 配置也未传递该字段。Entity 上层读取目前可能 HEAD 后读取整个对象、验证 SHA-256 再切片。论文需要把“组件已有代码”和“同一工作区的联合布局效果”分开；此外，EntityData 调用的 `S3Backend::put_object_create_only_durable()` 本身也未附带布局提示元数据。E00 必须核验每项处理所需的接线；仅在研究相应组合时补齐这三处并保留条件写语义，不能把它们作为普通 flat 或默认布局实验的前提。当前 Entity FUSE 单次写入至多 1 MiB、按本次写直接切片上传，自动提示策略仅对大于 1 MiB 的对象发送布局提示，因此补齐接线也不会让现有挂载的上层触发自动提示策略的提示分支。应先在打包式不可变快照构建／普通最终对象上传路径验证策略，再按实际上层对象分布限制组合结论。

当前行级证据见 [工作区](../evidence/principles-code/workspaces.md)、[打包式元数据](../evidence/principles-code/packed.md) 和 [对象粒度](../evidence/principles-code/objects.md)。`evidence/source_evidence.md` 与 `evidence/implementation_inventory.csv` 为历史检查点记录。

## 5. 研究问题与论文证据链

| RQ | 问题 | 主要实验 | 应形成的结论形式 |
|---|---|---|---|
| RQ1 | 真实 agent 负载是否存在足够的共享基线、元数据重复访问与细粒度 I/O？ | E01–E02：重新采集、按阶段和任务分析 | 在指定 harness/任务族中观察到何种分布，以及哪些任务不满足假设 |
| RQ2 | 增量工作区在何种规模和修改比例下减少创建与存储成本？ | E03–E04：生命周期和 churn | 成本随文件数、工作区数与变化量如何增长，何时退化 |
| RQ3 | 打包式不可变快照独立读取或作为下层时，能否在统一缓存预算下减少元数据库依赖与总访问成本？ | E05–E07：布局、缓存、构建摊销 | lower-KV 消除是否成立，节省是否被索引请求/过取/构建代价抵消 |
| RQ4 | 客户端 g、取数策略和后端 (B,q) 分别改变哪些请求、字节及物理 I/O？ | E08–E10：布局、策略因子和写/修复 | 固定 g 与 B/q 效应分开；读、写、校验与恢复代价，无收益或回退也应报告 |
| RQ5 | 三项机制之间存在可解释的组合效应吗？ | E11：合法因子消融 | D×P、P×G 的效应是否可测；非独立组合如何限制因果解释 |
| RQ6 | 这些改进能否转化为多 agent 任务吞吐、就绪时间或资源收益？ | E12–E13：回放和 AX/DSH 真实任务 | 存储关键路径及端到端改善，模型时间占比与输出质量保持情况 |
| RQ7 | 隔离、完整性、崩溃恢复和资源回收的边界是什么？ | E14–E16：语义、故障、稳态尾延迟 | 经过验证的操作范围、失败行为及剩余限制 |

详细实验协议见 `02-experiment-plan.zh.md`，机器可读列表见 `experiments/matrix.csv`。这里没有把 RQ 写成预期答案。

## 6. 12 页正文的写作结构

以下为完成实验后的篇幅预算；初稿允许更短，不用空白结果图填页数。参考文献另计。

| 章节 | 目标页数 | 核心内容 | 读者应理解什么 |
|---|---:|---|---|
| 1 Introduction | 1.2 | 场景、具体代价、近邻缺口、统一观点、贡献与结果摘要 | 为什么该问题具有系统意义，三项可选设计各自解决什么成本、何时组合 |
| 2 Background and Motivation | 1.4 | agent 执行阶段、工作区复用、真实 trace、现有方案局限 | 观察支持设计，且观察有样本和适用范围 |
| 3 Overview and Contract | 0.7 | 基础路径、三项可选能力、对象身份、私有与共享状态 | 启用与省略后如何工作，哪些组合已有接线，哪些保证不包含在系统内 |
| 4 Delta-Based Workspaces | 1.1 | namespace 覆盖、删除标记、数据映射、复制/创建与语义边界 | 增量状态的具体含义及在线解析成本 |
| 5 Packed Metadata | 1.3 | 选择子树、名称区间布局、分页路径、构建发布和缓存 | lower 读取如何不依赖逐文件 KV，代价转移到何处 |
| 6 Variable-Granularity Object Storage | 1.0 | g 的对象形成、L_o、请求与读取代价、可选 B/q、持久解释与兼容 | 固定配置与动态方案的区别，各层粒度如何影响请求和字节 |
| 7 Implementation | 0.6 | 固定实现入口、启用状态、外部依赖、插桩 | 设计在什么配置上实际运行 |
| 8 Evaluation | 3.7 | RQ2–RQ7 结果；RQ1 画像可放动机 | 与强基线的因果证据、边界、摊销和负面结果 |
| 9 Related Work and Limitations | 0.8 | 与最接近工作逐项区别、剩余问题 | 创新边界和结论适用范围 |
| 10 Conclusion | 0.2 | 已经由数据支持的一个系统性结论 | 读者应带走的设计经验 |
| **合计** | **12.0** | 不含参考文献 | 不靠缩小字号或负间距满足限制 |

### 引言逐段安排

1. 从可观察的执行动作进入：多个隔离任务共享仓库和依赖，并反复读取目录与少量数据；不以“AI 快速发展”开篇。
2. 解释现有工作区物化、远端元数据访问、对象读取之间的具体开销，避免把所有现有系统描述成全量复制。
3. 用已有请求结构观察及后续完整画像限定负载假设；当前 passthrough 数据不识别 BrewFS 的性能瓶颈，也不能把累计 handler time 写成任务墙钟或后端存储延迟。
4. 正面承认 OverlayFS、BranchFS、DeltaFS 等已提供的机制，然后指出本文要解决的精确接口和布局问题。
5. 给出视图构成、不可变记录组织、对象形成及后端布局的选择边界，说明各机制可以省略，且组合须满足实际入口契约。
6. 用两三句展开每个机制的具体行为；贡献表述包含可检验对象，不使用“高效”“智能”等无度量形容词。
7. 最后写有条件、可复现的结果。当前初稿保留“planned evaluation”说明，未来由作者依据数据完成。

### 设计章节共同模板

每节依次说明：目标约束 → 关键数据结构/接口 → 一次典型操作 → 正确性不变量 → 代价及反例。不要只有组件列表，也不要把整个源代码图直接放入论文。三节分别使用一个清晰例子：修改/删除一个继承文件；一次 lookup+getattr+read；固定 g 的对象划分及范围读取怎样映射到 B/q。明确 dirty overlay 仅合并本客户端未完成写回的字节，不等同于工作区增量状态。

## 7. 图表规划

| 图表 | 内容 | 数据或来源要求 |
|---|---|---|
| Figure 1 | 基础文件路径与三项可选机制：视图、不可变元数据表示、g/L_o/后端 B/q | 源码核验的架构示意，不画成强制串联，也不是实验结果 |
| Figure 2 | workload 阶段与 metadata/read/write 分布 | 新 trace、任务分组、样本数；不能只画聚合饼图 |
| Figure 3 | 单个目录名称区间及分页查询示意 | 说明 index page、GroupMeta、data locator 的区别 |
| Figure 4 | 工作区创建/首读延迟和元数据占用随并发变化 | OverlayFS/reflink/对象文件系统基线，说明预置和冷取 |
| Figure 5 | 打包式元数据布局分解：KV 调用、对象 GET、传输量、P99 | 同缓存预算，各请求种类单列 |
| Figure 6 | B×q 实际物理读放大与校验 CPU | 用有效布局分面，inline/fallback 单列 |
| Figure 7 | 固定客户端 g、Range/整对象策略与后端 layout 的分层因子结果 | 相同应用 trace；g 变化使用独立对象集，固定 writeback/cache 其余因素 |
| Figure 8 | 构建快照的摊销与 churn 负面区域 | 包含重建、上传、回收；不能隐去构建成本 |
| Figure 9 | 多 agent provisioning、工具执行、model wait 分解 | tracing 关键路径，不把重叠时间相加 |
| Figure 10 | 组合消融与资源-性能曲线 | 只测合法配置；没有交互效应也应如实解释 |
| Table 1 | 操作语义与支持边界 | 同一运行入口的实际行为及错误码 |
| Table 2 | 环境、版本、cache/durability 配置 | 实机采集值；规划值不能原样当作已使用环境 |
| Table 3 | 故障/完整性测试与恢复结果 | 故障点、预期结果、观测结果和遗留风险 |

论文空间不足时，将 Figure 2 只保留最能解释设计的分布，将部分敏感性结果放单独复现材料。主结论的必要证据必须留在正文。

## 8. 可能导致审稿失败的问题及应对

**问题 A：只是将已有 OverlayFS、索引和 EC 机制拼接。** 回应必须来自统一操作契约、具体布局和组合实验证据。D×P 无交互时，诚实说明它们减少不同瓶颈；若 G 无额外作用，重新评估第三项是否适合与另外两项同等突出，不能用表述弥补数据缺口。

**问题 B：新场景没有新的系统挑战。** 需要真实 agent fan-out、共享依赖与变化比例的画像，也需要同样仓库的传统构建/CI 对照。若两类负载无法区分，就把适用范围写成“共享基线的短生命周期工作区”，避免宣称 agent 专属。

**问题 C：收益来自更大的缓存或放宽持久化。** 在预算、缓存状态和完成条件一致时比较；记录 fsync、对象上传和元数据提交完成时间。不能只计前台 write 返回。

**问题 D：打包式元数据的下层零 KV 查询只是 warm cache 效应。** 在冷数据页、受控索引缓存及禁止下层元数据库访问的条件下验证；区分上层检查和下层回访。

**问题 E：(B,q) 机制未实际启用。** 上传后读取有效布局并采样后端持久化值；按对象长度、inline 状态、MPU、保护模式分组。开关不是证据。

**问题 F：模型时间掩盖存储时间。** 同时做确定性回放和真实闭环 agent；报告关键路径占比与端到端收益，不从微基准推导任务成功率。

**问题 G：失败、恢复或长期垃圾未评估。** 用 E14–E16 覆盖并保留负面行为；修改粒度过大、snapshot churn、目录热点、长尾与 repair 并发均应出现。

## 9. 执行顺序与决策门槛

### 阶段一：固定可测系统（建议 10 月 23 日—11 月 1 日）

冻结每项实验的入口与 commit；先核验默认路径和机制单独使用，再验证拟测组合所需的下层、私有上层和对象布局接口；补因子控制、每层字节计数、持久化完成标记。完成小规模语义/布局验证并补采 workload 字段。组合未接通时仍可报告合格的独立组件结果，但不得将其写成该组合的总系统性能结论。

### 阶段二：机制与反例（建议 11 月 2—12 日）

优先 E03、E05、E08/E09；随后验证构建摊销、高 mutation 和顺序大读反例。先完成最接近机制对照，再扩大规模。若增益只出现在弱基线，不扩写引言中的性能承诺。

### 阶段三：组合、故障和端到端（建议 11 月 13—22 日）

完成 E11–E16、独立回放和闭环 AX/DSH 任务；检查正确性及失败样本。明确哪部分收益来自 provisioning、metadata 和 I/O，哪部分被模型或构建计算掩盖。

### 阶段四：作者实质写作和冻结（建议 11 月 23 日—12 月 1 日）

作者基于原始结果重写摘要、引言和 Evaluation；逐条核实相关工作；确定题目是否仍准确覆盖三项有证据的贡献。整理匿名稿和复现包；至少安排一次不带作者解释的内部阅读。

OSDI 2027 官方时间对应北京时间：摘要注册 **2026-12-02 06:59**，全文 **2026-12-09 06:59**。建议内部目标分别提前至少 24 小时；只有已完成研究能支撑摘要时才注册。最后一周用于消除证据和表达问题，不承担大规模重构。官方日期与规则可能更新，投稿前再次核验。[O1]

## 10. 格式与作者责任

OSDI 2027 要求正文至多 12 页（含图表），参考文献另计，US Letter、10pt/12pt、双栏 7×9 in 文本区和 0.33 in 栏间距，需页码。主 PDF 不用附录突破页数限制；CFP 允许另传补充文件，但正文必须可独立评审。[O1][O2]

当前标题保留用户确定的 BrewFS 名称用于内部交流。Research-track 匿名投稿需按官方规则处理公开系统名称、仓库链接、作者机构、PDF metadata 和自引。仓库只维护命名研究稿；仅替换系统名称不能完成匿名审查，正式投稿时需要作者重新检查并制作投稿文件。

官方 CFP 还规定不接受完全或大部分由 AI 生成的投稿，允许 AI 编辑工具。因此本包是供作者推进研究、核验事实和实质重写的工作底稿；不能将本次生成的英文稿原样作为投稿。此要求来自官方投稿政策，而不是对研究方向的额外限制。[O1]

## 关键来源

- [O1] [OSDI 2027 Call for Papers](https://www.usenix.org/conference/osdi27/call-for-papers)
- [O2] [OSDI 2027 Requirements for Authors](https://www.usenix.org/conference/osdi27/requirements-authors)
- 当前原理依据：[机制关系](03-mechanism-relationships.zh.md)、[PPT 正文与讲稿](../evidence/ppt-principles/slides.json)、[工作区代码审计](../evidence/principles-code/workspaces.md)、[Packed 代码审计](../evidence/principles-code/packed.md)、[对象粒度代码审计](../evidence/principles-code/objects.md)。
- [S1] [BrewFS cooperative I/O design，历史固定提交](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/innovations/brewfs-rustfs/design.md)
- [S2] [RustFS EC layout，固定提交](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/object_api/ec_block_layout.rs)
- [R1] [OverlayFS，Linux 官方文档](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html)
- [R2] [BranchFS 原文](https://arxiv.org/abs/2602.08199)
- [R3] [YoloFS 作者预印本](https://arxiv.org/abs/2604.13536)
- [R4] [DeltaFS，SC 2021 原文](https://www.pdl.cmu.edu/PDL-FTP/Storage/zheng-deltafs_sc21.pdf)
- [R5] [Okapi，OSDI 2025](https://www.usenix.org/conference/osdi25/presentation/athlur)
- [R6] [Mantle，SOSP 2025 作者页面](https://madsys.cs.tsinghua.edu.cn/publication/mantle-efficient-hierarchical-metadata-management-for-cloud-object-storage-services/)
