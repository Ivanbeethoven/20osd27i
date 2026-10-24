# 机制②逐词技术审计：Packed Metadata

审计对象：`tools/draw_architecture_editable.py:144–183` 中的机制②。只读对照
`sections/03-overview.tex`、`05-packed.tex`、`07-implementation.tex` 与固定源码
`../brewfs-principles-242af5f/src/workspace_overlay/packed_v3/`。
未修改图片、图形生成代码或正文。

## 先修的三个问题

1. **`/h/y` 是明确的错误，不只是抽象层级欠佳。** `Name` 是单个目录项的原始名称字节，
   代码直接拒绝斜杠；应改成 `y`。父目录单独属于索引键/组上下文。
2. **`Index` 隐去了本机制最重要的组织方法。** 当前图只示意名称查询，应写为
   `Name-range index`（可分两行），其入口是 `(parent, name)`。不要让人以为这是全路径
   索引、目录树图，或所有查询都经过同一个索引。
3. **`Locator → Packed frame` 省略了有语义负担的间接寻址。** GroupMeta 中的 extent
   不保存完整 frame descriptor，也不是对象偏移；它包含 frame ordinal 和解码后 frame
   内的偏移。读数据时还要从已认证的 frame-directory 页取得 object offset、stored length、
   codec 与 digest。应保留 `Data locator`，并在到 payload 的路径上表示一次 descriptor
   解析，或明确将这条线定义为“经过描述符的引用”。不能把 Locator 改称 `Object offset`。

## 逐标签裁决

表中 `src/…` 均相对于固定源码根目录；`sections/…` 相对于当前论文根目录。

