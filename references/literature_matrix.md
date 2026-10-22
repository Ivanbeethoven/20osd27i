# BrewFS 文献核验与可辩护差异

核验日期：2026-10-22。本文档对应 `references.bib` 的 29 个条目：23 篇研究论文（其中 BranchFS 是 workshop 论文）、6 项官方技术文档、数据集或研究公告。原有 27 条保持不变，补入 SWE-bench Pro V2 数据集与 JuiceFS 官方架构文档。MesaFS 的书目信息已经核验，但本次未取得可阅读的全文，因此**只列为必须补读的近邻，不依据搜索摘要写技术比较**。其余条目阅读深度见 `source_registry.csv`。

本文件描述的是文献证据和 BrewFS 的**拟议定位**。它不能代替 BrewFS 代码审计，不能证明实现已经具备某项语义，也不包含 BrewFS 实验结果。引用用稳定 BibTeX key 标记；每行提供主来源。

## 1. 对论文定位最重要的结论

**需要收紧“首次”或单点机制创新的叙述。** 共享不可变基线、私有差分、目录元数据聚合、懒加载和编码参数分离均有直接先例。尤其 DeltaFS 已经组合了每作业私有命名空间、对象存储、不可变 SSTable 日志以及快照 manifest；CernVM-FS 已经使用只读目录目录表和内容寻址；BranchFS 与 YoloFS 已经直接面向 agent 的文件系统操作。BrewFS 的贡献应建立在三项设计之间的具体连接、清晰约束及其可测收益上，而不能来自对这些已有机制更名。

当前最值得检验的研究主张是：**在共享大规模只读基线且各工作区独立修改的场景下，目录感知的有界分页布局与私有上层解析协同减少元数据服务依赖；再把布局生成的最终对象大小传到后端，使编码块与物理读取粒度分别适配实际对象和请求。** 这是待验证的系统假设，不是已证实的新颖性判断。是否足以支持 OSDI 投稿，要看端到端瓶颈证据、强基线、正确性和多维消融。

## 2. 命名空间、元数据布局与服务

