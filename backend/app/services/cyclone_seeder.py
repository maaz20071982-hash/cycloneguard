"""
Database Seeder for Historical Benchmark Cyclones (Sprint 13).
Populates the 6 verified North Indian Ocean cyclones into the cyclones table.
Preserves strict historical fidelity — no synthetic storms or fake records.
"""

from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from app.models.cyclone import Cyclone

logger = logging.getLogger("cycloneguard.seeder")

HISTORICAL_STORMS = [
    {
        "id": "2015301N11065",
        "name": "CHAPALA",
        "basin": "North Indian Ocean",
        "international_id": "2015-04A",
        "status": "HISTORICAL_VERIFIED",
        "genesis_time": datetime(2015, 10, 27, 12, 0, tzinfo=timezone.utc),
        "dissipation_time": datetime(2015, 11, 4, 0, 0, tzinfo=timezone.utc),
        "notes": (
            "Extremely Severe Cyclonic Storm Chapala. Second-strongest cyclone on record in the Arabian Sea. "
            "Underwent rapid intensification from 30 kt to 65 kt (+35 kt / 24h) starting 2015-10-28 18:00 UTC, "
            "eventually peaking at 115 kt. Verified benchmark storm with 61 coincident HURSAT-B1 infrared observations."
        ),
    },
    {
        "id": "2014297N11062",
        "name": "NILOFAR",
        "basin": "North Indian Ocean",
        "international_id": "2014-04A",
        "status": "HISTORICAL_VERIFIED",
        "genesis_time": datetime(2014, 10, 23, 12, 0, tzinfo=timezone.utc),
        "dissipation_time": datetime(2014, 11, 1, 12, 0, tzinfo=timezone.utc),
        "notes": (
            "Very Severe Cyclonic Storm Nilofar. Underwent rapid intensification over the Arabian Sea, "
            "peaking at 110 kt before rapid weakening prior to Gujarat landfall. 73 verified observations, 11 RI+ events."
        ),
    },
    {
        "id": "2013281N12098",
        "name": "PHAILIN",
        "basin": "North Indian Ocean",
        "international_id": "2013-02B",
        "status": "HISTORICAL_VERIFIED",
        "genesis_time": datetime(2013, 10, 7, 12, 0, tzinfo=timezone.utc),
        "dissipation_time": datetime(2013, 10, 14, 6, 0, tzinfo=timezone.utc),
        "notes": (
            "Extremely Severe Cyclonic Storm Phailin. Prompted India's largest evacuation in 14 years. "
            "Rapidly intensified over the Bay of Bengal from 45 kt to 115 kt. 55 verified observations, 11 RI+ events."
        ),
    },
    {
        "id": "2014279N11096",
        "name": "HUDHUD",
        "basin": "North Indian Ocean",
        "international_id": "2014-03B",
        "status": "HISTORICAL_VERIFIED",
        "genesis_time": datetime(2014, 10, 6, 6, 0, tzinfo=timezone.utc),
        "dissipation_time": datetime(2014, 10, 14, 9, 0, tzinfo=timezone.utc),
        "notes": (
            "Very Severe Cyclonic Storm Hudhud. Made destructive landfall at Visakhapatnam, Andhra Pradesh. "
            "66 verified observations, 1 RI+ event."
        ),
    },
    {
        "id": "2015309N14067",
        "name": "MEGH",
        "basin": "North Indian Ocean",
        "international_id": "2015-05A",
        "status": "HISTORICAL_VERIFIED",
        "genesis_time": datetime(2015, 11, 4, 12, 0, tzinfo=timezone.utc),
        "dissipation_time": datetime(2015, 11, 10, 12, 0, tzinfo=timezone.utc),
        "notes": (
            "Extremely Severe Cyclonic Storm Megh. Formed directly after Chapala and struck Socotra Island. "
            "49 verified observations, 6 RI+ events."
        ),
    },
    {
        "id": "2013322N13090",
        "name": "HELEN",
        "basin": "North Indian Ocean",
        "international_id": "2013-04B",
        "status": "HISTORICAL_VERIFIED",
        "genesis_time": datetime(2013, 11, 18, 0, 0, tzinfo=timezone.utc),
        "dissipation_time": datetime(2013, 11, 23, 6, 0, tzinfo=timezone.utc),
        "notes": (
            "Severe Cyclonic Storm Helen. Moderate intensity cyclone over the Bay of Bengal peaking at 55 kt. "
            "Did not undergo rapid intensification (0 RI+ events). Canonical RI-negative historical benchmark (43 observations)."
        ),
    },
]


def seed_historical_cyclones(db: Session) -> int:
    """Seeds the 6 verified NIO historical cyclones if not already present."""
    count = 0
    for storm_data in HISTORICAL_STORMS:
        existing = db.query(Cyclone).filter(
            (Cyclone.id == storm_data["id"]) | (Cyclone.name == storm_data["name"])
        ).first()
        if not existing:
            cyclone = Cyclone(**storm_data)
            db.add(cyclone)
            count += 1
        else:
            # Update fields to ensure consistency
            existing.status = storm_data["status"]
            existing.notes = storm_data["notes"]
            existing.basin = storm_data["basin"]
            existing.genesis_time = storm_data["genesis_time"]
            existing.dissipation_time = storm_data["dissipation_time"]
            existing.international_id = storm_data["international_id"]

    db.commit()
    return count
