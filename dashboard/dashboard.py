import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style="darkgrid")

# Load cleaned dataset
air_quality_df = pd.read_csv("main_data.csv")

# Mengubah kolom datetime ke tipe datetime
air_quality_df["datetime"] = pd.to_datetime(air_quality_df["datetime"])

# Mengurutkan data berdasarkan waktu
air_quality_df = air_quality_df.sort_values(by="datetime").reset_index(drop=True)

def create_station_pm25_df(df):
    station_pm25_df = (
        df.groupby("station")["PM2.5"]
        .mean()
        .reset_index()
        .sort_values(by="PM2.5", ascending=False)
    )

    return station_pm25_df

def create_wind_pm25_df(df):
    df = df.copy()

    df["wind_speed_category"] = pd.cut(
        df["WSPM"],
        bins=[-float("inf"), 1.1, 1.9, float("inf")],
        labels=["Rendah", "Sedang", "Tinggi"]
    )

    wind_pm25_df = (
        df.groupby(
            "wind_speed_category",
            observed=True
        )["PM2.5"]
        .mean()
        .reset_index()
    )

    return wind_pm25_df

# Dashboard title
st.header("🌫️ Air Quality Dashboard")

# Menentukan rentang tanggal dataset
min_date = air_quality_df["datetime"].min().date()
max_date = air_quality_df["datetime"].max().date()

with st.sidebar:
    st.header("Filter")

    date_range = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0]

    selected_stations = st.multiselect(
        label="Stasiun",
        options=sorted(air_quality_df["station"].unique()),
        default=sorted(air_quality_df["station"].unique())
    )

main_df = air_quality_df[
    (air_quality_df["datetime"].dt.date >= start_date) &
    (air_quality_df["datetime"].dt.date <= end_date) &
    (air_quality_df["station"].isin(selected_stations))
]

if main_df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

station_pm25_df = create_station_pm25_df(main_df)
wind_pm25_df = create_wind_pm25_df(main_df)

# Overview
st.subheader("Overview")

col1, col2, col3 = st.columns(3)

with col1:
    avg_pm25 = main_df["PM2.5"].mean()
    st.metric(
        label="Rata-rata PM2.5",
        value=f"{avg_pm25:.2f}"
    )

with col2:
    max_pm25 = main_df["PM2.5"].max()
    st.metric(
        label="PM2.5 Maksimum",
        value=f"{max_pm25:.2f}"
    )

with col3:
    avg_wspm = main_df["WSPM"].mean()
    st.metric(
        label="Rata-rata Kecepatan Angin",
        value=f"{avg_wspm:.2f} m/s"
    )

st.subheader("Rata-rata PM2.5 Berdasarkan Stasiun")

station_plot = station_pm25_df.sort_values(
    by="PM2.5",
    ascending=True
)

fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(
    data=station_plot,
    x="PM2.5",
    y="station",
    ax=ax
)

for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=3)

ax.set_xlabel("Rata-rata PM2.5")
ax.set_ylabel("Stasiun")
ax.set_title("Rata-rata Konsentrasi PM2.5 pada Stasiun Terpilih")

st.pyplot(fig)

st.subheader("Rata-rata PM2.5 Berdasarkan Kecepatan Angin")

fig, ax = plt.subplots(figsize=(8, 5))

sns.barplot(
    data=wind_pm25_df,
    x="wind_speed_category",
    y="PM2.5",
    order=["Rendah", "Sedang", "Tinggi"],
    ax=ax
)

for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", padding=3)

ax.set_xlabel("Kategori Kecepatan Angin")
ax.set_ylabel("Rata-rata PM2.5")
ax.set_title("Konsentrasi PM2.5 Berdasarkan Kecepatan Angin")

st.pyplot(fig)

st.subheader("Insight")

if not station_pm25_df.empty:
    highest_station = station_pm25_df.iloc[0]

    st.write(
        f"Pada periode dan stasiun yang dipilih, **{highest_station['station']}** "
        f"memiliki rata-rata PM2.5 tertinggi sebesar "
        f"**{highest_station['PM2.5']:.2f}**."
    )

if not wind_pm25_df.empty:
    highest_wind_category = wind_pm25_df.loc[
        wind_pm25_df["PM2.5"].idxmax()
    ]

    st.write(
        f"Kategori kecepatan angin **{highest_wind_category['wind_speed_category']}** "
        f"memiliki rata-rata PM2.5 tertinggi sebesar "
        f"**{highest_wind_category['PM2.5']:.2f}**."
    )

st.caption(
    "Catatan: hubungan antara kecepatan angin dan PM2.5 menunjukkan asosiasi "
    "dalam data dan tidak membuktikan hubungan sebab-akibat."
)

st.caption("Air Quality Analysis Dashboard")