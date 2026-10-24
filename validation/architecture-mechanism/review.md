# 机制图审核

日期：2026-10-23。

## 设计与技术核验

- 两个 agent 是外部工作区使用者；没有添加 agent 通信、调度器或安全沙箱主张。
- 对齐的 Range map 明示 S/Ui 引用。S 是显式 LowerRange；Ui 是分开的私有 payload。Δ 是当前元数据与映射状态，驻留位置由图注交代。
- 共享 snapshot 内的联合记录直接定位一个 frame；只展示代表性 name 访问，完整图注保留其他索引与 upper 完整对象校验边界。
- 灰线从 O1 整体外框走到右侧 O1 行的高度，避免把单个 packed frame 与 q 等同。图注明确灰线为同一对象的存储表示。
- 右侧 O1/O2 以 4 B1 / 1 B2 展示支持的不同固定配置，caption 指明等字节域、非自动策略输出。
- q inset 标为 Stripe shard，s=B1/d=2q1；不会将一个 stripe 内的 shard 单元误叫整个对象 shard 长度。
- hint 按已配置策略在 finalization 处请求，后端 admission/persistence；Read/repair 指向 stored layout。没有将读取画成重新选布局。
- smaller-q 的对象资格与两个 default-off gates、Entity/producer 接线缺口、frame≠q 均保留在图注。

核对来源：paper §§1、3–6，evidence/source_evidence.md，以及当前 checkout 的 entity/data.rs、resolver.rs、packed_lower.rs 和 cadapter/s3.rs。动态布局与论文图形两个子代理分别审阅，并采纳 Stripe shard、Range map、O1 连接路由三项修正。

## 渲染与检查

- 最终尺寸：504 × 230 pt，与上一版相同。
- 字号：9.5–10.5 pt，PDF text audit 无低于阈值文本。
- SVG audit 无 FAIL；仅预设 Nature 89/183 mm 尺寸提示。当前图为 USENIX 7 in / 177.8 mm，属于有意的不同版心。
- 最终 collision audit：0 FAIL、0 WARN。36 个文本处于填充框内是有意标签，详见 collision.json。
- 两个 workspace 的宽高、地图行高和区间坐标一致；右侧两对象条带等宽。Shard 为独立放大结构，无跨尺度比较含义。几何与例外保存在 scene.json。
- XeLaTeX 使用论文的 usenix2019_v3_xetex 样式编译一页 proof，已渲染检查。图与图注不溢出。
- 最终图已在完整尺寸预览和论文排版样张中检查。字体缺失的 Unicode 数字下标已改为真实数字的定位文本，无方框占位符。

生成依赖曾在执行期间失去 pymupdf/svglib 模块；重新安装后重新生成全部输出并重新执行最终检查。最后审核针对重新生成的 PDF。

## 来源与可编辑性

AI 来源与完整提示词见 paper/figures/system-architecture-mechanism.README.md。最终 SVG/PDF 使用原创、确定性矢量图元，无光栅嵌入；提交政策资格未作为此次内部设计审核结论。
