# 打包式元数据：PPT 与当前代码的原理核验

核验日期：2026-10-23。源码快照：`../brewfs-principles-242af5f`；来源版本由本轮下载记录固定为 `242af5f7e9bba7afc0c61778f1084fcb20e083a0`。该目录是无 `.git` 的源码快照。本次读取了根 `AGENTS.md`，并沿构造函数、挂载分派、查找和发布调用核验；未运行挂载、性能或故障试验。以下路径均相对此源码根。PPT 来源与 SHA-256 见 `evidence/ppt-principles/slides.json`，页码按原始文件顺序。

## 1. 可直接用于论文的结论

**共享不可变下层是工作区的语义角色，打包式元数据是这个角色的一种存储与访问实现。** 两者没有必然依赖：当前 `WorkspaceMetaLayer` 默认使用原生目录记录层，可按已持久化绑定接入 `PackedV3`；打包式不可变快照也有不带私有可写上层的独立只读挂载。因此可分别讨论增量工作区、打包式元数据，以及它们的组合。这里的可选性是不同可构造路径与接口边界，不意味着任意运行中的挂载可以无条件热切换，也不证明全部因子组合已经完成实验。

**PPT 第15页讲的是 clustered frozen metadata v2 的 tree+batch 路径；当前 `packed_v3` 是独立格式及读取器。** 共同原理是将稳定状态封存后，以认证索引定位有界记录集合，按需获取、验证、解码和复用。不能把 v2 的按类型批次、两级示意图、对象格式或入口状态直接称为当前 PM11/IP06/GroupMeta 实现。当前 CLI 明确拒绝 `packed-metadata-v1` 和 `packed-metadata-v2`，接受 `packed-metadata-v3`。

**下层查询独立性替代的是支持查询所需的逐文件下层元数据库访问，不是删除整个系统的 KV 服务。** 独立只读读取器由对象客户端、认证快照、索引读取器和缓存构造；工作区组合仍使用控制目录、私有上层、持久化绑定、租约和 reader pins。

## 2. 入口与组合关系：实际调用证据

| 路径／角色 | 当前代码调用与行号 | 能确认的边界 |
|---|---|---|
| 普通可写工作区，不选择打包式元数据 | `workspace_overlay/meta_layer/mod.rs:251` 默认 `lower: WorkspaceLower::Native`；`meta_layer/packed_lower.rs:230–234` 定义 `Native` / `PackedV3` | `Native` 的注释明确指原生 catalog layers，**不是** `native_base` 模块或旧 packed decoder。增量工作区不以 Packed 为前提。 |
| workspace-v1 按需组合 Packed | `cli.rs:883` 调用 `mount_workspace_with_store`；`1949–1991` 创建 `WorkspaceMetaLayer`、读取 `load_packed_lower_binding`，仅 `Some(binding)` 时调用 `attach_workspace_packed_lower` | 无绑定走已有下层，有绑定才选择 Packed；若缺完整目录权限／ID／生命周期能力，`1965–1966` 拒绝挂载。 |
| 组合所需的认证与寿命约束 | `cli.rs:2233–2316`：打开 packed reader session → 固定绑定 authority → 校验当前绑定 → `AuthenticatedV3Snapshot::open` → `PackedV3ReadonlyMeta::from_v3_budget` → `with_packed_v3_lower` | 构造器本身不代替发布；`meta_layer/mod.rs:414–442` 明确绑定持久化／发布须另行完成，生产入口从 store 读取绑定。 |
| Packed 独立只读挂载 | `cli.rs:417–418,437–438` 从 LocalFS/S3 分派；`1013–1091` 读取 manifest；`963–1009` 认证并创建 `PackedV3ReadonlyMeta`、其 block store 和 VFS | 没有在这里创建私有可写上层。证明 Packed 可单独服务只读文件系统。只读错误由 `packed_v3/readonly.rs:1011–1014` 返回 `EROFS`。 |
| 独立挂载当前门槛 | `cli.rs:931–936` 拒绝非零 payload memory/SSD cache 或预取；`1057–1076` 只接受 wire005，并要求用户选定的 content-addressed SHA-256 manifest key | 不能把元数据缓存与 payload 缓存混为同一个开关；不能声称 CLI 自动兼容 v1/v2 或 wire004。 |
| Entity 组合路径 | `cli/entity_mount.rs:50–69` 经 `RedisEntityExperiment::create_fresh_from_manifest` 创建；`entity/packed_lower.rs:451–452,629–632` 为 `PackedLower` 实现 `ImmutableLower` / `ImmutableLowerData`；接口位于 `entity/resolver.rs:22,47` | 是另一个组合适配器，不是整个 Packed 机制。当前 CLI 仍要求实验性 fresh namespace；`cli.rs:862–866` 明确生产准入及进程崩溃接管禁用。 |
| 原生 KV 与 Packed 的布局对照入口 | `cli.rs:912–917` 的 `BREWFS_PACKED_METADATA_ARM` 接受 `packed` / `native-tikv`；`1095–1146` 连接 `NativePlacementRepository`，导入或打开 `NativePackedPlacementProvider` | 这里的 `native-tikv` 是同一 pinned packed manifest 的只读元数据放置对照，不等于 Native Base。`1127–1128` 将导入构建与实际挂载分开。 |
| Native Base 另一路径 | `native_base/frozen/readonly.rs:60–74` 提供只含 `FrozenCatalog` 的只读 facade；`native_base/frozen/mod.rs:309–356` 区分 KV namespace refs 与 frozen namespace root | 库级别确实有另一套冻结元数据结构。当前 `workspace-native-v2` CLI 的 `cli.rs:1245–1287` 是 mutable P1 KV 入口，遇 `FROZEN_METADATA_FEATURE` 明确失败，不能将库组件存在写成该 CLI 已支持 frozen 挂载。 |

