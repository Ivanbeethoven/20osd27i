# 对象粒度原理审计

审计日期：2026-10-23。BrewFS 只读源码快照：`../brewfs-principles-242af5f`，提交 `242af5f7e9bba7afc0c61778f1084fcb20e083a0`。这里只做代码阅读，没有修改系统代码或运行性能实验。RustFS 补核验保持已有研究分支的固定提交 `Ivanbeethoven/rustfs@cc4926fac1107aee76540f28bf22dbd47fcbca24`，不代表当前上游 RustFS 默认支持这些扩展。

## 核心结论

三项机制位于不同决策层。增量工作区决定“工作区继承什么、私有修改什么”；打包式元数据决定“不可变命名空间及其访问索引如何组织和读取”；可变粒度对象存储决定“字节如何形成对象，以及对象如何编码和服务读取”。对象层可以服务普通 flat 卷，不需要先有增量工作区或 Packed Metadata。前两项也不以 RustFS 布局提示为正确性前提。组合只改变输入对象和访问形状，不自动证明性能协同。

必须修正上一稿的范围：PPT 第 17 张（页脚 16/22）的“动态 Block Size”讨论的是**客户端 Block 对象划分**，候选 1/4/8/16 MiB；原论文第 6 章只讨论 RustFS 编码块提示及 q，因此缩窄了作者的原意。两层可以纳入同一“可变粒度对象存储”设计，但不能声称客户端动态选档已实现。

## PPT 对应含义

来源为 `evidence/ppt-principles/slides.json`，含幻灯片正文和显式关联讲稿。

- 第 9 张说明已有 Chunk/Slice/Block 模型：Chunk 是默认 64 MiB 的逻辑地址范围；一个 10 MiB Slice 可形成 4+4+2 MiB 的 Block 对象。一次 write 不等同一个 Slice，Block 大小不等于每次下载量，BrewFS 沿用该模型而不将其列为创新。
- 第 13 张区分 dirty overlay 与 workspace diff：前者用于本客户端读自己的未完成写回数据，后者管理工作区私有元数据。默认先上传对象再发布映射；提前发布为可选写回模式，不能混同本地可读与远端持久化。
- 第 17 张明确写明动态粒度是**研究方案**，默认仍是 64 MiB Chunk、4 MiB Block；1/4/8/16 MiB 是拟评估档位，尚无自动选档收益。64 MiB 文件的完整对象数为 64/16/8/4，只对整块获取或解码的情形给出局部读放大示例；Range GET 可以只读部分对象。不可变 Slice 覆盖本身不要求重写旧对象。

## 可复核的代码证据

以下相对路径都以 BrewFS 快照根为基准；行号来自上述固定 SHA。

| 主张 | 代码位置 | 边界 |
|---|---|---|
| 普通 flat 卷可独立选择客户端 Block 大小及 S3 后端；无 workspace/Packed 先决条件 | `src/cli.rs:380–447`，尤其 `397–400` 创建 layout、`429–447` 创建 S3 client 和普通 ObjectBlockStore | 非 flat 卷会走适用专用分支；不能用某个专用分支代表整个 BrewFS |
| 默认 Chunk=64 MiB、Block=4 MiB | `src/chunk/layout.rs:11–41` | 是逻辑分割参数，不是 RustFS 编码参数 |
| Block 是固定配置，当前不是按文件/对象动态学习选档 | `src/config.rs:289–295,1271–1286`；`src/chunk/slice.rs:88–102`；`src/chunk/reader.rs:167–204` | 配置校验 Chunk 为 Block 的非零整数倍；SliceDesc 不携带独立块几何，reader 根据同一个 layout 计算 Block，不能随意在已有卷上更改解释 |
| 声明的 volume 几何具有约束 | `src/config.rs:1061–1081` | CLI/layout 与声明的 volume 值冲突会失败；不能将配置能力描述成透明的在线迁移 |
| Slice 数据按 Block 边界分成上传对象 | `src/chunk/writer.rs:161–176` | 客户端输入可以是多个 Bytes 段；对象形成还受 flush、尾段等影响，不保证每个对象都填满目标 Block |
| 对象最终长度由实际内容、适用压缩和 framing 决定 | `src/chunk/store.rs:1035–1082`；`src/chunk/compress.rs:88–145` | 写入偏移可能产生零前缀；不应把目标 Block 大小等同最终上传长度 |
| 普通压缩/不压缩读取策略存在区别 | `src/chunk/store.rs:421–478,862–875,1211–1217` | Block 默认 4 MiB，range 阈值 25%，page 默认 64 KiB；字节可寻址及较小请求才适用相应范围读取；大范围或压缩块可能整对象获取/解码 |
| 新 Slice 覆盖与整旧对象重写不是同一件事 | `src/chunk/writer.rs:169–174` 的新 slice_id 对象键；`src/chunk/reader.rs:155–204` 的可见 Slice 区间解析 | compaction、flush、小尾段和重试等仍会影响写放大，应测实际字节 |
| RustFS hint 完全独立于客户端 Block 边界及 MPU part size | `src/cadapter/s3.rs:118–122` | 原文注释明确说明不会改变二者 |
| hint 默认关闭且需要显式编译 feature | `Cargo.toml:342–348`；`src/cadapter/s3.rs:76–89,125–138`；`src/config.rs:261–267,1212–1217` | 默认 features 不含 `rustfs-ec-block-size-hint`；未编译时配置 hint 会失败；hint 要求 S3 后端和兼容服务端 |
| hint 的 fixed 候选为 64 KiB/256 KiB/1 MiB/4 MiB；auto 只是长度阈值规则 | `src/cadapter/s3.rs:62–89` | `L_o <= 1 MiB` 不发 hint；大于 1 MiB 请求 1 MiB；不是 PPT 的 1/4/8/16 MiB Block 选档 |
| hint 按完成后的对象 wire length 决定 | `src/cadapter/s3.rs:25–26,734–735,774–775,809–812,942–945,1155–1156` | 覆盖普通、vectored、非 strict create-only、MPU initiation；MPU 采用完整对象长度而非每 part 长度 |
| 打开 hint 同时改变普通读策略 | `src/cadapter/s3.rs:1110–1112`；`src/chunk/store.rs:506–519,1216–1217` | 任一 hint 配置开启 whole-object preference、LRU；即使 auto 对小对象不发送 header，读策略仍改变，不能将收益全归于 B |
| Entity mount 目前未传入 hint | `src/cli/entity_mount.rs:35–48` | S3Config 用默认 None；不能声称 all-on Entity 集成已完成 |
| Entity strict durable create-only PUT 未接 hint | `src/cadapter/s3.rs:1191–1218`；`src/workspace_overlay/entity/data.rs:438–443` | 该路径刻意不降级成 unconditional PUT，不能为了接 hint 破坏原语义 |
| fixture 构建器默认未配置 hint | `src/bin/packed_v3_snapshot_fixture.rs:918–927` | 已构建 packed 对象不会因读取时开启 hint 重新编码 |
| Entity 上层与普通 Block uploader 是不同对象形成路径 | `src/fuse/entity.rs:37,615`；`src/workspace_overlay/entity/data.rs:400–443` | FUSE 单写不超过 1 MiB，按逻辑 chunk 边界截段后直接上传；未走普通 4 MiB 聚合，不能套用普通 Block 选档 |
| Entity upper 部分读目前获取并认证完整对象 | `src/workspace_overlay/entity/data.rs:829–867` | HEAD 确认长度，GET `[0,size)`，核验 SHA-256，再由调用者截取需要区间；4 KiB 应用读不等于 4 KiB 网络 GET |

