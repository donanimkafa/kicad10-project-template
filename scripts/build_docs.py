#!/usr/bin/env python3
"""Build KiCad ERC/DRC reports and manufacturing deliverables.

Run this from any directory with:
    python scripts/build_docs.py

By default the project root is the parent directory of this script. Only files
directly in the project root are auto-detected; this avoids picking up backups
or generated files in output folders.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class StepResult:
    name: str
    status: str
    detail: str = ""


def find_kicad_cli() -> str | None:
    """Find kicad-cli on PATH or in common platform install locations."""
    executable = "kicad-cli.exe" if os.name == "nt" else "kicad-cli"
    on_path = shutil.which(executable) or shutil.which("kicad-cli")
    if on_path:
        return on_path

    candidates: list[Path] = []
    if sys.platform == "darwin":
        candidates.append(Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"))
    elif os.name == "nt":
        for base in (Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
                     Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))):
            candidates.extend(base.glob("KiCad/*/bin/kicad-cli.exe"))
    else:
        candidates.extend((Path("/usr/bin/kicad-cli"), Path("/usr/local/bin/kicad-cli")))
    return str(next((path for path in candidates if path.is_file()), "")) or None


def resolve_input(value: str | None, project_dir: Path, suffix: str, label: str) -> Path | None:
    if value:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = project_dir / path
        path = path.resolve()
        if not path.is_file():
            raise ValueError(f"{label} dosyası bulunamadı: {path}")
        if path.suffix.lower() != suffix:
            raise ValueError(f"{label} dosyası {suffix} uzantılı olmalı: {path}")
        return path

    candidates = sorted(
        (path for path in project_dir.iterdir()
         if path.is_file() and path.suffix.lower() == suffix),
        key=lambda path: path.name.casefold(),
    )
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    # A common project basename is a safe tie-breaker when several files exist.
    for candidate in candidates:
        if candidate.stem.casefold() == project_dir.name.casefold():
            return candidate
    choices = "\n  ".join(str(path.name) for path in candidates)
    raise ValueError(
        f"Birden fazla {label} dosyası bulundu. --{label} ile seçim yapın:\n  {choices}"
    )


def run_step(
    cli: str,
    name: str,
    args: Sequence[str | Path],
    log,
    results: list[StepResult],
    *,
    violation_exit: bool = False,
) -> bool:
    command = [cli, *(str(arg) for arg in args)]
    print(f"[RUN] {name}")
    log.write("\n$ " + subprocess.list2cmdline(command) + "\n")
    log.flush()
    try:
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
    except OSError as exc:
        detail = str(exc)
        log.write(f"[LAUNCH ERROR] {detail}\n")
        results.append(StepResult(name, "HATA", detail))
        print(f"[HATA] {name}: {detail}")
        return False

    if completed.stdout:
        log.write(completed.stdout)
        if not completed.stdout.endswith("\n"):
            log.write("\n")
    if completed.stderr:
        log.write("[stderr]\n" + completed.stderr)
        if not completed.stderr.endswith("\n"):
            log.write("\n")
    log.flush()

    if completed.returncode == 0:
        results.append(StepResult(name, "OK"))
        print(f"[OK]  {name}")
        return True
    if violation_exit and completed.returncode == 5:
        detail = "ERC/DRC ihlalleri bulundu; raporu inceleyin."
        results.append(StepResult(name, "BULGU", detail))
        print(f"[UYARI] {name}: {detail}")
        return True

    detail = f"kicad-cli çıkış kodu: {completed.returncode}"
    results.append(StepResult(name, "HATA", detail))
    print(f"[HATA] {name}: {detail}; build.log dosyasını inceleyin.")
    return False


def build(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.is_dir():
        print(f"Proje klasörü bulunamadı: {project_dir}", file=sys.stderr)
        return 2

    try:
        schematic = resolve_input(args.schematic, project_dir, ".kicad_sch", "schematic")
        board = resolve_input(args.board, project_dir, ".kicad_pcb", "board")
    except ValueError as exc:
        print(f"Hata: {exc}", file=sys.stderr)
        return 2

    if schematic is None and board is None:
        print(f"{project_dir} içinde kök seviyede .kicad_sch veya .kicad_pcb bulunamadı.", file=sys.stderr)
        return 2

    cli = args.kicad_cli or find_kicad_cli()
    if not cli:
        print("kicad-cli bulunamadı. PATH'e ekleyin veya --kicad-cli ile yolunu belirtin.", file=sys.stderr)
        return 2

    output = (Path(args.output_dir).expanduser() if args.output_dir else project_dir / "manufacturing")
    if not output.is_absolute():
        output = project_dir / output
    output = output.resolve()
    reports_dir = output / "reports"
    schematic_dir = output / "schematic"
    assembly_dir = output / "assembly"
    model_dir = output / "3d"
    output.mkdir(parents=True, exist_ok=True)
    for directory in (reports_dir, schematic_dir, assembly_dir, model_dir):
        directory.mkdir(parents=True, exist_ok=True)

    log_path = reports_dir / "build.log"
    results: list[StepResult] = []
    failures = 0
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write(f"KiCad build log\nProject: {project_dir}\nCLI: {cli}\n")
        run_step(cli, "KiCad sürümü", ["version"], log, results)

        if schematic:
            erc_report = reports_dir / f"{schematic.stem}-erc.rpt"
            run_step(cli, "Şematik ERC", ["sch", "erc", "--severity-all", "--exit-code-violations",
                     "--output", erc_report, schematic], log, results, violation_exit=True)
            run_step(cli, "Şematik PDF", ["sch", "export", "pdf", "--output",
                     schematic_dir / f"{schematic.stem}-schematic.pdf", schematic], log, results)
            run_step(cli, "BOM CSV", ["sch", "export", "bom", "--output",
                     output / f"{schematic.stem}-bom.csv", "--fields",
                     "Reference,Value,Footprint,QUANTITY,DNP", "--labels",
                     "Refs,Value,Footprint,Qty,DNP", "--sort-field", "Reference", "--sort-asc",
                     schematic], log, results)

        if board:
            drc_report = reports_dir / f"{board.stem}-drc.rpt"
            run_step(cli, "PCB DRC", ["pcb", "drc", "--severity-all", "--exit-code-violations",
                     "--output", drc_report, board], log, results, violation_exit=True)

            # Export into a fresh staging directory so the ZIP cannot include stale files.
            with tempfile.TemporaryDirectory(prefix="kicad-manufacturing-", dir=output) as temp_name:
                staging = Path(temp_name)
                gerber_dir = staging / "gerbers"
                drill_dir = staging / "drill"
                gerber_dir.mkdir()
                drill_dir.mkdir()
                run_step(cli, "Gerber dosyaları", ["pcb", "export", "gerbers", "--output",
                         gerber_dir, "--check-zones", board], log, results)
                run_step(cli, "Excellon drill ve harita", ["pcb", "export", "drill", "--output",
                         drill_dir, "--excellon-separate-th", "--generate-map", "--map-format", "pdf",
                         "--generate-report", "--report-path", drill_dir / f"{board.stem}-drill.rpt", board],
                         log, results)

                archive = output / f"{board.stem}-Gerber-Drill.zip"
                try:
                    files = sorted(path for path in staging.rglob("*") if path.is_file())
                    if not files:
                        raise RuntimeError("Gerber/drill çıktısı oluşmadı.")
                    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
                        for path in files:
                            package.write(path, path.relative_to(staging))
                    results.append(StepResult("Gerber + drill ZIP", "OK"))
                    print(f"[OK]  Gerber + drill ZIP: {archive.name}")
                except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                    results.append(StepResult("Gerber + drill ZIP", "HATA", str(exc)))
                    print(f"[HATA] Gerber + drill ZIP: {exc}")

            run_step(cli, "Montaj PDF (F.Fab/B.Fab)", ["pcb", "export", "pdf", "--mode-multipage",
                     "--layers", "F.Fab,B.Fab", "--output", assembly_dir / f"{board.stem}-assembly.pdf",
                     "--check-zones", board], log, results)
            run_step(cli, "3D STEP modeli", ["pcb", "export", "step", "--force", "--subst-models",
                     "--output", model_dir / f"{board.stem}.step", board], log, results)

    failures += sum(1 for result in results if result.status == "HATA")
    findings = [result for result in results if result.status == "BULGU"]
    print(f"\nÇıktı klasörü: {output}")
    print(f"Komut günlüğü: {log_path}")
    if findings:
        print("ERC/DRC bulguları raporlara yazıldı:")
        for result in findings:
            print(f"  - {result.name}: {result.detail}")
    if failures:
        print(f"Build {failures} hata ile tamamlandı. Ayrıntılar için build.log dosyasını inceleyin.")
        return 1
    if findings:
        print("Çıktılar oluşturuldu; ERC/DRC bulguları nedeniyle sonuç kodu 1.")
        return 1
    print("Tüm çıktılar başarıyla oluşturuldu.")
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    script_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="KiCad ERC/DRC ve üretim dosyalarını manufacturing/ içine çıkarır.")
    parser.add_argument("--project-dir", type=Path, default=script_root,
                        help="Proje klasörü (varsayılan: scripts/ klasörünün üst dizini).")
    parser.add_argument("--schematic", help="Kullanılacak .kicad_sch dosyası; göreli yollar proje köküne göredir.")
    parser.add_argument("--board", help="Kullanılacak .kicad_pcb dosyası; göreli yollar proje köküne göredir.")
    parser.add_argument("--kicad-cli", help="kicad-cli çalıştırılabilir dosyasının yolu.")
    parser.add_argument("--output-dir", type=Path, help="Çıktı dizini (varsayılan: <proje>/manufacturing).")
    return parser.parse_args(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(build(parse_args()))
    except KeyboardInterrupt:
        print("\nİşlem kullanıcı tarafından durduruldu.", file=sys.stderr)
        raise SystemExit(130)
