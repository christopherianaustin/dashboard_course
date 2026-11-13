# Final Project — Customer Churn Intelligence Dashboard

Dokumen pendamping dashboard `sesi8/app_final_dashboard.py` (template Buku Praktikum 8.9).
Semua angka di dokumen ini dihitung ulang oleh `sesi8/hitung_insight.py` dan sama dengan tampilan dashboard.

Jalankan dashboard: `python sesi8/app_final_dashboard.py` → buka http://127.0.0.1:8053

---

## 1. Business Problem

Sebuah penyedia layanan internet kehilangan sekitar sepertiga pelanggannya. Tim retensi perlu tahu
ke mana harus fokus.

**Pertanyaan bisnis:** pelanggan mana yang berisiko churn, di segmen mana risiko terkonsentrasi,
dan tindakan apa yang perlu diambil?

## 2. Data Understanding

| Aspek | Keterangan |
|---|---|
| Sumber | `data/customer_churn.csv` — data latihan sintetis (seed tetap) |
| Ukuran | 3.000 pelanggan, 13 kolom; pendaftaran Januari 2023 – Desember 2025 |
| Target | `churn` (1 = berhenti berlangganan); churn rate keseluruhan **34,9%** |
| Fitur | 5 numerik (tenure, tagihan bulanan, total tagihan, keluhan, panggilan CS) dan 5 kategorik (region, segmen, kontrak, metode bayar, layanan internet) |
| Kualitas data | 45 baris `total_charges` kosong. Di dashboard diisi `monthly_charges × tenure_months`; di dalam model diisi median oleh Pipeline |
| Data inference | `data/new_customers.csv` — 200 pelanggan baru tanpa label |

## 3. EDA (Sesi 2)

- **Jenis kontrak adalah pembeda terkuat:** churn Bulanan 54,6%, Tahunan 16,8%, Dua Tahun 9,7%.
- **Keluhan menaikkan churn secara bertahap:** 0 keluhan 26,7% → 2 keluhan 42,4% → 4 keluhan 53,5% → 5 keluhan 72,0%.
- **Tenure pendek lebih rentan:** churn terkonsentrasi pada pelanggan dengan tenure di bawah 12 bulan.
- **Layanan internet bukan pembeda:** Fiber 34,7%, DSL 34,9%, Mobile Broadband 35,5%.
- **Churn per kuartal pendaftaran relatif stabil:** 31,3% – 39,3%, tidak ada tren memburuk.

## 4. Visualization

| Chart | Pertanyaan yang dijawab | Alasan pemilihan |
|---|---|---|
| Donut komposisi kategori risiko | Berapa porsi pelanggan berisiko? | Komposisi 3 kategori; angka total di tengah |
| Bar horizontal porsi risiko tinggi per region | Region mana yang diprioritaskan? | Perbandingan 5 kategori, diurutkan |
| Line churn aktual vs prediksi per kuartal | Apakah prediksi sejalan dengan kenyataan dari waktu ke waktu? | Tren waktu, dua seri |
| Stacked bar risiko per jenis kontrak | Di kontrak mana risiko terkumpul? | Komposisi di dalam tiap kategori |
| Histogram probabilitas + garis threshold | Bagaimana sebaran skor model? | Distribusi; garis menjelaskan batas 0,5 |
| Scatter region aktual vs prediksi | Apakah model akurat per region? | Hubungan dua ukuran; ukuran titik = jumlah pelanggan |
| Gauge (tab simulasi) | Seberapa berisiko satu pelanggan ini? | KPI tunggal berwarna sesuai kategori |

## 5. Final ML Model

| Atribut | Nilai |
|---|---|
| File | `models/churn_model.joblib` + `models/model_metadata.json` |
| Jenis | scikit-learn Pipeline: imputasi median + standarisasi + one-hot encoding → GradientBoostingClassifier |
| Kinerja holdout | ROC-AUC 0,7887 · akurasi 0,7183 · F1 0,5786 |
| Threshold | 0,5 (probabilitas ≥ 0,5 → diprediksi churn) |
| Kategori risiko | Rendah < 0,30 · Sedang 0,30–0,60 · Tinggi ≥ 0,60 |

