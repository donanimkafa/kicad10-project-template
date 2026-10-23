import tempfile
import unittest
from pathlib import Path

from scripts.build_docs import resolve_input


class InputSelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def add(self, *names):
        for name in names:
            (self.root / name).touch()

    def select(self, value=None):
        return resolve_input(value, self.root, ".kicad_sch", "schematic")

    def test_project_selects_root_among_subsheets(self):
        self.add("board.kicad_pro", "board.kicad_sch", "Block Diagram.kicad_sch")
        self.assertEqual(self.select(), self.root / "board.kicad_sch")

    def test_multiple_projects_require_explicit_selection(self):
        self.add("a.kicad_pro", "a.kicad_sch", "b.kicad_pro", "b.kicad_sch")
        with self.assertRaisesRegex(ValueError, "--schematic"):
            self.select()
        self.assertEqual(self.select("b.kicad_sch"), self.root / "b.kicad_sch")

    def test_missing_matching_root_remains_ambiguous(self):
        self.add("board.kicad_pro", "child1.kicad_sch", "child2.kicad_sch")
        with self.assertRaises(ValueError):
            self.select()

    def test_directory_name_is_not_a_selection_rule(self):
        self.add(self.root.name + ".kicad_sch", "child.kicad_sch")
        with self.assertRaises(ValueError):
            self.select()

    def test_multiple_boards_remain_ambiguous(self):
        self.add("a.kicad_pro", "a.kicad_pcb", "b.kicad_pcb")
        with self.assertRaisesRegex(ValueError, "--board"):
            resolve_input(None, self.root, ".kicad_pcb", "board")


if __name__ == "__main__":
    unittest.main()
