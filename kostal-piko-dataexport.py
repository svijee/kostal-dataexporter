#!/usr/bin/env python3

import argparse
import json
import os
import time
import math
from datetime import datetime

import psycopg2
import requests
from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient as InfluxDB2Client
from influxdb_client.client.write_api import SYNCHRONOUS


data_mapping = {
  'pv_generator_dc_input_1_voltage': 33555202,
  'pv_generator_dc_input_1_current': 33555201,
  'pv_generator_dc_input_1_power': 33555203,
  'pv_generator_dc_input_2_voltage': 33555458,
  'pv_generator_dc_input_2_current': 33555457,
  'pv_generator_dc_input_2_power': 33555459,
  'house_home_consumption_covered_by_solar_generator': 83886336,
  'house_home_consumption_covered_by_battery': 83886592,
  'house_home_consumption_covered_by_grid': 83886848,
  'house_phase_selective_home_consumption_phase_1': 83887106,
  'house_phase_selective_home_consumption_phase_2': 83887362,
  'house_phase_selective_home_consumption_phase_3': 83887618,
  'grid_grid_parameters_output_power': 67109120,
  'grid_grid_parameters_grid_frequency': 67110400,
  'grid_grid_parameters_cos': 67110656,
  'grid_grid_parameters_limitation_on': 67110144,
  'grid_phase_1_voltage': 67109378,
  'grid_phase_1_current': 67109377,
  'grid_phase_1_power': 67109379,
  'grid_phase_2_voltage': 67109634,
  'grid_phase_2_current': 67109633,
  'grid_phase_2_power': 67109635,
  'grid_phase_3_voltage': 67109890,
  'grid_phase_3_current': 67109889,
  'grid_phase_3_power': 67109891,
  'stats_total_yield': 251658753,
  'stats_total_operation_time': 251658496,
  'stats_total_total_home_consumption': 251659009,
  'stats_total_self_consumption_kwh': 251659265,
  'stats_total_self_consumption_rate': 251659280,
  'stats_total_degree_of_self_sufficiency': 251659281,
  'stats_day_yield': 251658754,
  'stats_day_total_home_consumption': 251659010,
  'stats_day_self_consumption_kwh': 251659266,
  'stats_day_self_consumption_rate': 251659278,
  'stats_day_degree_of_self_sufficiency': 251659279,
}

def get_key_by_value(dict_object, search_value):
  return next(key for key, value in dict_object.items() if value == search_value)

def get_data():
  url = 'http://{}/api/dxs.json'.format(os.environ.get('KOSTAL_HOST'))
  auth = (os.environ.get('KOSTAL_USERNAME'), os.environ.get('KOSTAL_PASSWORD'))

  current_values = {}

  query_max_size = 25
  num_requests = math.ceil(len(list(data_mapping)) / query_max_size)
  for query_index in range(num_requests):
    slice_from = query_index * query_max_size
    slice_to = (query_index + 1) * query_max_size
    payload = { 'dxsEntries': [data_mapping[k] for k in list(data_mapping)[slice_from:slice_to]] }

    response = requests.get(url, auth=auth, params=payload, timeout=5)
    json_data = json.loads(response.text)
    for entry in json_data['dxsEntries']:
      entry_name = get_key_by_value(data_mapping, entry['dxsId'])
      current_values[entry_name] = entry['value']

  return current_values

