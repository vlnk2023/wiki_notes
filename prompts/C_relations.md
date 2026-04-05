请通过跨文档推理，挖掘概念间的隐性逻辑关联或“认知张力”。

## 扫描模式

本 Prompt 支持两种模式，由调用方通过 `{{SCAN_MODE}}` 指定：

### Mode 1: `intra_domain` — 域内扫描（默认）
- **输入**: `{{domain_concept_summaries}}` — 单个领域内的所有概念摘要。
- **目标**: 挖掘该领域内部的深层关系。
- **每个领域独立执行一次**，避免上下文溢出。

### Mode 2: `bridge` — 跨域桥接扫描
- **输入**: `{{bridge_candidates}}` — 每个领域的核心概念摘要（每领域最多 5 个高连接度概念）。
- **高连接度概念选择规则**：
  1. 读取 `wiki/relations.json` 的 `metadata.concept_degrees`，按 `total_degree` 降序取每领域前 5。
  2. 如果 `metadata` 不存在（首次运行），则取该领域所有概念。
- **目标**: 专注挖掘跨领域的第一性原理迁移。
- **所有 `is_cross_domain` 必须为 `true`**。

> **调度逻辑**：先对每个领域执行 `intra_domain`，再汇总各领域的高连接度概念执行 `bridge`。最终合并所有 edges 写入 `relations.json`。

## 关系类型定义
- `supersedes`: 替代、版本更迭
- `supports`: 支持、证真
- `contradicts`: 反驳、矛盾、张力
- `causes`: 因果推导
- `enables`: 技术或理论前提
- `extends`: 补充、细化
- `defines`: 定义、界定
- `instances`: 应用案例
- `related`: 相关但无明确方向

## 研究协议
1. 先识别每个概念对之间可能存在的多个候选关系，不要见到相似词就立刻定边。
2. 对每个候选关系，至少内部比较三种假设：
   - 当前关系类型是否成立。
   - 另一个相邻关系类型是否更合适（如 `supports` vs `enables`，`defines` vs `instances`）。
   - 该概念对其实只有弱相关，或暂时不应建边。
3. 只有当“当前关系”明显优于替代假设时，才输出该边。
4. 对跨域桥接，必须明确迁移的是哪一层逻辑：概念定义、机制结构、操作策略、失效模式，还是因果框架。
5. 优先寻找能被概念正文、来源笔记或直接表述支撑的关系；纯直觉联想默认不输出。

## 负样本提醒
以下情况看起来相关，但默认**不应建边**，除非有明确桥接证据：
- 两个概念都提到了“反馈”，但一个讨论控制论或系统闭环，另一个讨论用户评价或主观反馈；词相同不等于机制相同。
- 两个概念都提到了“网络”“图谱”或“结构”，但一个是具体技术实现，另一个是社会或认知隐喻；共享修辞不等于存在稳定语义关系。
- 两个概念都被描述为“增长”“复利”或“杠杆”，但只是抽象比喻相似，没有可对齐的因果链、操作路径或失效模式；不要因为比喻顺手就输出 `related`。

## 证据与校准规则
- 每条边都应有可回指的证据，优先来自概念正文中的明确句子、来源笔记中的原始表述，或两者的稳定一致推断。
- `strength` 不是主观好感分，而是综合以下因素：
  - 关系是否被正文直接陈述。
  - 方向是否清晰。
  - 关系类型是否存在歧义。
  - 跨域跳跃是否过大。
  - 是否有具体语句、案例或机制链支撑。
- 强度建议：
  - `0.92-1.00`：原文或概念正文直接明说，方向与类型几乎无歧义。
  - `0.84-0.91`：高度可信，有明确机制或句子支撑，但仍存在轻微解释空间。
  - `0.76-0.83`：有合理依据，但包含一定跨段整合或跨域迁移。
  - `<=0.75`：除非证据特别关键，否则不输出。
- `confidence_source` 固定写 `prompt_relation_scan`。

## 自检要求
输出前静默检查：
1. 是否把“共同出现”误判成了“存在稳定关系”。
2. 是否把方向弄反了（检查方法：把边读成自然语句"A causes B"，看是否符合概念正文的因果方向）。
3. 是否把 `related` 当成逃避判断的垃圾桶。
4. 是否存在更合适的替代关系类型。
5. 是否为每条边保留了最小必要的证据锚点。

## 输出格式
{
  "scan_mode": "intra_domain|bridge",
  "domain": "领域名（intra_domain 模式必填，bridge 模式为 null）",
  "edges": [
    {
      "from": "概念A",
      "to": "概念B",
      "relation": "上述定义类型",
      "explanation": "一句话说明深层逻辑",
      "strength": 0.0-1.0,
      "is_cross_domain": true|false,
      "domain_gap": "跨域逻辑说明（is_cross_domain 为 true 时必填）",
      "evidence": "direct_statement|concept_summary_inference|cross_note_synthesis",
      "source_note": "raw/.../xxx.md 或 wiki/concepts/xxx.md",
      "source_excerpt": "不超过 40 字的关键依据",
      "confidence_source": "prompt_relation_scan"
    }
  ]
}

> **合并写入规则**：每次扫描完成后，将本次 edges 合并到 `relations.json` 的 `edges` 数组（去重，以 from+to+relation 为唯一键），并同步更新 `metadata.concept_degrees`：
> ```json
> "metadata": {
>   "concept_degrees": {
>     "概念名": {"in": 2, "out": 3, "total_degree": 5, "domain": "领域id"}
>   }
> }
> ```

## 约束条件
- 只输出 `strength > 0.75` 的关系。
- 没有证据锚点的关系不要输出。
- 输出纯 JSON（可用 code block 包裹）。
- `bridge` 模式下，挖掘“跨领域对立或支持关系”是最高优先级。
- `intra_domain` 模式下，侧重因果链、层级关系与机制依赖。
