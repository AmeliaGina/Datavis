# import streamlit as st
# import pandas as pd
# import plotly.express as px

# # ====== Load & Prepare Data ======
# @st.cache_data
# def load_data():
#     df = pd.read_excel("hazard_report_darimf.xlsx")
#     df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
#     df['Month'] = df['Date'].dt.to_period('M').astype(str)
#     return df.dropna(subset=['Date'])

# df = load_data()

# # ====== Sidebar Filters ======
# st.sidebar.header("🔍 Filter Global")
# date_range = st.sidebar.date_input("Periode", [df["Date"].min(), df["Date"].max()])
# lokasi = st.sidebar.multiselect("Lokasi / Site", options=df["Location"].dropna().unique())
# dept = st.sidebar.selectbox("Department", options=["All"] + list(df["Department"].dropna().unique()))
# risk_rank = st.sidebar.slider("Risk Rank", min_value=1, max_value=25, value=(1, 25))
# status_filter = st.sidebar.multiselect("Status", options=df["Status"].dropna().unique())

# # Apply filters
# filtered = df[
#     (df["Date"] >= pd.to_datetime(date_range[0])) &
#     (df["Date"] <= pd.to_datetime(date_range[1]))
# ]

# if lokasi:
#     filtered = filtered[filtered["Location"].isin(lokasi)]

# if dept != "All":
#     filtered = filtered[filtered["Department"] == dept]

# filtered = filtered[
#     (filtered["Est Risk Rank"].fillna(0) >= risk_rank[0]) &
#     (filtered["Est Risk Rank"].fillna(0) <= risk_rank[1])
# ]

# if status_filter:
#     filtered = filtered[filtered["Status"].isin(status_filter)]

# # ====== 1. Executive Summary Cards ======
# st.title("📋 Hazard Report Dashboard")

# col1, col2, col3, col4, col5 = st.columns(5)

# col1.metric("Total Laporan", len(filtered))
# complete_pct = filtered["Status"].value_counts(normalize=True).get("Complete", 0) * 100
# col2.metric("% Complete", f"{complete_pct:.0f}%")

# if "Corrective Finding/Date" in filtered.columns and "Corrective Finding/Status" in filtered.columns:
#     closed = filtered[filtered["Status"] == "Complete"]
#     if not closed.empty:
#         closed["days_to_close"] = (closed["Corrective Finding/Date"] - closed["Date"]).dt.days
#         col3.metric("Avg Time to Close (hari)", f"{closed['days_to_close'].mean():.1f}")
#     else:
#         col3.metric("Avg Time to Close (hari)", "N/A")
# else:
#     col3.metric("Avg Time to Close", "N/A")

# rr4_5 = filtered[(filtered["Est Risk Rank"] >= 4) & (filtered["Status"] != "Complete")]
# col4.metric("Risk 4–5 Belum Selesai", len(rr4_5))

# unsafe_pct = filtered["Risk Category"].value_counts(normalize=True).get("Unsafe Action", 0) * 100
# col5.metric("Unsafe Action %", f"{unsafe_pct:.0f}%")

# # ====== 2. Tren per Bulan ======
# st.subheader("📈 Tren Laporan Hazard per Bulan")
# trend = filtered.groupby("Month").size().reset_index(name="Jumlah")
# fig = px.bar(trend, x="Month", y="Jumlah", title="Jumlah Laporan per Bulan")
# st.plotly_chart(fig, use_container_width=True)

# # ====== 3. Risiko per Lokasi ======
# st.subheader("🧭 Lokasi Risiko Tertinggi")
# loc_count = filtered.groupby("Location").agg({
#     "Est Risk Rank": "max",
#     "Date": "count"
# }).rename(columns={"Date": "Jumlah"}).sort_values(by="Jumlah", ascending=False).head(10)

# fig = px.treemap(loc_count.reset_index(), path=["Location"], values="Jumlah", color="Est Risk Rank",
#                  color_continuous_scale="Reds", title="Peta Risiko (Top 10 Lokasi)")
# st.plotly_chart(fig, use_container_width=True)

# # ====== 4. Hazard Type & Status ======
# st.subheader("⚠️ Kategori & Status Hazard Report")
# colA, colB = st.columns(2)
# with colA:
#     fig = px.pie(filtered, names="Risk Category", title="Jenis Hazard (Type)")
#     st.plotly_chart(fig, use_container_width=True)
# with colB:
#     fig = px.pie(filtered, names="Status", title="Status Laporan")
#     st.plotly_chart(fig, use_container_width=True)

