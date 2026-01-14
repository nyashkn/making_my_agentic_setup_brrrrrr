# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-14

### Added
- Initial release with modern config management
- Task-based command runner (replaces Make + bash)
- TOML-based structured configs (replaces .env)
- UV-powered Python tooling
- Claude Code mode switching (Anthropic API / AWS Bedrock)
- Personal config overrides (merge pattern)
- Auto-detected repository location (work from anywhere)
- Shell integration for automatic environment loading
- Placeholder directories for skills, agents, commands, MCP
- Version tracking and sync detection

### Features
- Flexible repository location (clone/work anywhere)
- Personal configs always in ~/.claude/ (consistent)
- Python tools with auto-detection via Path(__file__)
- Task uses {{.ROOT_DIR}} for repo location
- Skills/agents/commands installation workflow
- Settings template management
- MCP server configuration

### Documentation
- Quick start guide
- Setup and usage documentation
- Architecture overview
- Update workflow
