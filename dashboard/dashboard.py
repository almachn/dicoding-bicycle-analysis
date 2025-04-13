import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Load data harian
all_data = pd.read_csv('https://raw.githubusercontent.com/almachn/dicoding-bycicle-analisist/refs/heads/main/dashboard/main_data.csv')


# Convert date columns to datetime
datetime_columns = ['date']
all_data.sort_values(by='date', inplace=True)
all_data.reset_index(inplace=True)

for column in datetime_columns:
    all_data[column] = pd.to_datetime(all_data[column])

def create_month_recap(df):
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    if 'cnt' not in df.columns:
        df['cnt'] = df['registered'] + df['casual']

    df['year_month'] = df['month'].astype(str).str.zfill(2) + ' ' + df['year'].astype(str)
    df['total_sum'] = df.groupby('year_month')['cnt'].transform('sum')

    return df[['year_month', 'total_sum']].drop_duplicates().reset_index(drop=True)


def create_season_recap(df):
    return df.groupby('season')[['registered', 'casual']].sum().reset_index()

def create_weather_recap(df):
    return df.groupby('weather')[['registered', 'casual']].sum().reset_index()

def create_workingday_recap(df):
    return df.groupby('workingday')[['registered', 'casual']].sum().reset_index()

def create_rfm_recap(df):
    rfm_df = all_data.groupby(by="hour", as_index=False).agg({
    "date": "max",
    "instant": "nunique",
    "cnt": "sum"
    })

    rfm_df.columns = ["hour", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = all_data["date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

def create_daily_recap(df):
    return df.groupby('date').agg({'cnt': 'sum'}).reset_index()

def get_total_registered(df):
    return df['registered'].sum()

def get_total_casual(df):
    return df['casual'].sum()

def get_avg_temp(df):
    return df['temp'].mean()

def get_avg_hum(df):
    return df['hum'].mean()

# membuat komponen filter
min_date = all_data["date"].dt.date.min()
max_date = all_data["date"].dt.date.max()

with st.sidebar:
    st.image('https://raw.githubusercontent.com/almachn/dicoding-bycicle-analisist/main/dashboard/icon.png')

    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date,max_date]
    )
    if st.checkbox("Display Dataset"):
        st.subheader("Dataset")
        st.write(all_data)

st.sidebar.title('Created By:')
st.sidebar.write('**Alma Choerunisa**')
st.sidebar.write('Email: MC367D50927@student.devacademy.id')

main_df = all_data[(all_data["date"] >= str(start_date)) & (all_data["date"] <= str(end_date))]

month_recap_df = create_month_recap(main_df)
season_recap_df = create_season_recap(main_df)
weather_recap_df = create_weather_recap(main_df)
workingday_recap_df = create_workingday_recap(main_df)
rfm_recap_df = create_rfm_recap(main_df)
daily_recap_df = create_daily_recap(main_df)
# Total dan rata-rata dari data terfilter
total_registered = get_total_registered(main_df)
total_casual = get_total_casual(main_df)
avg_temp = get_avg_temp(main_df)
avg_hum = get_avg_hum(main_df)

st.header('ANALISIS PENYEWAAN SEPEDA')
st.subheader ("Rangkuman Dashboard")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    daily_recap = daily_recap_df['cnt'].sum()
    st.metric(label="Jumlah Penyewaan", value=daily_recap)

with col2:
    st.metric("Total Registered Users", total_registered)

with col3:
    st.metric("Total Casual Users", total_casual)

with col4:
    st.metric("Average Temperature (°C)", round(avg_temp, 2))

with col5:
    st.metric("Average Humidity", f"{round(avg_hum * 100, 1)}%")

# Subheader Monthly Recap
st.subheader('📅 Monthly Rent Recap')
fig, ax = plt.subplots(figsize=(16, 8))
colors = sns.color_palette("husl", len(month_recap_df['year_month']))
ax.bar(
    month_recap_df['year_month'],
    month_recap_df['total_sum'],
    color=colors
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15, rotation=45)
ax.set_title('Monthly Rent Recap', fontsize=25)
ax.set_xlabel('Year Month', fontsize=20)
ax.set_ylabel('Total Sum', fontsize=20)

st.pyplot(fig)

# Subheader Season and Weather Recap
st.subheader('🌤️ Season and Weather Recap')
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=season_recap_df,
        x='season',
        y='registered',
        color='skyblue',
        label='Registered',
        ax=ax
    )
    sns.barplot(
        data=season_recap_df,
        x='season',
        y='casual',
        color='lightcoral',
        label='Casual',
        ax=ax
    )
    ax.set_title('Total Rentals by Season', fontsize=18)
    ax.set_xlabel('Season', fontsize=14)
    ax.set_ylabel('Total Rentals', fontsize=14)
    ax.legend()
    st.pyplot(fig)

with col2:
    weather_recap_df['total'] = weather_recap_df['registered'] + weather_recap_df['casual']
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=weather_recap_df,
        x='weather',
        y='total',
        palette='viridis',
        ax=ax
    )
    ax.set_title('Total Rentals by Weather', fontsize=18)
    ax.set_xlabel('Weather', fontsize=14)
    ax.set_ylabel('Total Rentals', fontsize=14)
    st.pyplot(fig)

# Subheader RFM Recap
st.subheader('⏱ RFM Recap')
col1, col2, col3 = st.columns(3)

top_recency = rfm_recap_df.sort_values(by="recency").head(5)
top_frequency = rfm_recap_df.sort_values(by="frequency", ascending=False).head(5)
top_monetary = rfm_recap_df.sort_values(by="monetary", ascending=False).head(5)

fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(10, 24))

sns.barplot(data=top_recency, x="hour", y="recency", palette='Blues_d', ax=ax[0])
ax[0].set_title("Top 5 Hours by Recency")
ax[0].set_xlabel("Hour")
ax[0].set_ylabel("Recency")

sns.barplot(data=top_frequency, x="hour", y="frequency", palette='Greens_d', ax=ax[1])
ax[1].set_title("Top 5 Hours by Frequency")
ax[1].set_xlabel("Hour")
ax[1].set_ylabel("Frequency")

sns.barplot(data=top_monetary, x="hour", y="monetary", palette='Reds_d', ax=ax[2])
ax[2].set_title("Top 5 Hours by Monetary")
ax[2].set_xlabel("Hour")
ax[2].set_ylabel("Monetary")

plt.tight_layout()
st.pyplot(fig)
