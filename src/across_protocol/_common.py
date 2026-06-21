"""Internal helpers shared by the sync and async clients.

These functions hold the request/response logic that does not depend on whether
the underlying HTTP call is blocking or awaitable, so both client variants stay
in lockstep.
"""

from __future__ import annotations

from typing import Any, Optional, Union

import httpx

from across_protocol.exceptions import AcrossAPIError

DEFAULT_BASE_URL = "https://app.across.to/api"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "across-protocol-py"

# Default polling cadence for deposit status; the indexer updates roughly every
# 10 seconds, so polling faster yields little benefit.
DEFAULT_POLL_INTERVAL = 5.0


def normalize_base_url(base_url: str) -> str:
    """Strip a trailing slash so endpoint paths join cleanly."""
    return base_url.rstrip("/")


def _drop_none(params: dict[str, Any]) -> dict[str, Any]:
    """Remove keys whose value is ``None`` so they are omitted from the query."""
    return {k: v for k, v in params.items() if v is not None}


def build_suggested_fees_params(
    *,
    input_token: str,
    output_token: str,
    origin_chain_id: int,
    destination_chain_id: int,
    amount: Union[int, str],
    recipient: Optional[str] = None,
) -> dict[str, Any]:
    """Build the query parameters for ``GET /suggested-fees``."""
    return _drop_none(
        {
            "inputToken": input_token,
            "outputToken": output_token,
            "originChainId": origin_chain_id,
            "destinationChainId": destination_chain_id,
            "amount": str(amount),
            "recipient": recipient,
        }
    )


def build_available_routes_params(
    *,
    origin_chain_id: Optional[int] = None,
    destination_chain_id: Optional[int] = None,
    origin_token: Optional[str] = None,
    destination_token: Optional[str] = None,
) -> dict[str, Any]:
    """Build the query parameters for ``GET /available-routes``."""
    return _drop_none(
        {
            "originChainId": origin_chain_id,
            "destinationChainId": destination_chain_id,
            "originToken": origin_token,
            "destinationToken": destination_token,
        }
    )


def build_limits_params(
    *,
    input_token: str,
    output_token: str,
    origin_chain_id: int,
    destination_chain_id: int,
) -> dict[str, Any]:
    """Build the query parameters for ``GET /limits``."""
    return _drop_none(
        {
            "inputToken": input_token,
            "outputToken": output_token,
            "originChainId": origin_chain_id,
            "destinationChainId": destination_chain_id,
        }
    )


def build_deposit_status_params(
    *,
    origin_chain_id: Optional[int],
    deposit_id: Optional[Union[int, str]],
    deposit_tx_ref: Optional[str],
) -> dict[str, Any]:
    """Build and validate query parameters for ``GET /deposit/status``.

    Callers must supply either ``deposit_tx_ref`` or both ``origin_chain_id``
    and ``deposit_id``.

    Raises:
        ValueError: If neither valid identifier combination is provided.
    """
    if deposit_tx_ref is not None:
        return {"depositTxnRef": deposit_tx_ref}
    if origin_chain_id is not None and deposit_id is not None:
        return {"originChainId": origin_chain_id, "depositId": str(deposit_id)}
    raise ValueError("Provide either deposit_tx_ref, or both origin_chain_id and deposit_id.")


def raise_for_status(response: httpx.Response) -> None:
    """Convert a non-success HTTP response into an :class:`AcrossAPIError`."""
    if response.is_success:
        return
    try:
        body: Any = response.json()
    except ValueError:
        body = response.text
    message = "Across API request failed"
    if isinstance(body, dict):
        message = body.get("message") or body.get("error") or message
    raise AcrossAPIError(message, status_code=response.status_code, response_body=body)
