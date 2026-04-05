# 知识图谱可视化

基于 `wiki/relations.json` 自动生成，仅显示强度 >= 0.8 的关系。

```mermaid
graph LR
  classDef cognition fill:#E8D9BF,stroke:#5B5243,stroke-width:1.5px
  classDef strategy fill:#D8E6F4,stroke:#5B5243,stroke-width:1.5px
  classDef systems fill:#DCE8D1,stroke:#5B5243,stroke-width:1.5px
  classDef finance fill:#E8E0CF,stroke:#5B5243,stroke-width:1.5px
  classDef psychology fill:#F2DEE7,stroke:#5B5243,stroke-width:1.5px
  classDef knowledge_engineering fill:#F2E1D3,stroke:#5B5243,stroke-width:1.5px

  n_53b351986244e43e["AI 增强型学术搜索机制"]
  n_2c0934fe205c06f0["Graphiti 知识演进机制"]
  n_28a9ebf5ef2e915d["事实溯源知识地图"]
  n_0230433970442299["元数据"]
  n_a7a22089f486be33["基于 D3.js 的事实溯源可视化"]
  n_4c8ee607aa2f959b["基于 Zep 的 Wiki 语义图谱构建"]
  n_827af7f8ea54b1ef["睡眠-活力-绩效动态模型"]

  n_0230433970442299 -->|supports| n_28a9ebf5ef2e915d
  n_2c0934fe205c06f0 -->|extends| n_4c8ee607aa2f959b
  n_4c8ee607aa2f959b -->|enables| n_28a9ebf5ef2e915d
  n_a7a22089f486be33 -->|instances| n_28a9ebf5ef2e915d
  n_53b351986244e43e -.->|instances| n_827af7f8ea54b1ef
  n_2c0934fe205c06f0 -->|supports| n_0230433970442299
  n_4c8ee607aa2f959b -->|supports| n_2c0934fe205c06f0
  n_a7a22089f486be33 -->|supports| n_2c0934fe205c06f0
  n_827af7f8ea54b1ef -.->|related| n_53b351986244e43e
  n_28a9ebf5ef2e915d -->|related| n_4c8ee607aa2f959b

  class n_0230433970442299 knowledge_engineering
  class n_28a9ebf5ef2e915d knowledge_engineering
  class n_2c0934fe205c06f0 knowledge_engineering
  class n_4c8ee607aa2f959b knowledge_engineering
  class n_53b351986244e43e knowledge_engineering
  class n_827af7f8ea54b1ef psychology
  class n_a7a22089f486be33 knowledge_engineering
```
