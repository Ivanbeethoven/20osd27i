# BrewFS 论文统一术语表

确认日期：2026-10-23。以下名称已经作者在本轮对话中确认，适用于当前论文正文、图表及中文研究文档。按作者本轮补充，三项机制均为可选、可组合能力；对象粒度定义补入 PPT 所指的客户端 Block 大小 g，B/q 保持原义。后续写作沿用此表；历史审计记录、外部文献名称和源码标识保留原样。

## 核心机制

| 规范英文 | 规范中文 | 定义与使用边界 |
|---|---|---|
| Delta-Based Multi-Agent Workspaces | 基于增量状态的多智能体工作区 | 简称 delta-based workspaces／增量工作区。可选的视图构成机制，将固定共享基线与私有增量状态组合；Delta 包括被修改实体的当前状态和显式数据映射，不要求字段级或字节级差分编码，也不要求基线采用 Packed 格式。 |
| Packed Metadata | 打包式元数据 | 可选的不可变元数据组织与读取机制；按目录和名称区间联合组织目录项、常用属性及数据定位信息，并通过分页索引访问。范围涵盖所选只读子树的完整元数据与访问结构，可独立只读使用，也可用作工作区下层。 |
| packed immutable snapshot | 打包式不可变快照 | Packed Metadata 机制的产物；定义后可简称 packed snapshot。机制名与产物名按各自含义使用。 |
| Variable-Granularity Object Storage | 可变粒度对象存储 | 可选的数据路径策略：选择客户端块大小 g 以控制对象形成，并可在最终上传对象长度 L_o 已知后向兼容后端请求 B，由后端验证和持久化有效 B 及适用的 q。普通 flat 卷可独立使用；当前 g 为固定配置，尚无 PPT 所讨论的在线动态选档控制器。 |

## 工作区与元数据

| 规范英文／符号 | 规范中文 | 定义与使用边界 |
|---|---|---|
| workspace / workspace view, W_i | 工作区／工作区视图 | W_i = Resolve(S, Δ_i)。同一工作区的修改不改变共享基线或其他工作区的私有状态。 |
| shared immutable lower, S | 共享不可变下层 | 供工作区复用的只读基线；强调权限时可称共享只读下层。 |
| pinned snapshot | 固定绑定的快照 | 绑定明确的快照身份，不在每次读取时追随可变的 latest。 |
| private writable upper, Δ_i | 私有可写上层 | 保存私有名称、当前属性、删除记录和数据映射；新增数据字节另存。定义后可简称 private upper／私有上层。 |
| whiteout / deletion marker | 删除标记 | 显式屏蔽继承名称；与上层没有记录的状态区分。whiteout 与 deletion marker 是解释性对应，避免另引 tombstone 作为本文同一机制的新称呼。 |
| Data | 上层数据区间 | 显式映射中引用新增上层数据的区间；保留源码类型名及大小写。 |
| LowerRange | 下层引用区间 | 显式映射中引用固定快照数据的区间；保留源码类型名及大小写。 |
| Hole | 空洞 | 显式映射中读取为零的区间；保留源码类型名及大小写。 |
| logical read group | 逻辑读取组 | 按父目录和原始名称区间组织；逻辑组不等同于物理对象。源码标识 ReadGroup 原样保留。 |
| GroupMeta page | 组元数据页 | 组织目录项、常用属性及数据定位信息的页面。只有明确指同一页面类型时才将泛称 metadata page 统一为 GroupMeta page。 |
| lower-query independence | 下层查询独立性 | 支持的下层查询从快照取得所需信息，不依赖逐文件元数据库记录；私有上层和控制操作仍可能使用元数据库。 |
| Entity path | Entity 实现路径 | 实验性的工作区实现路径，保留 Entity，不编造缩写全称，不等同于整个 BrewFS。 |
| dirty overlay | 脏数据覆盖 | 本客户端读取时，以尚未完成写回的新字节覆盖已提交内容；与工作区私有增量状态不同，本地可读不等于远端持久化。 |

## 对象布局与读取

| 规范英文／符号 | 规范中文 | 定义与使用边界 |
|---|---|---|
| client block size, g | 客户端块大小／对象形成粒度 | 普通数据路径中由 ChunkLayout.block_size 定义的 Slice 数据分块大小，默认 4 MiB；属于固定配置，不等于每个对象的最终长度。PPT 的 1/4/8/16 MiB 为研究档位，不表示现有在线动态选档。 |
| finalized upload length, L_o | 最终上传对象长度 | 经过适用的压缩、头部和成帧处理后的最终对象长度；受尾段和对象形成路径影响，不等同于 g。 |
| erasure-coding block size, B | 纠删码编码块大小 | 后端实际采用并持久化的编码块大小；首次完整定义后可简称 encoding block size／编码块大小。 |
| physical verification/read quantum, q | 物理校验／读取粒度 | 后端分片内校验和读取的粒度，满足适用的 q \| s、qd \| B 编码几何约束。定义后可用 q 指代。 |
| layout hint | 布局提示 | 本文接口具体提供编码块大小提示（encoding-block-size hint），主要请求 B；q 由后端受约束地选择。提示不等同于实际生效布局。 |
| automatic hint policy | 自动提示策略 | 当前为简单阈值规则：L_o ≤ 1 MiB 时省略提示，L_o > 1 MiB 时请求 1 MiB 的 B；不称自适应优化。 |
| packed frame | Packed 数据帧 | 快照格式中的数据访问和完整性验证单位，与后端物理校验／读取粒度 q 分属不同层。 |
| range read / whole-object fetch | 范围读取／整对象获取 | 客户端取数方式；范围请求长度不直接等于物理读取量。HTTP Range 头及 API 名称保留原大小写。 |

## 编辑规则

- 英文机制名在标题中采用 Title Case，在正文中按语法使用小写；句首大写不构成术语变体。
- 不把文件长度、应用／FUSE 请求大小、逻辑 Chunk、客户端块 g、对象长度 L_o、编码块 B、后端粒度 q 或 Packed 数据帧统称为同一种“块大小”。
- 可选性描述架构职责与配置选择；不能据此声称当前任意入口都支持全部组合。省略对象粒度优化时仍使用固定客户端块大小和后端默认布局。
- 保留 BrewFS、RustFS、Entity、GroupMeta、PM11、IP06 等系统名、类型名和格式标识；不擅自展开成全称。
- 讨论外部系统时保留该系统自己的术语；一般意义的 delta（例如两个代码版本的差异）不强行替换成工作区增量状态。
- 术语统一不改变公式、参数、观测数据、实现状态或计划实验的证据边界。

原文依据：`sections/03-overview.tex`、`sections/04-delta.tex`、`sections/05-packed.tex`、`sections/06-layout.tex`；正式论文入口为仓库根目录的 `main.tex`。关系框架见 [03-mechanism-relationships.zh.md](03-mechanism-relationships.zh.md)，当前代码证据见 [工作区](../evidence/principles-code/workspaces.md)、[Packed](../evidence/principles-code/packed.md) 和 [对象粒度](../evidence/principles-code/objects.md)。
