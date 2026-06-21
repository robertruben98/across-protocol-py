"""Tests for pydantic response models parsing real Across API payloads."""

from __future__ import annotations

from typing import Any

from across_protocol import (
    AvailableRoute,
    DepositStatus,
    Limits,
    SuggestedFees,
)


def test_suggested_fees_parses_real_payload(suggested_fees_payload: dict[str, Any]) -> None:
    fees = SuggestedFees.model_validate(suggested_fees_payload)

    assert fees.estimated_fill_time_sec == 2
    assert fees.output_amount == "9990351"
    assert fees.is_amount_too_low is False
    assert fees.timestamp == "1782074207"
    assert fees.total_relay_fee.pct == "964900000000000"
    assert fees.total_relay_fee.total == "9649"
    assert fees.limits.min_deposit == "500154"
    assert fees.input_token.symbol == "USDC"
    assert fees.input_token.decimals == 6
    assert fees.output_token.symbol == "USDC.e"
    assert fees.output_token.chain_id == 137
    assert fees.spoke_pool_address == "0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5"


def test_suggested_fees_tolerates_unknown_fields(
    suggested_fees_payload: dict[str, Any],
) -> None:
    suggested_fees_payload["someBrandNewField"] = "ignore me"
    fees = SuggestedFees.model_validate(suggested_fees_payload)
    assert fees.output_amount == "9990351"


def test_available_route_parses_real_payload(
    available_routes_payload: list[dict[str, Any]],
) -> None:
    route = AvailableRoute.model_validate(available_routes_payload[0])
    assert route.origin_chain_id == 1
    assert route.destination_chain_id == 4326
    assert route.origin_token_symbol == "WETH"
    assert route.is_native is False


def test_limits_parses_real_payload(limits_payload: dict[str, Any]) -> None:
    limits = Limits.model_validate(limits_payload)
    assert limits.min_deposit == "500154"
    assert limits.max_deposit == "1389862444460"
    assert limits.relayer_fee_details.relay_fee_total == "7895"
    assert limits.reserves.liquid_reserves == "948756529073"


def test_deposit_status_parses_real_payload(deposit_status_payload: dict[str, Any]) -> None:
    status = DepositStatus.model_validate(deposit_status_payload)
    assert status.status == "filled"
    assert status.origin_chain_id == 1
    assert status.deposit_id == "2000000"
    assert status.destination_chain_id == 8453
    assert status.fill_tx_ref == (
        "0xe2d2361de170a8c437a6b2a91ca280365327038186aebc39264ad840e15f6bd0"
    )
    assert status.deposit_refund_tx_ref is None


def test_deposit_status_is_terminal() -> None:
    assert DepositStatus.model_validate({"status": "filled"}).is_terminal is True
    assert DepositStatus.model_validate({"status": "refunded"}).is_terminal is True
    assert DepositStatus.model_validate({"status": "expired"}).is_terminal is True
    assert DepositStatus.model_validate({"status": "pending"}).is_terminal is False