Model tidak dilatih ulang di dashboard. Catatan asal-usul: file model dibuat ulang dengan
`models/prepare_final_model.py` mengikuti spesifikasi buku, dan hasilnya identik dengan semua angka acuan buku
(metrik holdout, output `cek_inference.py`, dan checkpoint Sesi 4 & 8).

## 6. Model Loading & Inference

1. `load_model()` / `load_metadata()` di `utils/model_utils.py` — dimuat **sekali** saat aplikasi start.
2. `validate_input()` — menolak kolom hilang, kategori tak dikenal (mis. "Mingguan"), atau kolom numerik bertipe teks.
3. `prepare_input()` — memilih dan mengurutkan 10 fitur sesuai `feature_order`.
4. `predict()` — `predict_proba(X)[:, 1]` → probabilitas, kelas (threshold 0,5), dan kategori risiko.

Batch inference dijalankan untuk seluruh 3.000 pelanggan saat start; callback filter hanya memotong
DataFrame yang sudah berisi prediksi, sehingga respons cepat.

## 7. Prediction Output

- **Probabilitas churn** (0–100%) — di tabel prioritas, histogram, dan gauge simulasi.
- **Kelas prediksi** — Churn / Bertahan (threshold 0,5).
- **Kategori risiko** — Rendah / Sedang / Tinggi, dipakai juga sebagai **filter** di sidebar.
- **Rekomendasi tindakan** per kategori pada tab Simulasi Prediksi.

## 8. Interactive Components

- **5 filter** di sidebar: region, segmen, jenis kontrak, kategori risiko (output model), rentang tenure.
- **9 input simulasi**: region, segmen, kontrak, pembayaran, layanan, tenure, tagihan, keluhan, panggilan CS + tombol *Jalankan prediksi*.
- **Tabel** dengan sort, filter per kolom, dan paging.
- Hover, zoom, dan legend toggle bawaan Plotly di semua chart.

## 9. Callback / App Logic

| Callback | Input | Output |
|---|---|---|
| `update_overview` | 5 filter (region, segmen, kontrak, risiko, tenure) | 4 KPI, 6 chart, data tabel, judul tabel |
| `run_prediction` | Tombol (Input) + 9 field form (State), `prevent_initial_call=True` | Teks hasil prediksi + gauge |

- Filter kosong (mis. semua kontrak tidak dicentang) → pesan "Tidak ada data — longgarkan filter", tanpa error.
- Field simulasi kosong → `PreventUpdate`, hasil sebelumnya tidak berubah.
- Callback tidak mengubah variabel global (aman untuk banyak pengguna).

## 10. Dashboard — pemenuhan requirement minimum

| Requirement | Implementasi | Status |
|---|---|---|
| ≥ 4 KPI | Pelanggan, Churn rate aktual, Rata-rata prob. churn, Risiko tinggi (+ tagihan berisiko) | ✅ |
| ≥ 3 visualisasi | 6 chart Plotly + gauge | ✅ |
| ≥ 2 filter/input | 5 filter + 9 input simulasi | ✅ |
| ≥ 1 tampilan prediksi | Filter risiko, histogram probabilitas, tabel prioritas, gauge | ✅ |
| ≥ 1 tabel detail | Tabel prioritas retensi (200 teratas, sort/filter/paging) | ✅ |
| Layout jelas | Header → KPI → chart → tabel; filter di sidebar; tab simulasi terpisah | ✅ |
| Judul, unit, periode | Judul deskriptif, format %, Rupiah, periode 2023–2025 di header | ✅ |
| Menjawab pertanyaan bisnis | Pertanyaan di header; dijawab KPI risiko + tabel prioritas | ✅ |

**Checkpoint 8.6 (sudah diuji):** tanpa filter 3.000 pelanggan · 34,9% · 34,7% · 624 risiko tinggi · Rp288.289.000/bln;
filter hanya Tinggi → semua chart/tabel hanya risiko tinggi; kontrak kosong → pesan tanpa error;
simulasi default → 71,1%, Churn, Tinggi, gauge merah.

## 11. Insight & Recommendation

