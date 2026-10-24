# Figure 2：小尺寸架构图的视觉编码建议

日期：2026-10-23。只读检查当前 `figures/system-architecture-editable.png` 和 `tools/draw_architecture_editable.py:113–242`。以下建议沿用已完成的逐词审计，不重新命名机制，也不扩充实现主张；本次未修改图片、绘图代码或论文。

## 最值得做的三个变化

### 1. 让颜色表示数据归属，不表示“这个框需要好看”

当前橙色同时用于私有 U₁ 和 Packed object Oₚ、locator、frame，因此读者无法从①追踪到②③时判断橙色究竟表示私有还是 payload。建议统一以下编码：

| 语义 | 建议颜色 | 应覆盖的元素 |
|---|---|---|
| 工作区私有状态与 payload | 克制的橙色边线／浅橙底，例如 `#B65D25` / `#F9E9DC` | Δᵢ 标签或小节点、Data 范围、Data→U₁、U₁ 对象与③匹配端口及其入后端线。 |
| 共享不可变来源与其访问结构 | 同一蓝色谱，例如 `#356A9A` / `#E8F1F8` | LowerRange、S、pinned reference、Native catalog、Packed snapshot、index、GroupMeta 的选中行、locator、Object Oₚ、Packed frame、③ Oₚ 端口。 |
| 普通客户端对象形成 | 中性灰边线／白底 | Slice、g₁/g₂ 分块、普通 upload 容器、Compress & frame、L_o 对象。普通对象不必属于共享 S，避免继续用“shared blue”标成同一归属。 |
| 后端解释与持久布局 | 灰青，例如 `#4E737A` / `#EEF3F3` | RustFS、backend-side hints、B/s/q 和持久布局；不是另一类 workspace。 |

两个 agent 图标都用深墨色，避免当前第二个 agent 的灰青与后端色发生意外对应。三个机制编号和标题保持统一深墨色，不按机制分三种强色，否则会与上述归属编码竞争。普通正文可用 `#243447`，背景保持白色，大面积卡片底色尽量减少。

Native catalog 可以用灰底、蓝边，与 Packed 分支同属 shared-lower 的替代表示；图中的 `or` 保留。蓝色不是“已经使用 Packed”的同义词。所有关系仍有文字、形状和位置依据，不能只依赖颜色区分。

### 2. ①用最短的主线表达 upper-first，而不是让公式悬在空白中

目前①的关键原理由一行公式承担，Δ 的完整名称和公式没有图形联系，视觉上反而是大 S 框最突出。建议把现有 Δ 标签与 Resolve 公式作为一个紧凑的解析单元：

- Δᵢ 用橙色短连线进入 Resolve 区，作为最近、最醒目的输入。
- 在 Resolve 旁用极短操作标签 **`upper first`**，无需增加解释段。
- S 仍通过蓝色 pinned reference 关联继承来源，保留无方向固定引用的表达；不可画成向 S 写入。
- W₁/W₂ 及 file-range 条带继续表达结果视图。Data→U₁、LowerRange→S、Hole→zeros 的局部对应关系保留，不将全部 W 重新等同 Δ。

这里不建议画一个简单 `miss → S` 的无条件回退菱形：whiteout 以及适用的下层继承阻断会终止解析，只有许可的 absence 才能回退。`upper first` 是准确的优先规则，不声称每次私有检查都访问后端或每个缓存命中仍完成整条路径。依据 `sections/04-delta.tex:22–38`、`03-overview.tex:53–58`。

若空间不足以加入连线，至少把公式中的 Δᵢ 标橙、S 标蓝，并让 Δ 的定义紧邻其输入；不应为新连线牺牲字体或重新引入跨整图的长线。

### 3. ②突出“一页联合记录”，③突出“两个决定时刻”

②的原理可以用一个连续焦点表达：**选中的索引页 → 同一 GroupMeta 页内的一整行 Name / Attrs / Locator → Oₚ 内的 frame**。目前索引是三个相同格子，唯一强色却是 locator/frame，因此看不出前两类记录与 locator 是一起取得的。

- 索引保留少量页形或分段，单独高亮被选中的一页；其余淡化，不画固定两级树或固定 GET 次数。
- GroupMeta 的 Name/Attrs/Locator 所属同一行使用一条淡蓝底色，保留三个列标题和边线。这能表达 joint records，避免只突出 locator 一格。
- 索引、选中整行、locator/frame 的线用相同蓝色；对象外框与 frame 内框仍要分开。
- 只读入口和 native/packed 替代分支保留；它们是可组合性的重要信息，不作为装饰删掉。

③建议用对齐而非更多文字区分两个时刻：

1. 普通上传一条中性主线：**fixed g → Compress & frame → 最终对象及 L_o**。
2. 后端一条灰青主线：**RustFS Layout selection → Persisted layout / B → shard span s → q**。

Optional B hint h(L_o) 从最终长度的位置分出，继续用虚线，只进入后端选择。U₁ 与 Oₚ 以橙／蓝匹配端口进入后端，保持绕开 ordinary fixed-g 形成路径；不要为让主线“更顺”把三种 producer 都强行并入同一个 uploader。当前代码对 Entity、Packed hints 的接线限制仍须由原图注及实现章承担，视觉整合不能变成全部路径已集成的主张。

## 可以交给图形承担的少量文字

| 当前文字 | 可压缩方法 | 不丢义的条件 |
|---|---|---|
| 两处 `tail` | 改为一个共用 `tail`，两条短引线分别指向两个末段。 | 每行仍清楚只有一个短末段；g₁/g₂ 的分块总长不变。 |
| `Final length L_o` | 用尺寸括号直接标 `L_o`；Final length 的词可省。 | 括号跨的是压缩／成帧后的单个对象，仍位于可选 hint 的来源处；原图注已定义 finalized upload length。 |
| 索引多页的重复小文字（若要新增） | 用后叠的页形、一个选中页或分段高亮。 | 不给页形标 1/2/3 次请求，不暗示索引固定高度。 |
| 当前 attribute 单元中的无文字值线 | 保留为短横线，不新增示例属性串。 | `Attrs` 列名保留，整行高亮表达联合取得。 |

不建议仅靠图标或颜色替代 `private writable upper`、`pinned reference`、`Read-only mount`、`via descriptor`、`Optional B hint`，或删掉 B/s/q 的不同层次名称。这些词承担真实契约；锁头、闪电或齿轮无法准确区分固定身份、认证、持久化和可选策略。

缩小纸面占用应优先压缩重复标签、外层圆角卡片和空白，保持现有正文级文字尺寸；不要通过整张等比缩小重新使技术名词不可读。以上变化不需要增加图注段落或新实验结论。
