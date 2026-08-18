from types import SimpleNamespace
import unittest

from app.services.lore_linter import build_lint_candidates, normalize_entity_name, parse_temporal_order


def entity(id: str, name: str, entity_type: str = "character", **values):
    return SimpleNamespace(
        id=id,
        world_id=values.pop("world_id", "world-1"),
        name=name,
        entity_type=entity_type,
        faction_id=values.pop("faction_id", None),
        **values,
    )


def event(id: str, title: str, order: int, entity_ids: list[str], **values):
    return SimpleNamespace(
        id=id,
        title=title,
        date=values.pop("date", str(order)),
        date_order=order,
        description=values.pop("description", None),
        tags=values.pop("tags", []),
        entity_ids=entity_ids,
        **values,
    )


def relation(id: str, source_id: str, target_id: str, **values):
    return SimpleNamespace(
        id=id,
        source_id=source_id,
        target_id=target_id,
        relation_type=values.pop("relation_type", "ally"),
        label=values.pop("label", None),
        date_start=values.pop("date_start", None),
        date_end=values.pop("date_end", None),
        **values,
    )


def issue_types(issues):
    return {issue.issue_type for issue in issues}


class LoreLinterTests(unittest.TestCase):
    def test_name_and_date_normalization(self):
        self.assertEqual(normalize_entity_name(" SCP-CN-001 "), normalize_entity_name("ＳＣＰ CN 001"))
        self.assertEqual(parse_temporal_order("公元前 1200 年"), -1200)
        self.assertEqual(parse_temporal_order("21世纪"), 2000)
        self.assertIsNone(parse_temporal_order("unknown"))

    def test_structural_rules_find_duplicates_and_invalid_ranges(self):
        entities = [entity("a", "Jane Doe"), entity("b", "Jane-Doe")]
        relations = [relation("r1", "a", "b", date_start="2080年", date_end="2070年")]

        issues = build_lint_candidates("world-1", entities, relations, [])

        self.assertEqual(issue_types(issues), {"duplicate_entity", "relation_date_order"})

    def test_timeline_rule_detects_action_after_death(self):
        entities = [entity("a", "Jane")]
        events = [
            event("death", "Jane 阵亡", 2070, ["a"]),
            event("later", "Jane 领导突袭", 2077, ["a"]),
        ]

        issues = build_lint_candidates("world-1", entities, [], events)

        self.assertIn("post_death_appearance", issue_types(issues))

    def test_posthumous_context_does_not_raise_timeline_issue(self):
        entities = [entity("a", "Jane")]
        events = [
            event("death", "Jane 去世", 2070, ["a"]),
            event("later", "Jane 的生前档案公开", 2077, ["a"]),
        ]

        issues = build_lint_candidates("world-1", entities, [], events)

        self.assertNotIn("post_death_appearance", issue_types(issues))

    def test_missing_event_reference_is_reported(self):
        issues = build_lint_candidates(
            "world-1",
            [entity("a", "Jane")],
            [],
            [event("event-1", "未知访客", 2077, ["missing"])],
        )

        self.assertEqual(issue_types(issues), {"dangling_event_reference"})


if __name__ == "__main__":
    unittest.main()
