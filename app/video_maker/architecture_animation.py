"""Normalize model-authored architecture diagrams into an animation timeline."""

from __future__ import annotations

import re
from collections import defaultdict, deque
from typing import Any


NODE_SHAPES = {
    "database", "rectangle", "rounded_rectangle", "circle", "diamond", "hexagon",
    "cloud", "document", "table", "terminal", "dashboard",
}
EDGE_STYLES = {"straight", "curved", "elbow", "bezier"}
LAYOUTS = {"pipeline", "layered", "hierarchical", "tree"}
ACTION_ALIASES = {
    "reveal": "reveal_node",
    "enter": "reveal_node",
    "node_entrance": "reveal_node",
    "draw": "draw_edge",
    "draw_connector": "draw_edge",
    "connect": "draw_edge",
    "focus": "highlight_node",
    "highlight": "highlight_node",
    "data_flow": "packets",
    "move_data": "packets",
    "expand": "expand_node",
    "pulse": "pulse_node",
    "morph": "morph_node",
}


def _slug(value: Any) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return value[:64] or "component"


def _shape_for(node: dict[str, Any]) -> str:
    shape = str(node.get("shape") or node.get("type") or node.get("kind") or "").lower()
    aliases = {
        "db": "database", "cylinder": "database", "warehouse": "database", "storage": "database",
        "rect": "rectangle", "box": "rectangle", "service": "rounded_rectangle", "process": "rounded_rectangle",
        "rounded": "rounded_rectangle", "rounded-rectangle": "rounded_rectangle", "api": "rounded_rectangle",
        "circle-node": "circle", "hex": "hexagon", "file": "document", "doc": "document",
        "terminal_window": "terminal", "shell": "terminal", "table_grid": "table", "bi": "dashboard",
        "chart": "dashboard",
    }
    shape = aliases.get(shape, shape)
    if shape in NODE_SHAPES:
        return shape
    label = f"{node.get('label', '')} {node.get('description', '')}".lower()
    if re.search(r"database|warehouse|snowflake|oracle|postgres|mysql|sql server|dynamodb|bigquery", label):
        return "database"
    if re.search(r"dashboard|analytics|report|visuali[sz]ation|bi tool", label):
        return "dashboard"
    if re.search(r"terminal|command line|shell", label):
        return "terminal"
    if re.search(r"document|file|object store|s3 bucket", label):
        return "document"
    if re.search(r"table|dataset|records", label):
        return "table"
    if re.search(r"cloud|vpc|region", label):
        return "cloud"
    return "rounded_rectangle"


def _stage_for_time(stages: list[dict[str, Any]], timestamp: float) -> int:
    for index, stage in enumerate(stages):
        if float(stage.get("start", 0) or 0) <= timestamp <= float(stage.get("end", 0) or 0):
            return index
    return max(0, len(stages) - 1)


def _layout_nodes(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], layout: str) -> None:
    if not nodes:
        return
    if layout == "pipeline":
        row_count = (len(nodes) + 1) // 2
        for index, node in enumerate(nodes):
            row = index // 2
            column = index % 2 if row % 2 == 0 else 1 - index % 2
            node.update({
                "x": 0.5 if len(nodes) == 1 else 0.25 + 0.5 * column,
                "y": 0.5 if row_count == 1 else 0.22 + 0.56 * row / (row_count - 1),
                "layer": row,
                "column_index": column,
                "column_count": 2 if len(nodes) > 1 else 1,
            })
        return

    node_ids = {node["id"] for node in nodes}
    incoming = {node_id: 0 for node_id in node_ids}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        source, target = edge["from"], edge["to"]
        if source in node_ids and target in node_ids and source != target:
            outgoing[source].append(target)
            incoming[target] += 1
    queue = deque(node["id"] for node in nodes if incoming[node["id"]] == 0)
    levels = {node_id: 0 for node_id in queue}
    while queue:
        source = queue.popleft()
        for target in outgoing[source]:
            levels[target] = max(levels.get(target, 0), levels[source] + 1)
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)
    next_level = max(levels.values(), default=-1) + 1
    for node in nodes:
        levels.setdefault(node["id"], next_level)
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        groups[levels[node["id"]]].append(node)
    ordered_levels = sorted(groups)
    level_count = max(1, len(ordered_levels))
    for layer_index, level in enumerate(ordered_levels):
        group = groups[level]
        for column_index, node in enumerate(group):
            node.update({
                "x": 0.5 if len(group) == 1 else 0.2 + 0.6 * column_index / (len(group) - 1),
                "y": 0.16 if level_count == 1 else 0.16 + 0.59 * layer_index / (level_count - 1),
                "layer": layer_index,
                "column_index": column_index,
                "column_count": len(group),
            })


