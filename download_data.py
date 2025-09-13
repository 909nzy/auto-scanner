# 文件名: download_data.py
import yfinance as yf
import os
import time

# --- 您可以在这里修改想扫描的股票代码列表 ---
TICKERS = [
    '600519.SS', # 贵州茅台
    '000001.SZ', # 平安银行
    '300750.SZ', # 宁德时代
    '600036.SS', # 招商银行
]
# ------------------------------------------

DATA_PATH = 'stock_data'
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

for ticker in TICKERS:
    try:
        print(f"开始下载 {ticker} 的历史数据...")
        data = yf.download(ticker, start='2020-01-01', end=None, progress=False)
        if not data.empty:
            file_path = os.path.join(DATA_PATH, f"{ticker}.csv")
            data.to_csv(file_path)
            print(f"{ticker} 数据已保存到 {file_path}")
        else:
            print(f"未能获取 {ticker} 的数据。")
    except Exception as e:
        print(f"下载 {ticker} 时出错: {e}")
    time.sleep(1)

print("\n所有数据下载完成！")
