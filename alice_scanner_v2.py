import yfinance as yf
import pandas as pd
import twstock
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. 取得全市場股票清單 (上市 + 上櫃)
def get_all_taiwan_symbols():
    print("🔍 正在取得全市場股票清單...")
    codes = []
    # 上市股票
    for code, item in twstock.codes.items():
        if item.type == '股票' and (item.market == '上市' or item.market == '上櫃'):
            # 轉換為 yfinance 格式: 2330.TW (上市) 或 8069.TWO (上櫃)
            suffix = ".TW" if item.market == '上市' else ".TWO"
            codes.append(f"{code}{suffix}")
    print(f"✅ 取得完成，共 {len(codes)} 檔標的。")
    return codes

# 2. 單一股票掃描邏輯 (強勢股模型)
def scan_logic(symbol):
    try:
        # 抓取最近 40 天數據 (足夠計算 20MA 與 ATR)
        stock = yf.Ticker(symbol)
        df = stock.history(period="40d")
        
        if df.empty or len(df) < 20:
            return None

        # 計算基礎指標
        df['5MA'] = df['Close'].rolling(window=5).mean()
        df['20MA'] = df['Close'].rolling(window=20).mean()
        df['Vol_MA5'] = df['Volume'].rolling(window=5).mean()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # --- 飆股篩選核心條件 (Rocket Screener V2) ---
        # 1. 多頭排列: 價格 > 5MA > 20MA
        is_bullish = latest['Close'] > latest['5MA'] > latest['20MA']
        
        # 2. 帶量突破: 今日成交量 > 5日均量 1.5 倍
        volume_spike = latest['Volume'] > latest['Vol_MA5'] * 1.5
        
        # 3. 價格動能: 今日漲幅 > 2% 且 股價站在近 20 日高點附近 (突破意圖)
        price_change = (latest['Close'] - prev['Close']) / prev['Close'] * 100
        recent_high = df['Close'].iloc[-20:].max()
        is_breakout = latest['Close'] >= recent_high * 0.98  # 距離 20 日高點 2% 以內
        
        # 只保留符合「強勢」或「突破」的標的
        if is_bullish and (volume_spike or price_change > 3.0):
            return {
                "代號": symbol,
                "現價": round(latest['Close'], 2),
                "漲幅%": round(price_change, 2),
                "量能倍率": round(latest['Volume'] / latest['Vol_MA5'], 2),
                "多頭排列": "✅" if is_bullish else "❌",
                "突破意圖": "🔥 高" if is_breakout else "中",
                "score": price_change + (latest['Volume'] / latest['Vol_MA5']) # 簡易評分排序
            }
    except:
        pass
    return None

# 3. 多執行緒平行掃描 (加速全市場處理)
def run_full_scan():
    all_symbols = get_all_taiwan_symbols()
    results = []
    
    print(f"🚀 開始全市場掃描 (使用 10 執行緒加速)...")
    start_time = time.time()
    
    # 限制掃描數量測試 (如需全掃描請移除 [:100])
    # all_symbols = all_symbols[:100] 
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_symbol = {executor.submit(scan_logic, s): s for s in all_symbols}
        
        count = 0
        for future in as_completed(future_to_symbol):
            res = future.result()
            if res:
                results.append(res)
            count += 1
            if count % 100 == 0:
                print(f"已掃描 {count}/{len(all_symbols)} 檔...")

    end_time = time.time()
    print(f"✨ 掃描完成！耗時: {round(end_time - start_time, 2)} 秒")
    
    if results:
        df_final = pd.DataFrame(results)
        # 根據評分排序，取出前 20 檔最強勢的
        top_picks = df_final.sort_values(by="score", ascending=False).head(20)
        
        print("\n🏆 【Alice Rocket Picks - 今日強勢標的名單】")
        print("=" * 60)
        print(top_picks[["代號", "現價", "漲幅%", "量能倍率", "多頭排列", "突破意圖"]].to_string(index=False))
        print("=" * 60)
        
        # 儲存結果供後續 AI 評論使用
        top_picks.to_csv("daily_scan_results.csv", index=False)
        print(f"✅ 結果已儲存至 daily_scan_results.csv，準備進入 AI 評論階段。")
    else:
        print("今日市場似乎較為冷清，未發現符合條件的飆股。")

if __name__ == "__main__":
    run_full_scan()
