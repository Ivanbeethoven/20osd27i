# BrewFS 公式与系统图语义核验

日期：2026-10-23。审计对象为根目录 `main.tex` 引用的 `sections/`，以及原始图 `figures/system-architecture-single-column.png`。最终可编辑版本为 `figures/system-architecture-editable.svg`，已根据下文语义约束复核。本文行号对应本次严谨性修订后的源文件。

本次只修改 `sections/04-delta.tex`、`sections/05-packed.tex`、`sections/06-layout.tex` 中的定义和适用条件，没有更改实验数字、公式参数值、系统实现或结论。可编辑图和最终论文编译由主任务统一完成；本审计没有运行主论文编译或性能实验。

## 结论

六条独立行间公式没有发现算术错误。名称解析式原先以“在 W_i 中被隐藏”作为定义 R_i 的分支条件，存在循环表述；现已改成四个互斥分支。其余修订补全成本模型的生命周期边界、q 几何条件的准入范围，以及区间计数公式的定义域。公式本身不能作为性能收益或全部路径已集成的证明。

## 逐式核验

| 公式／位置 | 核验结论与边界 | 本次处理 |
|---|---|---|
| `W_i = Resolve(S, Δ_i)`；`sections/03-overview.tex:42–58`，`sections/04-delta.tex:6–13` | 合理的视图定义；Resolve 包括上层优先、删除屏蔽与允许时继承。不是普通加法、无条件集合并集或字节差分。S 可以是 native catalog 或 packed 表示。 | 不改等式。 |
| 名称解析 `R_i(d,n)`；`sections/04-delta.tex:22–38` | 用 Δ_i 的 Present、Whiteout、Absent 三态，并将 Absent 按 H_i 的真假再分为两支，四个条件互斥且覆盖有效状态。H_i 仅阻断适用的下层继承，不隐藏 present upper 条目。 | 去掉依赖结果视图的“the name is hidden in W_i”；保留原 Δ_i 记号，未另引 D_i。 |
| `M_live-meta = M_S + Σ M_Δi + M_control`；`sections/04-delta.tex:95–110` | 对一个共享基线、互不重叠记录类别的逻辑元数据记账合理。S 只计一次；不是物理磁盘占用公式，不含 payload、编码/checksum、缓存或未回收对象。当前正文已有这些边界。 | 不改等式或口径。 |
| `C_c(K)`；`sections/05-packed.tex:108–121` | 适用于可加资源成本；CPU-seconds、字节和金额分别计量，不能把并行任务 wall time 相加为 makespan。每个 published version 的生命周期含构建、发布、K 次使用和回收。 | 明确一个版本及 K 次使用；反复重建按各版本累计，共享工作只计一次。 |
| `q | s`、`qd | B`；`sections/06-layout.tex:110–119` | 与固定研究分支选择器的几何准入检查一致。B、s、q 为适用的正 byte 尺寸，d 为数据 shard 数；这是新 q framing 的准入要求，不能扩展为所有默认／legacy 布局无条件成立的定律。 | 加入 eligible new framing 和 admission constraints 的限定；不改约束。 |
| `n_q(a,ℓ) = ceil((a+ℓ)/q) − floor(a/q)`；`sections/06-layout.tex:121–133` | 正确计算半开 shard 区间 `[a,a+ℓ)` 所相交的 quanta 数。条件为 a≥0、ℓ>0、q>0；空区间不能直接套用。`n_q q` 是忽略尾部与批处理后的覆盖量，不等于一次应用请求的物理磁盘字节。 | 明写半开区间及三个条件，保留等式与后续物理读取边界。 |

区间计数的边界检查：`[0,q)` 相交 1 个 quantum；`[q,2q)` 也相交 1 个；对整数 byte 尺寸 q>1，`[q−1,q+1)` 相交 2 个。结束点落在 quantum 边界时不会多算下一段。

## 其他符号与算例

