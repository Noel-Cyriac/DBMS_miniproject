import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit_folium import folium_static

# Function to insert data into the temporary table
def insert_data(data_list, table_name):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password312',
        database='crime_data'
    )
    cursor = conn.cursor()

    insert_query = f'''
        INSERT INTO {table_name} (latitude, longitude, location_name, district, crime_date, crime_type, time_of_crime)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.executemany(insert_query, data_list)

    conn.commit()
    conn.close()

# Function to fetch filtered data from new_crime_data
def fetch_filtered_data(location_filter, crime_type_filter):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password312',
        database='crime_data'
    )
    cursor = conn.cursor()

    query = 'SELECT * FROM new_crime_data WHERE 1=1'
    params = []

    if location_filter:
        query += f" AND location_name = '{location_filter}'"

    if crime_type_filter:
        query += f" AND crime_type = '{crime_type_filter}'"

    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

# Streamlit app
def app():
    # Connection to MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password312',
        database='crime_data'
    )

    st.title("Crime Mapping Analytics")

    location_filter = st.text_input("Filter by Location:")
    crime_type_filter = st.text_input("Filter by Crime Type:")

    st.subheader("Filtered Crime Data")
    filtered_data = fetch_filtered_data(location_filter, crime_type_filter)
    df_filtered = pd.DataFrame(filtered_data, columns=['id', 'location_name', 'district', 'crime_date', 'crime_type', 'time_of_crime', 'latitude', 'longitude'])
    df_filtered = df_filtered[['id', 'location_name', 'district', 'crime_date', 'crime_type', 'time_of_crime', 'latitude', 'longitude']]
    df_filtered['latitude'] = pd.to_numeric(df_filtered['latitude'], errors='coerce')
    df_filtered['longitude'] = pd.to_numeric(df_filtered['longitude'], errors='coerce')
    df_filtered['time_of_crime'] = pd.to_timedelta(df_filtered['time_of_crime']).dt.total_seconds().apply(lambda x: pd.to_datetime(x, unit='s').time())
    st.write(df_filtered)

    # Display visualizations
    m_point = folium.Map(location=[df_filtered['latitude'].mean(), df_filtered['longitude'].mean()], zoom_start=7)
    markers = MarkerCluster().add_to(m_point)

    for index, point in df_filtered.iterrows():
        folium.Marker([point['latitude'], point['longitude']], popup=point['location_name']).add_to(markers)

    m_heatmap = folium.Map(location=[df_filtered['latitude'].mean(), df_filtered['longitude'].mean()], zoom_start=7)
    heat_data = [[point['latitude'], point['longitude']] for index, point in df_filtered.iterrows()]
    HeatMap(heat_data).add_to(m_heatmap)

    st.subheader("Point Map")
    folium_static(m_point)

    st.subheader("Heatmap")
    folium_static(m_heatmap)

    # Display additional visualizations below heatmap
    st.markdown("<h2 style='text-align: left; color: black; margin-bottom: 20px;'>Number of Crimes by District</h2>", unsafe_allow_html=True)
    # Fetch district data
    query_district = "SELECT district FROM new_crime_data"
    district_data = pd.read_sql(query_district, connection)
    district_counts = district_data['district'].value_counts()

    # Bar chart for the number of crimes by district
    fig_district_counts, ax_district_counts = plt.subplots()
    ax_district_counts.bar(district_counts.index, district_counts)
    ax_district_counts.set_xticklabels(ax_district_counts.get_xticklabels(), rotation=45, horizontalalignment='right')
    st.pyplot(fig_district_counts)
    st.text("This bar chart displays the number of crimes in each district.")

    # Circular plot (pie chart) with a 45-degree start angle
    st.markdown("<h2 style='text-align: left; color: black; margin-top: 50px; margin-bottom: 20px;'>Circular Plot</h2>", unsafe_allow_html=True)
    fig_pie_chart, ax_pie_chart = plt.subplots()
    ax_pie_chart.pie(district_counts, labels=district_counts.index, autopct='%1.1f%%', startangle=45, counterclock=False)
    ax_pie_chart.axis('equal')
    st.pyplot(fig_pie_chart)
    st.text("This pie chart shows the distribution of crimes across districts.")

    # Treemap for crime types
    st.markdown("<h2 style='text-align: left; color: black; margin-top: 50px; margin-bottom: 20px;'>Crime Type Treemap</h2>", unsafe_allow_html=True)
    query_crime_type = "SELECT crime_type FROM new_crime_data"
    crime_type_data = pd.read_sql(query_crime_type, connection)
    fig_treemap = px.treemap(crime_type_data, path=['crime_type'], title='Crime Type Treemap')
    st.plotly_chart(fig_treemap)
    st.text("This treemap visualizes the distribution of crime types.")

    # Line graph for crime types over years
    st.markdown("<h2 style='text-align: left; color: black; margin-top: 50px; margin-bottom: 20px;'>Crime Type Line Graph Over Years</h2>", unsafe_allow_html=True)
    query_line_graph = "SELECT crime_date, crime_type FROM new_crime_data"
    line_graph_data = pd.read_sql(query_line_graph, connection)
    line_graph_data['year'] = pd.to_datetime(line_graph_data['crime_date']).dt.year
    line_graph_counts = line_graph_data.groupby(['year', 'crime_type']).size().reset_index(name='count')
    fig_line_graph, ax_line_graph = plt.subplots(figsize=(12, 8))
    sns.lineplot(data=line_graph_counts, x='year', y='count', hue='crime_type', palette='viridis', ax=ax_line_graph)
    ax_line_graph.set_xlabel('Year')
    ax_line_graph.set_ylabel('Count')
    ax_line_graph.set_title('Crime Type Line Graph Over Years')
    st.pyplot(fig_line_graph)
    st.text("This line graph shows the count of each crime type over the years.")

    # Line graph for overall crimes per year
    st.markdown("<h2 style='text-align: left; color: black; margin-top: 50px; margin-bottom: 20px;'>Count of All Crimes Per Year</h2>", unsafe_allow_html=True)
    all_crimes_per_year = line_graph_data.groupby('year').size().reset_index(name='count')
    fig_all_crimes, ax_all_crimes = plt.subplots(figsize=(12, 8))
    sns.lineplot(data=all_crimes_per_year, x='year', y='count', marker='o', color='b', ax=ax_all_crimes)
    ax_all_crimes.set_xlabel('Year')
    ax_all_crimes.set_ylabel('Count')
    ax_all_crimes.set_title('Count of All Crimes Per Year')
    st.pyplot(fig_all_crimes)
    st.text("This line graph shows the overall count of crimes per year.")

    # Add New Crime Data section
    st.subheader("Add New Crime Data")
    new_data = st.text_area("Enter data (latitude, longitude, location name, district, crime date, crime type, time of crime):")

    if st.button("Request Addition"):
        data_list = [tuple(entry.strip().split(',')) for entry in new_data.split('\n') if entry.strip()]
        insert_data(data_list, 'temporary')
        st.success("Crime Data addition requested")

    # Close the database connection
    connection.close()

# Streamlit app entry point
if __name__ == "__main__":
    st.set_page_config(page_title="User_Page")
    app()
