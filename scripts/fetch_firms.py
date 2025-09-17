import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 🔥 Load MODIS fire data
fires = pd.read_csv("data/firms/fire_archive_J1V-C2_661536.csv")
fires['geometry'] = [Point(xy) for xy in zip(fires.longitude, fires.latitude)]
fires_gdf = gpd.GeoDataFrame(fires, geometry='geometry', crs="EPSG:4326")



kerala = gpd.read_file("data/shapefiles/kerala_districts.shp").to_crs("EPSG:4326")

fires_kerala = gpd.sjoin(fires_gdf, kerala, predicate='intersects')

hotspot_counts = fires_kerala.groupby('DISTRICT').size().reset_index(name='thermal_count')
hotspot_counts['DISTRICT'] = hotspot_counts['DISTRICT'].str.strip().str.lower()
hotspot_counts['thermal_flag'] = (hotspot_counts['thermal_count'] > 0).astype(int)
fused = pd.read_csv("data/fused/fused_ndvi_weather.csv")

fused['district'] = fused['district'].str.strip().str.lower()

fused = pd.merge(
    fused,
    hotspot_counts,
    left_on='district',
    right_on='DISTRICT',
    how='left'
)

fused['thermal_flag'] = fused['thermal_flag'].fillna(0).astype(int)
fused['thermal_count'] = fused['thermal_count'].fillna(0).astype(int)
fused['dryness_index'] = (1 - fused['ndvi']) * (1 - fused['rh'] / 100)

print(fused.head())
print(fused.columns)
fused.to_csv("data/fused/fused_ndvi_weather_thermal.csv", index=False)
