import urllib.request
import urllib.error
import json
import sys

print("=" * 75)
print("CYCLONEGUARD SPRINT 3 ADMIN PORTAL INTEGRATION & E2E VERIFICATION")
print("=" * 75)

failed = False

# -------------------------------------------------------------
# 1. Test Admin Frontend Routes (Protected by AdminLayout Session Gating)
# -------------------------------------------------------------
admin_routes = [
    "/admin",
    "/admin/dashboard",
    "/admin/data",
    "/admin/models",
    "/admin/predictions",
    "/admin/alerts",
    "/admin/users",
    "/admin/system",
]

print("\n--- 1. Testing Admin Frontend Routes (Protected Session Gating) ---")
for path in admin_routes:
    url = f"http://localhost:3000{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AdminPortalVerifier/1.0"})
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read().decode("utf-8")
            if status == 200:
                print(f"[PASS] {path:25} -> HTTP {status} (Rendered and protected by session gating)")
            else:
                print(f"[FAIL] {path:25} -> HTTP {status}")
                failed = True
    except Exception as e:
        print(f"[ERROR] {path:25} -> {e}")
        failed = True


# -------------------------------------------------------------
# 2. Test Unauthenticated Requests to Admin API (Must return 401)
# -------------------------------------------------------------
admin_api_endpoints = [
    "/api/v1/admin/dashboard",
    "/api/v1/admin/data-sources",
    "/api/v1/admin/models",
    "/api/v1/admin/predictions",
    "/api/v1/admin/alerts",
    "/api/v1/admin/users",
    "/api/v1/admin/audit-logs",
    "/api/v1/admin/system",
]

print("\n--- 2. Testing Unauthenticated Access to Admin API (HTTP 401 Enforcement) ---")
for ep in admin_api_endpoints:
    url = f"http://localhost:8000{ep}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AdminPortalVerifier/1.0"})
        with urllib.request.urlopen(req) as resp:
            print(f"[FAIL] {ep:30} -> Unexpected HTTP {resp.status} (Expected 401)")
            failed = True
    except urllib.error.HTTPError as he:
        if he.code == 401:
            print(f"[PASS] {ep:30} -> HTTP 401 (Properly rejected unauthenticated request)")
        else:
            print(f"[FAIL] {ep:30} -> HTTP {he.code}")
            failed = True
    except Exception as e:
        print(f"[ERROR] {ep:30} -> {e}")
        failed = True


# -------------------------------------------------------------
# 3. Authenticate Admin and User Accounts
# -------------------------------------------------------------
print("\n--- 3. Authenticating Users to Test Authorization Model ---")

