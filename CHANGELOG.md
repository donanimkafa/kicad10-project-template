# Changelog

All notable changes to this project are documented in this file.

This project follows [Semantic Versioning](https://semver.org/) and the
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

Company: Donanimkafa

## [Unreleased]

### Fixed

- Clear previous generated manufacturing files before a new build to prevent stale outputs after phase or project name changes.
- Remove the tracked Python bytecode cache; existing ignore rules prevent it from being added again.
- Document label setup through the existing GitHub Actions workflow, including how repeated runs update labels.
- Replace changelog link placeholders with the repository's actual GitHub address.

### Added

- Add unreleased changes here.

## [1.0.0] - 2026-10-18

### Added

- Initial KiCad project template and automated manufacturing documentation.

<!-- When creating a repository from this template, replace donanimkafa/kicad10-project-template with your own owner/repository. -->
[Unreleased]: https://github.com/donanimkafa/kicad10-project-template/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/donanimkafa/kicad10-project-template/releases/tag/v1.0.0
