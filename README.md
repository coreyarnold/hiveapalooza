# hiveapalooza
Raspberry Pi based honeybee hive monitoring, sending data up to New Relic

Find out address of i2c devices on the raspberry pi
`sudo i2cdetect -y 1`

install the newrelic_telemetry_sdk
`pip install newrelic_telemetry_sdk`

install the necessary python modules
`pip install RPi.bme280`
`pip install python-dotenv`
