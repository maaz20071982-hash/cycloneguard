# CycloneGuard — INSAT-3D/3DR Data Integration Status

**Document Version:** 1.0.0  
**Last Updated:** Sprint 4 (Data Architecture & Ingestion)  
**Classification:** Operational Technical Status  

---

## 1. Overview & Source Definition

* **Satellite System:** INSAT-3D (launched 2013) & INSAT-3DR (launched 2016)
* **Agency / Provider:** Indian Space Research Organisation (ISRO)
* **Data Portal:** Meteorological & Oceanographic Satellite Data Archival Centre (MOSDAC)
* **Portal URL:** [https://www.mosdac.gov.in/](https://www.mosdac.gov.in/)
* **Primary Payload:** 6-channel Multi-Spectral Imager:
  * Visible (VIS): $0.55 - 0.75\,\mu\text{m}$ ($1\,\text{km}$ nadir resolution)
  * Shortwave Infrared (SWIR): $1.55 - 1.70\,\mu\text{m}$ ($1\,\text{km}$)
  * Middle Infrared (MIR): $3.80 - 4.00\,\mu\text{m}$ ($4\,\text{km}$)
  * Water Vapor (WV): $6.50 - 7.10\,\mu\text{m}$ ($8\,\text{km}$)
  * Thermal Infrared-1 (TIR-1): $10.30 - 11.30\,\mu\text{m}$ ($4\,\text{km}$) — *Primary cyclone eyewall temperature channel*
  * Thermal Infrared-2 (TIR-2): $11.50 - 12.50\,\mu\text{m}$ ($4\,\text{km}$)

---

## 2. Access Method & Authentication Investigation

Programmatic verification of the MOSDAC data infrastructure revealed the following operational constraints:

1. **Authentication Requirement:**
   * Unlike NOAA open archives (e.g., IBTrACS), ISRO MOSDAC does not permit anonymous HTTP or FTP downloads.
   * Every automated request requires an authenticated MOSDAC user profile, active session cookies, and API client registration.
2. **API Access Architecture:**
   * Automated access requires the official MOSDAC Python API client configured via a local `config.json` containing verified account credentials and secret tokens.
3. **Data Latency & Permission Tiers:**
   * **General Registered Users:** Experience a standard 3-day data hold for Level-1 (L1B/L1C) calibrated radiances.
   * **Near-Real-Time (NRT) Users:** Requires explicit institutional affiliation approval from ISRO for sub-hour automated operational feeds.
4. **File Formats:**
   * MOSDAC distributes L1B/L1C data in hierarchical HDF5 format (`.h5`), containing geographic look-up tables (GLT) and calibrated radiance tables requiring conversion to brightness temperature using sensor Planck coefficients.

---

## 3. Verified Availability

| Parameter | Specification | Verified Status |
| :--- | :--- | :--- |
| **Temporal Coverage** | 2013 – Present | Confirmed available in archive |
| **Cadence** | 30-min per satellite (15-min staggered) | Confirmed operational |
| **Spatial Coverage** | Indian Ocean Full Disk ($40^\circ\text{E} - 120^\circ\text{E}$, $45^\circ\text{S} - 45^\circ\text{N}$) | Confirmed covers all Bay of Bengal and Arabian Sea systems |
| **Anonymous Download** | Public REST / S3 | **NOT AVAILABLE** (Strictly gated) |
| **Automated Client** | `mosdac_download` script via `config.json` | Requires user-provided credentials |

---

## 4. Current Integration Status

* **Status:** `NOT YET INTEGRATED`
* **Adapter Implementation:** [`ml/data/adapters/insat.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/adapters/insat.py) is implemented with discovery metadata and staging interfaces.
* **Download Policy:** In strict compliance with the CycloneGuard scientific integrity rule (*"Do NOT pretend an API exists if it has not been verified; do NOT fake successful ingestion"*), the adapter reports `DownloadStatus.NOT_IMPLEMENTED` with clear guidance until institutional credentials are configured.

---

## 5. Next Actions for Production Deployment

1. **Credential Onboarding:**
   * Register a dedicated CycloneGuard institutional research account on MOSDAC.
   * Download the official MOSDAC API package and generate the authorized `config.json` token.
2. **HDF5 Decompression Worker:**
   * Implement the HDF5 radiance-to-brightness-temperature Planck converter for INSAT TIR-1 ($10.8\,\mu\text{m}$) and WV ($6.7\,\mu\text{m}$) channels.
3. **Staging Pipeline:**
   * Map INSAT-3D/3DR full-disk coordinates onto the standard CycloneGuard cyclone-centered crop schema.
