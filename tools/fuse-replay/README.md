# fuse-workload-replay

Linux 上的 Rust 文件系统负载回放器。对一个已有挂载目录执行真实 POSIX 文件操作，可用于 FUSE、XFS、JuiceFS、CephFS 等挂载点的**相同文件操作负载**对比。它不调用模型，不花费 Agent token。

这是 **mounted-filesystem workload replay**：经过内核和文件系统客户端的 POSIX 回放，**不是 FUSE wire protocol 回放，也不是完整 Agent 重跑**。内核缓存会改变实际 FUSE 请求数量；本工具的 logical ops/s 不能称为底层 FUSE IOPS。

## 快速运行

依赖 Linux 5.6+ 的 `openat2`、Rust 1.88+。目前实测环境为 WSL Ubuntu 24.04/Linux；Windows 原生不执行文件操作。

```bash
cargo build --release --locked
cargo test --locked
cargo clippy --locked --all-targets -- -D warnings

# 默认只验证，不访问或修改测试目录。
target/release/fuse-replay --trace examples/small.jsonl

# 父目录须存在；目标目录必须不存在或为空。
target/release/fuse-replay init --root /tmp/replay-demo-001

# 输出必须在被测目录外，且不能已经存在。
target/release/fuse-replay run \
  --trace examples/small.jsonl \
  --root /tmp/replay-demo-001 \
  --output /tmp/replay-demo-001.result.json \
  --workers 2 --pace asap --timing off --timeout-seconds 300
```

示例写入两个独立文件，再在全局 phase 屏障后跨流读取。它包含一次有意的短读和一次预期 `ENOENT`；两者的预期值明确写在 trace 中。运行会留下文件，不自动清理、不自动重置，也不覆盖已有结果。重跑这个有创建操作的示例请使用一个新的专用目录。

已有数据集应先在空目录 `init`，再把冻结的初始数据复制/reflink 到其中。禁止通过硬链接把工作区连接到仓库原件。`init` 不接受非空目录，以免误把整个仓库或挂载根标记成可写测试区域。

## 格式与执行语义

每行是一个 JSON 对象；第一行必须是头部，后续每行恰好一个操作。空行、未知操作、未知字段、无效句柄、路径逃逸、参数超限都会在执行前报错，不跳过记录。

```json
{"format":"mounted-fs-replay","version":1,"payload_provenance":"synthetic","description":"example"}
{"phase":0,"stream":0,"op":"open","fd":1,"path":"data.bin","access":"read_write","create":true,"exclusive":true}
{"phase":0,"stream":0,"op":"pwrite","fd":1,"offset":0,"len":4,"data_hex":"01020304","expected_bytes":4}
{"phase":0,"stream":0,"op":"pread","fd":1,"offset":0,"len":4,"expected_bytes":4}
{"phase":0,"stream":0,"op":"close","fd":1}
```

- `stream` 是逻辑执行流编号，同一流严格保持 trace 文件中的顺序；logical FD 只在流内有意义。所有预期成功的 `open` 都必须显式 `close`。
- `phase` 在文件中必须非递减；所有 worker 完成当前 phase 后才能进入下一个 phase。跨流的生产→消费依赖应分到不同 phase。没有编码的细粒度依赖、跨流共享 FD、同 phase 竞争的确定次序均不支持。
- `--workers N` 创建固定数量线程（1..256）。将按编号排序的流轮转分配给 worker；每个 worker 按文件顺序执行自己的操作。`N < stream 数` 时，几个流共享一个线程；这代表有限执行并发，不代表每个流独占线程。
- `--pace asap` 不插入 trace 延迟。`--pace trace` 使用 `at_ns`，表示相对整次执行开始的计划时间，不能超过 24 小时；同一流非递减，省略时沿用该流上一值。paced 模式要求 `workers >= stream 数`，避免一个流的等待阻挡另一流。phase 屏障和 I/O 时间可能导致迟到，结果报告总迟到与最大迟到。
- 只做单次 `pread/pwrite` 系统调用，不自动补齐短读写、不自动重试 EINTR。成功时默认 `expected_bytes=len`；合法 EOF/短返回必须明确填写实际预期长度。
- `expected_errno` 默认 0；非零表示预期 Linux errno 数值。预期错误单独计数，不冒充成功。错误 close 的 FD 生命周期有平台差异，本格式明确拒绝该场景。
- `--max-io` 默认 1 MiB，允许 1..64 MiB；零长度 I/O 暂不支持。偏移/长度必须适合有符号 64 位文件偏移。
- `--iterations K` 默认 1。仅在 `asap` 且整个 trace 只读时允许大于 1：完整回放 K 次，不重置初始树；每轮仍有所有 phase 屏障和显式 FD 关闭。结果同时给出 `iterations`、`operations_per_iteration` 和全部实际操作/字节数。主要用于摊薄启动/解析成本，不能用于写负载偷偷增加请求数。

