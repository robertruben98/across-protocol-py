"""Asynchronous client for the Across Protocol bridge API."""

from __future__ import annotations

import asyncio
import time
from types import TracebackType
from typing import Any, Optional, Union

import httpx

from across_protocol._common import (
    DEFAULT_BASE_URL,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_TIMEOUT,
    USER_AGENT,
    build_available_routes_params,
    build_deposit_status_params,
    build_limits_params,
    build_suggested_fees_params,
    normalize_base_url,
    raise_for_status,
)
from across_protocol.models import (
    AvailableRoute,
    DepositStatus,
    Limits,
    SuggestedFees,
)


class AsyncAcrossClient:
    """An asynchronous client for the Across Protocol bridge API.

    This mirrors :class:`across_protocol.AcrossClient`; every request method is
    a coroutine. The default base URL targets the public production API, which
    requires no API key for the quoting endpoints exposed here.

    Args:
        base_url: Base URL of the Across API. Defaults to the production host.
        timeout: Per-request timeout in seconds.
        client: An optional pre-configured :class:`httpx.AsyncClient`. When
            supplied, the caller owns its lifecycle and :meth:`aclose` will not
            close it.

    Example:
        >>> import asyncio
        >>> async def quote() -> str:
        ...     async with AsyncAcrossClient() as client:
        ...         fees = await client.get_suggested_fees(
        ...             input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        ...             output_token="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        ...             origin_chain_id=1,
        ...             destination_chain_id=137,
        ...             amount=10_000_000,
        ...         )
        ...         return fees.output_amount
        >>> asyncio.run(quote())  # doctest: +SKIP
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.base_url = normalize_base_url(base_url)
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=timeout, headers={"User-Agent": USER_AGENT}
        )

    async def __aenter__(self) -> AsyncAcrossClient:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP client, unless it was supplied by the caller."""
        if self._owns_client:
            await self._client.aclose()

    async def _get(self, path: str, params: dict[str, Any]) -> Any:
        response = await self._client.get(f"{self.base_url}{path}", params=params)
        raise_for_status(response)
        return response.json()

    async def get_suggested_fees(
        self,
        *,
        input_token: str,
        output_token: str,
        origin_chain_id: int,
        destination_chain_id: int,
        amount: Union[int, str],
        recipient: Optional[str] = None,
    ) -> SuggestedFees:
        """Get a bridge quote (fees, output amount, limits) for a transfer.

        Args:
            input_token: Input token address on the origin chain.
            output_token: Output token address on the destination chain.
            origin_chain_id: Chain ID the deposit originates from.
            destination_chain_id: Chain ID the funds are bridged to.
            amount: Input amount in the token's smallest unit (int or decimal string).
            recipient: Optional recipient address used for a more precise gas estimate.

        Returns:
            The suggested fees and resulting output amount for the transfer.

        Raises:
            AcrossAPIError: If the API returns a non-success response.

        Example:
            >>> async with AsyncAcrossClient() as client:  # doctest: +SKIP
            ...     quote = await client.get_suggested_fees(
            ...         input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            ...         output_token="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            ...         origin_chain_id=1,
            ...         destination_chain_id=137,
            ...         amount=10_000_000,
            ...     )
        """
        params = build_suggested_fees_params(
            input_token=input_token,
            output_token=output_token,
            origin_chain_id=origin_chain_id,
            destination_chain_id=destination_chain_id,
            amount=amount,
            recipient=recipient,
        )
        return SuggestedFees.model_validate(await self._get("/suggested-fees", params))

    async def get_available_routes(
        self,
        *,
        origin_chain_id: Optional[int] = None,
        destination_chain_id: Optional[int] = None,
        origin_token: Optional[str] = None,
        destination_token: Optional[str] = None,
    ) -> list[AvailableRoute]:
        """List supported token routes, optionally filtered.

        Args:
            origin_chain_id: Restrict results to this origin chain.
            destination_chain_id: Restrict results to this destination chain.
            origin_token: Restrict results to this origin token address.
            destination_token: Restrict results to this destination token address.

        Returns:
            The supported routes matching the given filters.

        Raises:
            AcrossAPIError: If the API returns a non-success response.
        """
        params = build_available_routes_params(
            origin_chain_id=origin_chain_id,
            destination_chain_id=destination_chain_id,
            origin_token=origin_token,
            destination_token=destination_token,
        )
        data = await self._get("/available-routes", params)
        return [AvailableRoute.model_validate(item) for item in data]

    async def get_limits(
        self,
        *,
        input_token: str,
        output_token: str,
        origin_chain_id: int,
        destination_chain_id: int,
    ) -> Limits:
        """Get transfer limits and fee details for a route.

        Args:
            input_token: Input token address on the origin chain.
            output_token: Output token address on the destination chain.
            origin_chain_id: Chain ID the deposit originates from.
            destination_chain_id: Chain ID the funds are bridged to.

        Returns:
            The minimum/maximum deposit amounts and fee details for the route.

        Raises:
            AcrossAPIError: If the API returns a non-success response.
        """
        params = build_limits_params(
            input_token=input_token,
            output_token=output_token,
            origin_chain_id=origin_chain_id,
            destination_chain_id=destination_chain_id,
        )
        return Limits.model_validate(await self._get("/limits", params))

    async def get_deposit_status(
        self,
        *,
        origin_chain_id: Optional[int] = None,
        deposit_id: Optional[Union[int, str]] = None,
        deposit_tx_ref: Optional[str] = None,
    ) -> DepositStatus:
        """Get the lifecycle status of a deposit.

        Identify the deposit either by ``deposit_tx_ref`` (the origin-chain
        deposit transaction hash) or by both ``origin_chain_id`` and ``deposit_id``.

        Args:
            origin_chain_id: Chain ID the deposit originated on.
            deposit_id: On-chain deposit ID.
            deposit_tx_ref: Origin-chain deposit transaction hash.

        Returns:
            The current status of the deposit.

        Raises:
            ValueError: If neither identifier combination is provided.
            AcrossAPIError: If the API returns a non-success response.
        """
        params = build_deposit_status_params(
            origin_chain_id=origin_chain_id,
            deposit_id=deposit_id,
            deposit_tx_ref=deposit_tx_ref,
        )
        return DepositStatus.model_validate(await self._get("/deposit/status", params))

    async def wait_for_deposit(
        self,
        *,
        origin_chain_id: Optional[int] = None,
        deposit_id: Optional[Union[int, str]] = None,
        deposit_tx_ref: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: Optional[float] = None,
    ) -> DepositStatus:
        """Poll a deposit's status until it reaches a terminal state.

        A deposit is terminal once its status is ``filled``, ``refunded``, or
        ``expired``.

        Args:
            origin_chain_id: Chain ID the deposit originated on.
            deposit_id: On-chain deposit ID.
            deposit_tx_ref: Origin-chain deposit transaction hash.
            poll_interval: Seconds to wait between status checks.
            timeout: Maximum seconds to wait before giving up. ``None`` waits
                indefinitely.

        Returns:
            The terminal deposit status.

        Raises:
            ValueError: If neither identifier combination is provided.
            TimeoutError: If the deposit does not reach a terminal state in time.
            AcrossAPIError: If the API returns a non-success response.
        """
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            status = await self.get_deposit_status(
                origin_chain_id=origin_chain_id,
                deposit_id=deposit_id,
                deposit_tx_ref=deposit_tx_ref,
            )
            if status.is_terminal:
                return status
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Deposit did not reach a terminal status within {timeout}s "
                    f"(last status: {status.status})."
                )
            await asyncio.sleep(poll_interval)
