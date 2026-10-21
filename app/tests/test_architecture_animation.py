import unittest

from app.video_maker.architecture_animation import build_architecture_animation


class ArchitectureAnimationTests(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "layout": "pipeline",
            "nodes": [
                {"id": "oracle", "label": "Oracle Database", "shape": "database"},
                {"id": "dms", "label": "AWS DMS", "shape": "rectangle"},
                {"id": "snowflake", "label": "Snowflake Database", "shape": "database"},
                {"id": "sql", "label": "SQL Processing", "shape": "terminal"},
                {"id": "dashboard", "label": "Analytics Dashboard", "shape": "dashboard"},
            ],
            "edges": [
                {"id": "oracle-dms", "from": "oracle", "to": "dms", "style": "bezier", "data_flow": True},
                {"id": "dms-snowflake", "from": "dms", "to": "snowflake", "style": "elbow", "data_flow": True},
                {"id": "snowflake-sql", "from": "snowflake", "to": "sql", "style": "curved", "data_flow": True},
                {"id": "sql-dashboard", "from": "sql", "to": "dashboard", "style": "straight", "data_flow": True},
            ],
        }
        self.stages = [
            {"title": "Source", "speech": "Oracle stores source records.", "start": 0, "end": 8},
            {"title": "Migration", "speech": "AWS DMS moves changed records.", "start": 8, "end": 18,
             "diagram_actions": [{"target_id": "oracle-dms", "action": "draw_edge", "cue_progress": 0.25},
                                 {"target_id": "dms", "action": "reveal_node", "cue_progress": 0.65}]},
            {"title": "Warehouse", "speech": "Snowflake stores the loaded data.", "start": 18, "end": 28},
            {"title": "Query", "speech": "SQL transforms warehouse data.", "start": 28, "end": 38},
            {"title": "Analytics", "speech": "The dashboard presents the results.", "start": 38, "end": 50},
        ]

    def test_oracle_to_analytics_demo_has_editable_timed_components(self):
        result = build_architecture_animation(self.graph, self.stages, 50, "Oracle to Analytics")
        self.assertEqual([node["label"] for node in result["nodes"]], [
            "Oracle Database", "AWS DMS", "Snowflake Database", "SQL Processing", "Analytics Dashboard"
        ])
        self.assertEqual([edge["from"] for edge in result["edges"]], ["oracle", "dms", "snowflake", "sql"])
        self.assertTrue(all(0.2 <= node["x"] <= 0.8 and 0.16 <= node["y"] <= 0.75 for node in result["nodes"]))
        actions = {(item["target_id"], item["action"]): item for item in result["actions"]}
        self.assertEqual(actions[("oracle-dms", "draw_edge")]["start"], 10.5)
        self.assertLess(actions[("oracle-dms", "draw_edge")]["start"], actions[("dms", "reveal_node")]["start"])
        self.assertEqual(actions[("dashboard", "highlight_node")]["stage_index"], 4)

    def test_layouts_keep_branch_nodes_separate_and_edges_connected(self):
        graph = {
            "layout": "hierarchical",
            "nodes": [{"id": "root", "label": "API Gateway"}] + [
                {"id": f"service-{index}", "label": f"Service {index}"} for index in range(4)
            ],
            "edges": [{"from": "root", "to": f"service-{index}"} for index in range(4)],
        }
        result = build_architecture_animation(graph, self.stages, 50)
        children = [node for node in result["nodes"] if node["id"].startswith("service-")]
        self.assertEqual({node["layer"] for node in children}, {1})
        self.assertEqual(len({node["x"] for node in children}), 4)
        child_width = 1080 * 0.7 / 4
        ordered_children = sorted(children, key=lambda node: node["x"])
        self.assertTrue(all(
            (right["x"] - left["x"]) * 1080 >= child_width
            for left, right in zip(ordered_children, ordered_children[1:])
        ))
        ids = {node["id"] for node in result["nodes"]}
        self.assertTrue(all(edge["from"] in ids and edge["to"] in ids for edge in result["edges"]))

    def test_stage_entities_and_relationships_build_a_programmatic_graph(self):
        result = build_architecture_animation(None, [{
            "title": "Ingestion",
            "speech": "Data moves from a source to processing.",
            "start": 0,
            "end": 12,
            "entities": [
                {"label": "Source Database", "shape": "cylinder"},
                {"label": "Transform", "shape": "rounded_rectangle"},
            ],
            "relationships": [{"from": "Source Database", "to": "Transform", "label": "records"}],
        }], 12)
        self.assertEqual([node["shape"] for node in result["nodes"]], ["database", "rounded_rectangle"])
        self.assertEqual(result["edges"][0]["from"], result["nodes"][0]["id"])
        self.assertTrue(any(action["action"] == "draw_edge" for action in result["actions"]))


if __name__ == "__main__":
    unittest.main()
