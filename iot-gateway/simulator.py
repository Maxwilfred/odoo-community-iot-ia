#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time
import random
import logging
from datetime import datetime
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
BASE_TOPIC = "sensor/temperature"

# Liste des capteurs disponibles
SENSORS = [
    {"id": "entrepot_nord", "min": 18, "max": 32, "offset": 0},
    {"id": "entrepot_sud", "min": 19, "max": 31, "offset": 1},
    {"id": "entrepot_est", "min": 17, "max": 30, "offset": -1},
    {"id": "entrepot_ouest", "min": 18, "max": 33, "offset": 2},
    {"id": "salle_serveurs", "min": 20, "max": 28, "offset": -2},
]

THRESHOLD = 25.0
FREQUENCY = 30  # secondes

def generate_temperature(sensor):
    """Génère une température pour un capteur spécifique"""
    base = random.uniform(sensor["min"], sensor["max"])
    # Ajouter une tendance (variation lente)
    variation = random.uniform(-0.5, 0.5)
    temp = base + variation + sensor.get("offset", 0)
    return round(temp, 1)

def main():
    parser = argparse.ArgumentParser(description='Simulateur de capteurs IoT')
    parser.add_argument('--sensors', type=int, default=3, 
                       help='Nombre de capteurs à simuler (1-5)')
    parser.add_argument('--frequency', type=int, default=30,
                       help='Fréquence d\'envoi en secondes')
    args = parser.parse_args()
    
    nb_sensors = min(args.sensors, len(SENSORS))
    active_sensors = SENSORS[:nb_sensors]
    
    logger.info(f"🚀 Démarrage simulateur avec {nb_sensors} capteurs")
    for s in active_sensors:
        logger.info(f"   📡 Capteur: {s['id']} (plage {s['min']}-{s['max']}°C)")
    
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    
    counters = {s['id']: 0 for s in active_sensors}
    
    try:
        while True:
            for sensor in active_sensors:
                counters[sensor['id']] += 1
                temp = generate_temperature(sensor)
                exceed = temp > THRESHOLD
                timestamp = int(time.time())
                
                msg = {
                    "device_id": sensor['id'],
                    "timestamp": timestamp,
                    "value": temp,
                    "unit": "celsius",
                    "threshold_exceeded": exceed
                }
                
                topic = f"{BASE_TOPIC}/{sensor['id']}"
                client.publish(topic, json.dumps(msg))
                
                status = "⚠️ DEPASSEMENT" if exceed else "normal"
                logger.info(f"[{sensor['id']}:{counters[sensor['id']]}] {status} - {temp}°C")
            
            time.sleep(args.frequency)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt demandé")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()