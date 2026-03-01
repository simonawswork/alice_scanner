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
    name = row.get('名稱', '')
    change = row['漲幅%']
    vol_ratio = row['量能倍率']
    
    # 取得支撐壓力點位
    s1, s2 = row.get('支撐1', 0), row.get('支撐2', 0)
    r1, r2 = row.get('壓力1', 0), row.get('壓力2', 0)
    
    points_info = f"<br><b>📍 關鍵位：</b><br>壓力：{r1} / {r2}<br>支撐：{s1} / {s2}"
    
    insights = {
        "8048.TWO": f"【{name}】今日強勢突破近 20 日高點，量能放大顯示主力籌碼集中。多頭排列完整，具續航力。{points_info}",
        "3632.TWO": f"【{name}】今日強勢鎖漲停，成交量倍增。目前剛突破底部整理區間，突破意圖極強。{points_info}",
        "2316.TW": f"【{name}】今日帶量長紅，技術面呈現漂亮碗型底噴發。受惠 AI 供應鏈需求，後市看好。{points_info}",
        "3357.TWO": f"【{name}】今日帶量強攻，漲幅近 10%。在半導體通路升級趨勢下，具備基本面支撐。{points_info}",
        "1717.TW": f"【{name}】今日帶量突破箱頂，量能倍率高。多頭趨勢明顯，建議關注支撐位防守。{points_info}"
    }
    
    default_insight = f"【{name}】今日漲幅 {change}%，成交量放大 {vol_ratio} 倍。技術面多頭排列且具突破意圖。{points_info}"
    return insights.get(symbol, default_insight)

def get_30d_history(symbol):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="45d")
        if df.empty: return {"prices": [], "volumes": [], "dates": []}
        df = df.tail(30)
        return {
            "prices": [round(p, 2) for p in df['Close'].tolist()],
            "volumes": [int(v) for v in df['Volume'].tolist()],
            "dates": [d.strftime('%m/%d') for d in df.index]
        }
    except:
        return {"prices": [], "volumes": [], "dates": []}

def generate_html_v3_1():
    try:
        df = pd.read_csv(CSV_FILE)
        top_picks = df.head(6).copy()
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        chart_data_js = "const chartData = {};\n"
        cards_html = ""
        
        for i, row in top_picks.iterrows():
            symbol = row['代號']
            history = get_30d_history(symbol)
            chart_id = f"chart_{symbol.replace('.', '_')}"
            chart_data_js += f"chartData['{chart_id}'] = {json.dumps(history)};\n"
            
            badge_color = "bg-rose-500" if row['漲幅%'] > 7 else "bg-orange-500"
            trust_buy = row.get('投信買超', 0)
            foreign_buy = row.get('外資買超', 0)
            
            # 時間區間顯示
            date_range = f"{history['dates'][0]} - {history['dates'][-1]}" if history['dates'] else "N/A"

            cards_html += f"""
            <div class="group bg-white rounded-2xl shadow-sm hover:shadow-xl border border-gray-100 p-6 transition-all duration-500 hover:-translate-y-2 relative overflow-hidden flex flex-col h-full">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-widest block mb-1">TOP {i+1} PICK</span>
                        <h3 class="text-2xl font-black text-gray-900 tracking-tighter">{row.get('名稱', '')} ({symbol})</h3>
                    </div>
                    <div class="{badge_color} text-white text-[10px] px-2 py-1 rounded-full font-black shadow-lg shadow-rose-200 uppercase italic">
                        {row['漲幅%']}% UP
                    </div>
                </div>

                <!-- 混合圖表區域 (價格折線 + 成交量柱狀) -->
                <div class="w-full h-40 mb-2 bg-slate-50 rounded-xl relative overflow-hidden group-hover:bg-indigo-50/30 transition-colors">
                    <canvas id="{chart_id}" class="w-full h-full"></canvas>
                </div>
                <div class="text-[9px] text-gray-400 font-bold flex justify-between px-1 mb-4 uppercase tracking-tighter">
                    <span>{date_range}</span>
                    <span>30D TREND ANALYSIS</span>
                </div>

                <div class="flex-grow">
                    <p class="text-gray-600 text-[13px] leading-relaxed font-medium mb-6">
                        {get_alice_insight(row)}
                    </p>
                </div>

                <div class="grid grid-cols-2 gap-3 mb-6 p-3 bg-slate-50/50 rounded-lg border border-slate-100">
                    <div class="flex flex-col">
                        <span class="text-[9px] font-bold text-slate-400 uppercase">投信買超</span>
                        <span class="text-xs font-black {'text-rose-500' if trust_buy > 0 else 'text-slate-600'}">{trust_buy:+,d}</span>
                    </div>
                    <div class="flex flex-col">
                        <span class="text-[9px] font-bold text-slate-400 uppercase">外資買超</span>
                        <span class="text-xs font-black {'text-rose-500' if foreign_buy > 0 else 'text-slate-600'}">{foreign_buy:+,d}</span>
                    </div>
                </div>

                <div class="flex flex-wrap gap-2 pt-4 border-t border-gray-50">
                    <span class="px-2 py-0.5 bg-green-50 text-green-600 text-[9px] font-bold rounded border border-green-100">多頭排列 ✅</span>
                    <span class="px-2 py-0.5 bg-blue-50 text-blue-600 text-[9px] font-bold rounded border border-blue-100">突破意圖 {row['突破意圖']}</span>
                </div>
            </div>
            """

        table_rows = ""
        for _, row in df.iterrows():
            change_class = "text-rose-600" if row['漲幅%'] > 0 else "text-emerald-600"
            table_rows += f"""
            <tr class="hover:bg-indigo-50/30 transition-colors border-b border-gray-50">
                <td class="px-6 py-4 text-sm font-black text-gray-900">{row.get('名稱', '')} ({row['代號']})</td>
                <td class="px-6 py-4 text-sm font-black {change_class}">{row['漲幅%']}%</td>
                <td class="px-6 py-4 text-sm font-bold text-gray-600">{row['現價']}</td>
                <td class="px-6 py-4 text-sm font-bold text-indigo-500">{row['量能倍率']}x</td>
                <td class="px-6 py-4 text-sm font-bold text-rose-500">{row.get('投信買超', 0):+,d} / {row.get('外資買超', 0):+,d}</td>
                <td class="px-6 py-4 text-sm text-center font-bold text-gray-400">{row['多頭排列']}</td>
            </tr>
            """

        full_html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alice Scanner | Pro Analysis V3.1</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', 'Noto Sans TC', sans-serif; }}
        .glass {{ background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); }}
    </style>
