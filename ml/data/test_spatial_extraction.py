import os
import time
import pandas as pd
import numpy as np
from ml.features.satellite_spatial import SatelliteSpatialFeatureExtractor

df = pd.read_csv('data/processed/hursat_ri_samples.csv')
print(f"Loaded {len(df)} samples from hursat_ri_samples.csv")

extractor = SatelliteSpatialFeatureExtractor()

t0 = time.time()
extracted_features = []
missing_patches = 0

for idx, row in df.iterrows():
    patch_dir = row['patch_dir']
    
    # Load IRWIN
    irwin_path = os.path.join(patch_dir, "IRWIN", "patch.npy")
    irwvp_path = os.path.join(patch_dir, "IRWVP", "patch.npy")
    vschn_path = os.path.join(patch_dir, "VSCHN", "patch.npy")
    
    irwin_patch = np.load(irwin_path) if os.path.exists(irwin_path) else None
    irwvp_patch = np.load(irwvp_path) if os.path.exists(irwvp_path) else None
    vschn_patch = np.load(vschn_path) if os.path.exists(vschn_path) else None
    
    if irwin_patch is None:
        missing_patches += 1
        continue
        
    feats = extractor.extract_all_features(irwin_patch, irwvp_patch, vschn_patch)
    feats['storm_id'] = row['storm_id']
    feats['storm_name'] = row['storm_name']
    feats['cyclone_time_utc'] = row['cyclone_time_utc']
    feats['partition'] = row['partition']
    feats['ri_target'] = row['ri_target']
    feats['ri_label_status'] = row['ri_label_status']
    extracted_features.append(feats)

t1 = time.time()
print(f"Extracted {len(extracted_features)} fixes in {t1 - t0:.2f}s. Missing patches: {missing_patches}")

feat_df = pd.DataFrame(extracted_features)
print(f"Feature matrix shape: {feat_df.shape}")
print("Number of columns:", len(feat_df.columns))

# Check for non-metadata feature names
feat_cols = [c for c in feat_df.columns if c not in ('storm_id', 'storm_name', 'cyclone_time_utc', 'partition', 'ri_target', 'ri_label_status')]
print(f"Total extracted feature columns: {len(feat_cols)}")
print("Sample feature values (first 3 rows):")
print(feat_df[feat_cols[:8]].head(3))

# Check NaN rates per feature
nan_counts = feat_df[feat_cols].isna().sum()
high_nan = nan_counts[nan_counts > 0]
print("Features with NaNs across 347 samples:")
print(high_nan)
