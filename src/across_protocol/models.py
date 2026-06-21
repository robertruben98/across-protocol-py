"""Pydantic models for Across Protocol API requests and responses.

Numeric on-chain values (amounts, fees, percentages) are returned by the API as
decimal strings to preserve full ``uint256`` precision, and are kept as ``str``
here for the same reason. Convert them to ``int`` at the call site when needed.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# Deposit lifecycle states that will not transition further.
TERMINAL_DEPOSIT_STATUSES = frozenset({"filled", "refunded", "expired"})


class _ApiModel(BaseModel):
    """Base model that accepts (and ignores) unknown fields from the API.

    The Across API is evolving; tolerating extra keys keeps the client from
    breaking when the upstream response gains new fields.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class FeeBreakdown(_ApiModel):
    """A single fee component, expressed as a percentage and an absolute total."""

    pct: str = Field(description="Fee as a fraction of the input, scaled by 1e18 (decimal string).")
    total: str = Field(description="Absolute fee amount in the input token's smallest unit.")


class TransferLimits(_ApiModel):
    """Per-route deposit size limits, all in the input token's smallest unit."""

    min_deposit: str = Field(alias="minDeposit", description="Minimum depositable amount.")
    max_deposit: str = Field(alias="maxDeposit", description="Maximum depositable amount.")
    max_deposit_instant: str = Field(
        alias="maxDepositInstant",
        description="Maximum amount eligible for an instant (fast) fill.",
    )
    max_deposit_short_delay: str = Field(
        alias="maxDepositShortDelay",
        description="Maximum amount eligible for a short-delay fill.",
    )
    recommended_deposit_instant: str = Field(
        alias="recommendedDepositInstant",
        description="Recommended maximum for a reliably instant fill.",
    )


class TokenInfo(_ApiModel):
    """Metadata describing a token on a specific chain."""

    address: str = Field(description="Token contract address.")
    symbol: str = Field(description="Token symbol, e.g. ``USDC``.")
    decimals: int = Field(description="Number of decimals the token uses.")
    chain_id: int = Field(alias="chainId", description="Chain ID the token lives on.")


class SuggestedFees(_ApiModel):
    """A bridge quote returned by ``GET /suggested-fees``.

    This is the headline quote: it contains the fees a relayer will charge, the
    resulting output amount, transfer limits, and the contract addresses needed
    to submit the deposit on-chain.
    """

    estimated_fill_time_sec: int = Field(
        alias="estimatedFillTimeSec",
        description="Estimated seconds until the deposit is filled on the destination chain.",
    )
    total_relay_fee: FeeBreakdown = Field(
        alias="totalRelayFee", description="Total relayer fee (capital + gas)."
    )
    relayer_capital_fee: FeeBreakdown = Field(
        alias="relayerCapitalFee", description="Relayer's capital fee component."
    )
    relayer_gas_fee: FeeBreakdown = Field(
        alias="relayerGasFee", description="Relayer's gas fee component."
    )
    lp_fee: FeeBreakdown = Field(alias="lpFee", description="Liquidity provider fee.")
    capital_fee_pct: str = Field(
        alias="capitalFeePct", description="Capital fee percentage (scaled by 1e18)."
    )
    capital_fee_total: str = Field(alias="capitalFeeTotal", description="Capital fee total.")
    relay_gas_fee_pct: str = Field(
        alias="relayGasFeePct", description="Relay gas fee percentage (scaled by 1e18)."
    )
    relay_gas_fee_total: str = Field(alias="relayGasFeeTotal", description="Relay gas fee total.")
    relay_fee_pct: str = Field(
        alias="relayFeePct", description="Total relay fee percentage (scaled by 1e18)."
    )
    relay_fee_total: str = Field(alias="relayFeeTotal", description="Total relay fee amount.")
    lp_fee_pct: str = Field(alias="lpFeePct", description="LP fee percentage (scaled by 1e18).")
    output_amount: str = Field(
        alias="outputAmount", description="Amount the recipient receives, after fees."
    )
    is_amount_too_low: bool = Field(
        alias="isAmountTooLow", description="True if the requested amount is below the minimum."
    )
    timestamp: str = Field(description="Quote timestamp (Unix seconds, as a string).")
    quote_block: str = Field(alias="quoteBlock", description="Origin-chain block the quote uses.")
    fill_deadline: str = Field(
        alias="fillDeadline", description="Unix timestamp after which the fill is no longer valid."
    )
    spoke_pool_address: str = Field(
        alias="spokePoolAddress", description="Origin-chain SpokePool contract address."
    )
    destination_spoke_pool_address: str = Field(
        alias="destinationSpokePoolAddress",
        description="Destination-chain SpokePool contract address.",
    )
    exclusive_relayer: str = Field(
        alias="exclusiveRelayer",
        description="Relayer with exclusive fill rights, or the zero address if none.",
    )
    exclusivity_deadline: int = Field(
        alias="exclusivityDeadline",
        description="Unix timestamp until which the exclusive relayer has priority (0 if none).",
    )
    limits: TransferLimits = Field(description="Deposit size limits for this route.")
    input_token: TokenInfo = Field(alias="inputToken", description="Resolved input token info.")
    output_token: TokenInfo = Field(alias="outputToken", description="Resolved output token info.")


