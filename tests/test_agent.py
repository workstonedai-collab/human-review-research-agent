import json
import unittest
from pathlib import Path

from agent import export_markdown, prepare, review


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "facts.json"


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.corpus = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.state = prepare("What is Example City planning for library hours?", self.corpus)

    def test_retrieval_and_draft_cite_selected_facts(self):
        self.assertEqual(self.state["stage"], "needs_review")
        self.assertTrue(any(item["id"] == "library-plan" for item in self.state["facts"]))
        self.assertFalse(any(item["id"] == "transit-plan" for item in self.state["facts"]))
        self.assertIn("[source:library-plan]", self.state["draft"]["sections"][0]["text"])

    def test_export_requires_approval(self):
        with self.assertRaisesRegex(ValueError, "approval"):
            export_markdown(self.state)
        review(self.state, "reject", "Demo reviewer", "Check the evidence")
        with self.assertRaisesRegex(ValueError, "approval"):
            export_markdown(self.state)

    def test_approval_is_bound_to_draft_content(self):
        review(self.state, "approve", "Demo reviewer")
        self.assertIn("Reviewed by", export_markdown(self.state))
        self.state["draft"]["sections"][0]["text"] += " Modified later"
        with self.assertRaisesRegex(ValueError, "changed after approval"):
            export_markdown(self.state)

    def test_missing_evidence_stops_drafting(self):
        with self.assertRaisesRegex(ValueError, "no matching facts"):
            prepare("unrelated quantum topic", self.corpus)

    def test_rejection_requires_reason(self):
        with self.assertRaisesRegex(ValueError, "rejection comment"):
            review(self.state, "reject", "Demo reviewer")


if __name__ == "__main__":
    unittest.main()
