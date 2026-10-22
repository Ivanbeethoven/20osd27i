# 面向论文的代码就绪门与可证伪实验建议

此文件是基于固定提交静态审阅的后续实验建议，不包含新实验结果，也不表示已部署环境。源码和主张边界见 `source_evidence.md`；具体事实的固定提交链接见 `implementation_inventory.csv`。

## G0：冻结研究对象，避免用多个原型拼出一个不存在的系统

推荐把 `workspace-entity-v1 + packed-v3 + RustFS cc4926f` 明确设为论文研究原型。第一阶段只研究 fresh workspaces、单一写租约、同一精确 immutable lower 的多个私有视图。不要在本稿主张旧卷在线迁移、多写者共享上层、跨工作区事务、完整 POSIX 或生产 crash-takeover。

实现前置工作应形成一张门禁表，每项带代码 SHA 和自包含验证证据：

1. Entity mount 显式向 S3Config 传递逐对象 hint，且 strict conditional durable PUT 请求本身必须补 hint header；snapshot producer 明确支持构建期 hint。普通 CLI 有该参数不等于实验入口已经应用。当前 EntityFuse 最大 write 1 MiB，upper 逐次原样上传，因此 auto 的 >1 MiB 阈值不会触发；固定 B 另组，或把此路径作为 no-effect 控制。跨压缩阈值试验只用于实际有编码/压缩的上传入口。
2. 将 B 策略、完整对象读取偏好、LRU/默认准入拆为可单独控制的研究变量，或在独立 S3 台架上固定客户端策略。现有 hint 开关不能直接作为“只改变 B”的消融。
3. 实际上传记录至少包含 object key hash、最终 bytes、请求 hint、有效 B、实际 q/legacy framing、inline、d/p、PUT/MPU、checksum/protected 模式。明确 q-on但实际q不变的样本。
4. 关联 FUSE operation → upper/lower source → object request → RustFS shard I/O，验证受测请求经过期望路径。
5. 在所选 mount 路径上完成数据/命名空间 oracle 和至少核心故障点。源仓库的测试文件存在只证明可测试性，不能代替本次执行。
6. 明确 fresh-create、reopen/resume、discard、crash takeover、publish/reclaim 的支持矩阵。当前 Entity wrapper 仅 fresh-only；缺失 wrapper 的连续生命周期/恢复测量须等待新增实现，fresh scope/bucket teardown 不能充当恢复或生产 GC。
7. D0/P0/P1/C 等同路径控制需要研究适配器，不能由切换 volume-format 伪装。普通 VFS 写预算释放与 shared reply 没有 hint gate，固定一致即可；Entity 不使用这两个路径。
8. Entity 完整 readdir 上限 4096 条且有 4 MiB retained byte bound；100,000 fanout 用 standalone Packed reader，或先新增 Entity 分页。当前 wire005 readonly payload cache/prefetch 必须为零，cache sweeps 分开 metadata/payload/backend 层。
9. q 对象需以相同内容和长度分别创建成 legacy/selector 两组，布局持久化后再做客户端 C 因子。四服务器各一 drive 不触发全本地 batch-pread；单服务器四独立 drive 与分布式台架分别验证。

只有通过后才开始“完整 BrewFS”主结果。门未完成时仍可完成单机制 microbenchmark，但需要按路径分别命名。

## G1：工作负载画像必须解释为什么需要三项机制

独立真实 Agent pilot 与确定性 replay，不混入速度对比。恢复 DSH 0.1.5-rc.1 / deepseek-v4-flash 的原始 task IDs、输入代码版本、会话配置、成功/失败运行、FUSE events 和采样层说明。保留其实际名称，不把模型改名成未运行的版本。

至少测量：

- 每任务与每阶段的 lookup/getattr/readdir/open/read/write/fsync/rename/unlink 数量；以操作数和字节数分别归一化。
- 文件大小、FUSE 请求大小、对象最终上传大小三个不同分布；API层请求和内核FUSE事件不是一一对应。
- 首次访问/重复访问、读取字节覆盖率、目录访问局部性；基线 bytes 与每工作区 changed bytes/changed entities 比例。
- 同一基线下多个任务的共享文件集合；跨工作区共享率以唯一文件/唯一字节分别统计，不能从共享依赖名称直接断言缓存命中。
- I/O等待对 task critical path 的比例；包含模型推理、工具调用、编译和测试时的整体时间拆分，避免将累计多线程等待相加当 wall time。

