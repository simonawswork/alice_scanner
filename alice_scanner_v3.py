import yfinance as yf
import pandas as pd
import twstock
import requests
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. 抓取法人數據 (整合上市 TWSE + 上櫃 TPEx)
def get_institutional_data():
    """
    抓取今日 (或最近交易日) 的法人買賣超 (上市 + 上櫃)
    """
    today = datetime.now()
    # 如果是週末，先找週五
    if today.weekday() >= 5:
        offset = today.weekday() - 4
        today = today - timedelta(days=offset)
    
    inst_map = {}
    
    # 嘗試找最近 5 天內有數據的交易日
    for i in range(5):
        target_date = today - timedelta(days=i)
        date_twse = target_date.strftime("%Y%m%d") # 20260301
        date_tpex = f"{target_date.year - 1911}/{target_date.strftime('%m/%d')}" # 115/03/01
        
        # --- A. 抓取上市 (TWSE) ---
        url_twse = f"https://www.twse.com.tw/rwd/zh/fund/T86FU1?date={date_twse}&selectType=ALLBUT0999&response=json"
        # --- B. 抓取上櫃 (TPEx) ---
        url_tpex = f"https://www.tpex.org.tw/web/stock/aftertrading/fund/t86/t86_result.php?l=zh-tw&d={date_tpex}&stk_typ=EW&_={int(time.time()*1000)}"
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            # 處理上市
            res_twse = requests.get(url_twse, headers=headers, timeout=10).json()
            if res_twse.get('stat') == 'OK':
                for row in res_twse.get('data', []):
                    symbol = row[0].strip()
                    foreign = int(row[4].replace(',', ''))
                    trust = int(row[10].replace(',', ''))
                    inst_map[f"{symbol}.TW"] = {"外資": foreign, "投信": trust}
                
                # 處理上櫃 (只有在上市有數據時才抓上櫃，確保日期同步)
                res_tpex = requests.get(url_tpex, headers=headers, timeout=10).json()
                if res_tpex.get('iTotalRecords', 0) > 0:
                    for row in res_tpex.get('aaData', []):
                        symbol = row[0].strip()
                        # 上櫃格式: 0:代號, 1:名稱, 5:外資買賣超, 11:投信買賣超 (依官網 JSON 結構)
                        foreign = int(row[5].replace(',', ''))
                        trust = int(row[11].replace(',', ''))
                        inst_map[f"{symbol}.TWO"] = {"外資": foreign, "投信": trust}
                
                print(f"✅ 成功取得 {date_twse} 法人數據 (上市+上櫃)，共 {len(inst_map)} 筆。")
                break # 找到數據就跳出迴圈
        except Exception as e:
            print(f"⚠️ 嘗試 {date_twse} 失敗: {e}")
            continue
            
    return inst_map

# 2. 取得全市場清單
def get_all_taiwan_symbols():
    codes = []
    for code, item in twstock.codes.items():
        if item.type == '股票' and (item.market == '上市' or item.market == '上櫃'):
            suffix = ".TW" if item.market == '上市' else ".TWO"
            codes.append(f"{code}{suffix}")
    return codes

# 3. 掃描邏輯 (V3.2: 整合上市櫃法人)
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
        volume_spike = latest['Volume'] > latest['Vol_MA5'] * 1.3 # 稍微放寬量能門檻
        price_change = (latest['Close'] - prev['Close']) / prev['Close'] * 100
        recent_high = df['Close'].iloc[-20:].max()
        is_breakout = latest['Close'] >= recent_high * 0.98
        
        inst = inst_map.get(symbol, {"外資": 0, "投信": 0})
        is_trust_buying = inst["投信"] > 100  # 調整門檻：投信買超 100 張即標註
        is_foreign_buying = inst["外資"] > 500 # 調整門檻：外資買超 500 張即標註
        
        if is_bullish and (volume_spike or price_change > 2.0):
            score = price_change + (latest['Volume'] / latest['Vol_MA5'])
            if inst["投信"] > 0: score += 5 # 只要法人有買就加分
            if inst["外資"] > 0: score += 2
            
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
    print("🚀 Alice Scanner V3.2: 啟動『全市場上市櫃籌碼整合』系統...")
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
        print(f"✅ 掃描完成。Top 10 預覽:")
        print(top_picks[["代號", "現價", "漲幅%", "投信買超", "外資買超", "法人認養"]].head(10).to_string(index=False))

if __name__ == "__main__":
    run_full_scan()
