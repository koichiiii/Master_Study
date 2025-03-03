import psutil
import time

while True:
    # CPU使用率の取得（全コアの平均）
    cpu_usage = psutil.cpu_percent(interval=1)  # interval=1秒ごとに測定
    print(f"CPU使用率: {cpu_usage}%")

    # メモリ使用率の取得
    memory = psutil.virtual_memory()
    print(f"メモリ使用率: {memory.percent}%")
    print(f"使用中のメモリ: {memory.used / (1024 ** 3):.2f} GB")
    print(f"総メモリ: {memory.total / (1024 ** 3):.2f} GB")

    time.sleep(10)
