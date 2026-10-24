# 实测验证记录

日期：2026-10-23。工具版本 0.1.0。本目录保存真实本地测量，不含云资源、模型调用、BrewFS 或其他 FUSE 文件系统结果。

## 构建与正确性

在 WSL Ubuntu 24.04 中执行：

```bash
CARGO_TARGET_DIR=/tmp/codex-fuse-replay-target cargo test --locked
CARGO_TARGET_DIR=/tmp/codex-fuse-replay-target cargo clippy --locked --all-targets -- -D warnings
CARGO_TARGET_DIR=/tmp/codex-fuse-replay-target cargo build --release --locked
```

结果：**19 个集成测试通过，0 失败；Clippy 无警告；release 构建通过。**

覆盖：16 流并发隔离、phase 生产消费依赖、FD 在 rename/unlink 后保持有效、读字节 oracle、短读默认失败/显式短读成功、预期错误单列、只读 8 轮总操作/字节精确计数、禁止写操作/同步/paced 的重复回放、路径/符号链接/硬链接/FIFO 约束、输出拒覆写与禁止位于 root 内、初始树 hash 核验、超时退出 124 且未知部分计数为 null、执行不匹配退出 1。

独立只读代码审查另运行了 3 个外部临时目录场景：FD 在 rename+unlink 后继续写读；父目录符号链接不能把 unlink 引到 root 外；两个 paced 流（150ms 和 0ms）由两个 worker 独立执行。审查发现并已修复：paced 流共享 worker 的额外等待、默认短读写被误判成功、缺少执行期限、每个 worker 为所有流分配 FD、close 错误后的不确定生命周期。未保留已知阻断问题。

## 回放器开销

环境：Intel Core Ultra 9 275HX，WSL 可见 16 CPU，Linux ext4 `/dev/sdd`，暖缓存。完整内核、编译器、挂载参数、二进制 SHA256、trace SHA256、逐进程 CPU/RSS 在 [environment.json](2026-10-23-local-ext4/environment.json) 与 [runs.csv](2026-10-23-local-ext4/runs.csv)。

命令：

```bash
python3 bench/run.py \
  --binary /tmp/codex-fuse-replay-target/release/fuse-replay \
  --output /tmp/fuse-replay-benchmark-20261023-v2 \
  --operations 1048576 --iterations 8 --repeats 3
```

每份 trace 为 1,048,576 个 stat 或 pread 请求，16 个独立流，每进程完整回放 8 遍；只读 FD 打开/关闭也计数。每格 3 个独立进程，36 次全部有效。8 遍是一个测量单元，不是 8 个独立样本。先前一次单遍开销试跑发现 16-worker 热读只有约 20ms，因此统一增加到 8 遍再做本表；未根据某个并发配置单独改变请求量。

下表为三次独立进程的中位数；请求速率单位为**百万 logical operations/s**。完整范围和原始结果见 [summary.json](2026-10-23-local-ext4/summary.json)；它们不代表存储设备的带宽或原始 FUSE 请求速率。

| 固定负载 | worker | timing off：秒 / 百万操作每秒 | timing op：秒 / 百万操作每秒 |
|---|---:|---:|---:|
| stat-heavy | 1 | 4.336 / 1.935 | 4.667 / 1.798 |
| stat-heavy | 4 | 2.834 / 2.960 | 2.805 / 2.991 |
| stat-heavy | 16 | 3.195 / 2.625 | 3.454 / 2.429 |
| pread 4KiB 热读 | 1 | 1.611 / 5.206 | 1.928 / 4.352 |
| pread 4KiB 热读 | 4 | 0.382 / 21.953 | 0.457 / 18.339 |
| pread 4KiB 热读 | 16 | 0.157 / 53.377 | 0.184 / 45.606 |

- stat 每进程实际 8,388,608 个 logical 请求，包含 8,388,608 个主调用 + 同量安全 open + 同量安全 close，共 25,165,824 次统计到的系统调用。4→16 worker 没有改善本地 stat 吞吐，不声称所有负载线性扩展。
- pread 每进程实际 8,388,608 次 4KiB 读取，加 256 次打开/关闭，共 8,388,864 个 logical 请求，读取总计 34,359,738,368 字节。只读 16 个 4KiB 热文件并反复复制到线程缓冲，不能当成磁盘/网络吞吐。
- 16-worker 热读 timing off 的执行范围为 0.152–0.179 秒，仍是短测，三次只能描述当前宿主机的观测。没有隔离 CPU、没有控制后台 Windows/WSL 活动，不作显著性或生产容量推断。
- 每次进程都预解析 trace。stat 解析中位数约 0.340–0.346 秒，热读约 0.406–0.417 秒；准备阶段 0.011–0.027 秒。它们在执行计时外，不能从总成本中删除。
- stat 的逐进程最大 RSS 中位数约 252–254 MiB；热读约 155–160 MiB。这包含解析和运行，不是纯 I/O 缓冲大小。
- per-op 计时对热读的开销明显。stat 4-worker 的 off/op 区间重叠，op 中位数略快属本次波动，不能解释为开启时钟提高性能。

目录保留全部 36 份结果、逐次 CSV/JSON、fixture 哈希、环境和汇总；约百 MiB 的可再生 trace 与原始 fixture 没有提交仓库，`bench/run.py` 按固定种子生成，环境记录提供精确哈希核验。默认内容 oracle 关闭，所有 pread 长度检查开启；各配置相同。
