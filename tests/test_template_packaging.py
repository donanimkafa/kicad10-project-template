import tempfile
import unittest
from pathlib import Path

from scripts.build_kicad_template import collect_schematics


class TemplateHierarchyTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def sheet(self, name, *children):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        refs = ''.join(f'(sheet (property "Sheetfile" "{child}"))' for child in children)
        path.write_text(f'(kicad_sch {refs})', encoding="utf-8")
        return path

    def test_nested_shared_sheets_and_unrelated_file(self):
        root = self.sheet("root.kicad_sch", "parts/child.kicad_sch", "common.kicad_sch")
        self.sheet("parts/child.kicad_sch", "../common.kicad_sch")
        self.sheet("common.kicad_sch")
        self.sheet("unused.kicad_sch")
        files = collect_schematics(root, self.root)
        self.assertEqual(len(files), 3)
        self.assertNotIn(self.root / "unused.kicad_sch", files)

    def test_missing_child_fails(self):
        root = self.sheet("root.kicad_sch", "missing.kicad_sch")
        with self.assertRaisesRegex(ValueError, "bulunamadı"):
            collect_schematics(root, self.root)

    def test_cycle_fails(self):
        root = self.sheet("root.kicad_sch", "root.kicad_sch")
        with self.assertRaisesRegex(ValueError, "Döngüsel"):
            collect_schematics(root, self.root)

    def test_external_path_fails(self):
        root = self.sheet("root.kicad_sch", "../outside.kicad_sch")
        with self.assertRaisesRegex(ValueError, "dışında"):
            collect_schematics(root, self.root)

    def test_graphic_text_is_not_a_sheet_reference(self):
        root = self.root / "root.kicad_sch"
        root.write_text('(kicad_sch (text "(sheet)"))', encoding="utf-8")
        self.assertEqual(collect_schematics(root, self.root), [root])
