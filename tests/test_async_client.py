"""Tests for the asynchronous AsyncAcrossClient using respx-mocked HTTP."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from across_protocol import (
    AcrossAPIError,
    AsyncAcrossClient,
    AvailableRoute,
    DepositStatus,
    Limits,
    SuggestedFees,
)

BASE = "https://app.across.to/api"


async def test_default_base_url() -> None:
    async with AsyncAcrossClient() as client:
        assert client.base_url == BASE


async def test_custom_base_url_strips_trailing_slash() -> None:
    async with AsyncAcrossClient(base_url="https://testnet.across.to/api/") as client:
        assert client.base_url == "https://testnet.across.to/api"


@respx.mock
async def test_get_suggested_fees(suggested_fees_payload: dict[str, Any]) -> None:
    route = respx.get(f"{BASE}/suggested-fees").mock(
        return_value=httpx.Response(200, json=suggested_fees_payload)
    )
    async with AsyncAcrossClient() as client:
        fees = await client.get_suggested_fees(
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            origin_chain_id=1,
            destination_chain_id=137,
            amount=10_000_000,
        )
    assert isinstance(fees, SuggestedFees)
    assert fees.output_amount == "9990351"
    params = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert params["amount"] == "10000000"


@respx.mock
async def test_get_available_routes(
    available_routes_payload: list[dict[str, Any]],
) -> None:
    respx.get(f"{BASE}/available-routes").mock(
        return_value=httpx.Response(200, json=available_routes_payload)
    )
    async with AsyncAcrossClient() as client:
        routes = await client.get_available_routes()
    assert len(routes) == 2
    assert all(isinstance(r, AvailableRoute) for r in routes)


@respx.mock
async def test_get_limits(limits_payload: dict[str, Any]) -> None:
    respx.get(f"{BASE}/limits").mock(return_value=httpx.Response(200, json=limits_payload))
    async with AsyncAcrossClient() as client:
        limits = await client.get_limits(
            input_token="0xa",
            output_token="0xb",
            origin_chain_id=1,
            destination_chain_id=137,
        )
    assert isinstance(limits, Limits)
    assert limits.max_deposit == "1389862444460"


@respx.mock
async def test_get_deposit_status(deposit_status_payload: dict[str, Any]) -> None:
    route = respx.get(f"{BASE}/deposit/status").mock(
        return_value=httpx.Response(200, json=deposit_status_payload)
    )
    async with AsyncAcrossClient() as client:
        status = await client.get_deposit_status(origin_chain_id=1, deposit_id=2000000)
    assert isinstance(status, DepositStatus)
    assert status.status == "filled"
    params = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert params["depositId"] == "2000000"


async def test_get_deposit_status_requires_identifier() -> None:
    async with AsyncAcrossClient() as client:
        with pytest.raises(ValueError):
            await client.get_deposit_status()


@respx.mock
async def test_api_error_raised_on_4xx() -> None:
    respx.get(f"{BASE}/limits").mock(
        return_value=httpx.Response(400, json={"message": "bad route"})
    )
    async with AsyncAcrossClient() as client:
        with pytest.raises(AcrossAPIError) as exc_info:
            await client.get_limits(
                input_token="0xa",
                output_token="0xb",
                origin_chain_id=1,
                destination_chain_id=137,
            )
    assert exc_info.value.status_code == 400


@respx.mock
async def test_wait_for_deposit_polls_until_terminal() -> None:
    pending = {"status": "pending"}
    refunded = {"status": "refunded"}
    respx.get(f"{BASE}/deposit/status").mock(
        side_effect=[
            httpx.Response(200, json=pending),
            httpx.Response(200, json=refunded),
        ]
    )
    async with AsyncAcrossClient() as client:
        final = await client.wait_for_deposit(origin_chain_id=1, deposit_id=5, poll_interval=0.0)
    assert final.status == "refunded"
    assert respx.calls.call_count == 2


@respx.mock
async def test_wait_for_deposit_times_out() -> None:
    respx.get(f"{BASE}/deposit/status").mock(
        return_value=httpx.Response(200, json={"status": "pending"})
    )
    async with AsyncAcrossClient() as client:
        with pytest.raises(TimeoutError):
            await client.wait_for_deposit(
                origin_chain_id=1, deposit_id=5, poll_interval=0.0, timeout=0.05
            )