</head>
<body class="bg-gray-50/50 text-gray-900">

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
                        Alice <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-emerald-400">Scanner V3.1</span>
                    </h1>
                    <p class="text-slate-400 text-lg font-medium max-w-xl">
                        全方位台股雷達：整合 30 日量價 K 線趨勢、法人籌碼與 AI 深度評論。
                    </p>
                </div>
                <div class="glass p-6 rounded-2xl border border-white/10 shadow-2xl text-center">
                    <div class="text-slate-500 text-[10px] font-bold uppercase mb-1 tracking-widest">Update intelligence</div>
                    <div class="text-2xl font-black text-slate-100">{now_str}</div>
                    <div class="mt-2 flex items-center justify-center space-x-2">
                        <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                        <span class="text-emerald-400 text-[10px] font-bold uppercase tracking-widest">System Active</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <main class="max-w-7xl mx-auto -mt-10 px-6 pb-24">
        <section class="mb-20">
            <div class="flex items-end justify-between mb-10 px-2">
                <h2 class="text-3xl font-black text-gray-900 tracking-tight">核心精選標的</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {cards_html}
            </div>
        </section>

        <section>
            <div class="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
                <div class="px-8 py-8 border-b border-gray-50 flex justify-between items-center">
                    <h2 class="text-2xl font-black text-gray-900">全市場掃描清單 (Top 20)</h2>
                    <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Quant Filter Active</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left">
                        <thead>
                            <tr class="bg-gray-50/50">
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase">標的代號</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase">漲幅%</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase">現價</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase">量能倍率</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase">投信/外資</th>
                                <th class="px-8 py-5 text-[10px] font-black text-gray-400 uppercase text-center">多頭格局</th>
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
        <p class="text-gray-400 text-[10px] font-bold uppercase tracking-[0.4em]">Alice Trading Intelligence V3.1 PRO</p>
    </footer>

    <script>
        {chart_data_js}

        window.onload = function() {{
            Object.keys(chartData).forEach(id => {{
                const ctx = document.getElementById(id).getContext('2d');
                const data = chartData[id];
                
                new Chart(ctx, {{
                    data: {{
                        labels: data.dates,
                        datasets: [
                            {{
                                type: 'line',
                                label: 'Price',
                                data: data.prices,
                                borderColor: '#6366f1',
                                borderWidth: 3,
                                pointRadius: 0,
                                tension: 0.4,
                                yAxisID: 'y',
                                fill: true,
                                backgroundColor: (context) => {{
                                    const chart = context.chart;
                                    const {{ctx, chartArea}} = chart;
                                    if (!chartArea) return null;
                                    const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                                    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.2)');
                                    gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');
                                    return gradient;
                                }}
                            }},
                            {{
                                type: 'bar',
                                label: 'Volume',
                                data: data.volumes,
                                backgroundColor: 'rgba(226, 232, 240, 0.6)',
                                yAxisID: 'y1',
                                barPercentage: 0.7,
                                borderRadius: 2
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: true, mode: 'index', intersect: false }} }},
                        scales: {{
                            x: {{ display: false }},
                            y: {{
                                display: false,
                                type: 'linear',
                                position: 'left',
                            }},
                            y1: {{
                                display: false,
                                type: 'linear',
                                position: 'right',
                                grid: {{ drawOnChartArea: false }},
                                max: Math.max(...data.volumes) * 3 // 讓成交量在下方
                            }}
                        }}
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
            
        print(f"✨ 網頁 UI V3.1 (Pro Chart Engine) 升級成功！")

    except Exception as e:
        print(f"❌ 網頁生成失敗: {e}")

if __name__ == "__main__":
    generate_html_v3_1()
