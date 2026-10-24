# 系统图逐词修订版：最终语义核对

日期：2026-10-23。只读检查当前 `figures/system-architecture-editable.png/.svg`、生成代码 `tools/draw_architecture_editable.py`，及 `sections/03-overview.tex:69–95` 的相关正文与图注。没有修改图、代码或论文；本次只新增本记录。

**结论：未发现需要继续修改的实质语义错误，也未发现关键机制因缩写而丢失。当前标签与图注合读足以表达边界。**

- **视图与私有上层**：View W₁/W₂ 对应完整工作区视图；图注明确条带只是 file-range sources。Δᵢ 为 private writable upper，图注进一步限定为 private metadata and data mappings；不再把同一条带同时命名为完整 W 和完整 Δ。Resolve 仍为上层优先、按规则继承的定义，未被替换为算术相加。依据：`sections/03-overview.tex:42–58,81–82`，`04-delta.tex:22–38,49–72`。
- **共享、删除与字节来源**：Data 引用私有 U₁，LowerRange 引用固定 S，Hole 明确为 zeros。W₂ 的线从蓝色继承范围连出，未接到 Hole；pinned reference 表示绑定来源，不暗示对 S 的写入。private/writable 不额外承诺 payload 此刻的远端持久性。依据：`sections/04-delta.tex:49–64,76–81`；固定代码 `entity/model.rs:75–101`、`entity/resolver.rs:22–26,56–65`。
- **S 的表示与 Packed 路径**：S 可以使用 sealed native records 或 packed snapshot，图中两分支有 or，未将 Packed 变为工作区必要条件。Read-only mount 可独立进入 Packed；parent/name 与 Name-range index 对应按父目录及原始名称范围的查询，页中 Name、Attrs、Locator 是联合记录。Object Oₚ 与内部 Packed frame 已分开，via descriptor 由图注补充 authenticated frame descriptors；未把框内示例误作所有读取类型或固定 GET 数。依据：`sections/03-overview.tex:83–86`，`05-packed.tex:31–37,59–79`。
- **客户端与后端粒度**：fixed g 与图注中的 alternative g₁ or g₂ 表达配置备选，不暗示在线动态控制器。两条分块带具有相同总长，分别为 10+10+10+5 和 20+15，最后一段各为一个短尾；此图形算例相容。适用的压缩／framing 在客户端产生 L_o，之后的 Optional B hint h(L_o) 与对象数据路径分离。依据：`sections/03-overview.tex:87–91`，`06-layout.tex:14–32,41–47,94–108`。
- **B、s、q 与后端决策**：EC block size B、Shard span s、Verify/read q 分层呈现；q 括号只覆盖 shard 内一个小段，其余以继续符号表示，不虚构固定 shard 数。图注明确 s 是 one-stripe logical shard span、q 是 physical verification/read quantum，并限定 RustFS research backend、B hint 验证与独立 q gate。未把 client hint 当作客户端对 q 的直接赋值，也未声称任意 q 都合法。依据：`sections/03-overview.tex:91–95`，`06-layout.tex:110–133`。
- **重复标识和下标**：U₁ 的 1 与左侧 W₁ 示例关联；g₁/g₂ 在图注被定义为 alternative fixed sizes，不再可能在合读时解释为强制对应两个工作区。Oₚ 的上下两个端口都指同一 packed 对象；图注 `:89–91` 明确 matching ports 和 producer-specific upload contracts。图中未使用数值 p 参与 EC 计算，因此 Oₚ 不会对正文 parity-shard 数 p 增添约束。

未发现新的术语事实错误；原有重要信息——三种可选机制、共享固定基线、私有数据映射、独立只读使用、联合元数据页与定位、客户端对象形成、后端持久布局及可选提示——均保留。格式兼容性、调用路径接线、缓存／写回和后台持久化的完整边界放在正文与图注是合理的；无需把它们全部塞回单栏图。

该结论是标签与连接语义核验，不是新增运行或性能实验的证明。最终 PDF 清晰度、标签遮挡与排版由主任务的编译及页面检查确认。
