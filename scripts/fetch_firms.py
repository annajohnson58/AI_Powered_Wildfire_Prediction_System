import ee
ee.Initialize(project='foresightai-469610')

# Define Thrissur region (10 km buffer)
region = ee.Geometry.Point([76.214, 10.527]).buffer(10000)

# Define time range
start_date = '2024-01-01'
end_date = '2024-12-31'

# Load FIRMS fire point data
fire_points = (
    ee.FeatureCollection("NASA/LANCE/SNPP_VIIRS/C2")


    .filterDate(start_date, end_date)
    .filterBounds(region)
)

# Count fire points per day
def count_fires(date):
    day_start = ee.Date(date)
    day_end = day_start.advance(1, 'day')
    daily = fire_points.filterDate(day_start, day_end)
    return ee.Feature(None, {
        'date': day_start.format('YYYY-MM-dd'),
        'fire_count': daily.size()
    })

# Generate list of dates
dates = ee.List.sequence(0, 364).map(lambda d: ee.Date(start_date).advance(d, 'day'))
daily_counts = ee.FeatureCollection(dates.map(count_fires))

# Export to Drive
task = ee.batch.Export.table.toDrive(
    collection=daily_counts,
    description='FIRMS_FireCounts_Thrissur_2024',
    folder='EarthEngineExports',
    fileNamePrefix='firms_firecounts_thrissur_2024',
    fileFormat='CSV'
)
task.start()

print("✅ FIRMS fire point count export started. Check your Drive > EarthEngineExports folder.")
