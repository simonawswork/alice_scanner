import pandas as pd
import json
import os
from datetime import datetime

# 設定路徑
BASE_DIR = "/home/ubuntu/.openclaw/workspace/alice_scanner"
CSV_FILE = os.path.join(BASE_DIR, "daily_scan_results.csv")
SECRETS_FILE = os.path.join(BASE_DIR, "secrets.json")

def send_telegram_notification():
    try:
        # 1. 讀取 Secrets
        with open(SECRETS_FILE, "r") as f:
            secrets = json.load(f)
        target = secrets["telegram"]["target"]

        # 2. 讀取前 5 檔標的
        df = pd.read_csv(CSV_FILE).head(5)
        
        # 3. 構建訊息
        date_str = datetime.now().strftime("%Y-%m-%d")
        msg = f"🚀 【Alice Scanner - 每日強勢股雷達】\n"
        msg += f"📅 日期：{date_str}\n"
        msg += f"━━━━━━━━━━━━━━━\n\n"
        
        for i, row in df.iterrows():
            trust = row.get('投信買超', 0)
            foreign = row.get('外資買超', 0)
            inst_tag = "🌟" if trust > 500 and foreign > 1000 else ("🔷" if trust > 500 else "")
            
            msg += f"{i+1}. {row['代號']} | 漲幅: {row['漲幅%']}% {inst_tag}\n"
            msg += f"   💰 現價: {row['現價']} | 量能: {row['量能倍率']}x\n"
            msg += f"   📊 法人: 投信{trust:+,d} / 外資{foreign:+,d}\n\n"
        
        msg += f"━━━━━━━━━━━━━━━\n"
        msg += f"🔗 完整 AI 深度評論請見網站：\n"
        msg += f"https://simonawswork.github.io/alice_scanner/\n"
        
        # 4. 透過 openclaw 指令發送 (安全且方便)
        safe_msg = msg.replace("'", "")
        os.system(f"/usr/bin/openclaw message send --target \"{target}\" --message \"{safe_msg}\" > /dev/null 2>&1")
        
        print(f"✅ Telegram 今日選股推播成功發送至 {target}！")

    except Exception as e:
        print(f"❌ Telegram 推播失敗: {e}")

if __name__ == "__main__":
    send_telegram_notification()
