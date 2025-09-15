import pandas as pd
import os

FIRE_PATH = "data/fire_features.csv"
WEATHER_PATH = "data/weather_data.csv"
OUTPUT_PATH = "data/merged_features.csv"

def main():
    if not os.path.exists(FIRE_PATH) or not os.path.exists(WEATHER_PATH):
        print("❌ Required input files not found.")
        return

    try:
        fire_df = pd.read_csv(FIRE_PATH)
        weather_df = pd.read_csv(WEATHER_PATH)

        # Ensure date format matches
        fire_df['acq_date'] = pd.to_datetime(fire_df['acq_date'])
        weather_df['acq_date'] = pd.to_datetime(weather_df['acq_date'])

        # Merge on date and region
        merged_df = pd.merge(fire_df, weather_df, on=['acq_date', 'region'], how='left')

        # Fill missing fire counts with 0 (no fires that day)
        merged_df['fire_count'] = merged_df['fire_count'].fillna(0).astype(int)

        merged_df.to_csv(OUTPUT_PATH, index=False)
        print(f"✅ Merged dataset saved to: {OUTPUT_PATH}")
        print(merged_df.head())
    except Exception as e:
        print(f"⚠️ Error during merging: {e}")

if __name__ == "__main__":
    main()