| # | Insight (angka dari dashboard) | Rekomendasi |
|---|---|---|
| 1 | **624 pelanggan (20,8%)** berada di kategori risiko tinggi, dengan tagihan **Rp288,3 juta per bulan**. | Jadikan angka ini target utama program retensi; pantau bulanan. |
| 2 | **96,0%** pelanggan risiko tinggi berkontrak **Bulanan**. | Program migrasi ke kontrak Tahunan dengan insentif diskon untuk pelanggan Bulanan berisiko tinggi. |
| 3 | Rata-rata tenure risiko tinggi **14,0 bulan**, hampir separuh rata-rata seluruh pelanggan (26,5 bulan). | Perkuat onboarding dan kontak proaktif pada 12 bulan pertama. |
| 4 | Rata-rata keluhan risiko tinggi **1,78**, dibanding 1,13 untuk seluruh pelanggan. | SLA penyelesaian keluhan maksimal 48 jam untuk pelanggan berisiko tinggi. |
| 5 | Porsi risiko tinggi pada **Transfer Bank 27,4%**, tertinggi dibanding E-Wallet 19,6%, Kartu Kredit 17,0%, Virtual Account 16,6%. | Dorong autodebit atau e-wallet untuk mengurangi friksi pembayaran. |
| 6 | **Sumatera** memiliki porsi risiko tinggi terbesar (**24,3%**); Bali-Nusa Tenggara terendah (18,3%). | Prioritaskan kampanye retensi regional di Sumatera. |
| 7 | Kategori risiko konsisten dengan data historis: churn aktual **78,5%** di Tinggi, 45,4% di Sedang, 9,7% di Rendah. | Kategori risiko layak dipakai untuk memprioritaskan kerja tim retensi. |
| 8 | **134 pelanggan masih aktif** (belum churn) tetapi masuk kategori risiko tinggi. | Jadikan 134 pelanggan ini daftar kerja pertama tim retensi minggu ini (tabel prioritas, filter Risiko = Tinggi). |

**Keterbatasan**
- Data sintetis untuk latihan; pola nyata dapat berbeda.
- Sebagian data yang dipakai untuk insight 7 juga dipakai saat model dilatih, sehingga angka tersebut cenderung
  lebih baik daripada kinerja pada pelanggan baru. Acuan kinerja yang adil adalah metrik holdout (ROC-AUC 0,79).
- Model menunjukkan **siapa** yang berisiko, bukan **mengapa**; rekomendasi perlu diuji (mis. A/B test penawaran kontrak).

---

## Struktur presentasi 5–7 menit (8.8)

| Waktu | Bagian | Isi yang disampaikan |
|---|---|---|
| 0:30 | Masalah bisnis | ±1 dari 3 pelanggan churn; pertanyaan: siapa yang berisiko dan apa tindakannya? |
| 0:45 | Data & model | 3.000 pelanggan 2023–2025; GradientBoosting (ROC-AUC 0,79); arti probabilitas, threshold 0,5, dan 3 kategori risiko |
| 2:00 | Tur dashboard | KPI → donut risiko → region → kontrak → histogram + threshold → aktual vs prediksi → tabel prioritas |
| 1:00 | Demo interaksi | Filter Risiko = Tinggi + region Sumatera; lalu tab Simulasi: nilai default (71,1%), ganti kontrak ke Dua Tahun & tenure 48 → risiko turun drastis |
| 1:30 | Insight | Insight 1, 2, 3, 5, 8 |
| 1:00 | Rekomendasi & keterbatasan | Migrasi kontrak, onboarding 12 bulan, SLA keluhan; data sintetis, kinerja holdout |

## Checklist final submission (8.10)

- [x] Source code Streamlit/Dash — `sesi1/` … `sesi8/`
- [x] Dataset / analytical data — `data/customer_churn.csv`, `data/new_customers.csv`
- [x] EDA workflow — `sesi2/eda_churn.py`, `sesi2/app_eda.py`
- [x] Interactive Plotly visualizations — `sesi6/`, dashboard final
- [x] Final trained / selected best-performing ML model — `models/churn_model.joblib`
- [x] Model loading & inference workflow — `utils/model_utils.py`, `sesi4/cek_inference.py`
- [x] Prediction result/output — `sesi4/app_prediksi.py`, dashboard final
- [x] Interactive dashboard — `sesi8/app_final_dashboard.py`
- [x] Filter/input components — 5 filter + 9 input simulasi
- [x] Callback implementation — `sesi7/`, `sesi8/`
- [x] Business insight — bagian 11
- [x] Recommendation — bagian 11
- [ ] Presentasi final project — gunakan struktur di atas
