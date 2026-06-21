# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-21

### Added

- Initial release.
- Synchronous `AcrossClient` and asynchronous `AsyncAcrossClient`, with identical surfaces.
- `get_suggested_fees` — headline bridge quote via `GET /suggested-fees`.
- `get_available_routes` — supported token routes via `GET /available-routes`.
- `get_limits` — per-route transfer limits via `GET /limits`.
- `get_deposit_status` and `wait_for_deposit` — deposit lifecycle tracking via
  `GET /deposit/status`, including a poll-to-terminal helper.
- Fully typed (`py.typed`) pydantic v2 models for all responses.
- Configurable base URL (defaults to `https://app.across.to/api`) and request timeout.
- `AcrossError` / `AcrossAPIError` exception hierarchy.

[0.1.0]: https://github.com/robertruben98/across-protocol-py/releases/tag/v0.1.0