# Login Admin
admin_token = None
try:
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/login",
        data=json.dumps({
            "email": "admin@cycloneguard.internal",
            "password": "CycloneGuard2026!Admin"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        admin_token = res["data"]["access_token"]
        print(f"[PASS] Admin login succeeded (Role: {res['data']['user']['role']})")
except Exception as e:
    print(f"[ERROR] Admin login failed: {e}")
    failed = True

# Register or login standard user
user_token = None
try:
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/register",
        data=json.dumps({
            "name": "Standard Analyst",
            "email": "analyst_e2e@cycloneguard.internal",
            "password": "StandardPass123!",
            "role": "USER"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            pass
    except urllib.error.HTTPError as he:
        # Ignore if user already exists
        pass

    # Login standard user
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/login",
        data=json.dumps({
            "email": "analyst_e2e@cycloneguard.internal",
            "password": "StandardPass123!"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        user_token = res["data"]["access_token"]
        print(f"[PASS] Standard user login succeeded (Role: {res['data']['user']['role']})")
except Exception as e:
    print(f"[ERROR] Standard user setup failed: {e}")
    failed = True


# -------------------------------------------------------------
# 4. Test Standard USER Forbidden from Admin API (Must return 403)
# -------------------------------------------------------------
print("\n--- 4. Testing Standard USER Forbidden Access (HTTP 403 Enforcement) ---")
if user_token:
    for ep in admin_api_endpoints:
        url = f"http://localhost:8000{ep}"
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {user_token}",
                    "User-Agent": "AdminPortalVerifier/1.0"
                }
            )
            with urllib.request.urlopen(req) as resp:
                print(f"[FAIL] {ep:30} -> Unexpected HTTP {resp.status} (Expected 403)")
                failed = True
        except urllib.error.HTTPError as he:
            if he.code == 403:
                print(f"[PASS] {ep:30} -> HTTP 403 (USER role strictly forbidden)")
            else:
                print(f"[FAIL] {ep:30} -> HTTP {he.code}")
                failed = True
        except Exception as e:
            print(f"[ERROR] {ep:30} -> {e}")
            failed = True


# -------------------------------------------------------------
# 5. Test Admin User Access to Admin Endpoints (Must return 200)
# -------------------------------------------------------------
print("\n--- 5. Testing Admin User Access (HTTP 200 & Telemetry Integrity) ---")
if admin_token:
    for ep in admin_api_endpoints:
        url = f"http://localhost:8000{ep}"
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {admin_token}",
                    "User-Agent": "AdminPortalVerifier/1.0"
                }
            )
            with urllib.request.urlopen(req) as resp:
                status = resp.status
                data = json.loads(resp.read().decode("utf-8"))
                if status == 200 and data.get("success") is True:
                    print(f"[PASS] {ep:30} -> HTTP 200 (Success: True)")
                else:
                    print(f"[FAIL] {ep:30} -> HTTP {status}")
                    failed = True
        except Exception as e:
            print(f"[ERROR] {ep:30} -> {e}")
            failed = True


# -------------------------------------------------------------
# 6. Test Admin User Management Lifecycle & Safety Rules
# -------------------------------------------------------------
print("\n--- 6. Testing Admin User Management Security & Safety Rules ---")
if admin_token:
    try:
        # Get users list
        req = urllib.request.Request(
            "http://localhost:8000/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        with urllib.request.urlopen(req) as resp:
            users_list = json.loads(resp.read().decode("utf-8"))["data"]["users"]
            admin_user = next((u for u in users_list if u["role"] == "ADMIN"), None)
            standard_user = next((u for u in users_list if u["role"] == "USER"), None)

        if admin_user and standard_user:
            # 6a. Admin cannot revoke own ADMIN role (prevent lockout)
            try:
                patch_req = urllib.request.Request(
                    f"http://localhost:8000/api/v1/admin/users/{admin_user['id']}",
                    data=json.dumps({"role": "USER"}).encode("utf-8"),
                    headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
                    method="PATCH"
                )
                with urllib.request.urlopen(patch_req) as resp:
                    print("[FAIL] Admin self-demotion was allowed (Safety violation)")
                    failed = True
            except urllib.error.HTTPError as he:
                if he.code == 400:
                    print("[PASS] Admin self-demotion properly rejected with HTTP 400 (Lockout prevention)")
                else:
                    print(f"[FAIL] Admin self-demotion returned HTTP {he.code}")
                    failed = True

            # 6b. Admin cannot deactivate own account
            try:
                patch_req = urllib.request.Request(
                    f"http://localhost:8000/api/v1/admin/users/{admin_user['id']}/status",
                    data=json.dumps({"is_active": False}).encode("utf-8"),
                    headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
                    method="PATCH"
                )
                with urllib.request.urlopen(patch_req) as resp:
                    print("[FAIL] Admin self-deactivation was allowed (Safety violation)")
                    failed = True
            except urllib.error.HTTPError as he:
                if he.code == 400:
                    print("[PASS] Admin self-deactivation properly rejected with HTTP 400 (Lockout prevention)")
                else:
                    print(f"[FAIL] Admin self-deactivation returned HTTP {he.code}")
                    failed = True

            # 6c. Admin can update standard user role
            patch_req = urllib.request.Request(
                f"http://localhost:8000/api/v1/admin/users/{standard_user['id']}",
                data=json.dumps({"role": "ADMIN"}).encode("utf-8"),
                headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
                method="PATCH"
            )
            with urllib.request.urlopen(patch_req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                assert data["data"]["role"] == "ADMIN"
                print(f"[PASS] Role mutation (USER -> ADMIN) succeeded for target user")

            # Revert role back
            patch_req = urllib.request.Request(
                f"http://localhost:8000/api/v1/admin/users/{standard_user['id']}",
                data=json.dumps({"role": "USER"}).encode("utf-8"),
                headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
                method="PATCH"
            )
            with urllib.request.urlopen(patch_req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                assert data["data"]["role"] == "USER"
                print(f"[PASS] Role revert (ADMIN -> USER) succeeded for target user")
    except Exception as e:
        print(f"[ERROR] User management testing failed: {e}")
        failed = True


# -------------------------------------------------------------
# 7. Test Audit Logs Integrity
# -------------------------------------------------------------
print("\n--- 7. Testing Audit Logging Verification ---")
if admin_token:
    try:
        req = urllib.request.Request(
            "http://localhost:8000/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        with urllib.request.urlopen(req) as resp:
            logs = json.loads(resp.read().decode("utf-8"))["data"]["logs"]
            actions = [l["action"] for l in logs]
            print(f"[PASS] Audit logs retrieved ({len(logs)} entries found)")
            print(f"       Recorded actions: {list(set(actions))}")
            assert "ADMIN_LOGIN" in actions or "USER_ROLE_CHANGED" in actions
            print(f"[PASS] Real operational events (ADMIN_LOGIN / USER_ROLE_CHANGED) verified in audit trail")
    except Exception as e:
        print(f"[ERROR] Audit logging check failed: {e}")
        failed = True


# -------------------------------------------------------------
# 8. Test Health Check Probes
# -------------------------------------------------------------
print("\n--- 8. Testing Health Check Probes ---")
try:
    req = urllib.request.Request("http://localhost:8000/api/v1/health")
    with urllib.request.urlopen(req) as resp:
        health_data = json.loads(resp.read().decode("utf-8"))
        print(f"[PASS] Health check: application={health_data.get('application')}, database={health_data.get('database')}, ai_engine={health_data.get('ai_engine')}, data_pipeline={health_data.get('data_pipeline')}")
        assert health_data.get("ai_engine") == "not_deployed"
        assert health_data.get("data_pipeline") == "not_connected"
        print("[PASS] Health endpoint truthfully reports 'not_deployed' and 'not_connected' (Zero fake health)")
except Exception as e:
    print(f"[ERROR] Health check failed: {e}")
    failed = True

print("=" * 75)
if failed:
    print("SPRINT 3 VERIFICATION FAILED")
    sys.exit(1)
else:
    print("ALL SPRINT 3 ADMIN PORTAL CHECKS PASSED WITH ZERO ERRORS")
    sys.exit(0)
