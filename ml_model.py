import pandas as pd 
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("system_data_with_anomalies.csv")
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values(by='Timestamp').reset_index(drop = True)

df['cpu_diff'] = df['CPU_Usage'].diff()
df['network_total'] = df['Bytes_Sent'] + df['Bytes_Recv']
df['cpu_rolling_mean'] = df['CPU_Usage'].rolling(window=5).mean()

df = df.dropna().reset_index(drop=True)

df["Current_Stress_State"] = df.apply(lambda row: 1 if (
    row["CPU_Usage"] > 70 or 
    row["Bytes_Sent"] > 100000 or 
    row["Bytes_Recv"] > 100000
) else 0, axis=1)

PREDICTION_LOOKAHEAD_STEPS = -10 
df["Future_Failure_Target"] = df["Current_Stress_State"].shift(PREDICTION_LOOKAHEAD_STEPS)

df = df.dropna().reset_index(drop=True)

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
y = df["Future_Failure_Target"].astype(int)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2 , shuffle = False)

model = RandomForestClassifier(n_estimators = 100 ,random_state = 42)
model.fit(X_train, y_train)

accuracy = model.score(X_test,y_test)
print(f"Accuracy:{accuracy * 100:.2f}%")

y_pred = model.predict(X_test)
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred))

joblib.dump(model, "rf_model.pkl")
print("Model successfully optimized and saved as 'rf_model.pkl'!")

loaded_model = joblib.load("rf_model.pkl")

df["Risk_Prediction"] = loaded_model.predict(df[features])
