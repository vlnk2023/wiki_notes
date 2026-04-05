你是一个知识提炼专家。请分析以下原始文档，将其解构为“一组可写成高质量概念卡片”的结构化信息。

## 任务目标
1. **先拆概念卡**：先判断原文适合沉淀为几个可独立成文的概念卡，再逐卡抽取。目标是输出 `concept_cards[]`，而不是把整篇材料压成一个总 JSON。
2. **逐卡领域判定**：对每张概念卡，从 `wiki/taxonomy.json` 的已有领域列表中选择最匹配的 `domain`。如果所有现有领域均无法覆盖，可在该卡中额外添加 `"proposed_domain": {"id": "...", "label": "...", "description": "..."}`。
3. **逐卡概念类型判定**：判断每张概念卡更接近 `object|mechanism|strategy|framework|case` 中的哪一类。
4. **保留核心骨架**：优先抽取核心主张、关键概念、核心论证单元、逻辑链、机制链、成立条件、失效条件、关键案例、独特观点。
5. **为下游写作提供可校验输入**：尽量让抽象结论能被具体案例、具体表述或清晰推理链支撑。

## 允许的领域列表（taxonomy）
从以下领域中选择 `domain`，不得使用列表外的值（如无匹配可在卡片中添加 `proposed_domain`）：

{{TAXONOMY}}

## 先拆卡，再抽取
### 1. 拆卡规则
- 一篇原文可以输出 1-N 张概念卡。
- 只有当一个概念能够支撑“独立标题 + 独立主张 + 独立正文结构”时，才单独成卡。
- 如果某个概念只是服务于另一个更大概念的局部例子、子类型或解释部件，优先保留在主卡的 `key_concepts`、`argument_units` 或 `evidence_examples` 中，而不是强行拆成单独卡。
- 高度近义、只是在不同表述层面重复同一主张的内容，应合并为一张卡，不要拆成多张弱卡。

### 2. 主卡与辅卡
- `card_role = primary`：该概念是本文主要沉淀对象，足以单独写成 Wiki 条目。
- `card_role = supporting`：该概念在本文中有独立价值，但证据密度或篇幅略弱，通常作为次级条目。
- 如果全文只能稳定支撑一张卡，就只输出一张 `primary` 卡。

## 两轮抽取协议
### 第一轮：确定卡集合与核心骨架
先确定 `concept_cards[]` 的成员，再对每张卡只抽以下最小必需信息：
- `concept`
- `card_role`
- `domain`
- `theme`
- `concept_type`
- `core_claim`
- `key_concepts`
- `argument_units`
- `source_file`

### 第二轮：按需增强
只有在某张卡对应的原文材料确实提供了相应信息时，才为该卡补充以下字段：
- `logic_chain`
- `mechanism_chain`
- `applicability`
- `evidence_examples`
- `distinctive_views`
- `semantic_relations`
- `answerable_questions`
- `uncertainties`
- `extended_info`

如果一张普通概念卡不需要某些增强字段，就不要为了凑完整而硬填。信息密度优先于字段齐全。

## 字段适用规则
- `logic_chain`：只在原文存在明确的前提 -> 推导 -> 结论、因果链、决策路径或论证步骤时输出。`case`、`strategy`、`framework` 类型通常更常见。
- `mechanism_chain`：只在原文解释了结构层次、运行机制、操作流程或反馈回路时输出。`mechanism`、`object`、`strategy` 类型更常见；`case` 类型只有在案例中能抽出可迁移机制时才输出。
- `applicability`：只保留会改变结论成立范围的前提、边界、失效条件、代价与风险。
- `evidence_examples`：如果原文靠案例、故事、类比、数据点支撑论证，就必须输出；若原文几乎全是概念阐释，可不输出。
- `distinctive_views`：只保留作者真正有辨识度、不可被抽象化抹平的观点。没有就省略。
- `extended_info`：只保留虽然不属于核心骨架、但有助于检索、延展和后续写作的内容。不要把剩余边角料都塞进来。
- `uncertainties`：只记录原文中的真实争议、保留意见、证据不足点或需要交叉验证的问题。不要机械补“可能存在局限”。
- `semantic_relations`：只在当前卡的 `concept` 与其他概念之间存在明确关系，或关系可被稳定推断时输出。不要为建立图谱而过度联想。每条关系必须包含当前卡概念作为 `source` 或 `target`，并优先让当前卡概念作为 `source`（若方向合理）。

