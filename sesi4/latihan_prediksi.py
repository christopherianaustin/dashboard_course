# sesi4/latihan_prediksi.py — Latihan mandiri Sesi 4 no. 1–4
# Dasar: app_prediksi.py, ditambah:
#   1. Slider threshold keputusan (0,3–0,7) di sidebar
#   2. Validasi CSV — uji dengan sesi4/contoh_kontrak_salah.csv
#   3. Tabel ringkasan region × risk_category (pd.crosstab)
#   4. Potensi pendapatan berisiko = jumlah monthly_charges pelanggan berkategori Tinggi
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))                      # agar folder utils bisa di-import
from utils.model_utils import load_model, load_metadata, validate_input, predict

st.set_page_config(page_title="Prediksi Churn — Latihan", page_icon="🤖", layout="wide")


@st.cache_resource
def get_model():
    return load_model()


@st.cache_data
def get_meta():
    return load_metadata()


model, meta_asli = get_model(), get_meta()

# ---------- Latihan 1: threshold keputusan dari slider di sidebar ----------
st.sidebar.header("⚙️ Pengaturan")
threshold = st.sidebar.slider("Threshold keputusan", min_value=0.30, max_value=0.70,
                              value=float(meta_asli["decision_threshold"]), step=0.05)
st.sidebar.caption("Probabilitas ≥ threshold → diprediksi churn. Kategori risiko tidak berubah "
                   "karena memakai risk bins yang tetap.")
meta = {**meta_asli, "decision_threshold": threshold}   # salinan; metadata asli tidak diubah

st.title("🤖 Prediksi Risiko Churn Pelanggan — Latihan")
with st.expander("ℹ️ Informasi model final", expanded=False):
    st.write(f"**{meta['model_name']}** · versi {meta['model_version']} · {meta['algorithm']}")
    st.write("Fitur input:", ", ".join(meta["feature_order"]))
    st.write(f"Threshold keputusan: {meta['decision_threshold']:.2f} "
             f"(bawaan model {meta_asli['decision_threshold']}) · Risk bins: {meta['risk_bins']}")
    st.caption("Model tidak dilatih ulang di aplikasi ini; aplikasi hanya melakukan inference.")

COLOR = {"Rendah": "🟢", "Sedang": "🟡", "Tinggi": "🔴"}
RISK_ORDER = ["Rendah", "Sedang", "Tinggi"]
tab_single, tab_batch = st.tabs(["👤 Prediksi satu pelanggan", "📂 Prediksi batch (CSV)"])

# ---------- Prediksi satu pelanggan ----------
with tab_single:
    cats = meta["categories"]
    with st.form("form_prediksi"):
        c1, c2, c3 = st.columns(3)
        region = c1.selectbox("Region", cats["region"])
        segment = c1.selectbox("Segmen", cats["segment"])
        contract = c2.selectbox("Jenis kontrak", cats["contract_type"])
        payment = c2.selectbox("Metode pembayaran", cats["payment_method"])
        service = c3.selectbox("Layanan internet", cats["internet_service"])
        tenure = c3.number_input("Tenure (bulan)", 1, 72, 6)
        d1, d2, d3 = st.columns(3)
        monthly = d1.number_input("Tagihan bulanan (Rp)", 100_000, 2_000_000, 450_000, step=10_000)
        complaints = d2.number_input("Jumlah keluhan", 0, 10, 2)
        calls = d3.number_input("Panggilan ke CS", 0, 15, 3)
        submitted = st.form_submit_button("🔮 Prediksi", type="primary")

    if submitted:
        row = pd.DataFrame([{
            "tenure_months": tenure, "monthly_charges": monthly,
            "total_charges": monthly * tenure, "num_complaints": complaints,
            "support_calls": calls, "region": region, "segment": segment,
            "contract_type": contract, "payment_method": payment, "internet_service": service,
        }])
        errs = validate_input(row, meta)
        if errs:
            st.error("\n".join(errs))
        else:
            res = predict(model, row, meta).iloc[0]
            m1, m2, m3 = st.columns(3)
            m1.metric("Probabilitas churn", f"{res.churn_probability:.1%}")
            m2.metric("Prediksi", "Churn" if res.predicted_churn else "Bertahan",
                      help=f"Threshold {threshold:.2f}")
            m3.metric("Kategori risiko", f"{COLOR[res.risk_category]} {res.risk_category}")
            st.progress(float(res.churn_probability))
            if res.risk_category == "Tinggi":
                st.error("Rekomendasi: prioritaskan retensi — tawarkan migrasi ke kontrak tahunan "
                         "dan tindak lanjuti keluhan dalam 48 jam.")
            elif res.risk_category == "Sedang":
                st.warning("Rekomendasi: pantau, kirim survei kepuasan dan penawaran loyalitas.")
            else:
                st.success("Rekomendasi: pertahankan layanan standar.")

