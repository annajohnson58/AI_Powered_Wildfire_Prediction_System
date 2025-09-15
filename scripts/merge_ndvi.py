import pandas as pd

# Load your climate–fire dataset
df = pd.read_csv('data/kerala_wildfire_dataset_2024.csv')

# Load NDVI data
ndvi = pd.read_csv('data/Sentinel2_NDVI_Kerala_2024.csv')  # rename your exported file accordingly

# Merge on month and district
merged = pd.merge(df, ndvi[['district', 'month', 'ndvi']], on=['district', 'month'], how='left')

# Save the enriched dataset
merged.to_csv('data/kerala_wildfire_with_ndvi.csv', index=False)
print("✅ NDVI merged successfully. Rows:", len(merged))