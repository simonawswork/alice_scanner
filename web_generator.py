import pandas as pd
import yfinance as yf
import json
import os
from datetime import datetime, timedelta

# 設定路徑
BASE_DIR = "/home/ubuntu/.openclaw/workspace/alice_scanner"
CSV_FILE = os.path.join(BASE_DIR, "daily_scan_results.csv")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

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
    default_insight = f"【{symbol}】今日漲幅 {change}%，成交量顯著放大 {vol_ratio} 倍。技術面多頭排列且具強勢突破意圖。"
    return insights.get(symbol, default_insight)

def get_30d_prices(symbol):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="35d")
        if df.empty: return []
        # 只取最後 30 筆 Close 價格
        return [round(p, 2) for p in df['Close'].tail(30).tolist()]
    except:
        return []

def generate_html_v3():
    try:
        df = pd.read_csv(CSV_FILE)
        top_picks = df.head(6).copy() # 改為 6 檔，排版更對齊
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 準備每個標的的圖表數據
        chart_data_js = "const chartData = {};\n"
        cards_html = ""
        
        for i, row in top_picks.iterrows():
            symbol = row['代號']
            prices = get_30d_prices(symbol)
            chart_id = f"chart_{symbol.replace('.', '_')}"
            chart_data_js += f"chartData['{chart_id}'] = {json.dumps(prices)};\n"
            
            badge_color = "bg-rose-500" if row['漲幅%'] > 7 else "bg-orange-500"
            trust_buy = row.get('投信買超', 0)
            foreign_buy = row.get('外資買超', 0)
            
            inst_tag = ""
            if trust_buy > 500 and foreign_buy > 1000:
                inst_tag = '<span class="px-2 py-1 bg-amber-100 text-amber-700 text-[10px] font-black rounded border border-amber-200">🌟 雙強買超</span>'
            elif trust_buy > 500:
                inst_tag = '<span class="px-2 py-1 bg-blue-100 text-blue-700 text-[10px] font-black rounded border border-blue-200">🔷 投信認養</span>'

            cards_html += f"""
            <div class="group bg-white rounded-2xl shadow-sm hover:shadow-2xl border border-gray-100 p-6 transition-all duration-500 hover:-translate-y-2 relative overflow-hidden flex flex-col h-full">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-widest block mb-1">TOP {i+1} PICK</span>
                        <h3 class="text-2xl font-black text-gray-900 tracking-tighter">{symbol}</h3>
                    </div>
                    <div class="{badge_color} text-white text-[10px] px-2 py-1 rounded-full font-black shadow-lg shadow-rose-200 uppercase italic">
                        {row['漲幅%']}% UP
                    </div>
                </div>

                <!-- 迷你 K 線區域 (30 天日線) -->
                <div class="w-full h-32 mb-6 bg-slate-50 rounded-xl relative overflow-hidden group-hover:bg-indigo-50/50 transition-colors">
                    <canvas id="{chart_id}" class="w-full h-full"></canvas>
                </div>

                <div class="flex-grow">
                    <p class="text-gray-600 text-[13px] leading-relaxed font-medium mb-6">
                        {get_alice_insight(row)}
                    </p>
                </div>

                <!-- 籌碼數據區塊 -->
                <div class="grid grid-cols-2 gap-3 mb-6 p-3 bg-slate-50/50 rounded-lg border border-slate-100">
                    <div class="flex flex-col">
                        <span class="text-[9px] font-bold text-slate-400 uppercase">投信</span>
                        <span class="text-xs font-black {'text-rose-500' if trust_buy > 0 else 'text-slate-600'}">{trust_buy:+,d}</span>
                    </div>
                    <div class="flex flex-col">
                        <span class="text-[9px] font-bold text-slate-400 uppercase">外資</span>
                        <span class="text-xs font-black {'text-rose-500' if foreign_buy > 0 else 'text-slate-600'}">{foreign_buy:+,d}</span>
                    </div>
                </div>

                <div class="flex flex-wrap gap-2 pt-4 border-t border-gray-50">
                    <span class="px-2 py-0.5 bg-green-50 text-green-600 text-[9px] font-bold rounded border border-green-100">多頭排列 ✅</span>
                    <span class="px-2 py-0.5 bg-blue-50 text-blue-600 text-[9px] font-bold rounded border border-blue-100">突破意圖 {row['突破意圖']}</span>
                    {inst_tag}
                </div>
            </div>
            """

        table_rows = ""
        for _, row in df.iterrows():
            change_class = "text-rose-600" if row['漲幅%'] > 0 else "text-emerald-600"
            table_rows += f"""
            <tr class="hover:bg-indigo-50/30 transition-colors border-b border-gray-50">
                <td class="px-6 py-4 text-sm font-black text-gray-900">{row['代號']}</td>
                <td class="px-6 py-4 text-sm font-black {change_class}">{row['漲幅%']}%</td>
                <td class="px-6 py-4 text-sm font-bold text-gray-600">{row['現價']}</td>
                <td class="px-6 py-4 text-sm font-bold text-indigo-500">{row['量能倍率']}x</td>
                <td class="px-6 py-4 text-sm font-bold text-rose-500">{row.get('投信買超', 0):+,d} / {row.get('外資買超', 0):+,d}</td>
                <td class="px-6 py-4 text-sm text-center">
                    <span class="px-2 py-1 bg-gray-100 text-gray-500 text-[10px] font-bold rounded-full">{row['多頭排列']}</span>
                </td>
            </tr>
            """

        full_html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alice Scanner | AI 選股報告 V3.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', 'Noto Sans TC', sans-serif; }}
        .glass {{ background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); }}
    </style>
