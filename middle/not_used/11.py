# 従来のやつ
from flask import Flask, request, jsonify
import threading
import time
from datetime import datetime
import random
import numpy as np
import requests
import time
import csv
from queue import Queue
from collections import defaultdict
import psutil

NUM_ROOMS = 1000
# 保存するファイル名とヘッダー
csv_filename1 = "aircon_conventional.csv"
csv_filename2 = "person_conventional.csv"
csv_filename3 = "cpu_conventional.csv"
csv_filename4 = "memory_conventional.csv"
csv_header = ["Timestamp"]

# SPARQLエンドポイントのURL
SPARQL_ENDPOINT = "http://192.168.100.151:3030/sparql"

def get_object(query):
    """
    SPARQLクエリを実行して結果を取得する
    """
    headers = {
        "Accept": "application/sparql-results+json"
    }
    response = requests.post(SPARQL_ENDPOINT, data={"query": query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"SPARQL query failed: {response.status_code}")
        return None
    
def get_property(name,property):
        try:
            uri = f"http://192.168.100.151:8080/api/2/things/{name}/features/measurements/properties/{property}"
            response = requests.get(uri,auth=("owner","704lIlac"))
            data = response.json()  # 応答をJSON形式で解析
            return data
        except Exception as e:
            # print(f"Failed to get data from {url}: {e}")
            return None

def auto_aircon_control():
    global NUM_ROOMS
    while True:
        start = datetime.now()
        print("----自動エアコン制御を開始します。")

        results = generate_auto_aircon_control()
        # output(results)
        results2 = group_by_room(results)
        # output(results2)

        threads = []
        for i in range(10):
            list = []
            for j in range(int(NUM_ROOMS/10)):
                list.append(results2[int(i*NUM_ROOMS/10)+j])
                # print(int(i*NUM_ROOMS/10)+j)
            # print(list[0][1])
            thread = threading.Thread(target=room_aircon_control, args=(list,),daemon=True)
            threads.append(thread)
            thread.start()

        # 全てのスレッドが終了するまで待機
        for thread in threads:
            thread.join()

        end = datetime.now()
        elapsed_time = end -start
        save_time_to_csv(elapsed_time, csv_filename1)
        print(f"----自動エアコン制御を終了します。{elapsed_time}  を {csv_filename1} に保存しました。\n")

        time.sleep(10)  # 5分（300秒）

            
def navigate():
    while True:
        #リクエストがあったユーザにとって最適な場所を提案する
        #一人ずつ、快適温度から離れた位置にいる場合、温度マップと個人の快適な温度から適切な部屋、ポジションを出力する
        print("--ナビゲーションを開始します")
        start = datetime.now()
        random_number = random.randint(0, 9999)
        person = f"Building:person{random_number}"
        ctemp = get_property(person,"comfort_temp")
        # 本当はSPARQLクエリ
        room = "Building:room10"
        rtemp = get_property(room,"set_temp")
        # print(ctemp)
        # print(rtemp)

        diff = round(abs(ctemp - rtemp),1)
        comfort_position = [[room,diff]]

        if diff >= 1:
            temp_queue = Queue()  # キューを作成 (スレッドセーフ)
            threads = []
            
            for i in range(10):
                room_list =[]
                for j in range(int(NUM_ROOMS/10)):
                    room_list.append(f"Building:room{i*100+j}")

                thread = threading.Thread(target=get_navigation, args=(room_list,temp_queue),daemon=True)
                threads.append(thread)
                thread.start()

            # 全てのスレッドが終了するまで待機
            for thread in threads:
                thread.join()

            # 結果の収集
            temp_list = []
            while not temp_queue.empty():
                temp_list.append(temp_queue.get())

            # print(temp_list)

            for temp in temp_list:
                difference = round(abs(temp[1] - ctemp),1)
                if difference == comfort_position[-1][-1]:
                    comfort_position.append([temp[0],difference])
                elif difference < comfort_position[-1][-1]:
                    comfort_position =  [[temp[0],difference]]
            print(f"{person}は {comfort_position}が最適な環境です")
        else:
            print(f"{person}は移動する必要はありません")

        end = datetime.now()
        elapsed_time = end -start
        save_time_to_csv(elapsed_time, csv_filename2)
        print(f"--ナビゲーションを終了します。{elapsed_time}  を {csv_filename2} に保存しました。\n")
        time.sleep(10)

def get_navigation(room_list,queue):
    for room in room_list:
        temp = get_property(room,"set_temp")
        queue.put([room,temp])  # 結果をキューに格納

def room_aircon_control(list):
    # aircon = list[3]
    # print(aircon)
    ditto_list = get_ditto_property(list)
    # output(comfort_list)
    # print(ditto_list)
    # cnt = 0
    for room_data in ditto_list:
        aircon_temp = calculate_temperature(room_data)
        # cnt = cnt + 1
        # print(aircon_temp)
        operate_property(room_data[0],"temperature",room_data[1])
    # print(cnt)
    for i in range(100):
        operate_property(ditto_list[0],"set_temp",23)
    

        
def operate_property(object,property,data):
        try:
            uri = f"http://192.168.100.151:8080/api/2/things/{object}/features/measurements/properties/{property}"
            response = requests.put(uri,json=data,auth=("owner","704lIlac"))
            data = response.json()  # 応答をJSON形式で解析
            return data
        except Exception as e:
            # print(f"Failed to post data from {uri}: {e}")
            return None

def calculate_temperature(list):
    sum=0
    cnt=0
    ave=0
    for ctemp in list[2]:
        # print(ctemp)
        sum = sum + ctemp
        cnt = cnt + 1
        
    if cnt ==0:
        ave=0
    else:
        ave = sum / cnt
    ave = round(ave,1)
 
    aircon = list[1]
    resuls = [aircon[0],ave]
    # print(resuls)
    return resuls







def get_ditto_property(list):
    results = []
    for data in list:
        tmp = []
        room = get_property(data[1],"set_temp")
        aircon = get_property(data[3],"temperature")
        for person in data[4]:
            comfort_temp = get_property(person,"comfort_temp")
            # print(comfort_temp)
            tmp.append(comfort_temp)
        # print(results)
        results.append([[data[1],room],[data[3],aircon],tmp])
    return results





def group_by_room(list):
    results = []

    for i in range(0,int(len(list) / 10)):
        tmp = []
        tmp.append(list[i][0])
        tmp.append(list[i*10][1])
        tmp.append(list[i*10][2])
        tmp.append(list[i*10][3])
        person= []
        for j in range(0,10):
            person.append(list[i*10+j][4])
        tmp.append(person)
        results.append(tmp)

    return results


def output(results):
    # for result in range(100):
    #     print(results[result])
    i = 0
    for result in results:
        i = i+ 1
        print(result)
    print(i)

# CSVファイルに時間を保存する関数
def save_time_to_csv(timestamp, filename):
    # ファイルが存在するかチェック
    try:
        with open(filename, mode='x', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(csv_header)  # ヘッダーを追加
            writer.writerow([timestamp])  # 時刻を追加
    except FileExistsError:
        # 既存ファイルに追記
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp])