若 I/O 占 task wall time 很小，论文仍可研究工作区创建、成本、尾延迟与吞吐，但不能将较大的纯I/O加速外推为同等 Agent task 加速。

## G2：Delta 工作区的核心实验

**问题：**共享 immutable base + 私有当前状态是否使创建/修改成本随变化量而非整个基线规模增长？

**条件：**基线文件数 10^4/10^5/10^6；文件字节量分开固定或扫描；workspaces 1/8/32/64/128；mutation fraction 0/0.1/1/10/50/100%；写集合重叠与独立目录分别设置。256 active owner bound 以内先测量，超过范围作为实现扩展而不是默认能力。

**对照：**在同一引擎中实现 eager materialized upper（如可行）对比 pinned lower + sparse upper；外部系统再用 local filesystem full copy、reflink/copy-on-write、OverlayFS 类目录共享和分布式文件系统 baseline。Git worktree 可作开发工作区参考，但 `.git` 共享与依赖复制策略必须明确。跨引擎结果不得称为纯 Delta 因果消融。

**度量：**初始化全时长、首次可用时间、首个文件访问时延、metadata rows/bytes、远端独占bytes、总共享bytes、首次写入copy-up的读/写bytes、每次rename/unlink/truncate的RTT、碎片span数、同目录/同inode冲突、workspaces并发创建的p95/p99。共享基线准备成本单列，并报告摊销到不同workspaces数量后的总成本。

**否证条件：**元数据复制虽然减少但首次读取/owner管理抵消收益；高 mutation fraction 时 map 替换与碎片化更贵；write-through小对象使吞吐明显恶化。均应保留并解释。

## G3：Packed 元数据必须分清减少了哪类操作

**问题：**目录访问关系驱动的元数据联合布局，是否在相同语义下消除 immutable-base per-file KV 查询，并降低总远端开销？

**受控序列：**exists/lookup、stat-only、readdir、readdir+stat、open+small-read、完整文件读、random seek、深目录walk、超大单目录与tiny-directory混合。raw byte names、hardlinks、ACL/xattrs/symlinks、稀疏文件用于语义验证；不把全部都混进主吞吐分布而掩盖主要机制。

**分层比较：**metadata 分散与联合布局；相同 data layout 下 metadata-only 优化；inline on/off；相同 frame/codec 的 data copack on/off；metadata cache冷/热。若某个格式组合当前不能运行，要实现匹配对照或改成独立实验，不能假称已有2^3全因子配置。

**关键指标：**lower KV commands、upper/control KV commands、HTTP API calls与SDK retries、manifest/index/GroupMeta/descriptor/data payload 的GET次数与received bytes、raw decode bytes、TTFB、文件/目录操作p50/p95/p99、RSS峰值、cache budget、深cookie跳转。证明lower zero-KV时不要把control-plane请求漏计成全系统zero-KV。

**成本：**capture/build/hash/upload/verify/manifest-publish 分段时长；索引与hot metadata总bytes；对象数、GET和PUT成本；临时磁盘、内存峰值；新快照建立成本及复用workspaces的break-even。

## G4：B/q 的实验必须先在对象存储台架得到干净因果

### 当前代码能执行的合法变量

- B ∈ {64 KiB, 256 KiB, 1 MiB, 4 MiB}，另列 no-hint 与 current-auto（后者大对象为1MiB）。
- q ∈ {legacy, current selector enabled}。把selector返回值和持久化marker作为结果；没有现成任意q参数。
- EC 2+2 可作为四独立drive的基础台架；4+2或4+4作为几何敏感性需要相应部署并记录实际d/p。单机四盘不能证明多机故障域安全。
- 对象大小按 4/16/64/256 KiB、1/4/16/64 MiB 的代表点及阈值±1 byte设置；请求范围4/16/64/128/256KiB/1MiB/whole；对齐、跨frame、跨B、尾stripe分别测试。小对象inline和外部shard分开。
- 普通PUT与MPU分开；读取时不随当前开关重新生成布局。新对象在新prefix创建；切换配置后读取旧对象用于兼容性验证。

