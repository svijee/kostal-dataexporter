#!/usr/bin/env python3

import requests
import json
import time
import psycopg2
import os

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

  payload1 = {
    'dxsEntries': [
      data_mapping['pv_generator_dc_input_1_voltage'],
      data_mapping['pv_generator_dc_input_1_current'],
      data_mapping['pv_generator_dc_input_1_power'],
      data_mapping['house_home_consumption_covered_by_solar_generator'],
      data_mapping['house_home_consumption_covered_by_grid'],
      data_mapping['house_phase_selective_home_consumption_phase_1'],
      data_mapping['house_phase_selective_home_consumption_phase_2'],
      data_mapping['house_phase_selective_home_consumption_phase_3'],
      data_mapping['grid_grid_parameters_output_power'],
      data_mapping['grid_grid_parameters_grid_frequency'],
      data_mapping['grid_grid_parameters_cos'],
      data_mapping['grid_phase_1_voltage'],
      data_mapping['grid_phase_1_current'],
      data_mapping['grid_phase_1_power'],
      data_mapping['grid_phase_2_voltage'],
      data_mapping['grid_phase_2_current'],
      data_mapping['grid_phase_2_power'],
      data_mapping['grid_phase_3_voltage'],
      data_mapping['grid_phase_3_current'],
      data_mapping['grid_phase_3_power'],
    ]
  }

  # Second payload, because the inverter only returns 25 key-value pairs per request
  payload2 = {
    'dxsEntries': [
      data_mapping['stats_total_yield'],
      data_mapping['stats_total_operation_time'],
      data_mapping['stats_total_total_home_consumption'],
      data_mapping['stats_total_self_consumption_kwh'],
      data_mapping['stats_total_self_consumption_rate'],
      data_mapping['stats_total_degree_of_self_sufficiency'],
      data_mapping['stats_day_yield'],
      data_mapping['stats_day_total_home_consumption'],
      data_mapping['stats_day_self_consumption_kwh'],
      data_mapping['stats_day_self_consumption_rate'],
      data_mapping['stats_day_degree_of_self_sufficiency'],
    ]
  }

  response1 = requests.get(url, auth=(os.environ.get('KOSTAL_USERNAME'), os.environ.get('KOSTAL_PASSWORD')), params=payload1, timeout=5)
  response2 = requests.get(url, auth=(os.environ.get('KOSTAL_USERNAME'), os.environ.get('KOSTAL_PASSWORD')), params=payload2, timeout=5)

  json_data1 = json.loads(response1.text)
  json_data2 = json.loads(response2.text)

  current_values = {}

  for entry in json_data1['dxsEntries']:
    entry_name = get_key_by_value(data_mapping, entry['dxsId'])
    current_values[entry_name] = entry['value']

  for entry in json_data2['dxsEntries']:
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

def main():
  while True:
    print('Process values on {}'.format(time.asctime()))
    current_values = get_data()
    insert_data_into_postgres(current_values)
    time.sleep(30)

if __name__ == '__main__':
  main()
