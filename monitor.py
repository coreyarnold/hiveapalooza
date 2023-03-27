import os
import time
from newrelic_telemetry_sdk import GaugeMetric, CountMetric, SummaryMetric, MetricClient
from dotenv import load_dotenv

load_dotenv()

metric_client = MetricClient(os.getenv('NEWRELIC_INSIGHTS_INSERT_API_KEY'))

def measure_cpu_temp():
	temp = os.popen("vcgencmd measure_temp").readline()
	degrees_c = ((temp.replace("temp=","")).replace("'C",""))
	degrees_f = float(degrees_c) * 9/5 + 32
	return degrees_f

def measure_sensor_one():
	return GaugeMetric("temperature", 85, {"units": "Farenheit","hiveid": "arnoldacres-hive-001","sensorid": "abc123"})

def measure_sensor_two():
	return GaugeMetric("temperature", 93, {"units": "Farenheit","hiveid": "arnoldacres-hive-001","sensorid": "abc124"})

while True:
	cpu = measure_cpu_temp()
	print(cpu)
	temperature = GaugeMetric("temperature", cpu, {"units": "Farenheit","host.name": "arnoldacres-hive-001"})

	batch = [temperature, measure_sensor_one(), measure_sensor_two()]
	response = metric_client.send_batch(batch)
	response.raise_for_status()
	print("Sent metrics successfully!")
	time.sleep(10)