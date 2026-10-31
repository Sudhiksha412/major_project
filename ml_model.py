import pandas as pd 
import joblib
import numpy as np
import psutil
import shap
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from imblearn.over_sampling import SMOTE

# 1. loading dataset with anomalies
df = pd.read_csv("system_data_with_anomalies.csv")
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values(by='Timestamp').reset_index(drop=True)

df['cpu_diff'] = df['CPU_Usage'].diff().fillna(0)
df['network_total'] = df['Bytes_Sent'] + df['Bytes_Recv']
df['cpu_rolling_mean'] = df['CPU_Usage'].rolling(window=5, min_periods=1).mean()

total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
cpu_cores = psutil.cpu_count(logical=True)  
df['Total_RAM_Capacity_GB'] = total_ram_gb
df['CPU_Cores_Count'] = cpu_cores

features_for_labeling = [
    'CPU_Usage', 'RAM_Usage', 'Disk_Usage', 'Process_Count', 
    'Bytes_Sent', 'Bytes_Recv', 'cpu_diff', 'network_total', 'cpu_rolling_mean'
]

features_for_training = features_for_labeling + ['Total_RAM_Capacity_GB', 'CPU_Cores_Count']
split_idx = int(len(df) * 0.8)
train_df_raw = df.iloc[:split_idx].copy().reset_index(drop=True)
test_df_raw = df.iloc[split_idx:].copy().reset_index(drop=True)

print(f"Dataset partition: Train samples = {len(train_df_raw)} | Test samples = {len(test_df_raw)}")

print("🤖 Fitting unsupervised Isolation Forest tracking context on Train Split...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(train_df_raw[features_for_labeling])
X_test_scaled = scaler.transform(test_df_raw[features_for_labeling])

iso_forest = IsolationForest(contamination=0.05, random_state=42)
iso_forest.fit(X_train_scaled)

train_df_raw["Anomaly"] = [1 if pred == -1 else 0 for pred in iso_forest.predict(X_train_scaled)]
test_df_raw["Anomaly"] = [1 if pred == -1 else 0 for pred in iso_forest.predict(X_test_scaled)]

joblib.dump(scaler, "scaler.pkl")
joblib.dump(iso_forest, "isolation_forest_model.pkl")

processed_df = pd.concat([train_df_raw, test_df_raw], axis=0).reset_index(drop=True)

# predicting future failure based on current system health metrics 
PREDICTION_LOOKAHEAD_STEPS = -10 
processed_df["Future_Anomaly_Target"] = processed_df["Anomaly"].shift(PREDICTION_LOOKAHEAD_STEPS)
final_clean_df = processed_df.dropna(subset=["Future_Anomaly_Target"]).reset_index(drop=True)

X_full = final_clean_df[features_for_training]
y_full = final_clean_df["Future_Anomaly_Target"].astype(int)

final_split_idx = int(len(final_clean_df) * 0.8)
X_train, X_test = X_full.iloc[:final_split_idx], X_full.iloc[final_split_idx:]
y_train, y_test = y_full.iloc[:final_split_idx], y_full.iloc[final_split_idx:]

anomaly_count = y_train[y_train == 1].sum()
if anomaly_count > 1:
    k_neigh = min(2, anomaly_count - 1)
    smote = SMOTE(k_neighbors=k_neigh, random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
else:
    X_train_res, y_train_res = X_train, y_train

model = HistGradientBoostingClassifier(
    max_iter=100, learning_rate=0.05, max_leaf_nodes=15, 
    class_weight="balanced", random_state=42
)
model.fit(X_train_res, y_train_res)

y_pred = model.predict(X_test)
y_baseline = final_clean_df["Anomaly"].iloc[final_split_idx:].astype(int).values

print("\n" + "="*60)
print("PERFORMANCE COMPARISON: HIST GRADIENT BOOST VS. NAIVE BASELINE")
print("="*60)
cm_model = confusion_matrix(y_test, y_pred)
cm_base = confusion_matrix(y_test, y_baseline)

def compute_fpr(cm):
    tn, fp, fn, tp = cm.ravel()
    return fp / (fp + tn) if (fp + tn) > 0 else 0.0

print(f"HistGradientBoosting Performance Model:")
print(classification_report(y_test, y_pred, zero_division=0))
print(f"  - Confusion Matrix:\n {cm_model}")
print(f"  - False Positive Rate (FPR): {compute_fpr(cm_model):.4f}")

print(f"\n Naive Persistence Baseline (Current Anomaly Status -> Future Predictor):")
print(classification_report(y_test, y_baseline, zero_division=0))
print(f"  - Confusion Matrix:\n {cm_base}")
print(f"  - False Positive Rate (FPR): {compute_fpr(cm_base):.4f}")

print("\n Target Definition Statement:")
print("  Model Target Definition: Foretelling whether system parameters will encounter")
print("  an unsupervised resource anomaly state exactly 20 seconds into the future.")

print("\n" + "="*60)
print("EXPLAINABLE AI DIAGNOSTICS (SHAP)")
print("="*60)
explainer = shap.Explainer(model, X_train_res)
shap_values = explainer(X_test, check_additivity=False)

anomalous_indices = np.where(y_test == 1)[0]
if len(anomalous_indices) > 0:
    sample_idx = anomalous_indices[0]
    sample_shap = shap_values.values[sample_idx, :, 1] if len(shap_values.values.shape) == 3 else shap_values.values[sample_idx]
    top_contributors = np.argsort(np.abs(sample_shap))[::-1][:3]
    
    print(f"ALERT: Valid Anomaly Signature Detected at sample step index [{sample_idx}]!")
    for rank, feat_idx in enumerate(top_contributors, 1):
        feature_name = features_for_training[feat_idx]
        feature_value = X_test.iloc[sample_idx][feature_name]
        impact_dir = "+" if sample_shap[feat_idx] > 0 else ""
        print(f"  {rank}. {feature_name} (Value: {feature_value}) | SHAP Impact Weight: {impact_dir}{sample_shap[feat_idx]:.4f}")
else:
    print(" No anomalous instances found in evaluation subset partitions.")

joblib.dump(model, "hist_gb_personalized_model.pkl")
print("\n Model checkpoint saved as 'hist_gb_personalized_model.pkl'")

final_clean_df["Risk_Prediction"] = model.predict(X_full)
final_clean_df.to_csv("system_data_with_predictions.csv", index=False)
print(" Global data tracks successfully exported to 'system_data_with_predictions.csv'")