class AvailableRoute(_ApiModel):
    """A supported bridging route returned by ``GET /available-routes``."""

    origin_chain_id: int = Field(alias="originChainId", description="Origin chain ID.")
    origin_token: str = Field(alias="originToken", description="Origin token contract address.")
    destination_chain_id: int = Field(
        alias="destinationChainId", description="Destination chain ID."
    )
    destination_token: str = Field(
        alias="destinationToken", description="Destination token contract address."
    )
    origin_token_symbol: str = Field(alias="originTokenSymbol", description="Origin token symbol.")
    destination_token_symbol: str = Field(
        alias="destinationTokenSymbol", description="Destination token symbol."
    )
    is_native: bool = Field(
        alias="isNative", description="Whether the origin token is the chain's native asset."
    )


class RelayerFeeDetails(_ApiModel):
    """Relayer fee breakdown nested inside a ``/limits`` response."""

    relay_fee_total: str = Field(alias="relayFeeTotal", description="Total relay fee amount.")
    relay_fee_percent: str = Field(
        alias="relayFeePercent", description="Total relay fee percentage (scaled by 1e18)."
    )
    gas_fee_total: str = Field(alias="gasFeeTotal", description="Gas fee amount.")
    gas_fee_percent: str = Field(
        alias="gasFeePercent", description="Gas fee percentage (scaled by 1e18)."
    )
    capital_fee_total: str = Field(alias="capitalFeeTotal", description="Capital fee amount.")
    capital_fee_percent: str = Field(
        alias="capitalFeePercent", description="Capital fee percentage (scaled by 1e18)."
    )


class GasFeeDetails(_ApiModel):
    """Gas cost breakdown nested inside a ``/limits`` response."""

    native_gas_cost: str = Field(
        alias="nativeGasCost", description="Estimated gas units for the fill."
    )
    gas_price: str = Field(alias="gasPrice", description="Gas price used for the estimate (wei).")
    token_gas_cost: str = Field(
        alias="tokenGasCost", description="Gas cost denominated in the input token."
    )


class Reserves(_ApiModel):
    """Liquidity reserve figures nested inside a ``/limits`` response."""

    liquid_reserves: str = Field(
        alias="liquidReserves", description="Currently available liquidity."
    )
    utilized_reserves: str = Field(
        alias="utilizedReserves", description="Liquidity currently in use."
    )


class Limits(_ApiModel):
    """Transfer limits for a route returned by ``GET /limits``."""

    min_deposit: str = Field(alias="minDeposit", description="Minimum depositable amount.")
    max_deposit: str = Field(alias="maxDeposit", description="Maximum depositable amount.")
    max_deposit_instant: str = Field(
        alias="maxDepositInstant", description="Maximum amount eligible for an instant fill."
    )
    max_deposit_short_delay: str = Field(
        alias="maxDepositShortDelay", description="Maximum amount eligible for a short-delay fill."
    )
    recommended_deposit_instant: str = Field(
        alias="recommendedDepositInstant",
        description="Recommended maximum for a reliably instant fill.",
    )
    relayer_fee_details: RelayerFeeDetails = Field(
        alias="relayerFeeDetails", description="Relayer fee breakdown."
    )
    gas_fee_details: GasFeeDetails = Field(alias="gasFeeDetails", description="Gas cost breakdown.")
    reserves: Reserves = Field(description="Liquidity reserve figures.")


class DepositStatusPagination(_ApiModel):
    """Index of this fill within a multi-fill deposit."""

    current_index: int = Field(alias="currentIndex", description="Index of the current fill.")
    max_index: int = Field(alias="maxIndex", description="Highest fill index for this deposit.")


class DepositStatus(_ApiModel):
    """Lifecycle state of a deposit returned by ``GET /deposit/status``.

    The ``status`` field is one of ``pending``, ``filled``, ``expired``, or
    ``refunded``. Use :attr:`is_terminal` to check whether it will change again.
    """

    status: str = Field(description="Lifecycle state: pending, filled, expired, or refunded.")
    origin_chain_id: Optional[int] = Field(
        default=None, alias="originChainId", description="Origin chain ID."
    )
    destination_chain_id: Optional[int] = Field(
        default=None, alias="destinationChainId", description="Destination chain ID."
    )
    deposit_id: Optional[str] = Field(
        default=None, alias="depositId", description="On-chain deposit ID."
    )
    deposit_tx_ref: Optional[str] = Field(
        default=None, alias="depositTxnRef", description="Origin-chain deposit transaction hash."
    )
    fill_tx_ref: Optional[str] = Field(
        default=None,
        alias="fillTxnRef",
        description="Destination-chain fill transaction hash (present when filled).",
    )
    deposit_refund_tx_ref: Optional[str] = Field(
        default=None,
        alias="depositRefundTxnRef",
        description="Origin-chain refund transaction hash (present when refunded).",
    )
    actions_succeeded: Optional[bool] = Field(
        default=None,
        alias="actionsSucceeded",
        description="Whether embedded cross-chain actions succeeded, if any.",
    )
    actions_target_chain_id: Optional[int] = Field(
        default=None,
        alias="actionsTargetChainId",
        description="Target chain ID for embedded actions, if any.",
    )
    pagination: Optional[DepositStatusPagination] = Field(
        default=None, description="Fill index information for multi-fill deposits."
    )

    @property
    def is_terminal(self) -> bool:
        """Whether the deposit has reached a final state (filled/refunded/expired)."""
        return self.status in TERMINAL_DEPOSIT_STATUSES
