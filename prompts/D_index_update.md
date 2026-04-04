你是一个 Wiki 架构维护者。请执行索引增量更新与反向链接扫描。

## 当前状态
- 当前 Wiki 索引：{{current_index_md}}
- 新增/更新的文章：{{new_additions}}

## 任务目标
1. **领域聚类**：将新概念归入 `index.md` 中对应的领域（Domain）和主题（Theme）下。
2. **跨领域识别**：如果概念具有跨领域通用性（Cross-Domain Commonalities），将其标记在“跨领域基石”板块。
3. **Backlink 回填发现**：检查已有的 Wiki 文章，看哪些内容应该新增指向这些新概念的 `[[双链]]` 或 `@关系`。

## 输出约束
输出包含四个板块：

1. **New Index**：
   完整的、按领域组织的 `index.md` 内容。
   结构：`# Domain` -> `## Theme` -> `[[Concept]]`。
   > 保留 `<!-- CONCEPT_INDEX_START -->` 和 `<!-- CONCEPT_INDEX_END -->` 标记，只替换标记之间的内容。

2. **Cross-Domain Bridges**：
   列出本次更新发现的跨领域桥接点及其逻辑。

3. **Update Tasks**：
   列出需要手动（或由 Agent 下一步）修改的文章。
   格式：`- [ ] [[旧文章名]]: 在哪一段插入 [[新概念|描述 @关系]]`

## 保持扁平与聚类
主分类必须是物理领域（Domain，来自 `wiki/taxonomy.json`），子分类为逻辑主题（Theme）。

4. **Knowledge Map**：
   基于 `wiki/relations.json` 生成 Mermaid 图，保存到 `wiki/knowledge_map.md`。
   规则：
   - 节点按领域着色（用 `classDef` 定义每个 domain 的颜色）。
   - 只绘制 `strength >= 0.8` 的边。
   - `is_cross_domain: true` 的边用虚线（`-.->`)，域内边用实线（`-->`）。
   - 边标签为关系类型。
   格式示例：
   ```
   ```mermaid
   graph LR
     classDef cognition fill:#E8D5B7
     classDef strategy fill:#B7D5E8
     认知杠杆:::cognition -->|enables| 制度套利:::strategy
     去自然化能力:::cognition -.->|enables| 认知杠杆:::cognition
   ```
   ```

