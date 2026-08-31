import pandas as pd 
import os

try:
    df = pd.read_csv("system_with_agent_response.csv")
except FileNotFoundError:
    print("Error: 'system_with_agent_response.csv' not found. Please run your pipeline first.")
    exit()

log_file = "system_logs.txt"

def determine_severity(row):
    if row["CPU_Usage"] > 70 or row["Bytes_Recv"] > 200000:
        return "HIGH"
    elif row["CPU_Usage"] > 40:
        return "MEDIUM"
    else:
        return "LOW"

print("Processing system data and writing to logs...")
with open(log_file,"a") as file:
    file.write("\n=== SYSTEM ANOMALY LOG REPORT ({pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n\n")

    anomaly_count = 0

    for index, row in df.iterrows():

        if row["Anomaly"] == 1 and (row["CPU_Usage"] > 40 or row["Bytes_Sent"] > 50000 or row["Bytes_Recv"] > 50000):
            anomaly_count += 1

            severity_status = determine_severity(row)

            log_entry = (
                f"Time: {row['Timestamp']}\n"
                f"Severity: {severity_status}\n"
                f"CPU: {row['CPU_Usage']}%\n"
                f"RAM: {row['RAM_Usage']}%\n"
                f"Disk: {row['Disk_Usage']}%\n"
                f"Processes: {int(row['Process_Count']) if 'Process_Count' in row else 'N/A'}\n"
                f"Network Total: {row['network_total']} Bytes\n"
                f"{'-'*50}\n"
            )
            file.write(log_entry)
            
    file.write("\n REPORT SUMMARY \n")
    file.write(f"Total critical anomalies recorded in this session: {anomaly_count}\n")
    file.write(f"{'='*50}\n\n")

print("✅ Logging system executed successfully!")
print(f"📂 Open up '{log_file}' in your VS Code workspace to check your results.")
       