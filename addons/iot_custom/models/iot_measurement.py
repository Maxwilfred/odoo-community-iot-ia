from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class IoTMeasurement(models.Model):
    _name = 'iot.measurement'
    _description = 'Mesure IoT'
    _order = 'timestamp desc'

    device_id = fields.Char(string='Identifiant capteur', required=True)
    timestamp = fields.Datetime(string='Date/heure', default=fields.Datetime.now)
    value = fields.Float(string='Valeur', required=True)
    unit = fields.Char(string='Unité', default='celsius')
    threshold_exceeded = fields.Boolean(string='Seuil dépassé', default=False)
    alert_generated = fields.Boolean(string='Alerte générée', default=False)
    ticket_id = fields.Many2one('project.task', string='Ticket de maintenance')
    alert_id = fields.Many2one('iot.alert', string='Alerte IoT')

    @api.model
    def create(self, vals):
        """Vérifie le seuil et crée un ticket/alerte si nécessaire"""
        # Récupérer le seuil depuis la configuration
        threshold = float(self.env['ir.config_parameter'].sudo().get_param(
            'iot.threshold_temperature', default='25.0'
        ))
        
        # Vérifier si le seuil est dépassé
        if 'threshold_exceeded' not in vals:
            vals['threshold_exceeded'] = vals.get('value', 0) > threshold
        
        # Créer l'enregistrement
        record = super().create(vals)
        
        # Si seuil dépassé et pas encore d'alerte
        if record.threshold_exceeded and not record.alert_generated:
            # Créer une alerte IoT (indépendante du module qualité)
            alert = record.generate_alert()
            record.alert_id = alert.id
            
            # Créer un ticket de maintenance
            ticket = record.generate_maintenance_ticket()
            record.ticket_id = ticket.id
            record.alert_generated = True
            
            _logger.info(f"Alerte IoT {alert.id} et ticket {ticket.id} créés pour mesure {record.id}")
        
        return record

    def generate_alert(self):
        """Crée une alerte IoT (sans dépendance au module qualité)"""
        alert = self.env['iot.alert'].create({
            'name': f'Alerte température - {self.device_id}',
            'device_id': self.device_id,
            'measurement_id': self.id,
            'value': self.value,
            'threshold': 25.0,
            'priority': '2',  # Haute priorité
            'description': f"""
                <p><strong>Capteur :</strong> {self.device_id}</p>
                <p><strong>Date :</strong> {self.timestamp}</p>
                <p><strong>Valeur mesurée :</strong> {self.value}°C</p>
                <p><strong>Seuil dépassé :</strong> 25°C</p>
                <p><strong>Actions recommandées :</strong></p>
                <ul>
                    <li>Vérifier le système de climatisation</li>
                    <li>Inspecter la zone de stockage</li>
                    <li>Vérifier les produits sensibles</li>
                </ul>
            """
        })
        return alert

    def generate_maintenance_ticket(self):
        """Crée un ticket de maintenance quand le seuil est dépassé"""
        # Chercher ou créer un projet "Maintenance IoT"
        project = self.env['project.project'].search([('name', '=', 'Maintenance IoT')], limit=1)
        if not project:
            project = self.env['project.project'].create({
                'name': 'Maintenance IoT',
                'privacy_visibility': 'portal',
            })
        
        # Chercher ou créer un tag "IoT"
        tag = self.env['project.tags'].search([('name', '=', 'IoT')], limit=1)
        if not tag:
            tag = self.env['project.tags'].create({'name': 'IoT'})
        
        # Créer le ticket
        ticket = self.env['project.task'].create({
            'name': f'Alerte IoT - Dépassement sur {self.device_id}',
            'description': f"""<h3>Alerte de température</h3>
<p><strong>Capteur :</strong> {self.device_id}</p>
<p><strong>Date :</strong> {self.timestamp}</p>
<p><strong>Valeur mesurée :</strong> {self.value}°C</p>
<p><strong>Seuil :</strong> 25°C</p>
<p><strong>Alerte associée :</strong> <a href=# data-oe-model=iot.alert data-oe-id={self.alert_id.id if self.alert_id else ''}>Voir l'alerte</a></p>

<h4>Actions recommandées :</h4>
<ul>
    <li>Vérifier le système de climatisation</li>
    <li>Inspecter la zone de stockage</li>
    <li>Vérifier les produits sensibles (ordinateurs)</li>
    <li>Enregistrer les mesures correctives</li>
</ul>

<p><em>Ticket généré automatiquement par le système IoT</em></p>""",
            'project_id': project.id,
            'user_id': self.env.ref('base.user_admin').id,
            'priority': '1',  # Haute priorité
            'tag_ids': [(4, tag.id)],
        })
        
        return ticket