def build_architecture_animation(
    raw_graph: Any,
    stages: list[dict[str, Any]],
    duration: float,
    title: str = "",
) -> dict[str, Any]:
    """Build a stable, editable graph and voiceover-timed component actions."""
    graph_data = raw_graph if isinstance(raw_graph, dict) else {}
    raw_nodes = list(graph_data.get("nodes") or graph_data.get("components") or [])
    raw_edges = list(graph_data.get("edges") or graph_data.get("connectors") or [])
    collect_scene_nodes = not raw_nodes
    collect_scene_edges = not raw_edges
    layout = str(graph_data.get("layout") or graph_data.get("type") or "pipeline").lower()
    layout = layout if layout in LAYOUTS else "pipeline"

    for stage in stages:
        visual = stage.get("visual_data") if isinstance(stage.get("visual_data"), dict) else {}
        scene_graph = visual.get("architecture_graph") or visual.get("graph") or {}
        if isinstance(scene_graph, dict):
            if collect_scene_nodes:
                raw_nodes.extend(scene_graph.get("nodes") or scene_graph.get("components") or [])
            if collect_scene_edges:
                raw_edges.extend(scene_graph.get("edges") or scene_graph.get("connectors") or [])
        if collect_scene_nodes:
            raw_nodes.extend(visual.get("nodes") or stage.get("entities") or [])
            steps = visual.get("steps") or []
            if isinstance(steps, list):
                raw_nodes.extend(step if isinstance(step, dict) else {"label": step} for step in steps)
        if collect_scene_edges:
            raw_edges.extend(visual.get("edges") or stage.get("relationships") or [])

    nodes: list[dict[str, Any]] = []
    id_by_key: dict[str, str] = {}
    for raw in raw_nodes:
        if isinstance(raw, str):
            raw = {"label": raw}
        if not isinstance(raw, dict):
            continue
        label = str(raw.get("label") or raw.get("name") or raw.get("title") or "").strip()
        if not label:
            continue
        proposed_id = _slug(raw.get("id") or label)
        existing_id = id_by_key.get(proposed_id) or id_by_key.get(_slug(label))
        if existing_id:
            node = next(item for item in nodes if item["id"] == existing_id)
            if not node.get("description") and raw.get("description"):
                node["description"] = str(raw["description"]).strip()[:140]
            continue
        node_id = proposed_id
        suffix = 2
        while any(item["id"] == node_id for item in nodes):
            node_id = f"{proposed_id}-{suffix}"
            suffix += 1
        node = {
            "id": node_id,
            "label": label[:72],
            "description": str(raw.get("description") or raw.get("detail") or "").strip()[:140],
            "shape": _shape_for(raw),
            "color": str(raw.get("color") or "#38BDF8"),
            "parent_id": _slug(raw.get("parent_id")) if raw.get("parent_id") else None,
            "status": str(raw.get("status") or "active")[:24],
        }
        nodes.append(node)
        id_by_key[node_id] = node_id
        id_by_key[_slug(label)] = node_id

    if not nodes:
        for index, stage in enumerate(stages):
            label = str(stage.get("title") or f"Step {index + 1}").strip()
            node_id = _slug(label)
            if node_id not in id_by_key:
                nodes.append({
                    "id": node_id,
                    "label": label[:72],
                    "description": str(stage.get("speech") or "").strip()[:140],
                    "shape": _shape_for({"label": label}),
                    "color": "#38BDF8",
                    "parent_id": None,
                    "status": "active",
                })
                id_by_key[node_id] = node_id

    edges: list[dict[str, Any]] = []
    edge_ids: set[str] = set()
    for index, raw in enumerate(raw_edges):
        if not isinstance(raw, dict):
            continue
        source_key = _slug(raw.get("from") or raw.get("source") or raw.get("source_id"))
        target_key = _slug(raw.get("to") or raw.get("target") or raw.get("target_id"))
        source, target = id_by_key.get(source_key), id_by_key.get(target_key)
        if not source or not target or source == target:
            continue
        edge_id = _slug(raw.get("id") or f"{source}-to-{target}")
        if edge_id in edge_ids:
            continue
        edge_ids.add(edge_id)
        style = str(raw.get("style") or raw.get("type") or "bezier").lower()
        edges.append({
            "id": edge_id,
            "from": source,
            "to": target,
            "label": str(raw.get("label") or "").strip()[:60],
            "style": style if style in EDGE_STYLES else "bezier",
            "color": str(raw.get("color") or "#38BDF8"),
            "data_flow": bool(raw.get("data_flow", True)),
        })
    for node in nodes:
        if node["parent_id"]:
            node["parent_id"] = id_by_key.get(node["parent_id"], node["parent_id"])
            if node["parent_id"] in id_by_key.values() and not any(
                edge["from"] == node["parent_id"] and edge["to"] == node["id"] for edge in edges
            ):
                parent_edge_id = f"{node['parent_id']}-to-{node['id']}"
                edges.append({
                    "id": parent_edge_id,
                    "from": node["parent_id"],
                    "to": node["id"],
                    "label": "",
                    "style": "bezier",
                    "color": "#38BDF8",
                    "data_flow": False,
                })
                edge_ids.add(parent_edge_id)
    if not edges and len(nodes) > 1:
        for index in range(len(nodes) - 1):
            edges.append({
                "id": f"{nodes[index]['id']}-to-{nodes[index + 1]['id']}",
                "from": nodes[index]["id"],
                "to": nodes[index + 1]["id"],
                "label": "",
                "style": "bezier",
                "color": "#38BDF8",
                "data_flow": True,
            })

    _layout_nodes(nodes, edges, layout)
    node_ids = {node["id"] for node in nodes}
    groups = []
    for index, raw_group in enumerate(graph_data.get("groups") or []):
        if not isinstance(raw_group, dict):
            continue
        members = [id_by_key.get(_slug(item), _slug(item)) for item in raw_group.get("node_ids", raw_group.get("nodes", []))]
        members = [item for item in members if item in node_ids]
        if members:
            groups.append({
                "id": _slug(raw_group.get("id") or raw_group.get("label") or f"group-{index + 1}"),
                "label": str(raw_group.get("label") or f"Group {index + 1}")[:64],
                "shape": "cloud" if str(raw_group.get("shape") or "").lower() == "cloud" else "rounded_rectangle",
                "node_ids": members,
                "parent_id": _slug(raw_group.get("parent_id")) if raw_group.get("parent_id") else None,
            })
    graph = {
        "layout": layout,
        "title": str(graph_data.get("title") or title)[:100],
        "nodes": nodes,
        "edges": edges,
        "groups": groups,
        "actions": [],
    }
    if not nodes:
        return graph

    total_duration = max(0.1, float(duration or 0.1))
    event_keys: set[tuple[str, str]] = set()
    stages = stages or [{"start": 0.0, "end": total_duration, "duration": total_duration}]
    for stage_index, stage in enumerate(stages):
        stage_start = float(stage.get("start", 0) or 0)
        stage_end = float(stage.get("end", stage_start) or stage_start)
        stage_duration = max(0.1, stage_end - stage_start)
        visual = stage.get("visual_data") if isinstance(stage.get("visual_data"), dict) else {}
        authored_actions = stage.get("diagram_actions") or visual.get("diagram_actions") or []
        for action_data in authored_actions if isinstance(authored_actions, list) else []:
            if not isinstance(action_data, dict):
                continue
            target_key = _slug(
                action_data.get("target_id") or action_data.get("component_id") or action_data.get("edge_id")
                or action_data.get("target") or action_data.get("node_id")
            )
            target_id = id_by_key.get(target_key) or (target_key if target_key in edge_ids else None)
            if not target_id:
                continue
            action = str(action_data.get("action") or action_data.get("type") or "reveal").lower()
            action = ACTION_ALIASES.get(action, action)
            is_edge = target_id in edge_ids
            if action == "reveal_node" and is_edge:
                action = "draw_edge"
            elif action == "draw_edge" and not is_edge:
                continue
            if action not in {"reveal_node", "draw_edge", "highlight_node", "packets", "expand_node", "pulse_node", "morph_node"}:
                continue
            cue = action_data.get("cue_progress", action_data.get("progress", 0.3))
            try:
                cue = max(0.0, min(1.0, float(cue)))
            except (TypeError, ValueError):
                cue = 0.3
            start = stage_start + stage_duration * cue
            action_duration = action_data.get(
                "duration",
                max(0.1, stage_duration * (1 - cue)) if action in {"highlight_node", "packets"} else 0.8,
            )
            try:
                action_duration = max(0.1, float(action_duration))
            except (TypeError, ValueError):
                action_duration = stage_duration if action == "highlight_node" else 0.8
            graph["actions"].append({
                "target_id": target_id,
                "action": action,
                "start": round(start, 3),
                "end": round(min(total_duration, start + action_duration), 3),
                "duration": round(action_duration, 3),
                "stage_index": stage_index,
            })
            event_keys.add((target_id, action))

    sequence: list[tuple[str, str]] = []
    node_ids = {node["id"] for node in nodes}
    outgoing_edges: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        outgoing_edges[edge["from"]].append(edge)
    for node in nodes:
        sequence.append((node["id"], "reveal_node"))
        sequence.extend((edge["id"], "draw_edge") for edge in outgoing_edges[node["id"]])
    sequence = [item for item in sequence if item not in event_keys]
    for index, (target_id, action) in enumerate(sequence):
        start = total_duration * 0.72 * index / max(1, len(sequence) - 1)
        graph["actions"].append({
            "target_id": target_id,
            "action": action,
            "start": round(start, 3),
            "end": round(min(total_duration, start + (0.9 if action == "draw_edge" else 0.55)), 3),
            "duration": 0.9 if action == "draw_edge" else 0.55,
            "stage_index": _stage_for_time(stages, start),
        })

    for edge in edges:
        if not edge["data_flow"] or (edge["id"], "packets") in event_keys:
            continue
        draw_action = next((
            item for item in graph["actions"]
            if item["target_id"] == edge["id"] and item["action"] == "draw_edge"
        ), None)
        if draw_action:
            packet_start = min(total_duration, draw_action["start"] + draw_action["duration"])
            graph["actions"].append({
                "target_id": edge["id"],
                "action": "packets",
                "start": round(packet_start, 3),
                "end": round(total_duration, 3),
                "duration": round(max(0.1, total_duration - packet_start), 3),
                "stage_index": _stage_for_time(stages, packet_start),
            })
            event_keys.add((edge["id"], "packets"))

    for stage_index, stage in enumerate(stages):
        visual = stage.get("visual_data") if isinstance(stage.get("visual_data"), dict) else {}
        authored = stage.get("diagram_actions") or visual.get("diagram_actions") or []
        authored_targets = []
        for item in authored if isinstance(authored, list) else []:
            if not isinstance(item, dict):
                continue
            action = ACTION_ALIASES.get(str(item.get("action") or item.get("type") or "").lower(), str(item.get("action") or item.get("type") or "").lower())
            if action not in {"highlight_node", "reveal_node", "expand_node", "pulse_node"}:
                continue
            key = _slug(item.get("target_id") or item.get("component_id") or item.get("target") or item.get("node_id"))
            node_id = id_by_key.get(key)
            if node_id and node_id not in authored_targets:
                authored_targets.append(node_id)
        if not authored_targets:
            node_index = min(len(nodes) - 1, round(stage_index * max(0, len(nodes) - 1) / max(1, len(stages) - 1)))
            authored_targets = [nodes[node_index]["id"]]
        stage_start = float(stage.get("start", 0) or 0)
        stage_end = float(stage.get("end", total_duration) or total_duration)
        for target_id in authored_targets:
            if (target_id, "highlight_node") in event_keys:
                continue
            graph["actions"].append({
                "target_id": target_id,
                "action": "highlight_node",
                "start": round(stage_start, 3),
                "end": round(stage_end, 3),
                "duration": round(max(0.1, stage_end - stage_start), 3),
                "stage_index": stage_index,
            })
    graph["actions"].sort(key=lambda event: (event["start"], event["action"] == "draw_edge"))
    return graph
