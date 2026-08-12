import pandas as pd
import psutil
import time
import os 
from datetime import datetime

data = []

print("Collecting system data...")
prev_net = psutil.net_io_counters()

try:
    for i in range(300):
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage(os.path.abspath(os.sep)).percent
        
        net = psutil.net_io_counters()
        bytes_sent = net.bytes_sent - prev_net.bytes_sent
        bytes_recv = net.bytes_recv - prev_net.bytes_recv
        prev_net = net
        
        process_count = len(psutil.pids())
        
        battery = psutil.sensors_battery()
        battery_percent = battery.percent if battery else None
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Sample {i+1} | CPU: {cpu}% | RAM: {ram}% | Disk: {disk}% Proc:{process_count}")
        
        data.append([timestamp, cpu, ram, disk, bytes_sent,bytes_recv, process_count, battery_percent])
        
        time.sleep(2)

except KeyboardInterrupt:
    print("Data collection stopped by user.")

df = pd.DataFrame(data, columns=["Timestamp", "CPU_Usage", "RAM_Usage", "Disk_Usage", "Bytes_Sent", "Bytes_Recv", "Process_Count", "Battery_Percent"])
df.to_csv("system_data.csv", index=False)

print("Dataset saved successfully!")



