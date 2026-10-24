# 机制抽象版系统图

用户希望保留论文技术思路，提高抽象层级，并在入口加入少量 agent 图标；随后指出只有概念框过于简单。因此采用“一个整体关系、三个最小机制结构”，保持 504 × 230 pt 和 9.5–10.5 pt 字号。

核心论点：各 agent 以私有当前态解析同一个 pinned lower；共享 lower 将名字、属性和数据位置组织在一起；对象的物理布局在完成上传对象后被确定并持久保存，后续读取和修复使用保存的布局。

1. 两个 agent 仅是外部使用者。图标为 14 pt 原创线稿，不表示调度、协作通信或安全隔离。各自的 W = Resolve(S, Δ) 包含同一坐标下的示意映射，S 是显式 LowerRange，U 是 Data 引用。私有 payload 与映射分开，两个蓝色引用落到同一个 S。
2. 一个共享 S 内的联合记录 name | attrs | locator 指向对象 O₁ 中一个 frame。它是代表性名称访问；其他索引/直达 frame 访问不在主图枚举。Packed 的重点是共同组织与定位，不是格式版本。
3. O₁ 的整体外框连接其存储表示。Finalized O₁ 的 B hint 用虚线进入 RustFS 的 admit/persist。两条 O₁/O₂ 编码条带展示不同的 per-object 配置；一个代表性 O₁ shard 以 s=B₁/d 和 q₁ 子格表示不同物理尺度。它们是支持的配置示意，不是 auto 的输出或运行时重调。Read/repair 指向 stored layout，不回到 hint。

颜色：淡蓝 inherited/shared，淡橙 private，后端几何中性灰。全部标签深色；B/q 面板不沿用蓝色 frame 以避免等同。无阴影、渐变、3D 或未测性能值。

证据：sections/01-introduction.tex、03-overview.tex、04-delta.tex、05-packed.tex、06-layout.tex；../brewfs-upstream/src/workspace_overlay/entity/{resolver,data,packed_lower}.rs；../brewfs-upstream/src/cadapter/s3.rs；evidence/source_evidence.md。子代理复核了当前态解析、GroupMeta 和 layout admission/read-repair 边界。

技术边界放图注：Δ 在 mutable metadata service，U 在 object storage；upper whole-object verify 后切片；Hole/whiteout 等未展开；frame≠q；hint integration gaps；smaller q 仅 eligible new objects 且两个 default-off gates 开启。示意不声称完整运行集成或性能增益。

与参考论文的关系：采用 Oxbow 的有语义边界、Umap 的同构局部差异、CoPilotIO 的少量可追踪结构。保留各自的原始图作比较，不复制源图元。AI 抽象概念用于构图探索；用户指出技术过简后，确定性矢量版本补回三个机制结构。
