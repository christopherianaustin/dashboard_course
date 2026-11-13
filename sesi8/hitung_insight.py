# sesi8/hitung_insight.py — menghitung angka untuk insight & rekomendasi (8.7)
# Jalankan: python sesi8/hitung_insight.py
# Pengolahan data sama persis dengan app_final_dashboard.py, sehingga angkanya cocok dengan dashboard.
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from utils.model_utils import load_model, load_metadata, predict

META, MODEL = load_metadata(), load_model()
raw = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])
raw["total_charges"] = raw["total_charges"].fillna(raw["monthly_charges"] * raw["tenure_months"])
DF = predict(MODEL, raw, META)
T = DF[DF.risk_category == "Tinggi"]


def pct(x): return f"{x:.1%}".replace(".", ",")
def angka(x, d=1): return f"{x:.{d}f}".replace(".", ",")
def rupiah(x): return f"Rp{x:,.0f}".replace(",", ".")


porsi_bayar = DF.groupby("payment_method")["risk_category"].apply(lambda s: s.eq("Tinggi").mean())
porsi_region = DF.groupby("region")["risk_category"].apply(lambda s: s.eq("Tinggi").mean())
churn_risk = DF.groupby("risk_category")["churn"].mean()

print("KPI dashboard tanpa filter")
print(f"  Pelanggan {len(DF):,} · churn aktual {DF.churn.mean():.1%} · rata-rata prob "
      f"{DF.churn_probability.mean():.1%} · risiko tinggi {len(T):,} · tagihan {rupiah(T.monthly_charges.sum())}/bln")

print("\nInsight")
print(f"1. {len(T)} pelanggan ({pct(len(T) / len(DF))}) berisiko tinggi; tagihan "
      f"Rp{angka(T.monthly_charges.sum() / 1e6)} juta/bulan")
print(f"2. {pct(T.contract_type.eq('Bulanan').mean())} pelanggan risiko tinggi berkontrak Bulanan")
print(f"3. Rata-rata tenure risiko tinggi {angka(T.tenure_months.mean())} bln vs semua "
      f"{angka(DF.tenure_months.mean())} bln")
print(f"4. Rata-rata keluhan risiko tinggi {angka(T.num_complaints.mean(), 2)} vs semua "
      f"{angka(DF.num_complaints.mean(), 2)}")
print("5. Porsi risiko tinggi per metode bayar: " +
      ", ".join(f"{k} {pct(v)}" for k, v in porsi_bayar.sort_values(ascending=False).items()))
print("6. Porsi risiko tinggi per region: " +
      ", ".join(f"{k} {pct(v)}" for k, v in porsi_region.sort_values(ascending=False).items()))
print("7. Churn aktual per kategori: " +
      ", ".join(f"{k} {pct(churn_risk[k])}" for k in ["Tinggi", "Sedang", "Rendah"]))
print(f"8. Pelanggan aktif (belum churn) berisiko tinggi: {(T.churn == 0).sum()}")
