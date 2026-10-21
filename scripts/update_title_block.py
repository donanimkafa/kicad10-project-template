#!/usr/bin/env python3
"""Update KiCad schematic/PCB title blocks from Git and CHANGELOG metadata."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


SEMVER_RE = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
CHANGELOG_VERSION_RE = re.compile(
    r"^##\s+\[(v?\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)\]"
    r"(?:\s+-\s+(\d{4}-\d{2}-\d{2}))?\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Metadata:
    revision: str
    build_date: str
    company: str
    source: str


def git_output(project_dir: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_dir), *args],
            check=False,
            text=True,
            capture_output=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def changelog_metadata(changelog: Path) -> tuple[str | None, str | None, str | None]:
    if not changelog.is_file():
        return None, None, None
    text = changelog.read_text(encoding="utf-8")
    company_match = re.search(r"^Company:\s*(.+?)\s*$", text, re.IGNORECASE | re.MULTILINE)
    company = company_match.group(1).strip() if company_match else None
    for match in CHANGELOG_VERSION_RE.finditer(text):
        revision = match.group(1)
        if revision.lower() == "unreleased":
            continue
        revision = revision if revision.startswith("v") else f"v{revision}"
        return revision, match.group(2), company
    return None, None, company


def resolve_metadata(project_dir: Path, changelog: Path, company_override: str | None = None) -> Metadata:
    changelog_revision, changelog_date, changelog_company = changelog_metadata(changelog)

    # In a tag-triggered GitHub Actions run, use that exact tag. Locally and on
    # branch builds, use the nearest reachable semantic version tag.
    ref = os.environ.get("GITHUB_REF", "")
    tag = ref.removeprefix("refs/tags/") if ref.startswith("refs/tags/") else None
    if tag is None:
        tag = git_output(project_dir, "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*", "HEAD")

    if tag:
        if not SEMVER_RE.fullmatch(tag):
            raise ValueError(f"Git etiketi SemVer biçiminde değil: {tag!r} (örnek: v1.0.0)")
        revision = tag if tag.startswith("v") else f"v{tag}"
        source = "Git etiketi"
    elif changelog_revision:
        revision = changelog_revision
        source = "CHANGELOG.md"
    else:
        raise ValueError(
            "Revizyon bulunamadı. v1.0.0 biçiminde bir Git etiketi oluşturun veya "
            "CHANGELOG.md içine en az bir sürüm başlığı ekleyin."
        )

    build_date = git_output(project_dir, "log", "-1", "--format=%cs", "HEAD")
    if not build_date and changelog_date:
        build_date = changelog_date
    if not build_date:
        raise ValueError("Commit tarihi okunamadı ve CHANGELOG.md içinde sürüm tarihi yok.")
    try:
        date.fromisoformat(build_date)
    except ValueError as exc:
        raise ValueError(f"Geçersiz tarih: {build_date!r}; YYYY-MM-DD biçimini kullanın.") from exc

    company = (company_override or os.environ.get("KICAD_COMPANY") or changelog_company or "").strip()
    if not company or company.lower() in {"your company", "your company name", "şirket adınız"}:
        raise ValueError(
            "Şirket adı belirtilmemiş. CHANGELOG.md içindeki 'Company:' satırını doldurun, "
            "--company kullanın veya KICAD_COMPANY ortam değişkenini ayarlayın."
        )
    return Metadata(revision, build_date, company, source)


def matching_paren(text: str, open_index: int) -> int:
    """Return the closing parenthesis for an opening one, respecting strings."""
    depth = 0
    in_string = False
    escaped = False
    in_comment = False
    for index in range(open_index, len(text)):
        char = text[index]
        if in_comment:
            if char == "\n":
                in_comment = False
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == ";":
            in_comment = True
        elif char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("KiCad S-expression parantez yapısı tamamlanmamış.")


def find_title_block(text: str) -> tuple[int, int] | None:
    """Find the title_block that is a direct child of the root expression."""
    root_open = next((i for i, char in enumerate(text) if char == "("), None)
    if root_open is None:
        raise ValueError("KiCad dosyası boş veya geçersiz.")
    root_close = matching_paren(text, root_open)
    depth = 0
    in_string = False
    escaped = False
    in_comment = False
    index = root_open
    while index <= root_close:
        char = text[index]
        if in_comment:
            if char == "\n":
                in_comment = False
            index += 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == ";":
            in_comment = True
        elif char == '"':
            in_string = True
        elif char == "(":
            if depth == 1 and re.match(r"\(\s*title_block(?=\s|\))", text[index:]):
                return index, matching_paren(text, index) + 1
            depth += 1
        elif char == ")":
            depth -= 1
        index += 1
    return None


def quote_sexpr(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def update_block_text(text: str, revision: str, build_date: str, company: str) -> str:
    values = {"rev": revision, "date": build_date, "company": company}
    span = find_title_block(text)
    if span is None:
        root_open = next((i for i, char in enumerate(text) if char == "("), None)
        if root_open is None:
            raise ValueError("KiCad dosyası boş veya geçersiz.")
        root_close = matching_paren(text, root_open)
        root_line_start = text.rfind("\n", 0, root_open) + 1
        root_indent = re.match(r"\s*", text[root_line_start:root_open]).group(0)
        child_indent = root_indent + "  "
        block = "(title_block\n" + "".join(
            f"{child_indent}({name} {quote_sexpr(value)})\n" for name, value in values.items()
        ) + f"{root_indent})"
        close_line_start = text.rfind("\n", 0, root_close) + 1
        close_indent = text[close_line_start:root_close]
        if close_indent.strip() == "":
            # Insert before indentation that already belongs to the root close.
            insert_at = close_line_start
            separator = "" if insert_at == 0 or text[insert_at - 1] == "\n" else "\n"
            return text[:insert_at] + separator + root_indent + block + "\n" + text[insert_at:]
        # Compact one-line files need whitespace around the new root child.
        prefix = text[:root_close]
        separator = "" if not prefix or prefix[-1].isspace() else "\n"
        return prefix + separator + root_indent + block + "\n" + text[root_close:]

    start, end = span
    block_text = text[start:end]
    token = re.match(r"\(\s*title_block\b", block_text)
    assert token is not None
    cursor = token.end()
    replacements: dict[str, tuple[int, int, str]] = {}
    while cursor < len(block_text) - 1:
        if block_text[cursor].isspace():
            cursor += 1
            continue
        if block_text[cursor] != "(":
            cursor += 1
            continue
        node_end = matching_paren(block_text, cursor) + 1
        name_match = re.match(r"\(\s*([^\s()]+)", block_text[cursor:node_end])
        if name_match:
            name = name_match.group(1)
            if name in values and name not in replacements:
                replacements[name] = (
                    cursor,
                    node_end,
                    f"({name} {quote_sexpr(values[name])})",
                )
        cursor = node_end

    for name, (field_start, field_end, replacement) in sorted(
        replacements.items(), key=lambda item: item[1][0], reverse=True
    ):
        block_text = block_text[:field_start] + replacement + block_text[field_end:]

    missing = [name for name in values if name not in replacements]
    if missing:
        line_start = text.rfind("\n", 0, start) + 1
        block_indent = re.match(r"\s*", text[line_start:start]).group(0)
        child_indent = block_indent + "  "
        insertion = "".join(f"\n{child_indent}({name} {quote_sexpr(values[name])})" for name in missing)
        block_text = block_text[:-1] + insertion + "\n" + block_indent + ")"
    return text[:start] + block_text + text[end:]


def update_file(path: Path, metadata: Metadata) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = update_block_text(original, metadata.revision, metadata.build_date, metadata.company)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8", newline="")
    return True


def update_title_blocks(
    project_dir: Path,
    files: Iterable[Path],
    *,
    changelog: Path | None = None,
    company: str | None = None,
) -> Metadata:
    changelog_path = changelog or project_dir / "CHANGELOG.md"
    if not changelog_path.is_absolute():
        changelog_path = project_dir / changelog_path
    metadata = resolve_metadata(project_dir, changelog_path, company)
    print(
        f"[INFO] Başlık bloğu: Rev={metadata.revision}, Date={metadata.build_date}, "
        f"Company={metadata.company!r} ({metadata.source})"
    )
    for path in files:
        changed = update_file(path, metadata)
        print(f"[OK]  Başlık bloğu güncellendi: {path.name}" if changed else f"[OK]  Başlık bloğu güncel: {path.name}")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="KiCad şematik/PCB title_block alanlarını Git ve changelog ile günceller.")
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--hardware-dir", type=Path, default=Path("hardware"),
                        help="KiCad dosyalarının klasörü; göreli yol proje köküne göredir (varsayılan: hardware).")
    parser.add_argument("--schematic", type=Path, help="Şematik dosyası; varsayılan hardware klasöründeki tek dosya.")
    parser.add_argument("--board", type=Path, help="PCB dosyası; varsayılan hardware klasöründeki tek dosya.")
    parser.add_argument("--changelog", type=Path, help="CHANGELOG.md yolu (varsayılan: proje kökü).")
    parser.add_argument("--company", help="Company alanı; öncelik: bu seçenek, KICAD_COMPANY, CHANGELOG.md.")
    args = parser.parse_args()
    root = args.project_dir.expanduser().resolve()
    # KiCad dosyalarının klasörü; yoksa eski düzenle uyumlu olmak için proje köküne düşer.
    hardware_dir = args.hardware_dir.expanduser()
    if not hardware_dir.is_absolute():
        hardware_dir = root / hardware_dir
    if not hardware_dir.is_dir():
        hardware_dir = root
    try:
        files: list[Path] = []
        for option, suffix, label, flag in (
            (args.schematic, ".kicad_sch", "şematik", "--schematic"),
            (args.board, ".kicad_pcb", "PCB", "--board"),
        ):
            if option:
                path = option if option.is_absolute() else root / option
                if not path.is_file():
                    raise ValueError(f"{label} dosyası bulunamadı: {path}")
                files.append(path)
            else:
                found = sorted(hardware_dir.glob(f"*{suffix}"))
                if len(found) > 1:
                    raise ValueError(f"Birden fazla {label} dosyası var; {flag} ile seçin.")
                files.extend(found)
        if not files:
            raise ValueError("Güncellenecek .kicad_sch veya .kicad_pcb dosyası bulunamadı.")
        update_title_blocks(root, files, changelog=args.changelog, company=args.company)
        return 0
    except (OSError, ValueError) as exc:
        print(f"[HATA] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
