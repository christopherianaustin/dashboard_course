# sesi5/latihan_dash.py — Latihan mandiri Sesi 5 no. 1–4
# Dasar: app_dash_dasar.py, ditambah:
#   1. KPI card kelima: rata-rata jumlah keluhan
#   2. Grafik kedua (churn rate per region), dua grafik berdampingan dengan CSS grid
#   3. DataTable dengan sorting (sort_action="native") dan paging (page_size=5)
#   4. Gaya dipindah ke sesi5/assets/style.css dan dipakai lewat className
# Jalankan: python sesi5/latihan_dash.py  lalu buka http://127.0.0.1:8051
from pathlib import Path
import pandas as pd
from dash import Dash, html, dcc, dash_table

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])


def ringkasan(kolom):
    r = (df.groupby(kolom)
           .agg(pelanggan=("customer_id", "count"), churn_rate=("churn", "mean"))
           .reset_index())
    r["churn_rate"] = (r["churn_rate"] * 100).round(1)
    return r


ringkas = ringkasan("contract_type")
per_region = ringkasan("region").sort_values("churn_rate", ascending=False)

# Latihan 4: Dash otomatis memuat semua file .css di folder assets/.
# assets_folder ditulis eksplisit agar CSS tetap ditemukan dari folder mana pun aplikasi dijalankan.
app = Dash(__name__, title="Dash Dasar — Latihan",
           assets_folder=str(Path(__file__).resolve().parent / "assets"))


def kartu(judul, nilai):
    return html.Div([html.P(judul, className="kartu-judul"),
                     html.H2(nilai, className="kartu-nilai")], className="kartu")


def grafik_bar(x, y, warna):
    return {
        "data": [{"type": "bar", "x": x, "y": y, "marker": {"color": warna}}],
        "layout": {"yaxis": {"title": "Churn rate (%)"}, "height": 350,
                   "margin": {"l": 60, "r": 20, "t": 20, "b": 60}},
    }


app.layout = html.Div(className="halaman", children=[
    html.H1("Dashboard Churn — Versi Dash"),
    html.P("Latihan Sesi 5: lima KPI card, dua grafik berdampingan, dan tabel yang bisa diurutkan."),

    html.Div(className="baris-kartu", children=[
        kartu("Total pelanggan", f"{len(df):,}"),
        kartu("Churn rate", f"{df.churn.mean():.1%}"),
        kartu("Rata-rata tenure", f"{df.tenure_months.mean():.1f} bln"),
        kartu("Region", df.region.nunique()),
        kartu("Rata-rata keluhan", f"{df.num_complaints.mean():.2f}"),   # Latihan 1
    ]),

    # Latihan 2: dua grafik berdampingan dengan CSS grid
    html.Div(className="grid-2", children=[
        html.Div([html.H3("Churn rate per jenis kontrak"),
                  dcc.Graph(id="grafik-kontrak",
                            figure=grafik_bar(ringkas["contract_type"], ringkas["churn_rate"],
                                              "#C44E52"))]),
        html.Div([html.H3("Churn rate per region"),
                  dcc.Graph(id="grafik-region",
                            figure=grafik_bar(per_region["region"], per_region["churn_rate"],
                                              "#4C72B0"))]),
    ]),

    html.H3("Ringkasan per region"),
    html.P("Klik judul kolom untuk mengurutkan.", className="catatan"),
    # Latihan 3: sorting + paging
    dash_table.DataTable(data=per_region.to_dict("records"),
                         columns=[{"name": c, "id": c} for c in per_region.columns],
                         sort_action="native", page_size=5,
                         style_cell={"padding": "6px", "textAlign": "left"},
                         style_header={"fontWeight": "bold", "background": "#E9EDF5"}),

    html.Hr(),
    html.Small("Sumber: data latihan sintetis customer_churn.csv"),
])

if __name__ == "__main__":
    app.run(debug=True, port=8051)   # port 8051 agar bisa jalan bersamaan dengan app_dash_dasar.py
