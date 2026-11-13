# sesi6/latihan_plotly.py — Latihan mandiri Sesi 6 no. 1–4, ditampilkan di aplikasi Dash
#   1. Bar horizontal churn rate per payment_method, urut tertinggi, + garis rata-rata (add_vline)
#   2. Bubble chart: scatter dengan size="support_calls"
#   3. Sunburst region → segmen → kontrak (jumlah pelanggan) + cara membacanya
#   4. Gauge go.Indicator(mode="gauge+number") churn rate keseluruhan
# Jalankan: python sesi6/latihan_plotly.py  lalu buka http://127.0.0.1:8052
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc

ROOT = Path(__file__).resolve().parents[1]
STATUS = {"Bertahan": "#2a78d6", "Churn": "#eb6834"}
KATEGORI = ["#2a78d6", "#1baf7a", "#eda100", "#4a3aa7", "#e87ba4"]
KONTRAK = ["Bulanan", "Tahunan", "Dua Tahun"]

df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])
df["status"] = df["churn"].map({0: "Bertahan", 1: "Churn"})
df["tagihan_ribu"] = df["monthly_charges"] / 1000
rata2 = df.churn.mean() * 100

# ---------- Latihan 1: bar horizontal per payment_method ----------
pay = (df.groupby("payment_method", as_index=False)["churn"].mean()
         .assign(churn_pct=lambda d: d["churn"] * 100)
         .sort_values("churn_pct"))            # urut naik → batang tertinggi tampil paling atas
fig_pay = px.bar(pay, x="churn_pct", y="payment_method", orientation="h",
                 text=pay["churn_pct"].map("{:.1f}%".format),
                 color_discrete_sequence=["#eb6834"],
                 labels={"churn_pct": "Churn rate (%)", "payment_method": "Metode pembayaran"},
                 title="Transfer Bank memiliki churn rate tertinggi di antara metode pembayaran")
fig_pay.update_traces(textposition="outside",
                      hovertemplate="%{y}<br>Churn rate: %{x:.1f}%<extra></extra>")
fig_pay.add_vline(x=rata2, line_dash="dot", line_color="#52514e",
                  annotation_text=f"rata-rata nasional {rata2:.1f}%",
                  annotation_position="top")
fig_pay.update_xaxes(range=[0, 48])

# ---------- Latihan 2: bubble chart ----------
fig_bubble = px.scatter(df, x="tenure_months", y="tagihan_ribu", color="status",
                        size="support_calls", size_max=18, opacity=0.5,
                        color_discrete_map=STATUS, hover_name="customer_id",
                        hover_data={"contract_type": True, "support_calls": True,
                                    "tagihan_ribu": ":.0f"},
                        labels={"tenure_months": "Tenure (bulan)", "tagihan_ribu": "Tagihan (ribu Rp)",
                                "support_calls": "Panggilan ke CS", "status": "Status",
                                "contract_type": "Kontrak"},
                        title="Bubble: ukuran lingkaran = jumlah panggilan ke CS")

# ---------- Latihan 3: sunburst region → segmen → kontrak ----------
cnt = df.groupby(["region", "segment", "contract_type"], as_index=False).agg(
    pelanggan=("customer_id", "count"))
fig_sun = px.sunburst(cnt, path=["region", "segment", "contract_type"], values="pelanggan",
                      color="region", color_discrete_sequence=KATEGORI,
                      title="Jawa menyumbang 42% pelanggan, didominasi segmen Retail")
fig_sun.update_traces(hovertemplate="%{id}<br>Pelanggan: %{value:,}"
                                    "<br>Porsi dari induk: %{percentParent:.1%}<extra></extra>",
                      insidetextorientation="radial")

# ---------- Latihan 4: gauge churn rate keseluruhan ----------
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number", value=rata2,
    number={"suffix": "%", "valueformat": ".1f"},
    title={"text": "Churn rate keseluruhan"},
    gauge={"axis": {"range": [0, 100], "ticksuffix": "%"}, "bar": {"color": "#eb6834"},
           "steps": [{"range": [0, 20], "color": "#e3f4ec"},
                     {"range": [20, 40], "color": "#fdf1d6"},
                     {"range": [40, 100], "color": "#fbe3e3"}]}))

for f in [fig_pay, fig_bubble, fig_sun, fig_gauge]:
    f.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=60, b=20))

# ---------- Aplikasi Dash ----------
GRID = {"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"}
KOTAK = {"background": "#F4F6FA", "borderRadius": "10px", "padding": "12px 16px", "fontSize": "14px"}

app = Dash(__name__, title="Latihan Plotly")
app.layout = html.Div(style={"maxWidth": "1150px", "margin": "auto", "fontFamily": "Arial",
                             "padding": "20px"}, children=[
    html.H1("Latihan Mandiri Sesi 6 — Interactive Visualization with Plotly"),
    html.P("Arahkan kursor untuk detail, drag untuk zoom, double-click untuk reset, "
           "klik legenda untuk menyembunyikan kelompok."),

    html.Div(style=GRID, children=[
        html.Div([html.H3("Latihan 1 — Bar horizontal + garis rata-rata"),
                  dcc.Graph(figure=fig_pay)]),
        html.Div([html.H3("Latihan 4 — Gauge churn rate"),
                  dcc.Graph(figure=fig_gauge)]),
    ]),

    html.H3("Latihan 2 — Bubble chart"),
    dcc.Graph(figure=fig_bubble),

    html.H3("Latihan 3 — Sunburst region → segmen → kontrak"),
    html.Div(style=GRID, children=[
        dcc.Graph(figure=fig_sun, style={"height": "520px"}),
        html.Div(style=KOTAK, children=[
            html.H4("Cara membaca sunburst", style={"marginTop": 0}),
            html.Ol([
                html.Li("Baca dari tengah ke luar: cincin dalam = region, cincin tengah = segmen "
                        "di region itu, cincin luar = jenis kontrak di segmen itu."),
                html.Li("Lebar busur sebanding dengan jumlah pelanggan. Jawa memakai busur terlebar "
                        "(42% pelanggan), diikuti Sumatera (22%)."),
                html.Li("Setiap irisan anak adalah bagian dari induknya. Di Jawa, Retail mengambil "
                        "sekitar 64% pelanggan region itu, UMKM 27%, Korporat 10%."),
                html.Li("Di cincin luar, Bulanan selalu irisan terbesar (±48% di tiap segmen), "
                        "jadi kontrak bulanan — kelompok paling berisiko churn — ada di semua region."),
                html.Li("Klik sebuah region untuk zoom ke dalamnya; klik bagian tengah untuk kembali. "
                        "Hover menampilkan jumlah pelanggan dan porsinya terhadap induk."),
            ]),
        ]),
    ]),
])

if __name__ == "__main__":
    app.run(debug=False, port=8052)   # 8052 agar bisa jalan bersamaan dengan app_dash_plotly.py (8051)
