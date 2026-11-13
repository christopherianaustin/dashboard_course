# sesi7/latihan_callback.py — Latihan mandiri Sesi 7 no. 1–5
# Dasar: app_dash_callback.py, ditambah:
#   1. dcc.Checklist internet_service yang terhubung ke filter_df()
#   2. Output kelima di callback utama: histogram tenure yang ikut terfilter
#   3. Klik titik scatter -> detail pelanggan di html.Div
#   4. dcc.Store menyimpan hasil filter (to_dict("records")) sekali; callback tabel membaca dari store
#   5. Tantangan: selectedData (box/lasso select) pada scatter memfilter tabel
# Jalankan: python sesi7/latihan_callback.py  lalu buka http://127.0.0.1:8053
from pathlib import Path
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])
df["status"] = df["churn"].map({0: "Bertahan", 1: "Churn"})
WARNA = {"Bertahan": "#4C72B0", "Churn": "#C44E52"}
KARTU = {"flex": 1, "padding": "14px", "borderRadius": "10px", "background": "#F4F6FA",
         "textAlign": "center"}
TABEL_COLS = ["customer_id", "region", "segment", "contract_type", "internet_service",
              "tenure_months", "monthly_charges", "num_complaints", "status"]
LAYANAN = ["Fiber", "DSL", "Mobile Broadband"]
ABU = {"color": "#666"}

app = Dash(__name__, title="Dash Callback — Latihan")
app.layout = html.Div(style={"maxWidth": "1200px", "margin": "auto", "fontFamily": "Arial",
                             "padding": "0 16px"}, children=[
    html.H1("Dash Callback System — Latihan Sesi 7"),

    # ---- Panel filter ----
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr 1fr", "gap": "16px"}, children=[
        html.Div([html.Label("Region"),
                  dcc.Dropdown(id="dd-region", options=sorted(df.region.unique()), multi=True,
                               placeholder="Semua region")]),
        html.Div([html.Label("Segmen (opsi bergantung region)"),
                  dcc.Dropdown(id="dd-segment", multi=True, placeholder="Semua segmen")]),
        html.Div([html.Label("Jenis kontrak"),
                  dcc.RadioItems(id="rd-kontrak", inline=True, value="Semua",
                                 options=["Semua", "Bulanan", "Tahunan", "Dua Tahun"])]),
        # Latihan 1: checklist layanan internet
        html.Div([html.Label("Layanan internet"),
                  dcc.Checklist(id="cl-internet", options=LAYANAN, value=LAYANAN, inline=True,
                                inputStyle={"marginRight": "4px", "marginLeft": "8px"})]),
    ]),
    html.Div(style={"marginTop": "12px"}, children=[
        html.Label("Tenure (bulan)"),
        dcc.RangeSlider(id="rs-tenure", min=1, max=72, step=1, value=[1, 72],
                        marks={i: str(i) for i in (1, 12, 24, 36, 48, 60, 72)}),
    ]),
    html.Div(style={"display": "flex", "gap": "8px", "alignItems": "center"}, children=[
        html.Label("Minimal jumlah keluhan:"),
        dcc.Input(id="in-keluhan", type="number", min=0, max=10, value=0, style={"width": "70px"}),
        html.Button("Terapkan", id="btn-terapkan", n_clicks=0),
        html.Button("Reset filter", id="btn-reset", n_clicks=0),
        html.Span(id="info-keluhan", style=ABU),
    ]),
    dcc.Store(id="store-keluhan", data=0),
    dcc.Store(id="store-data"),                     # Latihan 4: hasil filter disimpan di browser

    # ---- KPI ----
    html.Div(id="kpi", style={"display": "flex", "gap": "12px", "margin": "16px 0"}),

    # ---- Charts ----
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"}, children=[
        dcc.Graph(id="g-bar"), dcc.Graph(id="g-scatter")]),
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"}, children=[
        dcc.Graph(id="g-hist"),                     # Latihan 2
        html.Div([                                  # Latihan 3
            html.H3("Detail pelanggan terpilih"),
            html.Div(id="detail-pelanggan", style={**KARTU, "textAlign": "left"}),
        ]),
    ]),
    html.P("Tip: klik batang region untuk memfilter tabel; klik titik scatter untuk melihat detail "
           "pelanggan; drag kotak (atau pilih Lasso Select di pojok kanan atas scatter) untuk memfilter "
           "tabel ke pelanggan terpilih. Double-click scatter untuk membatalkan pilihan.", style=ABU),
    html.H3(id="judul-tabel"),
    dash_table.DataTable(id="tbl", page_size=10, sort_action="native",
                         columns=[{"name": c, "id": c} for c in TABEL_COLS],
                         style_cell={"padding": "6px", "textAlign": "left"},
                         style_header={"fontWeight": "bold", "background": "#E9EDF5"},
                         style_data_conditional=[{"if": {"filter_query": "{status} = 'Churn'"},
                                                  "backgroundColor": "#FBE9EA"}]),
])


