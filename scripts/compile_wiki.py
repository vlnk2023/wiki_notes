from __future__ import annotations

import ast
import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / 'wiki'
CONCEPTS_DIR = WIKI_DIR / 'concepts'
TAXONOMY_PATH = WIKI_DIR / 'taxonomy.json'
RELATIONS_PATH = WIKI_DIR / 'relations.json'
INDEX_PATH = WIKI_DIR / 'index.md'
MAP_PATH = WIKI_DIR / 'knowledge_map.md'
CANVAS_PATH = WIKI_DIR / 'knowledge_map.canvas'
GRAPH_PATH = WIKI_DIR / 'graph.json'

MERMAID_COLORS = {
    'cognition': '#E8D9BF',
    'strategy': '#D8E6F4',
    'systems': '#DCE8D1',
    'finance': '#E8E0CF',
    'psychology': '#F2DEE7',
    'knowledge-engineering': '#F2E1D3',
}

FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n?(.*)$', re.S)


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding='utf-8')


def parse_scalar(value: str):
    value = value.strip()
    if value == '':
        return ''
    if value in {'true', 'false'}:
        return value == 'true'
    if value == 'null':
        return None
    if value.startswith('[') and value.endswith(']'):
        return ast.literal_eval(value)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return ast.literal_eval(value)
    return value


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    frontmatter_text, body = match.groups()
    data: dict[str, object] = {}
    current_list_key: str | None = None
    for raw_line in frontmatter_text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        stripped = line.lstrip()
        if stripped.startswith('- ') and current_list_key:
            data.setdefault(current_list_key, []).append(stripped[2:].strip())
            continue
        key_match = re.match(r'^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$', line)
        if not key_match:
            current_list_key = None
            continue
        key, value = key_match.groups()
        if value == '':
            data[key] = []
            current_list_key = key
        else:
            data[key] = parse_scalar(value)
            current_list_key = None
    return data, body


def sanitize_slug(value: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_]', '_', value)


def mermaid_node_id(value: str) -> str:
    return f'n_{hash_id(f"mermaid:{value}")}'


def mermaid_escape(value: str) -> str:
    return value.replace('\\', '\\\\').replace('"', '\\"')


def hash_id(prefix: str) -> str:
    return hashlib.sha1(prefix.encode('utf-8')).hexdigest()[:16]


def load_taxonomy() -> tuple[list[dict], dict[str, dict]]:
    taxonomy = json.loads(read_text(TAXONOMY_PATH))
    domains = taxonomy['domains']
    domain_map = {domain['id']: domain for domain in domains}
    return domains, domain_map


def load_concepts(domain_map: dict[str, dict]) -> dict[str, dict]:
    concepts: dict[str, dict] = {}
    for path in sorted(CONCEPTS_DIR.glob('*.md')):
        if path.name == '.gitkeep':
            continue
        meta, body = parse_frontmatter(read_text(path))
        title = str(meta.get('title') or path.stem)
        domain = str(meta.get('domain') or '')
        domain_label = str(meta.get('domain_label') or domain_map.get(domain, {}).get('label', domain))
        theme = str(meta.get('theme') or '未分组')
        tags = meta.get('tags') or []
        source_notes = meta.get('source_notes') or []
        concepts[title] = {
            'title': title,
            'domain': domain,
            'domain_label': domain_label,
            'theme': theme,
            'tags': tags if isinstance(tags, list) else [tags],
            'source_notes': source_notes if isinstance(source_notes, list) else [source_notes],
            'status': str(meta.get('status') or 'stable'),
            'updated_at': str(meta.get('updated_at') or ''),
            'file': path.relative_to(ROOT).as_posix(),
            'body': body,
        }
    return concepts


