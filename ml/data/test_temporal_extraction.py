import os
import pandas as pd
import numpy as np
from datetime import datetime
from ml.data.schemas.track import CycloneTrackPoint
from ml.features.track_features import TrackFeatureExtractor
from ml.features.temporal_features import TemporalFeatureExtractor

df = pd.read_csv('data/processed/hursat_ri_samples.csv')
print(f"Total rows: {len(df)}")

temporal_records = []
for storm_id, grp in df.groupby('storm_id'):
    grp = grp.sort_values('cyclone_time_utc')
    rows = grp.to_dict('records')
    
    for i, curr in enumerate(rows):
        t_curr = curr['cyclone_time_utc']
        season = int(t_curr[:4])
        p_curr = CycloneTrackPoint(
            storm_id=storm_id,
            storm_name=curr['storm_name'],
            season=season,
            basin="NI",
            timestamp_utc=t_curr,
            latitude=curr['latitude'],
            longitude=curr['longitude'],
            wind_speed_kts=curr['current_wind_kts'],
            central_pressure_mb=curr['central_pressure_mb'] if pd.notna(curr['central_pressure_mb']) else None,
            nature=curr['nature'] if pd.notna(curr['nature']) else "TS"
        )
        
        # Previous point for translation speed/bearing
        p_prev = None
        if i > 0:
            prev = rows[i-1]
            p_prev = CycloneTrackPoint(
                storm_id=storm_id,
                storm_name=prev['storm_name'],
                season=int(prev['cyclone_time_utc'][:4]),
                basin="NI",
                timestamp_utc=prev['cyclone_time_utc'],
                latitude=prev['latitude'],
                longitude=prev['longitude'],
                wind_speed_kts=prev['current_wind_kts'],
                central_pressure_mb=prev['central_pressure_mb'] if pd.notna(prev['central_pressure_mb']) else None,
                nature=prev['nature'] if pd.notna(prev['nature']) else "TS"
            )
            
        track_feats = TrackFeatureExtractor.extract(p_curr, p_prev)
        
        # Find 6h and 12h historical points
        dt_curr = datetime.fromisoformat(t_curr.replace('Z', '+00:00'))
        h6_row = None
        h12_row = None
        for j in range(i-1, -1, -1):
            t_past = datetime.fromisoformat(rows[j]['cyclone_time_utc'].replace('Z', '+00:00'))
            diff_h = (dt_curr - t_past).total_seconds() / 3600.0
            if h6_row is None and 4.0 <= diff_h <= 8.5:
                h6_row = rows[j]
            if h12_row is None and 10.0 <= diff_h <= 15.0:
                h12_row = rows[j]
            if diff_h > 16.0:
                break
                
        t_6h_time = h6_row['cyclone_time_utc'] if h6_row else None
        t_6h_wind = h6_row['current_wind_kts'] if h6_row else None
        t_6h_pres = h6_row['central_pressure_mb'] if (h6_row and pd.notna(h6_row['central_pressure_mb'])) else None
        
        t_12h_time = h12_row['cyclone_time_utc'] if h12_row else None
        t_12h_wind = h12_row['current_wind_kts'] if h12_row else None
        
        temp_feats = TemporalFeatureExtractor.extract(
            current_time_utc=t_curr,
            current_wind_kts=curr['current_wind_kts'],
            current_pressure_mb=curr['central_pressure_mb'] if pd.notna(curr['central_pressure_mb']) else None,
            hist_6h_time_utc=t_6h_time,
            hist_6h_wind_kts=t_6h_wind,
            hist_6h_pressure_mb=t_6h_pres,
            hist_12h_time_utc=t_12h_time,
            hist_12h_wind_kts=t_12h_wind,
        )
        
        # Build 23-feature vector matching Sprint 6 subset_b
        rec = {
            'storm_id': storm_id,
            'cyclone_time_utc': t_curr,
            'partition': curr['partition'],
            'ri_target': curr['ri_target'] if pd.notna(curr['ri_target']) else None,
            'ri_label_status': curr['ri_label_status'],
            
            'track_latitude_val': track_feats['track_latitude'] or 0.0,
            'track_latitude_is_observed': 1.0 if track_feats['track_latitude'] is not None else 0.0,
            
            'track_longitude_val': track_feats['track_longitude'] or 0.0,
            'track_longitude_is_observed': 1.0 if track_feats['track_longitude'] is not None else 0.0,
            
            'track_wind_speed_val': track_feats['track_wind_speed'] or 0.0,
            'track_wind_speed_is_observed': 1.0 if track_feats['track_wind_speed'] is not None else 0.0,
            
            'track_pressure_val': track_feats['track_pressure'] or 0.0,
            'track_pressure_is_observed': 1.0 if track_feats['track_pressure'] is not None else 0.0,
            
            'track_translation_speed_kts_val': track_feats['track_translation_speed_kts'] or 0.0,
            'track_translation_speed_kts_is_observed': 1.0 if track_feats['track_translation_speed_kts'] is not None else 0.0,
            
            'track_translation_bearing_deg_val': track_feats['track_translation_bearing_deg'] or 0.0,
            'track_translation_bearing_deg_is_observed': 1.0 if track_feats['track_translation_bearing_deg'] is not None else 0.0,
            
            'temp_delta_wind_6h_val': temp_feats['temp_delta_wind_6h'] or 0.0,
            'temp_delta_wind_6h_is_observed': 1.0 if temp_feats['temp_delta_wind_6h'] is not None else 0.0,
            
            'temp_delta_wind_12h_val': temp_feats['temp_delta_wind_12h'] or 0.0,
            'temp_delta_wind_12h_is_observed': 1.0 if temp_feats['temp_delta_wind_12h'] is not None else 0.0,
            
            'temp_delta_pressure_6h_val': temp_feats['temp_delta_pressure_6h'] or 0.0,
            'temp_delta_pressure_6h_is_observed': 1.0 if temp_feats['temp_delta_pressure_6h'] is not None else 0.0,
            
            'temp_wind_change_rate_per_hour_val': temp_feats['temp_wind_change_rate_per_hour'] or 0.0,
            'temp_wind_change_rate_per_hour_is_observed': 1.0 if temp_feats['temp_wind_change_rate_per_hour'] is not None else 0.0,
            
            'temp_delta_ir_min_6h_val': 0.0,
            'temp_delta_ir_min_6h_is_observed': 0.0,
            
            'quality_track_available': 1.0,
        }
        temporal_records.append(rec)

tdf = pd.DataFrame(temporal_records)
print("Temporal records built successfully:", len(tdf))
print("Sample head:")
print(tdf[['storm_id', 'cyclone_time_utc', 'track_wind_speed_val', 'temp_delta_wind_6h_val', 'temp_delta_wind_12h_val']].head())
