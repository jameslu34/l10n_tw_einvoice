from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    tw_einvoice_logo = fields.Binary(string="電子發票 Logo")
    hide_company_name = fields.Boolean(string="列印時隱藏公司名稱", default=False)
    tw_print_b2c_detail = fields.Boolean(string="消費者發票列印明細", default=True)
    tw_vat = fields.Char(string="統一編號", related='vat', readonly=False)
    tw_invoice_footer_msg = fields.Text(string="頁尾提醒文字", default="退換貨請持本發票辦理\n若有統一編號者，不得兌獎")
    tw_einvoice_seed_password = fields.Char(string="Turnkey 種子密碼")

    tw_turnkey_enable = fields.Boolean(string="啟用 Turnkey 自動傳輸", default=False)
    tw_turnkey_protocol = fields.Selection([
        ('local', '本機傳輸'),
        ('sftp', '遠端主機 (SFTP)')
    ], string="傳輸模式", default='local')
    
    tw_turnkey_host = fields.Char(string="主機位址 (IP)")
    tw_turnkey_port = fields.Integer(string="連接埠", default=22)
    tw_turnkey_user = fields.Char(string="帳號")
    tw_turnkey_password = fields.Char(string="密碼")

    tw_turnkey_routing_id = fields.Char(string="傳送方代號 (Routing ID)")
    tw_turnkey_party_id = fields.Char(string="發票開立人代號 (Party ID)")
    
    tw_turnkey_path_xml = fields.Char(string="XML 生成暫存路徑", default="/tmp")
    tw_turnkey_path_input = fields.Char(string="Turnkey 監控路徑 (Input)", default="/opt/turnkey/UpCast/B2SSTORAGE")
    tw_turnkey_path_output = fields.Char(string="Turnkey 結果路徑 (Output)", default="/opt/turnkey/RecvTarget")
    
    tw_api_app_id = fields.Char(string="平台 AppID")
    tw_api_api_key = fields.Char(string="平台 API Key")
    tw_api_uuid = fields.Char(string="軟體憑證 UUID")