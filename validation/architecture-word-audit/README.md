# BrewFS 系统图：逐词修订对照

本轮保持 **240 × 258 pt 单栏画布**，统一三项机制的术语，并修正会影响技术理解的图形关系。
最终 SVG 仍由可编辑文字、线条和形状组成。本记录以修订前后的 scene 文件为准，报告已经落实
的变化；审计报告中的备选建议不等于已经采用。

覆盖范围：原图 **54 次文字出现、50 个不同字符串**，以下逐行覆盖；新图 **56 次文字出现、
53 个不同字符串**。重复出现的 `Packed`、`frame`、`FUSE` 和 `tail` 均按所在位置单独核对。
原文字的处理为：**29 次原样保留、22 次改写或扩充、3 次移除文字**。

依据分为 [①工作区审计](panel1.md)、[②Packed 审计](panel2.md)、[③对象存储审计](panel3.md)。
三份报告保留正文和固定代码快照的证据行号。下面的 O01–O54 是旧 scene 的出现顺序，N01–N56
是新 scene 的出现顺序；它们只是本对照表的审计编号，不会出现在系统图中。

## 三个最重要的修正

- **Name 栏的 `/h/y` 确实不合法。** GroupMeta 保存单个目录项的原始名称字节，代码明确拒绝
  `/`；父目录在索引和组上下文中。图已改为 `y`，索引旁增加 `(parent, name)`，并把 Index
  明确为 Name-range index。证据：固定 BrewFS 源码 `packed_v3/meta.rs:605–615`、
  `packed_v3/wire005/manifest.rs:591–612`，详见②。
- **固定 g 的粗粒度行原来有两个短块。** 原细行 `[10,10,10,5]` 和粗行 `[20,10,5]` 都长35，
  错误不在总量，而在固定 g₂=20 的对齐连续输入不应被切成20、10、5。已改为 `[20,15]`，
  与细行总长相等，且各有一个尾段；尾段继续填充数据色，避免像 Hole。这里只是两种固定
  配置的示例，不是在线自动选粒度。详见③的 raw strips 审计。
- **Lₒ 是最终上传长度，不是对象名称。** 原 `Objects Lₒ` 已改成 `Final length Lₒ`，配一个
  完整对象的长度标尺。客户端适用的压缩、头部和成帧先确定长度，再可选地产生 B hint。
  Lₒ、客户端 g、后端编码 B、分片内 q 分属不同量，不能互换。详见③。

## 三个标题保持原名

| 标题 | 内部词语的含义与边界 |
|---|---|
| **Delta-Based Multi-Agent Workspaces** | Delta 是相对共享基线的私有当前状态，不专指字节差分；Based 表示以该机制构成视图；Multi 表示多个；Agent 是使用者；Workspaces 是文件系统视图。没有自动合并或进程隔离的承诺。逐词证据见①。 |
| **Packed Metadata** | Packed 指将固定记录组织进可索引、有界的存储单元；Metadata 是目录项、常用属性、数据定位及相关访问结构。不是“仅压缩元数据”，也不是只保存某个单文件属性。逐词证据见②。 |
| **Variable-Granularity Object Storage** | Variable 表示存在可配置/可选择的粒度；Granularity 指对象形成、编码和校验/读取的不同边界；Object 是上传后保存的对象；Storage 是后端保存及访问。不是名为 adaptive 的运行时优化器。逐词证据见③。 |

机制编号 1、2、3 是组织方式，不是必须依次执行或同时启用的三个步骤。

## 原图全部 54 次文字出现的落实对照

