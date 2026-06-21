"""Live integration test against the real, keyless Across API.

Marked ``integration`` and deselected by default (see pyproject addopts).
Run explicitly with: ``pytest -m integration``.
"""

from __future__ import annotations

import pytest

from across_protocol import AcrossClient, SuggestedFees

# USDC on Ethereum -> USDC.e on Polygon, a long-standing supported route.
USDC_ETHEREUM = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDC_E_POLYGON = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"


@pytest.mark.integration
def test_suggested_fees_live() -> None:
    with AcrossClient() as client:
        fees = client.get_suggested_fees(
            input_token=USDC_ETHEREUM,
            output_token=USDC_E_POLYGON,
            origin_chain_id=1,
            destination_chain_id=137,
            amount=10_000_000,
        )

    assert isinstance(fees, SuggestedFees)
    assert fees.input_token.symbol == "USDC"
    assert int(fees.output_amount) > 0
    assert int(fees.limits.min_deposit) > 0
    assert fees.estimated_fill_time_sec >= 0