| 当前标签 | 决策与推荐图中文字 | 精确语义与纠错理由 | 证据 |
|---|---|---|---|
| **Packed Metadata** | **保留原名** | 是机制名称：冻结并组织不可变文件系统记录，通过索引和有界页面读取；不是只把若干属性字节压缩到一个包里。输出还包含访问结构和数据定位信息。 | `sections/05-packed.tex:6–11,25–36`；`sections/03-overview.tex:22` |
| **Native catalog** | **保留**；若需强调不可变性，可用 `Sealed catalog` | 在这里表示 workspace lower 使用原生 catalog layer 的替代表示。不是 Native P1、`native_base` 子系统，也不是给 S 接一个实时可变 catalog。图已有 `Shared immutable lower`，因此现名在该上下文成立；不要扩写成 `Native filesystem`。 | `sections/03-overview.tex:47–50`；`sections/07-implementation.tex:37–39,53–59`；`src/workspace_overlay/meta_layer/packed_lower.rs:230–234` 的 `WorkspaceLower::{Native,PackedV3}` |
| **Packed**（分支小框） | **替换：`Packed snapshot`**；可两行 | 裸词不能说明它是一个被固定绑定的不可变快照表示，容易与机制名、打包操作或压缩状态混淆。该框对应 native catalog 的替代 lower 记录表示，而不是“执行 Packed 动作”。若空间足够，完整词为 `Immutable packed snapshot`。 | `sections/05-packed.tex:8–19`；`sections/03-overview.tex:47–50` |
| **or** | **保留** | 是同一 baseline 的表示选择，不是每次查询随机回退，不是 native 与 packed 同时作为两个串行阶段。也不表示所有挂载入口均支持任意组合。 | `sections/05-packed.tex:13–20`；`sections/07-implementation.tex:18–20,37–42,53–59` |
| **Read-only** | **替换：`Read-only mount`** | 这是独立使用 packed snapshot 的入口/角色。单独形容词 Read-only 可能被误读为 index 或 page 的性质。加 mount 才体现“无需 Δ 的另一入口”；不能写 `Read-only workspace`，否则又把两机制耦合。 | `sections/05-packed.tex:13–16`；`sections/07-implementation.tex:40–42`；`src/workspace_overlay/packed_v3/readonly.rs:976–986,1004–1008` |
| **Index** | **替换：`Name-range index`**；完整技术词放图注为 `Directory-name index` | 本图画的是 lookup 路径的 GroupIndex：按 parent key + raw name 的范围路由到组。IP06 是通用索引页格式；还存在 InodeIndex、ContainerIndex、FrameIndex 等，不能用这一个节点暗示所有操作都走相同输入键。 | `sections/05-packed.tex:25–29,31–33,59–69`；`src/workspace_overlay/packed_v3/wire005/manifest.rs:591–612`；`wire005/index.rs:114–150,159–172` |
| **GroupMeta page** | **保留** | 一个有界、经过认证的联合记录页面，含目录项、常用属性与数据定位；不是一整个目录，也不等于一个物理对象。目录可以分多个组，容器也可放多个组。不要把它改成 `Metadata block`，避免混淆 B/q。 | `sections/05-packed.tex:31–37,59–64`；`src/workspace_overlay/packed_v3/meta.rs:26,47–70,167–170`；`wire005/container.rs:17–30` |
| **Name** | **保留：`Name`**（精确扩写可为 `Entry name`） | 只含单个 raw entry name，不含 parent，不含全路径。父目录由 GroupRef 的 `parent_dir_key` 表示，在索引层与名称组合。它不保证 UTF-8；图中 `y` 只是可读例子。 | `src/workspace_overlay/packed_v3/meta.rs:49–51,605–615`；`wire005/container.rs:17–22`；`wire005/manifest.rs:596–607` |
| **Attr.** | **保留：`Attr.`**；若宽度允许用 `Attrs` | 表示 common/hot attributes，不是所有扩展属性都内联于这个单元格。包括 kind/mode、uid/gid、rdev、nlink、timestamps、size；inode 也在 entry 中。`All attributes` 属于过度承诺。 | `sections/05-packed.tex:32–34,63–67`；`src/workspace_overlay/packed_v3/meta.rs:49–64` |
| **Locator** | **替换：`Data locator`** | 精炼但应指明所定位的是文件数据。对于所画的非内联 packed 路径，是 file extents → frame ordinal + raw range，结合 group/container 上下文解析 authenticated descriptor。它不是 descriptor 本身，也不是直接 object offset。小文件可 inline；其他 placement 可有独立索引，因此不能宣称每个 entry 都必有一个外部 frame。 | `sections/05-packed.tex:63–73`；`src/workspace_overlay/packed_v3/meta.rs:39–45,65–70`；`wire005/manifest.rs:1139–1168,1201–1289`；`group.rs:418–428` |
| **/h/y** | **必须替换：`y`** | 该示例放在 Name 单元格内，违反实际格式：`validate_name` 明确拒绝 `/`。若确实要表达 `/h/y`，只能把整个路径移到用户查询示意中，并分解为 parent=`/h`、name=`y`；图内更建议直接删除路径上下文。 | `src/workspace_overlay/packed_v3/meta.rs:605–615`，尤其 `606`；`wire005/manifest.rs:596–607` |
| **…**（Attr. 值） | **删除，或替换为小字 `mode,size` 作为字段示意** | 不是协议字段，只表示省略。它没有帮助解释 co-location；若需要该格承载信息，用真实字段名比省略号有意义。不要填未经定义的伪测量数值。若维持最精炼风格，可以仅保留表头与抽象记录形状。 | `src/workspace_overlay/packed_v3/meta.rs:54,63`；`sections/05-packed.tex:32–34` |
| **Object Oₚ** | **推荐替换：`Packed object`，下方同名连接端同步替换；若保留 Oₚ，必须继续定义** | `Object` 在这里是保存所示 frame 的物理容器对象，不能指整个 snapshot。`Oₚ` 不是论文正文既有模型符号或源码字段；当前只在新图和 overview 图注中被引入为匹配端口。因此它不是“完全未定义”，但确实是额外视觉记号，没有新的技术含义。不能把 p 当作 persisted、page、part 等未定义索引。 | `tools/draw_architecture_editable.py:162,220`；`sections/03-overview.tex:87–88` 是唯一定义；`sections/05-packed.tex:35–37`；`src/workspace_overlay/packed_v3/wire005/container.rs:17–30,502–521` |
| **Packed frame** | **保留**；`Data frame` 可作较短但不优先的替代 | 是 snapshot 级的数据访问、编码及完整性验证单位，不是 RustFS 的 coding block B，也不是分片读取量子 q。它有独立 descriptor，使用 object_offset/stored_len 定位 stored bytes，再验证和解码。一个 frame 不必对应一个文件；一个文件也可有多个 extents。 | `sections/05-packed.tex:69–73`；`src/workspace_overlay/packed_v3/group.rs:418–433`；`wire005/frame_directory.rs:21–29,47–56,147–210` |

## 五个必须核实的问题：结论

### 1. Index key 到底是什么？

