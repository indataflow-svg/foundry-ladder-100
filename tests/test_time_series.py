"""Tests for ladder.time_series."""

import pytest

from ladder.time_series import resample, rolling_mean


def test_resample_buckets() -> None:
    assert resample([(1, 1.0), (2, 3.0), (10, 5.0)], 10) == [(0, 2.0), (10, 5.0)]


def test_rolling_mean_prefix() -> None:
    assert rolling_mean([1.0, 2.0, 3.0, 4.0], 3) == [1.0, 1.5, 2.0, 3.0]


def test_bad_window_rejected() -> None:
    with pytest.raises(ValueError):
        rolling_mean([1.0], 0)
