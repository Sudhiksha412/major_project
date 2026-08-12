import pandas as pd 
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

df = pd.read_csv("system_data_with_anomalies.csv")

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values(by='Timestamp')

df['cpu_diff'] = df['CPU_Usage'].diff()
df['network_total'] = df['Bytes_Sent'] + df['Bytes_Recv']

df['cpu_rolling_mean'] = df['CPU_Usage'].rolling(window=5).mean()

df = df.fillna(0)

df["Status"] = df.apply(lambda row: 1 if (
    row["CPU_Usage"] > 70 or 
    row["Bytes_Sent"] > 100000 or 
    row["Bytes_Recv"] > 100000
) else 0, axis=1)

features = [
    'CPU_Usage',
    'RAM_Usage',
    'Disk_Usage',
    'Bytes_Sent',
    'Bytes_Recv',
    'cpu_diff',
    'network_total',
    'cpu_rolling_mean'
]

X = df[features]
y = df["Status"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(random_state = 42)
model.fit(X_train, y_train)

accuracy = model.score(X_test,y_test)
print("Accuracy:",accuracy)
print("Model trained successfully!")