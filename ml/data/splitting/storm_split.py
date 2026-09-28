"""
Storm-Wise Dataset Splitting Engine for CycloneGuard.
Ensures zero data leakage across training, validation, and testing partitions.
MANDATORY SCIENTIFIC RULE:
Observations from the same tropical cyclone (storm_id) MUST NEVER appear in multiple splits.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import random
from pydantic import BaseModel, Field

from ml.data.schemas.track import CycloneTrackPoint, CycloneTrackSeries


class SplitSummary(BaseModel):
    train_storms: List[str]
    val_storms: List[str]
    test_storms: List[str]
    train_points_count: int
    val_points_count: int
    test_points_count: int
    total_storms: int
    total_points: int
    strategy: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StormWiseSplitter:
    """Partitions tropical cyclone data by storm identity."""

    @staticmethod
    def split_by_ratio(
        storms_dict: Dict[str, CycloneTrackSeries],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42,
    ) -> Tuple[Dict[str, CycloneTrackSeries], Dict[str, CycloneTrackSeries], Dict[str, CycloneTrackSeries], SplitSummary]:
        """
        Partitions storms randomly but deterministically by storm_id.
        Ratios must sum to 1.0.
        """
        assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Ratios must sum to 1.0"
        storm_ids = sorted(list(storms_dict.keys()))

        rng = random.Random(seed)
        shuffled_ids = list(storm_ids)
        rng.shuffle(shuffled_ids)

        n_total = len(shuffled_ids)
        n_train = max(1, int(round(n_total * train_ratio)))
        n_val = max(1, int(round(n_total * val_ratio))) if n_total >= 3 else 0
        n_test = n_total - n_train - n_val
        if n_test < 1 and n_total >= 3:
            n_train -= 1
            n_test = 1

        train_ids = set(shuffled_ids[:n_train])
        val_ids = set(shuffled_ids[n_train : n_train + n_val])
        test_ids = set(shuffled_ids[n_train + n_val :])

        # Strict disjointness verification
        assert len(train_ids & val_ids) == 0, "Data leakage detected: train and val share storms!"
        assert len(train_ids & test_ids) == 0, "Data leakage detected: train and test share storms!"
        assert len(val_ids & test_ids) == 0, "Data leakage detected: val and test share storms!"

        train_dict = {sid: storms_dict[sid] for sid in train_ids}
        val_dict = {sid: storms_dict[sid] for sid in val_ids}
        test_dict = {sid: storms_dict[sid] for sid in test_ids}

        train_pts = sum(len(s.points) for s in train_dict.values())
        val_pts = sum(len(s.points) for s in val_dict.values())
        test_pts = sum(len(s.points) for s in test_dict.values())

        summary = SplitSummary(
            train_storms=sorted(list(train_ids)),
            val_storms=sorted(list(val_ids)),
            test_storms=sorted(list(test_ids)),
            train_points_count=train_pts,
            val_points_count=val_pts,
            test_points_count=test_pts,
            total_storms=n_total,
            total_points=train_pts + val_pts + test_pts,
            strategy=f"ratio_random_seed_{seed}",
            metadata={"train_ratio": train_ratio, "val_ratio": val_ratio, "test_ratio": test_ratio},
        )

        return train_dict, val_dict, test_dict, summary

    @staticmethod
    def split_by_chronological_seasons(
        storms_dict: Dict[str, CycloneTrackSeries],
        val_season_start: int,
        test_season_start: int,
    ) -> Tuple[Dict[str, CycloneTrackSeries], Dict[str, CycloneTrackSeries], Dict[str, CycloneTrackSeries], SplitSummary]:
        """
        Partitions storms chronologically by season/year:
        - Train: season < val_season_start
        - Val: val_season_start <= season < test_season_start
        - Test: season >= test_season_start
        """
        train_ids: Set[str] = set()
        val_ids: Set[str] = set()
        test_ids: Set[str] = set()

        for sid, s in storms_dict.items():
            if s.season < val_season_start:
                train_ids.add(sid)
            elif s.season < test_season_start:
                val_ids.add(sid)
            else:
                test_ids.add(sid)

        # Assert disjointness
        assert len(train_ids & val_ids) == 0, "Data leakage detected: train and val share storms!"
        assert len(train_ids & test_ids) == 0, "Data leakage detected: train and test share storms!"
        assert len(val_ids & test_ids) == 0, "Data leakage detected: val and test share storms!"

        train_dict = {sid: storms_dict[sid] for sid in train_ids}
        val_dict = {sid: storms_dict[sid] for sid in val_ids}
        test_dict = {sid: storms_dict[sid] for sid in test_ids}

        train_pts = sum(len(s.points) for s in train_dict.values())
        val_pts = sum(len(s.points) for s in val_dict.values())
        test_pts = sum(len(s.points) for s in test_dict.values())

        summary = SplitSummary(
            train_storms=sorted(list(train_ids)),
            val_storms=sorted(list(val_ids)),
            test_storms=sorted(list(test_ids)),
            train_points_count=train_pts,
            val_points_count=val_pts,
            test_points_count=test_pts,
            total_storms=len(storms_dict),
            total_points=train_pts + val_pts + test_pts,
            strategy="chronological_seasons",
            metadata={"val_season_start": val_season_start, "test_season_start": test_season_start},
        )

        return train_dict, val_dict, test_dict, summary
