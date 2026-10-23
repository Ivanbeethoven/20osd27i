# BrewFS 工作区原理与生命周期：当前代码证据

审阅日期：2026-10-23。源码固定于 upstream/main `242af5f7e9bba7afc0c61778f1084fcb20e083a0`，只读导出目录为 `../brewfs-principles-242af5f`（相对于论文工程根目录）。已读该导出的 `AGENTS.md`。下列 `src/...:行号` 均相对于此源码根目录。本记录是源码审查，不是新挂载、故障注入或性能测试结果。

PPT 依据：`evidence/ppt-principles/slides.json`，按实际 presentation order 的第 11–16 页及讲稿。沿用 `planning/terminology.zh.md` 的正式术语；PPT 中 tombstone/whiteout 的同义表述在新正文统一为 whiteout / deletion marker。

## 1. 最重要的关系结论

**Delta-based workspaces 的必要条件是确定身份、不可变且受生命周期保护的共享基线，以及独立的 private writable upper；必要条件不是 Packed Metadata。** 共享与不可变属于状态和可见性契约，Packed Metadata 属于基线的表示和访问选择。可变粒度对象存储则属于对象形成与可选后端物理布局选择，不由工作区解析式推导出来。

直接证据是 `workspace-v1` 的真实挂载入口：`src/cli.rs:1949–1963` 先建立 `WorkspaceMetaLayer` 并查询可选的 packed lower binding；只有 `Some(binding)` 才在 `1964–1992` 附加 packed lower。无此绑定仍继续建立普通工作区 VFS（`2022–2034`）。`src/workspace_overlay/meta_layer/packed_lower.rs:230–233` 明确列出 `WorkspaceLower::{Native, PackedV3}`，且注释特别说明此处 Native 指 **native catalog layers**，不是旧 Packed 解码器，也不等于整个 `native_base` 子系统。

`WorkspaceMetaLayer` 默认 lower 是 `WorkspaceLower::Native`（`src/workspace_overlay/meta_layer/mod.rs:251`）；其挂载契约要求一个 sealed base 与一个 writable layer（同文件 `88–105`），不是任意深度叠层。用同一套可见性契约连接两种下层表示，不意味着每个实现、元数据后端或格式版本都可以自由互换。

## 2. 已有入口与实现边界

| 入口／代码路径 | 下层与上层关系 | 审查到的实际限制与证据 |
|---|---|---|
| `FlatV1` 普通卷 | 不构造工作区上层／下层；使用普通元数据库与对象数据路径 | `VolumeFormat` 的默认值为 FlatV1（`src/config.rs:311–325`）；`src/cli.rs:877–880` 直接 `create_meta_store` 后 `mount_with_store`。因此工作区能力不是每个卷的必经阶段。 |
| `WorkspaceV1`，无 packed binding | 可写私有目录、inode、extent 等记录叠加固定 sealed catalog base | `src/cli.rs:1949–1992` 的条件分支；`src/workspace_overlay/model.rs:21–24` 用 layer ID、sealed version、root hash 定义 `BaseRevision`；不是必须由对象中的 packed manifest 定义。 |
| `WorkspaceV1`，有 packed-v3 binding | 同一私有工作区机制，通过 adapter 从认证后的 packed snapshot 获取基线数据 | `src/cli.rs:1964–1966` 同时检查 catalog 是否具备完整 permission/ID/lifecycle 能力；`1968–1990` 分 LocalFs/S3 attach。不能把“存在 trait/格式”写成任意后端均可挂载。 |
| `WorkspaceNativeV2` 的 Native P1 | KV workspace namespace + Native data runtime；其基线读取来自 workspace-v1 view | `src/cli.rs:1267–1287` 要求 workspace-v1 schema-1，并显式拒绝将 mutable P1 KV mount 作为 frozen-metadata volume 的回退；`1324–1364` 组合 WorkspaceMetaLayer、WriteOverlay、WorkspaceBaseDataSource 与 NativeDataRuntime。 |
| `WorkspaceEntityV1` | 当前态实体上层，通过 `ImmutableLower` 接口解析一个已认证的固定下层 | trait 见 `src/workspace_overlay/entity/resolver.rs:22–53`。当前 CLI 是独立的 fresh-only 实验路径，并具体接 Redis/S3 + packed manifest：`src/cli/entity_mount.rs:1–2,35–69`；`src/workspace_overlay/entity/experiment.rs:37` 的 ExperimentalLower 明确是 PackedLower。 |
| 独立 `PackedMetadataV3` | 独立只读挂载，无需为了读取 Packed 而先建立可写工作区 | `src/cli.rs:413–418,433–438` 与工作区／Native 独立分派；`833–858` 接纳 V3，显式拒绝 V1/V2 当前挂载。旧组件存在不等于旧格式当前入口可用。 |

