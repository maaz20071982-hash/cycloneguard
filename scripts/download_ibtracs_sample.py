"""
Fetches authentic North Indian Ocean tropical cyclone observations directly from
NOAA NCEI IBTrACS archive and saves them into data/samples/ibtracs_sample_ni.csv.
"""

import os
import urllib.request

def download_sample():
    url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.last3years.list.v04r01.csv"
    out_path = "data/samples/ibtracs_sample_ni.csv"
    
    print(f"Connecting to NOAA NCEI stream: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "CycloneGuard/1.0 (Research)"})
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        h0 = resp.readline().decode("utf-8")
        h1 = resp.readline().decode("utf-8")
        
        ni_rows = []
        storm_counts = {}
        target_storms = {"2023129N08091", "2023156N10067", "2023030N08087"}
        
        for line in resp:
            line_str = line.decode("utf-8", errors="ignore")
            parts = [p.strip() for p in line_str.split(",")]
            if len(parts) > 10 and parts[3] == "NI":
                sid = parts[0]
                ni_rows.append(line_str)
                storm_counts[sid] = storm_counts.get(sid, 0) + 1
                if len(ni_rows) >= 400 and len(storm_counts) >= 4:
                    break
                    
    print(f"Retrieved {len(ni_rows)} real North Indian Ocean best-track records across {len(storm_counts)} storms.")
    for sid, count in storm_counts.items():
        print(f"  Storm SID: {sid} -> {count} records")
        
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(h0)
        f.write(h1)
        for row in ni_rows:
            f.write(row)
            
    print(f"Saved verified sample to {out_path} ({os.path.getsize(out_path)} bytes).")

if __name__ == "__main__":
    download_sample()
