你是一个 Wiki 架构维护者。请执行索引增量更新与反向链接扫描。

## 当前状态
- 当前 Wiki 索引：{{current_index_md}}
- 新增/更新的文章：{{new_additions}}

## 任务目标
1. **领域聚类**：将新概念归入 `index.md` 中对应的领域（Domain）和主题（Theme）下。
2. **跨领域识别**：如果概念具有跨领域通用性（Cross-Domain Commonalities），将其标记在”跨领域基石”板块。
3. **Backlink 回填发现**：检查已有的 Wiki 文章，看哪些内容应该新增指向这些新概念的 `[[双链]]` 或 `@关系`。

> **注意**：`index.md`、`knowledge_map.md`、`knowledge_map.canvas` 的实际写入由 `scripts/compile_wiki.py` 负责。本阶段只输出”需要做什么”，不直接生成最终文件内容。

## 输出约束
输出包含三个板块：

1. **Index Changes**：
   列出需要在 `index.md` 中新增或移动的条目，格式：
   - `新增 [[概念名]] 到 Domain > Theme`
   - `移动 [[概念名]] 从 Domain A > Theme X 到 Domain B > Theme Y`
   > 保留 `<!-- CONCEPT_INDEX_START -->` 和 `<!-- CONCEPT_INDEX_END -->` 标记，只替换标记之间的内容。

2. **Cross-Domain Bridges**：
   列出本次更新发现的跨领域桥接点及其逻辑。

3. **Update Tasks**：
   列出需要手动（或由 Agent 下一步）修改的文章。
   格式：`- [ ] [[旧文章名]]: 在哪一段插入 [[新概念|描述 @关系]]`

## 保持扁平与聚类
主分类必须是物理领域（Domain，来自 `wiki/taxonomy.json`），子分类为逻辑主题（Theme）。

