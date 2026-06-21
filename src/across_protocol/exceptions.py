"""Exception types raised by the Across Protocol client."""

from __future__ import annotations

from typing import Any, Optional


class AcrossError(Exception):
    """Base class for all errors raised by this library."""


class AcrossAPIError(AcrossError):
    """Raised when the Across API returns a non-success HTTP response.

    Args:
        message: Human-readable description of the failure.
        status_code: The HTTP status code returned by the API, if available.
        response_body: The parsed JSON body (or raw text) of the error response.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response_body: Optional[Any] = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        detail = f"[HTTP {status_code}] {message}" if status_code is not None else message
        super().__init__(detail)