def load_valid_edges(concepts: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    relations = json.loads(read_text(RELATIONS_PATH))
    valid = []
    skipped = []
    concept_names = set(concepts)
    for edge in relations.get('edges', []):
        if edge['from'] in concept_names and edge['to'] in concept_names:
            valid.append(edge)
        else:
            skipped.append(edge)
    return valid, skipped


def compute_degrees(concepts: dict[str, dict], edges: list[dict]) -> dict[str, dict]:
    degrees = {
        name: {'in': 0, 'out': 0, 'total_degree': 0, 'domain': concept['domain']}
        for name, concept in concepts.items()
    }
    for edge in edges:
        degrees[edge['from']]['out'] += 1
        degrees[edge['to']]['in'] += 1
    for degree in degrees.values():
        degree['total_degree'] = degree['in'] + degree['out']
    return degrees


def build_graph_json(concepts: dict[str, dict], edges: list[dict], skipped_edges: list[dict], degrees: dict[str, dict]) -> dict:
    nodes = []
    for concept in sorted(concepts.values(), key=lambda item: (item['domain'], item['theme'], item['title'])):
        nodes.append({
            'id': concept['title'],
            'label': concept['title'],
            'domain': concept['domain'],
            'domain_label': concept['domain_label'],
            'theme': concept['theme'],
            'file': concept['file'],
            'tags': concept['tags'],
            'status': concept['status'],
            'updated_at': concept['updated_at'],
            'source_notes': concept['source_notes'],
        })
    return {
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'concept_degrees': degrees,
            'skipped_edges': skipped_edges,
        },
    }


def build_index(domains: list[dict], concepts: dict[str, dict], edges: list[dict]) -> str:
    lines = ['# Wiki 概念索引', '', '本文件由编译脚本自动维护。', '', '<!-- CONCEPT_INDEX_START -->']
    for domain in domains:
        domain_id = domain['id']
        domain_concepts = [concept for concept in concepts.values() if concept['domain'] == domain_id]
        if not domain_concepts:
            continue
        lines.append(f"# {domain['label']}")
        themes = sorted({concept['theme'] for concept in domain_concepts})
        for theme in themes:
            themed = sorted(concept['title'] for concept in domain_concepts if concept['theme'] == theme)
            lines.append(f'## {theme}')
            for title in themed:
                lines.append(f'- [[{title}]]')
        lines.append('')

    bridge_edges = [edge for edge in edges if edge.get('is_cross_domain')]
    lines.append('# Cross-Domain Bridges')
    if bridge_edges:
        for edge in sorted(bridge_edges, key=lambda item: (item['from'], item['to'], item['relation'])):
            lines.append(f"- [[{edge['from']}]] -> [[{edge['to']}]]：{edge['explanation']}")
    else:
        lines.append('- 暂无跨领域桥接关系')
    lines.append('<!-- CONCEPT_INDEX_END -->')
    return '\n'.join(lines) + '\n'


def build_mermaid_map(domains: list[dict], concepts: dict[str, dict], edges: list[dict]) -> str:
    lines = [
        '# 知识图谱可视化',
        '',
        '基于 `wiki/relations.json` 自动生成，仅显示强度 >= 0.8 的关系。',
        '',
        '```mermaid',
        'graph LR',
    ]
    for domain in domains:
        class_name = sanitize_slug(domain['id'])
        fill = MERMAID_COLORS.get(domain['id'], '#E2E2E2')
        lines.append(f'  classDef {class_name} fill:{fill},stroke:#5B5243,stroke-width:1.5px')
    lines.append('')

    strong_edges = [edge for edge in edges if float(edge.get('strength', 0)) >= 0.8]
    node_ids: dict[str, str] = {}
    node_classes: dict[str, str] = {}
    for edge in strong_edges:
        source_name = edge['from']
        target_name = edge['to']
        source = concepts[source_name]
        target = concepts[target_name]
        source_class = sanitize_slug(source['domain'])
        target_class = sanitize_slug(target['domain'])
        node_ids.setdefault(source_name, mermaid_node_id(source_name))
        node_ids.setdefault(target_name, mermaid_node_id(target_name))
        node_classes[node_ids[source_name]] = source_class
        node_classes[node_ids[target_name]] = target_class

    if node_ids:
        for node_name, node_id in sorted(node_ids.items()):
            lines.append(f'  {node_id}["{mermaid_escape(node_name)}"]')
        lines.append('')

    for edge in strong_edges:
        source_id = node_ids[edge['from']]
        target_id = node_ids[edge['to']]
        arrow = '-.->' if edge.get('is_cross_domain') else '-->'
        lines.append(f'  {source_id} {arrow}|{edge["relation"]}| {target_id}')

    if node_classes:
        lines.append('')
        for node_id, cls in sorted(node_classes.items()):
            lines.append(f'  class {node_id} {cls}')

    lines.extend(['```', ''])
    return '\n'.join(lines)


