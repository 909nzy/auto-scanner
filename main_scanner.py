# 文件名: main_scanner.py
import pandas as pd
from hurst import compute_Hc
import os

def analyze_stock(ticker, data):
    print(f"\n--- 正在分析 {ticker} ---")
    if len(data) < 250:
        print(f"分析中止：数据量不足250天。")
        return
    data_weekly = data.resample('W-FRI').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna()
    if len(data_weekly) < 60:
        print(f"分析中止：周线数据不足60周。")
        return
    exp1_w = data_weekly['Close'].ewm(span=12, adjust=False).mean()
    exp2_w = data_weekly['Close'].ewm(span=26, adjust=False).mean()
    macd_w = exp1_w - exp2_w
    signal_w = macd_w.ewm(span=9, adjust=False).mean()
    is_above_signal = macd_w > signal_w
    crosses = (is_above_signal != is_above_signal.shift(1))
    if not crosses.any() or len(crosses[crosses]) < 2:
        print("分析中止：无法构成完整MACD周期。")
        return
    cross_indices = crosses[crosses].index
    last_cross_idx, prev_cross_idx = cross_indices[-1], cross_indices[-2]
    if is_above_signal.loc[last_cross_idx]:
         print("左侧不合格：不处于回调状态。")
         return
    rally_period_weekly = data_weekly.loc[prev_cross_idx:last_cross_idx]
    low_before_rally = data_weekly['Low'].loc[:prev_cross_idx].tail(10).min()
    high_during_rally = rally_period_weekly['High'].max()
    if high_during_rally / low_before_rally < 2.0:
        print(f"左侧不合格：上涨未翻倍。")
        return
    print(f"左侧合格：发现周线翻倍行情！")
    correction_start_date = last_cross_idx
    correction_data_daily = data.loc[correction_start_date:]
    rally_duration_weeks = len(rally_period_weekly)
    correction_duration_days = len(correction_data_daily)
    if correction_duration_days < (rally_duration_weeks * 7 * 0.67):
         print(f"中部不合格：回调时间不足。")
         return
    print("中部合格：回调时间充分。")
    exp1_d = data['Close'].ewm(span=12, adjust=False).mean()
    exp2_d = data['Close'].ewm(span=26, adjust=False).mean()
    macd_d = exp1_d - exp2_d
    signal_d = macd_d.ewm(span=9, adjust=False).mean()
    if not (macd_d.iloc[-2] < signal_d.iloc[-2] and macd_d.iloc[-1] > signal_d.iloc[-1]):
        print("右侧无信号：今天不是MACD金叉日。")
        return
    print("右侧信号：今天出现MACD金叉！正在多因子确认...")
    ma30 = data['Close'].rolling(window=30).mean()
    if data['Close'].iloc[-1] < ma30.iloc[-1]:
        print("确认失败：股价位于30日均线下方。")
        return
    low_recent = data['Low'].tail(10).min()
    low_correction_period = correction_data_daily['Low'].min()
    if low_recent <= low_correction_period:
        print("确认失败：近期创下回调期新低。")
        return
    H, _, _ = compute_Hc(data['Close'].values, kind='price', simplified=True)
    if H < 0.5:
        print(f"确认失败：市场为均值回归状态 (Hurst={H:.2f})。")
        return
    print(f"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"!!! 【蓝色买点信号】发现: {ticker} on {data.index[-1].date()} !!!")
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

def run_scanner():
    DATA_PATH = 'stock_data'
    if not os.path.exists(DATA_PATH): return
    data_files = [f for f in os.listdir(DATA_PATH) if f.endswith('.csv')]
    if not data_files: return
    for file_name in data_files:
        ticker = file_name.split('.csv')[0]
        file_path = os.path.join(DATA_PATH, file_name)
        df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        if len(df) > 250:
            analyze_stock(ticker, df)

if __name__ == '__main__':
    run_scanner()
