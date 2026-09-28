import urllib.request
import json
import sys

print("=" * 70)
print("CYCLONEGUARD SPRINT 2 USER PORTAL INTEGRATION & ROUTE VERIFICATION")
print("=" * 70)

failed = False

# 1. Test Public Routes (Content rendering)
public_routes = [
    ("/", ["cycloneguard", "cyclone", "monitor"]),
    ("/about", ["about cycloneguard", "rapid intensification", "limitations"]),
    ("/login", ["sign in", "password"]),
    ("/register", ["account", "password"]),
]

print("\n--- 1. Testing Public Routes ---")
for path, expected_substrings in public_routes:
    url = f"http://localhost:3000{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Sprint2Verifier/1.0"})
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read().decode("utf-8").lower()
            missing = [s for s in expected_substrings if s.lower() not in content]
            if status == 200 and not missing:
                print(f"[PASS] {path:25} -> HTTP {status} (Verified: {', '.join(expected_substrings)})")
            else:
                print(f"[FAIL] {path:25} -> HTTP {status}, missing: {missing}")
                failed = True
    except Exception as e:
        print(f"[ERROR] {path:25} -> {e}")
        failed = True

# 2. Test Protected User Portal Routes (Session Gating Verification)
protected_routes = [
    "/user/dashboard",
    "/user/monitor",
    "/user/cyclones",
    "/user/cyclones/ref-vortex-01",
    "/user/history",
    "/user/profile",
]

print("\n--- 2. Testing Protected User Portal Routes (Auth Session Gating) ---")
for path in protected_routes:
    url = f"http://localhost:3000{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Sprint2Verifier/1.0"})
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read().decode("utf-8")
            # Must verify session gating (renders Verifying platform session...)
            if status == 200 and "Verifying platform session" in content:
                print(f"[PASS] {path:30} -> HTTP {status} (Protected by PortalLayout session verification)")
            else:
                print(f"[FAIL] {path:30} -> HTTP {status} (Missing session protection check)")
                failed = True
    except Exception as e:
        print(f"[ERROR] {path:30} -> {e}")
        failed = True

# 3. Test Backend API Endpoints (Health, Auth, Cyclones, Historical, Forecast, Analysis)
api_endpoints = [
    ("http://localhost:8000/api/v1/health", False),
    ("http://localhost:8000/api/v1/system/info", False),
    ("http://localhost:8000/api/v1/cyclones", True),
    ("http://localhost:8000/api/v1/cyclones/historical", True),
    ("http://localhost:8000/api/v1/cyclones/test-storm/forecast", True),
    ("http://localhost:8000/api/v1/cyclones/test-storm/analysis", True),
]

print("\n--- 3. Testing Backend Endpoints ---")
for url, is_protected in api_endpoints:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Sprint2Verifier/1.0"})
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.status
                data = json.loads(resp.read().decode("utf-8"))
                print(f"[PASS] {url:60} -> HTTP {status} (Success: {data.get('success')})")
        except urllib.error.HTTPError as he:
            if is_protected and he.code == 401:
                print(f"[PASS] {url:60} -> HTTP 401 (Correctly unauthorized without JWT)")
            else:
                print(f"[FAIL] {url:60} -> HTTP {he.code}")
                failed = True
    except Exception as e:
        print(f"[ERROR] {url:60} -> {e}")
        failed = True

print("=" * 70)
if failed:
    print("VERIFICATION FAILED")
    sys.exit(1)
else:
    print("ALL SPRINT 2 USER PORTAL & API CHECKS PASSED SUCCESSFULLY")
    sys.exit(0)
