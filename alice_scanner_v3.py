import yfinance as yf
import pandas as pd
import twstock
import requests
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. 抓取三大法人數據 (上市)
def get_institutional_data():
    """
    抓取今日 (或最近交易日) 的法人買賣超
    """
    today = datetime.now()
    # 如果今天是週末，向前找最近的週五
    if today.weekday() >= 5:
        offset = today.weekday() - 4
        today = today - timedelta(days=offset)
    
    date_str = today.strftime("%Y%m%d")
    url = f"https://www.twse.com.tw/rwd/zh/fund/T86FU1?date={date_str}&selectType=ALLBUT0999&response=json"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('stat') != 'OK':
            print(f"⚠️ {date_str} 無法人數據，嘗試前一交易日...")
            yesterday = today - timedelta(days=1)
            date_str = yesterday.strftime("%Y%m%d")
            url = f"https://www.twse.com.tw/rwd/zh/fund/T86FU1?date={date_str}&selectType=ALLBUT0999&response=json"
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

        rows = data.get('data', [])
        inst_map = {}
        for row in rows:
            symbol = row[0].strip()
            foreign = int(row[4].replace(',', ''))
            trust = int(row[10].replace(',', ''))
            inst_map[f"{symbol}.TW"] = {"外資": foreign, "投信": trust}
        return inst_map
    except:
        return {}

# 2. 取得全市場清單
def get_all_taiwan_symbols():
    codes = []
    for code, item in twstock.codes.items():
        if item.type == '股票' and (item.market == '上市' or item.market == '上櫃'):
            suffix = ".TW" if item.market == '上市' else ".TWO"
            codes.append(f"{code}{suffix}")
    return codes

# 3. 掃描邏輯 (V3: 加入籌碼面分析)
def scan_logic(symbol, inst_map):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="40d")
        if df.empty or len(df) < 20: return None

        df['5MA'] = df['Close'].rolling(window=5).mean()
        df['20MA'] = df['Close'].rolling(window=20).mean()
        df['Vol_MA5'] = df['Volume'].rolling(window=5).mean()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        is_bullish = latest['Close'] > latest['5MA'] > latest['20MA']
        volume_spike = latest['Volume'] > latest['Vol_MA5'] * 1.5
        price_change = (latest['Close'] - prev['Close']) / prev['Close'] * 100
        recent_high = df['Close'].iloc[-20:].max()
        is_breakout = latest['Close'] >= recent_high * 0.98
        
        # 籌碼面判斷
        inst = inst_map.get(symbol, {"外資": 0, "投信": 0})
        is_trust_buying = inst["投信"] > 500  # 投信大買 500 張以上
        is_foreign_buying = inst["外資"] > 1000 # 外資大買 1000 張以上
        
        # 如果強勢且有法人加持，加分！
        if is_bullish and (volume_spike or price_change > 2.5):
            score = price_change + (latest['Volume'] / latest['Vol_MA5'])
            if is_trust_buying: score += 5
            if is_foreign_buying: score += 3
            
            return {
                "代號": symbol,
                "現價": round(latest['Close'], 2),
                "漲幅%": round(price_change, 2),
                "量能倍率": round(latest['Volume'] / latest['Vol_MA5'], 2),
                "多頭排列": "✅" if is_bullish else "❌",
                "突破意圖": "🔥 高" if is_breakout else "中",
                "投信買超": inst["投信"],
                "外資買超": inst["外資"],
                "法人認養": "🌟" if is_trust_buying and is_foreign_buying else ("🔷" if is_trust_buying else ""),
                "score": score
            }
    except: pass
    return None

def run_full_scan():
    print("🚀 Alice Scanner V3 啟動: 整合『籌碼面』分析系統...")
    inst_map = get_institutional_data()
    all_symbols = get_all_taiwan_symbols()
    results = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scan_logic, s, inst_map): s for s in all_symbols}
        for future in as_completed(futures):
            res = future.result()
            if res: results.append(res)
            
    if results:
        df_final = pd.DataFrame(results)
        top_picks = df_final.sort_values(by="score", ascending=False).head(20)
        top_picks.to_csv("daily_scan_results.csv", index=False)
        print("✅ 全市場籌碼+技術面掃描完成，結果已更新。")
        print(top_picks[["代號", "現價", "漲幅%", "投信買超", "外資買超", "法人認養"]].head(10).to_string(index=False))

if __name__ == "__main__":
    run_full_scan()
