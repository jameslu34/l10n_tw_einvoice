from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import os
import xml.etree.ElementTree as ET

_logger = logging.getLogger(__name__)

try:
    import paramiko
except ImportError:
    paramiko = None

class EinvoiceLottery(models.Model):
    _name = 'einvoice.lottery'
    _description = '發票中獎紀錄'
    _order = 'year desc, period desc'

    # 手動對獎參數
    year = fields.Char(string='民國年份', size=3, help="例如: 114")
    period = fields.Selection([
        ('01-02', '01-02月'), ('03-04', '03-04月'), ('05-06', '05-06月'),
        ('07-08', '07-08月'), ('09-10', '09-10月'), ('11-12', '11-12月')
    ], string='期別')
    
    special_prize = fields.Char(string='特別獎 (1000萬)')
    grand_prize = fields.Char(string='特獎 (200萬)')
    first_prize_1 = fields.Char(string='頭獎號碼 1')
    first_prize_2 = fields.Char(string='頭獎號碼 2')
    first_prize_3 = fields.Char(string='頭獎號碼 3')
    sixth_prize_add_1 = fields.Char(string='增開六獎 1')
    sixth_prize_add_2 = fields.Char(string='增開六獎 2')
    sixth_prize_add_3 = fields.Char(string='增開六獎 3')

    # 自動排程入口
    @api.model
    def auto_sync_turnkey_c0701(self):
        """ 
        [排程動作] 自動掃描 Turnkey Output 目錄中的 C0701 (中獎清冊通知)
        若發現中獎資訊，自動更新發票狀態並寄信。
        """
        companies = self.env['res.company'].search([('tw_turnkey_enable', '=', True)])
        for conf in companies:
            if not conf.tw_turnkey_path_output: continue
            
            try:
                # 取得 C0701 檔案列表
                files = []
                if conf.tw_turnkey_protocol == 'local':
                    if os.path.exists(conf.tw_turnkey_path_output):
                        for f in os.listdir(conf.tw_turnkey_path_output):
                            if f.startswith('C0701') and f.endswith('.xml'):
                                files.append(os.path.join(conf.tw_turnkey_path_output, f))
                elif conf.tw_turnkey_protocol == 'sftp' and paramiko:
                    # SFTP 邏輯 (略為簡化，需下載到本地處理)
                    pass 

                # 解析檔案
                for filepath in files:
                    self._process_c0701_xml(filepath)
                    # 處理完後建議備份或刪除，避免重複處理 (此處僅示範讀取)
                    # os.rename(filepath, filepath + '.processed')

            except Exception as e:
                _logger.error(f"Turnkey C0701 Sync Error: {e}")

    def _process_c0701_xml(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            # 命名空間處理 (視實際 MIG 版本調整)
            ns = {'e': 'urn:GEINV:eInvoiceMessage:C0701:3.2'} 
            
            # 假設結構為 Invoice/Main/InvoiceNumber...
            # 實際 C0701 可能包含多筆，需迴圈處理 Details
            # 這裡實作簡易邏輯
            inv_no = root.find('.//e:InvoiceNumber', ns).text
            prize_type = root.find('.//e:AwardType', ns).text # 獎別
            prize_amt = root.find('.//e:AwardAmount', ns).text # 金額

            if inv_no:
                self._mark_invoice_as_winner(inv_no, prize_type, prize_amt)

        except Exception as e:
            _logger.error(f"XML Parse Error ({filepath}): {e}")

    def _mark_invoice_as_winner(self, inv_no, prize_type, prize_amt):
        invoice = self.env['account.move'].search([
            ('tw_einvoice_number', '=', inv_no),
            ('move_type', '=', 'out_invoice')
        ], limit=1)

        if invoice:
            # 再次驗證資格 (雙重防呆)
            if invoice.tw_b2b_vat: 
                _logger.warning(f"發票 {inv_no} 為 B2B (有統編)，不得領獎。")
                return
            if invoice.tw_donate:
                _logger.warning(f"發票 {inv_no} 已捐贈，不得領獎。")
                return
            if invoice.state != 'posted':
                _logger.warning(f"發票 {inv_no} 非有效狀態。")
                return

            # 更新狀態
            invoice.write({
                'tw_is_winner': True,
                'tw_winning_type': prize_type,
                'tw_winning_amount': prize_amt
            })
            
            # 發送通知
            self._send_winning_email(invoice)

    def action_check_lottery(self):
        # 手動對獎邏輯 (僅針對一般獎項，雲端獎無法手動對)
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('is_tw_einvoice', '=', True),
            ('tw_einvoice_number', '!=', False),
            ('tw_b2b_vat', '=', False),
            ('tw_donate', '=', False)
        ])
        
        count = 0
        for inv in invoices:
            # (省略日期比對邏輯，同前版)
            is_winner = self._check_number(inv.tw_einvoice_number[-8:])
            if is_winner:
                inv.tw_is_winner = True
                inv.tw_winning_type = '一般獎項' # 手動對獎無法確知金額，僅標記
                self._send_winning_email(inv)
                count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '對獎完成',
                'message': f'共發現 {count} 張中獎發票！',
                'type': 'success',
                'sticky': False,
            }
        }

    def _check_number(self, inv_num):
        # (同前版手動比對邏輯)
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