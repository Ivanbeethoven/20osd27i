# 审阅意见落实与本地编译

2026-10-24。修改现有根目录 `main.tex` 及其章节文件，保留当前编辑器与根目录入口；本轮没有提交或推送。

## 已落实的修改

1. 三个机制仍独立可选。摘要、引言和总览统一为“共享版本身份与元数据、对象访问单位分离”，以接口契约解释组合；没有强制三者共同开启，也没有声称可选性本身带来性能优势。
2. 补充硬链接的 inode 身份、rename 的锁顺序、原子提交和单操作读验证，并区分带缓存/写回的实现与直接读写的实现。截断说明同时覆盖 lower 可见边界、已有 upper 映射清理和扩展前完成清理。
3. 成本改为 `C_c(K,T)`，加入 retention、按驻留字节和时间计费的积分，以及跨版本共享工作的去重。K 在工作区生命周期与独立查询会话之间分别定义；T 从构建覆盖至回收。
4. 组合相对最佳合法子集的增益、对外部系统的优势、统计交互效应分别检验；零交互不再意味着组合失败。
5. 实验协议固定共享基线分组、复用和保留政策、并发数 m、批次组成与配对方式。180/540 是任务执行预算，初始设计为每系统三批；正式批次数经方差试验冻结。批次指标按独立配对批次统计，未完成批次在共同截止时间右删失。
6. 压缩重复的可选性说明和审计清单。第 8 节由约 2,271 个空白分词降至 1,186；操作矩阵保存在 `experiments/evaluation-protocol.md`。移除两张实验宽表与密集的相关工作比较表，保留机制选择表及对象粒度算例。
7. 按作者后续要求，正文和实际引入的示意图去掉内部模块名、挂载代号、格式版本、实验编号及提交哈希，用实现思路说明差异。原始观测数字不变，采集类名移出正文；复现身份保留在配套记录。写作准则新增这一约束。
8. 更新实验 YAML 的源码基准及角色说明，修正 FUSE 主图 README 的当前单栏图入口。保留审阅期间更新的架构图与图注。

## 技术依据

本段供源码核查，不放入论文原理正文。固定文件系统快照为 `../brewfs-principles-242af5f`，完整版本身份在 `experiments/evaluation-protocol.md`。

- 硬链接：`src/workspace_overlay/entity/namespace.rs:730–785,1129–1151`；`src/workspace_overlay/meta_layer/mod.rs:2476–2533`。
- rename 与读验证：`entity/namespace.rs:313–318,542–631,1182–1261`；`entity/namespace_snapshot.rs:215–236`（均位于 `src/workspace_overlay/`）。
- Catalog 事务：`src/workspace_overlay/meta_layer/mod.rs:2575–2748`；`src/workspace_overlay/stores/kv_store.rs:1337–1414,3738–3800`。
- 截断：`src/workspace_overlay/entity/recovery.rs:97–132,228–233`；扩展前清理：`entity/data.rs:171–185,892–935`；示例测试定义：`entity/data_tests.rs:848–854`。
- 本轮进行了源码核对，未执行这些 Rust 正确性测试；正文没有将其升级为实测并发或故障保证。

## 检查结果

- 内置编译器仍在启动阶段报告 Windows restricted-token/split-writable-roots 环境错误，没有进入 TeX；已按用户要求使用本机 TeX Live 编译现有主文件。
- 命令：`latexmk -g -xelatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex`，退出码 0。
- 最终 PDF 共 **13 页**，正文结束于 **第 11 页**，参考文献从第 11 页开始。修改前共 16 页、正文结束于第 14 页。
- 最终日志 **0 Overfull、23 Underfull**；没有未解析引用/文献、缺字或致命错误。Underfull 为松排提示，未将它误报为溢出。
- 已查看全部 13 页缩略图，放大核对第 4 页架构图和第 6 页原理图/成本公式；最终架构图更新后重新编译和查看第 4 页。未发现图文裁切、重叠或公式越界。原模板、正文大小和页边距未改变。
- PDF 的 14 个字体资源均已嵌入，见 `fonts.json`。
- YAML 能解析；CSV 包含 17 条实验记录、字段完整；180/540 算式、章节标签和正文内部代号扫描通过；`git diff --check` 通过。
- 最终构建记录的源码和关键插图哈希在检查时一致。证据见本目录的 `compile-summary-final.json`、`static-checks.json`、`final-source-hashes.json`、`latexmk-output.txt` 与逐页图片。

源文件和 PDF 已更新；实验仍是计划，本轮没有生成性能测量或正确性测试结果。
