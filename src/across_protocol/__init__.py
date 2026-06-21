"""Typed Python client for the Across Protocol bridge API."""

__version__ = "0.1.0"

from across_protocol.async_client import AsyncAcrossClient
from across_protocol.client import AcrossClient
from across_protocol.exceptions import AcrossAPIError, AcrossError
from across_protocol.models import (
    AvailableRoute,
    DepositStatus,
    DepositStatusPagination,
    FeeBreakdown,
    GasFeeDetails,
    Limits,
    RelayerFeeDetails,
    Reserves,
    SuggestedFees,
    TokenInfo,
    TransferLimits,
)

__all__ = [
    "__version__",
    "AcrossAPIError",
    "AcrossClient",
    "AcrossError",
    "AsyncAcrossClient",
    "AvailableRoute",
    "DepositStatus",
    "DepositStatusPagination",
    "FeeBreakdown",
    "GasFeeDetails",
    "Limits",
    "RelayerFeeDetails",
    "Reserves",
    "SuggestedFees",
    "TokenInfo",
    "TransferLimits",
]
