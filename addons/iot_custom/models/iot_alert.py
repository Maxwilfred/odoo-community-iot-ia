from odoo import models, fields, api

class IoTAlert(models.Model):
    _name = 'iot.alert'
    _description = 'Alerte IoT'
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(string='Titre', required=True)
    device_id = fields.Char(string='Capteur', required=True)
    measurement_id = fields.Many2one('iot.measurement', string='Mesure associée')
    value = fields.Float(string='Valeur mesurée')
    threshold = fields.Float(string='Seuil', default=25.0)
    state = fields.Selection([
        ('new', 'Nouvelle'),
        ('in_progress', 'En cours'),
        ('done', 'Traitée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='new')
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
        ('3', 'Urgente'),
    ], string='Priorité', default='1')
    assigned_to = fields.Many2one('res.users', string='Assigné à')
    description = fields.Text(string='Description')
    resolution = fields.Text(string='Résolution')
    date_assign = fields.Datetime(string='Date assignation')
    date_done = fields.Datetime(string='Date résolution')

    def action_assign(self):
        """Prendre en charge l'alerte"""
        self.write({
            'state': 'in_progress',
            'assigned_to': self.env.user.id,
            'date_assign': fields.Datetime.now()
        })
        return True

    def action_done(self):
        """Marquer l'alerte comme traitée"""
        self.write({
            'state': 'done',
            'date_done': fields.Datetime.now()
        })
        return True

    def action_cancel(self):
        """Annuler l'alerte"""
        self.write({
            'state': 'cancelled',
            'date_done': fields.Datetime.now()
        })
        return True