def filter_df(region, segment, kontrak, tenure, min_keluhan, internet):
    d = df
    if region:
        d = d[d.region.isin(region)]
    if segment:
        d = d[d.segment.isin(segment)]
    if kontrak and kontrak != "Semua":
        d = d[d.contract_type == kontrak]
    if internet is not None:                        # Latihan 1: tidak ada yang dicentang = data kosong
        d = d[d.internet_service.isin(internet)]
    d = d[d.tenure_months.between(tenure[0], tenure[1])]
    return d[d.num_complaints >= (min_keluhan or 0)]


# 1) Chained callback: opsi segmen bergantung pada region terpilih
@callback(Output("dd-segment", "options"), Input("dd-region", "value"))
def update_segment_options(region):
    d = df[df.region.isin(region)] if region else df
    return sorted(d.segment.unique())


# 2) Tombol Terapkan / Reset (Reset juga mengembalikan checklist layanan internet)
@callback(Output("store-keluhan", "data"), Output("in-keluhan", "value"),
          Output("dd-region", "value"), Output("dd-segment", "value"),
          Output("rd-kontrak", "value"), Output("rs-tenure", "value"),
          Output("cl-internet", "value"),
          Input("btn-terapkan", "n_clicks"), Input("btn-reset", "n_clicks"),
          State("in-keluhan", "value"), prevent_initial_call=True)
def terapkan_atau_reset(n_apply, n_reset, nilai):
    if ctx.triggered_id == "btn-reset":
        return 0, 0, None, None, "Semua", [1, 72], LAYANAN
    if nilai is None:
        raise PreventUpdate
    return nilai, no_update, no_update, no_update, no_update, no_update, no_update


# 3) Callback utama: 6 input -> KPI, 3 chart, info, dan store data (Latihan 2 & 4)
@callback(Output("kpi", "children"), Output("g-bar", "figure"), Output("g-scatter", "figure"),
          Output("info-keluhan", "children"), Output("g-hist", "figure"), Output("store-data", "data"),
          Input("dd-region", "value"), Input("dd-segment", "value"), Input("rd-kontrak", "value"),
          Input("rs-tenure", "value"), Input("store-keluhan", "data"), Input("cl-internet", "value"))
