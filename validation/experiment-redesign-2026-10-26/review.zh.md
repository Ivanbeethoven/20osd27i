# 五 RQ 与配置关系修订检查

2026-10-26。状态：论文和计划修订完成；未运行系统性能实验，未提交或推送 Git。

- 作者配置：native 为基础路径，native-overlay 增加共享父状态和私有修改，native-overlay-pack 对固定下层采用 Packed。论文只讲原理，具体命名及源码映射在配套方案。Dynamic block 独立控制，三个机制仍独立可选。
- Packed 故事：把固定版本的只读元数据查询从中心数据库移到对象页面与客户端缓存；可写上层和控制记录仍使用数据库。查询减压不等于数据库空间自动释放。
- RQ1–RQ3 分别验证机制贡献；RQ4 验证迁移/恢复及提前发布成本；RQ5 验证多 Agent 完成任务和资源成本。共11项实验，七份回放身份冻结，真实会话验证单列。
- 计入首次 native seal、首次 Packed capture/build/upload/validate/publish、已有版本复用、版本更新、保留和实际回收。失败、无回本、冷读放大及源记录未退休均保留。
- 两个仓库的 `paper-design/` 六份文件逐字节一致；散列见 `synchronized-files.json`。现有采集脚本及其他任务改动未修改。
- 内置编译器在 TeX 启动前被 Windows restricted-token/split writable roots 限制阻断；本地 TeX Live 2026 的 latexmk/XeLaTeX 对同一根目录 main.tex 编译成功。PDF共13页，正文结束于第12页，字体均嵌入；没有未定义引用、缺字或 Overfull。
- 已检查全部页面缩略图及实验页大图；精简过长小标题和复用次数句子，未调整模板字号或页边距。
- `tools/validate_plan.py` 通过：五个RQ、11项矩阵、七份输入、规模计数、观测schema及LaTeX引用一致。两仓库修改通过 diff whitespace 检查；执行仓库 README 保持原 CRLF，检查使用 cr-at-eol。

局限：这是可复核的设计方案，不是已实现的分布式执行器。旧 campaign 生成器尚未适配七份任务表；首次执行需冻结官方版本、核对真实入口和语义，并登记实际资源。最新实现能力不能由历史源码快照推定。
