# across-protocol-py

[![CI](https://github.com/robertruben98/across-protocol-py/actions/workflows/ci.yml/badge.svg)](https://github.com/robertruben98/across-protocol-py/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/across-protocol-py.svg)](https://pypi.org/project/across-protocol-py/)
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://robertruben98.github.io/across-protocol-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/across-protocol-py.svg)](https://pypi.org/project/across-protocol-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A typed Python client for the [Across Protocol](https://across.to) bridge API. It wraps the
public, keyless quoting endpoints with [`pydantic`](https://docs.pydantic.dev) v2 models and
ships both synchronous and asynchronous [`httpx`](https://www.python-httpx.org)-based clients.

- Sync (`AcrossClient`) and async (`AsyncAcrossClient`) clients with identical surfaces.
- Fully typed (`py.typed`), validated request/response models.
- Headline quoting via `/suggested-fees`, plus `/available-routes`, `/limits`, and deposit
  status tracking with a poll-to-terminal helper.

## Installation

```bash
pip install across-protocol-py
```

## Quickstart

Get a cross-chain bridge quote (USDC from Ethereum to Polygon) in a few lines:

```python
from across_protocol import AcrossClient

with AcrossClient() as client:
    quote = client.get_suggested_fees(
        input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",   # USDC on Ethereum
        output_token="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC.e on Polygon
        origin_chain_id=1,
        destination_chain_id=137,
        amount=10_000_000,  # 10 USDC (6 decimals)
    )
    print(f"Output amount: {quote.output_amount}")
    print(f"Total relay fee: {quote.total_relay_fee.total}")
    print(f"Estimated fill time: {quote.estimated_fill_time_sec}s")
```

The async client mirrors the sync API:

```python
import asyncio
from across_protocol import AsyncAcrossClient


async def main() -> None:
    async with AsyncAcrossClient() as client:
        quote = await client.get_suggested_fees(
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            origin_chain_id=1,
            destination_chain_id=137,
            amount=10_000_000,
        )
        print(quote.output_amount)


asyncio.run(main())
```

## Other endpoints

```python
with AcrossClient() as client:
    routes = client.get_available_routes()             # GET /available-routes
    limits = client.get_limits(...)                    # GET /limits
    status = client.get_deposit_status(                # GET /deposit/status
        origin_chain_id=1, deposit_id=2000000,
    )
    # Block until the deposit reaches a terminal state (filled / refunded / expired):
    final = client.wait_for_deposit(origin_chain_id=1, deposit_id=2000000)
```

## Configuration

The base URL defaults to `https://app.across.to/api` and can be overridden:

```python
client = AcrossClient(base_url="https://testnet.across.to/api", timeout=30.0)
```

## Development

```bash
pip install -e ".[dev]"
ruff check .
mypy src
pytest -q                      # unit tests (respx-mocked)
pytest -m integration -q       # live integration test (hits the real API)
```

## License

MIT
