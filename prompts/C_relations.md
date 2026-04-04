请通过跨文档推理，挖掘概念间的隐性逻辑关联或"认知张力"。

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
      "domain_gap": "跨域逻辑说明（is_cross_domain 为 true 时必填）"
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
- 只输出 `strength > 0.7` 的关系。
- 输出纯 JSON（可用 code block 包裹）。
- `bridge` 模式下，挖掘"跨领域对立或支持关系"是最高优先级。
- `intra_domain` 模式下，侧重因果链和层级关系。