def insert_data_into_postgres(current_values):
  params = {
    "host": os.environ.get('DB_HOST'),
    "port": os.environ.get('DB_PORT'),
    "database": os.environ.get('DB_NAME'),
    "user": os.environ.get('DB_USER'),
    "password": os.environ.get('DB_PASSWORD'),
  }

  conn = psycopg2.connect(**params)

  sql_cmd = """INSERT INTO pvwr(
              pv_generator_dc_input_1_voltage,
              pv_generator_dc_input_1_current,
              pv_generator_dc_input_1_power,
              house_home_consumption_covered_by_solar_generator,
              house_home_consumption_covered_by_grid,
              house_phase_selective_home_consumption_phase_1,
              house_phase_selective_home_consumption_phase_2,
              house_phase_selective_home_consumption_phase_3,
              grid_grid_parameters_output_power,
              grid_grid_parameters_grid_frequency,
              grid_grid_parameters_cos,
              grid_phase_1_voltage,
              grid_phase_1_current,
              grid_phase_1_power,
              grid_phase_2_voltage,
              grid_phase_2_current,
              grid_phase_2_power,
              grid_phase_3_voltage,
              grid_phase_3_current,
              grid_phase_3_power,
              stats_total_yield,
              stats_total_operation_time,
              stats_total_total_home_consumption,
              stats_total_self_consumption_kwh,
              stats_total_self_consumption_rate,
              stats_total_degree_of_self_sufficiency,
              stats_day_yield,
              stats_day_total_home_consumption,
              stats_day_self_consumption_kwh,
              stats_day_self_consumption_rate,
              stats_day_degree_of_self_sufficiency)
            VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})""".format(
              current_values['pv_generator_dc_input_1_voltage'],
              current_values['pv_generator_dc_input_1_current'],
              current_values['pv_generator_dc_input_1_power'],
              current_values['house_home_consumption_covered_by_solar_generator'] or 0,
              current_values['house_home_consumption_covered_by_grid'] or 0,
              current_values['house_phase_selective_home_consumption_phase_1'],
              current_values['house_phase_selective_home_consumption_phase_2'],
              current_values['house_phase_selective_home_consumption_phase_3'],
              current_values['grid_grid_parameters_output_power'],
              current_values['grid_grid_parameters_grid_frequency'],
              current_values['grid_grid_parameters_cos'],
              current_values['grid_phase_1_voltage'],
              current_values['grid_phase_1_current'],
              current_values['grid_phase_1_power'],
              current_values['grid_phase_2_voltage'],
              current_values['grid_phase_2_current'],
              current_values['grid_phase_2_power'],
              current_values['grid_phase_3_voltage'],
              current_values['grid_phase_3_current'],
              current_values['grid_phase_3_power'],
              current_values['stats_total_yield'],
              current_values['stats_total_operation_time'],
              current_values['stats_total_total_home_consumption'],
              current_values['stats_total_self_consumption_kwh'],
              current_values['stats_total_self_consumption_rate'],
              current_values['stats_total_degree_of_self_sufficiency'],
              current_values['stats_day_yield'],
              current_values['stats_day_total_home_consumption'],
              current_values['stats_day_self_consumption_kwh'],
              current_values['stats_day_self_consumption_rate'],
              current_values['stats_day_degree_of_self_sufficiency']
            )

  cursor = conn.cursor()
  cursor.execute(sql_cmd)
  conn.commit()
  cursor.close()
  conn.close()

def insert_data_into_influx(current_values):
  influxdb_name = os.environ.get('INFLUXDB_NAME')
  influxClient = InfluxDBClient(
      host=os.environ.get('INFLUXDB_HOST'),
      port=os.environ.get('INFLUXDB_PORT'),
      username=os.environ.get('INFLUXDB_USER'),
      password=os.environ.get('INFLUXDB_PASSWORD')
  )

  current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

  influxClient.write_points([{
    "measurement": "pvwr",
    "time": current_time,
    "fields":  {
      "pv_generator_dc_input_1_voltage": float(current_values['pv_generator_dc_input_1_voltage']),
      "pv_generator_dc_input_1_current": float(current_values['pv_generator_dc_input_1_current']),
      "pv_generator_dc_input_1_power": float(current_values['pv_generator_dc_input_1_power']),
      "house_home_consumption_covered_by_solar_generator": float(current_values['house_home_consumption_covered_by_solar_generator'] or 0),
      "house_home_consumption_covered_by_grid": float(current_values['house_home_consumption_covered_by_grid'] or 0),
      "house_phase_selective_home_consumption_phase_1": float(current_values['house_phase_selective_home_consumption_phase_1']),
      "house_phase_selective_home_consumption_phase_2": float(current_values['house_phase_selective_home_consumption_phase_2']),
      "house_phase_selective_home_consumption_phase_3": float(current_values['house_phase_selective_home_consumption_phase_3']),
      "grid_grid_parameters_output_power": float(current_values['grid_grid_parameters_output_power']),
      "grid_grid_parameters_grid_frequency": float(current_values['grid_grid_parameters_grid_frequency']),
      "grid_grid_parameters_cos": float(current_values['grid_grid_parameters_cos']),
      "grid_phase_1_voltage": float(current_values['grid_phase_1_voltage']),
      "grid_phase_1_power": float(current_values['grid_phase_1_power']),
      "grid_phase_1_current": float(current_values['grid_phase_1_current']),
      "grid_phase_2_voltage": float(current_values['grid_phase_2_voltage']),
      "grid_phase_2_power": float(current_values['grid_phase_2_power']),
      "grid_phase_2_current": float(current_values['grid_phase_2_current']),
      "grid_phase_3_voltage": float(current_values['grid_phase_3_voltage']),
      "grid_phase_3_power": float(current_values['grid_phase_3_power']),
      "grid_phase_3_current": float(current_values['grid_phase_3_current']),
      "stats_total_yield": float(current_values['stats_total_yield']),
      "stats_total_operation_time": float(current_values['stats_total_operation_time']),
      "stats_total_total_home_consumption": float(current_values['stats_total_total_home_consumption']),
      "stats_total_self_consumption_kwh": float(current_values['stats_total_self_consumption_kwh']),
      "stats_total_self_consumption_rate": float(current_values['stats_total_self_consumption_rate']),
      "stats_total_degree_of_self_sufficiency": float(current_values['stats_total_degree_of_self_sufficiency']),
      "stats_day_yield": float(current_values['stats_day_yield']),
      "stats_day_total_home_consumption": float(current_values['stats_day_total_home_consumption']),
      "stats_day_self_consumption_kwh": float(current_values['stats_day_self_consumption_kwh']),
      "stats_day_self_consumption_rate": float(current_values['stats_day_self_consumption_rate']),
      "stats_day_degree_of_self_sufficiency": float(current_values['stats_day_degree_of_self_sufficiency']),
    }
  }], database=influxdb_name)

