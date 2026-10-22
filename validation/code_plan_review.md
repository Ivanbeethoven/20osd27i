# 论文大纲与实验计划源码复审

审阅基线：BrewFS `518e7cc39b2ff0b421ecf0f656de6d468cacb9b8`、RustFS `cc4926fac1107aee76540f28bf22dbd47fcbca24`。2026-10-22 对 `planning/01-research-outline.zh.md`（192 行）和 `planning/02-experiment-plan.zh.md`（366 行）做静态核验。以下位置按审阅时版本计；没有修改这两个文件，没有运行性能或故障实验。

P1 = 必须修正才能让实验处理组或执行前提成立；P2 = 会产生错误因果解释或适用范围误读，需在成稿前修正。计划已经明确没有实测结果，q selector 的数值示例也正确；问题主要是一些计划仍把待实现控制与现有可执行路径放在一起。

## P1-1：Entity B 路径还有第三处接线缺口，且当前 auto 在挂载 upper 上不会跨阈值

**位置：** 大纲 §4 第 7 项（第 67 行）；实验 E00（第 148–150 行）、E08/E11。

**事实：** 除 `entity_mount.rs` 与 packed fixture 的 `S3Config` 未传 hint，Entity 实际调用的 `S3Backend::put_object_create_only_durable()`（`src/cadapter/s3.rs:1191–1219`）也**没有发送 hint metadata**；同文件普通 create-only 方法有该逻辑。仅补挂载参数不能让 Entity upper 生效。此外，EntityFuse `MAX_WRITE=1 MiB` 并拒绝更大请求（`src/fuse/entity.rs:38,638`）；EntityData 将当前 write buffer 按 chunk 边界切片后直接 PUT，未做普通 VFS 聚合或压缩（`entity/data.rs:400–450`）。所以当前挂载 upper 对象不超过 1 MiB，而 auto 只对 **大于** 1 MiB 的对象发 hint。即使前两层接线修复，当前 auto 也不会对这些 upper 对象发 B hint。

**建议替换 E00 对应句：** “研究分支需补齐 Entity S3Config、strict conditional durable PUT 的 hint header，以及 Packed producer 构建参数；逐条验证请求 header 和有效布局，保留 If-None-Match 与冲突校验语义。跨压缩/最终对象尺寸阈值的试验先在实际具有编码或聚合步骤的 producer/普通上传路径实施。Entity upper 单独核验 ≤1 MiB 的对象形成方式；其 auto 无提示是当前路径的预期负向控制，显式固定 B 是另一个合法处理组。若要聚合 upper 写入或改变认证粒度，列为新增设计与正确性工作。”

