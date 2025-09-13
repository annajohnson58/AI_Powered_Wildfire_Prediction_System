import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

INPUT_PATH = "data/merged_features.csv"
MODEL_PATH = "models/fire_predictor.pkl"

def main():
    if not os.path.exists(INPUT_PATH):
        print("❌ Merged dataset not found.")
        return

    try:
        df = pd.read_csv(INPUT_PATH)

        # === Features and Target ===
        features = [
            'temperature_2m_max',
            'temperature_2m_min',
            'precipitation_sum',
            'windspeed_10m_max'
        ]
        X = df[features]
        y = df['fire_count']

        # === Train/Test Split ===
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # === Model Training ===
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # === Evaluation ===
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"✅ Model trained and saved to: {MODEL_PATH}")
        print(f"📊 MAE: {mae:.2f}")
        print(f"📈 R² Score: {r2:.2f}")

        # === Save Model ===
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, MODEL_PATH)

    except Exception as e:
        print(f"⚠️ Error during model training: {e}")

if __name__ == "__main__":
    main()
