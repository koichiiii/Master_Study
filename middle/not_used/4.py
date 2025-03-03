#エアコン制御、ナビゲーションマルチスレッド、清書、オブジェクト指向にする、BuildingManager追加、いらないもの削除して決定版
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
import psutil

# NUM_THREADS= 10

# 保存するファイル名とヘッダー
csv_filename1 = "aircon_multi_thread.csv"
csv_filename2 = "person_multi_thread.csv"
csv_filename3 = "cpu_proposal.csv"
csv_filename4 = "memory_proposal.csv"
csv_header = ["Timestamp"]

# app = Flask(__name__)

class All:
    def __init__(self,name):
        self.name = name

    def get_property(self,property):
        try:
            uri = f"http://192.168.100.151:8080/api/2/things/{self.name}/features/measurements/properties/{property}"
            response = requests.get(uri,auth=("owner","704lIlac"))
            data = response.json()  # 応答をJSON形式で解析
            return data
        except Exception as e:
            # print(f"Failed to get data from {url}: {e}")
            return None

    def operate_property(self,property,data):
        try:
            uri = f"http://192.168.100.151:8080/api/2/things/{self.name}/features/measurements/properties/{property}"
            response = requests.put(uri,json=data,auth=("owner","704lIlac"))
            data = response.json()  # 応答をJSON形式で解析
            return data
        except Exception as e:
            # print(f"Failed to post data from {uri}: {e}")
            return None


class Building(All):
    def __init__(self,name,temp=23):
        self.name = name
        self.floors = {}  # フロアのリスト
        self.persons = {} # 人のリスト
        self.outside_temp = temp

    # def add_floor(self, floor):
    #     self.floors.append(floor)
    def add_floor(self, floor):
        if floor.name not in self.floors:
            self.floors[floor.name] = floor

    def add_person(self, person):
        if person.name not in self.persons:
            self.persons[person.name] = person

    # def add_outside_temp(self,temp):
        # self.outside_temp = temp

    # def show_details(self):
    #     print(f"Building: {self.name}")
    #     print(f"外気温：{self.outside_temp}")
    #     for person in self.persons.values():
    #         person.show_details()
    #     for floor in self.floors.values():
    #         floor.show_details()


    # 定期的なエアコン制御を実行する関数
    # def auto_aircon_control(self):
    #     while True:
    #         start = datetime.now()
    #         print("----自動エアコン制御を開始します。")

            # threads = []
            # for floor in self.floors.values():
            #     thread = threading.Thread(target=floor.floor_control, args=(self.outside_temp,),daemon=True)
            #     threads.append(thread)
            #     thread.start()

            # # 全てのスレッドが終了するまで待機
            # for thread in threads:
            #     thread.join()

            # end = datetime.now()
            # elapsed_time = end -start
            # save_time_to_csv(elapsed_time, csv_filename1)
            # print(f"----自動エアコン制御を終了します。{elapsed_time}  を {csv_filename1} に保存しました。\n")

            # time.sleep(10)  # 5分（300秒）



    # def find_device(self, room_id, device_type):
    #     print("aaa")

    def __getattr__(self, item):
        return self.floors[item] if item in self.floors else None
        return self.persons[item] if item in self.persons else None


class Move_Object(All):
    def __init__(self, current_position=None, current_room=None):
        """
        Move_Objectクラスの初期化メソッド
        :param current_position: 現在の座標 (x, y, z) のタプル
        :param current_room: 現在の部屋の名前 (文字列)
        """
        self.current_position = current_position  # 現在の位置
        self.current_room = current_room  # 現在の部屋

    # def update_position(self, new_position):
    #     """
    #     現在の位置を更新する
    #     :param new_position: 新しい座標 (x, y, z) のタプル
    #     """
    #     self.current_position = new_position
    #     print(f"Position updated to {self.current_position}")

    def update_room(self, new_room):
        """
        現在の部屋を更新する
        :param new_room: 新しい部屋の名前 (文字列)
        """
        self.current_room = new_room
        # print(f"Room updated to {self.current_room.name}")

    # def show_details(self):
    #     """
    #     現在の位置と部屋を取得する
    #     :return: 現在の位置と部屋を含む辞書
    #     """
    #     return {
    #         "現在位置": self.current_position,
    #         "現在部屋": self.current_room.name
    #     }


