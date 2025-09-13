import ee
ee.Initialize(project='foresightai-469610')

# Define region and time
region = ee.Geometry.Point([76.214, 10.527]).buffer(5000)
start_date = '2024-01-01'
end_date = '2024-12-31'

# Load and filter NDVI
collection = (
    ee.ImageCollection('MODIS/061/MOD13Q1')
    .select('NDVI')
    .filterDate(start_date, end_date)
    .filterBounds(region)
)

# Function to extract mean NDVI
def extract(image):
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=250,
        maxPixels=1e13
    )
    ndvi = stats.get('NDVI')
    return ee.Feature(None, {
        'date': image.date().format('YYYY-MM-dd'),
        'NDVI': ee.Algorithms.If(ndvi, ndvi, -9999)
    })

# Build FeatureCollection
features = collection.map(extract)
fc = ee.FeatureCollection(features)

# Print diagnostics
print("🛰️ Image count:", collection.size().getInfo())
print("📊 Sample NDVI:", fc.limit(3).getInfo())

# Export to Drive
task = ee.batch.Export.table.toDrive(
    collection=fc,
    description='NDVI_Export_Thrissur_2024',
    folder='EarthEngineExports',
    fileNamePrefix='ndvi_thrissur_2024',
    fileFormat='CSV'
)
task.start()

print("✅ Export started. Check Drive > EarthEngineExports in a few minutes.")

