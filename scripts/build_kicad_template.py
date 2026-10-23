#!/usr/bin/env python3
"""Package the current cover project as an installable KiCad user template."""

from pathlib import Path
import json
import re
import shutil
import tempfile
import zipfile


def sheet_references(path: Path) -> list[str]:
    """Read Sheetfile properties from actual sheet nodes, ignoring graphic text."""
    stack: list[list] = []
    root = None
    for token in re.findall(r'"(?:\\.|[^"\\])*"|;[^\n]*|[()]|[^\s();]+',
                            path.read_text(encoding="utf-8-sig")):
        if token.startswith(";"):
            continue
        if token == "(":
            node: list = []
            if stack:
                stack[-1].append(node)
            elif root is not None:
                raise ValueError(f"Birden fazla kök ifade: {path}")
            else:
                root = node
            stack.append(node)
        elif token == ")":
            if not stack:
                raise ValueError(f"Geçersiz şematik: {path}")
            stack.pop()
        elif stack:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
        else:
            raise ValueError(f"Geçersiz şematik: {path}")
    if stack or not root or root[0] != "kicad_sch":
        raise ValueError(f"Geçersiz şematik: {path}")
    references = []
    for node in root[1:]:
        if isinstance(node, list) and node and node[0] == "sheet":
            files = [p[2] for p in node[1:] if isinstance(p, list)
                     and len(p) >= 3 and p[:2] == ["property", "Sheetfile"]]
            if len(files) != 1 or not files[0]:
                raise ValueError(f"Alt sayfanın Sheetfile alanı eksik: {path}")
            references.extend(files)
    return references


def collect_schematics(root_schematic: Path, hardware: Path) -> list[Path]:
    """Collect the reachable hierarchy, including shared sheets only once."""
    hardware = hardware.resolve()
    visited: set[Path] = set()
    active: set[Path] = set()

    def visit(path: Path) -> None:
        path = path.resolve()
        if not path.is_relative_to(hardware):
            raise ValueError(f"Alt sayfa hardware klasörü dışında: {path}")
        if not path.is_file() or path.suffix.lower() != ".kicad_sch":
            raise ValueError(f"Şematik dosyası bulunamadı veya uzantısı geçersiz: {path}")
        if path in active:
            raise ValueError(f"Döngüsel sayfa bağlantısı: {path}")
        if path in visited:
            return
        active.add(path)
        for reference in sheet_references(path):
            if Path(reference).is_absolute() or "${" in reference:
                raise ValueError(f"Taşınabilir paket için göreli Sheetfile yolu gerekli: {reference}")
            visit(path.parent / reference)
        active.remove(path)
        visited.add(path)

    visit(root_schematic)
    return sorted(visited)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    name = "kicad10-project-template"
    hardware = root / "hardware"
    schematics = collect_schematics(hardware / f"{name}.kicad_sch", hardware)
    destination = root / "manufacturing" / "templates"
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"{name}.zip"
    # Build from an allowlist; never copy local settings, backups or Git history.
    with tempfile.TemporaryDirectory(prefix="kicad-template-") as tmp:
        template = Path(tmp) / name
        template.mkdir()
        for suffix in (".kicad_pro", ".kicad_pcb"):
            shutil.copy2(root / "hardware" / f"{name}{suffix}", template)
        for source in schematics:
            target = template / source.relative_to(hardware.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        shutil.copytree(root / "hardware" / "sheet", template / "sheet")
        shutil.copytree(root / "templates" / "meta", template / "meta")
        shutil.copy2(root / "templates" / "USAGE.md", template / "USAGE.md")
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
            for path in sorted(template.rglob("*")):
                if path.is_file():
                    package.write(path, path.relative_to(Path(tmp)))
    print(f"KiCad template ({len(schematics)} şematik): {archive}")


if __name__ == "__main__":
    main()