来源：[strict PUT](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cadapter/s3.rs#L1191)、[auto policy](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cadapter/s3.rs#L64)、[FUSE cap](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/fuse/entity.rs#L38)、[object formation](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/data.rs#L400)。

## P1-2：fresh-only 的 mounted Entity 生命周期不能直接执行恢复、回收与连续 publish 计划

**位置：** 大纲 §4 第 2 项（第 62 行）；实验 E04 第 182–186 行、E07 第 210–214 行、E15 第 282–286 行、E16 第 290 行；E00 停止条件。

**事实：** 当前显式实验入口只 bootstrap fresh catalog/namespace；正常卸载保留 namespace、lower owner 和数据，wrapper 没有 reopen/resume、discard、process-crash takeover、importer 或 atomic cutover。已有底层 API/owner recovery 与一般设计契约不能替代 mounted stack qualification。Packed binding 源码也明确不认证 durable publication。连续创建新 scope 加 bucket teardown 只能测 fixture 周转，不能证明生产回收或恢复。

**建议新增统一门槛：** “E00 为每个入口建立 fresh-create / remount-existing / crash-takeover / discard / publish / reclaim 能力矩阵。当前 Entity mounted path 仅 fresh-create 与会话内操作有源码入口；E04 的连续回收、E15 的客户端崩溃后重开、E16 的 publish/GC 干扰，均须先新增并资格验证相应 wrapper。否则只测保留对象/owner 增长、拒绝行为和已支持的组件故障，不把 fresh bootstrap 算成恢复。E07 先分别测 producer 构建与已选定发布 API，不能默认能把正在使用的 Entity 工作区原子发表成下一代 lower。”

来源：[当前 experimental scope](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/doc/architecture/workspace-overlay.md#L102)、[binding foundation](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/publish/binding.rs#L1)。

## P1-3：fanout=100,000 超过当前 Entity readdir 契约

**位置：** 实验 §5.3 第 135 行；E05 第 190–192 行；E14 工作负载兼容性筛选。

**事实：** `entity/resolver.rs:19` 的 `MAX_DIRECTORY_ENTRIES=4096`，merge 后目录同样受限；PackedLower 读目录超过该限返回 `Unsupported`，另有 4 MiB retained directory byte bound。EntityFuse 在 opendir 时取得完整 Vec。这与 standalone Packed 分页 reader 的范围不同。总文件数 10^6 可经合理树形分布测试，但不能据此让一个 Entity 目录有 100,000 条并要求完整 readdir 成功。

**建议替换参数说明：** “Entity 主路径目录 fanout 使用 100/1,000/4096 边界，并测试 4097 的明确拒绝；长名称同时受目录字节上限约束。100,000 fanout 仅用于已支持分页的 standalone Packed reader 或新增 paginated Entity 实现。两条结果分开呈现，不归因于同一 mounted stack。”

来源：[merge bound](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/resolver.rs#L19)、[PackedLower 拒绝](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/packed_lower.rs#L588)、[opendir](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/fuse/entity.rs#L794)。

## P1-4：同路径 P0/P1、C 因子不是现有 flags，W/R 也不是 Entity 的开关

**位置：** 实验 §4.2 第 89–96 行、E05 第 190 行、E09 第 232 行、E11 第 248 行。

**事实：** D0 已注明需适配器，正确。P0（逐文件 KV）、P1（immutable sorted-KV）同样需新增同一 namespace/data/lower 契约的参考实现，不能复用另一个 volume-format 后只换标签。C 的独立布局/读取/eviction 控制也需新增配置或独立 S3 驱动。W/R 是 ordinary VFS 已保留的实现，不是现成 on/off 参数，Entity 直达路径不使用它们。

**建议替换消融开头：** “D0、P0、P1、可选 P3 和独立 C 控制均列为待实现的研究适配器；E00 必须记录 patch SHA、identity/ownership/fencing 契约和共同功能测试。完成前不能把这些格子列为可执行消融。W/R 在普通 VFS 中固定一致；仅当另有必要且控制分支具备正确性证据时补做敏感性实验。Entity 主路径不列 W/R 二元因子。”

来源：[Entity 绕过 VFS](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/doc/architecture/workspace-overlay.md#L130)、[ordinary writer](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/vfs/io/writer.rs#L936)、[ordinary reader](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/vfs/io/reader.rs#L599)。

## P1-5：E06 的非零 payload-cache sweep 在当前 Packed readonly 入口会被拒绝

**位置：** 实验 E06 第 202–204 行；§3.4 cache 字段。

**事实：** 当前 wire005 readonly mount 检查 read-memory、read-SSD、prefetch、range-background-prefetch，任一非零/启用直接报错。Metadata/index 缓存与 payload cache 是不同预算；Entity 也不走普通 VFS payload cache。四种 cache 状态不能统一当作所有入口都有的现成配置。

**建议替换：** “按入口分别列 metadata/index、payload、kernel、server cache。当前 Packed readonly payload cache/prefetch 保持零；0/256 MiB/1 GiB/4 GiB 仅扫已有可配置的元数据缓存，或明确标注为尚待新增的 payload-cache 研究分支。DATA-WARM 必须注明具体变热的是哪一层，Entity 不沿用普通 VFS 的数据 cache 参数。”

来源：[显式拒绝](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cli.rs#L931)。

## P2-1：hint 与 W/R 的因果关系写错，Entity 整对象读取应写成确定的当前路径

**位置：** 大纲 §4 第 4 项（第 64 行）、第 7 项（第 67 行）；实验 E09 第 234 行。

**事实：** hint config 的确联动普通 ObjectBlockStore 的整对象读取偏好与 LRU；writer 的 remote-complete budget release 及 reader 的 cached shared reply 代码没有 hint 条件。当前 Entity `read_object` 确定先 HEAD、读完整 descriptor.size、验 SHA-256，再由调用方取区间；不是“可能”走整对象。

**建议替换第 4 项：** “普通 ObjectBlockStore 的 hint 配置会联动完整对象读取策略及 LRU，需要独立控制；写预算释放和 shared-byte reply 属于普通 VFS 的其他保留优化，应在比较中保持一致，不能称为 hint 触发。Entity 使用独立数据路径。” 将“Entity upper 目前可能……”改为“当前 Entity upper 的 read_object 路径先 HEAD 并读取完整对象、校验 SHA-256 后返回所需数据；未来改为局部读取须重新设计完整性验证。”

来源：[hint preference](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cadapter/s3.rs#L1109)、[budget release](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/vfs/io/writer.rs#L936)、[shared reply](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/vfs/io/reader.rs#L599)、[upper read](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/data.rs#L836)。

## P2-2：T1 四服务器各一 drive 不触发 RustFS 的全本地 batch-pread 优化

**位置：** 实验 T1 表第 42–45 行；E08/E09 对物理读取解释。

**事实：** q marker/read 格式可在分布式配置中测试；但 `try_create_bitrot_readers_via_batch_pread` 明确要求 mmap-read 启用且所有在线 shard 本地可定位。任意远端 drive 会退回其他路径。因此不能把单服务器四盘的 batched pread 机制证据默认移植到四服务器单盘 T1。

**建议追加：** “增加单服务器四个独立 drive 的后端机制台架，记录 local batch-pread/fallback counters；四服务器单 drive 组独立验证分布式路径及网络开销。q-format 与 batching 是两个因素。两种配置均可用，但不能以同一机制解释全部结果。”

来源：[local batch preconditions](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/set_disk/core/io_primitives.rs#L1335)。

## P2-3：q treatment 必须重新生成对象，读取开关不能改变已有对象布局

**位置：** 实验 E09 第 232 行“在相同 upload objects ...交叉比较 legacy-q/selector-q”；E08 第 224 行数值正确，无需改值。

**事实：** q 是创建时选择并持久化的物理布局；打开/关闭写入 gate 不重编码旧对象，gate-off reader 仍依据旧 marker 读取。相同物理对象不可同时既是 legacy-q 又是 selector-q。

**建议替换：** “使用内容、长度、PUT/MPU 边界一致但分别创建的配对对象集实现 legacy-q 与 selector-q；逐对象审核 marker。每个固定布局对象集内部再切换 C 策略，保持对象及 trace 不变。gate-on但 q 等于 shard 的对象单列为 no-layout-change，不能放进小 q 处理组。”

来源：[persisted frame contract/selector](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/object_api/ec_block_layout.rs#L1)。

## P2-4：持久化完成点需按实现定义，Entity 不存在 ordinary VFS 的 local-staged 阶段

**位置：** 实验 §3.4 第 65 行、B3/B5 对齐、第 174 行、E10 第 240 行、E15。

**事实：** Entity write 成功前已做 PUT 和 metadata publication；fsync 是 FIFO barrier 与验证，并不自动提升 Redis 的配置持久性。RustFS PUT 成功的实际稳定存储合同也需记录。统一 fsync 调用次数并不自动等于统一故障域/掉电耐久性；本地 OverlayFS 和 EC 后端也有不同边界。

**建议追加：** “为各路径写 completion/failure-domain 表。不存在的 local-staged 等阶段记 N/A，不制造时间点。主比较的 acknowledged durable completion 至少明确对象成功响应合同、KV AOF/WAL 策略及 namespace 的同步范围。不能对齐的本地/远端持久性作为独立分面，而非同一等价服务结论。故障实验只验证此表中声明的保证。”

来源：[Entity fsync contract](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/workspace_overlay/entity/data.rs#L960)、[deployment policy caveat](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/doc/architecture/workspace-overlay.md#L434)、[S3 durable API contract](https://github.com/brewfs/brewfs/blob/518e7cc39b2ff0b421ecf0f656de6d468cacb9b8/src/cadapter/s3.rs#L1218)。

## 已核验正确的关键点

- q 新布局写入代码已存在且默认关闭，不能写“尚未实现”；现有选择器不是任意 q 参数。2+2 的 B/q 数值示例和“打开 gate 不保证改变布局”正确。
- 四 drive 2+2 是合理研究配置，文档没有误称 RustFS 的绝对最小支持配置。
- 写放大必须测量后才可主张降低；同 d/p 几何下不能从较小 B/q 直接推导降低冗余比例。计划已有该限定。
- 历史 DSH pilot、合成 agent-mixed 数据及 AX deploy scaffolding 未被写作本轮正式实测结果，边界正确。

