import pandas as pd 

df = pd.read_csv("system_with_agent_response.csv")

log_file = "system_logs.txt"

with open(log_file,"a") as file:
    file.write("\n=== SYSTEM ANOMALY LOG REPORT ===\n\n")

    anomaly_count = 0

    for index, row in df.iterrows():

        if row["Anomaly"] == 1 and (row["CPU_Usage"] > 40 or row["Bytes_Sent"] > 50000 or row["Bytes_Recv"] > 50000):
            anomaly_count += 1


        def get_severity(row):
            if row["CPU_Usage"] > 70 or row["Bytes_Recv"] > 200000:
                 severity = "HIGH"
            elif row["CPU_Usage"] > 40:
                 severity = "MEDIUM"
            else:
                severity = "LOW"

            Severity = get_severity(row)

            log_entry = (
                f"Time: {row['Timestamp']}\n"
                f"Severity: {severity}\n"
                f"CPU: {row['CPU_Usage']}%\n"
                f"RAM: {row['RAM_Usage']}%\n"
                f"Disk: {row['Disk_Usage']}%\n"
                f"Processes: {row['Process_Count']}\n"
                f"Network: {row['network_total']}\n"
                f"{'-'*50}\n"
            )

            file.write(log_entry)
    file.write("\n SUMMARY \n")
    file.write(f"Total anomalies detected: {anomaly_count}\n")

print("Logging system excuted successfully!")
print("Check system_logs.txt")