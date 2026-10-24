# 机制①逐词、逐符号审计

审计日期：2026-10-23。只读审查 `tools/draw_architecture_editable.py:113–141`、当前 `figures/system-architecture-editable.png/.svg` 及下列正文和代码；本次只新增这份报告，没有修改绘图源码、图片或论文。

## 推荐修改清单

1. `Δᵢ: private state + map` → **`Δᵢ: private writable upper`**。现文漏掉最重要的 writable/upper 角色，且把 state 与 map 列为两个同级实体，容易把 Δ 读成临时数据缓存或仅文件区间表。规范名称必须保留“私有、可写、上层”三个含义。
2. 删除悬浮在两条文件范围条带上方的独立 `Δ₁`、`Δ₂`；保留 `W₁`、`W₂`、统一的 Δᵢ 定义及 Resolve 公式。现在 W 和 Δ 共用一条未命名的条带，读者可能把完整工作区、整个 Δ、一个文件区间映射视为同一东西。图注注明条带表示每个视图的 **file-range sources**；完整 Δ 还包含 namespace、attributes 和 deletion records，不应画成只有这条数据带。
3. `U₁ payload` → 两行 **`Private payload` / `U₁`**。private 是必要属性，payload 单独不能排除共享基线对象；两行避免通过缩小字体挤入现有框。
4. 无方向引用线上的 `pin / read` → **`pinned reference`**。原标签把绑定固定身份和读取请求混在一起，斜杠也像二选一。此处线条表示固定引用，读取来源已经由 LowerRange／Data／Hole 的区间语义呈现。
5. `Hole` 下的 `0` → **`zeros`**。0 可以保留为数学简写，但在逐词优化中，zeros 能以很小空间明确“返回零字节内容”，避免零长度、EOF 或删除含义。

其余标签保留。不要将机制名称改为 FUSE、OverlayFS、copy-on-write，也不要将 S 全部改称 packed snapshot。图注需要保留“显式数据映射是图中采用的具体表示”这一边界；当前 `sections/03-overview.tex:69–71` 已在正文说明。

## 逐标签及逐词决策