class Person(Move_Object):
    def __init__(self, name,comfort_temp, current_position=None, current_room=None):
        """
        Personクラスの初期化メソッド
        :param name: 名前 (文字列)
        :param current_position: 現在の座標 (x, y, z) のタプル (親クラスから継承)
        :param current_room: 現在の部屋の名前 (文字列) (親クラスから継承)
        """
        super().__init__(current_position, current_room)  # 親クラスの初期化を呼び出し
        self.name = name  # 名前
        self.comfort_temp = comfort_temp

    # def show_details(self):
    #     print(f"  Person: {self.name},{self.comfort_temp}")
    #     print(super().show_details())

class Floor(All):
    def __init__(self, name):
        self.name = name
        self.rooms = {}  # 部屋のリスト

    def add_room(self, room):
        if room.name not in self.rooms:
            self.rooms[room.name] = room

    def floor_control(self, outside_temp):
        for room in self.rooms.values():
            room.room_control(outside_temp)

    # def show_details(self):
    #     print(f"  Floor: {self.name}")
    #     for room in self.rooms.values():
    #         room.show_details()
            

    def __getattr__(self, item):
        return self.rooms[item] if item in self.rooms else None

class Room(All):
    def __init__(self, name, temp_map=None):
        self.name = name
        self.aircons = {}  # エアコンのリスト
        self.temp_map = temp_map
        self.persons = {}

    def add_aircon(self, aircon):
        if aircon.name not in self.aircons:
            self.aircons[aircon.name] = aircon

    def add_tempmap(self, temp_map):
        self.temp_map = temp_map

    def add_person(self, person):
        if person.name not in self.persons:
            self.persons[person.name] = person
    
    def room_control(self,outside_temp):
        #部屋の中の人の個人の快適な温度の平均値をとりその温度になるようにエアコンを制御する
        #したがって、必要な入力情報は、その部屋のエアコンの設定温度、その部屋にいる人の快適温度リスト、現在の室温(過去も入れてもいい)、外気温、かな
        #出力は(エアコンオブジェクト、設定温度)のリスト
        aircon_temp = self.calculate_temperature(outside_temp)
        #エアコンのループ
        for aircon, temp in aircon_temp:
            aircon.operate_property("temperature",temp)
        self.operate_property("set_temp",aircon_temp[0][1])


    #エアコンと、その最適な設定温度を返す
    def calculate_temperature(self, outside_temp):
        list = []
        sum = 0
        ave = 0
        cnt = 0

        for aircon in self.aircons.values():
            temp = aircon.get_property("temperature")

        tmap = self.temp_map.get_property("temperature")

        for person in self.persons.values():
            temp = person.get_property("comfort_temp")
            # print(temp)
            sum = sum + temp
            cnt = cnt + 1
            # print(temp)

        if cnt != 0:
            ave = sum / cnt
        else:
            ave = 0
        ave = round(ave,1)

        for aircon in self.aircons.values():
            list.append((aircon,ave))

        return list

    # def show_details(self):
    #     print(f"    Room: {self.name}")
    #     for aircon in self.aircons.values():
    #         # print(f"  {aircon.name}: {aircon.temperature}°C")
    #         aircon.show_details()
    #     for person in self.persons.values():
    #         print(person.name)
    #     print("      "+ self.temp_map.name)

    def __getattr__(self, item):
        return self.aircons[item] if item in self.aircons else None
        return self.persons[item] if item in self.persons else None



class Aircon(All):
    def __init__(self, name, temperature=24):
        self.name = name
        self.temperature = temperature

    def control(self,temp):
        self.temperature = temp
        print(f"{self.name}: Air conditioner temperature set to "+ str(temp) + "°C\n")

    # def show_details(self):
    #     print(f"      Aircon: {self.name}")
    #     print(f"        {self.name}: {self.temperature}°C")

