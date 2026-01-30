# **臺灣電子發票模組 (Taiwan E-Invoice) for Odoo 19**

**符合財政部規範之 B2B/B2C 電子發票解決方案（開源版）**

由 **博客電腦企業社** 開發並回饋社群。本模組專為 Odoo 19 設計，提供從開立、配號到列印的完整解決方案，特別針對 5.7cm 熱感紙與 High DPI 條碼列印進行優化。

## **✨ 主要功能 (Features)**

* **完全法規遵循**：  
  * 支援 **B2B (統一編號)** 與 **B2C (二聯式)** 格式。  
  * **自動字軌配號** (Track & Numbering)，含期別防呆檢核。  
  * 符合 MIG 規範的 **QR Code** (含加密區段與完整明細) 與 **Code39 一維條碼** (無檢查碼)。  
* **精準列印**：  
  * 專為 **5.7cm 熱感紙** 設計的 RWD 版面。  
  * **High DPI 技術**：伺服器端直接生成高解析度條碼圖片，徹底解決模糊與藍色問號問題。  
* **高度自動化與彈性**：  
  * **彈性開關**：每一張發票皆可獨立選擇「是否開立電子發票」，方便內部記帳與正式稅務區隔。  
  * **企業級整合**：選擇公司客戶時，自動帶入統一編號；選擇消費者時，自動切換載具模式。  
  * **載具支援**：完整支援手機條碼 (/)、自然人憑證 (TP) 格式檢查。  
* **Turnkey 準備就緒**：  
  * 內建完整 Turnkey 傳輸參數設定 (Routing ID, Party ID) 與檔案交換路徑配置。  
  * 預留財政部大平台 API 介接欄位。

## **🚀 安裝方式 (Installation)**

### **方法一：直接下載安裝**

1. 下載本專案 Zip 檔。  
2. 將 l10n\_tw\_einvoice 資料夾放入您的 Odoo addons 目錄。  
3. 重新啟動 Odoo 服務。  
4. 進入 Odoo **應用程式 (Apps)**，搜尋 "Taiwan E-Invoice" 並點擊安裝。

### **方法二：Git Clone (推薦開發者)**

cd /path/to/your/odoo/addons  
git clone \[https://github.com/YourGithubID/odoo-l10n-tw-einvoice.git\](https://github.com/YourGithubID/odoo-l10n-tw-einvoice.git)  
sudo service odoo restart

## **⚙️ 設定說明 (Configuration)**

安裝後請至 **設定 \> 會計 \> 臺灣電子發票設定** 進行配置：

1. **電子發票 Logo**：上傳您的公司 Logo (建議寬度 300-500px 黑白圖片)。  
2. **字軌管理**：點擊「管理電子發票字軌」設定目前的字軌與號碼範圍。  
3. **隱藏公司名稱**：若您的 Logo 已包含文字，可勾選此項。  
4. **B2C 列印明細**：可選擇是否預設列印消費者發票的交易明細。  
5. **Turnkey 整合**：若需上傳財政部，請勾選並設定 Routing ID 與 Party ID。

## **🖨️ 使用方法 (Usage)**

1. 建立新的 **客戶發票 (Customer Invoice)**。  
2. 確認 **「開立電子發票」** 開關已開啟 (預設為開啟)。  
3. **B2C (消費者)**：  
   * 載具類型選擇「手機條碼」或「自然人憑證」並掃描。  
   * 或保留為「無 (列印紙本)」。  
4. **B2B (公司)**：  
   * 若客戶資料已設定統編，系統會自動帶入。  
   * 或手動選擇「統一編號」並輸入。  
5. 點擊 **確認 (Confirm)**，系統將自動取號並生成條碼。  
6. 點擊頂部的 **「列印電子發票」** 紫色按鈕即可下載 PDF。

## **🤝 貢獻與回饋 (Contribution)**

歡迎提交 Issue 或 Pull Request 來協助改進此模組。我們希望透過開源，讓臺灣的中小企業能有更優質的 ERP 體驗。

* **開發者**：博客電腦企業社  
* **授權**：LGPL-3 (GNU Lesser General Public License v3.0)
