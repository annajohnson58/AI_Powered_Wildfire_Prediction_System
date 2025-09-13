import ee
ee.Initialize(project='foresightai-469610')

# Thrissur region (50 km buffer to match ERA5 grid)
region = ee.Geometry.Point([76.214, 10.527]).buffer(50000)

# Time range
start_date = '2024-01-01'
end_date = '2024-12-31'

# Load ERA5-Land monthly aggregated dataset
era5 = (
    ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
    .filterDate(start_date, end_date)
    .filterBounds(region)
)

# Extract monthly features
def extract_monthly(image):
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=10000,
        maxPixels=1e13
    )

    def safe(key):
        return ee.Algorithms.If(stats.get(key), stats.get(key), -9999)

    return ee.Feature(None, {
    'date': image.date().format('YYYY-MM'),
    'temp_2m': safe('temperature_2m'),
    'precip_m': safe('total_precipitation_sum'),
    'u_wind_10m': safe('u_component_of_wind_10m'),
    'v_wind_10m': safe('v_component_of_wind_10m'),
    df['temp_C'] = df['temp_2m'] - 273.15

})


# Map and export
features = era5.map(extract_monthly)
fc = ee.FeatureCollection(features)

task = ee.batch.Export.table.toDrive(
    collection=fc,
    description='ERA5Land_Monthly_Thrissur_2024',
    folder='EarthEngineExports',
    fileNamePrefix='era5land_monthly_thrissur_2024',
    fileFormat='CSV'
)
task.start()

print("✅ ERA5-Land monthly weather export started. Check your Drive > EarthEngineExports folder.")