def choose_sides(source_xy: tuple[int, int], target_xy: tuple[int, int]) -> tuple[str, str]:
    dx = target_xy[0] - source_xy[0]
    dy = target_xy[1] - source_xy[1]
    if abs(dx) >= abs(dy):
        return ('right', 'left') if dx >= 0 else ('left', 'right')
    return ('bottom', 'top') if dy >= 0 else ('top', 'bottom')


def build_canvas(domains: list[dict], concepts: dict[str, dict], edges: list[dict]) -> dict:
    active_domains = [domain for domain in domains if any(concept['domain'] == domain['id'] for concept in concepts.values())]
    nodes = []
    edges_out = []
    node_ids: dict[str, str] = {}
    positions: dict[str, tuple[int, int]] = {}
    total = max(len(active_domains), 1)
    radius = 1500
    cols = 3
    node_width = 260
    node_height = 120
    gap_x = 320
    gap_y = 180
    padding = 80

    for index, domain in enumerate(active_domains):
        domain_concepts = sorted(
            [concept for concept in concepts.values() if concept['domain'] == domain['id']],
            key=lambda item: (item['theme'], item['title']),
        )
        rows = math.ceil(len(domain_concepts) / cols)
        inner_width = max(cols * gap_x, node_width)
        inner_height = max(rows * gap_y, node_height)
        group_width = inner_width + padding * 2
        group_height = inner_height + padding * 2
        angle = (2 * math.pi * index / total) - (math.pi / 2)
        center_x = round(math.cos(angle) * radius)
        center_y = round(math.sin(angle) * radius)
        group_x = center_x - group_width // 2
        group_y = center_y - group_height // 2
        group_id = hash_id(f'group:{domain["id"]}')
        color = str(index + 1)
        nodes.append({
            'id': group_id,
            'type': 'group',
            'label': domain['label'],
            'x': group_x,
            'y': group_y,
            'width': group_width,
            'height': group_height,
            'color': color,
        })
        for concept_index, concept in enumerate(domain_concepts):
            row, col = divmod(concept_index, cols)
            x = group_x + padding + col * gap_x
            y = group_y + padding + row * gap_y
            node_id = hash_id(f'node:{concept["title"]}')
            node_ids[concept['title']] = node_id
            positions[concept['title']] = (x + node_width // 2, y + node_height // 2)
            nodes.append({
                'id': node_id,
                'type': 'file',
                'file': concept['file'],
                'x': x,
                'y': y,
                'width': node_width,
                'height': node_height,
                'color': color,
            })

    for edge in edges:
        source_id = node_ids[edge['from']]
        target_id = node_ids[edge['to']]
        from_side, to_side = choose_sides(positions[edge['from']], positions[edge['to']])
        edge_item = {
            'id': hash_id(f"edge:{edge['from']}:{edge['to']}:{edge['relation']}"),
            'fromNode': source_id,
            'toNode': target_id,
            'fromSide': from_side,
            'toSide': to_side,
            'label': edge['relation'],
        }
        if edge.get('is_cross_domain'):
            edge_item['style'] = 'dashed'
        if edge.get('relation') == 'contradicts':
            edge_item['color'] = '6'
        edges_out.append(edge_item)
    return {'nodes': nodes, 'edges': edges_out}


def main() -> None:
    domains, domain_map = load_taxonomy()
    concepts = load_concepts(domain_map)
    valid_edges, skipped_edges = load_valid_edges(concepts)
    degrees = compute_degrees(concepts, valid_edges)

    write_text(GRAPH_PATH, json.dumps(build_graph_json(concepts, valid_edges, skipped_edges, degrees), ensure_ascii=False, indent=2) + '\n')
    write_text(INDEX_PATH, build_index(domains, concepts, valid_edges))
    write_text(MAP_PATH, build_mermaid_map(domains, concepts, valid_edges))
    write_text(CANVAS_PATH, json.dumps(build_canvas(domains, concepts, valid_edges), ensure_ascii=False, indent=2) + '\n')

    print(f'Compiled {len(concepts)} concepts and {len(valid_edges)} edges.')
    if skipped_edges:
        print(f'Skipped {len(skipped_edges)} edges referencing unknown concepts.')


if __name__ == '__main__':
    main()
