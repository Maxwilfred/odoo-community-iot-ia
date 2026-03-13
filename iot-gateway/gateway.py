#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import logging
import xmlrpc.client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature/#"

ODOO_HOST = "localhost"
ODOO_PORT = 8069
ODOO_DB = "odoo_community"
ODOO_USER = "d.maxwilfredb1@gmail.com"
ODOO_PASSWORD = "admin"

class Gateway:
    def __init__(self):
        self.odoo = None
        
    def connect_odoo(self):
        try:
            url = f"http://{ODOO_HOST}:{ODOO_PORT}"
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
            if uid:
                self.odoo = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
                self.uid = uid
                logger.info("Connecté à Odoo")
                return True
        except Exception as e:
            logger.error(f"Erreur Odoo: {e}")
            return False
    
    def send_to_odoo(self, data):
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(data['timestamp'])
            self.odoo.execute_kw(
                ODOO_DB, self.uid, ODOO_PASSWORD,
                'iot.measurement', 'create',
                [{
                    'device_id': data['device_id'],
                    'timestamp': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'value': data['value'],
                    'unit': data.get('unit', 'celsius'),
                    'threshold_exceeded': data.get('threshold_exceeded', False),
                }]
            )
            logger.info(f"Mesure envoyée: {data['value']}°C")
        except Exception as e:
            logger.error(f"Erreur envoi: {e}")
    
    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
            self.send_to_odoo(data)
        except Exception as e:
            logger.error(f"Erreur: {e}")
    
    def run(self):
        if not self.connect_odoo():
            return
        client = mqtt.Client()
        client.on_message = self.on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(MQTT_TOPIC)
        logger.info("Passerelle démarrée")
        client.loop_forever()

if __name__ == "__main__":
    g = Gateway()
    g.run()