# app/middleware.py
from flask import Flask, request, Response, jsonify
import requests
import os
import json
import logging


import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

bucket = "db_daikin"
org = "daikin"
token = '4iSDEWZxntqLEXv6AlZqmLcJOV-rvzKxMXHEdWJhKkGjMEO3HVkUi0S_RxPXvdtQUJcrVJse2MsrWwp3z-a3qQ=='
#
url="http://192.168.100.151:8086"

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)



app = Flask(__name__)

# # 環境変数からバックエンドサービスのURLを取得
# GATEWAY_URL = os.getenv('GATEWAY_URL', 'http://172.30.0.10:8080')
# TIME_SERVICE_URL = os.getenv('TIME_SERVICE_URL', 'http://172.30.0.17:8086')
GATEWAY_URL = 'http://192.168.100.151:8080/api/2/things/'
TIME_SERVICE_URL = 'http://k-owaki:704lIlac@192.168.100.151:8086/api/v2/query'


@app.route('/', methods=['POST','GET'])
def handle_api():
    data = request.get_json()
    # リクエストボディが存在しない場合
    # return "aaa"
    if not data:
        return jsonify({"message": "Bad request"}), 400
        

    # "start" と "end" フィールドの存在をチェック
    start = data.get('start')
    end = data.get('end')
    thing = data.get('thing')
    flag=0
    # Authorizationトークン（適宜変更）
    auth_token = "4iSDEWZxntqLEXv6AlZqmLcJOV-rvzKxMXHEdWJhKkGjMEO3HVkUi0S_RxPXvdtQUJcrVJse2MsrWwp3z-a3qQ=="

    if thing and start and end:
        response = {
            "message": "1",
            "start": start,
            "thing": thing,
            "end": end
        }
        flag=1
        app.logger.info(flag)

        target_url = TIME_SERVICE_URL
        target_full_url = f"{target_url}"

        
    elif thing and not ( start or end):
        response = {
            "message": "2",
            "start": start,
            "thing": thing,
            "end": end
        }
        flag=2
        app.logger.info(flag)

        target_url = GATEWAY_URL
        target_full_url = f"{target_url}{thing}"
    else:
        return "Bad request"



    # return Response(
    #     json.dumps(response, ensure_ascii=False),
    #     mimetype='application/json'
    # ), 200
    
    # target_full_url = f"{target_url}{thing}"
    app.logger.info(target_full_url)
    
    try:
        if flag==1:
            now = datetime.now() + timedelta(hours=9)

            first_obj = datetime.strptime(response["start"], "%Y-%m-%d %H:%M")-timedelta(hours=9)
            first_obj = first_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_obj = datetime.strptime(response["end"], "%Y-%m-%d %H:%M")-timedelta(hours=9)
            end_obj = end_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
            print(first_obj)
            print(end_obj)

            # diff1 = relativedelta(first_obj, now)
            # diff2 = relativedelta(end_obj, now)

            # print(now)
            # print(diff1.years)
            # print(diff1.months)
            # print(diff1.days)
            # print(diff1.hours)
            # print(diff1.minutes)
            # print(diff2.years)
            # print(diff2.months)
            # print(diff2.days)
            # print(diff2.hours)
            # print(diff2.minutes)
            

            query_api = client.query_api()
            # query = ' from(bucket:"db_daikin") |> range(start:-1m)'
            # query = f'''from(bucket:"{bucket}") \
            #     |> range(start: -{abs(diff1.years)}y{abs(diff1.months)}m{abs(diff1.days)}d{abs(diff1.hours)}h{abs(diff1.minutes)}m, stop: {abs(diff2.years)}y{abs(diff2.months)}m{abs(diff2.days)}d{abs(diff2.hours)}h{abs(diff2.minutes)}m) \
            #     |> filter(fn: (r) => r["DeviceId"] == "Building:temperature00001")'''
            query = f'''from(bucket:"{bucket}") \
                |> range(start: {first_obj}, stop: {end_obj}) \
                |> filter(fn: (r) => r._measurement == "devices") \
                |> filter(fn: (r) => r.deviceId == "Building:temperature00001")'''
            
            
            
            print(query)
            result = client.query_api().query(org=org, query=query)
            results = []
            for table in result:
                for record in table.records:
                    results.append((record.get_field(), record.get_value()))

            print(results)
            return jsonify(results)
            # csv_data = "id,name,value\n" + "\n".join(
            #     [f"{row['id']},{row['name']}" for row in results]
            # )
            # return Response(csv_data, mimetype='text/csv')
            
            
            # params= {"org": "daikin"}
            # headers = {
            #     'Authorization': "Token 4iSDEWZxntqLEXv6AlZqmLcJOV-rvzKxMXHEdWJhKkGjMEO3HVkUi0S_RxPXvdtQUJcrVJse2MsrWwp3z-a3qQ==",
            #     "Accept": "application/csv",
            #     "Content-type": "application/vnd.flux"
            # }
            # headers['Authorization']= 'Token ' + auth_token
            # # リクエストボディ
            # data = 'from(bucket:"db_daikin") |> range(start: -1m) |> filter(fn: (r) => r._field == "temperature")' 
            # print(headers)
            # # POSTリクエストの送信
            # response = requests.post(target_full_url, headers=headers, data=data, params=params)
            # # # レスポンスの表示
            # print(response.status_code)
            # print(response.text)
            

        elif flag==2:
             response = requests.request(
                # method=request.method,
                method="GET",
                url=target_full_url,
                headers={key: value for key, value in request.headers if key.lower() != 'host'},
                params=request.args,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False
            )   

        # レスポンスのヘッダーを設定（必要なものだけ）
        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in response.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(response.content, response.status_code, headers)
        # return

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error forwarding request: {e}")
        return Response(str(e), 500)


@app.route('/index')
def index():
    return render_template('index.html')
    # return "index page"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3001)