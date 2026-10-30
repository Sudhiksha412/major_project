import pandas as pd 
import joblib
import numpy as np
import psutil
import shap
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE

# 1. loading dataset with anomalies
df = pd.read_csv("system_data_with_anomalies.csv")
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values(by='Timestamp').reset_index(drop=True)

total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
cpu_cores = psutil.cpu_count(logical=True) 

# hardware details to understand system capacity 
df['Total_RAM_Capacity_GB'] = total_ram_gb
df['CPU_Cores_Count'] = cpu_cores

# predicting future failure based on current system health metrics 
PREDICTION_LOOKAHEAD_STEPS = -10 
df["Future_Failure_Target"] = df["Anomaly"].shift(PREDICTION_LOOKAHEAD_STEPS)

train_df = df.dropna(subset=["Future_Failure_Target"]).reset_index(drop=True)

features = [
    'CPU_Usage', 'RAM_Usage', 'Disk_Usage', 'Bytes_Sent', 'Bytes_Recv',
    'Process_Count', 'Battery_Percent', 'cpu_diff', 'network_total', 
    'cpu_rolling_mean', 'Total_RAM_Capacity_GB', 'CPU_Cores_Count'
]

X = train_df[features].fillna(0)
y = train_df["Future_Failure_Target"].astype(int)

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# SMOTE for balance
anomaly_count = y_train[y_train == 1].sum()
if anomaly_count > 1:
    k_neigh = min(2, anomaly_count - 1)
    smote = SMOTE(k_neighbors = k_neigh, random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
else:
    X_train_res, y_train_res = X_train, y_train

# Model Training
model = HistGradientBoostingClassifier(
    max_iter=100, learning_rate=0.05, max_leaf_nodes=15, 
    class_weight="balanced", random_state=42
)
model.fit(X_train_res, y_train_res)

# Evaluation
accuracy = model.score(X_test, y_test)
print(f" Model Accuracy based on System Personalization: {accuracy * 100:.2f}%")
print("\n Detailed Classification Report:")
print(classification_report(y_test, model.predict(X_test), zero_division=0))
print("\n" + "="*50)
print("EXPLAINABLE AI: REASONING BEHIND ANOMALIES & SYSTEM HEALTH EFFECT")
print("="*50)

# breaking down the model's decision-making process using SHAP
explainer = shap.Explainer(model,X_train_res)
shap_values = explainer(X_test)

# gets the reason for anomaly detection and its impact on system health
anomalous_indices = np.where(y_test == 1)[0]

if len(anomalous_indices) > 0:
    sample_idx = anomalous_indices[0]
    if len(shap_values.values.shape) == 3:
        sample_shap = shap_values.values[sample_idx ,:,1]
    else:
        sample_shap = shap_values.values[sample_idx]   

    # taking top 3 contributing features for the detected anomaly 
    top_contributors = np.argsort(np.abs(sample_shap))[::-1][:3]
    
    print(f"ALERT: Future Anomaly Detected at sample index [{sample_idx}]!")
    print("Reason for this Anomaly (Top Contributing Metrics):")
    
    for rank, feat_idx in enumerate(top_contributors, 1):
        feature_name = features[feat_idx]
        feature_value = X_test.iloc[sample_idx][feature_name]
        if sample_shap[feat_idx] > 0:
            print(f"  {rank}. {feature_name} (Value: {feature_value}), SHAP Impact: +{sample_shap[feat_idx]:.4f} - indicating it contributes positively to the anomaly")
        else:
            print(f"  {rank}. {feature_name} (Value: {feature_value}), SHAP Impact: {sample_shap[feat_idx]:.4f} - indicating it contributes negatively to the anomaly")

    print("\n Hardware-Aware Health Impact:")
    cores = X_test.iloc[sample_idx]['CPU_Cores_Count']
    ram_cap = X_test.iloc[sample_idx]['Total_RAM_Capacity_GB'] if 'Total_RAM_Capacity_GB' in X_test.columns else total_ram_gb
    
    print(f"  - Current Analysis Environment: {cores} CPU Cores | {ram_cap} GB Total RAM")
    print("  - Model is learning impact patterns relative to this specific hardware capacity.")

else:
    print(" No future anomalies detected. System Health is stable according to current hardware profile.")

# Save Model
joblib.dump(model, "hist_gb_personalized_model.pkl")

print("\nModel saved successfully as 'hist_gb_personalized_model.pkl'")
full_X = df[features].fillna(0)
df["Risk_Prediction"] = model.predict(full_X)
df.to_csv("system_data_with_predictions.csv", index=False)
print("Saved all live mapping tracks to 'system_data_with_predictions.csv'")