# # ====== 5. Corrective Action Analysis ======
# st.subheader("🛠️ Analisis Tindakan Korektif")
# if "Corrective Finding/Status" in filtered.columns:
#     ca_status = filtered["Corrective Finding/Status"].value_counts().reset_index()
#     ca_status.columns = ["Status", "Jumlah"]
#     fig = px.bar(ca_status, x="Status", y="Jumlah", color="Status", title="Status Corrective Action")
#     st.plotly_chart(fig, use_container_width=True)

# # ====== 6. Departemen Paling Aktif ======
# st.subheader("📊 Aktivitas per Departemen")
# dept_counts = filtered["Department"].value_counts().reset_index()
# dept_counts.columns = ["Department", "Jumlah"]
# fig = px.bar(dept_counts, x="Department", y="Jumlah", title="Jumlah Laporan per Departemen")
# st.plotly_chart(fig, use_container_width=True)

# # ====== 7. Tabel Prioritas / Insight ======
# st.subheader("📌 Prioritas Minggu Ini")
# risk5 = filtered[
#     (filtered["Est Risk Rank"] == 5) &
#     (filtered["Status"] != "Complete") &
#     ((pd.Timestamp.today() - filtered["Date"]).dt.days > 14)
# ]
# st.write(f"🔔 {len(risk5)} hazard Risk Rank 5 belum selesai > 14 hari")

# unsafe_by_dept = filtered[filtered["Risk Category"] == "Unsafe Action"]["Department"].value_counts(normalize=True) * 100
# if not unsafe_by_dept.empty:
#     top_dept = unsafe_by_dept.idxmax()
#     st.write(f"🚨 {top_dept} menyumbang {unsafe_by_dept.max():.1f}% unsafe action")

# top_loc = filtered["Location"].value_counts().head(1)
# if not top_loc.empty:
#     st.write(f"📍 Lokasi {top_loc.index[0]} muncul {top_loc.values[0]} kali bulan ini")

# # ====== 8. Tabel Detail ======
# st.subheader("📁 Detail Laporan Hazard")
# st.dataframe(filtered[[
#     "Date", "Risk Category", "Reported By", "Est Risk Rank",
#     "Status", "Location", "Department"
# ]].sort_values(by="Date", ascending=False))

import streamlit as st
import pandas as pd
import plotly.express as px

# ======== Data Loading ========
@st.cache_data
def load_data():
    df = pd.read_excel("hazard_report_darimf.xlsx")
    # df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.normalize()
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    return df.dropna(subset=['Date'])

df = load_data()

# ======== Risk Level Mapping ========
def map_risk_level(value):
    if pd.isna(value):
        return "Tidak diketahui"
    elif value <= 5:
        return "Signifikan"
    elif value <= 12:
        return "Tinggi"
    elif value <= 17:
        return "Sedang"
    elif value <= 25:
        return "Rendah"
    else:
        return "Tidak diketahui"

df["Risk Level"] = df["Est Risk Rank"].apply(map_risk_level)

# ======== Sidebar Filter ========
st.sidebar.header("🔍 Filter Global")
date_range = st.sidebar.date_input("Periode", [df["Date"].min(), df["Date"].max()])
lokasi = st.sidebar.multiselect("Lokasi / Site", options=df["Location"].dropna().unique())
dept = st.sidebar.selectbox("Department", options=["All"] + list(df["Department"].dropna().unique()))
risk_range = st.sidebar.slider("Risk Rank", 1, 25, (1, 25))
status_filter = st.sidebar.multiselect("Status", options=df["Status"].dropna().unique())

