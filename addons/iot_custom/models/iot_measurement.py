from odoo import models, fields, api

class IoTMeasurement(models.Model):
    _name = 'iot.measurement'
    _description = 'Mesure IoT'
    _order = 'timestamp desc'

    device_id = fields.Char(string='Capteur', required=True)
    timestamp = fields.Datetime(string='Date/Heure', default=fields.Datetime.now)
    value = fields.Float(string='Température (°C)', required=True)
    threshold_exceeded = fields.Boolean(string='Seuil dépassé')
    alert_generated = fields.Boolean(string='Alerte générée')