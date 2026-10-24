# 机制③逐词与图形语义审计

日期：2026-10-23。只读审计 `tools/draw_architecture_editable.py:183–233`
及其 PNG，核对根目录最新第 6、7 节和 BrewFS 固定源码
`242af5f7e9bba7afc0c61778f1084fcb20e083a0`。本报告不修改图、论文或系统代码。

本轮另用 GitHub connector 重新读取 RustFS 研究分支
`cc4926fac1107aee76540f28bf22dbd47fcbca24` 的三个原文件，确认后端
门控和几何；不是沿用未核验的上游假设：

- `crates/ecstore/src/object_api/ec_block_layout.rs`，blob
  `30d343c752854e0f8265e45fd2c7d8ebd10af381`。
- `crates/config/src/constants/object.rs`，blob
  `709053e8ca46ff86a883097942d0122255ef49a7`。
- `crates/ecstore/src/erasure/coding/erasure.rs`，blob
  `4548816e8504ae2893a916da2418374b12339f40`。

## 结论

标题正确，问题主要在压缩图形后丢掉的边界，而非术语表不完整。
需要修正的重点是：两个固定 g 的比较几何、客户端格式化与后端 EC
编码的区分、L_o 的“长度”含义，以及 B hint 与 q 的独立后端门控。
U₁/Oₚ 绕过普通 uploader 的关系应保留；它们进入同一存储服务不等于
这些 producer 已接入 hint，也不等于它们采用普通路径的 g。

## 逐标签判断

下表的 BrewFS 代码路径以只读快照根 `../brewfs-principles-242af5f/`
为基准；正文路径以当前论文根为基准。推荐语句是图中短标签，完整
限制应留在图注或正文，不把本表变成图内段落。

