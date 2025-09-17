import cdsapi
import datetime
import os

# 📅 Use latest available ERA5 date (typically 4–5 days behind)
latest_available_date = datetime.date.today() - datetime.timedelta(days=5)
date_str = latest_available_date.strftime('%Y-%m-%d')
print(f"📅 Requesting ERA5 weather for {date_str}")

# 📁 Output directory
output_dir = "data/weather"
os.makedirs(output_dir, exist_ok=True)

# 🌍 CDS API client
c = cdsapi.Client()

# 📦 ERA5-Land data request
c.retrieve(
    'reanalysis-era5-land',
    {
        'variable': [
            '2m_temperature',
            '2m_dewpoint_temperature',
            'total_precipitation',
            '10m_u_component_of_wind',
            '10m_v_component_of_wind'
        ],
        'year': str(latest_available_date.year),
        'month': str(latest_available_date.month).zfill(2),
        'day': str(latest_available_date.day).zfill(2),
        'time': [f"{hour:02d}:00" for hour in range(0, 24)],
        'format': 'netcdf',
        'area': [12.5, 74.5, 8.0, 78.5],  # Kerala bounding box: N, W, S, E
    },
    f"{output_dir}/era5_{date_str}.nc"
)

print(f"✅ ERA5 weather data saved to {output_dir}/era5_{date_str}.nc")
