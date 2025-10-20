import streamlit as st
import plotly.express as px
import pandas as pd

st.markdown("""
    <style>
    html {
        font-size: 20px !important;
    }
    
    [data-testid="stDataFrame"] {
        zoom: 1.4;
    }
    
    iframe[title="streamlit_dataframe.st_dataframe"] {
        zoom: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

#Load Data
@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv("weather_data_cleaned.csv")
    df['Temp_Numeric'] = pd.to_numeric(df['Temp_Numeric'], errors='coerce')
    df['Temp_Celsius'] = (df['Temp_Numeric'] - 32) * 5/9

    df['Country'] = df['Country'].str.replace('-', ' ').str.title()

    df['Country'] = df['Country'].replace({
        'Usa': 'USA',
        'Uk': 'UK',
        'Uae': 'UAE'
    })

    return df

df = load_data()

 #Title@introduction
st.title("Global Weather Dashboard")
st.markdown(f"Real-time weather data from **{len(df)} cities** worldwide")
st.divider()

#Sidebar filters
st.sidebar.header("Filters")

all_conditions = df['Condition_Normalized'].unique().tolist()
conditions = st.sidebar.multiselect(
    "Select weather conditions:",
    options=all_conditions,
    default=all_conditions
)

categories = ['All'] + df['Temp_Category'].unique().tolist()
category_filter = st.sidebar.selectbox("Temperature category:", categories)

temp_unit = st.sidebar.radio("Temperature unit:", ['Celsius (°C)', 'Fahrenheit (°F)'])

#filtering data
filtered = df[df['Condition_Normalized'].isin(conditions)]
if category_filter != 'All':
    filtered = filtered[filtered['Temp_Category'] == category_filter]


temp_col = 'Temp_Celsius' if 'Celsius' in temp_unit else 'Temp_Numeric'
unit = '°C' if 'Celsius' in temp_unit else '°F'

#Metric overview
st.markdown("Weather Overview")
st.markdown("A quick summary of the selected cities and their temperature statistics.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Cities", len(filtered))

with col2:
    st.metric("Average Temperature", f"{filtered[temp_col].mean():.1f}{unit}")

with col3:
    st.metric("Hottest", f"{filtered[temp_col].max():.1f}{unit}")

with col4:
    st.metric("Coldest", f"{filtered[temp_col].min():.1f}{unit}")

st.divider()

#Temperature distribution
 #Bar Chart
st.subheader(f"Top Cities by Temperature")
city_count = min(10, len(filtered))
top_cities = filtered.nlargest(city_count, temp_col)
fig1 = px.bar(top_cities, x='City', y=temp_col, color='Temp_Category',
              title=f'Top {city_count} Cities by Temperature',
              labels={temp_col: f'Temperature ({unit})'},
              color_discrete_map={
                  'Freezing': '#003366',
                  'Cold': '#0066CC',
                  'Cool': '#66B2FF',
                  'Warm': '#FFC107',
                  'Hot': '#E53935'
              })
fig1.update_layout(xaxis_tickangle=-45, height=500,font=dict(size=18),title_font=dict(size=22), margin=dict(l=60, r=30, t=60, b=80))
st.plotly_chart(fig1, use_container_width=True)

#Category @ condition
col1, col2 = st.columns(2)

#Pie Chart
with col1:
    st.subheader("Temperature Categories")
    st.markdown("Proportion of cities by temperature range.")
    category_counts = filtered['Temp_Category'].value_counts()
    fig2 = px.pie(values=category_counts.values, names=category_counts.index,
                  color=category_counts.index,
                  color_discrete_map={
                      'Freezing': '#003366',
                      'Cold': '#0066CC',
                      'Cool': '#66B2FF',
                      'Warm': '#FFC107',
                      'Hot': '#E53935'
                  })
    fig2.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(size=16, color='black'),)
    st.plotly_chart(fig2, use_container_width=True)

#Box Plot
with col2:
    st.subheader("Weather Conditions")
    st.markdown("Count of cities for each weather type (sunny, cloudy, etc.)")
    condition_counts = filtered['Condition_Normalized'].value_counts().head(10).reset_index()

    condition_counts.columns = ['Condition', 'Count']

    fig3 = px.bar(
        condition_counts,
        x='Condition',
        y='Count',
        labels={'Condition': 'Condition', 'Count': 'Number of Cities'},
        title='Number of Cities by Weather Condition'
    )

    fig3.update_layout(
        title={
            'text': 'Weather Conditions',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False,
        width=1000,
        height=500,
        font=dict(size=18),
        title_font=dict(size=24, color='black', family='Arial Black'),
        margin=dict(l=60, r=30, t=60, b=120),
        bargap=0.3
    )

    fig3.update_xaxes(
        tickangle=-45,
        tickfont=dict(size=14, color='gray'),
        title_font=dict(size=20, color='black', family='Arial Black')
    )

    fig3.update_yaxes(
        tickfont=dict(size=14),
        title_font=dict(size=16)
    )

    fig3.update_traces(
        width=0.8,
        marker_color='steelblue'
    )

    st.plotly_chart(fig3, use_container_width=True)

#Raw data table
st.subheader("Raw Data")
st.markdown("View the detailed table of cities that match your filter selections.")
show_data = st.checkbox("Show data table")
if show_data:
    st.dataframe(
        filtered[['City', 'Temp_Raw', 'Temp_Category', 'Condition_Normalized', 'Country']],
        use_container_width=True,
        height=400
    )



