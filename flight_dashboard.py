import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Flight Delay & Live Tracker", layout="wide")
st.title("✈️ Live Flight Tracker & Weather Delay Dashboard")

# Load Live Data from AviationStack API
@st.cache_data
def load_live_flight_data():
    API_KEY = "b34d51390a5d3c9b2fdcd5f662f10d27"
    url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&limit=50"
    response = requests.get(url)
    data = response.json()
    df = pd.json_normalize(data['data'])
    df['departure.scheduled'] = pd.to_datetime(df['departure.scheduled'])
    return df

# Load local weather delay CSV
@st.cache_data
def load_weather_data():
    df = pd.read_csv("flight_weather_data.csv")
    df['FlightDate'] = pd.to_datetime(df['FlightDate'])
    df['Month'] = df['FlightDate'].dt.month
    return df

# Sidebar
view_option = st.sidebar.radio("Choose View", ["📊 Weather Delay Analysis", "🌐 Live Flight Tracking"])

# View 1: Weather-Based Delay Analysis
if view_option == "📊 Weather Delay Analysis":
    df = load_weather_data()
    weather_df = df[df['DelayReason'] == 'Weather']

    st.sidebar.header("🔍 Filter")
    airlines = st.sidebar.multiselect("Airlines", weather_df['Airline'].unique(), default=weather_df['Airline'].unique())
    months = st.sidebar.multiselect("Months", weather_df['Month'].unique(), default=weather_df['Month'].unique())

    filtered_df = weather_df[
        (weather_df['Airline'].isin(airlines)) &
        (weather_df['Month'].isin(months))
    ]

    st.subheader("📋 Filtered Data")
    st.dataframe(filtered_df)

    st.subheader("📊 Weather Delays by Airline")
    st.bar_chart(filtered_df['Airline'].value_counts())

    st.subheader("📈 Monthly Weather Delay Trend")
    st.line_chart(filtered_df['Month'].value_counts().sort_index())

    st.subheader("⏱️ Avg Departure Delay (min)")
    avg_dep = filtered_df.groupby('Airline')['DepartureDelay'].mean()
    st.bar_chart(avg_dep)

    st.subheader("🌍 Delay Count by Origin Airport")
    top_airports = filtered_df['OriginAirport'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_airports.values, y=top_airports.index, ax=ax)
    ax.set_xlabel("Delays")
    ax.set_ylabel("Airport")
    st.pyplot(fig)

    # Download option
    st.download_button("📥 Download CSV", data=filtered_df.to_csv(index=False).encode('utf-8'), file_name="weather_delays.csv", mime="text/csv")

# View 2: Live Flight Tracker
elif view_option == "🌐 Live Flight Tracking":
    live_df = load_live_flight_data()

    st.sidebar.header("🔎 Track Specific Flight")
    flight_numbers = live_df['flight.number'].dropna().unique()
    selected_flight = st.sidebar.selectbox("Choose Flight Number", flight_numbers)

    st.subheader("📋 Live Flight Data (Top 50 Flights)")
    st.dataframe(live_df[['airline.name', 'flight.number', 'departure.iata', 'arrival.iata', 'departure.scheduled', 'flight_status']])

    st.subheader("📊 Flight Status Overview")
    status_counts = live_df['flight_status'].value_counts()
    st.bar_chart(status_counts)

    st.subheader("📍 Top 10 Departure Airports")
    top_dep = live_df['departure.iata'].value_counts().head(10)
    fig2, ax2 = plt.subplots()
    sns.barplot(x=top_dep.values, y=top_dep.index, ax=ax2)
    ax2.set_xlabel("Departures")
    ax2.set_ylabel("Airport")
    st.pyplot(fig2)

    flight_info = live_df[live_df['flight.number'] == selected_flight]
    if not flight_info.empty:
        st.subheader(f"📍 Live Status for Flight {selected_flight}")
        st.write(flight_info[['airline.name', 'flight.number', 'departure.iata', 'arrival.iata',
                              'departure.scheduled', 'arrival.scheduled',
                              'departure.estimated', 'arrival.estimated', 'flight_status']])
    else:
        st.warning("No data found for this flight.")
