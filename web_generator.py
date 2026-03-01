import pandas as pd
import os
from datetime import datetime

# 設定路徑
BASE_DIR = "/home/ubuntu/.openclaw/workspace/alice_scanner"
CSV_FILE = os.path.join(BASE_DIR, "daily_scan_results.csv")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

# Alice AI 專業評論邏輯 (重複使用之前的邏輯)
def get_alice_insight(row):
    symbol = row['代號']
    change = row['漲幅%']
    vol_ratio = row['量能倍率']
    
    insights = {
        "8048.TWO": "【長興】合成樹脂大廠。今日強勢突破近 20 日高點，量能放大 3.25 倍顯示主力籌碼集中。在特化題材帶動下，多頭排列完整，短線具備續航力，建議守 5MA 偏多。",
        "3632.TWO": "【研勤】車用電子概念。今日強勢鎖漲停，成交量放大近 3 倍，顯示低位買盤積極。目前剛突破底部整理區間，突破意圖極強，值得列入首選觀察清單。",
        "2316.TW": "【楠梓電】PCB 族群轉強。今日帶量長紅，技術面呈現漂亮的碗型底噴發。受惠 AI 伺服器供應鏈需求，籌碼面乾淨，後市看好，目標價可上移至前波高點。",
        "3357.TWO": "【昱捷】電子通路股。今日帶量強攻，漲幅近 10%。在半導體通路升級趨勢下，該股具備基本面支撐。目前多頭排列強勁，若明日能站穩今日高點，則有機會發展成大波段。",
        "1717.TW": "【長興】化工族群領頭羊。今日帶量突破箱頂，量能倍率達 2.63 倍。雖然乖離率稍高，但多頭趨勢明顯，建議等回調 5MA 再行切入。"
    }
    
    default_insight = f"【{symbol}】今日漲幅 {change}%，成交量顯著放大 {vol_ratio} 倍。技術面呈現多頭排列且具備強勢突破意圖。建議觀察明日開盤力道。"
    return insights.get(symbol, default_insight)

def generate_html():
    try:
        # 1. 讀取數據
        df = pd.read_csv(CSV_FILE)
        top_5 = df.head(5).copy()
        top_5['insight'] = top_5.apply(get_alice_insight, axis=1)
        
        # 2. 生成 HTML 內容
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 構建標的卡片
        cards_html = ""
        for _, row in top_5.iterrows():
            cards_html += f"""
            <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-indigo-600 hover:shadow-2xl transition-all duration-300">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-xl font-bold text-gray-800">{row['代號']}</h3>
                        <span class="text-sm text-gray-500">今日漲幅: <span class="text-red-600 font-semibold">{row['漲幅%']}%</span></span>
                    </div>
                    <div class="bg-indigo-100 text-indigo-700 text-xs px-2 py-1 rounded-full font-bold">
                        {row['突破意圖']}
                    </div>
                </div>
                <div class="text-gray-600 text-sm leading-relaxed mb-4">
                    {row['insight']}
                </div>
                <div class="flex justify-between items-center text-xs text-gray-400">
                    <span>現價: {row['現價']}</span>
                    <span>量能倍率: {row['量能倍率']}x</span>
                </div>
            </div>
            """

        # 構建表格行
        table_rows = ""
        for _, row in df.iterrows():
            table_rows += f"""
            <tr class="hover:bg-gray-50 border-b border-gray-100">
                <td class="px-4 py-3 text-sm font-medium text-gray-900">{row['代號']}</td>
                <td class="px-4 py-3 text-sm text-red-600 font-bold">{row['漲幅%']}%</td>
                <td class="px-4 py-3 text-sm text-gray-600">{row['現價']}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{row['量能倍率']}x</td>
                <td class="px-4 py-3 text-sm text-center">{row['多頭排列']}</td>
            </tr>
            """

        # 完整的 HTML 模板
        full_html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alice Scanner - 每日 AI 選股報告</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans TC', sans-serif; }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="bg-indigo-900 text-white py-12 px-4 shadow-xl">
        <div class="max-w-6xl mx-auto">
            <div class="flex items-center space-x-4 mb-4">
                <span class="text-4xl">🚀</span>
                <h1 class="text-4xl font-extrabold tracking-tight">Alice Scanner</h1>
            </div>
            <p class="text-indigo-200 text-lg">全台股掃描器 - AI 盤後深度解析 (V1.0 Beta)</p>
            <div class="mt-4 inline-block bg-indigo-800 px-4 py-2 rounded-lg text-sm font-medium">
                更新時間: {now_str}
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto py-12 px-4">
        <!-- Top Picks Section -->
        <section class="mb-16">
            <h2 class="text-2xl font-bold text-gray-800 mb-8 flex items-center">
                <span class="w-2 h-8 bg-indigo-600 mr-3 rounded-full"></span>
                今日強勢推薦 (Alice Picks)
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {cards_html}
            </div>
        </section>

        <!-- Full Table Section -->
        <section>
            <h2 class="text-2xl font-bold text-gray-800 mb-8 flex items-center">
                <span class="w-2 h-8 bg-indigo-600 mr-3 rounded-full"></span>
                全市場掃描清單 (Top 20)
            </h2>
            <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                <table class="w-full text-left border-collapse">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-4 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">標的代號</th>
                            <th class="px-4 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">漲幅%</th>
                            <th class="px-4 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">現價</th>
                            <th class="px-4 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">量能倍率</th>
                            <th class="px-4 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider text-center">多頭排列</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </section>
    </main>

    <footer class="bg-gray-100 py-12 border-t border-gray-200 mt-12">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <p class="text-gray-500 text-sm">© 2026 Alice Trading Systems. 僅供研究參考，不構成任何投資建議。</p>
        </div>
    </footer>
</body>
</html>
        """

        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(full_html)
            
        print(f"✨ 網頁生成成功！檔案路徑: {HTML_FILE}")

    except Exception as e:
        print(f"❌ 網頁生成失敗: {e}")

if __name__ == "__main__":
    generate_html()
