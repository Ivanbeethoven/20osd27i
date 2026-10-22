# BrewFS / RustFS：论文实现证据与主张边界

审阅日期：2026-10-22。BrewFS 固定提交 `518e7cc39b2ff0b421ecf0f656de6d468cacb9b8`；RustFS 研究分支固定提交 `cc4926fac1107aee76540f28bf22dbd47fcbca24`。本次工作是静态源码与设计契约核验，没有运行挂载、性能或故障实验。文中“已实现”仅表示在固定提交中找到对应代码和入口，不表示本轮重新验证了行为或性能。

## 1. 核验范围与证据优先级

BrewFS 使用上一轮工作保留的完整本地检出，并在本次独立目录复制后审阅。`git rev-parse HEAD` 为上述提交，提交时间为 2026-10-21 21:19:48 +08:00。受版本控制文件共 1,479 个。禁用 LFS 工作树过滤后的状态只有预置 xfstests 的二进制归档显示工作树差异；本文引用的 Rust、Markdown 和配置文件没有发现工作树变更。本次没有声称逐行读完全部文件，而是核验三项机制及关键运行入口、限制与实验资料。

RustFS 的关键文件通过 GitHub connector 按固定提交在线读取：`ec_block_layout.rs`、`constants/object.rs`、`set_disk/ops/object.rs`、`multipart.rs`、`set_disk/read.rs`、`core/io_primitives.rs`、`ops/heal.rs`、`erasure/coding/erasure.rs` 和 `config/storageclass.rs`。完整布局选择文件另存为 `rustfs_ec_block_layout_verified.rs`；其余文件仅保存核验所需的摘录与来源记录。

发生冲突时，证据优先级为：当前固定提交的实际入口和数据路径 → 当前 scope/precedence 契约 → 对应日期的实现 checkpoint → 历史设计段落。`packed-meta.md` 合并了历史 v1/v2/v3 设计，部分段落的“当前”仅指当时 checkpoint，不能直接移作现在的实现状态。

### 建议在论文内部使用的三种状态

| 标签 | 含义 | 合理措辞 |
|---|---|---|
| **I: implemented path** | 存在可选运行入口和相应实现；本文尚未重新执行验证 | “The prototype implements …”; 同时写明入口、版本和适用条件 |
| **P: experimental / gated prototype** | 已有实现，但限实验、特定模式、未完成组合资格或默认关闭 | “The experimental path supports … under …”; 不将其写成默认生产能力 |
| **D: design / evaluation obligation** | 设计契约、尚需接线的组合能力或尚未取得的实验结论 | “We will evaluate …”; “The publication protocol requires …”; 不能写“achieves” |

“已测试”应另列证据维度，不应由 I/P 自动推出。存量文档报告的测试只能标为“历史报告，本次未重跑”。

## 2. 论文必须先统一的运行路径

| 路径 | 固定提交中的入口和实际状态 | 对论文的影响 |
|---|---|---|
| `flat-v1` | `VolumeFormat` 默认值；普通 FUSE → VFS → metadata / ObjectBlockStore | 适合作为同仓库普通文件系统基线 |
| `workspace-v1` | `mount_workspace_with_catalog`，可装配 packed lower；旧 r31 表示与生命周期 | 不可把新 entity 的无全局 head/CAS 特性套给该路径 |
| `workspace-entity-v1` | 必须 `--experimental-entity-mount`，fresh-only Redis + S3；`EntityFuse` 直接调用 `EntityNamespace` / `EntityData` | 可研究当前实体增量设计，但应明确是研究原型；不能宣称可无缝恢复现有工作区 |
| `packed-metadata-v3` | 认证只读快照挂载；PM11/IP06；当前 CLI 拒绝非零 payload-cache/prefetch 预算 | 可单独检验 immutable metadata 查询路径，注意与可写工作区缓存配置不同 |
| `workspace-native-v2` | Native P1 数据运行时；仍要求 `workspace-v1` schema-1 元数据基线 | 不是新 entity 的别名，也不是三项创新天然完整接通的证明 |

