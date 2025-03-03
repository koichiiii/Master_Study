#エアコン制御シングルスレッド

from flask import Flask, request, jsonify
import threading
import time
from datetime import datetime
import random
import numpy as np
import requests
import time
import csv

NUM_THREADS= 10

# 保存するファイル名とヘッダー
csv_filename = "time_log_aircon.csv"
csv_header = ["Timestamp"]

app = Flask(__name__)

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
            print(f"Failed to get data from {url}: {e}")
            return None

    def operate_property(self,property,data):
        try:
            uri = f"http://192.168.100.151:8080/api/2/things/{self.name}/features/measurements/properties/{property}"
            response = requests.put(uri,json=data,auth=("owner","704lIlac"))
            data = response.json()  # 応答をJSON形式で解析
            return data
        except Exception as e:
            print(f"Failed to post data from {uri}: {e}")
            return None


class Building(All):
    
    # def initBuilding(self, id, pass):
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

    def add_outside_temp(self,temp):
        self.outside_temp = outside_temp

    def show_details(self):
        print(f"Building: {self.name}")
        print(f"外気温：{self.outside_temp}")
        for person in self.persons.values():
            person.show_details()
        for floor in self.floors.values():
            floor.show_details()
            # print(f"  {aircon.name}: {aircon.temperature}°C")
        


    def find_device(self, room_id, device_type):
        print("aaa")

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

    def update_position(self, new_position):
        """
        現在の位置を更新する
        :param new_position: 新しい座標 (x, y, z) のタプル
        """
        self.current_position = new_position
        print(f"Position updated to {self.current_position}")

    def update_room(self, new_room):
        """
        現在の部屋を更新する
        :param new_room: 新しい部屋の名前 (文字列)
        """
        self.current_room = new_room
        # print(f"Room updated to {self.current_room.name}")

    def show_details(self):
        """
        現在の位置と部屋を取得する
        :return: 現在の位置と部屋を含む辞書
        """
        return {
            "現在位置": self.current_position,
            "現在部屋": self.current_room.name
        }


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

    # def __init__(self, name, temp):
    #     self.name = name
    #     self.comfort_temp = temp
    #     self.current_position = {}

    # def add_position(self, position):
    #     if position.name not in self.position:
    #         self.position = {}
    #         self.position[position.name] = position

    def show_details(self):
        print(f"  Person: {self.name},{self.comfort_temp}")
        print(super().show_details())
        # for position in self.position.values():
        #     position.show_details()


# class Position:
#     def __init__(self, name, position=[2,2,2]):
#         self.name = name
#         self.position = position

#     def show_details(self):
#         # print(f"Aircon: {self.name}")
#         print(f"    {self.name}: {self.position}")


    
class Floor(All):
    def __init__(self, name):
        self.name = name
        self.rooms = {}  # 部屋のリスト

    # def add_room(self, room):
    #     self.rooms.append(room)
    def add_room(self, room):
        if room.name not in self.rooms:
            self.rooms[room.name] = room

    def show_details(self):
        print(f"  Floor: {self.name}")
        for room in self.rooms.values():
            room.show_details()
            # print(f"  {aircon.name}: {aircon.temperature}°C")
    
    def __getattr__(self, item):
        return self.rooms[item] if item in self.rooms else None

class Room(All):
    def __init__(self, name, temp_map=None):
        self.name = name
        self.aircons = {}  # エアコンのリスト
        self.temp_map = temp_map
        self.persons = {}

    # def add_aircon(self, aircon):
    #     self.aircons.append(aircon)
    def add_aircon(self, aircon):
        if aircon.name not in self.aircons:
            self.aircons[aircon.name] = aircon

    def add_tempmap(self, temp_map):    
        self.temp_map = temp_map

    def add_person(self, person):    
        if person.name not in self.persons:
            self.persons[person.name] = person

    def show_details(self):
        print(f"    Room: {self.name}")
        for aircon in self.aircons.values():
            # print(f"  {aircon.name}: {aircon.temperature}°C")
            aircon.show_details()
        for person in self.persons.values():
            print(person.name)
        print("      "+ self.temp_map.name)
    
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
    
    def show_details(self):
        print(f"      Aircon: {self.name}")
        print(f"        {self.name}: {self.temperature}°C")

