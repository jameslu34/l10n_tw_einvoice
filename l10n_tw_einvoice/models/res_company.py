from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    tw_einvoice_logo = fields.Binary(string="電子發票 Logo")
    hide_company_name = fields.Boolean(string="列印時隱藏公司名稱", default=False)
    tw_print_b2c_detail = fields.Boolean(string="B2C 列印交易明細", default=True)
    tw_vat = fields.Char(string="統一編號", related='vat', readonly=False)
    tw_invoice_footer_msg = fields.Text(string="自訂發票底部訊息", default="退換貨請持本發票辦理\n若有統一編號者，不得兌獎")
    tw_einvoice_seed_password = fields.Char(string="Turnkey 種子密碼 (AES Key)")

    tw_turnkey_enable = fields.Boolean(string="啟用 Turnkey 整合", default=False)
    tw_turnkey_routing_id = fields.Char(string="傳送方代號 (Routing ID)")
    tw_turnkey_party_id = fields.Char(string="發票開立人代號 (Party ID)")
    tw_turnkey_env = fields.Selection([
        ('test', '測試環境 (Test)'),
        ('prod', '正式環境 (Production)')
    ], string="Turnkey 環境", default='test')

    tw_turnkey_path_xml = fields.Char(string="XML 生成路徑", default="/opt/turnkey/xml_source")
    tw_turnkey_path_input = fields.Char(string="Turnkey 監控路徑 (Input)", default="/opt/turnkey/jbox/input")
    tw_turnkey_path_output = fields.Char(string="Turnkey 結果路徑 (Output)", default="/opt/turnkey/jbox/output")
    tw_turnkey_path_backup = fields.Char(string="備份路徑 (Backup)", default="/opt/turnkey/xml_backup")

    tw_api_app_id = fields.Char(string="平台 AppID")
    tw_api_api_key = fields.Char(string="平台 API Key")
    tw_api_uuid = fields.Char(string="軟體憑證 UUID")