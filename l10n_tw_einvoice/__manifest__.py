{
    'name': '臺灣電子發票',
    'version': '1.0',
    'category': 'Accounting/Localizations',
    'summary': '符合財政部規範之電子發票系統 (含自動兌獎與 Turnkey 傳輸)',
    'description': """
        臺灣電子發票管理系統
        
        這是一套專為臺灣企業設計的電子發票解決方案。
        
        核心功能：
        1. 智慧開立：自動判斷載具與統編，自動配發字軌。
        2. 合規列印：5.7cm 熱感紙格式，高解析度條碼。
        3. 自動傳輸：支援 Turnkey (本機/SFTP) 上傳。
        4. 自動兌獎：內建中獎號碼管理與通知。
    """,
    'author': '博客電腦企業社',
    'website': 'https://www.paq.com.tw',
    'license': 'LGPL-3',
    'depends': ['account', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'report/paperformat.xml',
        'report/ir_actions_report.xml',
        'views/report_templates.xml',
        'views/account_move_views.xml',
        'views/einvoice_track_views.xml',
        'views/einvoice_lottery_views.xml',
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