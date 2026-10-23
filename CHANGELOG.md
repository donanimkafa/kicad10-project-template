# Changelog

All notable changes to this project are documented in this file.

This project follows [Semantic Versioning](https://semver.org/) and the
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

Company: Donanimkafa

## [Unreleased]

### Fixed

- Resolve the root schematic through a unique matching KiCad project file so hierarchical subsheets do not make CI input selection ambiguous.

- Clear previous generated manufacturing files before a new build to prevent stale outputs after phase or project name changes.
- Remove the tracked Python bytecode cache; existing ignore rules prevent it from being added again.
- Document label setup through the existing GitHub Actions workflow, including how repeated runs update labels.
- Replace changelog link placeholders with the repository's actual GitHub address.
- Require explicit schematic/board selection when multiple matching KiCad files exist, instead of choosing by directory name.
- Correct title-block updater error messages to suggest the actual --schematic and --board options.
- Verify kicad-cli can run before updating title blocks or clearing previous manufacturing outputs.

### Added

- Package the cover as a KiCad user template with metadata, an allowlisted ZIP builder and installation instructions.

- Add an editable A3 schematic cover with project metadata, a manual contents index, PCB image placeholders and design notes.

- Document the Issue → working branch → PR → main → version tag workflow, with early Draft PRs for CI checks and release preparation guidance.

### Changed

- Run branch push CI on main; use main-targeting PRs for working branch checks instead of requiring a persistent dev branch.
- Add target branch and linked Issue checks to the PR template.

## [1.0.0] - 2026-10-18

### Added

- Initial KiCad project template and automated manufacturing documentation.

<!-- When creating a repository from this template, replace donanimkafa/kicad10-project-template with your own owner/repository. -->
[Unreleased]: https://github.com/donanimkafa/kicad10-project-template/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/donanimkafa/kicad10-project-template/releases/tag/v1.0.0