工作区 catalog 后端也有明确入口限制：`src/cli.rs:1804–1855` 为 workspace-v1 选择 SQLite（SQLx 必须 SQLite URL）、Redis、TiKV，拒绝 etcd。是否可挂 packed lower 仍额外受 `supports_packed_workspace_mount` 检查；不能因 SQLite 可挂普通工作区而推断其可挂全部 Packed 组合。

Entity 的接口可替换性与当前入口必须分开描述。`ImmutableLower` 要求稳定 binding、inode/dentry/xattr/chunk/readdir；`ImmutableLowerData` 要求返回精确的已认证字节或错误（`entity/resolver.rs:22–53`）。接口允许原则上编写其他满足契约的实现，但当前实际实验 wiring 使用 PackedLower；测试中的 MemoryLower 也不是生产可用的另一种挂载格式。`LowerBinding` 自身仍有 manifest key/digest 与 inode 边界（`entity/model.rs:18–23`），因此不可声称任意“未认证只读目录”可直接接入。

## 3. 工作区到底复用了什么

### 创建与修改

共享的是已封存的 namespace、属性、数据位置映射与其引用的内容；上层保存私有的新状态，而不是先复制整个基线目录树。PPT 第 14 页正好表达此原则，其“仅记录差异”不能解释成仅记录修改字段或字节差分编码。

- `WorkspaceLifecycle::fork_revision` 为每个子工作区分配独立 workspace/head ID 并引用同一 BaseRevision（`src/workspace_overlay/lifecycle/mod.rs:63–80`）。
- 当前 KV fork 实现验证固定 sealed base，创建 WorkspaceRecord 与 writable head，并写有限的控制记录；Packed 情况增加绑定/引用管理，非复制完整 dentry/inode 树：`src/workspace_overlay/stores/kv_store/packed_journal/registry/borrowed_alias.rs:351–403`。其中 `362–365` 要求 flat sealed base。
- 旧工作区表示有 `DentryDelta`（`model.rs:266–273`）、完整字段的 `InodeDelta`（`325–343`）、带 Data/Hole 的 `DataExtentDelta`（`366–399`）。因此“delta”是工作区状态相对于基线的私有增量，不意味着每行只含变化字段。
- Entity 表示刻意移除了 layer/shared head/mutation sequence/writable-layer digest（`src/workspace_overlay/entity/model.rs:1–4`），保存 current entity state。它是这一原理的另一种具体实现，不应替代整章对工作区原理的定义。

### 上层优先与删除屏蔽

`src/workspace_overlay/resolver/dentry.rs:32–47` 把 whiteout 解析为 Masked、Put 解析为 Present；`59–77` 从当前层向基线查找赢家。`resolver/mod.rs:18–24` 把 Present、Masked、Absent 分开：只有 Absent 可以向可选下层回退，Masked 是视图中的终止删除。目录枚举保留 masks 以避免下层名字复活（`resolver/dentry.rs:91–123`）。这层规则适用于 catalog 基线与 Packed adapter；Packed 不改变删除含义。

### 显式数据映射是 Entity 的例证

Entity 的 `ChunkSource::{Data,LowerRange,Hole}` 与完整规范化 `ChunkMap` 见 `src/workspace_overlay/entity/model.rs:75–101`；`lower_visible_size` 是仅减不增的继承边界（`51–54`）。它清楚地实现“修改区间私有、其余区间继承、空洞读零”，但不能写成其他工作区路径恰好也使用同一个 enum。`entity/data.rs:429–451` 先 durable create-only PUT，再产生可供后续发布使用的 receipt；应与普通 VFS 的可选写回模式分开。

## 4. Dirty overlay 与 workspace delta 不同

