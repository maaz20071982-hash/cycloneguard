import urllib.request
import sys

def inspect():
    url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.last3years.list.v04r01.csv"
    req = urllib.request.Request(url, headers={"User-Agent": "CycloneGuard/1.0"})
    print(f"Fetching {url}...")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            h0 = resp.readline().decode("utf-8")
            h1 = resp.readline().decode("utf-8")
            print("Header 0 (columns, count=" + str(len(h0.split(","))) + "):")
            cols = [c.strip() for c in h0.split(",")]
            units = [u.strip() for u in h1.split(",")]
            for idx in range(min(25, len(cols))):
                print(f"  [{idx:02d}] {cols[idx]} (units: '{units[idx]}')")
            
            # Find a few North Indian Ocean storms
            ni_records = []
            storms = {}
            for line in resp:
                line_str = line.decode("utf-8", errors="ignore")
                parts = [p.strip() for p in line_str.split(",")]
                if len(parts) > 10 and parts[3] == "NI":
                    sid = parts[0]
                    name = parts[5]
                    if sid not in storms:
                        storms[sid] = {"name": name, "count": 0, "first_time": parts[6], "records": []}
                    storms[sid]["count"] += 1
                    storms[sid]["last_time"] = parts[6]
                    if len(storms[sid]["records"]) < 5:
                        storms[sid]["records"].append({
                            "time": parts[6],
                            "lat": parts[8],
                            "lon": parts[9],
                            "wind": parts[10],
                            "pres": parts[11],
                        })
                    ni_records.append(line_str)
                    if len(storms) >= 3 and all(s["count"] >= 10 for s in storms.values()):
                        break
            
            print(f"\nDiscovered {len(storms)} North Indian Ocean storms in last3years dataset:")
            for sid, info in storms.items():
                print(f"  SID: {sid} | Name: {info['name']} | Obs count: {info['count']} | Period: {info['first_time']} to {info['last_time']}")
                for r in info["records"][:2]:
                    print(f"    -> {r['time']}: Lat {r['lat']}, Lon {r['lon']}, Wind {r['wind']} kts, Pres {r['pres']} mb")
                    
    except Exception as e:
        print("Error during inspection:", e)

if __name__ == "__main__":
    inspect()
