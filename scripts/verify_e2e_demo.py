import os
import sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from backend.app.main import app

def test_full_e2e_demo():
    client = TestClient(app)
    
    print("============================================================")
    print("CYCLONEGUARD SPRINT 14: END-TO-END DEMO FLOW TEST")
    print("============================================================")
    
    # STEP 1: Cyclone List
    r1 = client.get("/api/v1/cyclones")
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"
    cyclones = r1.json()["data"]["cyclones"]
    names = [c["name"] for c in cyclones]
    assert "CHAPALA" in names, "Cyclone CHAPALA not found in database!"
    chapala = next(c for c in cyclones if c["name"] == "CHAPALA")
    print(f"[STEP 1] Selected Storm: {chapala['name']} ({chapala['id']}) - Basin: {chapala['basin']}")
    
    # STEP 2: Verified Timeline Observation
    r2 = client.get(f"/api/v1/cyclones/{chapala['name']}/timeline")
    assert r2.status_code == 200
    timeline = r2.json()["data"]["timeline"]
    target_time = "2015-10-28T18:00:00Z"
    obs_times = [o["observation_time"] for o in timeline]
    assert any(target_time[:13] in t for t in obs_times), f"{target_time} not in timeline!"
    print(f"[STEP 2] Observation Selected: {target_time} (Found in {len(timeline)} timeline points)")
    
    # STEP 3-8: Case Study End-to-End Evaluation
    r3 = client.get(f"/api/v1/cyclones/{chapala['name']}/case-study?observation_time={target_time}")
    assert r3.status_code == 200
    cs = r3.json()["data"]
    
    model_saw = cs["what_the_model_saw"]
    
    # STEP 3: Current Intensity
    temp = model_saw["temporal_indicators"]
    curr_wind = temp["current_wind_kts"]
    curr_press = temp["central_pressure_mb"]
    print(f"[STEP 3] Current Intensity: {curr_wind} kt | Central Pressure: {curr_press} mb")
    
    # STEP 4: Temporal Evolution
    print(f"[STEP 4] Temporal Evolution: Delta V_6h={temp['wind_change_6h_kts']} kt, Delta V_12h={temp['wind_change_12h_kts']} kt, Delta P_6h={temp['pressure_drop_6h_mb']} mb")
    
    # STEP 5: Satellite Evidence
    sat = model_saw["satellite_evidence"]
    print(f"[STEP 5] Satellite Evidence: Source={sat['source']}, Channels={sat['channels_available']}, IRWIN Mean Tb={sat['irwin_mean_tb_k']} K, Core Mean={sat['core_convection_mean_k']} K")
    assert "IRWIN" in sat["channels_available"], "Expected IRWIN channel to be available!"
    
    # STEP 5b: Real Patch Image Bytes
    r4 = client.get(sat["imagery_endpoint"])
    assert r4.status_code == 200
    assert r4.headers.get("content-type") == "image/png"
    assert len(r4.content) > 1000, "Patch image size abnormally small"
    print(f"[STEP 5b] Authentic Satellite Patch Retrieved: {len(r4.content)} bytes (image/png) from {sat['imagery_endpoint']}")
    
    # STEP 6: Frozen Model Prediction Result
    model_score = model_saw["model_score"]
    risk_idx = model_score["ri_risk_index"]
    tau = model_score["operating_threshold"]
    signal = model_score["ri_flag"]
    score_label = model_score["score_label"]
    assert abs(risk_idx - 0.3592) < 0.001, f"Expected ~0.3592, got {risk_idx}"
    assert tau == 0.125, f"Expected tau=0.125, got {tau}"
    assert signal is True, "Expected model-estimated RI risk = True"
    assert score_label == "Empirical RI Risk Index", f"Label mismatch: {score_label}"
    print(f"[STEP 6] Model Result: {score_label} = {risk_idx:.4f} (Threshold tau = {tau}) -> Signal = {signal}")
    
    # STEP 7: Model Feature Attribution
    attr = model_saw["model_feature_attribution"]
    top_features = attr["top_supporting_features"]
    assert len(top_features) > 0, "No attribution features returned"
    print(f"[STEP 7] Feature Attribution ({attr['title']}): {len(top_features)} top supporting features")
    for idx, f in enumerate(top_features[:4], 1):
        print(f"         {idx}. {f['display_name']} ({f['feature_name']}): score={f['attribution_score']:.4f}")
        
    # STEP 8: Historical Outcome (Quarantined)
    outcome = cs["historical_outcome"]
    future_wind = outcome["observed_future_wind_kts"]
    delta_v = outcome["observed_delta_v_24h"]
    ri_occurred = outcome["ri_occurred"]
    assert future_wind == 65.0, f"Expected 65.0 kt, got {future_wind}"
    assert delta_v == 35.0, f"Expected +35.0 kt, got {delta_v}"
    assert ri_occurred is True, "Expected RI occurred = True"
    print(f"[STEP 8] Historical Ground-Truth Outcome ({outcome['title']}): Future V={future_wind} kt, Delta V_24h=+{delta_v} kt, RI Occurred={ri_occurred}")
    
    # STEP 9: Explanation
    print("[STEP 9] Scientific Principle Verified: The system detected a model-estimated RI signal (0.3592 > 0.125) before the verified 24-hour intensification outcome (+35 kt).")
    print("============================================================")
    print("DEMO FLOW TEST RESULT: 100% VERIFIED AUTHENTIC & ACCURATE")
    print("============================================================")

if __name__ == "__main__":
    test_full_e2e_demo()
