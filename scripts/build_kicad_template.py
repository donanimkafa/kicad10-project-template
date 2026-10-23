#!/usr/bin/env python3
"""Package the current cover project as an installable KiCad user template."""

from pathlib import Path
import shutil
import tempfile
import zipfile


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    name = "kicad10-project-template"
    destination = root / "manufacturing" / "templates"
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"{name}.zip"
    # Build from an allowlist; never copy local settings, backups or Git history.
    with tempfile.TemporaryDirectory(prefix="kicad-template-") as tmp:
        template = Path(tmp) / name
        template.mkdir()
        for suffix in (".kicad_pro", ".kicad_sch", ".kicad_pcb"):
            shutil.copy2(root / "hardware" / f"{name}{suffix}", template)
        shutil.copytree(root / "hardware" / "sheet", template / "sheet")
        shutil.copytree(root / "templates" / "meta", template / "meta")
        shutil.copy2(root / "templates" / "USAGE.md", template / "USAGE.md")
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
            for path in sorted(template.rglob("*")):
                if path.is_file():
                    package.write(path, path.relative_to(Path(tmp)))
    print(f"KiCad template: {archive}")


if __name__ == "__main__":
    main()
