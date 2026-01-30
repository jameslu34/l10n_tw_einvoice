{
    'name': '臺灣電子發票',
    'version': '1.0',
    'category': 'Accounting/Localizations',
    'summary': '財政部電子發票模組',
    'description': """
        臺灣電子發票
        專為 Odoo 系統打造的「臺灣電子發票」擴充模組。
    """,
    'author': '博客電腦企業社',
    'website': 'https://github.com/jameslu34/l10n-tw-einvoice',
    'license': 'LGPL-3',
    'depends': ['account', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'report/paperformat.xml',
        'report/ir_actions_report.xml',
        'views/report_templates.xml',
        'views/account_move_views.xml',
        'views/einvoice_track_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'l10n_tw_einvoice/static/src/css/thermal_styles.css',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'application': True,
    'installable': True,
}