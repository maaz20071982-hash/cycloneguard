import datetime
import urllib.request

d0 = datetime.date(1800, 1, 1)

for year, test_date in [(2013, datetime.date(2013, 10, 7)), (2014, datetime.date(2014, 10, 6)), (2015, datetime.date(2015, 10, 27))]:
    # Query DAS to get actual time range start for the year
    url = f'https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{year}.nc.ascii?time[0:1:1]'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req, timeout=10)
    lines = res.read().decode('utf-8').splitlines()
    # Find line with float
    time_start = None
    for l in lines:
        try:
            val = float(l.strip())
            if val > 50000:
                time_start = val
                break
        except ValueError:
            pass
    target_days = (test_date - d0).days
    idx = int(target_days - time_start)
    print(f'{year}: Jan 1 days = {time_start}, Target {test_date} days = {target_days}, Calculated idx = {idx}')
    
    # Verify index query
    url_test = f'https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{year}.nc.ascii?time[{idx}:1:{idx}]'
    req_t = urllib.request.Request(url_test, headers={'User-Agent': 'Mozilla/5.0'})
    res_t = urllib.request.urlopen(req_t, timeout=10)
    out = res_t.read().decode('utf-8')
    assert str(float(target_days)) in out, f"Mismatch: expected {target_days} in {out}"
    print(f'  -> Verified NOAA PSL time index {idx} exactly matches {test_date}!')
