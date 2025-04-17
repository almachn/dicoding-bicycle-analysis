import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='whitegrid')

# Load data 
all_data = pd.read_csv("https://raw.githubusercontent.com/almachn/dicoding-bycicle-analisist/main/dashboard/main_data.csv")
all_data['date'] = pd.to_datetime(all_data['date'])

# Komponen sidebar
min_date = all_data["date"].dt.date.min()
max_date = all_data["date"].dt.date.max()

with st.sidebar:
    st.image('https://raw.githubusercontent.com/almachn/dicoding-bycicle-analisist/main/dashboard/icon.png')
    start_date, end_date = st.date_input("Rentang Waktu", min_value=min_date, max_value=max_date, value=[min_date, max_date])
    if st.checkbox("Display Dataset"):
        st.subheader("Dataset")
        st.write(all_data)

st.sidebar.title('Created By:')
st.sidebar.write('**Alma Choerunisa**')
st.sidebar.write('Email: MC367D50927@student.devacademy.id')

# Filter data sesuai tanggal
main_df = all_data[(all_data['date'] >= str(start_date)) & (all_data['date'] <= str(end_date))]

# Hitung total dan rata-rata
total_registered = main_df['registered'].sum()
total_casual = main_df['casual'].sum()
avg_temp = main_df['temp'].mean() * 41  # Convert normalized temp to Celsius
avg_hum = main_df['hum'].mean()

st.title('📊 Bike Sharing Dashboard')

# Ringkasan metrik
st.subheader("*Insight:*")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Peminjaman", main_df['cnt'].sum())
col2.metric("Registered Users", total_registered)
col3.metric("Casual Users", total_casual)
col4.metric("Avg Temperature (°C)", round(avg_temp, 2))
col5.metric("Avg Humidity", f"{round(avg_hum * 100, 1)}%")

# Pertanyaan 1: Perbandingan Hari Kerja vs Libur
st.subheader("Penggunaan Sepeda: Working Day vs Weekend/Holiday")
main_df['day_type'] = main_df['workingday'].apply(lambda x: 'Working Day' if x == 'Working Day' else 'Weekend/Holiday')
day_type_stats = main_df.groupby('day_type').agg(total_sum=('cnt', 'sum'), total_mean=('cnt', 'mean')).reset_index()

fig, ax = plt.subplots(figsize=(7,5))
sns.barplot(data=day_type_stats, x='day_type', y='total_mean', palette='pastel', ax=ax)
ax.set_title("Rata-rata Peminjaman per Hari")
ax.set_ylabel("Rata-rata Jumlah Peminjaman")
st.pyplot(fig)

# Pertanyaan 2: Jam Puncak
st.subheader("Jam Puncak Penggunaan Sepeda")
hourly_usage = main_df.groupby(['hour', 'day_type'])['cnt'].mean().reset_index()

fig, ax = plt.subplots(figsize=(12,6))
sns.lineplot(data=hourly_usage, x='hour', y='cnt', hue='day_type', marker='o', ax=ax)
ax.set_title("Rata-rata Penggunaan Sepeda per Jam")
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Jumlah Peminjam")
ax.grid(True)
st.pyplot(fig)

# Pertanyaan 3: Distribusi Jam
st.subheader("Distribusi Penggunaan Sepeda per Jam")
fig, ax = plt.subplots(figsize=(12,6))
sns.boxplot(data=main_df, x='hour', y='cnt', hue='day_type', ax=ax)
ax.set_title('Distribusi Penggunaan Sepeda per Jam (Working Day vs Weekend/Holiday)')
ax.set_xlabel('Jam')
ax.set_ylabel('Jumlah Peminjam')
ax.grid(True)
st.pyplot(fig)

# Visual tambahan: Barplot per jam
st.subheader("Perbandingan Jam per Tipe Hari")
fig, ax = plt.subplots(figsize=(14,6))
sns.barplot(data=hourly_usage, x='hour', y='cnt', hue='day_type', palette='Set2', ax=ax)
ax.set_title("Rata-rata Penggunaan Sepeda per Jam (Grouped Bar)")
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Jumlah Peminjam")
ax.grid(True, axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig)

# Analisis Lanjutan: RFM-like
st.subheader("RFM-style Analysis (per Hari)")
rfm_df = main_df.groupby('date')['cnt'].sum().reset_index()
rfm_df['recency'] = (main_df['date'].max() - rfm_df['date']).dt.days
rfm_df['frequency'] = rfm_df['cnt']
rfm_df['monetary'] = rfm_df['cnt']

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
sns.boxplot(y=rfm_df['recency'], ax=axes[0], color='skyblue')
axes[0].set_title('Distribusi Recency')
sns.boxplot(y=rfm_df['frequency'], ax=axes[1], color='lightgreen')
axes[1].set_title('Distribusi Frequency')
sns.boxplot(y=rfm_df['monetary'], ax=axes[2], color='salmon')
axes[2].set_title('Distribusi Monetary')
plt.tight_layout()
st.pyplot(fig)