| 旧编号 | 旧文字与位置 | 已落实的新文字／去向 | 每词或符号的含义及修订理由 |
|---|---|---|---|
| O01 | `1`，第一标题 | 保留 → N01 | 第一项可选机制的编号，不是流水线第一步。① |
| O02 | `Delta-Based Multi-Agent Workspaces` | 保留 → N02 | 规范机制名称；内部各词见上表。① |
| O03 | `FUSE`，左工作区入口 | 保留 → N03 | 文件系统用户态接口（Filesystem in Userspace），不是对象存储 API 或解析器。① |
| O04 | `W₁`，左工作区 | `View W₁` → N04 | W 是工作区视图，下标1指第一个工作区；View 防止把它等同下面的单条文件范围图。① |
| O05 | `Δ₁`，左条带上方 | 删除独立文字 | Δ₁ 本应是该视图的整个私有上层；悬浮在条带上会误导为整份 Δ 只有一张范围图。统一定义仍在 N11。① |
| O06 | `FUSE`，右工作区入口 | 保留 → N05 | 第二个使用者的同类文件接口；不与 O03 合并计数。① |
| O07 | `W₂`，右工作区 | `View W₂` → N06 | 下标2指另一个独立视图，不是版本2。① |
| O08 | `Δ₂`，右条带上方 | 删除独立文字 | 原因与 O05 相同；保留通用 Δᵢ 定义和 Resolve 公式，不删除私有状态机制。① |
| O09 | `LowerRange` | 保留 → N07 | Lower 是固定下层来源；Range 是明确的逻辑文件区间。它是来源类型，不是未覆盖区间的隐式回退规则。① |
| O10 | `Data` | 保留 → N08 | 指向私有 payload 的映射来源类型，不是“所有数据”，也不表示字节直接保存在 Δ 标签内。① |
| O11 | `Hole` | 保留 → N09 | 逻辑区间返回零内容；不是 whiteout、删除标记或不存在的名称。① |
| O12 | `0`，Hole 下方 | `zeros` → N10 | 明确为范围内的零字节内容，避免读成零长度、EOF 或对象编号。① |
| O13 | `Δᵢ: private state + map` | `Δᵢ: private writable upper` → N11 | Δ 为私有上层，i 对应视图；private 限定归属，writable 限定可修改，upper 限定优先解析层。state 本含 mappings，删除把整体与部分并列的 `+ map`。① |
| O14 | `Wᵢ = Resolve(S, Δᵢ)` | 保留 → N12 | Wᵢ 是结果视图，= 是定义，Resolve 是按规则解析，S 是固定基线，Δᵢ 是私有上层；括号和逗号表示实参，不是字节加法或自动合并。① |
| O15 | `U₁ payload` | 两行 `Private payload` / `U₁` → N13、N14 | U₁ 是第一个视图的私有数据对象示例；payload 是实际新增字节，private 明确归属。它不是一个工作区的全部数据；下方同名端口仍对应它。① |
| O16 | `S  Shared immutable lower` | 保留 → N15 | S 是基线身份；Shared 表示复用；immutable 表示绑定版本不原地修改；lower 是允许继承时的逻辑来源。S 不必为 packed。① |
| O17 | `pin / read` | `pinned reference` → N16 | pinned 是固定版本身份，reference 是引用关系。移除斜杠，避免把绑定和每次读取混作二选一操作。① |
| O18 | `2`，第二标题 | 保留 → N17 | 第二机制的编号，不表示①之后必须启用。② |
| O19 | `Packed Metadata` | 保留 → N18 | 机制名称，Packed/Metadata 的含义见标题表。② |
| O20 | `Native catalog` | 保留 → N19 | native catalog layer 作为 S 的替代表示；在 S 的 immutable 约束下使用，不是 Native P1 或 native_base 子系统。未采用 Sealed catalog 的备选改名。② |
| O21 | `Packed`，表示选择框 | `Packed snapshot` → N20 | snapshot 补足名词：这是不可变快照表示，而不是一个“打包”动作。此处与 O32 的 Packed 不同。② |
| O22 | `or`，两种表示之间 | 保留 → N21 | 表示 lower 的替代表示，不是每次查询回退，也不是 native→packed 的串行转换。② |
| O23 | `Read-only`，独立入口框 | 两行 `Read-only` / `mount` → N22、N23 | read-only 是只读属性，mount 明确这是独立挂载入口，不需工作区私有上层。② |
| O24 | `Index` | 两行 `Name-range` / `index` → N24、N25 | name-range 是按名称区间路由；index 是访问结构。只示意 lookup 使用的目录名索引，不把其他 inode/frame 索引压成同一路径；另增键标签 N28。② |
| O25 | `GroupMeta page` | 保留 → N26 | GroupMeta 是联合记录页格式，page 是有界访问单元；一个组/页不等于一个目录或一个物理对象。② |
| O26 | `Object Oₚ`，frame 外层 | 保留 → N27 | Object 是保存所示 frame 的对象，O 是对象记号，p 表示 packed 示例来源；它不是完整快照。保留了与下方 N52 配对的端口名。②③ |
| O27 | `Name`，表头 | 保留 → N29 | 单个目录项 raw name；不含 parent 或斜杠路径，且不要求 UTF-8。② |
| O28 | `Attr.`，表头 | `Attrs` → N30 | attributes 的精炼复数，表示常用属性；不是承诺全部扩展属性都在此单元格内。② |
| O29 | `Locator`，表头 | 保留 → N31 | 数据定位记录；不是完整 frame descriptor 或直接 object offset。新 N35 明确后续经过 descriptor，未采用 Data locator 的备选扩写。② |
| O30 | `/h/y`，Name 单元格 | `y` → N32 | 原全路径在该字段中明确不合法；y 是合法的单个名称示例，parent 另属索引上下文。② |
| O31 | `…`，Attrs 单元格 | 移除文字，换成两条属性值示意线 | 省略号没有字段信息；图形表示有属性记录，未编造具体 mode、size 等数值，也未将属性删掉。② |
| O32 | `Packed`，payload 内第一行 | 保留 → N33 | 此处修饰下一行 frame，组成 Packed frame；不是 O21 的 snapshot 选择框，不能统一替换为 Packed snapshot。② |
| O33 | `frame`，payload 内第二行 | 保留 → N34 | 与 O32 组成 snapshot 级访问/验证单位 Packed frame，区别于③的客户端成帧动作与后端 q。② |
| O34 | `3`，第三标题 | 保留 → N36 | 第三机制编号，不是强制执行顺序。③ |
| O35 | `Variable-Granularity Object Storage` | 保留 → N37 | 规范机制名；内部各词见标题表，不改为 dynamic/adaptive。③ |
| O36 | `Ordinary uploader · configured g` | `Ordinary upload · fixed g` → N38 | Ordinary 区分普通上传路径与私有/packed producer；upload 表示该路径；fixed 说明 g 是固定配置。中点分隔限定语，不是运算符。③ |
| O37 | `Slice` | 保留 → N39 | chunk 内连续范围的数据输入，不是完整文件或一次 FUSE 请求；其输入图标已去掉没有独立语义的四分格。③ |
| O38 | `g₁`，细分行 | 保留 → N40 | g 是客户端原始块目标大小，下标1表示一种固定配置；几何仍为10+10+10+5。③ |
| O39 | `g₂`，粗分行 | 保留 → N41 | 下标2表示另一固定配置；几何已由20+10+5修为20+15，不是同一配置动态生成多个不足 g 的尾段。③ |
| O40 | `tail`，细分行 | 保留并随尾段定位 → N42 | 最后不足 g₁ 的真实数据段，不是空洞或补零。③ |
| O41 | `tail`，粗分行 | 保留并随尾段定位 → N43 | 最后不足 g₂ 的真实数据段；与 O40 分别对应不同配置。③ |
| O42 | `Encode /`，客户端处理第一行 | `Compress` → N44 | 改用压缩措辞，避免把客户端处理误读为后端 erasure coding；只在适用时压缩，不保证缩小。与 N45 连读。③ |
| O43 | `frame`，客户端处理第二行 | `& frame` → N45 | & 表示与适用的压缩共同构成客户端格式处理；frame 是成帧动作，不是 O33 的 Packed frame 名词。③ |
| O44 | `Objects Lₒ` | `Final length Lₒ` → N46，配完整对象标尺 | Final 是上传表示已形成，length 是字节长度，L 为长度，o 指对象而非数字0。它是属性而非对象名称；原无定义的最终对象分格也已去掉。③ |
| O45 | `RustFS` | 保留 → N47 | 固定研究分支的兼容对象后端，名称本身不声称所有上游或 S3 后端均具备这些能力。③ |
| O46 | `default / hinted` | `Layout selection` → N48 | Layout 是对象编码/读取布局，selection 表示后端决定；避免“收到hint就采用”的二分误读，也不把 B/q 独立门控混为一件事。③ |
| O47 | `B hint h(Lₒ)` | 与 O48 重组为 `Optional B hint` / `h(Lₒ)` → N49、N50 | B 是 EC 块大小；hint 是建议而非赋值；h 是策略，Lₒ 是最终长度。函数可能不发提示，不表示 B=h(Lₒ) 必成立。③ |
| O48 | `optional` | 并入 N49 `Optional B hint`，与 O47 共用两行 | optional 明确可不启用/不发送，虚线已从长度标尺引出；不表示 q 由同一 hint 直接选择。③ |
| O49 | `U₁`，后端入口 | 保留 → N51 | 与① N14 匹配的私有对象示例端口；绕过普通 g 分块器，不宣称其 producer 已接通 hint。①③ |
| O50 | `Oₚ`，后端入口 | 保留 → N52 | 与② N27 的 packed 对象匹配；p 不是 parity、页号或普通块序号，不接普通 uploader 的 hint 线。②③ |
| O51 | `Stored (B, q)` | `Persisted layout` → N53 | Persisted 是与对象保存并供之后读取/修复解释的布局；不是所有对象都物理存着一对相同形式的显式字段。B、q 在内部标签分别定义。③ |
| O52 | `EC block B` | `EC block size B` → N54 | EC=erasure coding；block 是后端编码输入块；size 明确 B 是大小。B 不等于客户端 g 或最终对象长度 Lₒ。③ |
| O53 | `Shard s` | `Shard span s` → N55 | shard 是编码分片；span s 是一个完整 stripe 对应的分片跨度，不是整个对象 shard file 长度。③ |
| O54 | `q` | `Verify/read q` → N56 | q 是分片内校验/读取量子；verify/read 补足其类型。不是网络 GET、FUSE 请求、Packed frame 或客户端 g。③ |