def generate_auto_aircon_control():
    # フロア数、部屋数（1フロアあたり）、エアコン数（1部屋あたり）、総人数
    NUM_FLOORS = 10
    global NUM_ROOMS
    NUM_ROOMS_PER_FLOOR = NUM_ROOMS // NUM_FLOORS
    NUM_PEOPLE_PER_ROOM = 10
    NUM_PEOPLE = NUM_ROOMS * NUM_PEOPLE_PER_ROOM
    
    # 各部屋に関連するデータを格納するリスト
    result_list = []
    cnt = 0
    # フロアと部屋、エアコン、温度マップのデータ生成
    for floor in range(0, NUM_FLOORS):  # 1から10までのループ
        for room in range(0,NUM_ROOMS_PER_FLOOR):
            floor_id = f"Building:floor{floor}"
            room_id = f"Building:room{floor*NUM_ROOMS_PER_FLOOR+room}"
            tempmap_id=f"Building:temp_map{floor*NUM_ROOMS_PER_FLOOR+room}"
            aircon_id = f"Building:airon{floor*NUM_ROOMS_PER_FLOOR+room}"
            for person in range(0,NUM_PEOPLE_PER_ROOM):
                person_id = f"Building:person{(floor*NUM_ROOMS_PER_FLOOR+room)*NUM_PEOPLE_PER_ROOM+person}"
                result_list.append([floor_id,room_id,tempmap_id,aircon_id,person_id])
                cnt = cnt +1
            # result_list.append([floor_id,room_id,tempmap_id,aircon_id,person_id])
    # output(result_list)
    # print(cnt)
    return result_list

def stop():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)  # interval=1秒ごとに測定
        # print(f"CPU使用率: {cpu_usage}%")
        memory = psutil.virtual_memory()
        memory_used = f"{memory.used / (1024 ** 3):.2f}"
        save_time_to_csv(cpu_usage, csv_filename3)
        save_time_to_csv(memory_used, csv_filename4)

        # print(f"メモリ使用率: {memory.percent}%")
        # print(f"使用中のメモリ: {memory.used / (1024 ** 3):.2f} GB")
        # print(f"総メモリ: {memory.total / (1024 ** 3):.2f} GB")
        time.sleep(10)

def main():
    threads = []
    thread1 = threading.Thread(target=auto_aircon_control, args=(),daemon=True)
    thread2 = threading.Thread(target=navigate, args=(),daemon=True)
    threads.append(thread1)
    threads.append(thread2)
    thread1.start()
    thread2.start()
 
    stop()
    
    # 全てのスレッドが終了するまで待機
    for thread in threads:
        thread.join()



if __name__ == '__main__':
    main()