来源：[格式默认值](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/config.rs#L311)、[CLI 分流](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cli.rs#L378)、[entity 入口拒绝默认 admission](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cli.rs#L861)、[只读 packed 挂载](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cli.rs#L920)、[Native P1](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cli.rs#L1245)。

### 会阻断三项联合主实验的三个接线缺口及对象形成限制

1. **Entity 挂载当前没有传递 EC hint。** `src/cli/entity_mount.rs` 构造 `S3Config` 时设置 bucket、endpoint、part size 等字段，随后使用 `..Default::default()`，没有设置 `rustfs_ec_block_size_hint`。普通 CLI 的 `create_s3_client` 则明确传递 `args.s3_rustfs_ec_block_size_hint`。因此三个模块分别存在，不代表当前 entity 命令行组合已经启用第三项机制。[Entity S3 构造](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cli/entity_mount.rs#L49)；[普通 CLI 对照](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cli.rs#L1473)。

2. **当前 packed fixture 的 S3 构造也没有传递 hint。** `packed_v3_snapshot_fixture.rs` 的 S3 配置同样使用默认 hint。研究对象若是 packed containers 的布局，必须明确增加构建期配置、为每轮生成新对象，并从服务器持久化元数据验证实际 B/q。[Fixture S3 构造](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/bin/packed_v3_snapshot_fixture.rs#L918)。

3. **Entity strict conditional durable PUT 本身也没有 hint header。** `S3Backend::put_object_create_only_durable()` 直接构建 PUT 请求，未调用 hint policy/metadata；而同文件普通 `put_object_create_only()` 有对应逻辑。EntityData 调用前者，故只补 S3Config 不足以接通。这一处修复必须保留 If-None-Match、412 冲突后的内容核对与不降级 unconditional PUT 的原契约。[strict PUT](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cadapter/s3.rs#L1191)。

**进一步的对象形成限制：** EntityFuse `MAX_WRITE=1 MiB`，write callback 拒绝更大请求。EntityData 将该请求按 chunk 边界切片，逐片原样上传，无普通 VFS 聚合或压缩。因此当前 mounted Entity upper 对象不超过 1 MiB；auto 又只对大于 1 MiB 的对象发提示。即使全部接线补齐，当前 upper auto 仍无 B hint，应作为负向控制。固定 B 模式可以成为另一个处理组；更大 upper 聚合对象则需要新增设计。不能用大逻辑文件或改变内容压缩率假装 Entity upper 已跨 finalized-object 阈值。[FUSE 写上限](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/fuse/entity.rs#L38)、[写对象形成](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/data.rs#L400)、[auto 条件](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cadapter/s3.rs#L64)。

补接线前，初稿应将“完整协同原型的实验”作为计划，不能写成已完成的实现验收。上述补齐属于后续代码工作，本次规划没有修改产品代码。

## 3. Delta-Based：可以主张什么

工作区状态可表述为 `W_i = Resolve(B, U_i)`，其中 B 为精确固定的不可变 lower，U_i 为私有可变元数据和新数据映射。Delta 表示“与共享基线不同的状态”，不要求每个字段采用差分编码，不是字节级压缩算法，也不承诺保存全部操作历史。当前 entity 上层保存 changed entities 的**当前值**：目录项、inode 属性、xattr/ACL 与规范化 chunk map。

### 实际解析语义

- 上层 `Present` 覆盖 lower，`Whiteout` 明确删除，只有上层不存在才回落到 lower。已删除状态不能等同“无记录”，否则会复活 lower 文件。
- inode 首次 copy-up 后由私有当前属性服务；hardlink 别名指向同一工作区 inode，修改不传播到兄弟工作区。
- present chunk map 完整覆盖当前逻辑 chunk，span 为 upper `Data`、`LowerRange` 或 `Hole`；不存在的 span 不是隐含回退。
- 首次写入主要物化映射元数据并替换写入区间，不要求先复制完整 lower payload。新数据仍然必须存储。
- `lower_visible_size` 只减不增；truncate 后重新 extend 的区域必须为零或新写入，不能恢复旧 lower 字节。
- 并发控制以冲突 inode、chunk、parent 为范围；live lease 和交易中的 authority 校验提供 stale-writer fencing。Redis Lua 仍在 Redis 内串行执行，没有“Redis 单线程瓶颈消失”的依据。

来源：[当前实体契约 §§1–8](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/doc/superpowers/specs/overlay-workspace.md#L95)、[实际 resolver](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/resolver.rs#L123)、[ChunkMap](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/model.rs#L246)、[data write 路径](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/data.rs#L304)。

### 不能省略的当前限制

当前 entity adapter 使用 **direct I/O、零 metadata TTL、不接入普通 VFS cache/writeback**；每个写入在对象 durable PUT 后发布映射。它与 buffered flat/workspace-v1 的比较同时改变了缓存与持久化路径。因此，“entity 比普通卷快/慢”不能被解释成纯增量表示的效果。主因果实验应在相同 entity 引擎上比较预物化基线与共享 lower，或另行构造语义和缓存匹配的对照；跨引擎比较应明确作为整体系统对照。[适配器](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/fuse/entity.rs#L1)。

entity `MAX_IO_BYTES` 为 16 MiB；实验 runner 使用 4 MiB chunk/block，普通 64 MiB chunk 默认值不适用。packed entity lower owner 当前每个 store 的 active census 上限为 256。计划中 1/8/32/64/128 个工作区可作为合理初始曲线；超过上限必须先实现分页所有权管理，不能简单修改计数上限冒充可扩展性证明。[IO 上限](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/data.rs#L35)、[owner 限额](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/stores/kv_store/packed_reader_pins/entity_owners.rs#L177)。

另有与分页能力不同的 **Entity 目录完整枚举上限**：`MAX_DIRECTORY_ENTRIES=4096`，merge 结果也受该限；PackedLower load_directory 超限返回 Unsupported，并限制 retained directory bytes 为 4 MiB。EntityFuse opendir 先取得完整 Vec。大 fanout 的 standalone Packed 分页试验不能当作已接入 Entity 的能力；Entity 10^6 总文件规模需合理分散目录。[目录契约](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/resolver.rs#L19)、[lower 拒绝路径](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/packed_lower.rs#L588)。

fresh-only mount 仅提供当前实验的启动和 orderly unmount；不提供 reopen/resume/discard 包装器、process-crash takeover、旧工作区导入或原子切换。功能 API 中存在 recovery/ownership 方法，不等于完整挂载栈故障恢复已经通过。[明确范围](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/doc/architecture/workspace-overlay.md#L100)。

## 4. Packed Metadata：必须写成快照结构

第二项机制的对象是**对象存储上的不可变文件系统快照及其访问索引**。`ReadGroup`、`GroupMeta`、`GroupContainer` 的作用不同：逻辑 group 按同一 parent 下的 raw-name 区间组织；GroupMeta 页面联合包含目录项、常用 inode 属性、inline 内容或数据 frame 定位；一个物理 container 可容纳多个 group。大目录通过分层 IP06 索引和有权重的目录序号访问，不需要在挂载时把整个目录或快照读入内存。

PM11 manifest 提供认证根与格式契约；访问还可能经过 group/inode/container/frame/cold/large/reverse 等索引。direct `getattr` 可使用 inode index 的 hot attributes，不必拉整个 GroupMeta；普通 frame read 仍需认证 descriptor 及 payload Range。不能承诺“每文件固定两个 GET”，不能把所有索引访问隐去，也不能把 metadata 合并等同数据访问一定更快。

来源：[GroupMeta 当前结构](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/packed_v3/meta.rs#L1)、[认证 snapshot](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/packed_v3/wire005/manifest.rs#L345)、[按权重分页](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/packed_v3/wire005/index.rs#L990)、[hot-attribute 路径](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/packed_v3/readonly.rs#L939)。

“无需回访元数据库”的可辩护范围是 **immutable lower 的目录、属性和数据定位查询**。可写 upper 查询、lease、reader pin、发布、GC 等仍可访问 Redis/TiKV。把这一点写成“整个文件系统无元数据服务器”是不成立的。

当前 GroupMeta raw page 上限 256 KiB；小文件可 inline，但 inline 不是论文主张的必要条件。比较时需把以下因素解耦：metadata 联合布局、数据 co-pack、inline、压缩、frame 大小与缓存。否则性能收益无法归因于 metadata placement。[有界页面与 inline 限制](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/packed_v3/meta.rs#L23)。

### 发布与恢复

source namespace importer、producer、认证 binding、journal、reader pins 与收集器已有实现。`publish/binding.rs` 明确其基础 proof 不证明 uploaded dependency closure 或 source-view consistency。当前实验 entity export/恢复与旧 r31 管理路径应分别核验。不能用 `finish()` 返回 manifest 或只读挂载成功替代原子发布和崩溃恢复。

论文正确性契约应要求：固定一致源 → 构建/上传所有引用对象 → 验证依赖 → 写 index roots/manifest → 取得新不可变 owner → 原子发布 binding → 保留旧 view 的 reader/owner → 可恢复地清理失败对象。普通 fsync/close 不自动构建新 packed snapshot。增量重发布、跨目录任意重布局、任意 4 KiB 修改仅产生 4 KiB PUT 均不能直接作为当前承诺。[发布基础 proof](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/publish/binding.rs#L1)、[source importer](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/packed_v3/wire005/source_namespace.rs#L412)、[spec 发布边界](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/doc/superpowers/specs/packed-meta.md#L903)。

## 5. Variable-Granularity：对象大小、B、q 是三个层次

`S_o` 表示最终上传对象字节长度，已包含 framing/compression；它不同于文件长度、FUSE request、BrewFS chunk、写回暂存分配长度。B 为 RustFS EC 编码块，q 为 shard 内可独立校验/读取的物理 frame 大小。packed snapshot 的压缩 frame 又是另一个层次；不能复用 B/q 的术语把这些大小写成相同机制。

BrewFS S3 adapter 在普通 PUT / vectored PUT / 非严格 create-only / MPU 创建入口按最终 wire bytes 调用同一 hint policy；Entity 使用的 strict durable create-only 入口尚未加入 hint header，不能把此描述推广到所有上传 API。当前候选 B 为 64 KiB、256 KiB、1 MiB、4 MiB；`auto` 对 `S_o <= 1 MiB` 不发送 hint，对更大对象请求 1 MiB。RustFS 当前 default B 也为 1 MiB。所以 auto 在该默认配置中可能**完全不改变 B**。HEAD 中有效 B 才是布局证据，请求 header 仅是建议。[客户端选择函数](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cadapter/s3.rs#L25)、[服务端请求与持久化契约](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/object_api/ec_block_layout.rs#L1)。

### q 是已实现且默认关闭的能力

RustFS `RUSTFS_EC_READ_QUANTUM_ENABLE` 和 `RUSTFS_EC_READ_QUANTUM_FLEET_CONFIRMED` 默认均为 false。两个 gate 都启用后，普通 PUT 与 MPU 对适用的新对象选择 q；非 inline、非 protected/shard-integrity 写入才进入该路径。仅当 q 与完整 shard 不同时持久化 marker。GET、读取校验和 healing 根据对象已有 marker 解读，而不是按当前写开关重新解释旧对象。[默认值](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/config/src/constants/object.rs#L130)、[PUT 写入](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/set_disk/ops/object.rs#L3684)、[MPU 写入](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/set_disk/ops/multipart.rs#L2269)、[GET](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/set_disk/read.rs#L1090)、[healing](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/set_disk/ops/heal.rs#L1082)。

设数据 shard 数为 d，完整 shard 大小为 s，选择器要求 `q | s` 且 `(q*d) | B`。当前策略为：B≤256 KiB 时目标 s/2；256 KiB<B≤1 MiB 时目标 s；B>1 MiB 时目标 1 MiB；再从有限候选集中选择满足几何的 q。它不是面向每次请求动态学习的策略，也不是可以任意设 q 的现成公开参数。

以现代编码、EC 2+2 的完整 stripe 为例：

| B | s=B/2 | q gate 关闭 | q gate 开启的选择 | 是否改变 framing |
|---:|---:|---:|---:|---|
| 64 KiB | 32 KiB | 32 KiB | 16 KiB | 是，适用对象 |
| 256 KiB | 128 KiB | 128 KiB | 64 KiB | 是，适用对象 |
| 1 MiB | 512 KiB | 512 KiB | 512 KiB | 否；没有新 marker |
| 4 MiB | 2 MiB | 2 MiB | 1 MiB | 是，适用对象 |

在 d=4、B=4 MiB 时，s=q=1 MiB，开关同样不改变 framing；d=8 时也不会把 4 MiB B 对应 shard 再切小。实验必须按实际持久化几何分组，不以“q-on”替代实际布局变化。任意 q sweep 需修改研究接口，应该作为待实现实验控制，而非现有配置。

### 两项重要读取混杂

**普通 ObjectBlockStore 路径：**只要挂载配置了任意 hint，`prefers_full_object_reads()` 为 true；继而关闭相应小范围路径，使用完整对象 SingleFlight 和相同容量的 LRU。即使 auto 对某个小对象不发 header，这个挂载级策略仍启用。B/q 因果实验必须固定这些客户端策略。[策略开关](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cadapter/s3.rs#L1109)、[LRU](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/chunk/store.rs#L506)、[Range 条件](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/chunk/store.rs#L1216)。

**Entity upper 路径：**对每个命中的 upper object，当前 `read_object` 先 HEAD，再 GET Range `[0, descriptor.size)`，校验完整 SHA-256 后切出用户需要的区间。因此 upper 4 KiB 读取不意味着 4 KiB 后端 Range。只有增加独立认证单元并正确接线后，才可能把 upper 局部读变为真正的细粒度对象请求；这不是当前已有能力。Packed lower 本身具备 authenticated frame Range，可优先用于第三项的组合研究。[实际读取](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/data.rs#L836)。

### “读写放大”应该如何收敛

物理读放大必须由实际磁盘 bytes / logical delivered bytes 测得；网络 Range body、metadata GET、decode raw bytes 是不同口径。B/q 不改变固定 d+p 编码的名义冗余率 `(d+p)/d`。RustFS 尾 stripe 按实际剩余长度计算，不是每个尾对象都补满 B，因此不能预设“大 B 浪费一个完整 stripe”。q 更小还会增加 checksum/frame 管理开销。BrewFS immutable update 引起的重写、对象个数、压缩边界、上传重试与 RustFS EC overhead 必须分别计数。[尾 shard 计算](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/erasure/coding/erasure.rs#L1087)。

初稿可写“reduces the mismatch between object layout and partial-access granularity”作为目标；“reduces read and write amplification”必须作为待检验假设，并明确可能出现读写权衡，不应把二者都写成必然结果。

## 6. 现有实验与集成的证据位置

### Agent-like mixed I/O 历史结果

仓库的 `agent-mixed-fuse-results.md` 明确是**合成访问轨迹**，不含模型推理和编译。正式 36 次运行使用同一 BrewFS/RustFS 二进制、六轮配对，所有读写覆盖完整文件。两组实际 B 都为 1 MiB，q 写入关闭；变化是 hint 与 full-object/LRU 联动。报告自己明确该结果不能证明“改变 B 提速”，整套性能 acceptance 也未完全通过。本次不将其中数字移入新论文实验结果。

历史环境可作为重现起点：BrewFS 4 vCPU/8 GiB，RustFS 16 vCPU/32 GiB，Redis 1 vCPU/2 GiB，四块独立 40 GiB ESSD PL1，EC2+2；这是一组配置记录，不是为 OSDI 建议环境已经部署完成的证明。[实验报告](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/innovations/brewfs-rustfs/agent-mixed-fuse-results.md)、[配置 provenance](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/innovations/brewfs-rustfs/evidence/provenance.json)、[明确关闭 q 的 job generator](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/tools/perf/rustfs-hint/agent-mixed/prepare_jobs.py#L22)。

### 用户先前真实 Agent 画像

当前上下文报告 DSH `0.1.5-rc.1`、模型实际配置 `deepseek-v4-flash`、SWE-bench Verified 小样本、WSL passthrough/FUSE 画像。该报告属于用户先前工作线索；本次没有原始日志可重算，不能将它作为新的独立测量。应先取回完整 task IDs、trace、采样时钟、失败事件、缓存层说明和代码 SHA，再用于 motivation 的负载证据；它本身不证明 BrewFS/RustFS 性能提升。

### AX

`deploy/ax-kind` 提供 Google's AX + Agent Substrate、gVisor WorkerPool 和接受预挂载 `/workspace` 的 runner。smoke 使用 durableDir；真正的 BrewFS workspace 仍需 runtime/CSI/sidecar 提供。AX 部署或 Task Running 都不足以证明 Agent 文件访问已走 BrewFS。正式入口应让每个 workspace 记录 mount ID、BrewFS session ID、manifest digest 和探针事件，且在任务读写时能关联到 FUSE/object counters。[AX README](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/deploy/ax-kind/README.md#L47)。

## 7. 可直接用于英文初稿的审慎表述

> BrewFS represents an agent workspace as a private mutable namespace over a pinned immutable snapshot. Its packed snapshot layout co-locates directory entries, frequently accessed attributes, and data locators in bounded pages indexed by directory-name ranges, allowing immutable-base lookup to bypass per-file records in the metadata service. A separate BrewFS–RustFS interface selects an erasure-coding layout from the finalized object length and lets the storage backend persist an aligned physical verification and read quantum. Our evaluation plan distinguishes these mechanisms from client caching and request coalescing, and tests when their combination improves workspace provisioning and file-access costs.

这一段说明设计与评估计划，没有假装已经得到性能结果。Implementation 章节应继续披露 Entity S3Config、strict durable PUT 与 snapshot producer 三处 hint 接线缺口，以及 mounted upper ≤1 MiB 导致当前 auto 无提示、实验性挂载边界与 q 的默认关闭状态。论文贡献可以围绕“共享状态的表示与放置，以及应用请求到对象布局的可解释映射”组织；单独的 overlay、metadata packing、variable blocks 都不宜宣称首次发明。