## 新增与补充词语怎么读

这里只解释修订中新增的意思，不另造一套术语；大小写及斜杠与最终图一致。

| 新词／短语 | 对应新文字 | 精确含义 |
|---|---|---|
| **View** | N04、N06 | 完整的文件系统可见状态；下方条带仅展示该视图内文件范围的来源。 |
| **private writable upper** | N11 | private 属于指定工作区；writable 承接修改；upper 是优先解析的逻辑层，不是内存等级，也不等于“该字节已远端持久化”。 |
| **zeros** | N10 | Hole 覆盖的字节返回零，不是返回零字节或删除文件。 |
| **pinned reference** | N16 | 固定绑定一个基线身份；reference 表示引用关系，不追随每次更新的 latest。 |
| **Private**（payload） | N13 | payload 属于该工作区的私有新增数据，与 Δ 的元数据/映射记录分开。 |
| **snapshot** | N20 | 被固定表示的一版不可变记录及访问结构；不是整个源卷必然冻结，也不是单个对象。 |
| **mount** | N23 | 独立只读挂载入口，明确 Packed 可以不依赖 Δ 工作区使用。 |
| **Name-range index** | N24、N25 | 根据目录内 raw name 区间路由到组；不是按源目录树深度画出的路径树。 |
| **(parent, name)** | N28，新增独立标签 | parent 是父目录身份，name 是单个名称；括号/逗号表示组合键概念。实际实现用32字节 parent key拼接raw name。 |
| **Attrs** | N30 | 常用属性的复数简称。具体值由抽象线条表示，未填伪造的示例数值。 |
| **via descriptor** | N35，新增独立标签 | via 表示经由；descriptor 是已认证的 frame 描述符。Locator先解析frame/容器引用，再获得object offset、stored length等，随后访问payload。 |
| **fixed** | N38 | 当前挂载/卷声明的一套固定客户端 g 几何；两行是配置对比，不是在线控制。 |
| **Compress & frame** | N44、N45 | 客户端适用的压缩与成帧。&连接处理含义，不承诺每次都压缩成功；也不表示后端纠删码。 |
| **Final length** | N46 | 对象完成适用的压缩、头部和成帧后的上传字节长度。 |
| **Optional B hint** | N49 | 可选地向兼容后端建议编码块大小；后端仍可忽略或按准入规则选择。 |
| **Layout selection** | N48 | 后端根据默认值、资格、门控和允许的hint决定实际布局；q还有独立门控。 |
| **Persisted layout** | N53 | 对象写入后保留的解释规则；读取/修复使用该对象的布局，不用当前配置重解释旧对象。 |
| **EC block size** | N54 | 后端 erasure-coding 输入块的大小；不是客户端原始分块大小。 |
| **Shard span** | N55 | 一个完整编码stripe在单个shard上的逻辑跨度；不含整个对象的所有stripe长度。 |
| **Verify/read q** | N56 | 图中实际写法带斜杠；表示物理校验/读取量子，不是新增名为“Verify-read”的独立机制。 |