class TempMap(All):
    def __init__(self, name):
        self.name = name
        self.temperature = [
            [
                [20, 21, 19],  # x=0, y=0, z=0,1,2 の温度
                [22, 23, 22],  # x=0, y=1, z=0,1,2 の温度
                [24, 25, 23]   # x=0, y=2, z=0,1,2 の温度
            ],
            [
                [21, 22, 20],  # x=1, y=0, z=0,1,2 の温度
                [23, 21, 23],  # x=1, y=1, z=0,1,2 の温度
                [26, 27, 24]   # x=1, y=2, z=0,1,2 の温度
            ],
            [
                [22, 23, 21],  # x=2, y=0, z=0,1,2 の温度
                [24, 25, 24],  # x=2, y=1, z=0,1,2 の温度
                [27, 28, 26]   # x=2, y=2, z=0,1,2 の温度
            ]
        ]

    def get_temperature(self,x,y,z):
        return self.temperature[x][y][z]

    def show_details(self):
        print(f"      Temp_map: {self.name}")
        print(f"        {self.name}: {self.temperature}")

# CSVファイルに時間を保存する関数
def save_time_to_csv(timestamp, filename):
    # ファイルが存在するかチェック
    try:
        with open(filename, mode='x', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(csv_header)  # ヘッダーを追加
            writer.writerow([timestamp])  # 現在時刻を追加
    except FileExistsError:
        # 既存ファイルに追記
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp])


#エアコンと、その最適な設定温度を返す
def calculate_temperature(aircons,temp_map,persons,outside_temp):
    list = []
    sum = 0
    ave = 0
    cnt = 0

    atemp = []
    for aircon in aircons.values():
        temp = aircon.get_property("temperature")
        print(f"取得した{aircon.name}の温度は{temp}")
        atemp.append(aircon)
        atemp.append(temp)

    
    tmap = temp_map.get_property("temperature")
    print(f"取得した温度マップは{temp}")
    # ctemp = []
    for person in persons.values():
        temp = person.get_property("comfort_temp")
        print(f"取得したcomfort_tempは{temp}")
        sum = sum + temp
        cnt = cnt + 1
        

    if cnt != 0:
        ave = sum / cnt
    print(f"comfortの平均は{ave}")
    for aircon in aircons.values():
        list.append((aircon,ave))

    return list




# 定期的なエアコン制御を実行する関数
def auto_aircon_control(building):
    elapsed_time = []
    request_time = []
    while True:
        #こんな使い方ができるよ、サンプル
        # for room in building.floor1.rooms.values():
        #     print(room)
        # print(building.floors["floor1"].rooms["room1"])
        # print(building.floor1.room1.name)

        start = datetime.now()
        print("自動エアコン制御を開始します。\n")    

        for floor in building.floors.values():
            for room in floor.rooms.values():
                #部屋の中の人の個人の快適な温度の平均値をとりその温度になるようにエアコンを制御する
                #したがって、必要な入力情報は、その部屋のエアコンの設定温度、その部屋にいる人の快適温度リスト、現在の室温(過去も入れてもいい)、外気温、かな
                #出力は(エアコンオブジェクト、設定温度)のリスト 

                aircon_temp = calculate_temperature(room.aircons,room.temp_map, room.persons ,building.outside_temp)
                
                #エアコンのループ    
                for aircon, temp in aircon_temp:
                    # aircon.control(temp)
                    aircon.operate_property("temperature",temp)
                
        end = datetime.now()
        print("自動エアコン制御を終了します。\n")
        elapsed_time.append(end - start)
        save_time_to_csv(end-start, csv_filename)
        print(f"時間  を {csv_filename} に保存しました。")
        if(len(elapsed_time)==100):

            print(elapsed_time)
            print(request_time)
            return
        # print(f"{elapsed_time}かかりました")

        time.sleep(10)  # 5分（300秒）


