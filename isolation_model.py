import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

df = pd.read_csv("system_data.csv")
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values(by='Timestamp').reset_index(drop=True)

df['cpu_diff'] = df['CPU_Usage'].diff().fillna(0)
df['network_total'] = df['Bytes_Sent'] + df['Bytes_Recv']
df['cpu_rolling_mean'] = df['CPU_Usage'].rolling(window=5,min_periods = 1).mean()

df = df.dropna().reset_index(drop = True)

features = [
    'CPU_Usage',
    'RAM_Usage',
    'Disk_Usage',
    'Process_Count',
    'Bytes_Sent',
    'Bytes_Recv',
    'cpu_diff',
    'network_total',
    'cpu_rolling_mean'
]

X = df[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(contamination = 0.05,random_state = 42)
model.fit(X_scaled)

raw_predictions = model.predict(X_scaled)


df["Anomaly"] = [1 if pred == -1 else 0 for pred in raw_predictions]

joblib.dump(scaler, "scaler.pkl")
joblib.dump(model, "isolation_forest_model.pkl")

df.to_csv("system_data_with_anomalies.csv", index = False)

print("Isolation Forest model trained successfully!")
print(f"Total Samples Analyzed: {len(df)}")
print(f"Anomalies detected: {df['Anomaly'].sum()}")

if df["Anomaly"].sum() > 0:
    print("\n Snippet of Detected Anomalies:")
    print(df[df["Anomaly"] == 1][["Timestamp", "CPU_Usage", "RAM_Usage", "Anomaly"]].head(5))