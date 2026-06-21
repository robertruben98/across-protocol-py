"""Shared test fixtures: captured real Across API response payloads."""

from __future__ import annotations

from typing import Any

import pytest

# Captured live from GET /suggested-fees (USDC Ethereum -> USDC.e Polygon, 10 USDC).
SUGGESTED_FEES_PAYLOAD: dict[str, Any] = {
    "estimatedFillTimeSec": 2,
    "capitalFeePct": "100000000000000",
    "capitalFeeTotal": "1000",
    "relayGasFeePct": "864900000000000",
    "relayGasFeeTotal": "8649",
    "relayFeePct": "964900000000000",
    "relayFeeTotal": "9649",
    "lpFeePct": "0",
    "timestamp": "1782074207",
    "isAmountTooLow": False,
    "quoteBlock": "25368400",
    "exclusiveRelayer": "0x0000000000000000000000000000000000000000",
    "exclusivityDeadline": 0,
    "spokePoolAddress": "0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5",
    "destinationSpokePoolAddress": "0x9295ee1d8C5b022Be115A2AD3c30C72E34e7F096",
    "totalRelayFee": {"pct": "964900000000000", "total": "9649"},
    "relayerCapitalFee": {"pct": "100000000000000", "total": "1000"},
    "relayerGasFee": {"pct": "864900000000000", "total": "8649"},
    "lpFee": {"pct": "0", "total": "0"},
    "internalizedSwapFee": {"pct": "0", "total": "0"},
    "limits": {
        "minDeposit": "500154",
        "maxDeposit": "1389862444460",
        "maxDepositInstant": "281785201840",
        "maxDepositShortDelay": "1389862444460",
        "recommendedDepositInstant": "281785201840",
    },
    "fillDeadline": "1782081407",
    "outputAmount": "9990351",
    "inputToken": {
        "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "symbol": "USDC",
        "decimals": 6,
        "chainId": 1,
    },
    "outputToken": {
        "address": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "symbol": "USDC.e",
        "decimals": 6,
        "chainId": 137,
    },
    "id": "n947p-1782074293622-7debc684ca34",
}

# Captured live from GET /available-routes (first element).
AVAILABLE_ROUTES_PAYLOAD: list[dict[str, Any]] = [
    {
        "originChainId": 1,
        "originToken": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "destinationChainId": 4326,
        "destinationToken": "0x4200000000000000000000000000000000000006",
        "originTokenSymbol": "WETH",
        "destinationTokenSymbol": "WETH",
        "isNative": False,
    },
    {
        "originChainId": 1,
        "originToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "destinationChainId": 137,
        "destinationToken": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "originTokenSymbol": "USDC",
        "destinationTokenSymbol": "USDC.e",
        "isNative": False,
    },
]

# Captured live from GET /limits.
LIMITS_PAYLOAD: dict[str, Any] = {
    "minDeposit": "500154",
    "maxDeposit": "1389862444460",
    "maxDepositInstant": "281785201840",
    "maxDepositShortDelay": "1389862444460",
    "recommendedDepositInstant": "281785201840",
    "relayerFeeDetails": {
        "relayFeeTotal": "7895",
        "relayFeePercent": "78950100000000000000",
        "gasFeeTotal": "7895",
        "gasFeePercent": "78950000000000000000",
        "capitalFeeTotal": "0",
        "capitalFeePercent": "100000000000000",
    },
    "gasFeeDetails": {
        "nativeGasCost": "151109",
        "gasPrice": "644046646600",
        "tokenGasCost": "97321244721079400",
    },
    "reserves": {
        "liquidReserves": "948756529073",
        "utilizedReserves": "482550981740",
    },
}

# Captured live from GET /deposit/status (origin 1, depositId 2000000, filled).
DEPOSIT_STATUS_PAYLOAD: dict[str, Any] = {
    "status": "filled",
    "originChainId": 1,
    "depositId": "2000000",
    "depositTxHash": "0x77b8dc8877c4015e06b682e9d7515d7d6432c3b0e617084fd6acb9532906ec61",
    "depositTxnRef": "0x77b8dc8877c4015e06b682e9d7515d7d6432c3b0e617084fd6acb9532906ec61",
    "fillTx": "0xe2d2361de170a8c437a6b2a91ca280365327038186aebc39264ad840e15f6bd0",
    "fillTxnRef": "0xe2d2361de170a8c437a6b2a91ca280365327038186aebc39264ad840e15f6bd0",
    "destinationChainId": 8453,
    "depositRefundTxHash": None,
    "depositRefundTxnRef": None,
    "actionsSucceeded": None,
    "actionsTargetChainId": None,
    "pagination": {"currentIndex": 0, "maxIndex": 0},
}


@pytest.fixture
def suggested_fees_payload() -> dict[str, Any]:
    return dict(SUGGESTED_FEES_PAYLOAD)


@pytest.fixture
def available_routes_payload() -> list[dict[str, Any]]:
    return [dict(r) for r in AVAILABLE_ROUTES_PAYLOAD]


@pytest.fixture
def limits_payload() -> dict[str, Any]:
    return dict(LIMITS_PAYLOAD)


@pytest.fixture
def deposit_status_payload() -> dict[str, Any]:
    return dict(DEPOSIT_STATUS_PAYLOAD)
