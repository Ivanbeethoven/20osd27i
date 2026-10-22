# 英文初稿源码复审：Sections 04–06

2026-10-22。完整阅读 `04-delta.tex`（99 行）、`05-packed.tex`（118 行）、`06-layout.tex`（129 行），按 BrewFS `518e7cc39b2ff0b421ecf0f656de6d468cacb9b8` 与 RustFS `cc4926fac1107aee76540f28bf22dbd47fcbca24` 静态核验。未改原稿，未执行系统实验。

## 必须同步的两处处理范围

### P1：06-layout.tex 第 29–35 行，上传入口描述需要排除当前 strict durable PUT

原文 “The adapter applies the policy at the relevant upload entry points” 太容易被读成整个 Entity 上传链已有该能力。当前普通 PUT、vectored PUT、非 strict create-only、MPU 有 hint 路径，但 Entity 用的 `put_object_create_only_durable` 没有 header 逻辑。Implementation 即使列出缺口，此处也宜加明确范围。

建议替换起句：

> The ordinary PUT, vectored-PUT, non-strict create-only, and multipart paths apply this policy to the finalized object length. The Entity path uses a stricter conditional durable PUT whose hint propagation is not yet wired in the audited revision; Section~\ref{sec:implementation} identifies this integration obligation.

保留后文关于 MPU 全对象布局和服务器有效布局的正确说明。

### P1：06-layout.tex 第 119–121 行，upper 小对象描述需落实为当前挂载的确定上限

当前说 “Small writes may consequently create small upper objects” 仍掩盖了一个重要负向处理：EntityFuse 明确 `MAX_WRITE=1 MiB`；EntityData 每次 write 按 chunk 边界切片、直接原样 PUT；没有普通 VFS 聚合和压缩。当前 auto 仅接受 `L_o>1 MiB`，因此补完 header 后也不会在这个 mounted upper 上触发 hint。

建议替换：

> The current Entity FUSE adapter caps a write request at 1 MiB. EntityData splits that request at chunk boundaries and uploads the resulting raw segments without ordinary-VFS aggregation. Consequently, mounted upper objects do not cross the automatic policy's greater-than-1-MiB threshold. After hint wiring is completed, automatic mode remains a no-hint control for this path; fixed hints form a distinct experiment. The packed lower's authenticated frame requests are an initial candidate for testing physical range granularity.

证明与固定提交链接见 `plan_review.md` P1-1 和 `source_evidence.md` §2；不能仅改变 mount 配置就把当前 upper auto 写成有效 treatment。

## 另外两点小范围修订

### P2：03-overview.tex 第 9–10 行的多 subtree 绑定超出当前 Entity 原型

虽不在本次指定 04–06 内，查阅时发现 “A workspace may contain several selected immutable subtrees; S denotes their bound baseline view” 容易暗示 arbitrary multi-lower grafting 已接通。当前实验 bootstrap 绑定一个精确 manifest/reference；选择一个子树作为快照范围与同时绑定多个不同 lower 是不同能力。

建议改为：

> A snapshot may cover a selected directory subtree rather than an entire volume. The inspected Entity prototype binds each workspace to one exact lower manifest; composing several independently bound lower snapshots is outside this implementation scope.

若作者想保留多子树作为目标，应明确写 proposed extension，不应放入当前模型而不限定。

### P3：06-layout.tex 第 86–92 行，理想帧公式限定正长度

公式对非空区间正确；当 `ell=0` 且 `a` 不对齐时，现有公式会给一帧。建议首句写 “For a nonempty interval of length $\ell>0$ ...”。本项不改变核心设计结论。

## 核验通过的主要内容

- Delta 的 Present/Whiteout/Absent 可见性、Data/LowerRange/Hole 映射、不能把未覆盖 interval 视为 lower、单调不增 lower-visible size 均与当前模型相符。
- 文稿将 hardlink/枚举上限放在受支持操作契约内，没有借这些语句承诺完整 POSIX；生命周期写成 fresh-only、reopen/takeover 义务，正确。
- Packed 的 PM11/IP06、256 KiB GroupMeta 页、inode hot-attribute 直接读取、snapshot paging 与 Entity bounded enumeration 的区别正确。
- Packed publication 段区分 source consistency、dependency closure、manifest serialization 与完整发表；没有将组件存在写成已完成故障验收。
- RustFS q selector、默认 false 的两类 gate、inline/protected 限制、2+2 表格、stored layout 控制 read/heal、tail 与固定冗余率说明正确。
- 普通 VFS hint 联动 whole-object/SingleFlight/LRU 与 Entity full-object SHA-256 读路径的区别正确；没有将缓存收益归因于改变 B。

后续 Implementation 与 Evaluation 还需保留：Entity 缺 discard wrapper；4096 条/4 MiB 目录边界；Packed readonly 非零 payload-cache 被拒绝；同路径 D0/P0/P1/C 需要新增控制；四服务器各一 drive 不触发全本地 batch-pread。这些属于实验就绪条件，详见 `plan_review.md`。
