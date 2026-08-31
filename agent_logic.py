import pandas as pd 
import os

file_name = "system_data_with_anomalies.csv"
if not os.path.exists(file_name):
    print(f"Error: '{file_name}' not found! Please check your file paths.")
    exit()

df = pd.read_csv(file_name)

def resolution_agent(row):
    if row["Anomaly"] == 1:
        insights = []

        # High CPU spike
        if row["CPU_Usage"] > 75:
            insights.append("High CPU usage detected -> Suggest closing heavy background applications.")

        # Network anomaly
        if row["network_total"] > 100000:
            insights.append("Unusual network spike -> Check for large downloads or suspicious traffic.")

        # RAM anomaly
        if row["RAM_Usage"] > 80:
            insights.append("High RAM usage detected -> Suggest restarting system or clearing memory.")

        #disk anomaly
        if "Disk_Usage" in row and row["Disk_Usage"] > 85:
            insights.append("High Disk space consumption -> Suggest cleaning temp files.")

        if "cpu_diff" in row and abs(row["cpu_diff"]) > 30:
            insights.append("Sudden CPU fluctuation -> Potential process execution spike.")

        if not insights:
            return "Unusual behavioral signature detected -> System deviation anomaly requiring investigation."

        return " | ".join(insights)

    else:
        return "System operating normally."

def get_severity(row):
    if row["Anomaly"] == 0:
        return "NORMAL"

    # FIX: Guarding against KeyErrors and incorporating the absolute difference logic consistently
    cpu_spike = row["CPU_Usage"] > 75
    ram_spike = row["RAM_Usage"] > 80
    disk_spike = row.get("Disk_Usage", 0) > 85

    if cpu_spike or ram_spike or disk_spike:
        return "HIGH"
        
    elif abs(row.get("cpu_diff", 0)) > 30 or row["network_total"] > 50000:
        return "MEDIUM"
        
    else:
        return "LOW"

print("Agentic AI reasoning structures are evaluating system rows...")
df["Agent_Response"] = df.apply(resolution_agent, axis=1)
df["Severity"] = df.apply(get_severity, axis=1)

output_file = "system_with_agent_response.csv"
df.to_csv(output_file, index=False)

print("\n Agent Logic Pipeline Finished Successfully!")
print(f" Severity breakdown:\n{df['Severity'].value_counts()}")
print(f" File built and saved cleanly as '{output_file}'!")