PPT 第 13 页的 [2,10) KiB 示例是 **本客户端的数据读写一致性**：新写入 [4,8) KiB 尚未完成写回时，读结果由旧已提交范围与本地脏范围拼接。workspace delta 则是 **持久的私有工作区视图组成**，覆盖名字、属性、删除、文件数据映射。两者可能在同一路径组合，不能将二者都称作“私有 diff”并认为生命周期相同。

当前普通 VFS 源码证据：

- 完整被本地脏数据覆盖时直接返回 dirty data：`src/vfs/fs/mod.rs:4970–4989`。
- 不为每次读取做全文件 flush；对于已发布但未完成上传的重叠范围，等待必要上传：`4992–5007`，具体等待循环见 `src/vfs/io/writer.rs:3749–3766`。
- 读取已提交数据后应用先前快照与当前 dirty patches：`src/vfs/fs/mod.rs:5010–5045`。局部拼接仍有复制，不能从“overlay”推出零拷贝。
- `UploadBeforeCommit` 是默认；`CommitBeforeUpload` 需明确选择，并存在元数据已可见而对象未上传的窗口：`src/vfs/cache/config.rs:27–38`，默认字段另见 `122`。本地可读、元数据可见、远端持久化是不同状态。

这一 dirty overlay 位于普通 VFS 路径，不能据此将工作区视图原理限定为 buffered VFS，也不能把 Entity 的 durable-then-map 路径写成拥有同样的 dirty-buffer 行为。

## 5. Worker 接力需要的协议，与已经存在的组件

PPT 第 11 页把文件恢复点与运行中的进程/内存会话/打开文件句柄分开；第 16 页给出接力方案：应用显式检查点 → 暂停源端新写 → 排空并验证必要对象 → 原子发布恢复版本 → 隔离旧写者并给目标写入资格 → 目标校验版本、重新打开工具并继续。崩溃后的恢复点是最后确认发布的文件状态，不能承诺未提交内存状态随文件系统自动迁移。

源代码中有支撑这些步骤的组件，但不能将库组件或某条恢复命令等同于任意 Worker 的完整自动迁移：

1. **封存边界与持久日志**：`src/native_base/lifecycle/seal.rs:24–59` 列出 LocalFreezing、Quiesced、DataDrained、CandidateVerified、RetentionPrepared、PublishedRetained 等阶段与恢复动作；`166–250` 在 expected head/view/generation guard 下将 workspace 切至 Freezing 并写 journal。
2. **远端验证**：`seal.rs:63–67` 区分 ExactReadback 与强服务 receipt；`717–759` 不允许含新远端写入的候选用 NoopTestBarrier 充当验证，并只从 DataDrained 推进 CandidateVerified。此 API 的存在不替代对实际上传/验证 driver 的运行测试。
3. **原子发布与引用保留**：`src/native_base/lifecycle/publish.rs:299–305` 绑定 KV base 与 manifest namespace；`377–409` 检查 matching journal、head、view 和写者 generation；`433–438,542–561` 在同一事务中发布 PublishedRevision、替换 head/view 并记录 journal 结果。`525–534` 清零 visible delta，但保留私有 open orphan 状态，不把未命名打开文件自动纳入公开快照。
4. **引用式 fork**：`src/native_base/lifecycle/fork.rs:96–112` 要求精确匹配、同卷、永久保留的 PublishedRevision；`123–159` 建立 base 引用、独立 head/domain 和 `visible_delta_count: 0`；`170–190` 原子写控制记录。此函数不遍历文件树，但不能据此宣称完整 mount/readiness 的测量时延为常数或零。
5. **旧写者隔离**：`src/native_base/write/lease.rs:189–230` 使用后端时钟及 generation 判断租约，过期/被取代租约无法取得 guard；`write/commit.rs:1–24` 和 `347–357,405–407` 的提交路径再次校验 head/generation/domain 并原子提交。普通 workspace mount 在获取租约后重新验证 head 与 base（`src/workspace_overlay/lifecycle/mod.rs:145–178`），续约失败撤销本地 validity（`309–315`）。
6. **仍要区分入口**：本次检索 `src` 中 `fork_from_published(`、`publish_candidate(`、Native `begin_seal(` 的调用，目前只发现函数定义及 native lifecycle 单元测试，未发现普通 CLI 挂载调用这些 Native lifecycle 函数。因此这些是已实现库协议，不能写成已贯通的跨 Worker 发布/挂载路径。
7. **最新 Packed 恢复并非全空白**：`src/cli/packed_mount_recovery.rs:1–2` 已标明 production **same-PVC packed-v3 recovery**；`43–49` 校验新的 generation/lease/pod identity 与原挂载配置；`85` 限 Redis/TiKV；`150–177` 以原 mount reference 和 scoped metadata/PVC driver 恢复。它是有条件的现存恢复入口，不是任意工作区跨机器自动接力，更不是 Entity fresh-only 接管能力。