def update_dashboard(region, segment, kontrak, tenure, min_keluhan, internet):
    d = filter_df(region, segment, kontrak, tenure, min_keluhan, internet)
    info = f"Filter keluhan aktif: ≥ {min_keluhan}"
    data = d[TABEL_COLS].to_dict("records")          # Latihan 4: disimpan sekali di sini
    if d.empty:
        kosong = px.scatter(title="Tidak ada data untuk filter ini")
        return [html.Div("Data kosong", style=KARTU)], kosong, kosong, info, kosong, data

    def kartu(j, v):
        return html.Div([html.Small(j), html.H2(v, style={"margin": "4px 0"})], style=KARTU)
    kpi = [kartu("Pelanggan", f"{len(d):,}"), kartu("Churn rate", f"{d.churn.mean():.1%}"),
           kartu("Rata-rata tagihan", f"Rp{d.monthly_charges.mean():,.0f}".replace(",", ".")),
           kartu("Rata-rata keluhan", f"{d.num_complaints.mean():.2f}")]

    reg = d.groupby("region", as_index=False)["churn"].mean().sort_values("churn", ascending=False)
    bar = px.bar(reg, x="region", y="churn", template="plotly_white", title="Churn rate per region",
                 labels={"churn": "Churn rate", "region": ""}, color_discrete_sequence=["#C44E52"])
    bar.update_yaxes(tickformat=".0%")

    # custom_data membawa customer_id agar klik/seleksi titik bisa dilacak (Latihan 3 & 5)
    sc = px.scatter(d, x="tenure_months", y="monthly_charges", color="status", opacity=0.6,
                    color_discrete_map=WARNA, template="plotly_white", hover_name="customer_id",
                    custom_data=["customer_id"],
                    title="Tenure vs tagihan (drag untuk memilih)",
                    labels={"tenure_months": "Tenure (bulan)", "monthly_charges": "Tagihan (Rp)"})
    sc.update_layout(dragmode="select")

    # Latihan 2: histogram tenure yang ikut terfilter
    hist = px.histogram(d, x="tenure_months", color="status", nbins=24, barmode="overlay",
                        opacity=0.7, color_discrete_map=WARNA, template="plotly_white",
                        labels={"tenure_months": "Tenure (bulan)", "status": "Status"},
                        title="Distribusi tenure (terfilter)")
    hist.update_layout(yaxis_title="Pelanggan")
    return kpi, bar, sc, info, hist, data


# Latihan 3: klik titik scatter -> detail pelanggan
@callback(Output("detail-pelanggan", "children"), Input("g-scatter", "clickData"))
def tampil_detail(click):
    if not click or "customdata" not in click["points"][0]:
        return html.Span("Klik salah satu titik pada scatter.", style=ABU)
    cid = click["points"][0]["customdata"][0]
    r = df.loc[df.customer_id == cid].iloc[0]
    baris = [("ID pelanggan", r.customer_id), ("Region", r.region), ("Segmen", r.segment),
             ("Kontrak", r.contract_type), ("Jumlah keluhan", r.num_complaints),
             ("Tenure", f"{r.tenure_months} bulan"),
             ("Tagihan", f"Rp{r.monthly_charges:,.0f}".replace(",", ".")), ("Status", r.status)]
    return html.Table([html.Tr([html.Td(k, style={**ABU, "paddingRight": "16px"}),
                                html.Td(html.B(str(v)))]) for k, v in baris])


# 4) Tabel membaca dari store (Latihan 4), lalu klik batang atau seleksi scatter (Latihan 5)
@callback(Output("tbl", "data"), Output("judul-tabel", "children"),
          Input("store-data", "data"), Input("g-bar", "clickData"),
          Input("g-scatter", "selectedData"))
def update_tabel(data, click, selected):
    d = pd.DataFrame(data or [], columns=TABEL_COLS)
    judul = "Detail pelanggan (semua region terpilih)"
    if ctx.triggered_id == "g-bar" and click:
        reg = click["points"][0]["x"]
        d = d[d.region == reg]
        judul = f"Detail pelanggan — region {reg}"
    elif ctx.triggered_id == "g-scatter" and selected and selected.get("points"):
        ids = {p["customdata"][0] for p in selected["points"] if "customdata" in p}
        d = d[d.customer_id.isin(ids)]
        judul = f"Detail pelanggan — {len(d):,} pelanggan terpilih di scatter"
    return d.to_dict("records"), judul


if __name__ == "__main__":
    app.run(debug=True, port=8053)   # 8053 agar bisa jalan bersamaan dengan app_dash_callback.py (8052)