| 当前标签与图源行 | 逐词／符号的准确含义 | 处理 | 推荐最短措辞 | 证据及必要边界 |
|---|---|---|---|---|
| **Variable-Granularity Object Storage**，184 | Variable：可分别配置的粒度；Granularity：对象形成、编码及读取/校验的不同边界；Object：形成后的上传单位；Storage：对象保存及服务访问。不是在线自适应控制器的名称。 | **保留**，不要另造 dynamic/adaptive 标题。 | 原名原样保留。 | `sections/06-layout.tex:1,6–21,41–47,92–119`；`sections/07-implementation.tex:100–113`。g 为固定配置；h 当前为阈值规则。 |
| **Ordinary uploader · configured g**，185–186 | Ordinary：普通对象数据路径，用来和 Entity/快照 producer 区分；uploader：按 slice 内偏移及块索引形成上传对象；configured：卷/挂载声明的一套固定几何；g：客户端原始块目标大小，非对象最终长度、EC B 或 q。 | **保留路径限定，替换较弱的 configured**。仅有 ordinary 不能让初读者自动知道可独立用于 flat 卷。 | `Ordinary path · fixed g`；若需要图本身直接说清独立性，用 `Flat-volume example · fixed g`。 | `sections/06-layout.tex:6–12,25–32,41–47`；`sections/07-implementation.tex:34–36,100–105`；`src/cli.rs:397–447`；`src/config.rs:1271–1286`。后者标签明确是一个例子，不声称普通路径只服务 flat 卷。 |
| **Slice**，187–188 | Slice：chunk 内一个连续区间的内容及身份；不是整个 chunk、文件、一次 FUSE write，也不是对象本身。图内应表示 slice **数据**。 | **保留／轻微补全**。 | `Slice data`（空间不够保留 `Slice`）。 | `src/chunk/slice.rs:88–102`；`src/chunk/writer.rs:153–176`；`sections/06-layout.tex:25–32`。输入小图标的内部四分格没有额外语义，建议去掉。 |
| **g₁ / g₂**，189–193 | g：client block size；下标 1、2：两套备选的固定配置，不是同时存在的 per-object 动态决策，更不是第 1/2 个对象长度。 | **保留符号，改几何并表明二选一**。 | 两行仍为 `g₁`、`g₂`；分叉处加短 `or` 或 `fixed g` 已有的明确上下文。 | `sections/06-layout.tex:41–47`；`sections/07-implementation.tex:100–105`；`src/chunk/reader.rs:167–204`；`src/config.rs:1278–1286`。当前 reader 依赖声明的统一几何，没有在线选档。具体错误见下节。 |
| **tail**（两处），194–197 | 一个分割后最后不足 g 的真实数据块；不是补齐到 g 的空白、Hole 或零填充。 | **保留一次或各行保留；移到正确短块**。 | `tail`。 | `sections/06-layout.tex:29–32`；`src/chunk/writer.rs:161–176`；`src/chunk/store.rs:1049–1062`。客户端起始非零 offset 可以引入零前缀，和图示尾段不是同一含义。最后白格与① Hole 同色会误读，建议 tail 仍用数据填色。 |
| **Encode / frame**，200–203 | 这里实际是客户端压缩（如适用）及持久化头部/成帧；不是 RustFS 的 erasure coding。frame 是普通对象格式帧，亦非② Packed frame。 | **替换 Encode**。斜线目前含义也不明确。 | `Compress / frame`；极简可用 `Client format`，由正文定义包含可选压缩和成帧。 | `src/chunk/store.rs:1056–1062` 调用 `encode_persisted_block`；`src/chunk/compress.rs:88–112,133–147` 明确无压缩/不可压缩时仍成帧；`sections/06-layout.tex:14–21,29–31`。Compress 不应解释为必然压缩成功或缩小字节数。 |
| **Objects Lₒ**，204–208 | Objects 是实体；L 是 length；下标 o 指某个对象的最终上传表示。L_o 是适用压缩、头部和成帧之后的 byte 长度，不是对象名或对象集合。 | **替换并分离实体和属性**。 | 图标旁 `Objects`；在一对象的长度标尺旁 `Length Lₒ`。如只能留一标签，用 `Final length Lₒ`，但必须让标尺指向一个完整对象。 | `sections/06-layout.tex:14–18,29–31,94–101`；`src/chunk/store.rs:1057–1063`；`src/cadapter/s3.rs:25–26,734–735,942–945`。当前把 Lₒ 接在 Objects 后面确实容易当作对象标识，与 Oₚ 混淆。 |
| **B hint h(Lₒ)**，213–215 | B：EC 编码块大小；hint：客户端请求值，可被忽略；h：配置选定的可选策略，不保证返回值；L_o：**已完成对象**长度。不是客户端赋值 `B=h(L_o)`，也不是 q hint。 | **保留，控制线移至明确的最终长度来源**。 | `B hint h(Lₒ)`。 | `sections/06-layout.tex:94–108`；`src/cadapter/s3.rs:62–89,118–122,734–735,942–945`；RustFS `ec_block_layout.rs:176–229`。fixed 返回常数，auto 仅当 L_o>1 MiB 发 B=1 MiB；当前默认 B 也为 1 MiB。 |
| **optional**，216 | 可不配置、不发送 hint；不是说必须选择机制①/②后才可使用③，也不是 hint 有/无能够代表 q 开/关。 | **保留但并入提示标签**，删独立重复行可节省空间。 | `Optional B hint` + `h(Lₒ)`，或保留上行原标签并在图注解释虚线。 | `sections/06-layout.tex:6–12,94–108,137–145`；`sections/07-implementation.tex:107–113`；`src/cadapter/s3.rs:125–138`。q 具有单独的 enable/fleet gates。 |
| **U₁**，217–218、221 | U：私有上层 payload 对象/对象集合的示例引用；下标1对应①的第一个 workspace，不代表 ordinary block index。 | **保留符号和绕过 ordinary uploader 的位置**。 | `U₁`（继续与①同名）。 | `sections/06-layout.tex:137–142`；`sections/07-implementation.tex:116–123`；`src/cli/entity_mount.rs:35–48`；`src/workspace_overlay/entity/data.rs:400–443`；`src/cadapter/s3.rs:1191–1218`。Entity 按写入段直接上传，默认无 hint，strict durable create-only 不附 hint；不能画出 U₁→h(L_o) 接线。 |
| **Oₚ**，219–220、222 | O：对象；p：packed 来源，匹配②的 packed payload object，而非客户端 g 的第 p 个块，也不是 parity shard。 | **保留引用端口**；不要接到普通 g 分块器或 hint 线。 | `Oₚ`。 | `sections/06-layout.tex:79–82,137–142`；`sections/07-implementation.tex:116–120`；`src/bin/packed_v3_snapshot_fixture.rs:918–927` 使用默认 S3Config。图可以表达其存入同一兼容服务，但不能表达已接入 ordinary hint 路径。 |
| **RustFS**，209–210 | 这里是固定研究分支中的兼容对象后端，并非所有上游 RustFS/S3 服务的固有能力；B/q 的准入与选择权在服务端。 | **保留名称，补研究范围**。 | `RustFS backend`；研究限定可放图注，若脱离图注传播则 `RustFS (research)`。 | `sections/06-layout.tex:94–101`；`sections/07-implementation.tex:9–17,107–113`；`evidence/principles-code/objects.md:3,46–55`。 |
| **default / hinted**，211 | default 应指后端默认 B/既有 framing；hinted 若仅指“收到请求”则不等于有效值，若指“采用 hint”则漏掉被忽略路径。该二分还错误压扁了 B 与 q 的独立状态。 | **替换，不能用两个词概括最终布局**。 | 后端副标签用 `Layout selection`；以独立小标签 `B gate`、`q gate` 表达两条准入，或把独立性移到图注。 | RustFS `ec_block_layout.rs:176–229,235–290`；`constants/object.rs:130–155`；`sections/06-layout.tex:98–119`；`sections/07-implementation.tex:109–113`。hint 被忽略可仍是默认 B；q 可独立开启，B 改变也不推出 q 变小。 |
| **Stored (B, q)**，223–224 | Stored：落盘对象几何并在后续读取/修复时使用；B 是 persisted erasure 字段；q 新格式有内部 marker，旧格式 marker 缺省并按旧布局解释。括号不应暗示所有对象都物理保存同一对显式元数据字段。 | **建议替换为持久化布局名**；保留 B、q 在内部几何标签中即可。 | `Persisted layout`。 | RustFS `ec_block_layout.rs:1–7,35–39,293–324`；`sections/06-layout.tex:116–119`；`sections/07-implementation.tex:112–113`。没有 q marker 不代表没有校验粒度，也不能套用当前新写配置解释旧对象。 |
| **EC block B**，225 | EC：erasure coding；block：一次编码的逻辑输入块；B：该块大小。和客户端原始 block g 是不同层。 | **保留**。 | `EC block B`。 | `sections/06-layout.tex:14–21,94–108,110–119`；RustFS `ec_block_layout.rs:12–16,176–229`。不要把 B 标在普通 uploader 的 raw block 上，也不要声称 B=L_o 或 B=g。 |
| **Shard s**，226、228–229 | Shard 是编码后的一个分片；s 在论文中专指**一个完整 stripe 对应的逻辑 shard 尺寸**，不是整个对象的 shard file 长度，也不含 bitrot/checksum 字节。 | **轻微替换或在图注限定**。 | `Shard span s`（图注说明 one full stripe）；若保留 `Shard s`，必须保留该限定。 | `sections/06-layout.tex:110–119`；RustFS `erasure.rs:1077–1105` 区分 shard_size 与 shard_file_size，尾 stripe 另算。不要未经条件化写 `s=B/d`。 |
| **q**，230–232 | 小写 q：单 shard 内的物理校验／读取量子，受新 framing 资格和几何约束；不是网络 GET 大小、FUSE 请求大小、Packed frame 或 g。当前 q 标注仅一个字母，语义在图本身不足。 | **保留符号，补两三个词的类型名**。 | `Verify/read q`，或两行 `Read quantum` / `q` 并在图注写 verification。 | `sections/06-layout.tex:17–21,110–133`；RustFS `ec_block_layout.rs:235–290,293–324`。q 的决策在后端，不由 h(L_o) 直接返回；小 q 会增加 checksum/framing 开销，不能单向标为“优化”。 |