# ---------- Prediksi batch ----------
with tab_batch:
    up = st.file_uploader("Upload CSV pelanggan baru (format sama dengan data/new_customers.csv)",
                          type="csv")
    st.caption("Latihan 2: upload sesi4/contoh_kontrak_salah.csv untuk melihat pesan validasi.")
    pakai_contoh = st.checkbox("Gunakan contoh data/new_customers.csv", value=up is None)
    if up is not None:
        data = pd.read_csv(up)
    elif pakai_contoh:
        data = pd.read_csv(ROOT / "data" / "new_customers.csv")
    else:
        st.info("Upload file atau centang contoh data.")
        st.stop()

    # Latihan 2: validasi sebelum prediksi — kategori salah seperti "Mingguan" ditolak
    errs = validate_input(data, meta)
    if errs:
        for e in errs:
            st.error(e)
        st.stop()

    hasil = predict(model, data, meta)
    tinggi = hasil[hasil.risk_category == "Tinggi"]

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Pelanggan diproses", f"{len(hasil):,}")
    k2.metric("Prediksi churn", f"{hasil.predicted_churn.sum():,}",
              help=f"Probabilitas ≥ threshold {threshold:.2f}")
    k3.metric("Rata-rata probabilitas", f"{hasil.churn_probability.mean():.1%}")
    k4.metric("Risiko tinggi", f"{len(tinggi):,}")
    # Latihan 4: potensi pendapatan berisiko
    k5.metric("Pendapatan berisiko / bulan", f"Rp{tinggi.monthly_charges.sum():,.0f}".replace(",", "."),
              help="Jumlah monthly_charges pelanggan berkategori Tinggi")

    RISK_COLOR = {"Rendah": "#1baf7a", "Sedang": "#eda100", "Tinggi": "#e34948"}
    a, b = st.columns(2)
    donut = px.pie(hasil, names="risk_category", hole=0.55, color="risk_category",
                   color_discrete_map=RISK_COLOR, title="Komposisi kategori risiko",
                   category_orders={"risk_category": RISK_ORDER})
    donut.update_traces(textinfo="percent+label")
    a.plotly_chart(donut.update_layout(height=330, showlegend=False), width="stretch")
    pk = hasil.groupby("contract_type", as_index=False)["churn_probability"].mean()
    bar = px.bar(pk, x="contract_type", y="churn_probability", text_auto=".1%",
                 color_discrete_sequence=["#eb6834"], title="Rata-rata probabilitas churn per kontrak")
    bar.update_yaxes(tickformat=".0%")
    b.plotly_chart(bar.update_layout(height=330, template="plotly_white", xaxis_title=""),
                   width="stretch")

    # Latihan 3: ringkasan region × risk_category
    st.subheader("Jumlah pelanggan per region × kategori risiko")
    ringkas = pd.crosstab(hasil["region"], hasil["risk_category"], margins=True, margins_name="Total")
    ringkas = ringkas.reindex(columns=[c for c in RISK_ORDER + ["Total"] if c in ringkas.columns])
    st.dataframe(ringkas, width="stretch")

    risiko = st.multiselect("Tampilkan kategori risiko", ["Tinggi", "Sedang", "Rendah"],
                            default=["Tinggi"])
    tampil = hasil[hasil.risk_category.isin(risiko)].sort_values("churn_probability",
                                                                 ascending=False)
    st.dataframe(tampil, width="stretch", height=320,
                 column_config={"churn_probability": st.column_config.ProgressColumn(
                     "Probabilitas churn", min_value=0.0, max_value=1.0, format="%.2f")})
    st.download_button("⬇️ Unduh hasil prediksi", hasil.to_csv(index=False).encode("utf-8"),
                       "hasil_prediksi_churn.csv", "text/csv")
