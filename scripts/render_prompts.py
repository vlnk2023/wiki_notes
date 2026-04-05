from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"
TMP_DIR = ROOT / "tmp" / "prompt_runs"
INDEX_PATH = ROOT / "wiki" / "index.md"
TAXONOMY_PATH = ROOT / "wiki" / "taxonomy.json"
EXTRACT_DIR = ROOT / "raw" / ".extracted"
MIGRATED_DIR = ROOT / "raw" / ".extracted_v2"
QUOTE_CHARS = "\"'“”‘’「」『』"
CARD_REQUIRED_FIELDS = ["concept", "card_role", "domain", "theme", "concept_type", "core_claim", "key_concepts", "argument_units", "source_file"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_template(template: str, mapping: dict[str, str]) -> str:
    rendered = template
    for key, value in mapping.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def slugify(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]", "_", value)
    value = re.sub(r"\s+", "_", value.strip())
    return value or "untitled"


def normalize_lookup(value: str) -> str:
    table = str.maketrans("", "", QUOTE_CHARS)
    cleaned = value.translate(table)
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned.casefold()


def resolve_existing_path(path: Path) -> Path:
    if path.exists():
        return path
    parent = path.parent
    if not parent.exists():
        return path
    target = normalize_lookup(path.name)
    for candidate in parent.iterdir():
        if normalize_lookup(candidate.name) == target:
            return candidate
    return path


def resolve_from_root(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    return resolve_existing_path(candidate)


def ensure_existing_file(path: Path, label: str) -> Path:
    resolved = resolve_existing_path(path)
    if resolved.exists():
        return resolved
    rel_path = path.relative_to(ROOT).as_posix() if path.is_absolute() and ROOT in path.parents else str(path)
    raise SystemExit(f"{label} not found: {rel_path}")


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            return parts[1]
    return text


def extract_snippets(path: Path, max_chars: int = 1600, max_blocks: int = 6) -> str:
    path = resolve_existing_path(path)
    if not path.exists():
        return ""
    text = strip_frontmatter(read_text(path)).strip()
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    chosen: list[str] = []
    total = 0
    for block in blocks:
        compact = re.sub(r"\n{2,}", "\n", block)
        if total + len(compact) > max_chars and chosen:
            break
        chosen.append(compact)
        total += len(compact)
        if len(chosen) >= max_blocks or total >= max_chars:
            break
    return "\n\n".join(chosen)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(resolve_existing_path(path)))


def load_taxonomy() -> dict[str, Any]:
    if not TAXONOMY_PATH.exists():
        return {}
    return load_json(TAXONOMY_PATH)


def taxonomy_domain_keys() -> set[str]:
    taxonomy = load_taxonomy()
    keys: set[str] = set()
    for domain in taxonomy.get("domains", []):
        if not isinstance(domain, dict):
            continue
        for key in [domain.get("id"), domain.get("label")]:
            if isinstance(key, str) and key.strip():
                keys.add(key.strip())
        for alias in domain.get("aliases", []):
            if isinstance(alias, str) and alias.strip():
                keys.add(alias.strip())
    return keys


def taxonomy_alias_map() -> dict[str, str]:
    taxonomy = load_taxonomy()
    mapping: dict[str, str] = {}
    for domain in taxonomy.get("domains", []):
        if not isinstance(domain, dict):
            continue
        domain_id = str(domain.get("id") or "").strip()
        if not domain_id:
            continue
        for candidate in [domain_id, domain.get("label"), *(domain.get("aliases") or [])]:
            if isinstance(candidate, str) and candidate.strip():
                mapping[candidate.strip()] = domain_id
    return mapping


def canonicalize_domain(value: str, alias_map: dict[str, str]) -> tuple[str, str | None]:
    stripped = value.strip()
    if not stripped:
        return "", None
    canonical = alias_map.get(stripped, stripped)
    if canonical != stripped:
        return canonical, stripped
    return canonical, None


def derive_legacy_concept(extract_data: dict[str, Any], fallback_name: str) -> str:
    concept = extract_data.get("concept")
    if isinstance(concept, str) and concept.strip():
        return concept.strip()
    key_concepts = extract_data.get("key_concepts")
    if isinstance(key_concepts, list) and key_concepts:
        first = key_concepts[0]
        if isinstance(first, dict):
            name = first.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
        if isinstance(first, str) and first.strip():
            return first.strip()
    return fallback_name


def normalize_extract(extract_data: dict[str, Any], fallback_name: str) -> dict[str, Any]:
    source_file = str(extract_data.get("source_file") or "")
    cards = extract_data.get("concept_cards")
    if isinstance(cards, list) and cards:
        normalized_cards = []
        for card in cards:
            if not isinstance(card, dict):
                continue
            next_card = dict(card)
            next_card.setdefault("source_file", source_file)
            next_card.setdefault("card_role", "primary")
            normalized_cards.append(next_card)
        if normalized_cards:
            return {
                "source_file": source_file,
                "concept_cards": normalized_cards,
            }

    legacy_card = {
        "concept": derive_legacy_concept(extract_data, fallback_name),
        "card_role": "primary",
        "domain": extract_data.get("domain", ""),
        "theme": extract_data.get("theme", ""),
        "concept_type": extract_data.get("concept_type", ""),
        "core_claim": extract_data.get("core_claim", ""),
        "key_concepts": extract_data.get("key_concepts", []),
        "argument_units": extract_data.get("argument_units", []),
        "logic_chain": extract_data.get("logic_chain", []),
        "mechanism_chain": extract_data.get("mechanism_chain", []),
        "applicability": extract_data.get("applicability", {}),
        "evidence_examples": extract_data.get("evidence_examples", []),
        "distinctive_views": extract_data.get("distinctive_views", []),
        "extended_info": extract_data.get("extended_info", []),
        "semantic_relations": extract_data.get("semantic_relations", []),
        "answerable_questions": extract_data.get("answerable_questions", []),
        "uncertainties": extract_data.get("uncertainties", []),
        "source_file": source_file,
    }
    return {
        "source_file": source_file,
        "concept_cards": [legacy_card],
    }


def infer_concept_type(card: dict[str, Any]) -> str:
    text_parts = [
        str(card.get("concept") or ""),
        str(card.get("theme") or ""),
        str(card.get("core_claim") or ""),
    ]
    for item in card.get("key_concepts") or []:
        if isinstance(item, dict):
            text_parts.append(str(item.get("name") or ""))
            text_parts.append(str(item.get("definition") or ""))
    text = " ".join(text_parts)

    keyword_groups = [
        ("case", ["案例", "个案", "事件", "故事", "实验", "复盘"]),
        ("framework", ["框架", "分类", "地图", "图谱", "体系", "范式"]),
        ("strategy", ["策略", "方法", "思维", "套利", "战术", "路径", "打法", "防御"]),
        ("mechanism", ["机制", "效应", "闭环", "回路", "触发", "反馈", "分配", "过程"]),
    ]
    for concept_type, keywords in keyword_groups:
        if any(keyword in text for keyword in keywords):
            return concept_type
    return "object"


def definition_from_card(card: dict[str, Any]) -> str:
    concept = str(card.get("concept") or "").strip()
    for item in card.get("key_concepts") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        definition = str(item.get("definition") or "").strip()
        if name == concept and definition:
            return definition
    for item in card.get("key_concepts") or []:
        if isinstance(item, dict):
            definition = str(item.get("definition") or "").strip()
            if definition:
                return definition
    return ""


def synthesize_argument_units(card: dict[str, Any]) -> list[dict[str, str]]:
    concept = str(card.get("concept") or "").strip() or "该概念"
    units: list[dict[str, str]] = []
    definition = definition_from_card(card)
    core_claim = str(card.get("core_claim") or "").strip()
    if definition:
        units.append(
            {
                "role": "definition",
                "point": f"{concept}：{definition}",
                "reason": "缺少定义锚点，下游写作无法稳定判断条目边界。",
            }
        )
    if core_claim:
        units.append(
            {
                "role": "importance",
                "point": core_claim,
                "reason": "这是当前条目的核心主张，决定正文主线与重要性展开。",
            }
        )
    if not units:
        units.append(
            {
                "role": "definition",
                "point": concept,
                "reason": "至少需要一个基础论证单元来承接定义段。",
            }
        )
    return units


def localize_relations(card: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    concept = str(card.get("concept") or "").strip()
    relations = card.get("semantic_relations") or []
    if not isinstance(relations, list):
        return [], 0
    kept: list[dict[str, Any]] = []
    dropped = 0
    for edge in relations:
        if not isinstance(edge, dict):
            dropped += 1
            continue
        source = str(edge.get("source") or "").strip()
        target = str(edge.get("target") or edge.get("to") or "").strip()
        if concept not in {source, target}:
            dropped += 1
            continue
        normalized_edge = dict(edge)
        if "target" not in normalized_edge and target:
            normalized_edge["target"] = target
        if "type" not in normalized_edge and edge.get("relation"):
            normalized_edge["type"] = edge.get("relation")
        kept.append(normalized_edge)
    return kept, dropped


def migrate_extract_data(extract_data: dict[str, Any], fallback_name: str, alias_map: dict[str, str]) -> tuple[dict[str, Any], dict[str, int]]:
    normalized = normalize_extract(extract_data, fallback_name)
    stats = {
        "legacy_wrapped": 0,
        "concept_type_filled": 0,
        "argument_units_filled": 0,
        "relations_filtered": 0,
        "domain_canonicalized": 0,
    }
    if "concept_cards" not in extract_data:
        stats["legacy_wrapped"] += 1

    migrated_cards: list[dict[str, Any]] = []
    top_source_file = str(normalized.get("source_file") or extract_data.get("source_file") or "")
    for card in normalized.get("concept_cards") or []:
        if not isinstance(card, dict):
            continue
        next_card = dict(card)
        next_card.setdefault("source_file", top_source_file)
        next_card.setdefault("card_role", "primary")

        domain = str(next_card.get("domain") or "")
        canonical_domain, domain_label = canonicalize_domain(domain, alias_map)
        if canonical_domain:
            next_card["domain"] = canonical_domain
        if domain_label:
            next_card.setdefault("domain_label", domain_label)
            stats["domain_canonicalized"] += 1

        if not str(next_card.get("concept_type") or "").strip():
            next_card["concept_type"] = infer_concept_type(next_card)
            stats["concept_type_filled"] += 1

        if not isinstance(next_card.get("argument_units"), list) or not next_card.get("argument_units"):
            next_card["argument_units"] = synthesize_argument_units(next_card)
            stats["argument_units_filled"] += 1

        localized_relations, dropped = localize_relations(next_card)
        if dropped:
            stats["relations_filtered"] += dropped
        next_card["semantic_relations"] = localized_relations

        migrated_cards.append(next_card)

    migrated = {
        "source_file": top_source_file,
        "concept_cards": migrated_cards,
    }
    return migrated, stats


def semantic_yaml_for(card: dict[str, Any]) -> str:
    concept = str(card.get("concept") or "").strip()
    grouped: dict[str, list[str]] = {}
    for edge in card.get("semantic_relations") or []:
        if not isinstance(edge, dict):
            continue
        if str(edge.get("source") or "").strip() != concept:
            continue
        relation = str(edge.get("type") or edge.get("relation") or "").strip()
        target = str(edge.get("target") or edge.get("to") or "").strip()
        if not relation or not target:
            continue
        grouped.setdefault(relation, [])
        link = f"[[{target}]]"
        if link not in grouped[relation]:
            grouped[relation].append(link)

    if not grouped:
        return "# no outgoing semantic relations from current concept card"

    lines: list[str] = []
    for relation in sorted(grouped):
        lines.append(f"{relation}:")
        for link in grouped[relation]:
            lines.append(f'  - "{link}"')
    return "\n".join(lines)


def select_cards(cards: list[dict[str, Any]], concept: str | None, all_cards: bool) -> list[dict[str, Any]]:
    if concept:
        for card in cards:
            if str(card.get("concept") or "").strip() == concept:
                return [card]
        available = ", ".join(str(card.get("concept") or "") for card in cards)
        raise SystemExit(f"Concept not found: {concept}. Available: {available}")
    if all_cards or len(cards) != 1:
        return cards
    return [cards[0]]


def taxonomy_summary() -> str:
    taxonomy = load_taxonomy()
    lines: list[str] = []
    for domain in taxonomy.get("domains", []):
        if not isinstance(domain, dict):
            continue
        domain_id = domain.get("id", "")
        label = domain.get("label", "")
        description = domain.get("description", "")
        aliases = ", ".join(domain.get("aliases") or [])
        line = f"- `{domain_id}` ({label})"
        if aliases:
            line += f" — 别名: {aliases}"
        if description:
            line += f" — {description}"
        lines.append(line)
    return "\n".join(lines) if lines else "(taxonomy not found)"


def render_stage_a(raw_file: Path, output_dir: Path) -> list[Path]:
    raw_file = ensure_existing_file(raw_file, "Raw file")
    template = read_text(PROMPTS_DIR / "A_extract.md")
    rendered = render_template(
        template,
        {
            "FILE": raw_file.relative_to(ROOT).as_posix() if raw_file.is_absolute() else raw_file.as_posix(),
            "raw_content": read_text(raw_file),
            "TAXONOMY": taxonomy_summary(),
        },
    )
    output_path = output_dir / f"{slugify(raw_file.stem)}.prompt.md"
    write_text(output_path, rendered)
    return [output_path]


def render_stage_b(extract_json: Path, output_dir: Path, concept: str | None, all_cards: bool) -> list[Path]:
    extract_json = ensure_existing_file(extract_json, "Extract JSON")
    template = read_text(PROMPTS_DIR / "B_write_wiki.md")
    extract_data = normalize_extract(load_json(extract_json), extract_json.stem)
    cards = select_cards(extract_data["concept_cards"], concept, all_cards)
    index_text = read_text(INDEX_PATH) if INDEX_PATH.exists() else ""
    output_paths: list[Path] = []

    for card in cards:
        source_file = Path(str(card.get("source_file") or ""))
        source_path = resolve_from_root(source_file) if str(source_file) else Path()
        concept_card_block = "```json\n" + json.dumps(card, ensure_ascii=False, indent=2) + "\n```"
        source_snippets = extract_snippets(source_path) if source_path else ""
        source_snippets_block = "```markdown\n" + (source_snippets if source_snippets else "(none)") + "\n```"
        rendered = render_template(
            template,
            {
                "CONCEPT": str(card.get("concept") or extract_json.stem),
                "DOMAIN": str(card.get("domain") or ""),
                "CONCEPT_CARD": concept_card_block,
                "SOURCE_SNIPPETS": source_snippets_block,
                "INDEX": index_text,
                "SEMANTIC_YAML": semantic_yaml_for(card),
            },
        )
        output_path = output_dir / f"{slugify(extract_json.stem)}__{slugify(str(card.get('concept') or 'concept'))}.prompt.md"
        write_text(output_path, rendered)
        output_paths.append(output_path)
    return output_paths


def render_stage_c(scan_mode: str, domain: str | None, output_dir: Path) -> list[Path]:
    """Render a Stage C (relations scan) prompt.

    intra_domain mode: summarise all concept files for a single domain.
    bridge mode: summarise top-5 concepts by total_degree per domain.
    """
    template = read_text(PROMPTS_DIR / "C_relations.md")
    relations_path = ROOT / "wiki" / "relations.json"
    concepts_dir = ROOT / "wiki" / "concepts"

    # Load degree data if available
    degrees: dict[str, dict] = {}
    if relations_path.exists():
        rel_data = load_json(relations_path)
        degrees = rel_data.get("metadata", {}).get("concept_degrees", {})

    # Collect concept summaries grouped by domain
    domain_summaries: dict[str, list[str]] = {}
    if concepts_dir.exists():
        for md_file in sorted(concepts_dir.glob("*.md")):
            text = strip_frontmatter(read_text(md_file)).strip()
            # Extract domain from frontmatter
            raw = read_text(md_file)
            fm_match = re.match(r"^---\n(.*?)\n---", raw, re.S)
            file_domain = ""
            if fm_match:
                for line in fm_match.group(1).splitlines():
                    m = re.match(r"^domain:\s*(.+)$", line)
                    if m:
                        file_domain = m.group(1).strip()
                        break
            if not file_domain:
                deg_entry = degrees.get(md_file.stem, {})
                file_domain = str(deg_entry.get("domain") or "unknown")
            snippet = text[:600].strip()
            domain_summaries.setdefault(file_domain, []).append(f"### {md_file.stem}\n{snippet}")

    if scan_mode == "intra_domain":
        target_domain = domain or ""
        summaries = domain_summaries.get(target_domain, [])
        input_block = "\n\n".join(summaries) if summaries else "(no concepts found for this domain)"
        rendered = render_template(
            template,
            {
                "SCAN_MODE": "intra_domain",
                "domain_concept_summaries": input_block,
                "bridge_candidates": "(not used in intra_domain mode)",
            },
        )
        rendered += f"\n\n---\n## 输入数据（domain: {target_domain}）\n\n{input_block}\n"
        fname = f"c_intra_{slugify(target_domain)}.prompt.md"
    else:
        # bridge: top-5 per domain by total_degree
        top_per_domain: dict[str, list[str]] = {}
        for concept_name, deg in sorted(degrees.items(), key=lambda kv: -kv[1].get("total_degree", 0)):
            d = str(deg.get("domain") or "unknown")
            top_per_domain.setdefault(d, [])
            if len(top_per_domain[d]) < 5:
                summaries_for = domain_summaries.get(d, [])
                match = next((s for s in summaries_for if s.startswith(f"### {concept_name}\n")), None)
                if match:
                    top_per_domain[d].append(match)
        bridge_block = "\n\n".join(
            f"## {d}\n" + "\n\n".join(items) for d, items in sorted(top_per_domain.items()) if items
        ) or "(no concepts found — run Stage B first to populate wiki/concepts/)"
        rendered = render_template(
            template,
            {
                "SCAN_MODE": "bridge",
                "domain_concept_summaries": "(not used in bridge mode)",
                "bridge_candidates": bridge_block,
            },
        )
        rendered += f"\n\n---\n## 输入数据（bridge candidates）\n\n{bridge_block}\n"
        fname = "c_bridge.prompt.md"

    output_path = output_dir / fname
    write_text(output_path, rendered)
    return [output_path]


def infer_extract_path(raw_file: Path) -> Path:
    return ROOT / "raw" / ".extracted" / f"{raw_file.stem}.json"


def is_stage_a_extract_file(path: Path) -> bool:
    return path.suffix.lower() == ".json" and not path.name.endswith("_relations.json")


def classify_schema(data: dict[str, Any]) -> str:
    cards = data.get("concept_cards")
    if isinstance(cards, list):
        return "concept_cards"
    return "legacy"


def validate_card(card: dict[str, Any], domain_keys: set[str], card_index: int) -> list[str]:
    issues: list[str] = []
    concept = str(card.get("concept") or "").strip() or f"card[{card_index}]"
    for field in CARD_REQUIRED_FIELDS:
        value = card.get(field)
        if value is None:
            issues.append(f"[Warning] {concept}: missing `{field}`")
            continue
        if isinstance(value, str) and not value.strip():
            issues.append(f"[Warning] {concept}: empty `{field}`")
        if isinstance(value, list) and not value:
            issues.append(f"[Info] {concept}: empty `{field}`")
    role = str(card.get("card_role") or "")
    if role and role not in {"primary", "supporting"}:
        issues.append(f"[Warning] {concept}: invalid `card_role` {role!r}")
    domain = str(card.get("domain") or "").strip()
    if domain and domain_keys and domain not in domain_keys:
        issues.append(f"[Warning] {concept}: domain `{domain}` not found in taxonomy")
    relations = card.get("semantic_relations") or []
    if isinstance(relations, list):
        for idx, edge in enumerate(relations, start=1):
            if not isinstance(edge, dict):
                issues.append(f"[Warning] {concept}: semantic_relations[{idx}] is not an object")
                continue
            source = str(edge.get("source") or "").strip()
            target = str(edge.get("target") or edge.get("to") or "").strip()
            relation = str(edge.get("type") or edge.get("relation") or "").strip()
            if concept not in {source, target}:
                issues.append(f"[Warning] {concept}: semantic_relations[{idx}] does not include current concept")
            if not relation:
                issues.append(f"[Warning] {concept}: semantic_relations[{idx}] missing relation type")
    else:
        issues.append(f"[Warning] {concept}: `semantic_relations` is not a list")
    return issues


def validate_extract_file(path: Path, domain_keys: set[str]) -> tuple[str, list[str]]:
    path = resolve_existing_path(path)
    data = load_json(path)
    issues: list[str] = []
    schema = classify_schema(data)
    if schema == "legacy":
        issues.append("[Info] legacy schema: rerun Stage A or use `migrate` to produce `concept_cards[]`")
    source_file = str(data.get("source_file") or "").strip()
    if not source_file:
        issues.append("[Warning] missing top-level `source_file`")
    else:
        source_path = resolve_from_root(Path(source_file))
        if not source_path.exists():
            issues.append(f"[Warning] source file not found: {source_file}")
    normalized = normalize_extract(data, path.stem)
    cards = normalized.get("concept_cards") or []
    if not cards:
        issues.append("[Critical] no concept cards available after normalization")
    for idx, card in enumerate(cards, start=1):
        issues.extend(validate_card(card, domain_keys, idx))
    return schema, issues


def find_extract_files(paths: list[Path] | None) -> list[Path]:
    if not paths:
        return sorted(path for path in EXTRACT_DIR.glob("*.json") if is_stage_a_extract_file(path))
    resolved: list[Path] = []
    for path in paths:
        candidate = resolve_from_root(path)
        if candidate.is_dir():
            resolved.extend(sorted(item for item in candidate.glob("*.json") if is_stage_a_extract_file(item)))
        elif is_stage_a_extract_file(candidate):
            resolved.append(candidate)
    return resolved


def validate_extracts(paths: list[Path] | None, report_path: Path | None) -> str:
    files = find_extract_files(paths)
    domain_keys = taxonomy_domain_keys()
    lines = ["# Extract Validation", "", f"Checked: {len(files)} file(s)"]
    legacy_count = 0
    issue_count = 0
    lines.append(f"Legacy schema files: {legacy_count}")
    lines.append(f"Total issues: {issue_count}")
    lines.append("")
    for path in files:
        schema, issues = validate_extract_file(path, domain_keys)
        if schema == "legacy":
            legacy_count += 1
        issue_count += len(issues)
        rel = path.relative_to(ROOT).as_posix() if path.exists() else str(path)
        lines.append(f"## {rel}")
        lines.append(f"- Schema: {schema}")
        if issues:
            for issue in issues:
                lines.append(f"- {issue}")
        else:
            lines.append("- OK")
        lines.append("")
    lines[3] = f"Legacy schema files: {legacy_count}"
    lines[4] = f"Total issues: {issue_count}"
    report = "\n".join(lines).rstrip() + "\n"
    if report_path is not None:
        write_text(resolve_from_root(report_path), report)
    return report


def migrate_extract_files(paths: list[Path] | None, output_dir: Path, report_path: Path | None) -> str:
    files = find_extract_files(paths)
    alias_map = taxonomy_alias_map()
    lines = ["# Extract Migration", "", f"Migrated: {len(files)} file(s)", ""]
    totals = {
        "legacy_wrapped": 0,
        "concept_type_filled": 0,
        "argument_units_filled": 0,
        "relations_filtered": 0,
        "domain_canonicalized": 0,
    }
    output_dir = resolve_from_root(output_dir)
    for path in files:
        original = load_json(path)
        migrated, stats = migrate_extract_data(original, path.stem, alias_map)
        target = output_dir / path.name
        write_text(target, json.dumps(migrated, ensure_ascii=False, indent=2) + "\n")
        for key, value in stats.items():
            totals[key] += value
        rel = path.relative_to(ROOT).as_posix() if path.exists() else str(path)
        lines.append(f"## {rel}")
        lines.append(f"- Output: {target.relative_to(ROOT).as_posix()}")
        lines.append(f"- Cards: {len(migrated.get('concept_cards') or [])}")
        lines.append(f"- legacy_wrapped: {stats['legacy_wrapped']}")
        lines.append(f"- concept_type_filled: {stats['concept_type_filled']}")
        lines.append(f"- argument_units_filled: {stats['argument_units_filled']}")
        lines.append(f"- relations_filtered: {stats['relations_filtered']}")
        lines.append(f"- domain_canonicalized: {stats['domain_canonicalized']}")
        lines.append("")
    summary = [
        f"Legacy wrapped: {totals['legacy_wrapped']}",
        f"Concept types filled: {totals['concept_type_filled']}",
        f"Argument units filled: {totals['argument_units_filled']}",
        f"Relations filtered: {totals['relations_filtered']}",
        f"Domains canonicalized: {totals['domain_canonicalized']}",
        "",
    ]
    lines[3:3] = summary
    report = "\n".join(lines).rstrip() + "\n"
    if report_path is not None:
        write_text(resolve_from_root(report_path), report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render, validate, and migrate Stage A/B prompt artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_a = subparsers.add_parser("a", help="Render a Stage A prompt from a raw markdown file.")
    parser_a.add_argument("raw_file", type=Path)
    parser_a.add_argument("--output-dir", type=Path, default=TMP_DIR / "a")

    parser_b = subparsers.add_parser("b", help="Render Stage B prompt(s) from an extract JSON file.")
    parser_b.add_argument("extract_json", type=Path)
    parser_b.add_argument("--concept")
    parser_b.add_argument("--all-cards", action="store_true")
    parser_b.add_argument("--output-dir", type=Path, default=TMP_DIR / "b")

    parser_ab = subparsers.add_parser("ab", help="Render Stage A and Stage B prompts together.")
    parser_ab.add_argument("raw_file", type=Path)
    parser_ab.add_argument("--extract-json", type=Path)
    parser_ab.add_argument("--concept")
    parser_ab.add_argument("--all-cards", action="store_true")
    parser_ab.add_argument("--output-dir", type=Path, default=TMP_DIR)

    parser_c = subparsers.add_parser("c", help="Render a Stage C (relations scan) prompt.")
    parser_c.add_argument("scan_mode", choices=["intra_domain", "bridge"], help="Scan mode")
    parser_c.add_argument("--domain", default=None, help="Domain id for intra_domain mode")
    parser_c.add_argument("--output-dir", type=Path, default=TMP_DIR / "c")

    parser_validate = subparsers.add_parser("validate", help="Validate extract JSON files against the current Stage A contract.")
    parser_validate.add_argument("paths", nargs="*", type=Path)
    parser_validate.add_argument("--report", type=Path, default=TMP_DIR / "validation.md")

    parser_migrate = subparsers.add_parser("migrate", help="Wrap legacy extract JSON files into concept_cards[] and fill minimal required fields.")
    parser_migrate.add_argument("paths", nargs="*", type=Path)
    parser_migrate.add_argument("--output-dir", type=Path, default=MIGRATED_DIR)
    parser_migrate.add_argument("--report", type=Path, default=TMP_DIR / "migration.md")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "a":
        raw_file = ensure_existing_file(resolve_from_root(args.raw_file), "Raw file")
        outputs = render_stage_a(raw_file, args.output_dir)
        for output in outputs:
            print(output.relative_to(ROOT).as_posix())
        return

    if args.command == "b":
        extract_json = ensure_existing_file(resolve_from_root(args.extract_json), "Extract JSON")
        outputs = render_stage_b(extract_json, args.output_dir, args.concept, args.all_cards)
        for output in outputs:
            print(output.relative_to(ROOT).as_posix())
        return

    if args.command == "ab":
        raw_file = ensure_existing_file(resolve_from_root(args.raw_file), "Raw file")
        outputs = []
        outputs.extend(render_stage_a(raw_file, args.output_dir / "a"))
        extract_json = args.extract_json
        if extract_json is None:
            inferred = infer_extract_path(raw_file)
            if inferred.exists():
                extract_json = inferred
        if extract_json is not None:
            extract_path = ensure_existing_file(resolve_from_root(extract_json), "Extract JSON")
            outputs.extend(render_stage_b(extract_path, args.output_dir / "b", args.concept, args.all_cards))
        for output in outputs:
            print(output.relative_to(ROOT).as_posix())
        return

    if args.command == "c":
        outputs = render_stage_c(args.scan_mode, args.domain, args.output_dir)
        for output in outputs:
            print(output.relative_to(ROOT).as_posix())
        return

    if args.command == "validate":
        report = validate_extracts(args.paths, args.report)
        print(report, end="")
        if args.report is not None:
            print(f"Report written: {resolve_from_root(args.report).relative_to(ROOT).as_posix()}")
        return

    report = migrate_extract_files(args.paths, args.output_dir, args.report)
    print(report, end="")
    if args.report is not None:
        print(f"Report written: {resolve_from_root(args.report).relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