## raw strips：总量相同，但 g₂ 分割不成立

图源 `:192` 为 `[10,10,10,5]`，`:193` 为 `[20,10,5]`。
`strip()` 在 `:102–106` 按各宽度直接相邻拼接，不额外加 gap。
因此两行总可视长度都是 35；**没有“总字节数不等”的错误**。
但第二行若代表固定 g₂=20，一段从 0 对齐、总长35的连续 slice 应为
`[20,15]`，不是 `[20,10,5]`。现图在一个 tail 前另造了一个短块，
无法由所展示的单一 slice、单一 fixed g 推导；没有画 flush/不同 slice
边界时，不能用未显示的条件替它辩护。

建议最小修正：保留同长 35，第一行 `[10,10,10,5]`，第二行 `[20,15]`，
分别标 g₁、g₂，尾段仍有数据填色。这样同量数据、不同固定分块、
对象数变化和短尾全部可见，不需要增加图内说明。也可改为论文的
10 MiB 示例：固定 g₁=2 MiB 对应 2+2+2+2+2，g₂=4 MiB 对应4+4+2。
不要把这些候选例子画成 runtime controller。

输入 Slice 当前为 `[5,5,5,4]` 总长19（`:188`），不与输出35共比例。
若只是小图标，其尺寸可独立；但四格会使读者以为它已按另一种粒度分块。
建议改成单块未分段输入，或直接用两行等长、相同端点表示同一输入范围。