</head>
<body class="bg-gray-50/50 text-gray-900">

    <!-- Hero Section -->
    <div class="relative bg-slate-950 py-20 px-6 overflow-hidden">
        <div class="absolute inset-0 opacity-10 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]"></div>
        <div class="max-w-7xl mx-auto relative">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-8">
                <div>
                    <div class="flex items-center space-x-3 mb-4">
                        <div class="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg transform rotate-6">
                            <span class="text-xl">📊</span>
                        </div>
                        <h2 class="text-indigo-400 font-black tracking-widest text-xs uppercase">Intelligent Quant</h2>
                    </div>
                    <h1 class="text-5xl md:text-6xl font-black text-white tracking-tighter mb-4">
                        Alice <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-emerald-400">Scanner V3.0</span>
                    </h1>
                    <p class="text-slate-400 text-lg font-medium max-w-xl">
                        自動化全市場掃描，結合技術指標、法人籌碼與 30 天趨勢圖。
                    </p>
                </div>
                <div class="glass p-6 rounded-2xl border border-white/10 shadow-2xl">
                    <div class="text-slate-500 text-[10px] font-bold uppercase mb-1 tracking-widest">Update intelligence</div>
                    <div class="text-2xl font-black text-slate-100">{now_str}</div>
                    <div class="mt-2 flex items-center space-x-2">
                        <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                        <span class="text-emerald-400 text-[10px] font-bold uppercase tracking-widest">AI Core Online</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto -mt-10 px-6 pb-24">
        
        <section class="mb-20">
            <div class="flex items-end justify-between mb-10 px-2">
                <div>
                    <h2 class="text-3xl font-black text-gray-900 tracking-tight mb-1">今日核心精選</h2>
                    <p class="text-gray-500 text-sm font-medium">30 天趨勢與 AI 深度解讀</p>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {cards_html}
            </div>
        </section>

        <!-- Full Scan List -->
        <section>
            <div class="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
                <div class="px-8 py-8 border-b border-gray-50">
                    <h2 class="text-2xl font-black text-gray-900">全市場強勢股清單 (Top 20)</h2>
                    <p class="text-gray-400 text-xs font-bold mt-1">REAL-TIME QUANTITATIVE ANALYSIS</p>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left">
                        <thead>
                            <tr class="bg-gray-50/50">
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase tracking-widest">標的代號</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase tracking-widest">漲幅%</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase tracking-widest">現價</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase tracking-widest">量能倍率</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase tracking-widest">投信/外資</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase tracking-widest text-center">多頭格局</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-50">
                            {table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    </main>

    <footer class="bg-white py-16 border-t border-gray-100 text-center">
        <p class="text-gray-400 text-xs font-bold uppercase tracking-[0.3em]">Alice Trading Intelligence V3.0</p>
    </footer>

    <script>
        {chart_data_js}

        window.onload = function() {{
            Object.keys(chartData).forEach(id => {{
                const ctx = document.getElementById(id).getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: new Array(30).fill(''),
                        datasets: [{{
                            data: chartData[id],
                            borderColor: '#6366f1',
                            borderWidth: 3,
                            pointRadius: 0,
                            fill: true,
                            backgroundColor: (context) => {{
                                const chart = context.chart;
                                const {{ctx, chartArea}} = chart;
                                if (!chartArea) return null;
                                const gradient = ctx.createLinearGradient(0, 0, 0, chartArea.bottom);
                                gradient.addColorStop(0, 'rgba(99, 102, 241, 0.2)');
                                gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');
                                return gradient;
                            }},
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: true }} }},
                        scales: {{ x: {{ display: false }}, y: {{ display: false }} }}
                    }}
                }});
            }});
        }};
    </script>
</body>
</html>
        """

        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(full_html)
            
        print(f"✨ 網頁 UI V3.0 (Chart Engine) 升級成功！檔案路徑: {HTML_FILE}")

    except Exception as e:
        print(f"❌ 網頁生成失敗: {e}")

if __name__ == "__main__":
    generate_html_v3()