### Native P1 还提供了直接反例

`src/native_base/lifecycle/manifest.rs:18–35` 定义 `KvNamespace { layer_id, sealed_version }`，并注明 P2 Frozen namespace 不在 P1 格式内；`81–83` 编码 KV namespace mode。因此，即使存在不可变 manifest、Data Seal、对象 inventory 和发布版本，也不能把它们统称为本文 Packed Metadata 机制已经启用。持久化版本的 manifest 是通用生命周期结构，和目录联合组织的 Packed Metadata 是不同概念。

## 6. 对 04-delta 原理重写的建议

推荐先写可组合的状态原理，再写具体实现证据：

1. 开头以 `W_i = Resolve(S, Δ_i)` 定义 shared immutable lower 与 private writable upper，并明确 `S` 可以由固定 KV catalog 或 packed snapshot 承载；工作区不要求后者，也不要求可变对象布局。
2. 解释引用式创建、上层优先、whiteout、名字/属性/数据映射分别私有以及与 inode 身份保持的关系。
3. 给一个短区间覆盖例子，使用 Entity Data/LowerRange/Hole 作为具体表示，注明另一路径用 catalog delta/extents；不要把 Entity 作为整套工作区能力的唯一模型。
4. 用一个短段落区分 dirty overlay 的本客户端读己之写与 workspace delta 的持久视图分离。
5. 生命周期写为“基线固定—私有修改—有条件封存/发布—引用式 fork 或恢复”，并明确发布/写入资格/保留协议与布局格式分别选择。最后列真实入口边界，避免“只要不可变快照便支持完整接力”。
6. 元数据共享的逻辑空间核算可保留，但只说明基线计一次和私有记录增长，不新增测量收益或声称 fork 整体零成本。

结论不是“八种组合已经全部能挂载”。可组合性是三个机制所解决问题与接口边界的区别；可运行配置必须逐条由入口、后端能力、持久化与恢复协议共同证明。

## 7. 已完成的章节重写

按 `planning/03-mechanism-relationships.zh.md` 重写 `paper/sections/04-delta.tex`，约 810 个空白分隔词项（含 LaTeX 数学记号），三小节分别为共享基线与私有状态、修改数据与本地 dirty reads、发布与生命周期。保留名称解析和逻辑元数据核算公式；不增加性能测量或已验证的接力保证。

主要论点与证据映射：

| 论点 | 证据 | 状态 |
|---|---|---|
| Workspace 可使用固定 catalog lower 或 Packed lower | 本记录第 1–2 节，CLI 条件 attach 与 WorkspaceLower 枚举 | 当前代码支持；不推广全部组合 |
| 创建保留基线引用并分配私有状态 | fork_revision、KV create workspace、Native fork 的控制记录构造 | 结构性证据；无时延结论 |
| 上层 present/whiteout/absent 决定名字可见性 | dentry resolver 与 Resolution 枚举 | 当前代码支持 |
| Data/LowerRange/Hole 与 lower-visible size | Entity model/resolver/data | Entity 的具体表示；不推广所有实现 |
| dirty overlay 是本客户端未完成写回的数据覆盖 | VFS read 与 Writer 范围等待 | 当前代码支持；局部可读不等于发布 |
| Worker handoff 要求检查点、停写、持久化、发布、写者隔离 | PPT 11/16、Native seal/publish/lease/commit | 协议原理和现存组件；完整接力未在本次验证 |

没有改动论文其他章节、图表或源码；只进行静态术语、论点边界和 `git diff --check` 校验，统一编译由主代理执行。