右边“Objects”目前是 `[10,10,7]` 和 `[10,6]`（`:206–207`），数量也不
对应左侧分块。若每一格表示一个对象，压缩/成帧不会把四个 raw block
合并成三个对象：`src/chunk/writer.rs:166–174` 每 span 发出一个
`write_fresh_vectored`。若每格只是对象内的 header/payload 边界，又缺少
定义。建议画**一个带长度标尺的最终对象示意**，不要用无语义分格暗示
对象数；或者让两个配置的最终对象数量逐一对应各自 raw blocks。

## B、q 和连接语义的最小改法

1. `Slice → fixed g → Compress/frame → Object` 是 ordinary client 数据路径。
   L_o 标在最终对象的字节长度上；它不是对象名字。
2. 仅从 finalized length 引出可选 `B hint h(L_o)` 虚线，终点为后端
   **B admission**。不把 hint 箭头直接连到 q 或输出 `(B,q)`，不写赋值等式。
3. 后端 q 新 framing 有独立 enable/fleet-confirmed gates。B hint 的两个
   gates 与 q 的两个 gates 在固定分支都默认 false。建议后端内用简短
   `B gate` / `q gate`，图注一句交代 independent gates；不要增加整段解释。
4. U₁/Oₚ 两条实线绕过 ordinary block formation 是正确的抽象，继续保留。
   当前图的 hint 虚线起点在最终对象下方且紧贴这两个端口，容易看成它们
   的公共 hint 通道；应移开并从 L_o 标尺明确引出。
5. object → EC block B → one-stripe shard s → q 才是包含关系。
   目前五等分的 shard 图（`:229`）若被当作 s=5q 的具体几何，并不代表
   当前选择器的通用结果。换成**两格**即可对应已存在的合法示意，
   如 B=64 KiB,d=2,s=32 KiB,q=16 KiB，或 B=4 MiB,d=2,s=2 MiB,q=1 MiB。
   不必把这些示例数值加进主图；不要把示意格数误写成实际所有布局比例。
6. 读和修复使用 persisted layout；当前写设置改变不重编码既有对象。
   这是 `Persisted layout` 的用途，单独写 `Stored` 很难表达这一技术点。

## 重要性排序与可压缩空间

- **必须修**：g₂ 的两个短块；L_o 作为对象标签；Encode 的层次歧义；
  default/hinted 二分遗漏 admission 和独立 q；任何把 U₁/Oₚ 接入 hint 的读法。
- **应修**：白色 tail 与 Hole 冲突；最终对象分格的计数歧义；q 缺类型名；
  Shard s 未限定完整 stripe；五格示意可能诱发固定比例理解。
- **可省字**：optional 并入 hint 标签；Stored tuple 改 Persisted layout，
  B、q 只各出现一次；tail 可使用一个共享图例；不要在图中重复 auto 的阈值。
- **无需改**：三项核心机制名；g、L_o、B、q 的不同字母；U₁/Oₚ 分别作为
  上两部分的对应端口；backend 才决定最终 B/q 的总体方向。

本轮只产生审计报告，未改生成脚本、SVG/PNG/PDF 或正文，也未运行系统实验。