| 文献及主来源 | 问题与已核实方法 | 与 BrewFS 的重叠 | 可辩护的差异与必须检验的内容 |
|---|---|---|---|
| [`tablefs2013`](https://www.usenix.org/conference/atc13/technical-sessions/presentation/ren), ATC 2013 | 把本地文件系统元数据组织为表，以父目录和名称相关的 key 排序，行中包含属性，小文件可内联；LSM 合并减少随机写。已读布局相关章节。 | 名称邻近性、目录项与属性共同组织、聚合小对象均已有先例。 | BrewFS 拟针对对象存储中的共享只读子树，而非可变本地 LSM。必须比较同等缓存下 lookup、readdir+stat 的页数与字节数，不能把“元数据装进对象”单独当创新。 |
| [`indexfs2014`](https://www.pdl.cmu.edu/PDL-FTP/FS/IndexFS-SC14.pdf), **SC 2014** | 目录分区、无状态缓存、SSTable 格式及客户端批量导入，提高分布式元数据服务性能。已读设计及 bulk insertion。 | 有序表、目录聚合、减少每文件 RPC。 | BrewFS 拟让选定的不可变 lower 查询避开 KV 服务；IndexFS 针对可变元数据的服务与导入。需要对照 SSTable 布局及批量构建成本，不能把 bulk creation 的收益全归因于新增格式。 |
| [`deltafs2021`](https://www.pdl.cmu.edu/PDL-FTP/Storage/zheng-deltafs_sc21.pdf), **SC 2021** | 每作业私有命名空间；修改形成对象存储上的不可变 SSTable 日志；manifest 保存成员及 key 范围；注册服务记录快照。已读命名空间及对象布局。 | **最强概念近邻之一**：private delta、共享快照、对象存储承载元数据均重叠。 | 需说明 BrewFS 的目录名称区间分页、常用属性和 locator 同页、实时 upper/lower 合成以及 B/q 连接提供什么不同取舍。应做一个逻辑等价的 SSTable/LSM lower 布局对照；不要把它命名为完整 DeltaFS，除非真的运行原系统。 |
| [`locofs2017`](https://storage.cs.tsinghua.edu.cn/papers/sc17-locofs.pdf), SC 2017 | 减少层次命名空间在 KV 上的操作依赖，解耦目录相关信息与文件元数据。阅读作者公开 PDF 的摘要及设计内容。 | 同样认为 namespace 组织方式决定元数据请求成本。 | 不能笼统说已有 KV 文件系统只支持逐级串行请求。BrewFS 的特殊条件是固定 lower 可以离线组织；需展示可变目录与不可变 lower 的边界。 |
| [`infinifs2022`](https://www.usenix.org/conference/fast22/presentation/lv), FAST 2022 | 分离 access/content metadata，结合推测式并行解析与客户端缓存，缓解路径解析开销。本次读官方摘要。 | 路径解析、属性访问与 RPC 减少。 | 属于可变服务优化路径；BrewFS 拟用 lower 不可变性去除特定查询对 KV 的依赖。此差异不能外推成“所有文件操作均不访问元数据库”。 |
| [`mantle2025`](https://madsys.cs.tsinghua.edu.cn/publication/mantle-efficient-hierarchical-metadata-management-for-cloud-object-storage-services/SOSP25-Li.pdf), SOSP 2025 | 在对象服务上提供层次元数据：IndexNode 集中必要目录信息，TafDB 存储元数据，使用路径缓存与更新机制减少开销和争用。已读架构及目录处理。 | 对象存储中的层次命名空间和减少远程元数据访问，**必须讨论的近期近邻**。 | Mantle 管理活跃可变命名空间；BrewFS 限定于已发布只读子树加私有修改。需量化发布、缓存失效和 upper 增长成本，不能仅比较理想只读路径。 |
| [`switchfs2026`](https://arxiv.org/html/2410.08618v3), EuroSys 2026 | 延后目录更新，利用交换机中的 dirty set 维持可见性，在读目录时聚合并应用更新。已读架构及操作协议。 | 都试图降低目录元数据访问和同步成本。 | SwitchFS 处理可变目录更新与协调；BrewFS lower 不可变避免了相应协调域。硬件依赖不同，应作定性比较，不强行声称标准机器上的性能优越性。 |
| [`mesafs2026`](https://doi.org/10.1145/3767295.3803573), EuroSys 2026 | 标题、Hao Guo / Jiwu Shu / Youyou Lu、会议年份与 DOI 已由作者和会议主来源交叉核实。ACM 全文读取返回 403。 | 标题表明它属于非常相关的元数据 I/O 研究方向。 | **技术差异尚未判定。** 不把搜索结果中“一次 SSD 写”等摘要片段写成已阅读的证据。投稿前必须取得作者版或出版版，完成机制与实验对照。 |

## 3. 共享只读基线、分发与 agent 工作区

| 文献及主来源 | 问题与已核实方法 | 与 BrewFS 的重叠 | 可辩护的差异与必须检验的内容 |
|---|---|---|---|
| [`cvmfs2011`](https://doi.org/10.1088/1742-6596/331/4/042003), JPCS 2011 | CernVM-FS 发布只读软件树，用可嵌套 SQLite catalogs 保存目录、属性与内容 hash；文件和 catalogs 可缓存并按需获取。已读设计。 | **最强 readonly metadata 近邻之一**：子树 catalogs、元数据聚合、内容位置、共享不可变内容。 | 需要解释 BrewFS 有界分页索引相对 nested catalogs 的冷启动、点查和宽目录扫描取舍；CVMFS + OverlayFS 是重要系统基线候选。不能把 CVMFS 描述为必然预取整个仓库。 |
| [`overlayfs`](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html), 官方内核文档 | upper 覆盖 lower，whiteout 表示删除，目录合并；copy-up、metacopy、redirect_dir 等配置会改变代价和语义。已读相关章节。 | 直接继承的覆盖语义，应在设计中明确致谢。 | BrewFS 若只复制元数据和数据映射而非整个文件，应证明相应实现并测首次小修改。基线必须记录内核、metacopy、redirect_dir、index、xino 等有效设置，不能挑一个弱默认配置代表所有 OverlayFS。 |
| [`nydus_rafs`](https://nydus.dev/docs/concepts/rafs/), 官方技术文档 | RAFS 将元数据与数据 blobs 分开，支持按需加载和 chunk 级处理；不同版本涉及 FUSE 与 EROFS。本次阅读概念与 lazy-loading 文档。 | 元数据打包、只读镜像、共享数据与远程按需读取。 | Nydus + OverlayFS 是重要现代基线候选；需统一版本、缓存、压缩、chunk 与 bootstrap 条件。BrewFS 的分页目录元数据是否优于已有 bootstrap 必须测量，不能仅对比逐文件 S3 GET。 |
| [`slacker2016`](https://www.usenix.org/conference/fast16/technical-sessions/presentation/harter), FAST 2016 | 通过后端共享存储与懒加载降低 Docker 镜像分发及启动开销。本次读官方摘要。 | 避免为每个实例提前复制所有内容。 | 它支持容器启动的背景论证，不能提供 agent 的文件访问比例。BrewFS 需同时测初始化和稳定运行；不能将旧论文工作负载的稀疏读取比例挪作本系统动机数据。 |
| [`dadi2020`](https://www.usenix.org/conference/atc20/presentation/li-huiba), ATC 2020 | 面向镜像的块级按需读取和分发服务，改善部署效率。本次读官方摘要。 | 惰性物化共享基线。 | 比较应区分镜像分发问题与长期可变工作区语义；启动收益不能代替 readdir/stat/随机读取证据。 |
| [`xethub2023`](https://www.cidrdb.org/cidr2023/papers/p43-low.pdf), CIDR 2023 | 把 Git 风格的版本管理扩展到大数据，结合内容共享与数据版本组织。已读摘要和系统概述。 | 共享版本、避免全量重复数据。 | 不能写“Git worktree 必然复制仓库对象”；应分别测工作树物化、已有对象共享和运行时访问。Xet 属于相邻的数据版本管理工作，不必强行当 POSIX FS 性能基线。 |
| [`agentfs2025`](https://turso.tech/blog/agentfs), 官方软件公告 | SQLite 承载文件系统、键值状态及工具调用信息，强调 agent 状态的可保存和检查。已读公告及官方仓库。 | 明确面向 agent 的文件系统抽象。 | 这是软件事实而非同行评议论文；不要写成“首个 agent 文件系统”。BrewFS 拟聚焦多工作区共享与远端存储效率，应按固定版本核对其接口和持久性再选择比较范围。 |
| [`branchfs2026`](https://arxiv.org/html/2602.08199v2), **Agentic OS Workshop / ASPLOS 2026** | 已实现 FUSE 文件级 COW、分支链与 first-commit-wins；首次改文件复制整文件。`branch()` 系统调用仍是提案。已读 §4、§6、§8。 | **直接工作区近邻**：agent 私有差分、低成本创建和生命周期。 | BrewFS 的远程共享基线、目录布局与映射级修改是可检验的差别；是否支持 commit、嵌套分支不能自行补全。BranchFS 的 ephemeral `fsync` 是 no-op、持久化在 commit；若比较吞吐必须匹配语义。 |
| [`yolofs2026`](https://arxiv.org/html/2604.13536v5), **SOSP 2026** | agent 文件系统控制与观察：staging、权限、快照/恢复；设计使用 override tree 与 flat file store。已读 §5 设计。 | agent 文件系统及路径与内容映射分离，属于不可遗漏的近期近邻。 | 主目标为操作可控性和安全工作流，BrewFS 为共享与 I/O 效率；此差异是目标和部署范围，不能推导出性能胜负。不能声称 BrewFS 率先为 agent 引入快照或映射。 |

## 4. 分布式存储与纠删编码

| 文献及主来源 | 已核实主张 | 对 BrewFS 写作及实验的约束 |
|---|---|---|
| [`ceph2006`](https://static.usenix.org/event/osdi06/tech/full_papers/weil/weil_html/index.html), OSDI 2006 | 元数据管理与对象数据服务分离，客户端可以直接访问对象数据；已读架构。 | 可支持分离式文件系统背景。历史论文不能描述今日 CephFS 的全部能力；若用当前版本作基线，应补其固定版本配置及功能核验。 |
| [`juicefs_architecture`](https://juicefs.com/docs/community/architecture/), 官方 Community Edition 文档 | 客户端连接对象存储和元数据引擎；文件经过 chunk、slice、block 层次组织，最终对象不必等于最大 block 尺寸。页面标明 2025-11-06 更新，2026-10-22 阅读。 | 支持把 JuiceFS 选为同类对象文件系统基线，不证明与指定 RustFS fork 已兼容。需要实测固定版本、对象服务、元数据库持久性、缓存和块配置；不能把逻辑 chunk、最终对象或后端 EC 粒度混称为同一种块。官方文档不是同行评议论文，也不证明 BrewFS 性能优势。 |
| [`tectonic2021`](https://www.usenix.org/conference/fast21/presentation/pan), FAST 2021 | 大规模多租户文件系统兼顾多种负载和效率。官方摘要及书目信息核实。 | 说明生产系统必须处理多样性。不要引用其部署规模作为 BrewFS 的可扩展性证据；也不假定其每种负载均采用单一固定粒度。 |
| [`azureec2012`](https://www.usenix.org/conference/atc12/technical-sessions/presentation/huang), ATC 2012 | Local Reconstruction Codes 调整冗余结构，以降低恢复代价。 | BrewFS 当前没有提出新纠删码。需区分健康读取与降级读取，分别报告修复流量、读放大和容错条件；变小 B/q 不能被表述为提高纠删码理论效率。 |
| [`morph2024`](https://www.pdl.cmu.edu/ftp/Storage/Morph_Final.pdf), SOSP 2024 | 按文件生命周期调整冗余，使用可转换编码与布局降低转换代价。已读摘要、动机与编码背景。 | BrewFS 根据最终上传对象大小选择 B，不等同于按生命周期转码或改变 k/m。若评估节省写流量，必须按真实编码、尾部填充、校验和实际字节归因。 |
| [`okapi2025`](https://www.usenix.org/conference/osdi25/presentation/athlur), OSDI 2025 | 将数据条带化与冗余分组解耦，分别管理并行访问和可靠性；已读设计和读取部分。 | “解耦粒度”不是空白领域。BrewFS 拟分离的是编码块 B 与物理读取/校验粒度 q，层次不同。固定 k/m、故障容忍、压缩、checksum 等条件，再做 B-only、q-only 与 B+q 消融。 |

## 5. Agent 负载来源与质量控制

| 文献及主来源 | 可以支持的内容 | 不能据此推断的内容／使用约束 |
|---|---|---|
| [`swebench2024`](https://proceedings.iclr.cc/paper_files/paper/2024/hash/edac78c3e300629acfe6cbe9ca88fb84-Abstract-Conference.html), ICLR 2024 | 真实 GitHub issue 修复任务及测试式验证框架。 | 原论文不是多 agent 文件系统负载研究，不能证明小文件瓶颈、共享率或读放大。历史任务可作固定 trace，但必须标任务集、镜像、repo commit。 |
| [`sweagent2024`](https://proceedings.nips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html), NeurIPS 2024 | agent 会导航仓库、编辑代码、执行命令和测试。 | 不能证明所有 agent 有相同访问分布，也不能从模型成功率推出 FS 性能。分别采集工具调用、系统调用、对象请求和后端字节。 |
| [`openhands2025`](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a4b6ad6b48850c0c331d1259fc66a69c-Abstract-Conference.html), ICLR 2025 | 开放 agent 平台与可运行软件任务，适合建立可复现执行器。 | 模型 API 等待可能掩盖存储差异。既需固定 trace 重放隔离存储因素，也需少量 live run 验证外部有效性；不能把重放当作完整 agent 智能评估。 |
| [`multi_swebench2025`](https://proceedings.neurips.cc/paper_files/paper/2025/hash/5afa9cb1e917b898ad418216dc726fbd-Abstract-Datasets_and_Benchmarks_Track.html), NeurIPS 2025 | 正式论文覆盖多语言 issue 修复，可补充 Rust/Go/C++ 等编译型负载。 | 正式版本是 2,132 个任务、8 种语言；早期 arXiv v1 是 1,632 / 7。不要混用两版作者、规模或数据清单。应以实际下载 revision 和所选任务 manifest 为准。 |
| [`swebench_pro_v2`](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro), 官方数据集 | 官方 V2 / 2.0.0 发布于 2026-09-22；`default/test` 包含 642 个任务，`hard` 为 51 个任务，原始 `v1` 为 731 个任务。2026-10-22 核实官方 card 和 release commit。 | 用于任务与版本来源，不作新论文或模型能力证据。候选冻结 revision 为 `2d52cb3df914a3fcf80c7f66738b3a88ae37fc50`；实际任务清单、harness commit、image digests 还须在执行前冻结。V2 使用匹配的 `docker_image` 和 verifier，避免沿用 v1 镜像配置；agent 与独立评分阶段隔离。 |
| [`swebench_audit2026`](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/), 官方公告 2026-02-23 | 官方审计指出 SWE-bench Verified 存在测试缺陷和污染问题，限制前沿模型比较的可信度。 | 被审计困难子集不是整个数据集的随机样本；不能把该子集比例外推成所有任务缺陷比例。历史 trace 仍可用于确定性 FS 重放，但不应承担模型能力结论。主扩展可采用固定版本 SWE-bench Pro 和 Multi-SWE-bench，并独立审查测试有效性。 |

SWE-bench Pro V2 的版本候选由[固定发布 commit](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro/commit/2d52cb3df914a3fcf80c7f66738b3a88ae37fc50)支持。这里记录的是建议冻结的公开版本，不是已经完成的数据集下载或实验执行；642 也不是本计划实际采样数量。

## 6. 需要进入实验计划的文献驱动对照

这些是根据上述设计重叠提出的研究判断，不是被引论文对 BrewFS 的结论。

1. **创建工作区：** eager copy 仅作容易理解的参照；必须另含具有共享能力的 OverlayFS、reflink/快照或可运行 BranchFS。分别报告只分配逻辑工作区、挂载就绪、首个访问、首次写和回收时延。全量复制基线不能独占主比较。
2. **只读 lower：** 增加 CVMFS + OverlayFS、Nydus + OverlayFS 中至少一个成熟实现；并增加逻辑内容相同的 SSTable/LSM lower 格式对照，用于隔离“只读”与“自定义布局”的贡献。若不能部署某完整系统，清楚标注限制，不能把简化实现冠以该系统名。
3. **冷元数据：** 同时控制客户端缓存、FUSE/dentry cache、后端 OS page cache；记录请求数、页数、字节数、KV 次数及缓存占用。分别测试单点 lookup、深路径、宽目录 readdir+stat、属性和数据位置联合查询。
4. **后端粒度：** 在相同 k/m 和持久性下，分别启用 B 和 q；记录 client 请求、网络 Range 请求、后端 shard 读取、checksum 验证和实际落盘字节。只测 S3 返回字节不能证明物理读放大下降；只减少 padding 不能自动推出全部写放大下降。
5. **正确性与成本：** 加入 snapshot 发布、crash 后恢复、删除/whiteout、rename、open/unlink、hardlink/symlink（若承诺支持）、upper 增长和垃圾回收。针对 BranchFS 的持久性差异单独规定比较合同。

## 7. 可引用的贡献表达与禁用表达

| 不宜采用 | 更稳妥的草稿表达 |
|---|---|
| “The first filesystem for AI agents.” | “BrewFS targets the storage cost of concurrent agent workspaces that share a read-only baseline.” 随后讨论 AgentFS、BranchFS、YoloFS。 |
| “We introduce delta-based namespaces.” | “We adapt overlay-style namespace composition to shared immutable subtree snapshots and private metadata/data mappings.” 明确引用 OverlayFS 与 DeltaFS。 |
| “Existing systems require a metadata-server lookup for every file.” | “For selected immutable lower subtrees, BrewFS is designed to resolve supported baseline queries directly from snapshot pages.” 必须限定命中范围，排除 upper 查询、发布及权限例外。 |
| “Packing metadata is novel.” | “BrewFS jointly lays out name ranges, common attributes, and data locators, and evaluates the resulting request and memory costs against established catalog and table layouts.” |
| “Variable EC blocks reduce redundancy.” | “BrewFS and RustFS select an EC block size using the final object size, while separately choosing a physical read/verification granularity under the code's constraints.” 不声称改变 k/m。 |
| “Our design improves performance by X.” | 当前初稿只能写 “We plan to evaluate whether …”。所有 X、百分比、显著性和胜率均待真实测量。 |

## 8. 阅读记录、边界与后续检索

已阅读超过摘要的核心设计来源包括 TABLEFS、IndexFS、DeltaFS、CernVM-FS、Ceph、Mantle、Morph、Okapi、SwitchFS、BranchFS、YoloFS；其余阅读范围逐项记录在 registry。这里的“读设计”表示读过相关章节，**不表示复现过论文或独立验证过其性能数字**。

另有一篇必须在投稿前补读的近邻：Wenhao Lv、Hao Guo、Qing Wang、Youyou Lu、Jiwu Shu，*Accelerating Distributed Filesystem Metadata Service via Decoupling Directory Semantics from Metadata Indexing*，SoCC 2025，DOI [10.1145/3772052.3772237](https://doi.org/10.1145/3772052.3772237)，系统名 HMFS。作者[主页](https://storage.cs.tsinghua.edu.cn/~gh)提供了[作者版 PDF](https://raw.githubusercontent.com/kurodes/SoCC25-HMFS/main/Accelerating_Distributed_Filesystem_Metadata_Service_via_Decoupling_Directory_Semantics_from_Metadata_Indexing.pdf)。本次已核实书目信息，但未把未读的机制写入主体论证，也未为凑条目数加入引用。

f4、Stripeless Data Placement for Erasure-Coded In-Memory Storage（Nos, OSDI 2025）等真实工作已经筛选，因本阶段重点是元数据、工作区与粒度边界而未收入主集。Succinct 的压缩查询问题也不能直接替代 POSIX 目录布局证据。正式提交前，应再次以提交日期为界检索 OSDI/SOSP/FAST/EuroSys/ATC/SoCC 的新增文献；当前 2026 近邻不能省略，也不应把本列表称为穷尽性综述。

### 尚未解决的证据缺口

- MesaFS 与 HMFS 的具体结构、适用语义、代码和实验配置还须补读，不能据当前资料断言 BrewFS 与其完全不同。
- BrewFS 的实现是否确实做到页级按需读取、locator 覆盖常用查询、数据映射级修改，以及 RustFS B/q 是否真正进入物理读取路径，需要代码审计。
- Agent 工作负载是否具有高基线共享率、少量修改、目录局部性和小范围读取，需要采样测量；文献仅能说明任务与接口存在。
- “三机制协同”的创新性需要交互消融或反事实对照支持。把三个独立优化并列展示，不能充分证明协同。