# ======== Apply Filters ========
filtered = df[
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

if lokasi:
    filtered = filtered[filtered["Location"].isin(lokasi)]

if dept != "All":
    filtered = filtered[filtered["Department"] == dept]

filtered = filtered[
    (filtered["Est Risk Rank"].fillna(0) >= risk_range[0]) &
    (filtered["Est Risk Rank"].fillna(0) <= risk_range[1])
]

if status_filter:
    filtered = filtered[filtered["Status"].isin(status_filter)]

filtered["Risk Level"] = filtered["Est Risk Rank"].apply(map_risk_level)

# ======== Title ========
st.title("📋 Hazard Report Dashboard")

# ======== KPI Cards ========
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Laporan", len(filtered))

complete_pct = filtered["Status"].value_counts(normalize=True).get("Complete", 0) * 100
col2.metric("% Complete", f"{complete_pct:.0f}%")

if "Corrective Finding/Date" in filtered.columns:
    closed = filtered[filtered["Status"] == "Complete"]
    if not closed.empty:
        closed["days_to_close"] = (closed["Corrective Finding/Date"] - closed["Date"]).dt.days
        col3.metric("Avg Time to Close", f"{closed['days_to_close'].mean():.1f} hari")
    else:
        col3.metric("Avg Time to Close", "N/A")
else:
    col3.metric("Avg Time to Close", "N/A")

rr_critical = filtered[(filtered["Est Risk Rank"] <= 5) & (filtered["Status"] != "Complete")]
col4.metric("Risk 1-5 Belum Selesai", len(rr_critical))

# unsafe_pct = filtered["Risk Category"].value_counts(normalize=True).get("Unsafe Action", 0) * 100
# col5.metric("Unsafe Action %", f"{unsafe_pct:.0f}%")

# ======== Tren Bulanan ========
st.subheader("📈 Tren Laporan Hazard per Bulan")
trend = filtered.groupby("Month").size().reset_index(name="Jumlah")
fig = px.bar(trend, x="Month", y="Jumlah", title="Jumlah Laporan per Bulan")
st.plotly_chart(fig, use_container_width=True)

# ======== Risk Location Treemap ========
st.subheader("🧭 Lokasi Risiko Tertinggi")
loc_count = filtered.groupby("Location").agg({
    "Est Risk Rank": "max",
    "Date": "count"
}).rename(columns={"Date": "Jumlah"}).sort_values(by="Jumlah", ascending=False).head(10)

fig = px.treemap(loc_count.reset_index(), path=["Location"], values="Jumlah", color="Est Risk Rank",
                 color_continuous_scale="Reds", title="Peta Risiko (Top 10 Lokasi)")
st.plotly_chart(fig, use_container_width=True)

# ======== Hazard Type & Status Pie ========
st.subheader("⚠️ Distribusi Jenis Hazard & Status")
colA, colB = st.columns(2)
with colA:
    fig = px.pie(filtered, names="Risk Category", title="Jenis Hazard")
    st.plotly_chart(fig, use_container_width=True)
with colB:
    fig = px.pie(filtered, names="Status", title="Status Laporan")
    st.plotly_chart(fig, use_container_width=True)

# ======== Risk Level Distribution ========
st.subheader("🎨 Distribusi Estimasi Risk Level")
risk_level_counts = filtered["Risk Level"].value_counts().reset_index()
risk_level_counts.columns = ["Risk Level", "Jumlah"]
fig = px.bar(risk_level_counts, x="Risk Level", y="Jumlah", color="Risk Level",
             color_discrete_map={
                 "Signifikan": "red",
                 "Tinggi": "orange",
                 "Sedang": "yellow",
                 "Rendah": "green"
             },
             title="Jumlah Laporan berdasarkan Risk Level")
st.plotly_chart(fig, use_container_width=True)

# ======== Corrective Action ========
st.subheader("🛠️ Corrective Action Status")
if "Corrective Finding/Status" in filtered.columns:
    ca = filtered["Corrective Finding/Status"].value_counts().reset_index()
    ca.columns = ["Status", "Jumlah"]
    fig = px.bar(ca, x="Status", y="Jumlah", color="Status", title="Status Corrective Action")
    st.plotly_chart(fig, use_container_width=True)

# ======== Aktivitas Departemen ========
st.subheader("📊 Aktivitas per Departemen")
dept_count = filtered["Department"].value_counts().reset_index()
dept_count.columns = ["Department", "Jumlah"]
fig = px.bar(dept_count, x="Department", y="Jumlah", title="Jumlah Laporan per Departemen")
st.plotly_chart(fig, use_container_width=True)

# ======== Insight Mingguan ========
st.subheader("📌 Highlight Prioritas Minggu Ini")
risk5 = filtered[
    (filtered["Est Risk Rank"] == 5) &
    (filtered["Status"] != "Complete") &
    ((pd.Timestamp.today() - filtered["Date"]).dt.days > 14)
]
st.write(f"🔔 {len(risk5)} hazard Risk Rank 5 belum selesai > 14 hari")

unsafe_dept = filtered[filtered["Risk Category"] == "Unsafe Action"]["Department"].value_counts(normalize=True) * 100
if not unsafe_dept.empty:
    top_dept = unsafe_dept.idxmax()
    st.write(f"🚨 Departemen {top_dept} menyumbang {unsafe_dept.max():.1f}% unsafe action")

top_loc = filtered["Location"].value_counts().head(1)
if not top_loc.empty:
    st.write(f"📍 Lokasi {top_loc.index[0]} muncul {top_loc.values[0]} kali bulan ini")

# ======== Tabel Detail ========
st.subheader("📁 Tabel Detail Laporan")
st.dataframe(filtered[[
    "Date", "Risk Category", "Reported By", "Est Risk Rank", "Risk Level",
    "Status", "Location", "Department"
]].sort_values(by="Date", ascending=False))

