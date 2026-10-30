import pandas as pd
import psutil
import time
import os
from datetime import datetime
data = []
print("Starting System Data Collection...")
print("TIP: Press 'Ctrl + C' anytime to save and exit.")
print("TIP: If you are running a heavy app/stress test right now, remember the sample numbers to label them later!\n")

prev_net = psutil.net_io_counters()
psutil.cpu_percent(interval=None)

TOTAL_SAMPLES = 1000
SLEEP_INTERVAL = 2.0 

try:
    for i in range(TOTAL_SAMPLES):
        start_time = time.time()

        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage(os.path.abspath(os.sep)).percent
        
        net = psutil.net_io_counters()
        bytes_sent = max(0 ,net.bytes_sent - prev_net.bytes_sent)
        bytes_recv = max(0,net.bytes_recv - prev_net.bytes_recv)
        prev_net = net
        
        process_count = len(psutil.pids())
        
        battery = psutil.sensors_battery()
        battery_percent = battery.percent if battery else None
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        failure_label = 0
        
        print(f"Sample {i+1}/{TOTAL_SAMPLES} | CPU: {cpu}% | RAM: {ram}% | Disk: {disk}% Proc:{process_count} | Label :{failure_label}")
        
        data.append([timestamp, cpu, ram, disk, bytes_sent,bytes_recv, process_count, battery_percent,failure_label])
        elapsed_time = time.time() - start_time
        time.sleep(max(0.1, SLEEP_INTERVAL - elapsed_time))

except KeyboardInterrupt:
    print("Data collection stopped by user.")

if data:
    df = pd.DataFrame(data, columns=[
        "Timestamp", "CPU_Usage", "RAM_Usage", "Disk_Usage", 
        "Bytes_Sent", "Bytes_Recv", "Process_Count", "Battery_Percent", "Failure_Label"
    ])
    df.to_csv("system_data.csv", index=False)
    print(f" Dataset saved successfully! Total samples collected: {len(df)}")
else:
    print("No data collected. File not saved.")



