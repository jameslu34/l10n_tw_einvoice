from odoo import api, SUPERUSER_ID

def post_init_hook(env):
    report = env.ref('l10n_tw_einvoice.action_report_tw_invoice', raise_if_not_found=False)
    paperformat = env.ref('l10n_tw_einvoice.paperformat_tw_invoice_57mm', raise_if_not_found=False)
    if report and paperformat:
        report.write({'paperformat_id': paperformat.id})