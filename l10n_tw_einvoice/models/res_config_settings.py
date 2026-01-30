from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tw_einvoice_logo = fields.Binary(related='company_id.tw_einvoice_logo', readonly=False)
    tw_hide_company_name = fields.Boolean(related='company_id.hide_company_name', readonly=False)
    tw_print_b2c_detail = fields.Boolean(related='company_id.tw_print_b2c_detail', readonly=False)
    tw_invoice_footer_msg = fields.Text(related='company_id.tw_invoice_footer_msg', readonly=False)
    tw_einvoice_seed_password = fields.Char(related='company_id.tw_einvoice_seed_password', readonly=False)
    
    tw_turnkey_enable = fields.Boolean(related='company_id.tw_turnkey_enable', readonly=False)
    tw_turnkey_protocol = fields.Selection(related='company_id.tw_turnkey_protocol', readonly=False)
    tw_turnkey_host = fields.Char(related='company_id.tw_turnkey_host', readonly=False)
    tw_turnkey_port = fields.Integer(related='company_id.tw_turnkey_port', readonly=False)
    tw_turnkey_user = fields.Char(related='company_id.tw_turnkey_user', readonly=False)
    tw_turnkey_password = fields.Char(related='company_id.tw_turnkey_password', readonly=False)

    tw_turnkey_routing_id = fields.Char(related='company_id.tw_turnkey_routing_id', readonly=False)
    tw_turnkey_party_id = fields.Char(related='company_id.tw_turnkey_party_id', readonly=False)
    
    tw_turnkey_path_xml = fields.Char(related='company_id.tw_turnkey_path_xml', readonly=False)
    tw_turnkey_path_input = fields.Char(related='company_id.tw_turnkey_path_input', readonly=False)
    
    tw_api_app_id = fields.Char(related='company_id.tw_api_app_id', readonly=False)
    tw_api_api_key = fields.Char(related='company_id.tw_api_api_key', readonly=False)
    tw_api_uuid = fields.Char(related='company_id.tw_api_uuid', readonly=False)