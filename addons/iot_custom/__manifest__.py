{
    'name': 'IoT Custom',
    'version': '1.0',
    'summary': 'Module IoT pour capteurs de température',
    'description': """
        Module personnalisé pour l'intégration de capteurs IoT
        - Gestion des mesures de température
        - Déclenchement d'alertes qualité
    """,
    'author': 'DJASRANGUE Maxwilfred',
    'category': 'IoT',
    'depends': ['base', 'stock', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/iot_measurement_views.xml',
        'views/iot_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}