支持的操作：

| op | 必填操作字段 | 可选字段/含义 |
|---|---|---|
| `open` | `fd,path,access` | access=`read/write/read_write`；create/exclusive/truncate 默认 false；mode 默认十进制 420（0644） |
| `close` | `fd` | 必须预期成功 |
| `pread` | `fd,offset,len` | expected_bytes；expected_sha256（实际返回字节的 SHA256） |
| `pwrite` | `fd,offset,len` | 必须且只能选 fill 或 data_hex；expected_bytes |
| `stat`,`lstat` | `path` | stat 禁止跟随符号链接；lstat 可查看链接本身 |
| `fstat` | `fd` | 查询已打开文件 |
| `readdir` | `path` | expected_entries；不保证目录条目顺序 |
| `mkdir` | `path` | mode 默认十进制 493（0755），受进程 umask 影响 |
| `rename` | `from,to` | 同一个专用 root 内的原子 renameat |
| `unlink`,`rmdir` | `path` | 删除文件/目录；不会递归删除 |
| `fsync`,`fdatasync` | `fd` | 使用真实系统调用 |
| `truncate` | `fd,len` | 使用 ftruncate，保留已打开 FD 语义 |

`readdir` 使用 `getdents64` 读完整目录，计数忽略 `.`、`..` 与内部标记 `.fuse-replay-root`。不排序、不逐条保存名称，当前 oracle 只验证条目数量，不能证明目录名集合相等。已打开文件即使被 rename/unlink，FD 仍指向原 inode。

## 输入内容与正确性

`payload_provenance` 必须为 `synthetic`、`captured` 或 `mixed`。

- `fill:65` 是预生成、复用的重复字节缓冲。它属于**合成载荷**，高度可压缩，仅适合功能/回放器开销测试，不能代表真实 Agent 写入的存储放大或压缩率。
- `data_hex` 保存确切写入字节，运行前解码。`captured` 禁止使用 fill。是否确实来自原 Agent 仍取决于采集流程；字段本身不能证明来源。
- `expected_sha256` 校验一次 pread 实际返回的数据。关闭操作计时不会关闭内容校验；对比时各系统必须使用相同 oracle 策略。
- 只有长度的历史 FUSE write 日志无法恢复原写入内容；缺失 logical FD、返回 inode、线程/依赖、errno 的旧 JSONL 也不能无损转换。本版不提供猜测转换器。

正式实验应冻结初始树与 trace。可生成可选的初始树指纹：

```bash
target/release/fuse-replay fingerprint --root /tmp/replay-fixture-001
# 把返回的 initial_tree_sha256 放进 trace 头部。
```

头部声明指纹后，每次 run 都在测量前核验；内容/路径/模式不一致直接拒绝。没有声明时 `initial_tree_hash_verified=false`，不声称初始数据相同。指纹不含内部标记、mtime/uid/gid/xattr；定义是：按相对路径原始字节排序，每项编码 type (`d/f/l`)、u64 little-endian 路径长度、路径字节、u32 little-endian 权限位(mode & 0777)；文件再编码 u64 长度及 SHA256 内容摘要，链接再编码 u64 目标长度及链接目标字节；加固定前缀 `mounted-fs-replay-tree-v1\0` 后计算整个 SHA256。不包括 root 本身。

**预检会读取目录元数据；指纹核验还会读取全部文件内容，因此会暖缓存。** 当前首版支持明确标注的暖缓存回放，不能仅在进程启动前清缓存后就声称是纯冷缓存实验。以后接入统一的“预检完成→重置客户端/服务端缓存→开始”控制屏障再做严格冷缓存测试，不以关闭路径检查代替。

## 性能与计时

热路径不解析 JSON、不打印逐操作日志、不拿全局统计锁。trace、路径 CString、write 载荷和 worker 程序在计时前准备；read 和目录缓冲按 worker 复用，FD 持续复用，统计在 worker 内累加，结束后合并。不同 fill 值只保留该值所需的最大缓冲；data_hex 目前每个操作单独存储，长写 trace 的内存占用需要计入准备成本。

| 字段 | 范围 |
|---|---|
| `parse_seconds` | 读 trace、SHA256、JSON 解析/验证、路径/写载荷预生成 |
| `preparation_seconds` | root/output/初始树检查、worker 程序、线程与缓冲准备；不含 parse |
| `initial_tree_scan_seconds` | preparation 内的树检查部分，不应再次相加 |
| `execution_seconds` | 同步启动到最后一个 worker 完成全部 phase；包含 pacing、校验、安全系统调用与 barrier；不含汇总和结果写盘 |
| `operation_time_ns` | 仅 `--timing op` 时：execute 调用耗时总和，含安全路径调用，不含随后内容 SHA256；并发总和可大于 wall time |
| `logical_operations_per_second` | 所有 attempted / execution_seconds；包含失败尝试，必须连同 valid/mismatches 读取 |
| `correct_operations_per_second` | (successful + expected_errors) / execution_seconds；预期错误仍单列 |
| `operation_syscalls` | 实际发出的主操作系统调用数量 |
| `safety_open_syscalls`,`safety_close_syscalls` | 额外目录/安全解析调用数量，已计入执行时间 |