- `g` 与 `L_o` 分属客户端对象形成和最终编码后上传长度，不能写成等式。10 MiB Slice、g=4 MiB 的原始 4+4+2 MiB 示例成立，但仍受对齐、flush 和对象形成路径约束。依据：`sections/06-layout.tex:14–32`；`evidence/principles-code/objects.md:26–32`。
- 表中的 64/16/8/4 个对象，以及 2/4/8/16 MiB 获取量，在对齐的 64 MiB Slice、读 `[10,12)` MiB、无缓存、无压缩、整对象获取的条件下算术正确。不能用于所有 Range GET。依据：`sections/06-layout.tex:54–82`。
- `h(L_o)` 是客户端对 B 的可选提示，不是对 B/q 的最终赋值。当前 automatic 策略：L_o≤1 MiB 不发 hint，否则请求 B=1 MiB；该 B 可能与默认值一致。依据：`sections/06-layout.tex:94–108`；`planning/terminology.zh.md:36–43`。
- `(d+p)/d` 是固定 EC 几何的名义冗余率，不是含 checksum、尾部和元数据的精确实存放大。依据：`sections/06-layout.tex:132–133`。
- `g_1/g_2` 如出现在图中，只能表示两个配置备选；当前普通路径没有按访问行为在线切换 g 的控制器。依据：`sections/06-layout.tex:41–47`；`sections/07-implementation.tex:100–105`。
- 不应无条件新添 `s=B/d`。实际 shard 计算分 modern／legacy，尾部另算；简图可只标 `Shard s`，在内部标 q 子区间。若采用 `s=B/d`，需要限定适用的整除示例几何。

## FUSE 定位和图示约束

FUSE 应作为 agent 的文件操作进入 BrewFS 解析／数据路径的接口标签，放在①入口附近；它不是①机制名称，不是 shared lower，也不直接等于 RustFS 接口。普通 VFS 与实验 Entity 使用不同适配路径，不应为了画一个统一入口宣称其内部缓存／写回语义相同。

正文依据：`sections/07-implementation.tex:19–48` 区分挂载入口；`:70–80` 说明 Entity 的 direct I/O、单写限制和整对象认证读取；`:116–123` 说明 Entity 的对象形成及 hint 接线限制。

固定 BrewFS 快照为 `242af5f7e9bba7afc0c61778f1084fcb20e083a0`，本地只读目录 `../brewfs-principles-242af5f`。源码依据：

- `src/fuse/entity.rs:411–418`：FUSE lookup 转交 namespace lookup。
- `src/fuse/entity.rs:591–597`：FUSE read 转交 data read。
- `src/fuse/entity.rs:622–630`：FUSE write 转交 data write。
- `src/cli/entity_mount.rs:70`：创建 EntityFuse 适配器。
- `src/workspace_overlay/resolver/mod.rs:18–24`：Present、Masked、Absent 三态，只有 Absent 能向可选下层回退。
- `src/workspace_overlay/resolver/dentry.rs:32–47`：Whiteout 解析为 Masked，Put 解析为 Present；`:91–123` 保留 masks 供目录合并使用。
- `src/workspace_overlay/entity/model.rs:75–101`：Data、LowerRange、Hole 以及完整显式映射；`:51–52` 的 lower-visible 边界只减不增。

原 PNG 的几个连接需要在可编辑重绘时准确表达：

1. S 与 Δ_i 是 Resolve 的输入；Δ_i 到 S 的箭头若无说明，容易被看成向不可变基线写入。应用 pin/read 引用或解析输入关系表达。
2. Data 引用私有 U_i；LowerRange 引用 S；Hole 返回零。私有 payload 不应画进 S。
3. q 是单 shard 内的校验／读取子区间，不能与 EC block B 画成同一层的同义分块。图示层次应为 object → EC block B → shard s → q。
4. Packed frame 是快照格式单位，与后端 q 不同；L_o → optional hint → backend selection 表达控制路径，不能把 hint 画成实时读请求的调节器。

## 后端原码复核

本次通过 GitHub connector 重新读取固定 RustFS 研究分支 `cc4926fac1107aee76540f28bf22dbd47fcbca24`：

- [ec_block_layout.rs](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/object_api/ec_block_layout.rs#L248)，blob `30d343c752854e0f8265e45fd2c7d8ebd10af381`。248–290 行选择候选 q，并检查 `shard_size.is_multiple_of(q)` 与 `block_size.is_multiple_of(q*data_shards)`；235–244 行为独立 enable/fleet-confirmed gates；293–326 行按持久化 marker 校验旧对象几何。
- [erasure.rs](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/erasure/coding/erasure.rs#L1077)，blob `4548816e8504ae2893a916da2418374b12339f40`。1077–1104 行按 modern／legacy 计算 shard size，完整 stripe 与最后一个短 stripe 分别核算；不支持“大 B 意味着每个尾对象补齐完整 B”的说法。

这些是固定研究代码的静态证据，不代表上游默认支持、挂载运行验收或性能提升。`git diff --check -- sections/04-delta.tex sections/05-packed.tex sections/06-layout.tex` 通过，最终两栏公式排版须随主任务编译和页面检查确认。
