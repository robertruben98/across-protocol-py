"""Tests for the exception hierarchy."""

from __future__ import annotations

import pytest

from across_protocol import (
    AcrossAPIError,
    AcrossError,
)


def test_api_error_is_across_error() -> None:
    assert issubclass(AcrossAPIError, AcrossError)


def test_api_error_carries_status_and_body() -> None:
    err = AcrossAPIError("boom", status_code=404, response_body={"error": "NotFound"})
    assert err.status_code == 404
    assert err.response_body == {"error": "NotFound"}
    assert "404" in str(err)
    assert "boom" in str(err)


def test_across_error_is_exception() -> None:
    with pytest.raises(AcrossError):
        raise AcrossError("generic failure")
