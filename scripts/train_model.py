import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

df = pd.read_csv('data/kerala_wildfire_features.csv')

# Create binary label from fire_count
df['fire_label'] = (df['fire_count'] > 0).astype(int)

# Define features and label
features = ['t2m', 'tp', 'u10', 'v10', 'ndvi', 'ndvi_lag1', 'ndvi_delta']
X = df[features]
y = df['fire_label']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
print("✅ Model trained. Accuracy:", model.score(X_test, y_test))
print(df['fire_label'].value_counts())