| 当前标签／源行 | 决策与精炼推荐 | 词或符号的准确含义 | 问题与证据 |
|---|---|---|---|
| `1`；绘图 `:114`、标题函数 `:90–94` | 保留 | 编号标识第一个机制，不表示运行步骤一，也不要求②③随后启用。 | `sections/03-overview.tex:6–12` 明确机制独立可选；图注 `:80` 为 three boundaries。 |
| `Delta-Based Multi-Agent Workspaces`；绘图 `:114` | 保留规范全名 | **Delta**：相对于基线的私有当前状态；**Based**：工作区由共享／私有状态解析构成；**Multi**：多个独立工作区可复用基线；**Agent**：任务工作区的使用者；**Workspaces**：多个文件系统视图。 | Delta 不等于字节差分、操作日志或 dirty write buffer。Multi-Agent 不保证自动合并、跨进程安全隔离或任意协作协议。依据 `sections/04-delta.tex:6–13,49–72`，`03-overview.tex:60–65`；规范名在 `planning/terminology.zh.md:9`。 |
| `FUSE` ×2；绘图 `:119` | 保留，继续放在入口箭头上 | 进入用户态文件系统的接口；此处是 agent 文件操作的入口标签。 | 不能把 FUSE 解释为 namespace resolver、shared lower 或对象 API；不需要在小图中展开缩写。依据 `sections/07-implementation.tex:46–48`；`src/fuse/entity.rs:411–418,591–597,622–630`。 |
| `W₁`、`W₂`；绘图 `:120` | 保留；位置继续紧随 FUSE 入口 | **W** 是整个 workspace view，包含可见名称、属性和数据；下标 **1/2** 是两个工作区的标识。 | W 不是下面一条小范围数据带本身；条带只是该视图的一个文件范围例子。依据 `sections/03-overview.tex:42–58`，`04-delta.tex:40–55`。建议图注补 `Bars show file-range sources within each view.` |
| 独立 `Δ₁`、`Δ₂`；绘图 `:121` | 删除这两处悬浮重复标记；通用 Δᵢ 定义及公式保留 | **Δ** 是该工作区的 private writable upper；下标应与 W 对应，不是数据新旧版本号或一个具体块号。 | 当前放在数据条带上方，和 W 共同指向同一图形；会暗示整条带就是全部 Δ，或 Δ 只等于数据差异。Δ₂ 所在条带全为继承／空洞，也并不证明已有一份实体上层映射。若必须保留个别 Δ₁/Δ₂，应移动到明确的 upper-state 节点，不能无边界悬浮在完整视图条带上。依据 `03-overview.tex:53–57`；`04-delta.tex:49–55`；代码 `entity/model.rs:37–101`。 |
| `LowerRange`；绘图 `:125` | 保留大小写，不改成 Base/Shared/Read | **Lower** 指固定基线来源；**Range** 是明确引用的文件区间。整个名称是代码 enum variant。 | 不表示没覆盖的区间自动回退，也不是物理后端 range GET 粒度。当前连 S 的关系正确。依据 `sections/04-delta.tex:49–55`；`entity/model.rs:81–85` 明确 binding_digest、ino、file_offset；`resolver.rs:31–39`。 |
| `Data`；绘图 `:126` | 保留大小写，不改成泛称 Data block | 是显式映射中指向已形成的 upper payload 的一种来源类型；不是所有数据，也不是 Δ 内直接嵌入完整字节。 | Data→U₁ 应读作引用关系，不是 S 的修改，也不意味着短写一定生成同样短对象。依据 `04-delta.tex:51–64`；`entity/model.rs:76–80` 的 slice_id、slice_offset。 |
| `Hole`；绘图 `:127` | 保留 | 文件逻辑范围读取时产生零内容；它是显式数据映射的一种来源。 | 不等同 whiteout／删除标记；删除标记控制名称可见性，Hole 控制范围字节。依据 `04-delta.tex:22–38,51–55,60–63`；`entity/model.rs:63–67,75–101`。 |
| `0`；绘图 `:128` | 推荐替换为 `zeros` | 表示整个 Hole 范围的每个返回字节为零。 | 单个 0 不应被当成返回零字节、EOF、零长度或对象 ID。zeros 更明确，且不用添加解释句。依据 `04-delta.tex:52–53,61–63`。 |
| `Δᵢ:`；绘图 `:129` | 保留 | Δ 是私有上层；**i** 将其绑定到 Wᵢ；冒号是标签定义。 | 不将 Δ 改为 dirty overlay，避免上下文中同名“增量”混淆。依据 `04-delta.tex:6–9,66–72`。 |
| `private`；绘图 `:129` | 保留，放入规范名 `private writable upper` | 修改属于指定工作区；不会直接改变 S 或其他工作区的私有状态。 | private 不代表加密、ACL 完整隔离、进程沙箱或网络隔离。依据 `03-overview.tex:60–65`。 |
| `state`；绘图 `:129` | 从此简标签替换为 `writable upper`，详细 state 含义留图注／正文 | 此处应指名称、当前属性、删除记录和数据映射。 | 只写 state 太泛，会包括内存会话、打开句柄、未写回数据或运行状态；本机制没有承诺保存这些状态。依据 `03-overview.tex:53–57,95–106`，`04-delta.tex:66–72`。 |
| `+`；绘图 `:129` | 删除，不改用数学加法符号 | 原意只是并列列举；不是数据合并操作。 | mappings 本来属于 upper state，写 state + map 将整体和部分并列；还可能与 Resolve 的非算术组合混淆。依据 `03-overview.tex:53–54`。 |
| `map`；绘图 `:129` | 从此标签删除，由图中的类型及图注表达；如果必须保留则用复数 `mappings` | Δ 可含多个文件／chunk 的映射，不是唯一一张全局表。 | 不应把 Δ 限定为区间表，也不应宣称所有实现恰好使用相同 ChunkMap enum。依据 `04-delta.tex:49–55`；`entity/model.rs:89–101`；`07-implementation.tex:34–48`。 |
| 新建议 `writable` | 增补 | 上层承接该工作区允许的私有修改，与 immutable lower 相对。 | writable 不表示 write 已经持久化。普通路径可选 commit-before-upload，Entity 采取 durable-then-map，不能由这个词推断统一完成语义。依据 `04-delta.tex:76–81`。 |
| 新建议 `upper` | 增补 | 元数据／映射的优先解析层，与 lower 形成规范的逻辑相对关系。 | 是逻辑层，不是空间位置、内存等级，也不是必须采用 Linux OverlayFS 实现。依据 `04-delta.tex:6–13,22–38`。 |
| `Wᵢ = Resolve(S, Δᵢ)`；绘图 `:130` | 整体保留 | **Wᵢ** 是结果视图；**=** 是定义；**Resolve** 是遵循可见性规则的解析操作；**S** 是固定共享基线；**Δᵢ** 是该视图的私有上层；括号／逗号区分函数实参。 | Resolve 不是 S+Δ 的字节加法、全集覆盖、自动合并或脏读缓存。正文已有四个互斥名称分支及显式数据来源说明。依据 `03-overview.tex:42–58`；`04-delta.tex:22–38,49–55`；代码 `resolver/mod.rs:18–24` 与 `resolver/dentry.rs:32–47`。 |
| `U₁ payload`；绘图 `:132` | 替换为两行 `Private payload` / `U₁` | **U₁** 是图示工作区的私有上层数据对象标识；**payload** 是实际存储的新增字节，与 Δ 中的名称、属性和映射记录相分离；**private** 明确归属。 | U₁ 不是所有 W₁ 数据的总对象，也不表示一个工作区只有一个对象；这里只画一个示例，③的匹配端口必须继续指同一个对象。依据 `03-overview.tex:53–54,81–88`；`04-delta.tex:49–64`。 |
| `S Shared immutable lower`；绘图 `:135` | 保留三个核心词及 S；可仅用中点／冒号统一符号和文字间距 | **S** 是基线身份；**Shared** 表示多个工作区复用；**immutable** 表示绑定的版本不原地变动；**lower** 表示被允许时继承的逻辑来源。 | Shared 不表示彼此可写；immutable 不表示快照构建期间输入自动一致，也不表示冻结整个源卷；lower 不等于 Packed。不能直接统一改为 Packed snapshot。依据 `03-overview.tex:47–58`；`04-delta.tex:6–20`；`entity/resolver.rs:22–26`；`workspace_overlay/model.rs:21–24`。 |
| `pin / read`；绘图 `:140` | 替换为 `pinned reference` | **pinned** 表示固定版本身份，读取不追随 mutable latest；**reference** 表示绑定／数据来源引用关系。 | pin 是绑定身份及必要生命周期保护，read 是访问动作；不是二选一，也不是每次 read 重做 pin。现有无箭头线最适合表达 reference。具体 reads 已有 LowerRange→S 语义。依据 `03-overview.tex:49–50,99–100`；`04-delta.tex:15–20,95–98`；`entity/resolver.rs:22–26,56–65`。 |