def insert_data_into_influx2(current_values):
  org = os.environ.get('INFLUXDB_ORG')
  bucket = os.environ.get('INFLUXDB_BUCKET')

  influxClient = InfluxDB2Client(
    url=os.environ.get('INFLUXDB_URL'),
    token=os.environ.get('INFLUXDB_TOKEN'),
  )

  write_api = influxClient.write_api(write_options=SYNCHRONOUS)

  data = (
    f"pvwr,pvwr=pvwr "
    f"pv_generator_dc_input_1_voltage={float(current_values['pv_generator_dc_input_1_voltage'])},"
    f"pv_generator_dc_input_1_current={float(current_values['pv_generator_dc_input_1_current'])},"
    f"pv_generator_dc_input_1_power={float(current_values['pv_generator_dc_input_1_power'])},"
    f"house_home_consumption_covered_by_solar_generator={float(current_values['house_home_consumption_covered_by_solar_generator'] or 0)},"
    f"house_home_consumption_covered_by_grid={float(current_values['house_home_consumption_covered_by_grid'] or 0)},"
    f"house_phase_selective_home_consumption_phase_1={float(current_values['house_phase_selective_home_consumption_phase_1'])},"
    f"house_phase_selective_home_consumption_phase_2={float(current_values['house_phase_selective_home_consumption_phase_2'])},"
    f"house_phase_selective_home_consumption_phase_3={float(current_values['house_phase_selective_home_consumption_phase_3'])},"
    f"grid_grid_parameters_output_power={float(current_values['grid_grid_parameters_output_power'])},"
    f"grid_grid_parameters_grid_frequency={float(current_values['grid_grid_parameters_grid_frequency'])},"
    f"grid_grid_parameters_cos={float(current_values['grid_grid_parameters_cos'])},"
    f"grid_phase_1_voltage={float(current_values['grid_phase_1_voltage'])},"
    f"grid_phase_1_power={float(current_values['grid_phase_1_power'])},"
    f"grid_phase_1_current={float(current_values['grid_phase_1_current'])},"
    f"grid_phase_2_voltage={float(current_values['grid_phase_2_voltage'])},"
    f"grid_phase_2_power={float(current_values['grid_phase_2_power'])},"
    f"grid_phase_2_current={float(current_values['grid_phase_2_current'])},"
    f"grid_phase_3_voltage={float(current_values['grid_phase_3_voltage'])},"
    f"grid_phase_3_power={float(current_values['grid_phase_3_power'])},"
    f"grid_phase_3_current={float(current_values['grid_phase_3_current'])},"
    f"stats_total_yield={float(current_values['stats_total_yield'])},"
    f"stats_total_operation_time={float(current_values['stats_total_operation_time'])},"
    f"stats_total_total_home_consumption={float(current_values['stats_total_total_home_consumption'])},"
    f"stats_total_self_consumption_kwh={float(current_values['stats_total_self_consumption_kwh'])},"
    f"stats_total_self_consumption_rate={float(current_values['stats_total_self_consumption_rate'])},"
    f"stats_total_degree_of_self_sufficiency={float(current_values['stats_total_degree_of_self_sufficiency'])},"
    f"stats_day_yield={float(current_values['stats_day_yield'])},"
    f"stats_day_total_home_consumption={float(current_values['stats_day_total_home_consumption'])},"
    f"stats_day_self_consumption_kwh={float(current_values['stats_day_self_consumption_kwh'])},"
    f"stats_day_self_consumption_rate={float(current_values['stats_day_self_consumption_rate'])},"
    f"stats_day_degree_of_self_sufficiency={float(current_values['stats_day_degree_of_self_sufficiency'])}"
  )

  write_api.write(bucket, org, data)


def main():
  parser = argparse.ArgumentParser(description='Kostal Dataexporter')
  parser.add_argument('--postgres', type=int, default=0, choices=[0, 1])
  parser.add_argument('--influx', type=int, default=0, choices=[0, 1])
  parser.add_argument('--influx2', type=int, default=1, choices=[0, 1])
  args = parser.parse_args()

  while True:
    print('Process values on {}'.format(time.asctime()))
    current_values = get_data()

    if args.postgres == 1:
      insert_data_into_postgres(current_values)

    if args.influx == 1:
      insert_data_into_influx(current_values)

    if args.influx2 == 1:
      insert_data_into_influx2(current_values)
    time.sleep(30)

if __name__ == '__main__':
  main()
