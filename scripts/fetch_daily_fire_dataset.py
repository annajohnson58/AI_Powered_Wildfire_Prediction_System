import ee
ee.Initialize(project='foresightai-469610')

# Thrissur region (10 km buffer)
region = ee.Geometry.Point([76.214, 10.527]).buffer(10000)

# Time range
start = '2024-01-01'
end = '2024-12-31'

# Load datasets
ndvi = (
    ee.ImageCollection("MODIS/061/MOD13Q1")
    .filterDate(start, end)
    .filterBounds(region)
    .select('NDVI')
    .map(lambda img: img.multiply(0.0001).copyProperties(img, ['system:time_start']))
)

lst = (
    ee.ImageCollection("MODIS/061/MOD11A1")
    .filterDate(start, end)
    .filterBounds(region)
    .select('LST_Day_1km')
    .map(lambda img: img.multiply(0.02).subtract(273.15).copyProperties(img, ['system:time_start']))
)

weather = (
    ee.ImageCollection("ECMWF/ERA5/DAILY")
    .filterDate(start, end)
    .filterBounds(region)
    .select(['temperature_2m', 'total_precipitation', 'u_component_of_wind_10m', 'v_component_of_wind_10m'])
)

firms = (
    ee.FeatureCollection("FIRMS")
    .filterDate(start, end)
    .filterBounds(region)
)

# Fire detection per day
def fire_count(date):
    start_d = ee.Date(date)
    end_d = start_d.advance(1, 'day')
    count = firms.filterDate(start_d, end_d).size()
    return ee.Feature(None, {
        'date': start_d.format('YYYY-MM-dd'),
        'fire_label': count
    })

dates = ee.List.sequence(0, ee.Date(end).difference(ee.Date(start), 'day').subtract(1))
date_list = dates.map(lambda d: fire_count(ee.Date(start).advance(d, 'day')))
fire_fc = ee.FeatureCollection(date_list)

# Daily NDVI, LST, Weather reducer with safe band checks
def daily_features(date):
    d = ee.Date(date)
    ndvi_img = ndvi.filterDate(d, d.advance(1, 'day')).first()
    lst_img = lst.filterDate(d, d.advance(1, 'day')).first()
    weather_img = weather.filterDate(d, d.advance(1, 'day')).mean()

    ndvi_val = ee.Algorithms.If(
        ndvi_img,
        ee.Algorithms.If(
            ndvi_img.bandNames().contains('NDVI'),
            ndvi_img.reduceRegion(ee.Reducer.mean(), region, 500).get('NDVI'),
            None
        ),
        None
    )

    lst_val = ee.Algorithms.If(
        lst_img,
        ee.Algorithms.If(
            lst_img.bandNames().contains('LST_Day_1km'),
            lst_img.reduceRegion(ee.Reducer.mean(), region, 1000).get('LST_Day_1km'),
            None
        ),
        None
    )

    weather_stats = weather_img.reduceRegion(ee.Reducer.mean(), region, 1000)
    temp_val = ee.Algorithms.If(weather_stats.contains('temperature_2m'), weather_stats.get('temperature_2m'), None)
    precip_val = ee.Algorithms.If(weather_stats.contains('total_precipitation'), weather_stats.get('total_precipitation'), None)
    u_wind = ee.Algorithms.If(weather_stats.contains('u_component_of_wind_10m'), weather_stats.get('u_component_of_wind_10m'), None)
    v_wind = ee.Algorithms.If(weather_stats.contains('v_component_of_wind_10m'), weather_stats.get('v_component_of_wind_10m'), None)

    return ee.Feature(None, {
        'date': d.format('YYYY-MM-dd'),
        'NDVI': ndvi_val,
        'LST_day': lst_val,
        'temp_2m': temp_val,
        'precip_m': precip_val,
        'u_wind_10m': u_wind,
        'v_wind_10m': v_wind
    })

daily_fc = ee.FeatureCollection(dates.map(lambda d: daily_features(ee.Date(start).advance(d, 'day'))))

# Merge fire + features
merged = daily_fc.map(lambda f: f.set('fire_label', fire_fc.filter(ee.Filter.eq('date', f.get('date'))).first().get('fire_label')))

# Export to Drive
task = ee.batch.Export.table.toDrive(
    collection=merged,
    description='Daily_Fire_Thrissur_2024',
    folder='EarthEngineExports',
    fileNamePrefix='merged_daily_fire_thrissur_2024',
    fileFormat='CSV'
)
task.start()

print("✅ Daily fire dataset export started. Check your Drive > EarthEngineExports folder.")
