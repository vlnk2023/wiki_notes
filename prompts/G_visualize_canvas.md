# Stage G: Visualize Canvas Contract

## Objective
Convert `wiki/relations.json` into a standards-compliant `.canvas` file for Obsidian, following the JSON Canvas Spec 1.0.

## Input Context
- **Relations Graph**: `wiki/relations.json` (with `metadata.concept_degrees`)
- **Domain Taxonomy**: `wiki/taxonomy.json`
- **Concept Files**: List of `.md` files in `wiki/concepts/`

## Visualization Rules (Heuristics)

### 1. Identity & Node Types
- **IDs**: All nodes and edges must have 16-character lowercase hexadecimal IDs.
- **Node Type**: Every concept is a `file` node pointing to `wiki/concepts/<name>.md`.
- **Groups**: Use `group` nodes to encapsulate concepts belonging to the same `domain` from `wiki/taxonomy.json`.

### 2. Layout & Positioning
- **Coordinate System**: X increases right, Y increases down.
- **Domain Clustering**:
  - Assign each `domain` a central (X, Y) coordinate.
  - Distribute `domain` centers in a circle (radius 1500px).
  - Arrange concepts within their domain group in a grid (3 columns, 400px spacing).
- **Node Size**: Default concept nodes to `width: 260`, `height: 120`.
- **Group Sizing**: Calculate the bounding box for each domain group and add 50px padding.

### 3. Styling & Relationships
- **Colors**: Assign colors `1` through `6` based on the domain index in `taxonomy.json`.
- **Edges**: 
  - Use `fromSide: "right"` and `toSide: "left"` for standard flow.
  - `label`: Display the relationship type (e.g., `supports`, `contradicts`).
  - `style`: Use `"dashed"` for `is_cross_domain: true` edges.
  - `color`: Use a specific color (e.g., red) for `contradicts` relations.

## Output Format
A pure JSON file saved to `wiki/knowledge_map.canvas`.

```json
{
  "nodes": [
    {
      "id": "16charhexid0001",
      "type": "group",
      "label": "Cognition",
      "x": -100, "y": -100, "width": 1000, "height": 800,
      "color": "1"
    },
    {
      "id": "16charhexid0002",
      "type": "file",
      "file": "wiki/concepts/认知杠杆.md",
      "x": 50, "y": 50, "width": 260, "height": 120,
      "color": "1"
    }
  ],
  "edges": [
    {
      "id": "16charhexid0003",
      "fromNode": "16charhexid0002",
      "toNode": "...",
      "fromSide": "right",
      "toSide": "left",
      "label": "enables"
    }
  ]
}
```