## 硬性约束
- 所有承担论证功能的案例、举例、故事必须保留到对应概念卡的输出中。
- 所有核心论点和独特观点必须保留原语义，不得为了整洁而抽象化抹平。
- 所有因果逻辑、推理步骤、判断前提必须完整呈现，不能只剩起点和结论。
- 所有数据、时间、人名、机构名、地点、专有名词等具体信息，如对论证有作用，不得省略。
- 不确定是否保留时，默认保留。

## 抽取原则
- 目标不是做摘要，而是为下游写作保留逻辑骨架。
- 优先保留：核心命题、核心逻辑链、机制链、成立条件、失效条件、关键案例、反例、争议、独特观点。
- 可以压缩：修辞、重复表达、铺垫性背景。
- 如果某条信息一旦删除就会让结论变形、适用范围改变，或让“为什么/如何”断裂，它就必须进入输出。

## 自检要求
输出前静默检查：
1. 是否有任何关键案例、故事、数据点、人名、时间被遗漏。
2. 是否有任何核心论点被改写得比原文更空泛。
3. 是否有任何推理链从“前提 -> 推导 -> 结论”被压成了单句结论。
4. 是否把本应留在同一张卡里的内容过度拆散，或把本应独立成卡的内容混成了一团。
5. 是否有任何增强字段只是为了凑 schema 而填写，实际并不增加信息。
6. 如有遗漏、抽象化过度、拆卡失衡或字段滥填，先修正再输出。

## 输出约束
- 只输出 JSON，不要任何额外文字。
- 输出顶层必须是文档级封装，至少包含 `source_file` 与 `concept_cards`。
- `concept_cards` 中每个条目的核心字段必须输出；增强字段只有在适用时才输出，可省略。
- `proposed_domain` 仅在该卡无法落入现有领域时输出，否则省略。
- `semantic_relations` 必须是当前卡的局部关系表，且每条边都包含当前卡概念。
- `argument_units` 中每个条目都要写清 `role`、`point`、`reason`。
- `logic_chain` 和 `mechanism_chain` 没有就直接省略；不要为了完整性编造空洞链条。
- `evidence_examples` 必须保留关键细节，不要只写“某案例说明了什么”。
- `distinctive_views` 应优先保留作者原创性高的判断，而不是常识句。
- 如果原文里出现多个概念，但其中某些概念不足以独立成文，不要硬拆卡；把它们留在更强主卡中。

以下是推荐输出结构示意。实际输出时，只保留适用字段。

{
  "source_file": "{{FILE}}",
  "concept_cards": [
    {
      "concept": "概念名",
      "card_role": "primary|supporting",
      "domain": "顶级领域 id（如：cognition、strategy、systems）",
      "proposed_domain": {"id": "...", "label": "...", "description": "..."},
      "theme": "具体主题名（如：认知偏差、套利策略、反馈控制）",
      "concept_type": "object|mechanism|strategy|framework|case",
      "core_claim": "该概念卡的核心主张",
      "key_concepts": [
        {"name": "概念名", "definition": "简短定义"}
      ],
      "argument_units": [
        {
          "role": "definition|importance|mechanism|condition|limitation|evidence|counterpoint",
          "point": "不可丢失的论点或信息",
          "reason": "如果删掉，会损失什么逻辑"
        }
      ],
      "logic_chain": [
        {
          "step": 1,
          "type": "premise|inference|conclusion|counterpoint",
          "content": "该步推理的具体内容"
        }
      ],
      "mechanism_chain": [
        {
          "stage": "触发条件|中介机制|结果|反馈|步骤1|步骤2",
          "detail": "该阶段发生了什么"
        }
      ],
      "applicability": {
        "preconditions": ["前提条件1"],
        "scope_boundaries": ["适用边界1"],
        "failure_modes": ["失效条件或副作用1"]
      },
      "evidence_examples": [
        {
          "type": "case|story|example|analogy|data|observation",
          "content": "案例、故事或证据内容，保留关键细节",
          "supports": "它支撑的论点"
        }
      ],
      "distinctive_views": ["不应被抽象化抹平的独特观点"],
      "extended_info": ["有助于检索、理解或后续扩展的补充信息"],
      "semantic_relations": [
        {"source": "当前概念或相关概念", "target": "目标概念", "type": "supports|contradicts|supersedes|causes|enables|extends|defines|instances|related", "reason": "简短说明"}
      ],
      "answerable_questions": ["问题1", "问题2"],
      "uncertainties": ["待验证点"],
      "source_file": "{{FILE}}"
    }
  ]
}

---原始文档---
{{raw_content}}