`stat` 为安全起见使用 `openat2(O_PATH)+fstat+close`，比原生单次 stat 多两个调用；namespace 操作也安全打开父目录。`readdir` 包含打开目录、多次 getdents64 和关闭。**这些额外调用可能改变元数据负载，因此本工具用于受约束的相同 POSIX 工作量对比，不保证重现原始 FUSE opcode 序列和成本。** 不提供绕过路径安全的不安全 fast mode。

`--timing off` 关闭每操作时钟读取；仍计算整段 wall time。`--timing op` 开启计时有开销，必须分别测量，不能从开启计时结果直接声称回放器无开销。

## 安全与失败处理

root 必须是专用绝对路径、有本工具标记，且 root/祖先不能经过符号链接；拒绝 `/`、`/home`、`/tmp`、当前 HOME 等宽泛路径。所有 trace 路径必须相对且不能含 `..`、空组件、反斜线、内部标记。使用 root dirfd + `openat2(RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS | RESOLVE_NO_MAGICLINKS)`，无不安全 fallback；修改 namespace 仅使用受约束父目录 FD 和 basename。

运行前拒绝硬链接文件和设备/FIFO/socket，避免通过已有 inode 写到 root 外。此保证假定专用 root、祖先及初始文件不被无关进程并发替换或添加硬链接；不把工具当作抵御恶意宿主/root 用户的安全沙箱。被测文件系统本身也必须可信。普通 symlink 可被 lstat/unlink，但不会跟随。

默认运行到 trace 末尾以保存所有请求的失败情况；一条操作失败不会减少后续请求数量。汇总按 worker 最多保留 64 个详细失败，总失败计数不截断。返回码：0=全部符合预期；1=执行完成但至少一次不符合预期；2=参数/预检/输出错误；124=执行超时。**valid=true 表示符合 trace 的预期，不表示所有系统调用成功，也不表示完整应用正确。**

`--timeout-seconds` 默认 300，只覆盖执行阶段，不覆盖读 trace/扫描树。超时写 `valid=false, totals=null` 并退出 124；线程局部的部分计数未知，不填 0。若需要整进程上限，外层用 `timeout` 并记录退出原因：

```bash
timeout --signal=TERM --kill-after=5s 600s target/release/fuse-replay run ...
```

被终止的写负载可能留下部分修改，需新 fixture；不要继续当作干净重复。外部 kill/准备阶段错误可能留下空的已预留结果文件，这不是成功结果。输出采用 create_new，任何已有文件/符号链接均拒绝覆盖。

## 可重复的本地开销测试

```bash
python3 bench/run.py \
  --binary target/release/fuse-replay \
  --output /tmp/fuse-replay-bench-new \
  --operations 1048576 --iterations 8 --repeats 3
```

生成两份固定 trace：stat-heavy 与 4KiB 热读；16 个独立流，worker=1/4/16，timing=off/op，每格 3 次，共 36 次。所有 worker 设置用相同 trace，且统一完整回放 8 遍；执行顺序用固定种子打乱。逐次保留结果及失败，输出 CSV/JSON 和 min/median/max。`wait4` 记录每个子进程自己的 CPU、最大 RSS 和上下文切换；这些进程指标包含解析/准备，不能当成纯执行指标。`--generate-only` 仅生成冻结输入。

每个进程内的 8 遍不算 8 个独立样本；独立重复数是每格 3 个进程。

实测记录见 [validation/README.md](validation/README.md)。它只展示本地 ext4 暖缓存下回放器的开销和扩展行为，**没有运行 FUSE/BrewFS/云资源，不能解释为它们的性能结果**。

## 与 Agent 实验的边界

回放适合大量重复的存储机制对比和消融：固定文件操作、字节、目录状态与并发计划，减少模型随机性与 token 开销。仍需少量真实 AX Agent 验证工具耗时、正确完成任务和迁移后继续推理。会话 history/checkpoint 随 workspace 搬迁和 AX 的恢复协议要单独测试；文件操作回放器不能证明模型会话已经恢复。

当前不支持 mmap、link/symlink 创建、xattr、锁、io_uring、跨 root 路径、真实时间竞争轨迹恢复或任意 Agent trace 自动采集。跨文件系统硬件/缓存/持久化确认仍由实验控制器统一设置。
