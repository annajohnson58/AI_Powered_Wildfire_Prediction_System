# import ee
# import pandas as pd
# from datetime import date

# ee.Initialize()

# today = date.today().isoformat()
# gaul = ee.FeatureCollection("FAO/GAUL/2015/level2")
# kerala_districts = gaul.filter(ee.Filter.eq('ADM1_NAME', 'Kerala'))
# target_districts = ['Thrissur', 'Palakkad', 'Idukki']
# results = []

# # 🛰️ Sentinel-2 surface reflectance
# sentinel = ee.ImageCollection('COPERNICUS/S2_SR') \
#     .filterDate('2025-09-01', today) \
#     .filterBounds(kerala_districts.geometry()) \
#     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
#     .select(['B4', 'B8'])  # Red and NIR

# # 🧠 Compute NDVI: (NIR - Red) / (NIR + Red)
# def compute_ndvi(image):
#     ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
#     return image.addBands(ndvi)

# sentinel_ndvi = sentinel.map(compute_ndvi)
# latest_ndvi = sentinel_ndvi.sort('system:time_start', False).first()

# image_count = sentinel_ndvi.size().getInfo()
# print(f"🛰️ Sentinel-2 NDVI images found: {image_count}")

# if image_count == 0:
#     print("⚠️ No Sentinel-2 NDVI images available in the selected date range.")
# else:
#     for district_name in target_districts:
#         district = kerala_districts.filter(ee.Filter.eq('ADM2_NAME', district_name))

#         try:
#             ndvi_mean = latest_ndvi.select('NDVI').reduceRegion(
#                 reducer=ee.Reducer.mean(),
#                 geometry=district.geometry(),
#                 scale=10,
#                 maxPixels=1e9
#             ).get('NDVI').getInfo()

#             results.append({
#                 'district': district_name,
#                 'date': today,
#                 'ndvi': ndvi_mean
#             })
#         except Exception as e:
#             print(f"⚠️ Error fetching NDVI for {district_name}: {e}")
#             results.append({
#                 'district': district_name,
#                 'date': today,
#                 'ndvi': None
#             })

#     df = pd.DataFrame(results)
#     df.to_csv('data/daily_ndvi.csv', index=False)
#     print("✅ Daily NDVI saved for:", ', '.join(target_districts))

import ee
import geemap
import pandas as pd
from datetime import datetime, timedelta

# 🌍 Initialize Earth Engine
ee.Initialize()

# 📅 Define 3-year date range
start_date = datetime(2022, 9, 17)
end_date = datetime(2025, 9, 17)
date_list = [start_date + timedelta(days=x) for x in range(0, (end_date - start_date).days, 5)]

# 🗺️ Load Kerala districts (replace with your asset path)
kerala_fc = ee.FeatureCollection("users/riarosemj27/kerala_districts")

# 📦 Store results
all_ndvi = []

# 🔁 Loop through dates
for date in date_list:
    date_str = date.strftime('%Y-%m-%d')
    start = ee.Date(date_str)
    end = start.advance(5, 'day')

    # 🛰️ Compute NDVI using harmonized Sentinel-2
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterDate(start, end) \
        .filterBounds(kerala_fc) \
        .map(lambda img: img.normalizedDifference(['B8', 'B4']).rename('NDVI')) \
        .mean()

    # 📊 Zonal mean NDVI per district
    try:
        stats = geemap.zonal_statistics(
            s2,
            kerala_fc,
            statistics_type='MEAN',
            scale=10,
            return_fc=False
        )

        if stats is not None and not stats.empty:
            stats['date'] = date_str
            all_ndvi.append(stats)
            print(f"✅ NDVI fetched for {date_str}")
        else:
            print(f"⚠️ No NDVI data for {date_str} (possibly cloudy or missing)")

    except Exception as e:
        print(f"❌ Error fetching NDVI for {date_str}: {e}")

# 🧾 Combine and save
if all_ndvi:
    ndvi_df = pd.concat(all_ndvi, ignore_index=True)
    ndvi_df.rename(columns={'mean': 'ndvi'}, inplace=True)
    ndvi_df.to_csv("data/ndvi_kerala_3yrs.csv", index=False)
    print("🎉 NDVI time series saved to data/ndvi_kerala_3yrs.csv")
else:
    print("⚠️ No NDVI data collected. Check asset path or cloud cover.")
