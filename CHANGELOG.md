# Changelog

All notable changes to this package are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.4.0] — 2026-08-28

The first release since **1.0.32 (2024-12-18)**. Twenty months of work reached `main`
without being published, so this release covers all of it rather than a single feature.
Everything below is already on `main` and has been for some time; what is new is that it
is installable.

Note on version numbering: `setup.py` never carried `1.0.32` — it went 1.0.31 → 1.3.2 →
1.4.0 — so there is no commit or tag in this repository corresponding to the last
published package. This release restores the correspondence, and it is tagged.

### Added

- **Real-time WebSocket: all ten markets.** The European equity streams (`eu`,
  `eu-quote`) and the derived ones (`us-candles`, `eu-candles`, `us-status`,
  `eu-status`) alongside the existing `us`, `us-quote`, `forex` and `crypto`.
  `max_symbols` is now a constructor argument rather than a hard-coded 50, since 50 is
  the default plan allowance and larger plans exist.
- **Credit & Sovereign Risk, Sanctions, and Interest Rates APIs.**
- **Real Estate Data API** (BIS property prices).
- **Commodities Historical Data API.**
- **Exchange Details API v2** and **Fundamentals API v1.1**.
- **17 further methods** across Search, Logo, User, Bulk Fundamentals, Treasury, ESG and
  the Unicornbay marketplace extras.
- **Marketplace endpoints**: Options Contracts, Options Underlying Symbols, Options
  End-of-Day, and Index Components.
- **US Live Extended Quotes**, **Upcoming Dividends**, **Mapping ID**, and additional
  Technical API functions.
- A parameter to retrieve listed and delisted tickers in one call.

### Fixed

- **WebSocket control frames were treated as market data.** Nothing filtered them, so the
  `{"status_code": 200, "message": "Authorized"}` acknowledgement and a `{"status": 403}`
  authentication denial were both stored, printed and fed to the candle builder. A wrong
  API key produced a stream of nonsense instead of an error. Authentication failures use
  the key `status` and arrive over the socket *after* a successful handshake, so opening
  the connection never proved the token was good.
- **European symbols could not be subscribed at all.** The symbol validator was
  `^[A-z0-9-$]{1,48}$`, which contains no dot, so `GSK.LSE`, `SAP.XETRA` and `ASML.AS`
  were rejected client-side before a socket was opened. (`[A-z]` also admitted the ASCII
  punctuation between `Z` and `a`.)
- **Candle aggregation raised `KeyError` on the `us` feed.** Volume accumulation read
  `q` unconditionally, but the equity trade streams carry size in `v`, so
  `display_candle_1m=True` failed on the second trade of a bar.
- **Crypto candle highs and lows were wrong.** Crypto sends prices as JSON strings, and
  the comparisons ran on those strings, where `"9" > "10"`.
- Error hierarchy, session pooling, request timeouts and WebSocket reconnection.
- Free-tier `warning` column handled in `get_historical_data`.
- Return-type annotations on `get_fundamentals_data` corrected.
- Commodity codes and interval values aligned with the backend; the unsupported `fmt`
  parameter removed from the Commodities API.
- API-key rights errors surfaced properly.

### Removed

- Retired endpoint wrappers for the old Bond Fundamentals and old Options APIs.

## [1.0.32] — 2024-12-18

Last release before the gap above. See the git history for detail; this file starts here.