### 因果次序

1. 固定B，legacy与selector-q比较；只有实际framing变化的点检验q效应。
2. 固定客户端请求和缓存策略，对四个B比较；记录q是否同时变化，若变化则不能称为纯B效应。
3. 比较no-hint与current-auto的实际布局。若完全一样，这应作为负向控制。
4. 客户端策略保持B/q不变，分别测试full-object/Range、LRU/既有准入、SingleFlight。当前实现需要增加独立研究开关。
5. 接入packed producer后，用相同内容与snapshot policy重建对象，检验精确frame Range到后端q的实际收益。最后才做完整workspace任务。

### 读写成本不能合并成一个不透明百分比

读侧分别报告 application delivered bytes、FUSE delivered bytes、S3 body bytes（metadata/payload/retries）、decompressed raw bytes、shard pread bytes及block-device bytes。缓存可能使最后两者不同；压缩可能使wire/logical<1，但不能由此推断raw overfetch为0。

写侧分别报告 changed logical bytes、BrewFS uploaded object bytes、PUT/MPU count、重写/失败重试bytes、EC data+parity bytes、checksum/frame bytes、设备实际写入bytes、CPU、hash次数和fsync/远端完成时长。B/q不改变名义d+p冗余比；若q增加hash而读收益有限，应呈现成本边界。用fdatasync/fsync和后台债务归零定义相同持久化终点，不以更松的完成语义换速度。

## G5：组合、真实 Agent 与不利场景

采用“真实trace识别场景—固定trace replay机制归因—真实Agent验证可用收益”三层证据。任务级重复与跨repo任务才是统计独立单元，不以百万FUSE事件冒充百万独立样本。固定模型version、提示、工具预算、初始环境、网络、编译cache；随机化运行顺序，保持任务与seed配对。报告成功率与任务质量，失败/timeout不可静默删除。LLM随机性下，task完成时间的改进须有置信区间且解释其方差。

必须包含以下反例：几乎不共享基线、接近全量修改、随机小范围读大frame、warm kernel cache、元数据库非瓶颈、对象存储高RTT、单目录写竞争、metadata budget很小、客户端或网络饱和、创建后立即丢弃的短生命周期工作区。BrewFS可能在其中不占优，论文应将这些点用于界定适用范围。

## G6：正确性与故障矩阵

| 边界 | 注入点 | 必须保持的不变量 |
|---|---|---|
| namespace isolation | create/rename/unlink/hardlink/xattr/permission交错 | 其他workspace的lower和private upper不被修改 |
| truncate | cut已提交、边界chunk清理中、恢复前extend | 旧upper/lower不可复活；新扩展为零 |
| upload→publish | PUT前、PUT完成后、metadata abort、commit response丢失 | 可见map只引用durable对象；不盲重放refcount |
| lease | 过期、renew失败、旧holder迟到完成 | 旧写者不能发布；读取生命周期有独立保护 |
| packed publication | data/descriptor/index/manifest/owner/binding各阶段 | 可见view必须完整；旧pinned view仍可读 |
| GC | owner acquire与delete reservation竞争 | live对象不删除；orphan可恢复清理 |
| B/q | header忽略、旧marker、冲突marker、截短、单shard损坏 | 持久化布局权威；错误fail closed；healing保留有效几何 |
| entire process | FUSE/client/server/metadata crash分离 | 只对已实现恢复路径主张结果，entity未接通路径标blocked |

不要把Redis persistence关闭的测试解释为断电durability。所有环境的metadata AOF/replication、对象存储ack语义和writeback策略必须写在部署清单中。

## 可复现性最小产物

冻结代码与binary SHA、Cargo features、kernel/FUSE参数、runtime配置、CPU/RAM/网络/磁盘拓扑、metadata durability、对象有效layout清单、task/trace/content hashes、计时边界、配对次序、raw events与aggregator版本、失败样本和exclusions。运行配置与结果分开保存；生成空表/图模板不能混入伪测量值。