## 已落实的图形关系与未采纳的备选项

**已落实：** Δ₁/Δ₂ 的独立标签删除，通用 Δᵢ 定义保留；attrs省略号改为抽象线条；粗粒度行
只有一个真实尾段；最终对象改成一个完整对象配 Lₒ 标尺；hint虚线从长度标尺出发；U₁/Oₚ
保留各自入口，绕过普通上传器；q 标尺标在一个局部跨度，后续用连续省略图形，避免把旧五格
误读为普遍成立的 s=5q。没有通过扩大整幅图解决这些语义问题。

**未采纳、不可写成已做：** `Native catalog` 没有改为 Sealed catalog；`Locator` 没有改为
Data locator；Oₚ 没有改为 Packed object；没有增加独立 Frame descriptor 大框，而采用
`via descriptor`；没有把 attrs填成具体mode/size示例值；没有把 g 改称动态自适应粒度。
这些选择保留了短标签，同时通过相邻关系与图注补足必要边界。

## 最终图形验收记录

主任务提供的最终图形检查结果：画布仍为 **240 × 258 pt**；SVG 含 **73 个可编辑 text 节点**，
对应 **56 个逻辑标签**；PDF 内 **0 个光栅图像对象**。渲染字体范围 **5.2–8.5 pt**，其中下标
以单独可编辑小字显示。自动图形检查为 **0 fail、3 warn**：三处警告来自编号圆徽章和标题
合并后的包围盒，主任务已逐一目视确认。

论文实际页面放置也已由主任务确认：两个版本均为16页，系统图位于第5页，无 Overfull、
Missing glyph 或 undefined 引用。完整记录见 [最终图形与排版验收](qa-final.md)。这些检查
针对图形、术语与排版，不代表本轮进行了挂载、持久化或性能实验。

## 可机器核对的覆盖文件

[coverage.json](coverage.json) 保存 O01–O54 与 N01–N56 的逐出现映射、原/新字符串、位置、
处理方式及完整性检查。它特意保留重名对象的出现身份，防止把 `Packed` 或 `frame` 全局替换。
