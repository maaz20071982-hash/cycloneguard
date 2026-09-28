"""
Unit tests for storm-wise dataset splitting and zero data leakage.
"""

import pytest

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries
from ml.data.splitting.storm_split import StormWiseSplitter


def _create_dummy_storms(count=10):
    storms = {}
    for i in range(count):
        sid = f"2023_{i:02d}"
        points = [
            CycloneTrackPoint(
                storm_id=sid,
                storm_name=f"STORM_{i}",
                season=2020 + (i % 4),
                basin="NI",
                timestamp_utc=f"2023-05-{10 + j:02d}T00:00:00Z",
                latitude=10.0 + j,
                longitude=80.0 + j,
                wind_speed_kts=40.0 + j * 5,
            )
            for j in range(5)
        ]
        storms[sid] = CycloneTrackSeries(
            storm_id=sid,
            storm_name=f"STORM_{i}",
            season=2020 + (i % 4),
            basin="NI",
            points=points,
        )
    return storms


def test_storm_wise_ratio_split_disjointness():
    storms = _create_dummy_storms(10)
    train, val, test, summary = StormWiseSplitter.split_by_ratio(
        storms, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=123
    )

    train_set = set(summary.train_storms)
    val_set = set(summary.val_storms)
    test_set = set(summary.test_storms)

    # 1. Total storms preserved
    assert len(train_set) + len(val_set) + len(test_set) == 10

    # 2. Strict disjointness (zero data leakage)
    assert len(train_set & val_set) == 0
    assert len(train_set & test_set) == 0
    assert len(val_set & test_set) == 0


def test_storm_wise_chronological_split():
    storms = _create_dummy_storms(10)  # Seasons 2020, 2021, 2022, 2023
    train, val, test, summary = StormWiseSplitter.split_by_chronological_seasons(
        storms, val_season_start=2022, test_season_start=2023
    )

    for sid, s in train.items():
        assert s.season < 2022

    for sid, s in val.items():
        assert 2022 <= s.season < 2023

    for sid, s in test.items():
        assert s.season >= 2023

    # Disjointness check
    assert len(set(train.keys()) & set(test.keys())) == 0
    assert len(set(train.keys()) & set(val.keys())) == 0
    assert len(set(val.keys()) & set(test.keys())) == 0
