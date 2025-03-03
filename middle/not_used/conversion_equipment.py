#!usr/bin/env python
# -*- coding: utf-8 -*- 

import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
import json
import ast
import re
import requests 
import datetime


# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
  print("Connected with result code " + str(rc))  # 接続できた旨表示
  client.subscribe("building/#")  # subするトピックを設定 

# ブローカーが切断したときの処理
def on_disconnect(client, userdata, rc):
  if  rc != 0:
    print("Unexpected disconnection.")

# ID取得
def extract_id(text):
    pattern = r"\/([^\/]+)\/things\/twin\/events\/modified"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return None


rows = 100
cols = 10
comfort_array = [[0] * cols for _ in range(rows)]

# メッセージが届いたときの処理
def on_message(client, userdata, msg):
  print("message recieved:")
  print(datetime.datetime.now())
  #print(str(msg.payload))
  payload = msg.payload.decode("utf-8")
  payload_fixed = payload.replace("undefined", "null")
  #print(payload_fixed)
  data = json.loads(payload_fixed)

  id = extract_id(data["topic"])
  #id_num = int(re.findall(r'\d+', id))
  #IDに基づいて変換処理
  ###データ取得時

  headers = data.get("headers",{})
  mqttt = headers.get("mqtt.topic",{})


  if re.search(r"all",id) and "mqtt.topic" in data["headers"]:
    #メッセージ格納用
    txt = ["{" for _ in range(11)]

    try:
      for key, value in data["value"]["FCU_all"]["properties"].items():
        #print(key, ":", value)
        pattern = r'([A-Za-z]+)(\d+)([A-Za-z]+)'
        matches = re.match(pattern, key)
        if matches:
          fcu = matches.group(1)

          num = int(matches.group(2))-1
          property = matches.group(3)

          #print("FCU:", fcu)
          #print("Number:", num)
          #print("property:", property)
          txt[num] = txt[num] + "\"" + property + "\":" +str(value).lower() + ","

      print("send message to ditto:")
      print(datetime.datetime.now())
      #print(id)
      parts = re.split(r"[^\d]+", id)
      # 数字部分のみを抽出（空文字を除外）
      numbers = [part for part in parts if part.isdigit()]
      if numbers:
        tens_digit = int(numbers[0]) % 10
        ones_digit = int(numbers[0]) % 100
        #print(tens_digit)
        for i in range(0,10):
        #  print(txt[i])
          
          txt[i] = txt[i]+"\"thingId\":\""+"test:emusensor"+ str(numbers[0]) +str(i)+"\""+"}"

          print("3/sample: emusensor"+str(numbers[0])+str(i))
          client.publish("3/sample",txt[i])
        print("publish complete")
    except Exception as e:
      print("このメッセージは無視します")


  ###制御時
  #elif re.search(r"emusensor",id) and "3/sample" not in data["headers"]["mqtt.topic"]:
  elif re.search(r"emusensor",id) and mqttt != "3/sample" :
    #print(id)
    #print("aaa")
    pattern = r"(\D+)(\d+)"
    matches = re.match(pattern, id)
    if matches:
      # "emusensor" と数字に分割
      sensor_name = matches.group(1)
      sensor_number = int(matches.group(2))
      tens_digit = sensor_number % 10 +1
      #print("センサー名:", sensor_name)
      #print("番号:", sensor_number)
    else:
      print("マッチしませんでした。")


    #print("aaa")
    property = "FCU" + str(tens_digit)
    path_value = data.get("path")
    property = property + path_value.split("/")[-1]
    #print(property)
    uri = "http://192.168.100.151:8080/api/2/things/test_all:all_0/features/FCU_all/properties/" + property
    #print(uri)
    #print("http:sensor_all")
    #print(data["value"])

    headers = {
    "Content-Type": "application/json",  # コンテンツタイプを指定する例
    "Authorization": "Basic ditto ditto"  # 認証トークンを指定する例
    }
    
    print("send http command to ditto:")
    print(datetime.datetime.now())
    response = requests.put(uri,json=data["value"],auth=("owner","704lIlac"))
    ##getの時
    #response = requests.get(uri, auth=("ditto","ditto"))
    print(response.text)
    print("completed")
  
  else:
    print("このメッセージは無視します（httpによるallの更新）")
 

# MQTTの接続設定
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)                 # クラスのインスタンス(実体)の作成
client.on_connect = on_connect         # 接続時のコールバック関数を登録
client.on_disconnect = on_disconnect   # 切断時のコールバックを登録
client.on_message = on_message         # メッセージ到着時のコールバック
 
client.connect("172.30.0.4", 1883, 60)  # 接続先は自分自身
 

client.loop_forever()                  # 永久ループして待ち続ける
