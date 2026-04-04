你是一个知识提炼专家。请分析以下原始文档，将其解构为高密度的结构化信息。

## 任务目标
1. **领域判定**：从 `wiki/taxonomy.json` 的已有领域列表中选择最匹配的 `domain`。如果所有现有领域均无法覆盖，可提议新领域——在输出 JSON 中额外添加 `"proposed_domain": {"id": "...", "label": "...", "description": "..."}` 字段。
2. **核心主张**：1-3句，总长度不超过50字。
3. **关键概念**：列出5-10个核心概念及简短定义。
4. **语义关系映射**：分析文档中的逻辑，将其映射到以下 Obsidian 标准关系类型：
   - `supports` (支持), `contradicts` (反驳), `supersedes` (取代)
   - `causes` (导致), `enables` (启用), `extends` (扩展)
   - `defines` (定义), `instances` (实例), `related` (相关)
5. **反向索引种子**：列出 3-5 个“该文档可以回答的问题”。
6. **不确定性标记**：作者存疑、争议结论或需交叉验证的点。

## 输出约束
- 只输出 JSON，不要任何额外文字。
- `relations` 必须包含目标概念及对应的标准 `@类型`。

{
  "domain": "顶级领域名（如：认知科学、金融、系统工程、心理学）",
  "theme": "具体主题名（如：认知偏差、套利策略、反馈控制）",
  "core_claim": "核心主张",
  "key_concepts": [
    {"name": "概念名", "definition": "简短定义"}
  ],
  "semantic_relations": [
    {"source": "来源概念", "target": "目标概念", "type": "supports|contradicts|supersedes|causes|enables|extends|defines|instances|related", "reason": "简短说明"}
  ],
  "answerable_questions": ["问题1", "问题2"],
  "uncertainties": ["待验证点"],
  "source_file": "{{FILE}}"
}

---原始文档---
{{raw_content}}
