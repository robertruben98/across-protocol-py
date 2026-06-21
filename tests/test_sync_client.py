"""Tests for the synchronous AcrossClient using respx-mocked HTTP."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from across_protocol import (
    AcrossAPIError,
    AcrossClient,
    AvailableRoute,
    DepositStatus,
    Limits,
    SuggestedFees,
)

BASE = "https://app.across.to/api"


def test_default_base_url() -> None:
    with AcrossClient() as client:
        assert client.base_url == BASE


def test_custom_base_url_strips_trailing_slash() -> None:
    with AcrossClient(base_url="https://testnet.across.to/api/") as client:
        assert client.base_url == "https://testnet.across.to/api"


@respx.mock
def test_get_suggested_fees(suggested_fees_payload: dict[str, Any]) -> None:
    route = respx.get(f"{BASE}/suggested-fees").mock(
        return_value=httpx.Response(200, json=suggested_fees_payload)
    )

    with AcrossClient() as client:
        fees = client.get_suggested_fees(
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            origin_chain_id=1,
            destination_chain_id=137,
            amount=10_000_000,
        )

    assert isinstance(fees, SuggestedFees)
    assert fees.output_amount == "9990351"
    sent = route.calls.last.request
    params = dict(httpx.QueryParams(sent.url.query))
    assert params["inputToken"] == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    assert params["outputToken"] == "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    assert params["originChainId"] == "1"
    assert params["destinationChainId"] == "137"
    assert params["amount"] == "10000000"
    assert "recipient" not in params


@respx.mock
def test_get_suggested_fees_includes_optional_recipient(
    suggested_fees_payload: dict[str, Any],
) -> None:
    route = respx.get(f"{BASE}/suggested-fees").mock(
        return_value=httpx.Response(200, json=suggested_fees_payload)
    )

    with AcrossClient() as client:
        client.get_suggested_fees(
            input_token="0xinput",
            output_token="0xoutput",
            origin_chain_id=1,
            destination_chain_id=137,
            amount=5,
            recipient="0xrecipient",
        )

    params = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert params["recipient"] == "0xrecipient"


@respx.mock
def test_amount_accepts_string(suggested_fees_payload: dict[str, Any]) -> None:
    route = respx.get(f"{BASE}/suggested-fees").mock(
        return_value=httpx.Response(200, json=suggested_fees_payload)
    )
    with AcrossClient() as client:
        client.get_suggested_fees(
            input_token="0xa",
            output_token="0xb",
            origin_chain_id=1,
            destination_chain_id=137,
            amount="1000000000000000000",
        )
    params = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert params["amount"] == "1000000000000000000"


@respx.mock
def test_get_available_routes(available_routes_payload: list[dict[str, Any]]) -> None:
    respx.get(f"{BASE}/available-routes").mock(
        return_value=httpx.Response(200, json=available_routes_payload)
    )
    with AcrossClient() as client:
        routes = client.get_available_routes()
    assert len(routes) == 2
    assert all(isinstance(r, AvailableRoute) for r in routes)
    assert routes[0].origin_token_symbol == "WETH"


@respx.mock
def test_get_available_routes_with_filters(
    available_routes_payload: list[dict[str, Any]],
) -> None:
    route = respx.get(f"{BASE}/available-routes").mock(
        return_value=httpx.Response(200, json=available_routes_payload)
    )
    with AcrossClient() as client:
        client.get_available_routes(origin_chain_id=1, destination_chain_id=137)
    params = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert params["originChainId"] == "1"
    assert params["destinationChainId"] == "137"


@respx.mock
def test_get_limits(limits_payload: dict[str, Any]) -> None:
    route = respx.get(f"{BASE}/limits").mock(return_value=httpx.Response(200, json=limits_payload))
    with AcrossClient() as client:
        limits = client.get_limits(
            input_token="0xa",
            output_token="0xb",
            origin_chain_id=1,
            destination_chain_id=137,
        )
    assert isinstance(limits, Limits)
    assert limits.max_deposit == "1389862444460"
    params = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert params["originChainId"] == "1"


@respx.mock
def test_get_deposit_status_by_deposit_id(deposit_status_payload: dict[str, Any]) -> None:
    route = respx.get(f"{BASE}/deposit/status").mock(
        return_value=httpx.Response(200, json=deposit_status_payload)
    )
    with AcrossClient() as client:
        status = client.get_deposit_status(origin_chain_id=1, deposit_id=2000000)
    assert isinstance(status, DepositStatus)
    assert status.status == "filled"
    params = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert params["originChainId"] == "1"
    assert params["depositId"] == "2000000"


@respx.mock
def test_get_deposit_status_by_tx_ref(deposit_status_payload: dict[str, Any]) -> None:
    route = respx.get(f"{BASE}/deposit/status").mock(
        return_value=httpx.Response(200, json=deposit_status_payload)
    )
    with AcrossClient() as client:
        client.get_deposit_status(deposit_tx_ref="0xabc")
    params = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert params["depositTxnRef"] == "0xabc"


def test_get_deposit_status_requires_identifier() -> None:
    with AcrossClient() as client, pytest.raises(ValueError):
        client.get_deposit_status()


def test_get_deposit_status_partial_id_pair_raises() -> None:
    with AcrossClient() as client, pytest.raises(ValueError):
        client.get_deposit_status(origin_chain_id=1)


@respx.mock
def test_api_error_raised_on_4xx() -> None:
    respx.get(f"{BASE}/suggested-fees").mock(
        return_value=httpx.Response(
            400, json={"error": "InvalidParamError", "message": "bad amount"}
        )
    )
    with AcrossClient() as client, pytest.raises(AcrossAPIError) as exc_info:
        client.get_suggested_fees(
            input_token="0xa",
            output_token="0xb",
            origin_chain_id=1,
            destination_chain_id=137,
            amount=1,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.response_body == {
        "error": "InvalidParamError",
        "message": "bad amount",
    }


@respx.mock
def test_wait_for_deposit_polls_until_terminal() -> None:
    pending = {"status": "pending", "originChainId": 1, "depositId": "5"}
    filled = {"status": "filled", "originChainId": 1, "depositId": "5"}
    respx.get(f"{BASE}/deposit/status").mock(
        side_effect=[
            httpx.Response(200, json=pending),
            httpx.Response(200, json=pending),
            httpx.Response(200, json=filled),
        ]
    )
    with AcrossClient() as client:
        final = client.wait_for_deposit(origin_chain_id=1, deposit_id=5, poll_interval=0.0)
    assert final.status == "filled"
    assert respx.calls.call_count == 3


@respx.mock
def test_wait_for_deposit_times_out() -> None:
    respx.get(f"{BASE}/deposit/status").mock(
        return_value=httpx.Response(200, json={"status": "pending"})
    )
    with AcrossClient() as client, pytest.raises(TimeoutError):
        client.wait_for_deposit(
            origin_chain_id=1, deposit_id=5, poll_interval=0.0, timeout=0.05
        )
