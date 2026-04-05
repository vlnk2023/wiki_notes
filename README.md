# 🧠 Wiki Notes: 知识演变系统

> **“真正有效的个人知识库，核心不在于存储，而在于构建可涌现的关系网络。”**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Obsidian Friendly](https://img.shields.io/badge/Editor-Obsidian-purple.svg)](https://obsidian.md/)

`wiki_notes` 是一个以关系为中心的个人知识系统。它超越了传统的“层级文件夹”模式，通过 LLM 增强的自动化工作流，将碎片化的原始摘录转化为具备“工作记忆”属性的动态知识库。

---

## 🌟 核心理念：为什么传统笔记会失效？

### 症状：三个“找不到”
*   **收藏癖**：网页剪藏一堆，真正要用时石沉大海。
*   **孤岛化**：摘录灵感满地，但内容之间没有化学反应。
*   **低效熵增**：笔记存得越多，系统越乱，无法沉淀为个人智慧。

### 范式转移
| 维度 | 传统笔记（文件夹/线性） | **Wiki 关系网络（本项目）** |
| :--- | :--- | :--- |
| **结构方向** | 自上而下预设分类（死板） | **自下而上涌现生长（灵活）** |
| **数据状态** | 存入即成“死数据” | **节点随链接持续激活** |
| **提取前提** | 必须记住它在哪个文件夹 | **从任意入口顺流而下** |
| **关联方式** | 手动标注“参见...” | **双向链接自动溯源** |

---

## 🚀 快速开始

### 1. 环境准备
*   **Python**: 3.11 或更高版本（仅需标准库）。
*   **编辑器**: 推荐使用 [Obsidian](https://obsidian.md/) 打开本仓库根目录。

### 2. 一键编译
运行以下命令初始化或更新你的知识地图：
```powershell
# 重新生成索引、图谱关系及可视化 Canvas
python scripts/compile_wiki.py
```

### 3. LLM 辅助抽取 (CLI 模式)
```powershell
# 针对特定素材生成抽取 Prompt (Stage A)
python scripts/render_prompts.py a raw/Clippings/your_note.md

# 跨领域关系扫描 (Stage C)
python scripts/render_prompts.py c bridge
```

---

## 🔄 核心工作流

本项目遵循 **Andrej Karpathy** 提倡的“工作记忆”构建流程：

1.  **📥 收集 (Collect)**：将原始网页剪藏、想法草稿丢入 `raw/` 目录。
2.  **💎 提炼 (Extract)**：利用 LLM 将素材抽离为原子化的 **概念卡片** (`wiki/concepts/`)。
3.  **🔗 织网 (Relate)**：定义概念间的因果、补充或跨领域连接，记录于 `wiki/relations.json`。
4.  **🗺️ 映射 (Visualize)**：自动生成 `index.md` 和 `.canvas` 知识地图，实现全局导航。
<img width="2485" height="1379" alt="image" src="https://github.com/user-attachments/assets/e05a11df-71f0-43c5-b0b8-3b2e36a383ad" />

---

## 🤖 Gemini CLI 深度集成

本项目已原生支持 `convert-to-wiki` 技能，你可以直接在 Gemini CLI 中使用自然语言指挥：

*   **全流程自动化**：
    > “请对 raw 文件夹中的新文件执行 A->B->C->D->G 的完整编译。”
*   **智能问答**：
    > “根据现有 Wiki 知识，分析『认知杠杆』与『规模效应』的关系。”
*   **库维护**：
    > “帮我扫描 wiki/ 下缺失关联的孤岛概念并建立索引。”

---

## 📂 目录结构说明

```text
D:\vscode_files\test_202603\wiki_notes\
├── wiki/               # 🏆 核心知识库 (概念卡片、索引、关系数据)
│   ├── concepts/       # 原子化笔记
│   ├── graph.json      # 关系图谱数据
│   └── knowledge_map   # 可视化导航 (MD/Canvas)
├── raw/                # 📥 原始素材仓库
├── prompts/            # 📝 LLM 阶段性提示词模板 (A-G 阶段)
├── scripts/            # 🛠️ 自动化编译与渲染脚本
└── README.md           # 📖 你正在阅读的指南
```

---

## 🔗 参考与致敬
*   **理论基础**：[Andrej Karpathy 关于动态知识库的分享](https://x.com/karpathy/status/1841890373447999818)
*   **工具支持**：[Obsidian](https://obsidian.md/) & [Gemini CLI](https://github.com/google/gemini-cli)

---
© 2026 Wiki Notes System. 基于“关系即智慧”的理念构建。
