"""
Unit tests for Rapid Intensification (RI) label generation.
"""

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries
from ml.data.sequences.ri_label import RILabelGenerator


def test_ri_label_detection():
    # 4 points: 00Z (35 kts), 12Z (50 kts), 24Z (70 kts), 36Z (85 kts)
    # 00Z to 24Z: +35 kts in 24h -> RI True
    series = CycloneTrackSeries(
        storm_id="RI_TEST",
        storm_name="RAPID_STORM",
        season=2023,
        basin="NI",
        points=[
            CycloneTrackPoint(
                storm_id="RI_TEST",
                storm_name="RAPID_STORM",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-10T00:00:00Z",
                latitude=10.0,
                longitude=85.0,
                wind_speed_kts=35.0,
            ),
            CycloneTrackPoint(
                storm_id="RI_TEST",
                storm_name="RAPID_STORM",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-10T12:00:00Z",
                latitude=11.0,
                longitude=85.5,
                wind_speed_kts=50.0,
            ),
            CycloneTrackPoint(
                storm_id="RI_TEST",
                storm_name="RAPID_STORM",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-11T00:00:00Z",
                latitude=12.0,
                longitude=86.0,
                wind_speed_kts=70.0,
            ),
        ],
    )

    # Test t0 = 00Z
    res = RILabelGenerator.generate_label(series.points[0], series, horizon_hours=24.0, threshold_kts=30.0)
    assert res.status == "AVAILABLE"
    assert res.is_ri is True
    assert res.delta_wind_kts == 35.0
    assert "Rapid Intensification detected" in res.justification


def test_non_ri_label():
    series = CycloneTrackSeries(
        storm_id="SLOW_TEST",
        storm_name="SLOW_STORM",
        season=2023,
        basin="NI",
        points=[
            CycloneTrackPoint(
                storm_id="SLOW_TEST",
                storm_name="SLOW_STORM",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-10T00:00:00Z",
                latitude=10.0,
                longitude=85.0,
                wind_speed_kts=35.0,
            ),
            CycloneTrackPoint(
                storm_id="SLOW_TEST",
                storm_name="SLOW_STORM",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-11T00:00:00Z",
                latitude=12.0,
                longitude=86.0,
                wind_speed_kts=45.0,  # Only +10 kts in 24h
            ),
        ],
    )
    res = RILabelGenerator.generate_label(series.points[0], series, horizon_hours=24.0, threshold_kts=30.0)
    assert res.status == "AVAILABLE"
    assert res.is_ri is False
    assert res.delta_wind_kts == 10.0


def test_missing_future_observation_uninferrable():
    # If the cyclone dissipates or track ends before t + 24h, label MUST be marked unavailable
    series = CycloneTrackSeries(
        storm_id="SHORT_TEST",
        storm_name="SHORT_STORM",
        season=2023,
        basin="NI",
        points=[
            CycloneTrackPoint(
                storm_id="SHORT_TEST",
                storm_name="SHORT_STORM",
                season=2023,
                basin="NI",
                timestamp_utc="2023-05-10T00:00:00Z",
                latitude=10.0,
                longitude=85.0,
                wind_speed_kts=35.0,
            ),
        ],
    )
    res = RILabelGenerator.generate_label(series.points[0], series, horizon_hours=24.0)
    assert res.status == "UNAVAILABLE_MISSING_FUTURE"
    assert res.is_ri is None
    assert res.future_wind_kts is None
