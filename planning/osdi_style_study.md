# OSDI 论文写作风格学习与 BrewFS 写作约束

核验日期：2026-10-22。本文用于研究筹划，不构成已完成实验或可直接投稿的声明。

## 1. 采用的依据

官方规则以 [OSDI 2027 CFP](https://www.usenix.org/conference/osdi27/call-for-papers)、[Requirements for Authors](https://www.usenix.org/conference/osdi27/requirements-authors) 和 [USENIX 官方模板页](https://www.usenix.org/conferences/author-resources/paper-templates) 为准。OSDI 2027 已发布，故无需将 2026 年规则冒充当前周期。用户尚未承诺参加这一周期，以下日期用于可行性判断。

写作原则还参考了官方推荐的 Levin 与 Redell 的系统论文写作文章，以及 Gopen 与 Swan 的科学写作文章；对 Assise（OSDI 2020）、SquirrelFS（OSDI 2024）和 WOLVES（OSDI 2025）进行了引言、设计、评估及局限部分的结构阅读。完整来源与定位见配套 skill 的 `references/venue-and-style.md` 和 `references/sources-and-attribution.md`。

## 2. 真正需要学习的论证方式

OSDI 官方评审要求同时关心问题的重要性、方案的理由、实现的实用性、证据与结论的匹配，以及对既有研究的明确推进。对于 BrewFS，这意味着论文不能只把三个已有方向放在同一系统中，再通过通用吞吐量实验给出总速度。需要解释多工作区共享基线、私有修改和对象存储物理访问之间出现了什么新的约束，以及为何三项机制共同处理了该约束。[1]

学习样本给出的可迁移经验如下。下表是结构分析，不把其他系统的实验发现视作 BrewFS 的证据。

| 样本 | 观察的论证结构 | 对 BrewFS 的直接启示 |
|---|---|---|
| Assise，OSDI 2020 | 硬件代价变化引出放置与一致性设计；评估解释延迟来源、应用收益、故障恢复与扩展性，并交代基线语义差异 | 对不同文件系统建立语义、持久性、缓存和部署位置对照表；未能完全对齐的维度必须显式说明 |
| SquirrelFS，OSDI 2024 | 从具体正确性问题推导机制；明确编译器能检查的性质及不能检查的部分；评估包括性能和正确性 | 将 overlay 视图隔离、快照发布、数据映射解析与崩溃恢复分别定义；不要用笼统的 POSIX 或一致性标签代替契约 |
| WOLVES，OSDI 2025 | 先分解路径中的元数据成本，再推导新的表示方式；同时测量正常路径、老化、恢复和资源消耗 | 为三项设计分别准备可归因的动机测量；将快照构建、索引成本、缓存和回收代价纳入设计的净收益 |

以上样本见 [4]–[6]。具体的实验问题、内容顺序和页数应服从 BrewFS 的论证，不能机械照搬样本目录。

## 3. BrewFS 的主线应当如何组织

建议把论文的统一问题表述为：**当多个编码智能体从同一不可变环境出发并独立修改文件时，如何避免重复维护共享状态，同时让共享元数据和文件数据在对象存储上保持可按需访问的表示？**

这是一条待用实验建立的系统论点。它使三个标题短语各自承担明确职责：Delta-Based 负责工作区差异的表示；Packed Metadata 负责共享基线的查询与数据定位；Variable-Granularity Object Storage 负责最终上传对象在后端的编码与物理读取。论文需要进一步证明三者的组合收益以及组合产生的语义约束。

| 写作阶段 | 需要回答的问题 | 主要证据 |
|---|---|---|
| 问题界定 | 哪类多智能体任务需要独立工作区，基线如何产生，共享持续多久？ | 实际任务定义、工作流、负载记录 |
| 动机 | 哪个成本随工作区数、目录规模或对象访问范围增长？ | 同语义基线的分解测量 |
| 洞察 | 哪些状态应共享，哪些状态应私有，哪些决策应按对象作出？ | 明确模型和设计替代方案 |
| 机制 | lookup、read、write、publish 如何经过三层表示？ | 固定提交代码、数据结构及关键路径 |
| 正确性 | 修改隔离、删除、重命名、发布与恢复如何成立？ | 契约、不变量、覆盖范围清楚的测试或形式模型 |
| 评价 | 各机制在何种范围内有效，代价和退化场景是什么？ | 端到端结果、消融、敏感性、失败/恢复实验 |

## 4. 初稿必须保持的确定程度

本次可以完成问题背景、文献比较、模型、设计、实现边界、研究问题和实验规划。性能收益尚未通过本次工作测量，因此不能写成 “BrewFS achieves 3×…” 或把空白图位填上估计曲线。

对现有负载记录应保留实际 harness 与模型名称。负载画像只能说明记录中发生了什么访问；机制是否提高性能，需要受控对照。对代码应区分规范提出、代码存在、运行路径接通和实测验证四个层次。

英文段落采用“问题—具体机制—作用范围”的顺序。把抽象名词改成明确对象和操作。例如，`metadata overhead` 应具体到每次查询的 KV 请求、对象 GET 次数、读取字节或 CPU 时间；`storage efficiency` 应区分容量冗余、网络流量和物理 I/O。标题里的三项机制在摘要、设计和评价中保持同一术语。[7]

## 5. 当前周期的必要约束

OSDI 2027 研究轨道要求双盲，正文最多 12 页，参考文献可另占页数；超页附录不能塞入主 PDF。独立补充文件被允许，但正文必须独立成立。公开项目的匿名投稿需使用不同的系统名。因此当前保留 BrewFS 名称的初稿用于内部讨论，投稿版应在作者决定后统一替换系统名并移除识别信息。[1][2]

官方截止时间换算为北京时间：摘要注册 2026-12-02 06:59，全文 2026-12-09 06:59。当前资料没有证明所有实现接通、正确性验证和正式实验能在这个窗口完成；是否赶该周期应由证据成熟度决定。[1]

OSDI 2027 禁止提交全部或主要由 AI 生成的工作，允许 AI 编辑辅助。这里交付的是研究工作初稿及规划资料；作者需要实质性负责论证、实现、实验、写作和最终审核，不能将生成稿原样提交。[1]

## 6. 可复用 skill 与验证状态

`skills/osdi-systems-paper/` 包含工作流与五份按需加载参考文件，已运行官方 `quick_validate.py`，结果为 `Skill is valid!`。另做了内部引用目标存在性检查。该验证只证明包结构和引用组织符合要求，不证明稿件的科学质量。

向受保护的 `/root/.codex/skills/remote-skills` 写入时，自动审批审查拒绝了操作。因而此次没有完成 Skills 页面安装、git 提交或推送；可移植 skill 源文件保存在本次用户明确要求的交付包内。没有绕过该限制。

## 参考来源

1. [OSDI 2027 Call for Papers](https://www.usenix.org/conference/osdi27/call-for-papers).
2. [OSDI 2027 Requirements for Authors](https://www.usenix.org/conference/osdi27/requirements-authors).
3. [USENIX Templates for Conference Papers](https://www.usenix.org/conferences/author-resources/paper-templates).
4. Anderson et al. [Assise: Performance and Availability via Client-local NVM in a Distributed File System](https://www.usenix.org/conference/osdi20/presentation/anderson). OSDI 2020.
5. LeBlanc et al. [SquirrelFS: using the Rust compiler to check file-system crash consistency](https://www.usenix.org/conference/osdi24/presentation/leblanc). OSDI 2024.
6. Pan et al. [Fast and Synchronous Crash Consistency with Metadata Write-Once File System](https://www.usenix.org/conference/osdi25/presentation/pan). OSDI 2025.
7. Gopen and Swan. [The Science of Scientific Writing](https://www.usenix.org/sites/default/files/gopen_and_swan_science_of_scientific_writing.pdf). *American Scientist* 78(6), 1990, 550–558.
8. Levin and Redell. [How (and How Not) to Write a Good Systems Paper](https://www.usenix.org/conference/osdi12/guidelines-authors). *ACM SIGOPS Operating Systems Review* 17(3), 1983, 35–40.
