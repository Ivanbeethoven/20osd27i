# 英文学术写作 skill 调查与选择

核验日期：2026-10-22。目标是选择有公开维护记录、适合研究写作且能够核对来源的参考 skill。没有可信的统一指标可证明某个单独 skill 是“全网最流行”，因此以本次核验候选的 GitHub 仓库星标作为透明的发现指标，同时考察内容与 OSDI 任务的匹配度。

## 1. 候选比较

| 候选 | 所属仓库 GitHub stars | 定位 | 本次使用方式 |
|---|---:|---|---|
| K-Dense `scientific-writing` | 53,699 | 科学写作、证据来源、事实一致性、作者责任与文稿审核 | 作为流行的通用学术写作参考，完整阅读当前 SKILL.md |
| Orchestra `systems-paper-writing` | 13,806 | OSDI/SOSP/NSDI 等系统会议的论证结构、设计与评价组织 | 作为更直接匹配 OSDI 的结构参考，完整阅读当前 SKILL.md |
| Orchestra `ml-paper-writing` | 同一仓库 13,806，不另计 | ML/AI 会议写作、引用核验、LaTeX 工作流 | 查阅其中代码库分析和引用核验部分；其自身将系统会议任务引导至 systems skill |

统计来自 GitHub repository API，快照见 `popularity_snapshot.json`。星标属于整个多技能仓库，不能解释为单个 skill 安装数、活跃用户数、科学正确性或质量排名。网页显示的舍入值与 API 的整数值可能不同。

## 2. 版本与许可

| 仓库 | 固定来源版本 | 许可 |
|---|---|---|
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | `593377bb048752abb0152deab9fbb1083a6087df` | MIT |
| [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | `773a52944ba4747a18bd4ae9ade53fff041adcbc` | MIT |

固定路径：

- [K-Dense scientific-writing/SKILL.md](https://github.com/K-Dense-AI/scientific-agent-skills/blob/593377bb048752abb0152deab9fbb1083a6087df/skills/scientific-writing/SKILL.md)
- [Orchestra systems-paper-writing/SKILL.md](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/773a52944ba4747a18bd4ae9ade53fff041adcbc/20-ml-paper-writing/systems-paper-writing/SKILL.md)
- [Orchestra ml-paper-writing/SKILL.md](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/773a52944ba4747a18bd4ae9ade53fff041adcbc/20-ml-paper-writing/ml-paper-writing/SKILL.md)

本次新 skill 是独立撰写的规则与检查问题，没有完整复制上游技能，也没有运行其安装器或导入其全部依赖。出处保留在 skill 的 attribution 参考文件中。

## 3. 采纳与修正

K-Dense 提供了“事实—证据—来源”的明确约束，对缺失与未核验状态作区分；这些思想适合 BrewFS 当前缺少正式结果的阶段。但其部分医学/临床报告流程不适用于系统会议，不应移植成 OSDI 要求。

Orchestra 的 systems skill 将问题、设计决策和评估组织为连续论证，比较符合本次目标。它给出的固定段落数、强制重复结论和页数分配属于建议，不能当作所有 OSDI 论文的风格规则；其年度会议规则也必须用当前官方 CFP 覆盖。

因此新建 `osdi-systems-paper` 同时包含可核查的代码证据分层、真实引用核验、系统论文的因果论证、可证伪的实验规划，以及当前 OSDI 格式与匿名要求。对 BrewFS 特别加入 final uploaded object、EC block `B`、physical read/checksum unit `q` 和 client fetch policy 的区分。

## 4. 学术写作来源说明

K-Dense 相关资料另有已核验预印本：Timothy Kassis, Vinayak Agarwal, Yuhuan He, Darshil Patel, and Aubrey M. Brueckner. *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*. arXiv:2609.00065, 2026. [arXiv](https://arxiv.org/abs/2609.00065), [DOI](https://doi.org/10.48550/arXiv.2609.00065)。访问时页面显示 v2，2026-09-02 修订。

该来源用于说明写作工具的出处；它不是 BrewFS 存储机制的相关工作，不应为增加参考文献数量而加入论文技术比较。

## 5. 保存与安装状态

可移植技能已初始化并通过结构验证，目录为 `skills/osdi-systems-paper/`。自动审批审查拒绝了向平台受保护 Skills 路径的写入，因而没有完成在线安装或 git 同步。交付包包含源码和来源记录；不能将“源码交付成功”表述为“技能已安装”。