检索 `src/` 与 `doc/architecture/` 中 dynamic/adaptive block 及 block-size policy/candidate/selection 后，没有找到 PPT 所指按访问轨迹选择 1/4/8/16 MiB 客户端 Block 的控制器。此为特定源码快照内的审计结论，不推广到尚未提供的其他分支。

## RustFS 研究分支的独立开关与持久化契约

2026-10-23 用 GitHub `fetch_file` 重新读取以下固定版本源文件：

- [ec_block_layout.rs](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/ecstore/src/object_api/ec_block_layout.rs#L1)，blob SHA `30d343c752854e0f8265e45fd2c7d8ebd10af381`。1–55 行给出默认 B=1 MiB、四档 B、响应头和独立 q marker；176–232 行表明无 hint、feature disabled、fleet unconfirmed 或 ineligible write 可保留默认 B；235–326 行给出 q 的独立写 gate、几何约束与持久化读取规则。
- [config constants](https://github.com/Ivanbeethoven/rustfs/blob/cc4926fac1107aee76540f28bf22dbd47fcbca24/crates/config/src/constants/object.rs#L130)，blob SHA `709053e8ca46ff86a883097942d0122255ef49a7`。130–155 行给出 B hint enable/fleet-confirmed 与 q enable/fleet-confirmed，共四个 gate，全部默认 false。

因此 B 与 q 也不是“必须一起打开”：B hint 请求是否接受由 B 的 gates 决定；新 q framing 由另两项 gates 决定。q 必须满足 `q | s` 及 `q*d | B`（s 为完整 shard 逻辑大小，d 为数据 shard 数），独立选择不表示任意几何都兼容。读者按持久化布局解释旧对象，不能把新写配置直接套到旧对象。auto 请求的 B=1 MiB 与此研究分支默认值一致，可能完全没有改变有效 B。

这里的后端代码是研究扩展证据。上游部署支持、完整客户端路径接线、读/修复/混合版本验收仍须分别确认，不能从发送一个 header 推导完成。

## 推荐给论文的原理结构

1. 可选性与职责：普通文件系统也需要对象形成；Delta/Packed 各自产生数据对象，但不决定必须启用哪种后端布局策略。
2. 客户端对象形成：用 `g` 暂表示客户端 Block 目标大小，`L_o` 为最终上传对象长度。默认固定 g=4 MiB，PPT 1/4/8/16 MiB 动态选择是研究方向；现有代码提供固定配置，而不是已完成的访问自适应控制器。
3. 读取与写入代价：对象数、实际传输字节、解码/认证粒度、缓存预算、重试/compaction 分别影响成本。用一个 64 MiB 连续 Slice 的条件示例解释 tradeoff，不假设所有小读整块下载或每次小写重写旧块。
4. 后端独立布局：定义 B、q 与几何约束，再解释 final-object hint、后端权威、持久化格式。保持既有确认术语，不能将 B 改成客户端 Block。
5. 组合边界：固定客户端对象大小与默认后端布局均合法；普通 flat 路径可独立启用 hints；packed frame 是另一层认证单元；Entity 的当前接线限制放实现章，原理章只简洁指出各 producer/reader 需遵守自己的对象格式与持久化契约。

建议论文主张为“把对象形成、取数策略和后端布局作为可分别选择的参数，降低其与访问形状的失配”，而不是“已有动态策略保证减少读写放大”。实验设计应分开 g、fetch/cache、B、q；已有 all-on 名称不足以证明这些变量实际改变。
