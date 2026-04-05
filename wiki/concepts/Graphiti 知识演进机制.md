---
type: concept
domain: knowledge-engineering
theme: 知识管理
supports: ["[[元数据]]"]
extends: ["[[基于 Zep 的 Wiki 语义图谱构建]]"]
---

# Graphiti 知识演进机制

## 定义
Graphiti 知识演进机制（Graphiti Knowledge Evolution Mechanism）是一种基于**双时态（Bitemporal）追踪**和**剧集（Episodes）**模型的新型 RAG（检索增强生成）引擎架构。它不仅能够从非结构化文本中提取实体与关系，更核心的能力在于能够感知知识随时间的变化，自动处理事实间的冲突与失效，实现知识图谱的动态迭代。

## 为什么重要
传统的知识图谱往往是静态的截图，无法应对知识的“保质期”问题：
1. **自动处理冲突**：当新注入的 Episode 包含与旧事实矛盾的信息时（如：项目负责人的变更），Graphiti 能自动推理出结论的变化，而非简单共存。
2. **支持增量构建**：无需重新扫描整个知识库，系统只需处理新增或修改的笔记，极大降低了大规模 Wiki 的维护成本。
3. **保留时序证据**：通过 `invalid_at` 标记，系统在 KuzuDB 中保留了事实的演进历史，用户可以回溯“某个结论在何时被推翻”。

## 如何工作
机制运行依赖于以下四个核心支柱：
1. **剧集模型 (Episodes Model)**：数据被视为一系列有先后顺序或逻辑关联的 Episode。每一篇 Markdown 笔记都被封装为一个带时间戳和元数据的 Episode。
2. **本体引导推理 (Ontology-Guided Inference)**：通过 Pydantic 模型预设实体的属性和关系类型（对应 `taxonomy.json`），引导 LLM 在抽取时遵循特定的业务逻辑，防止标签发散。
3. **版本化状态管理**：
   - **有效事实**：存入图数据库的主活跃区。
   - **失效事实**：被标记上 `invalid_at` 时间戳，在标准检索中予以过滤，但在历史回溯中可见。
4. **混合检索 (Hybrid Retrieval)**：结合了向量相似度（Vector）、关键词匹配（Keyword）以及图遍历（Graph Traversal）的多模态检索策略，能够实现跨文档的复杂关联推理。

## 局限性
- **LLM 调用成本**：每一次 Episode 的注入与推理都依赖大模型，对于海量静态文档的初始化可能带来高昂的 API 开销。
- **KuzuDB 本地化限制**：虽然适合个人或小型团队，但在超大规模、高并发的分布式查询场景下，性能不如成熟的 Neo4j 集群。

## 相关概念
- [[元数据|元数据 @supports]]：Graphiti 利用 Episode 中的 YAML 元数据来锁定事实的时空坐标。
- [[基于 D3.js 的事实溯源可视化|基于 D3.js 的事实溯源可视化 @related]]：本机制是可视化的数据供给层。
- [[基于 Zep 的 Wiki 语义图谱构建|基于 Zep 的 Wiki 语义图谱构建 @supports]]：Graphiti 是该框架的核心演进引擎。

## 来源
- `raw/Clippings/将非结构化的 Wiki 笔记转化为结构化的语义图谱.md`