当前 name lookup 的实际键为 `parent_dir_key || raw_name`。
`wire005/manifest.rs:596–600` 先验证 name，然后把 32-byte parent 与 name 拼接；
`602–610` 检查命中组的 parent 与 `[first_name,last_name]` 范围。
`wire005/index.rs:129–143` 又核对 index record 的 first/last key 是否等于
`group.parent_dir_key || first_name/last_name`。这不是把 `/h/y` 当作一个排序字符串。

parent key 通常由 snapshot identity 与 inode 派生：`catalog.rs:321–327`；root 使用
manifest 已保存的 root_dir_key：`readonly.rs:993–1000`。图无需画哈希细节，但 `(parent,name)`
应出现在入口或图注，且这一路最好限定为 lookup 示例。

### 2. Name 是否包含 parent？

不包含。`GroupMetaEntry` 只有 `name: Vec<u8>`；父目录位于 GroupRef 中。
所以 `Name=y` 正确；`Name=/h/y` 错误，不能靠“抽象示意”来解释。

### 3. Locator 是 frame descriptor 还是 object offset？

两者都不是。对于图示非内联路径，存储在 entry 的 `GroupMetaExtent` 是
`file_offset, logical_len, frame_ordinal, raw_offset, raw_len`（`meta.rs:39–45`）。
其中 `raw_offset` 是**解码后的 frame 内部**偏移，不是对象的字节偏移。

读取时会以 `(container_ordinal,frame_ordinal)` 查询 frame-directory index，读取经过认证的
descriptor 页（`manifest.rs:1596–1620`）；descriptor 才有 `object_offset,stored_len,codec,
frame_digest`（`group.rs:418–428`）。具体取数通过 `typed_exact(container.key,
frame.object_offset,frame.stored_len,...)`（`frame_directory.rs:190–210`）。

因此最小而正确的视觉关系应是：

`Data locator → Frame descriptor → Packed frame`。

可把 descriptor 表示成箭头上的小引用符号而不是又加大框；若完全省略它，图注必须明确这条
线是经过描述符的解析引用，而不是直接地址。当前图注“locators directly”描述 read-only
入口访问 joint records 尚可，但不能用来证明 locator 直接包含物理地址。

### 4. Oₚ 是否无端新增？

确实是新增的图例符号，而非机制的原有符号；不过当前 overview 图注第88行已经定义为
匹配端口，因此不是一个未定义变量。保留与否属于图复杂度取舍：推荐用 `Packed object`
匹配上下端口，少引入一个符号；若保留，写清 `p` 仅为 packed 示例对象标签，不能泛化为
“整个快照只对应一个对象”。

### 5. Packed 是否足以表达 immutable snapshot？

不足。机制标题已经叫 Packed Metadata，而分支节点需要名词指代其产物/表示。
`Packed snapshot` 是更合适的短标签；S 的 immutable 性质与 enclosing group 可以补齐
不可变语义。不要用 `Packed data`，因为所画集合主要是完整只读快照的元数据及访问结构。

## 文字以外但会影响文字真假的边界

- 当前大框把 index、GroupMeta 与 payload 包在一起，应解释为 **snapshot representation**，
  不是一个物理容器。索引和 descriptor 可以是独立对象；GroupMeta 是容器内 byte range。
  若大框被误读成单对象，改标签也不能修复。
- 图示是一条非内联文件 lookup/read 路径。`getattr` 可走 inode index、枚举有其他访问路径、
  inline 文件不需额外 frame（`sections/05-packed.tex:66–73`），无需全部画入主图，但不能
  让单一路径代表所有操作必经步骤。
- 当前图未体现 pinned manifest/authenticated references，这正是为何 index/page 可安全复用
  的技术边界。无需再加解释段落；可在 packed snapshot 标签旁加一个一致的 pin/immutable
  图形，或者把说明放现有图注。不要以 `Index` 一词代替这个身份/完整性边界。
- Native/Packed 是替代实现，Read-only mount 是另一使用入口，三者不能在图里被排成强制
  串行管线。

## 推荐最小词表

`Packed Metadata`；`Native catalog`；`Packed snapshot`；`or`；`Read-only mount`；
`Name-range index`；`GroupMeta page`；`Name`；`Attr.`；`Data locator`；`y`；
`Frame descriptor`（节点或引用标记）；`Packed object`；`Packed frame`。

这份词表只增加 descriptor 这一处会改变读路径解释的必要概念，删去伪全路径、省略号和
可选的 Oₚ 符号。更换名称时应同时更新图中匹配端口和 overview 图注，不要留下两套名称。
