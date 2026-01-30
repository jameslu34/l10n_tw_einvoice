from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import random
import base64
import logging
import re

try:
    from reportlab.graphics.barcode import createBarcodeDrawing
    from reportlab.graphics import renderPM
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.warning("ReportLab not found, barcode generation might fail.")

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_tw_einvoice = fields.Boolean(string="開立電子發票", default=True, copy=False, 
                                    help="勾選此項，過帳時將自動取用臺灣電子發票字軌並產生條碼。")

    tw_einvoice_track_id = fields.Many2one('einvoice.track', string="使用字軌", readonly=True, copy=False)
    tw_einvoice_number = fields.Char(string="發票號碼", readonly=True, copy=False, index=True)
    tw_random_number = fields.Char(string="隨機碼", size=4, readonly=True, copy=False)
    tw_barcode_content = fields.Char(string="一維條碼內容", readonly=True, copy=False)
    
    tw_qr_content_left = fields.Char(string="左 QR Code", readonly=True, copy=False)
    tw_qr_content_right = fields.Char(string="右 QR Code", readonly=True, copy=False)

    tw_carrier_type = fields.Selection([
        ('none', '無 (列印紙本)'),
        ('3J0002', '手機條碼'),
        ('CQ0001', '自然人憑證'),
        ('vat', '統一編號')
    ], string="發票處理", default='none', copy=False)

    tw_carrier_id = fields.Char(string="載具號碼", copy=False)
    tw_b2b_vat = fields.Char(string="統一編號", copy=False, size=8)

    @api.onchange('partner_id')
    def _onchange_partner_id_tw_einvoice(self):
        if not self.is_tw_einvoice:
            return
        if self.partner_id and self.partner_id.vat:
            self.tw_carrier_type = 'vat'
            self.tw_b2b_vat = self.partner_id.vat
            self.tw_carrier_id = False
        else:
            self.tw_carrier_type = 'none'
            self.tw_b2b_vat = False
            self.tw_carrier_id = False

    @api.constrains('is_tw_einvoice', 'tw_carrier_type', 'tw_carrier_id', 'tw_b2b_vat')
    def _check_tw_einvoice_data(self):
        for move in self:
            if not move.is_tw_einvoice:
                continue
            if move.tw_carrier_type == '3J0002':
                if not move.tw_carrier_id or not re.match(r'^/[0-9A-Z.\-+]{7}$', move.tw_carrier_id):
                    raise ValidationError("手機條碼格式錯誤！\n必須以 '/' 開頭，總長 8 碼。")
            elif move.tw_carrier_type == 'CQ0001':
                if not move.tw_carrier_id or not re.match(r'^[A-Z]{2}[0-9]{14}$', move.tw_carrier_id):
                    raise ValidationError("自然人憑證格式錯誤！\n必須為 2 碼英文 + 14 碼數字，總長 16 碼。")
            elif move.tw_carrier_type == 'vat':
                if not move.tw_b2b_vat or not re.match(r'^[0-9]{8}$', move.tw_b2b_vat):
                    raise ValidationError("統一編號格式錯誤！\n必須為 8 碼數字。")

    def action_post(self):
        for move in self:
            if move.move_type == 'out_invoice' and move.is_tw_einvoice and not move.tw_einvoice_number:
                move._assign_tw_einvoice_number()
        return super(AccountMove, self).action_post()

    def _assign_tw_einvoice_number(self):
        self.ensure_one()
        invoice_date = self.invoice_date or fields.Date.today()
        roc_year = str(invoice_date.year - 1911)
        month_str = invoice_date.strftime("%m")
        month_int = invoice_date.month
        
        month_map = {
            1: '01-02', 2: '01-02', 3: '03-04', 4: '03-04',
            5: '05-06', 6: '05-06', 7: '07-08', 8: '07-08',
            9: '09-10', 10: '09-10', 11: '11-12', 12: '11-12'
        }
        target_period = month_map.get(month_int)
        
        domain = [
            ('company_id', '=', self.company_id.id),
            ('year', '=', roc_year),
            ('period', '=', target_period),
            ('active', '=', True)
        ]
        
        track = self.env['einvoice.track'].search(domain, limit=1, order='id desc')

        if not track:
            raise UserError(f"錯誤：找不到 {roc_year}年 {target_period} 的有效字軌，請先至「設定 > 電子發票字軌」建立。")

        next_no = track.current_no + 1 if track.current_no >= track.start_no else track.start_no
        
        if next_no > track.end_no:
            raise UserError(f"字軌 {track.track_code} 號碼已用盡！")

        full_number = f"{track.track_code}{str(next_no).zfill(8)}"
        random_code = str(random.randint(0, 9999)).zfill(4)
        barcode_str = f"{roc_year.zfill(3)}{month_str}{full_number}{random_code}"

        track.sudo().write({'current_no': next_no})
        
        self.write({
            'tw_einvoice_track_id': track.id,
            'tw_einvoice_number': full_number,
            'tw_random_number': random_code,
            'tw_barcode_content': barcode_str
        })
        self._generate_qr_content()

    def _generate_qr_content(self):
        for move in self:
            try:
                date_str = str(move.invoice_date.year - 1911) + move.invoice_date.strftime("%m%d")
                sales_amt = hex(int(move.amount_untaxed))[2:].upper().zfill(8)
                total_amt = hex(int(move.amount_total))[2:].upper().zfill(8)
                
                if move.tw_carrier_type == 'vat' and move.tw_b2b_vat:
                    buyer_id = move.tw_b2b_vat
                else:
                    buyer_id = "00000000"
                
                seller_id = (move.company_id.vat or "00000000")[:8]
                rnd = move.tw_random_number or '0000'
                fake_encrypt = "0" * 24 
                
                header = f"{move.tw_einvoice_number}{date_str}{rnd}{sales_amt}{total_amt}{buyer_id}{seller_id}{fake_encrypt}"
                
                product_items = []
                for line in move.invoice_line_ids:
                    if line.display_type == 'product':
                        p_name = (line.name or "").replace(":", "：").replace("\n", "").strip()
                        qty = int(line.quantity)
                        price = int(line.price_unit)
                        item_str = f"{p_name}:{qty}:{price}"
                        product_items.append(item_str)
                
                details_str = ":".join(product_items)
                
                if details_str:
                    full_content = f"{header}:**{details_str}"
                else:
                    full_content = header

                limit = 480 
                if len(full_content) <= limit:
                    move.tw_qr_content_left = full_content
                    move.tw_qr_content_right = "**" 
                else:
                    move.tw_qr_content_left = full_content[:limit]
                    move.tw_qr_content_right = "**" + full_content[limit:]
                
            except Exception as e:
                _logger.error(f"Generate QR Error: {e}")
                move.tw_qr_content_left = "ERROR"

    def get_barcode_b64(self, barcode_type, value, width, height):
        if not value: return ""
        try:
            from odoo.tools.image import image_data_uri
        except ImportError:
            def image_data_uri(base64_source):
                return 'data:image/png;base64,' + base64_source.decode('utf-8')

        try:
            if barcode_type in ['Code39', 'Standard39']:
                try:
                    drawing = createBarcodeDrawing('Standard39', value=str(value), checksum=0, width=width, height=height, humanReadable=False)
                    barcode_bytes = renderPM.drawToString(drawing, fmt='PNG')
                    return image_data_uri(base64.b64encode(barcode_bytes))
                except Exception:
                    pass
            report_model = self.env['ir.actions.report']
            barcode_bytes = report_model.barcode(barcode_type, value, width=width, height=height, humanreadable=False)
            return image_data_uri(base64.b64encode(barcode_bytes))
        except Exception as e:
            _logger.error(f"Barcode Error: {e}")
            return ""

    def action_print_tw_einvoice(self):
        self.ensure_one()
        if not self.tw_einvoice_number:
            raise UserError("此發票未設定為電子發票，無法列印證明聯。")
        return self.env.ref('l10n_tw_einvoice.action_report_tw_invoice').report_action(self)