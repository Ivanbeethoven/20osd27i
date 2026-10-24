# 融合版架构图

三个技术点以包含关系和同一对象的表示自然连接：agent 私有视图引用一份共享 S；Packed Metadata 位于 S 内；S 中的 O1/O2 在下方分别展示保存的物理 B/q 布局。

- 最终画布 504 × 230 pt，Arial / Arial Bold 9.5–10.5 pt，与上一版相同。
- 34 个标签，62 个空白分隔单词；上一版为 41 个标签、78 个单词。
- 蓝色是共享 lower / packed frame，橙色是私有 payload，中性灰是物理编码/验证结构。
- 灰色无箭头投影表示同一对象，上下条带严格同 x、同宽；frame 与 B 的划分没有对齐。
- client B hint/admit 作为创建支路；read/repair 直接解释 stored layout。

## 文件

- `system-architecture-integrated.svg`：可编辑矢量和 live text。
- `system-architecture-integrated.pdf`：最终尺寸矢量 PDF。
- `system-architecture-integrated.png`：3× 预览。
- `system-architecture-integrated.caption.tex`：配套图注。
- `../tools/draw_architecture_integrated.py`：生成器，稳定图元 id。
- `../validation/architecture-integrated/figure-proof.pdf`：使用论文 USENIX 样式的一页排版样张。

此版直接重排上一版的原创矢量图元，没有再次调用 image_gen。早期构图探索的 image_gen 来源和提示词沿用 `system-architecture-mechanism.README.md` 记录。数据结构、标签、下标和图标均为确定性矢量，无光栅嵌入。

## 语义和使用

私有 Ui 不属于 S；Δ 在 mutable metadata service。S 是逻辑快照集合，metadata 页与 payload 不必属于同一物理对象。不同 B 图示为支持的固定配置，不是 auto-policy 运行结果。q inset 是一个完整 stripe 中的 shard，s=B1/d=2q1；其比例独立于上方 object 条带。资格、gates、hint 接线和 upper integrity 边界由图注保留。

这份图与图注可一起用于作者审阅；主论文仍引用原 architecture.tex 中的图。验证结果见 `../validation/architecture-integrated/review.md`。
