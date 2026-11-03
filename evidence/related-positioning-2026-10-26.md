# Introduction / Related Work 定位核对

日期：2026-10-26。范围仅为两节的论述与写作准则；三个机制保持独立可选，沿用既有术语。以下是技术定位，不是已完成的系统性能比较。

原稿主要问题：相关工作多次转向公平测试要求和证据限制；引言列出机制，但未具体说明它们相对最近邻设计改变了什么。此次以“已有能力 → 具体表示/服务路径差异 → 代价”组织，保留必要边界，去掉独立的重复限制段。

| 比较对象及核对来源 | 原工作已有能力 | 本文定位及本地依据 |
|---|---|---|
| [OverlayFS](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html)，Upper and Lower / copy-up；[BranchFS](https://arxiv.org/html/2602.08199v2)，§3–4 | 分层隔离、删除标记；BranchFS 原型首次修改时复制整文件，并有提交/放弃生命周期 | 私有当前状态及数据区间映射保留未改区间；固定下层可为 native 或 packed。依据：04-delta。不能据此声称本地 fork 更快。 |
| [DeltaFS](https://www.pdl.cmu.edu/PDL-FTP/Storage/zheng-deltafs_sc21.pdf)，§2–4 | 私有命名空间、对象存储中的 SSTable 日志、按需选择/合并快照、作业内服务与压实 | 对比当前值 upper、目录名称组联合读取以及可选打包时机。依据：04-delta、05-packed。不能把对象元数据或移出集中服务的思想归为本文首创。 |
| [IndexFS](https://www.pdl.cmu.edu/PDL-FTP/FS/IndexFS-SC14.pdf)，摘要/设计；[InfiniFS](https://www.usenix.org/conference/fast22/presentation/lv)，作者摘要 | 分区、局部性、客户端缓存及批量插入；解耦目录元数据和并行路径解析 | Packed 将选定固定版本的支持查询转到对象页和客户端缓存；可变记录及控制状态保留。依据：05-packed。查询卸载不自动等于源记录回收。 |
| [CernVM-FS 2011](https://s3.cern.ch/inspire-prod-files-2/25b9bd0b973d4f8d47c8fd3ab8d2c5fc)，§2–5 | 面向海量小文件；嵌套 SQLite catalog、内容寻址、按需下载与缓存；发布也有成本 | 本文重点为按目录/名称范围组织的有界联合页、索引路由以及读取组与物理容器分离。依据：05-packed。不能写成此前不可变系统都要整树加载。 |
| [Nydus RAFS](https://nydus.dev/docs/concepts/rafs/)，High Level Data Structure / Lazy Loading / Integrity | 分离 metadata 与 chunked data blob，支持懒加载、缓存及完整性验证 | 以元数据访问单位、页中有用记录比例及发布成本展开；兼容 writable upper 的组合是直接替代方案。现有 JuiceFS 实验不能代替此比较。 |
| [JuiceFS](https://juicefs.com/docs/community/architecture/)，Architecture / How JuiceFS stores files | 元数据引擎保存名称、属性、数据映射等，文件内容存于对象存储 | 支持衡量固定版本查询卸载的外部基线；不能假设每次文件操作都产生一次远程数据库请求。 |
| [Okapi](https://www.usenix.org/system/files/osdi25-athlur.pdf)，摘要及 §1；[Morph](https://www.pdl.cmu.edu/ftp/Storage/Morph_Final.pdf)，摘要及 §1 | 分别解耦数据条带化与冗余分组、降低文件生命周期内冗余转换开销 | 本文区分客户端对象形成 g、后端编码 B、物理校验/读取 q，以最终对象长度提示后端并保留实际布局。依据：06-layout、07-implementation。当前 g 仍为配置，无在线自适应控制器。 |

其他保留引用按原文核对：[YoloFS](https://arxiv.org/html/2604.13536v5) 的 staging/snapshot/permission；[AgentFS 官方公告](https://turso.tech/blog/agentfs) 的 SQLite 文件、键值与工具记录；[LocoFS 作者稿](https://storage.cs.tsinghua.edu.cn/papers/sc17-locofs.pdf) 的元数据职责拆分；[Mantle 作者稿](https://madsys.cs.tsinghua.edu.cn/publication/mantle-efficient-hierarchical-metadata-management-for-cloud-object-storage-services/SOSP25-Li.pdf) 的层次对象元数据；[SwitchFS](https://arxiv.org/html/2410.08618v3) 的异步目录更新；[DADI](https://www.usenix.org/conference/atc20/presentation/li-huiba) 的按需块传输。论文与软件文档的身份沿用 references.bib，不把官方文档写成评审论文。

证据边界：技术差异来自已读原文及既有源码审计；八次运行仅为请求特征分析。DB 压力、首次 fork、复用回本、迁移与恢复、对象布局收益均等待 §8 实验，未新增结果或普遍领先结论。