## 关键边界：为何不再用 private state + map

Δ 的 current state 不等于操作历史，也不等于纯字节差分。代码 `src/workspace_overlay/entity/model.rs:1–4` 明说 current entity state，并移除旧 layer/shared-head/mutation-sequence 字段；`:37–54` 保存完整 inode 当前属性；`:63–73` 保存名称／xattr 当前值或 whiteout；`:75–101` 另有数据来源和完整规范化区间表。因此 state 是上位概念，mapping 是其中一类记录，二者不应在图中用加号并列成两个独立层。

把标签换成规范 `private writable upper`，再在图注用一句 **`Δ_i stores private metadata and data mappings.`** 即可清楚地区别于 VFS dirty buffer。不要为排除误读而把 `persistent` 或 `durable` 塞进图内：普通路径允许显式选择 commit-before-upload，而 Entity 为 durable-before-map；“上层状态”与“该 payload 此刻远端持久化”仍需区分。依据 `sections/04-delta.tex:66–81`。

## 视图与示例条带的关系

当前条带同时靠近 Wᵢ 与 Δᵢ，且含 LowerRange、Data、Hole 三种来源。最省空间且准确的解释是：**条带举例展示 Wᵢ 中某文件的逻辑范围来源，Δᵢ 及固定 S 共同决定这些来源**。因此 W₁/W₂ 留在 FUSE 入口，独立 Δ₁/Δ₂ 标记移除；Δ 的定义只保留一次。图注定义一次条带即可，不需要把整个 workspace 画成实体磁盘或把 Δ 画成一份完整文件副本。

如果主任务仍要把条带明确解释为 Entity 的显式 ChunkMap，则应标为 `Data map in Δ_i`，并同时说明它只是 Δ 的一部分。不能将该具体表示无条件推广到 catalog/native 所有工作区路径；`sections/04-delta.tex:49–55` 把 Entity 明确定位为 one concrete current-state representation。

## 固定代码证据位置

代码快照：`../brewfs-principles-242af5f`，SHA `242af5f7e9bba7afc0c61778f1084fcb20e083a0`。本审计已读取该快照的 AGENTS.md；本次没有修改代码。

- `src/workspace_overlay/entity/resolver.rs:1–5`：upper-first current-state resolution，调用者保留 namespace lease/lower ownership。
- `src/workspace_overlay/entity/resolver.rs:22–26`：attach 建立稳定认证 manifest 身份，真实 adapter 保留验证后 manifest 和 lower reads 边界。
- `src/workspace_overlay/entity/resolver.rs:31–39`：下层 chunk map 含 LowerRange/Hole，超过 immutable EOF 为零；认证／传输故障不视为缺失。
- `src/workspace_overlay/entity/resolver.rs:56–65`：实际 binding 与 expected 不符则 fenced。
- `src/workspace_overlay/entity/model.rs:18–23`：LowerBinding 包含 manifest key/digest 和 inode 边界。
- `src/workspace_overlay/model.rs:21–24`：catalog BaseRevision 使用 layer_id、sealed_version、root_hash，不必绑定 packed manifest。
- `src/fuse/entity.rs:411–418`、`:591–597`、`:622–630`：FUSE lookup/read/write 分别进入 namespace/data 接口。
- `src/workspace_overlay/resolver/mod.rs:18–24`：Present／Masked／Absent 三态，只有 Absent 可回退。
- `src/workspace_overlay/resolver/dentry.rs:32–47`：Whiteout 变 Masked，Put 变 Present；`:91–123` 保留删除屏蔽以防下层名字复活。

这些定位支撑机制标签和关系，不表示本次已运行挂载、持久化或性能实验。最终所有标签是否仍满足字号和单栏尺寸，需要由主任务重绘后视觉检查。
