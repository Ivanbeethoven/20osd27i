# Current BrewFS checkout audit

审阅日期：2026-10-23。用户要求分析的上游仓库为
[`brewfs/brewfs`](https://github.com/brewfs/brewfs)，本地克隆位于
`work/brewfs-upstream`。

## 固定来源

```text
remote: https://github.com/brewfs/brewfs.git
branch: main
HEAD: f80e7148c82e9f1ef235ab19318b89cb41a093a2
parent: d8caa00 (AX Codex agent image merge)
working tree: clean at audit time
```

论文的行级实现清单仍以 `518e7cc39b2f` 作为 research checkpoint，因为它
对应已经冻结的 source inventory 和 RustFS fork。当前 HEAD 的变更不能被
默认为“只改部署”：它包含 Entity FUSE/namespace/data 路径的整理以及 AX、CSI
和 agent image 的新增。因此，正式跑实验前必须重新生成 source manifest，重新
执行 E00，并把当前 HEAD 作为实验二进制的唯一来源。

## 从当前代码确认的运行边界

| 观察 | 当前代码入口 | 论文含义 |
| --- | --- | --- |
| 普通卷、旧 workspace 和 Entity workspace 仍由不同 dispatch 选择 | `src/cli.rs`, `src/cli/entity_mount.rs` | 不可把 flat、legacy workspace 和 Entity 互换为单一消融 |
| Entity mount 明确是 fresh-only experiment，并在 lease renewal 失败时停止 admission、卸载并 drain | `src/cli/entity_mount.rs` | 当前路径不证明 reopen/resume 或进程崩溃 takeover |
| Entity FUSE 使用 `direct_io`, zero metadata TTL，拒绝 kernel writeback，单次 FUSE write 上限 1 MiB | `src/fuse/entity.rs` | 与 buffered ordinary VFS 的比较同时改变缓存和写回语义 |
| Entity data API 的有界 I/O 为 16 MiB；实验 bootstrap 仍应使用 4 MiB chunk/block | `src/workspace_overlay/entity/data.rs`, `src/cli/entity_mount.rs` | 不能直接套用普通 64 MiB chunk 的参数 |
| Entity lower 目录通过完整枚举并受 4096 entries 与 retained-byte 限制 | `src/workspace_overlay/entity/resolver.rs`, `packed_lower.rs` | 大目录 Packed 分页能力不能自动升级为 Entity mount 能力 |
| lower owner census 有界，terminal owner tombstone 参与回收 | `src/workspace_overlay/entity/packed_lower.rs`, `stores/.../entity_owners.rs` | workspace fan-out 必须在上限内测量，GC/owner 需要独立指标 |
| Entity upper read 先 HEAD、再取完整对象并校验 SHA-256 后切片 | `src/workspace_overlay/entity/data.rs` | q/B 对 upper 短 Range 的收益可能被完整对象完整性路径抵消 |
| Entity diagnostics instrumentation was removed from the current path | `src/workspace_overlay/entity/`, `tools/perf/run_entity_mount_comparison.sh` | The older SIGUSR1 snapshots and Redis RTT/row counters cannot support a current-HEAD causal claim; use external FUSE/object/Redis instrumentation or add a reviewed patch before relying on those counters |
| Entity S3 construction 和 strict durable create-only PUT 仍需独立审计 hint 传递 | `src/cli/entity_mount.rs`, `src/cadapter/s3.rs` | “三机制联合已接通”必须由 E00 的 request/header/effective-layout 证据证明 |
| AX/CSI/agent image 提供部署脚手架，不等于任务流量已进入 BrewFS mount | `deploy/ax-k3s`, `operator/brewfs-csi` | 端到端实验要用 mountinfo、canary 和 BrewFS counters 证明路径 |

HEAD 的 CSI README 另记录了一次 2026-10-22 单节点 k3s/AX canary：任务在
`/workspace` 读回文件并由 RustFS 对象哈希复核。这是 `workspace-v1` 的单写者
smoke，且 separate remount 仍标为 *Unverified*；csi-sanity 只执行了 33/92
项（30 通过、3 失败）。因此它可以作为“任务确实经过一次 CSI/BrewFS 路径”的
历史接入证据，却不能替代当前 `workspace-entity-v1` 的多 agent 负载、恢复或
性能实验，也不能把 AX 部署脚手架写成已完成端到端评估。

## 研究结论

当前仓库已经很适合作为研究系统的源码基线：它同时提供 POSIX/FUSE 路径、
对象存储数据层、Redis/TiKV 等元数据后端、packed-v3 只读快照和 agent 部署
脚手架。最有价值的论文优势是组合边界：共享 lower 的数据和元数据只读，
每个 agent 只维护 upper 当前值、tombstone 与 chunk map，同时用 lease/generation
fencing 保证旧 writer 不能继续提交；这套优势只有在冷 lower、稀疏修改和明确
持久化完成点下才有可测意义。

同时，当前代码明确暴露了论文必须正面处理的反例：Entity 的 direct I/O 和
1 MiB write cap 会改变缓存与对象形成；完整对象校验可能吞掉小 q 的 Range
收益；目录/owner 上限限制 fan-out；自动 B 可能与默认布局相同；部署路径的
存在也不等于 AX agent 的实际 I/O 已通过 FUSE。实验计划因此把这些条件列为
资格 gate 和 weakening outcome，而不是在摘要中把它们隐藏成“已解决”。

## HEAD 相对旧 runner 的测量边界

当前 `f80e7148c82e9f1ef235ab19318b89cb41a2` 删除了
`src/workspace_overlay/entity/diagnostics.rs`，并移除了 Entity FUSE、EntityData、
Redis backend 与 PackedLower 中的操作 span、Redis RTT/row 计数和 `SIGUSR1`
快照处理。仓库内的 `tools/perf/run_entity_mount_comparison.sh` 仍保留
`ENTITY_MOUNT_DIAGNOSTIC=1`、`BREWFS_ENTITY_DIAGNOSTICS=1` 和 helper
`snapshot` 的旧协议。因此该脚本在当前 HEAD 上不能产出可归因的 Entity 内部计数；
即使外部 Redis MONITOR 与 CPU 采样仍能运行，`entity-before/after` 也不能被当作
当前实现的内部证据。仓库中已有的单任务 AX/CSI canary smoke 只能证明一次受控
数据路径，不足以替代多 agent 负载、实体 workspace 隔离或重挂载证据。正式实验
必须使用外部 FUSE/object/Redis 观测，或在记录过
patch SHA 的研究分支中重新加入等价、低扰动的计数器，并在 E00 中验证计数器覆盖
和开关状态。

此外，`RedisEntityExperiment` 目前以裸 `ObjectClient::new(...)` 构造 PackedLower
和 EntityData，没有安装通用 `ReadObserver`；`EntityFuse` 也没有普通 VFS 的
`.stats` 虚拟文件。因此当前 Entity mount 同时缺少 lower/upper HTTP 请求分类的
内置导出，必须把 G06 的 per-layer counters 视为新增研究插桩，而不是现成能力。
