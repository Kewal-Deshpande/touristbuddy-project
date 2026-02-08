import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             ConfusionMatrixDisplay, RocCurveDisplay)
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Create models directory if not exists
os.makedirs('models', exist_ok=True)

# Load your data
df = pd.read_csv("pune_crime_data.csv")

# Convert date/time
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce')
df.dropna(subset=['Date', 'Time'], inplace=True)

# Extract temporal features
df['Hour'] = df['Time'].dt.hour
df['DayOfWeek'] = df['Date'].dt.dayofweek
df['Month'] = df['Date'].dt.month

# Create binary target (1 for violent crimes)
violent_crimes = ['Rape', 'Robbery', 'Molestation', 'Kidnapping']
df['IsViolent'] = df['Crime Type'].isin(violent_crimes).astype(int)

# --------------------------
# 1. Location clustering
coords = df[['Latitude', 'Longitude']]
kmeans = KMeans(n_clusters=5, random_state=42).fit(coords)
df['AreaCluster'] = kmeans.labels_

# Save KMeans model
joblib.dump(kmeans, 'models/kmeans.pkl')

# 2. Crime frequency features
# Calculate and save frequency features
hourly_counts = df.groupby('Hour').size().to_dict()
daily_counts = df.groupby('DayOfWeek').size().to_dict()
monthly_violent = df.groupby('Month')['IsViolent'].sum().to_dict()

joblib.dump(hourly_counts, 'models/hourly_counts.pkl')
joblib.dump(daily_counts, 'models/daily_counts.pkl')
joblib.dump(monthly_violent, 'models/monthly_violent.pkl')

# Add to dataframe
df['CrimesPerHour'] = df['Hour'].map(hourly_counts)
df['CrimesPerWeekday'] = df['DayOfWeek'].map(daily_counts)

# 3. Distance from a known hotspot (example: Hinjewadi coordinates)
hotspot_lat, hotspot_lon = 18.61426928, 73.91534962
df['DistanceFromHotspot'] = np.sqrt(
    (df['Latitude'] - hotspot_lat)**2 +
    (df['Longitude'] - hotspot_lon)**2
)

# 4. Temporal aggregations
df['ViolentCrimesThisMonth'] = df.groupby('Month')['IsViolent'].transform('sum')

# --------------------------
# Prepare Data
# --------------------------
# Select features
X = df[[
    'Latitude', 'Longitude',
    'Hour', 'DayOfWeek', 'Month',
    'AreaCluster',
    'CrimesPerHour', 'CrimesPerWeekday',
    'DistanceFromHotspot',
    'ViolentCrimesThisMonth'
]]

y = df['IsViolent']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save scaler
joblib.dump(scaler, 'models/scaler.pkl')

# Model Training
# --------------------------
# Initialize models with class weights
rf = RandomForestClassifier(
    n_estimators=200,
    class_weight='balanced',
    random_state=42
)

xgb = XGBClassifier(
    scale_pos_weight=len(y_train[y_train == 0])/len(y_train[y_train == 1]),
    eval_metric='logloss',
    random_state=42
)

# Train models
rf.fit(X_train_scaled, y_train)
xgb.fit(X_train_scaled, y_train)

# Evaluation
# --------------------------
def evaluate_model(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print(f"\n{model_name} Performance:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print(f"Precision: {precision_score(y_test, y_pred):.2f}")
    print(f"Recall: {recall_score(y_test, y_pred):.2f}")
    print(f"F1 Score: {f1_score(y_test, y_pred):.2f}")
    print(f"ROC AUC: {roc_auc_score(y_test, y_proba):.2f}")

    # Confusion Matrix
    fig, ax = plt.subplots(1, 2, figsize=(15, 5))
    ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, ax=ax[0])
    ax[0].set_title(f'{model_name} Confusion Matrix')

    # ROC Curve
    RocCurveDisplay.from_estimator(model, X_test, y_test, ax=ax[1])
    ax[1].set_title('ROC Curve')
    plt.show()

# Evaluate both models
evaluate_model(rf, X_test_scaled, y_test, "Random Forest")
evaluate_model(xgb, X_test_scaled, y_test, "XGBoost")

# For Random Forest
features = X.columns
importances = rf.feature_importances_
sorted_idx = np.argsort(importances)

plt.figure(figsize=(10, 6))
plt.barh(range(len(sorted_idx)), importances[sorted_idx], align='center')
plt.yticks(range(len(sorted_idx)), features[sorted_idx])
plt.title("Random Forest Feature Importance")
plt.show()

print("\nClass Distribution:")
print(y.value_counts(normalize=True))

# Generate comparison metrics
def get_metrics(model, X_test, y_test):
    y_pred = model.predict(X_test)
    return {
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred),
        'Recall': recall_score(y_test, y_pred),
        'F1': f1_score(y_test, y_pred)
    }

rf_metrics = get_metrics(rf, X_test_scaled, y_test)
xgb_metrics = get_metrics(xgb, X_test_scaled, y_test)

# Create comparison DataFrame
metrics_df = pd.DataFrame([rf_metrics, xgb_metrics],
                         index=['Random Forest', 'XGBoost'])

# 1. Evaluation Matrix (F1, Precision, Recall)
plt.figure(figsize=(10, 6))
metrics_df[['F1', 'Precision', 'Recall']].plot(kind='bar',
                                              colormap='Paired',
                                              edgecolor='black')
plt.title('Model Performance Comparison', fontsize=14)
plt.ylabel('Score', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title='Metrics', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# 2. Accuracy Comparison
plt.figure(figsize=(8, 5))
metrics_df['Accuracy'].plot(kind='bar',
                           color=['#1f77b4', '#ff7f0e'],
                           edgecolor='black')
plt.title('Model Accuracy Comparison', fontsize=14)
plt.ylabel('Accuracy', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Save best model logic
best_model_name = metrics_df['Accuracy'].idxmax()
models_dict = {'Random Forest': rf, 'XGBoost': xgb}

# Save best model
best_model = models_dict[best_model_name]
joblib.dump(best_model, 'best_model.pkl')

# Optional: Save scaler for deployment
joblib.dump(scaler, 'scaler.pkl')

print(f"\nSaved best model ({best_model_name}) with accuracy: {metrics_df.loc[best_model_name, 'Accuracy']:.4f}")

# Save both models
joblib.dump(rf, 'models/random_forest.pkl')
joblib.dump(xgb, 'models/xgboost.pkl')

# Save hotspot coordinates
hotspot_coords = {'lat': hotspot_lat, 'lon': hotspot_lon}
joblib.dump(hotspot_coords, 'models/hotspot_coords.pkl')

print("""
All artifacts saved:
- models/kmeans.pkl (cluster model)
- models/scaler.pkl (feature scaler)
- models/hourly_counts.pkl
- models/daily_counts.pkl
- models/monthly_violent.pkl
- models/random_forest.pkl
- models/xgboost.pkl
- models/hotspot_coords.pkl
""")