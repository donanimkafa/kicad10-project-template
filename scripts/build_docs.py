#!/usr/bin/env python3
"""Build KiCad lifecycle deliverables with the KiCad CLI."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

try:  # Support both direct script execution and importing in tests/tools.
    from .update_title_block import update_title_blocks
except ImportError:
    from update_title_block import update_title_blocks


PHASES = ("draft", "preliminary", "checked", "release")
PHASE_MARKER_RE = re.compile(r"\bPHASE\s*:\s*([A-Za-z0-9_-]*)", re.IGNORECASE)


@dataclass
class StepResult:
    name: str
    status: str
    detail: str = ""


def find_kicad_cli() -> str | None:
    """Find kicad-cli on PATH or common platform install locations."""
    executable = "kicad-cli.exe" if os.name == "nt" else "kicad-cli"
    on_path = shutil.which(executable) or shutil.which("kicad-cli")
    if on_path:
        return on_path

    candidates: list[Path] = []
    if sys.platform == "darwin":
        candidates.append(Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"))
    elif os.name == "nt":
        for base in (
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        ):
            candidates.extend(base.glob("KiCad/*/bin/kicad-cli.exe"))
    else:
        candidates.extend((Path("/usr/bin/kicad-cli"), Path("/usr/local/bin/kicad-cli")))
    return str(next((path for path in candidates if path.is_file()), "")) or None


def resolve_input(
    value: str | None,
    project_dir: Path,
    suffix: str,
    label: str,
    search_dir: Path | None = None,
) -> Path | None:
    """Return the requested KiCad file.

    Explicit relative paths are resolved against ``project_dir`` (repo root).
    Automatic discovery requires exactly one matching file inside ``search_dir``.
    """
    search_dir = search_dir or project_dir
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
        (p for p in search_dir.iterdir() if p.is_file() and p.suffix.lower() == suffix),
        key=lambda p: p.name.casefold(),
    )
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    choices = "\n  ".join(p.name for p in candidates)
    raise ValueError(f"Birden fazla {label} dosyası bulundu. --{label} ile seçim yapın:\n  {choices}")


def detect_phase(schematic: Path, project_dir: Path) -> str:
    """Read PHASE from a schematic comment or KiCad project text variable."""
    try:
        text = schematic.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Şematik UTF-8 olarak okunamadı: {schematic}") from exc

    schematic_phases = [match.group(1).lower() for match in PHASE_MARKER_RE.finditer(text)]

    # KiCad's custom text-variable table is stored in the sibling .kicad_pro
    # JSON file, while a Page Settings comment is serialized in .kicad_sch.
    # Support both UI entry points so engineers can choose either one.
    matching_project = schematic.with_suffix(".kicad_pro")
    if matching_project.is_file():
        project_files = [matching_project]
    else:
        project_files = sorted(project_dir.glob("*.kicad_pro"))
        if len(project_files) > 1:
            raise ValueError(
                "PHASE text variable için birden fazla .kicad_pro dosyası var; "
                "şematikle aynı ada sahip proje dosyası gerekli."
            )
    project_phases: list[str] = []
    for project_file in project_files[:1]:
        if not project_file.is_file():
            continue
        try:
            project_data = json.loads(project_file.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"KiCad proje ayarları okunamadı: {project_file}: {exc}") from exc
        variables = project_data.get("text_variables", {})
        if isinstance(variables, dict):
            for name, value in variables.items():
                if str(name).casefold() == "phase":
                    variable_value = str(value).strip()
                    embedded_marker = PHASE_MARKER_RE.search(variable_value)
                    project_phases.append(
                        embedded_marker.group(1).lower() if embedded_marker else variable_value.lower()
                    )

    matches = schematic_phases + project_phases
    if not matches:
        print("[INFO] Şematikte veya proje Text Variables alanında PHASE bulunamadı; varsayılan 'checked' kullanılacak.")
        return "checked"

    invalid = sorted(set(matches) - set(PHASES))
    if invalid:
        raise ValueError(
            f"Şematikte geçersiz PHASE değeri: {', '.join(invalid)}. "
            f"Kullanılabilir değerler: {', '.join(PHASES)}."
        )
    unique = set(matches)
    if len(unique) > 1:
        raise ValueError(
            "Şematik ve/veya KiCad proje ayarlarında birden fazla farklı PHASE değeri bulundu: "
            + ", ".join(sorted(unique))
            + ". Tek bir aşama belirtin."
        )
    return matches[0]


def write_phase_output(phase: str) -> None:
    """Expose the detected phase to later GitHub Actions jobs, when applicable."""
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8", newline="\n") as output:
            output.write(f"phase={phase}\n")


def run_step(
    cli: str,
    name: str,
    args: Sequence[str | Path],
    log,
    results: list[StepResult],
    *,
    violation_exit: bool = False,
    ignore_violation: bool = False,
    timeout_seconds: int = 300,
) -> bool:
    command = [cli, *(str(arg) for arg in args)]
    print(f"[RUN] {name} (zaman aşımı: {timeout_seconds} sn)", flush=True)
    log.write("\n$ " + subprocess.list2cmdline(command) + "\n")
    log.flush()
    try:
        completed = subprocess.run(
            command, text=True, capture_output=True, check=False, timeout=timeout_seconds
        )
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or "", exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        if stdout:
            log.write(stdout)
        if stderr:
            log.write("[stderr]\n" + stderr)
        detail = f"{timeout_seconds} saniyede tamamlanmadı; işlem durduruldu."
        log.write(f"[TIMEOUT] {detail}\n")
        results.append(StepResult(name, "HATA", detail))
        print(f"[ZAMAN AŞIMI] {name}: {detail}")
        return False
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
    # KiCad 10 uses exit code 5 when ERC/DRC violations are present.
    if violation_exit and completed.returncode == 5:
        detail = "ERC/DRC bulguları bulundu; raporu inceleyin."
        results.append(StepResult(name, "BULGU", detail))
        if ignore_violation:
            print(f"[UYARI] {name}: {detail} Derleme devam ediyor.")
            return True
        print(f"[HATA] {name}: {detail} Bu aşamada derleme durduruluyor.")
        return False

    detail = f"kicad-cli çıkış kodu: {completed.returncode}"
    results.append(StepResult(name, "HATA", detail))
    print(f"[HATA] {name}: {detail}; build.log dosyasını inceleyin.")
    return False


def clean_generated_outputs(output: Path) -> int:
    """Remove known build products, preserving unrelated files and directories."""
    patterns = (
        "*-bom.csv", "*-Gerber-Drill.zip",
        "schematic/*-schematic.pdf", "assembly/*-assembly.pdf",
        "fabrication/*-fabrication.pdf", "3d/*.step",
        "fabrication/*_Gerbers.zip",
        "reports/*-erc.rpt", "reports/*-drc.rpt", "reports/build.log",
    )
    root = output.resolve()
    candidates = sorted({path for pattern in patterns for path in output.glob(pattern)})
    # Validate every candidate before deleting anything. In particular, do not
    # follow linked output subdirectories outside the selected output folder.
    for path in candidates:
        if not path.resolve().is_relative_to(root):
            raise ValueError(f"Çıktı klasörü dışına yönlenen dosya temizlenemez: {path}")
        if not path.is_file() and not path.is_symlink():
            raise ValueError(f"Üretim dosyası yerine klasör bulundu: {path}")
    for path in candidates:
        path.unlink()
    return len(candidates)


def build(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.is_dir():
        print(f"Proje klasörü bulunamadı: {project_dir}", file=sys.stderr)
        return 2

    # KiCad dosyalarının bulunduğu klasör (varsayılan: <proje>/hardware).
    # Klasör yoksa eski düzenle uyumlu kalmak için proje köküne geri döner.
    hardware_dir = Path(args.hardware_dir).expanduser()
    if not hardware_dir.is_absolute():
        hardware_dir = project_dir / hardware_dir
    hardware_dir = hardware_dir.resolve()
    if not hardware_dir.is_dir():
        print(f"[INFO] {hardware_dir} bulunamadı; KiCad dosyaları proje kökünde aranacak.")
        hardware_dir = project_dir

    try:
        schematic = resolve_input(args.schematic, project_dir, ".kicad_sch", "schematic", hardware_dir)
        board = resolve_input(args.board, project_dir, ".kicad_pcb", "board", hardware_dir)
    except ValueError as exc:
        print(f"Hata: {exc}", file=sys.stderr)
        return 2

    if schematic is None:
        print(f"{hardware_dir} içinde .kicad_sch bulunamadı; tüm aşamalar şematik gerektirir.", file=sys.stderr)
        return 2
    try:
        phase = detect_phase(schematic, schematic.parent)
    except (OSError, ValueError) as exc:
        print(f"PHASE bilgisi okunamadı: {exc}", file=sys.stderr)
        return 2
    print(f"[INFO] Şematikten seçilen aşama: {phase}")
    write_phase_output(phase)

    if phase != "draft" and board is None:
        print(f"{phase} aşaması için {hardware_dir} içinde .kicad_pcb dosyası gerekli.", file=sys.stderr)
        return 2

    title_block_files = [schematic]
    if board is not None:
        title_block_files.append(board)
    try:
        metadata = update_title_blocks(
            project_dir,
            title_block_files,
            changelog=args.changelog,
            company=args.company,
        )
    except (OSError, ValueError) as exc:
        print(f"Başlık bloğu güncellenemedi: {exc}", file=sys.stderr)
        return 2
    print(f"Başlık bloğu metadata kaynağı: {metadata.source}; revizyon {metadata.revision}.")

    cli = args.kicad_cli or find_kicad_cli()
    if not cli:
        print("kicad-cli bulunamadı. PATH'e ekleyin veya --kicad-cli ile yolunu belirtin.", file=sys.stderr)
        return 2

    output = Path(args.output_dir).expanduser() if args.output_dir else project_dir / "manufacturing"
    if not output.is_absolute():
        output = project_dir / output
    output = output.resolve()
    try:
        removed = clean_generated_outputs(output)
    except (OSError, ValueError) as exc:
        print(f"Eski üretim çıktıları temizlenemedi: {exc}", file=sys.stderr)
        return 2
    print(f"[INFO] Önceki çalışmalardan kalan {removed} üretim dosyası temizlendi.")
    reports_dir = output / "reports"
    schematic_dir = output / "schematic"
    assembly_dir = output / "assembly"
    model_dir = output / "3d"
    for directory in (reports_dir, schematic_dir, assembly_dir, model_dir):
        directory.mkdir(parents=True, exist_ok=True)

    log_path = reports_dir / "build.log"
    results: list[StepResult] = []
    ignore_error = phase == "preliminary"
    strict_checks = phase in ("checked", "release")

    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write(f"KiCad build log\nPhase: {phase}\nProject: {project_dir}\nCLI: {cli}\n")
        log.write(f"KiCad version: {args.kicad_version or 'container/local default'}\n")

        # Draft produces only schematic PDF and BOM; no ERC/DRC or PCB outputs.
        if phase != "draft":
            erc_report = reports_dir / f"{schematic.stem}-erc.rpt"
            if not run_step(
                cli, "Şematik ERC",
                ["sch", "erc", "--severity-all", "--exit-code-violations", "--output", erc_report, schematic],
                log, results, violation_exit=True, ignore_violation=ignore_error,
                timeout_seconds=args.timeout,
            ):
                return finish(results, output, log_path, strict_checks)

            assert board is not None
            drc_report = reports_dir / f"{board.stem}-drc.rpt"
            if not run_step(
                cli, "PCB DRC",
                ["pcb", "drc", "--severity-all", "--exit-code-violations", "--output", drc_report, board],
                log, results, violation_exit=True, ignore_violation=ignore_error,
                timeout_seconds=args.timeout,
            ):
                return finish(results, output, log_path, strict_checks)

        # Every phase includes schematic PDF and BOM.
        if not run_step(
            cli, "Şematik PDF",
            ["sch", "export", "pdf", "--output", schematic_dir / f"{schematic.stem}-schematic.pdf", schematic],
            log, results, timeout_seconds=args.timeout,
        ):
            return finish(results, output, log_path, strict_checks)

        if not run_step(
            cli, "BOM CSV",
            ["sch", "export", "bom", "--output", output / f"{schematic.stem}-bom.csv", schematic],
            log, results, timeout_seconds=args.timeout,
        ):
            return finish(results, output, log_path, strict_checks)

        if phase != "draft":
            assert board is not None
            with tempfile.TemporaryDirectory(prefix="kicad-manufacturing-", dir=output) as temp_name:
                staging = Path(temp_name)
                gerber_dir, drill_dir = staging / "gerbers", staging / "drill"
                gerber_dir.mkdir()
                drill_dir.mkdir()
                gerbers_ok = run_step(
                    cli, "Gerber dosyaları",
                    ["pcb", "export", "gerbers", "--output", gerber_dir, "--check-zones", board],
                    log, results, timeout_seconds=args.timeout,
                )
                drill_ok = run_step(
                    cli, "Excellon drill ve harita",
                    ["pcb", "export", "drill", "--output", drill_dir, "--excellon-separate-th",
                     "--generate-map", "--map-format", "pdf", "--generate-report", "--report-path",
                     drill_dir / f"{board.stem}-drill.rpt", board],
                    log, results, timeout_seconds=args.timeout,
                )
                if not (gerbers_ok and drill_ok):
                    return finish(results, output, log_path, strict_checks)

                zip_suffix = "-preliminary-Gerber-Drill.zip" if phase == "preliminary" else "-Gerber-Drill.zip"
                archive = output / f"{board.stem}{zip_suffix}"
                try:
                    files = sorted(p for p in staging.rglob("*") if p.is_file())
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
                    return finish(results, output, log_path, strict_checks)

            if not run_step(
                cli, "Montaj PDF (F.Fab/B.Fab)",
                ["pcb", "export", "pdf", "--mode-multipage", "--layers", "F.Fab,B.Fab", "--output",
                 assembly_dir / f"{board.stem}-assembly.pdf", "--check-zones", board],
                log, results, timeout_seconds=args.timeout,
            ):
                return finish(results, output, log_path, strict_checks)

            if not run_step(
                cli, "3D STEP modeli",
                ["pcb", "export", "step", "--force", "--subst-models", "--output",
                 model_dir / f"{board.stem}.step", board],
                log, results, timeout_seconds=args.timeout,
            ):
                return finish(results, output, log_path, strict_checks)

    return finish(results, output, log_path, strict_checks)


def finish(results: list[StepResult], output: Path, log_path: Path, strict_checks: bool) -> int:
    findings = [result for result in results if result.status == "BULGU"]
    failures = [result for result in results if result.status == "HATA"]
    print(f"\nÇıktı klasörü: {output}")
    print(f"Komut günlüğü: {log_path}")
    if findings:
        print("ERC/DRC bulguları raporlara yazıldı:")
        for result in findings:
            print(f"  - {result.name}: {result.detail}")
    if failures:
        print(f"Build {len(failures)} hata ile tamamlandı. Ayrıntılar için build.log dosyasını inceleyin.")
        return 1
    if findings and strict_checks:
        print("Checked/release aşaması ERC/DRC bulguları nedeniyle başarısız oldu.")
        return 1
    if findings:
        print("Preliminary çıktıları oluşturuldu; ERC/DRC bulguları derlemeyi durdurmadı.")
    else:
        print("Tüm istenen çıktılar başarıyla oluşturuldu.")
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    script_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="KiCad lifecycle aşamasına göre manufacturing/ çıktıları oluşturur."
    )
    parser.add_argument("--project-dir", type=Path, default=script_root,
                        help="Proje klasörü (varsayılan: scripts/ klasörünün üst dizini).")
    parser.add_argument("--hardware-dir", type=Path, default=Path("hardware"),
                        help="KiCad dosyalarının klasörü; göreli yol proje köküne göredir (varsayılan: hardware).")
    parser.add_argument("--schematic", help="Şematik dosyası; göreli yollar proje köküne göredir.")
    parser.add_argument("--board", help="PCB dosyası; göreli yollar proje köküne göredir.")
    parser.add_argument("--kicad-cli", help="kicad-cli çalıştırılabilir dosyasının yolu.")
    parser.add_argument("--kicad-version", help="Build günlüğüne yazılacak KiCad sürüm etiketi.")
    parser.add_argument("--changelog", type=Path,
                        help="Changelog yolu (varsayılan: <proje>/CHANGELOG.md).")
    parser.add_argument("--company", help="Başlık bloğunda kullanılacak şirket adı; changelog/env değerini geçersiz kılar.")
    parser.add_argument("--output-dir", type=Path, help="Çıktı dizini (varsayılan: <proje>/manufacturing).")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Her kicad-cli komutu için saniye sınırı (varsayılan: 300).")
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(build(parse_args()))
