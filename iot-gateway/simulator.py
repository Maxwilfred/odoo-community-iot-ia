#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time
import random
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature/entrepot"

DEVICE_ID = "sensor_01"
MIN_TEMP = 18.0
MAX_TEMP = 32.0
THRESHOLD = 25.0
FREQUENCY = 30

def generate_temperature():
    if random.random() < 0.3:
        return round(random.uniform(26, 32), 1)
    return round(random.uniform(18, 24), 1)

def main():
    logger.info("Démarrage simulateur")
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    
    counter = 0
    try:
        while True:
            counter += 1
            temp = generate_temperature()
            exceed = temp > THRESHOLD
            
            msg = {
                "device_id": DEVICE_ID,
                "timestamp": int(time.time()),
                "value": temp,
                "unit": "celsius",
                "threshold_exceeded": exceed
            }
            
            client.publish(MQTT_TOPIC, json.dumps(msg))
            status = "⚠️ DEPASSEMENT" if exceed else "normal"
            logger.info(f"[{counter}] {status} - {temp}°C")
            time.sleep(FREQUENCY)
    except KeyboardInterrupt:
        logger.info("Arrêt")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()