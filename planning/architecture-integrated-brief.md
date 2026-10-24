# 融合版系统图

用户接受机制版方向，要求将共享快照、Packed Metadata、dynamic block size 自然融合，保留大字号与简洁风格。

采用一个纵向关系图，504 × 230 pt，文字仍为 Arial 9.5–10.5 pt：

1. 顶部两个 agent 与各自 Resolve(S,Δ) / range map。私有 U 均留在 S 外；显式 S 引用落到同一个共享边界。
2. 中间一整条 Shared snapshot S，Packed metadata 联合记录通过 locator 定位 O1 的 frame；O2 也属于这个快照。记录页与数据对象不是强制同一个物理对象。
3. 下方 RustFS 的 O1/O2 编码条带与上方对象严格同宽、同横坐标。无箭头灰色边线表达同一对象的两种表示；B 的分割与上方 frame 分割不对齐。O1 下仅展开一个 full-stripe shard 的 s=B1/d、两个 q1 单元。
4. finalized L → B hint → admit 为下方边缘的构建支路；只 hint 用虚线。read/repair 直接指向已存布局，不经过 hint/admit。

三个技术点通过包含关系和对象身份融合。它们不组成每次请求固定经历的三级流水线。固定布局示意不是当前 auto-policy 的运行结果。q 与 packed frame 不同；smaller-q 的资格与默认关闭的 gates、待补 hint 接线、upper 完整对象校验放在图注。

沿用已经核验的论文 §§3–6、Entity resolver/data/packed_lower 与 S3 adapter 证据。两个子代理分别审阅表示关系、生命周期路径和图形结构。最终图由既有原创 SVG 生成器重排，无需再次调用 image_gen。
