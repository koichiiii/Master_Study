import psutil
import time
import statistics

# データを格納するリスト
cpu_usage = []
memory_usage = []

# 100秒間データ収集
for _ in range(100):
    cpu = psutil.cpu_percent(interval=1)  # CPU使用率（1秒間隔）
    memory = psutil.virtual_memory().percent  # メモリ使用率
    
    cpu_usage.append(cpu)
    memory_usage.append(memory)

# 統計データの算出
cpu_avg = statistics.mean(cpu_usage)
cpu_max = max(cpu_usage)
cpu_min = min(cpu_usage)

memory_avg = statistics.mean(memory_usage)
memory_max = max(memory_usage)
memory_min = min(memory_usage)

# 結果の出力
print(f"CPU Usage: Avg={cpu_avg:.2f}%, Max={cpu_max:.2f}%, Min={cpu_min:.2f}%")
print(f"Memory Usage: Avg={memory_avg:.2f}%, Max={memory_max:.2f}%, Min={memory_min:.2f}%")
