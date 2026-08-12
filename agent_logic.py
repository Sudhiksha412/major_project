import pandas as pd 

df = pd.read_csv("system_data_with_anomalies.csv")

def resolution_agent(row):
    if row["Anomaly"] == 1:

        # High CPU spike
        if row["CPU_Usage"] > 60:
            return "High CPU spike detected -> Possible heavy process or malware."

        # Network anomaly
        elif row["network_total"] > 100000:
            return "Unusual network spike -> Check for large downloads or suspicious traffic."

        # RAM anomaly
        elif row["RAM_Usage"] > 75:
            return "High RAM usage -> Possible memory leak or too many applications."

        # Sudden CPU change
        elif abs(row["cpu_diff"]) > 30:
            return "Sudden CPU fluctuation detected -> System instability possible."

        else:
            return "Unknown anomaly -> Requires deeper analysis."

    return "System operating normally."
    
df["Agent_Response"] = df.apply(resolution_agent, axis=1)

df.to_csv("system_with_agent_response.csv", index = False)

print("Agent logic applied successfully!")
print("Check system_with_agent_response.csv")


