# train_model.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# === Step 1: Load dataset ===
df = pd.read_csv("dataset/train1.csv")  # Replace with your actual dataset file

# Clean column names
df.columns = df.columns.str.strip()
print("📋 Columns in dataset:", df.columns.tolist())

# === Step 2: Check for Label column ===
if 'Label' not in df.columns:
    raise Exception("❌ Dataset must contain a 'Label' column.")

# === Step 3: Handle missing/infinite values ===
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(axis=1, thresh=len(df) * 0.9, inplace=True)
df.dropna(inplace=True)

# === Step 4: Separate features and label ===
y = df['Label']
X = df.drop(columns=['Label']).select_dtypes(include=[np.number])
y = y[X.index]  # Align labels

# === Step 5: Encode labels ===
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# === Step 6: Train-test split ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# === Step 7: Feature scaling ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# === Step 8: Hyperparameter tuning ===
param_grid = {
    'n_estimators': [100],
    'max_depth': [None],
    'min_samples_split': [2],
    'min_samples_leaf': [1]
}
grid = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3, scoring='accuracy')
grid.fit(X_train_scaled, y_train)

model = grid.best_estimator_
print(f"✅ Best Parameters: {grid.best_params_}")

# === Step 9: Evaluate classifier ===
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy: {accuracy:.4f}")
print("📊 Classification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# === Step 10: Train Isolation Forest for Anomaly Detection ===
normal_df = df[df['Label'] == 'normal'].drop(columns=['Label'])
normal_df = normal_df.select_dtypes(include=[np.number])
normal_df_scaled = scaler.transform(normal_df)

anomaly_model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
anomaly_model.fit(normal_df_scaled)
print("🛡️ Trained Isolation Forest for anomaly detection")

# === Step 11: Save everything using pickle ===
os.makedirs("model", exist_ok=True)

with open("model/app_id_classifier.pkl", "wb") as f:
    pickle.dump(model, f)

with open("model/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

with open("model/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

with open("model/anomaly_detector.pkl", "wb") as f:
    pickle.dump(anomaly_model, f)

with open("model/feature_names.pkl", "wb") as f:
    pickle.dump(X_train.columns.tolist(), f)

print("📦 Model, scaler, encoder, anomaly detector saved using pickle in /model/")
