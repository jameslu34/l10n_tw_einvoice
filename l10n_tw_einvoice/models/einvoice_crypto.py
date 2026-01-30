# models/einvoice_crypto.py
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import time

class EInvoiceCrypto:
    def __init__(self, aes_key_hex, iv_base64='Dt8lyToo17X/XkXaQvihuA=='):
        """
        初始化加密器
        aes_key_hex: 財政部配發的 AES Key (32位元十六進制字串)
        iv_base64: 財政部規定的初始向量 (預設值通常固定，但也保留設定彈性)
        """
        self.key = bytes.fromhex(aes_key_hex)
        self.iv = base64.b64decode(iv_base64)
        self.block_size = 16

    def encrypt(self, plain_text):
        """
        執行 AES-128-CBC 加密與 Base64 編碼
        """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # PKCS#7 Padding: 補足 block_size 倍數
        padded_data = pad(plain_text.encode('utf-8'), self.block_size)
        encrypted_bytes = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted_bytes).decode('utf-8')

# 整合至 Account Move
class AccountMove(models.Model):
    #... (前略)
    
    def tw_generate_left_qrcode(self):
        """
        生成左側 QR Code 內容
        格式：發票字軌(10) + 日期(7) + 隨機碼(4) + 銷售額(8 hex) + 總額(8 hex) + 買方統編(8) + 賣方統編(8) + 加密驗證碼(24)
        """
        self.ensure_one()
        
        # 1. 準備欄位
        inv_no = self.tw_einvoice_number
        roc_date = self.tw_get_roc_date_str() # 自訂方法轉民國年
        random_no = self.tw_random_number
        sales_amt = format(int(self.amount_untaxed), '08X') # 轉 8位 16進制
        total_amt = format(int(self.amount_total), '08X')
        buyer_id = self.partner_id.vat or '00000000'
        seller_id = self.company_id.vat
        
        # 2. 準備加密明文 (發票號碼 + 隨機碼)
        plain_payload = f"{inv_no}{random_no}"
        
        # 3. 執行加密
        crypto = EInvoiceCrypto(self.company_id.tw_aes_key)
        encrypted_str = crypto.encrypt(plain_payload)
        
        # 4. 組合最終字串
        qr_content = f"{inv_no}{roc_date}{random_no}{sales_amt}{total_amt}{buyer_id}{seller_id}{encrypted_str}:**********:1:1:1"
        return qr_content

    def tw_generate_right_qrcode(self):
        """
        生成右側 QR Code 內容 (商品明細)
        格式：**商品1:數量:單價:商品2:數量:單價...
        """
        self.ensure_one()
        items_str = "**"
        for line in self.invoice_line_ids:
            # 需處理商品名稱中的冒號，避免分隔符號混淆
            safe_name = line.name.replace(':', '：')
            items_str += f"{safe_name}:{int(line.quantity)}:{int(line.price_unit)}:"
            
        return items_str