`WorkspaceStore` 默认 `load_packed_lower_binding` 返回 `None`、packed 挂载 capability 为 false（`workspace_overlay/catalog.rs:511–523`）；共享 KV 实现要求 consistent reads 和 reader-pin budget（`stores/kv_store.rs:2161–2163`）。这是明确的能力选择，不是“只要存在文件就自动走 Packed”。

## 3. 三种格式不能混写

| 实现 | 数据组织与索引 | 代码证据 | 与 PPT 的关系 |
|---|---|---|---|
| `clustered_snapshot` v2 | Namespace / Extent / Attribute / DirectoryProjection 等类型批次；`BatchLocator` 记录包偏移、存储／原始长度与摘要；多级 Merkle 索引定位批次 | `clustered_snapshot/mod.rs:1–7`；`batch.rs:21–36`；`cluster_format.rs:13–17,87–99`；`index_builder.rs:46–88` | PPT 第15页讲稿明确点名 v2 tree+batch，并引用同名 builder/format 源文件。图的“两级”只是示意；代码按容量逐层构建到单个根，不固定两级。 |
| Native Base frozen metadata | `SnapshotManifest` 的 `namespace_mode=1` 为 KV layer+sealed version，`2` 为 frozen root；独立 namespace/data/inventory roots，BNPG 页索引 | `native_base/frozen/mod.rs:309–356`；`native_base/frozen/catalog.rs:63–101`；`native_base/frozen/readonly.rs:1–5,60–74` | PPT 第12、14、16页所引用的 Native Base 生命周期与共享基线原理，与 v2 记录封存相邻，但不是 PM11/GroupMeta 同义词。 |
| 当前 `packed_v3` wire005 | PM11 manifest，IP06 认证分页索引，按父目录与名称范围定位逻辑读取组；GroupMeta 联合目录项、常用属性与数据定位，可选内联数据；容器及 Packed 数据帧另有定位／认证信息 | `packed_v3/mod.rs:1–5`；`wire005.rs:1,91–104,129–143`；`wire005/manifest.rs:75–134`；`wire005/index.rs:1,164,203`；`meta.rs:1–8,37–70` | 可用来具体实现和展开“稳定记录封存＋索引按需读”的原理，但必须说明当前选用的是新的访问组织，不能沿用旧格式字段和挂载能力。 |

v2 的 `.brfc` reader 只读取固定 superblock，随后按需读取独立认证的 index page 和 batch，并有有界缓存（`clustered_snapshot/remote.rs:1–7,99–110`）。这支持 PPT 的解释，不支持将其直接写成当前实际选择的 v3 入口。CLI 对 v1/v2 的拒绝见 `cli.rs:849–858,896–906`。

## 4. 当前 Packed v3 的职责与一次查询

