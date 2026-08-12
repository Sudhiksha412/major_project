import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("system_data.csv")
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values(by='Timestamp')

df['cpu_diff'] = df['CPU_Usage'].diff()
df['network_total'] = df['Bytes_Sent'] + df['Bytes_Recv']

df['cpu_rolling_mean'] = df['CPU_Usage'].rolling(window=5).mean()

df = df.fillna(0)

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

df["Anomaly"] = model.predict(X_scaled)

df["Anomaly"] = df["Anomaly"].map({1: 0, -1: 1})
df.to_csv("system_data_with_anomalies.csv", index = False)

print("Isolation Forest model trained successfully!")
print("Anomalies detected:", df["Anomaly"].sum())
