from ml.datasets.spatial_ri_dataset import SpatialRIDatasetBuilder, SPATIAL_FEATURE_NAMES, TEMPORAL_FEATURE_NAMES
import numpy as np

builder = SpatialRIDatasetBuilder()
dataset = builder.build()

print(f"Total samples: {len(dataset)}")
supervised = dataset.get_supervised_samples()
print(f"Supervised samples: {len(supervised)}")

train_ds = dataset.filter_by_partition("TRAIN")
val_ds = dataset.filter_by_partition("VAL")
test_ds = dataset.filter_by_partition("TEST")

print(f"Train total: {len(train_ds)}, supervised: {len(train_ds.get_supervised_samples())}")
print(f"Val total:   {len(val_ds)}, supervised: {len(val_ds.get_supervised_samples())}")
print(f"Test total:  {len(test_ds)}, supervised: {len(test_ds.get_supervised_samples())}")

X_tr_s, y_tr_s, _ = train_ds.to_numpy(supervised_only=True)
X_val_s, y_val_s, _ = val_ds.to_numpy(supervised_only=True)
X_te_s, y_te_s, _ = test_ds.to_numpy(supervised_only=True)

print(f"Spatial X_train shape: {X_tr_s.shape}, y_train positives: {np.sum(y_tr_s == 1)}")
print(f"Spatial X_val shape:   {X_val_s.shape}, y_val positives:   {np.sum(y_val_s == 1)}")
print(f"Spatial X_test shape:  {X_te_s.shape}, y_test positives:  {np.sum(y_te_s == 1)}")

X_tr_c, y_tr_c, _ = train_ds.to_numpy(supervised_only=True, include_temporal=True)
print(f"Combined X_train shape: {X_tr_c.shape}")
print(f"Spatial features count: {len(SPATIAL_FEATURE_NAMES)}")
print(f"Temporal features count: {len(TEMPORAL_FEATURE_NAMES)}")
print(f"Combined total: {len(SPATIAL_FEATURE_NAMES) + len(TEMPORAL_FEATURE_NAMES)}")
