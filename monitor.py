#!/usr/bin/env python3

import smbus2
import bme280
import os
import queue
import socket
import time
import requests
from newrelic_telemetry_sdk import GaugeMetric, CountMetric, SummaryMetric, MetricClient
from dotenv import load_dotenv

load_dotenv()

metric_client = MetricClient(os.getenv('NEWRELIC_INSIGHTS_INSERT_API_KEY'))
hostname = socket.gethostname()
hiveid = (os.getenv('HIVEID'))

port = 1
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

def measure_cpu_temp():
	temp = os.popen("vcgencmd measure_temp").readline()
	degrees_c = ((temp.replace("temp=","")).replace("'C",""))
	degrees_f = convert_centigrade_to_farenheit(float(degrees_c))
	return degrees_f

def convert_c_to_f(centigrade):
	return centigrade * 9/5 + 32

def measure_bme280_one():
	readings = []
	data = bme280.sample(bus, address, calibration_params)
	print(data)
	readings.append(GaugeMetric("temperature", convert_c_to_f(data.temperature), {"units": "Farenheit","host.name": hostname}))
	readings.append(GaugeMetric("pressure", data.pressure, {"units": "hPa","host.name": hostname}))
	readings.append(GaugeMetric("humidity", data.humidity, {"units": "% rH","host.name": hostname}))

	return readings

def is_cnx_active(timeout):
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

data_queue = queue.Queue()

while True:
	readings = measure_bme280_one()
	data_queue.put(readings)
#	with open("temperature_log.txt", "a") as file:
#		file.write(f"{time.time()}, {temperature / 100.0}, {humidity / 1024.0}\n")
	print(readings)
	
	try:
		response = metric_client.send_batch(readings)
		response.raise_for_status()
		print("Sent metrics successfully!")

		while(data_queue.empty()==False):
			print(data_queue.queue[0],end=" ")
			data_queue.get()
			
	except:
		print("problem sending data:",)
	time.sleep(60)
	