# sesi2/latihan_sesi2.py — Latihan mandiri Sesi 2 no. 1–4 (jalankan: python sesi2/latihan_sesi2.py)
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # agar bisa jalan tanpa layar
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sesi2" / "output"
OUT.mkdir(exist_ok=True)

# ---------- Gaya visual sama dengan eda_churn.py ----------
BIRU, ORANYE, HIJAU, KUNING, UNGU = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#4a3aa7"
WARNA = [BIRU, HIJAU, KUNING, UNGU, "#e87ba4"]
TEKS, TEKS2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
STATUS = {"Bertahan": BIRU, "Churn": ORANYE}
plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 200, "font.size": 10, "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.spines.top": False,
    "axes.spines.right": False, "axes.edgecolor": "#b9b8b2", "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.labelcolor": TEKS2, "xtick.color": TEKS2, "ytick.color": TEKS2,
})


def simpan(fig, nama):
    fig.tight_layout()
    fig.savefig(OUT / nama, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  tersimpan:", nama)


df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])
df["status"] = df["churn"].map({0: "Bertahan", 1: "Churn"})

# =============== LATIHAN 1: pie vs donut vs bar horizontal ===============
# 1a. Pie internet_service (3 kategori)
s = df["internet_service"].value_counts()
fig, ax = plt.subplots(figsize=(5, 4))
_, _, persen = ax.pie(s, labels=s.index, autopct="%1.1f%%", colors=WARNA[:3], startangle=90,
                      counterclock=False, wedgeprops=dict(edgecolor="white", linewidth=2))
for t in persen:
    t.set_color("white"); t.set_fontweight("bold")
ax.set_title("Fiber dipakai hampir separuh pelanggan")
simpan(fig, "latihan_1a_pie_internet_service.png")

# 1b. Donut region (5 kategori)
r = df["region"].value_counts()
fig, ax = plt.subplots(figsize=(5.5, 4))
ax.pie(r, colors=WARNA, startangle=90, counterclock=False,
       wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2))
ax.legend([f"{k} {v / len(df):.0%}" for k, v in r.items()], loc="center left",
          bbox_to_anchor=(0.95, 0.5), frameon=False)
ax.set_title("Donut region: 5 irisan sulit dibandingkan")
simpan(fig, "latihan_1b_donut_region.png")

# 1c. Bar horizontal terurut untuk region (pembanding)
rs = r.sort_values()
fig, ax = plt.subplots(figsize=(6.5, 3.6))
bars = ax.barh(rs.index, rs.values, color=BIRU, height=0.55)
ax.bar_label(bars, labels=[f"{v:,} ({v / len(df):.0%})".replace(",", ".") for v in rs.values],
             padding=3, color=TEKS)
ax.set(xlabel="Jumlah pelanggan", xlim=(0, rs.max() * 1.25)); ax.grid(axis="y", visible=False)
ax.set_title("Jawa menyumbang pelanggan terbanyak")
simpan(fig, "latihan_1c_barh_region.png")

# =============== LATIHAN 2: stacked bar 100% status per internet_service ===============
ct = pd.crosstab(df["internet_service"], df["status"], normalize="index").sort_values("Churn") * 100
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.barh(ct.index, ct["Bertahan"], color=BIRU, label="Bertahan", height=0.55)
ax.barh(ct.index, ct["Churn"], left=ct["Bertahan"], color=ORANYE, label="Churn", height=0.55)
for i, v in enumerate(ct["Churn"]):
    ax.text(100 - v / 2, i, f"{v:.1f}%", ha="center", va="center", color="white", fontweight="bold")
ax.set(xlabel="Proporsi pelanggan (%)", xlim=(0, 100)); ax.grid(axis="y", visible=False)
ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False)
ax.set_title("Layanan internet bukan pembeda churn")
simpan(fig, "latihan_2_stacked_internet_service.png")

# =============== LATIHAN 3: box plot support_calls per status ===============
fig, ax = plt.subplots(figsize=(6, 4))
bp = ax.boxplot([df.loc[df.status == s, "support_calls"] for s in ["Bertahan", "Churn"]],
                tick_labels=["Bertahan", "Churn"], patch_artist=True, widths=0.5,
                medianprops=dict(color=TEKS))
for patch, s in zip(bp["boxes"], ["Bertahan", "Churn"]):
    patch.set_facecolor(STATUS[s]); patch.set_alpha(0.55)
ax.set(ylabel="Jumlah panggilan ke CS")
ax.set_title("Median sama, tetapi sebaran panggilan CS lebih lebar pada churn")
simpan(fig, "latihan_3_box_support_calls.png")

# =============== LATIHAN 4: line chart churn rate per kuartal pendaftaran ===============
q = df.groupby(df.signup_date.dt.to_period("Q"))["churn"].mean() * 100
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot(q.index.astype(str), q.values, color=ORANYE, marker="o", linewidth=2)
ax.axhline(df.churn.mean() * 100, color=TEKS2, linestyle="--", linewidth=1)
ax.text(len(q) - 0.5, df.churn.mean() * 100 + 5, f"rata-rata {df.churn.mean():.1%}",
        ha="right", color=TEKS2, fontsize=9)
ax.set(xlabel="Kuartal pendaftaran", ylabel="Churn rate (%)", ylim=(0, 50))
ax.tick_params(axis="x", rotation=45)
ax.set_title("Churn rate per kuartal pendaftaran relatif stabil")
simpan(fig, "latihan_4_line_churn_kuartal.png")

# ---------- Angka pendukung untuk menulis insight ----------
print("\nPorsi churn per internet_service (%):\n", ct["Churn"].round(1))
print("\nsupport_calls per status:\n", df.groupby("status")["support_calls"].agg(["median", "mean"]).round(2))
print("\nChurn rate per kuartal (%): min {:.1f}, maks {:.1f}".format(q.min(), q.max()))
print("\nChurn rate per jumlah keluhan:\n",
      df.groupby("num_complaints")["churn"].agg(["count", "mean"]).round(3))
