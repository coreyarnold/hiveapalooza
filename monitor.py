#!/usr/bin/env python3

import smbus2
import bme280
import os
import socket
import time
import requests
from newrelic_telemetry_sdk import GaugeMetric, CountMetric, SummaryMetric, MetricClient
from dotenv import load_dotenv

#make sure to wait for the machine to connect to the network


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
	readings.append(GaugeMetric("temperature", convert_c_to_f(data.temperature), {"units": "Farenheit","host.name": hostname, "hive.id": hiveid}))
	readings.append(pressure = GaugeMetric("pressure", data.pressure, {"units": "hPa","host.name": hostname}))
	readings.append(GaugeMetric("humidity", data.humidity, {"units": "% rH","host.name": hostname}))

	return readings

def is_cnx_active(timeout):
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

# the sample method will take a single reading and return a
# compensated_reading object
#data = bme280.sample(bus, address, calibration_params)

# the compensated_reading class has the following attributes
#print(data.id)
#print(data.timestamp)
#print(data.temperature)
#print(data.pressure)
#print(data.humidity)

# there is a handy string representation too
#print(data)

while True:
	if is_cnx_active(10) is True:
		print("internet is active... yay")
		break
	else:
		print("no internet yet, sleeping for a bit :(")
		time.sleep(30)


while True:
	readings = measure_bme280_one()

	try:
		response = metric_client.send_batch(readings)
		response.raise_for_status()
		print("Sent metrics successfully!")
		time.sleep(60)
	except:
		print("problem sending data:",)