class TempMap(All):
    def __init__(self, name):
        self.name = name
        self.temperature = []

    # def get_temperature(self,x,y,z):
    #     return self.temperature[x][y][z]

    # def show_details(self):
    #     print(f"      Temp_map: {self.name}")
    #     print(f"        {self.name}: {self.temperature}")

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

class BuildingManager():
    def __init__(self, building):
        self.building = building
    
    def auto_aircon_control(self):
        while True:
            start = datetime.now()
            print("----自動エアコン制御を開始します。")

            threads = []
            for floor in self.building.floors.values():
                thread = threading.Thread(target=floor.floor_control, args=(self.building.outside_temp,),daemon=True)
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

    # ナビゲーション関数
    def navigate(self):
        while True:
            #リクエストがあったユーザにとって最適な場所を提案する
            #一人ずつ、快適温度から離れた位置にいる場合、温度マップと個人の快適な温度から適切な部屋、ポジションを出力する
            print("--ナビゲーションを開始します")
            start = datetime.now()
            random_number = random.randint(0, 9999)
            person = self.building.persons[f"Building:person{random_number}"]
            ctemp = person.get_property("comfort_temp")
            rtemp = person.current_room.get_property("set_temp")
            # print(ctemp)
            # print("aaa")
            diff = round(abs(ctemp - rtemp),1)
            comfort_position = [[person.current_room.name,diff]]

            if diff >= 1:
                temp_queue = Queue()  # キューを作成 (スレッドセーフ)
                threads = []
                for floor in self.building.floors.values():
                    thread = threading.Thread(target=get_navigation, args=(floor,temp_queue),daemon=True)
                    threads.append(thread)
                    thread.start()

                # 全てのスレッドが終了するまで待機
                for thread in threads:
                    thread.join()

                # 結果の収集
                temp_list = []
                while not temp_queue.empty():
                    temp_list.append(temp_queue.get())

                for temp in temp_list:
                    difference = round(abs(temp[1] - ctemp),1)
                    if difference == comfort_position[-1][-1]:
                        comfort_position.append([temp[0].name,difference])
                    elif difference < comfort_position[-1][-1]:
                        comfort_position =  [[temp[0].name,difference]]
                print(f"{person.name}は {comfort_position}が最適な環境です")
            else:
                print(f"{person.name}は移動する必要はありません")

            end = datetime.now()
            elapsed_time = end -start
            save_time_to_csv(elapsed_time, csv_filename2)
            print(f"--ナビゲーションを終了します。{elapsed_time}  を {csv_filename2} に保存しました。\n")
            time.sleep(10)

def get_navigation(floor,queue):
    for room in floor.rooms.values():
        temp = room.get_property("set_temp")
        queue.put([room,temp])  # 結果をキューに格納

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
    building0 = Building("Building:building0")

    floor_list =[]
    for i in range(0, 10):  # 1から10までのループ
        floor_list.append(Floor(f"Building:floor{i}"))
        building0.add_floor(floor_list[i])

    room_list = []
    for i, floor in enumerate(floor_list):  # floor_listをインデックス付きでループ
        for j in range(100):  # 0から99までのループ
            room_number = i * 100 + j
            room = Room(f"Building:room{room_number}")
            room_list.append(room)
            floor.add_room(room)

    temp_map_list = []
    aircon_list = []
    for num, room in enumerate(room_list):  # room_listをインデックス付きでループ
        temp_map = TempMap(f"Building:temp_map{num}")
        aircon = Aircon(f"Building:airon{num}")
        
        temp_map_list.append(temp_map)
        aircon_list.append(aircon)
        
        room.add_tempmap(temp_map)
        room.add_aircon(aircon)


    person_list = []
    for i in range(0, 10000):  # 1から10までのループ
        person_list.append(Person(f"Building:person{i}",25))
        building0.add_person(person_list[i])

    for person in person_list:
        random_number = random.randint(0, 999)
        person.update_room(room_list[random_number])
        room_list[random_number].add_person(person)

    manager = BuildingManager(building0)
    threads = []
    thread1 = threading.Thread(target=manager.auto_aircon_control, args=(),daemon=True)
    thread2 = threading.Thread(target=manager.navigate, args=(),daemon=True)
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