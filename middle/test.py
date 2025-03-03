from flask import Flask, request, jsonify
import threading
import time
from datetime import datetime

app = Flask(__name__)


class Building:
    
    # def initBuilding(self, id, pass):
    def __init__(self,name):
        self.name = name
        self.floors = {}  # フロアのリスト
        self.persons = {} # 人のリスト
        self.outside_temp = []
        # self.id = id
        # self.pass = arg1
        # self.structure = self.query_building_structure()

    # def add_floor(self, floor):
    #     self.floors.append(floor)
    def add_floor(self, floor):
        if floor.name not in self.floors:
            self.floors[floor.name] = floor

    def show_details(self):
        print(f"Building: {self.name}")
        for floor in self.floors:
            floor.show_details()
            # print(f"  {aircon.name}: {aircon.temperature}°C")

    def query_structure():
        ###ビルOSに問い合わせて階層構造を取得する###
        print("aaa")

    def find_device(self, room_id, device_type):
        print("aaa")

    def __getattr__(self, item):
        return self.floors[item] if item in self.floors else None

class Person:
    def __init__(self, name):
        self.name = name



class Floor:
    def __init__(self, name):
        self.name = name
        self.rooms = {}  # 部屋のリスト

    # def add_room(self, room):
    #     self.rooms.append(room)
    def add_room(self, room):
        if room.name not in self.rooms:
            self.rooms[room.name] = room

    def show_details(self):
        print(f"Floor: {self.name}")
        for room in self.rooms:
            room.show_details()
            # print(f"  {aircon.name}: {aircon.temperature}°C")
    
    def __getattr__(self, item):
        return self.rooms[item] if item in self.rooms else None

class Room:
    def __init__(self, name):
        self.name = name
        self.aircons = {}  # エアコンのリスト

    # def add_aircon(self, aircon):
    #     self.aircons.append(aircon)
    def add_aircon(self, aircon):
        if aircon.name not in self.aircons:
            self.aircons[aircon.name] = aircon

    def show_details(self):
        print(f"Room: {self.name}")
        for aircon in self.aircons:
            # print(f"  {aircon.name}: {aircon.temperature}°C")
            aircon.show_details()
    
    def __getattr__(self, item):
        return self.aircons[item] if item in self.aircons else None

    


class Aircon:
    def __init__(self, name, temperature=24):
        self.name = name
        self.temperature = temperature

    def control(self,temp):
        self.temperature = temp
        print(f"{self.name}: Air conditioner temperature set to "+ str(temp) + "°C")
    
    def show_details(self):
        print(f"Aircon: {self.name}")
        print(f"  {self.name}: {self.temperature}°C")


def calculate_temperature(room):
    list = []
    for aircon in room.aircons.values():
        list.append((aircon,24))

    return list

# 定期的なエアコン制御を実行する関数
def auto_aircon_control(building):
    while True:
        #こんな使い方ができるよ
        # for room in building.floor1.rooms.values():
        #     print(room)
        # print(building.floors["floor1"].rooms["room1"])
        # print(building.floor1.room1.name)

        for floor in building.floors.values():
            for room in floor.rooms.values():
                #設定温度を計算して（エアコン名、設定温度）のリストを作成
                # aircon_temp = calculate_temperature(<3次元温度分布の時系列データ(4次元配列)>,<その部屋にいる個人の快適温度(1次元配列)>,outside_temp,<人口密度>)
                aircon_temp = calculate_temperature(room)
                # aircon_temp = calculate_temperature(temperature_map,person_list,outside_temp,room.capacity)
                #エアコンのループ    
                for aircon, temp in aircon_temp:
                    aircon.control(temp)
 
        print(f"[{datetime.now()}] 自動エアコン制御が実行されました。")
        time.sleep(10)  # 5分（300秒）

# ユーザリクエストを処理するエンドポイント
@app.route('/navigate', methods=['POST'])
def navigate(building):
    data = request.get_json()
    if not data or "user_id" not in data:
        return jsonify({"status": "error", "message": "Invalid request. 'user_id' is required."}), 400
    
    user_id = data["user_id"]

    # ナビゲーションロジック（ここではモックとして適当な部屋を返す）
    # for person in persons:
    #     comfort_position = navigateHuman(comfort_temp,air_control_manager.getFutureTemp())

    ##ユーザにとって快適であるだろう部屋、ポジションをリストで返すlist(room,position)
    comfort_position = [["room1",[2,3,4]],["room2",[3,4,5]]]

    response = {
        "status": "success",
        "message": f"User {user_id} should go to these room. {comfort_position}",
        "timestamp": datetime.now().isoformat()
    }
    print(f"[{datetime.now()}] ユーザリクエストを処理: {response}")
    return jsonify(response)




def main():

    #インスタンス生成
    building = Building("shimonishi_building")

    floor1 = Floor("floor1")
    room1 = Room("room1")
    room2 = Room("room2")
    aircon1 = Aircon("aircon1")
    aircon2 = Aircon("aircon2")
    #階層化
    building.add_floor(floor1)
    floor1.add_room(room1)
    floor1.add_room(room2)
    room1.add_aircon(aircon1)
    room1.add_aircon(aircon2)

    #全てのビルインスタンスを表示
    # floor1.show_details()
    # room1.show_details()
    # building.show_details()

    #こんな使い方ができる
    # for room in building.floor1.rooms.values():
    #     print(room)
    # for room in floor1.rooms.values():
    #     print(room)
    # print(building.floors["floor1"].rooms["room1"])
    # print(building.floor1.room1.name)
    # print(room1.name)


    # 自動エアコン制御スレッドを開始
    control_thread = threading.Thread(target=auto_aircon_control, args=(building,),daemon=True)
    control_thread.start()

    # Flaskサーバを開始
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()