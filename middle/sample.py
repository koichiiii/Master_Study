#! /usr/bin/python
#
#	query_data.py
#
#						Jul/07/2021
# ------------------------------------------------------------------
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# ------------------------------------------------------------------
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

query_api = client.query_api()
query = ' from(bucket:"db_daikin")\
|> range(start: -12h)'
result = client.query_api().query(org=org, query=query)
results = []
for table in result:
    for record in table.records:
        results.append((record.get_field(), record.get_value()))

print(results)
# ------------------------------------------------------------------