1. **Manifest 固定身份和入口。** `V3SnapshotManifest` 保存 snapshot/root identity、build provenance 和多个认证根；`AuthenticatedV3Snapshot` 只由认证通过的 manifest 创建，读取代际来自 manifest 内容身份（`wire005/manifest.rs:110–128`）。具体编码为 PM11（`130–134`），文件首行仍留有 PM10 旧注释，判定格式必须以实际编码／解码检查为准。
2. **Index 负责路由，不能画成 POSIX 目录树的复制。** Groups、Inodes、Containers、Frames、ColdAttributes、ReverseNames、LargePlacements 是不同索引根（`manifest.rs:75–107`）。目录查找将 `parent_dir_key || raw_name` 作为索引键，校验落入目标组的父目录与名称边界（`591–612`）。inode 直接查询采用独立 Inodes 根（`628–645`），因此不是所有 `getattr` 都先走目录组。
3. **逻辑读取组不是物理对象。** `V3GroupRef` 包含 `container_ordinal`、父目录、首尾名称、元数据偏移／长度／编码／摘要、帧区间（`wire005/container.rs:17–30`）；`V3BuiltContainer` 包含多个组，builder 参数为组数组（`252–288`）。可以把若干组装进容器，不能据一个组推导一次整对象 GET。
4. **GroupMeta 是联合信息页。** 记录包括名称、inode、类型、常用 POSIX 属性、大小、数据定位 extents 或内联内容（`meta.rs:49–70`）。其有界原始页面上限为 256 KiB（`26`）；这是格式／实现约束，不是实验测得的最佳值。
5. **一次 `lookup(parent,name)`。** `PackedV3ReadonlyMeta::lookup_entry` 调到认证快照（`readonly.rs:976–986`）；后者先找到逻辑组，再由容器索引解析对象，按 `meta_offset/meta_stored_len` 读取 GroupMeta（`manifest.rs:716–731`）。读取器先验证存储字节摘要，再解压／解码，再验证名称边界、条目数及帧所属组（`container.rs:131–218`）。返回条目即可携带常用属性和数据定位，减少另一次按 inode 回访下层 KV 的需求；实际 GET 数仍随索引层数和缓存而变。
6. **数据读取沿定位信息执行。** 帧定位解析容器与 frame directory，再调用帧读取器（`manifest.rs:1568–1593`）。这是快照数据访问和完整性单位；对象后端自己的纠删码块 B 与物理校验／读取粒度 q 是另一层，Packed 帧大小不直接决定实际磁盘读取量。
7. **不可变性让复用可安全绑定身份。** `readonly.rs:615–631` 的属性与 dentry memo 绑定不可变快照；`wire005/index.rs:697–703` 的索引页缓存按摘要、kind、object_len 标识。无缓存时按实际后端路径读取（`692–695`），不能用暖缓存成功来证明下层查询独立性。

## 5. 构建、验证、可见性是不同时间边界

**源视图确定 → 组织并上传对象 → 校验依赖闭包与 manifest → 发布绑定／版本。** 这四步应在论文原理中分开。

- 捕获源状态不天然等于原子快照。`source_namespace.rs:1–6,31–41` 区分 `BestEffortDetected` 和 `SnapshotBacked`；前者是变化检测策略。实际 build 在 finish 前复核源状态，finish 后获取最终 source-view/fence 摘要（`912–926`）。不能把“最终生成 immutable 输出”倒推为“输入期间原子冻结”。
- Producer 给对象计算内容摘要及地址，执行 create-only PUT，然后分段读回比较（`producer.rs:450–498`）。`finish` 检查 inode/source/placement closure，建各索引根，最后写入并认证 manifest（`1003–1090`）。返回 `V3ObjectRef` 不会自动更新 workspace head；文件开头和 source builder 均明确该边界。
- `VerifiedPackedLower` 只证明认证 PM11/IP06 的 inode namespace 边界，**不**证明上传依赖闭包或源视图一致性（`publish/binding.rs:19–31`）。同名“verified”不能被扩大为完整持久发布保证。
- 当前工作区有持久化绑定和版本发布接口。`catalog.rs:525–545` 明确初始绑定与完整发布／pins／mutation capability 是不同门槛；版本替换针对准确 head/base/binding generation 原子发布。`stores/kv_store.rs:2536–2645` 的初始安装核验 guard、registry、allocator，再经 topology packet CAS 提交，失去竞争不会把旧请求套到新一代。
- 当前 v3 journal 提交要求 `Verified` phase 与匹配的 `CompletePackedGraphSeal`，将 phase 转为 `Committed` 并与 history/root 变更一起提交（`stores/kv_store/packed_journal.rs:2054–2094`）。这是代码中的协议结构，不是本次完成跨机故障试验的证据。
- PPT 第16页的“必要对象完成后发布，再转移写者资格”与上述时间边界一致；其实际引证是 Native Base `publish_candidate`。该实现要求精确注册为 `Verified` 的对象（`native_base/lifecycle/publish.rs:130–156`），并在同一控制事务更新 published revision、head、workspace view、publication journal（`523–562`）。clustered v2 另有完整 manifest 图验证后 head CAS（`clustered_snapshot/publication.rs:415–458`）。三套发布代码不能拼成一个假定已完成的统一跨 Worker 恢复路径。

## 6. 重写第五节时应保留的边界

- 先写“可选的不可变元数据访问表示”，说明可以独立只读挂载，也可给增量工作区提供下层；不要以“创建工作区必然构建 Packed”为起点。
- 共享基线解决重复状态表示；Packed 解决稳定基线的访问组织。二者可以组合，但不是同一个功能；对象布局接口也不是 Packed 格式的前提。
- 明确论文所选当前具体格式是 PM11/IP06/GroupMeta；PPT tree+batch 保留为原理来源和演进背景，不声称两者格式兼容。
- 写出查询所需信息如何从 manifest/index/GroupMeta/locator 到达，不把元数据格式简化成一个“包”，也不把查询独立性扩大成整个系统零 KV。
- 维护成本包括构建、认证、发布、重建与回收；减少在线逐文件查询的目标可能转移为索引请求、过取、解码和缓存代价。没有本次实测收益或加速数字。
- 当前入口的限制作实验证据边界，不取代设计原理；尤其不能沿用早期“只有 Entity 组合路径”的结论，也不能因为 frozen Native Base 库存在就宣称其 CLI 已接通。
