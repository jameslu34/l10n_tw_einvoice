from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EinvoiceLottery(models.Model):
    _name = 'einvoice.lottery'
    _description = '發票中獎號碼'
    _order = 'year desc, period desc'

    year = fields.Char(string='民國年份', size=3, required=True)
    period = fields.Selection([
        ('01-02', '01-02月'), ('03-04', '03-04月'), ('05-06', '05-06月'),
        ('07-08', '07-08月'), ('09-10', '09-10月'), ('11-12', '11-12月')
    ], string='期別', required=True)
    
    special_prize = fields.Char(string='特別獎 (1000萬)')
    grand_prize = fields.Char(string='特獎 (200萬)')
    first_prize_1 = fields.Char(string='頭獎號碼 1')
    first_prize_2 = fields.Char(string='頭獎號碼 2')
    first_prize_3 = fields.Char(string='頭獎號碼 3')
    sixth_prize_add_1 = fields.Char(string='增開六獎 1')
    sixth_prize_add_2 = fields.Char(string='增開六獎 2')
    sixth_prize_add_3 = fields.Char(string='增開六獎 3')

    def action_check_lottery(self):
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('is_tw_einvoice', '=', True),
            ('tw_einvoice_number', '!=', False)
        ])
        
        winning_count = 0
        for inv in invoices:
            inv_date = inv.invoice_date
            roc_year = str(inv_date.year - 1911)
            month = inv_date.month
            
            period_map = {1:'01-02', 2:'01-02', 3:'03-04', 4:'03-04', 5:'05-06', 6:'05-06', 7:'07-08', 8:'07-08', 9:'09-10', 10:'09-10', 11:'11-12', 12:'11-12'}
            current_period = period_map.get(month)
            
            if roc_year == self.year and current_period == self.period:
                is_winner = self._check_number(inv.tw_einvoice_number[-8:])
                if is_winner:
                    inv.tw_is_winner = True
                    self._send_winning_email(inv)
                    winning_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '對獎完成',
                'message': f'共發現 {winning_count} 張中獎發票！通知信已發送。',
                'type': 'success',
                'sticky': False,
            }
        }

    def _check_number(self, inv_num):
        if not inv_num: return False
        if self.special_prize and inv_num == self.special_prize: return True
        if self.grand_prize and inv_num == self.grand_prize: return True
        
        targets = [self.first_prize_1, self.first_prize_2, self.first_prize_3]
        for t in targets:
            if t and inv_num[-3:] == t[-3:]: return True
            
        adds = [self.sixth_prize_add_1, self.sixth_prize_add_2, self.sixth_prize_add_3]
        for a in adds:
            if a and inv_num[-3:] == a: return True
            
        return False

    def _send_winning_email(self, invoice):
        template = self.env.ref('l10n_tw_einvoice.email_template_tw_invoice_winning', raise_if_not_found=False)
        if template and invoice.partner_id.email:
            template.send_mail(invoice.id, force_send=True)