from umqtt.simple import MQTTClient
from machine import Pin
import binascii
import machine

from configs.mqtt_config import SERVER
from configs.hw_config import HW_LED_PIN

# ESP8266 ESP-12 modules have blue, active-low LED on GPIO2, replace
# with something else if needed.
led = Pin(HW_LED_PIN, Pin.OUT, value=1)

# Default MQTT server to connect to
#SERVER = "192.168.1.35"
CLIENT_ID = binascii.hexlify(machine.unique_id())
TOPIC = b"led"

state = 0

def sub_cb(topic, msg):
    global state
    print((topic, msg))
    if msg == b"on":
        led.value(1)
        state = 1
    elif msg == b"off":
        led.value(0)
        state = 0
    elif msg == b"toggle":
        # LED is inversed, so setting it to current state
        # value will make it toggle
        led.value(state)
        state = 1 - state


def sub_main(server=SERVER):
    c = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    print("Connected to %s, subscribed to %s topic" % (server, TOPIC))

    try:
        while 1:
            # micropython.mem_info()
            c.wait_msg()
    finally:
        c.disconnect()