#最適なポジションを探して、その座標を返す
# def search_best_position(room,comfort_temp):
#     position = []

    # for floor in building.floors.values():
    #     for room in floor.rooms.values():
    #         array = np.array(room.temp_map.temperature)
    #         differences = np.abs(array - comfort_temp)
    #         min_difference = np.min(differences)
    #         closest_indices = np.argwhere(differences == min_difference)
    #         position = position + [room.name,closest_indices]

#     return position

# ナビゲーション関数
def navigate(building):
    while True:
        #一人ずつ、快適温度から離れた位置にいる場合、温度マップと個人の快適な温度から適切な部屋、ポジションを出力する
        for person in building.persons.values():
            comfort_position = []
            if abs(person.comfort_temp - person.current_room.temp_map.get_temperature(1,1,1)) >= 2:
                for floor in building.floors.values():
                    for room in floor.rooms.values():
                        array = np.array(room.temp_map.temperature)
                        differences = np.abs(array - person.comfort_temp)
                        min_difference = np.min(differences)
                        closest_indices = np.argwhere(differences == min_difference)
                        comfort_position = comfort_position + [room.name,closest_indices]
                        # comfort_position = search_best_position(room,person.comfort_temp)
                # comfort_position = search_best_position(building,person.comfort_temp)
                print(f"{person.name}は {comfort_position}が最適な環境です\n")

        time.sleep(15)


def main():

    #インスタンス生成
    # building = Building("shimonishi_building")

    # floor1 = Floor("floor1")
    # room1 = Room("room1")
    # room2 = Room("room2")
    # aircon1 = Aircon("aircon1")
    # aircon2 = Aircon("aircon2")

    # person1 = Person("user1",24,[2,3,2],room1)
    # person2 = Person("user2",26,[2,2,2],room1)
    # # position1 = Position("position1")
    # # position2 = Position("position2")

    # temp_map1 = TempMap("temp_map1")
    # temp_map2 = TempMap("temp_map2")

    # #階層化
    # building.add_floor(floor1)
    # floor1.add_room(room1)
    # floor1.add_room(room2)
    # room1.add_aircon(aircon1)
    # room1.add_aircon(aircon2)

    # building.add_person(person1)
    # building.add_person(person2)

    # room1.add_tempmap(temp_map1)
    # room2.add_tempmap(temp_map2)
    # room1.add_person(person1)
    # room1.add_person(person2)


    building0 = Building("Building:building0")
    floor_list =[]
    for i in range(0, 10):  # 1から10までのループ
        floor_list.append(Floor(f"Building:floor{i}"))
        building0.add_floor(floor_list[i])
        # print(f"floor{i}")

    room_list = []
    i=0
    for floor in floor_list:
        for j in range(0,100):
            num = i*100+j
            room_list.append(Room(f"Building:room{num}"))
            floor.add_room(room_list[num])
        i = i+1

    temp_map_list = []
    aircon_list = []
    num=0
    for room in room_list:
        temp_map_list.append(TempMap(f"Building:temp_map{num}"))
        aircon_list.append(Aircon(f"Building:airon{num}"))
        room.add_tempmap(temp_map_list[num])
        room.add_aircon(aircon_list[num])
        num = num+1


    person_list = []
    for i in range(0, 10000):  # 1から10までのループ
        person_list.append(Person(f"Building:person{i}",25))
        building0.add_person(person_list[i])

    for person in person_list:
        random_number = random.randint(0, 999)
        person.update_room(room_list[random_number])
        room_list[random_number].add_person(person)
        # print(f"floor{i}")

    # building0.show_details()

    # print(person_list[1].get_property("comfort_temp"))
    # person_list[1].operate_property("comfort_temp",26)


    #全てのビルインスタンスを表示、デバッグ用
    # building.show_details()

    #こんな使い方ができる、サンプル
    # for room in building.floor1.rooms.values():
    #     print(room)
    # for room in floor1.rooms.values():
    #     print(room)
    # print(building.floors["floor1"].rooms["room1"])
    # print(building.floor1.room1.name)
    # print(room1.name)


    # 自動エアコン制御スレッドを開始
    control_thread = threading.Thread(target=auto_aircon_control, args=(building0,),daemon=True)
    control_thread.start()

    # navigate(building0)

    control_thread.join()


if __name__ == '__main__':
    main()