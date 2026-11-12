# sesi1/latihan_kalkulator_plus.py — Latihan mandiri Sesi 1 no. 1, 2, dan 4
import streamlit as st

st.set_page_config(page_title="Kalkulator Tagihan Plus", page_icon="🧾")

st.title("🧾 Kalkulator Estimasi Tagihan Internet (Plus)")
st.write("Masukkan paket, durasi, dan promo untuk melihat estimasi biaya.")

# Latihan 1: tambah layanan "Satelit" — cukup satu entri baru di dictionary
HARGA = {"DSL": 260_000, "Fiber": 420_000, "Mobile Broadband": 310_000, "Satelit": 550_000}
DISKON = {"Bulanan": 0.00, "Tahunan": 0.10, "Dua Tahun": 0.18}

# Latihan 4: siapkan penghitung klik di session_state (hanya dibuat sekali)
if "jumlah_klik" not in st.session_state:
    st.session_state.jumlah_klik = 0

layanan = st.selectbox("Jenis layanan", list(HARGA))
kontrak = st.radio("Jenis kontrak", list(DISKON), horizontal=True)
bulan = st.number_input("Durasi (bulan)", min_value=1, max_value=72, value=12, step=1)
# Latihan 2: slider diskon promosi tambahan 0–20%
promo = st.slider("Diskon promosi tambahan (%)", min_value=0, max_value=20, value=0)
ppn = st.checkbox("Tambahkan PPN 11%", value=True)

if st.button("Hitung", type="primary"):
    st.session_state.jumlah_klik += 1  # Latihan 4: bertambah setiap tombol diklik

    # Diskon kontrak dulu, lalu diskon promo dari harga yang sudah didiskon
    per_bulan = HARGA[layanan] * (1 - DISKON[kontrak]) * (1 - promo / 100)
    total = per_bulan * bulan * (1.11 if ppn else 1)
    hemat = 1 - per_bulan / HARGA[layanan]  # total penghematan dari harga normal

    st.metric("Biaya per bulan", f"Rp{per_bulan:,.0f}".replace(",", "."))
    st.metric(
        "Total estimasi",
        f"Rp{total:,.0f}".replace(",", "."),
        delta=f"hemat {hemat:.0%}" if hemat else None,
    )

# Ditulis setelah blok tombol agar angka sudah termasuk klik terbaru
st.caption(f"Tombol Hitung sudah diklik {st.session_state.jumlah_klik} kali.")
st.caption("Estimasi bersifat ilustratif untuk latihan.")
