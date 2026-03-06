# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

## [0.1.0] - 2026-03-07

### Added
- Centralized configuration module with environment-driven RAG/API settings.
- Vector index persistence and reload support for CLI and API.
- API upload guards (file extension and file size validation).
- Test suite for config, utils, API behavior, and RAG document routing.
- Open source maintenance assets:
  - License
  - Contributing guide
  - Code of conduct
  - Security policy
  - Issue and PR templates
  - CI workflow

### Changed
- Reworked imports to package-based `src.*` style.
- Replaced deprecated FastAPI startup event usage with lifespan handlers.
- Updated dependency constraints for LangChain compatibility.
- Replaced pseudo sample PDF/DOCX generation with real text samples.
