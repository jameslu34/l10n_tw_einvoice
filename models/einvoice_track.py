from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EinvoiceTrack(models.Model):
    _name = 'einvoice.track'
    _description = '電子發票字軌'
    _order = 'year desc, period desc'

    company_id = fields.Many2one('res.company', string='公司', required=True, default=lambda self: self.env.company)
    year = fields.Char(string='民國年份', size=3, required=True)
    period = fields.Selection([
        ('01-02', '01-02月'), ('03-04', '03-04月'), ('05-06', '05-06月'),
        ('07-08', '07-08月'), ('09-10', '09-10月'), ('11-12', '11-12月')
    ], string='期別', required=True)
    track_code = fields.Char(string='字軌代號', size=2, required=True)
    
    start_no = fields.Integer(string='起始號碼', required=True, default=0)
    end_no = fields.Integer(string='結束號碼', required=True, default=99999999)
    current_no = fields.Integer(string='目前已使用號碼', required=True, default=0)
    
    type = fields.Selection([
        ('07', '一般稅額計算'),
        ('08', '特種稅額計算')
    ], string='發票類別', default='07', required=True)

    active = fields.Boolean(default=True)

    @api.constrains('start_no', 'end_no', 'current_no')
    def _check_numbers(self):
        for record in self:
            if record.start_no >= record.end_no:
                raise ValidationError("起始號碼必須小於結束號碼")
            if record.current_no != 0 and record.current_no < record.start_no:
                raise ValidationError("目前號碼不能小於起始號碼")

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.year}年 {record.period} ({record.track_code})"
            result.append((record.id, name))
        return result