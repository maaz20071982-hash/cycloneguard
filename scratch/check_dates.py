import pandas as pd

df = pd.read_csv('data/processed/hursat_ri_samples.csv')
print('Unique storms:', df['storm_name'].unique())
print('Total rows:', len(df))
print('Date range per storm:')
for storm in df['storm_name'].unique():
    sdf = df[df['storm_name'] == storm]
    t_min = sdf['cyclone_time_utc'].min()
    t_max = sdf['cyclone_time_utc'].max()
    print(f'  {storm}: {len(sdf)} fixes, {t_min} to {t_max}')
