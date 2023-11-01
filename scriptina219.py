import time
import board
import busio
from adafruit_ina219 import INA219
import paho.mqtt.client as mqtt
from socket import gethostbyname, gaierror

MQTT_HOST = "192.168.88.155"
MQTT_PORT = 1883
MQTT_TOPIC_CURR = "ras/ina219/curr"
MQTT_TOPIC_VOL = "ras/ina219/vol"
MQTT_TOPIC_POW = "ras/ina219/pow"

i2c_bus = busio.I2C(board.SCL, board.SDA)
ina219 = INA219(i2c_bus)

def connect_to_mqtt():
    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe([(MQTT_TOPIC_CURR, 0), (MQTT_TOPIC_VOL, 0), (MQTT_TOPIC_POW, 0)])

    def on_message(client, userdata, message):
        print("Received message on topic " + message.topic + ": " + message.payload.decode())

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        host = gethostbyname(MQTT_HOST)
        client.connect(host, MQTT_PORT, 60)
    except gaierror:
        print("Couldn't resolve 192.168.88.155")
        return

    return client

def main():
    client = connect_to_mqtt()
    client.loop_start()

    while True:
        current_mA = ina219.current
        voltage_V = ina219.bus_voltage
        power_mW = ina219.power

        client.publish(MQTT_TOPIC_CURR, "{:.2f} mA".format(current_mA))
        client.publish(MQTT_TOPIC_VOL, "{:.2f}".format(voltage_V))
        client.publish(MQTT_TOPIC_POW, "{:.2f}".format(power_mW))

        time.sleep(2)

if __name__ == "__main__":
    main()

