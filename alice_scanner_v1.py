import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 初始追蹤清單 (之後可擴展為全市場)
WATCHLIST = [
    "2330.TW", "2317.TW", "2454.TW", "2308.TW", "2382.TW", 
    "3231.TW", "2357.TW", "6669.TW", "2603.TW", "2609.TW"
]

def scan_stock(symbol):
    try:
        # 抓取最近 60 天數據
        stock = yf.Ticker(symbol)
        df = stock.history(period="60d")
        
        if df.empty:
            return None

        # 計算指標
        df['5MA'] = df['Close'].rolling(window=5).mean()
        df['20MA'] = df['Close'].rolling(window=20).mean()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 篩選條件：
        # 1. 價格站在 5MA 與 20MA 之上
        # 2. 5MA 剛穿過 20MA (金叉) 或正在擴張
        # 3. 成交量放大
        
        is_bullish = latest['Close'] > latest['5MA'] > latest['20MA']
        volume_spike = latest['Volume'] > df['Volume'].mean() * 1.5
        
        status = {
            "symbol": symbol,
            "name": stock.info.get('shortName', symbol),
            "price": round(latest['Close'], 2),
            "change": round((latest['Close'] - prev['Close']) / prev['Close'] * 100, 2),
            "bullish": is_bullish,
            "volume_spike": volume_spike,
            "action": "⭐ 推薦關注" if is_bullish and volume_spike else "觀察"
        }
        return status
    except Exception as e:
        print(f"Error scanning {symbol}: {e}")
        return None

def main():
    print(f"🚀 Alice Scanner V1 啟動 - 掃描時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    results = []
    for symbol in WATCHLIST:
        res = scan_stock(symbol)
        if res:
            results.append(res)
    
    # 轉換成 DataFrame 顯示
    report_df = pd.DataFrame(results)
    print(report_df.sort_values(by="change", ascending=False).to_string(index=False))
    
    print("-" * 50)
    bulls = report_df[report_df['action'] == "⭐ 推薦關注"]
    if not bulls.empty:
        print(f"🔥 今日強勢推薦: {', '.join(bulls['name'].tolist())}")
    else:
        print("今日暫無符合強勢突破條件的標的。")

if __name__ == "__main__":
    main()
