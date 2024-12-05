import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import mysql.connector
from mysql.connector import Error

st.set_page_config(
    page_title = "Data Collection",
    page_icon = '🗃️',
    layout = "wide",
    initial_sidebar_state = "expanded"
)

def fetch_data(table_name, vin, sequence_number, colour, type):
    db_config = {
        'host': 'localhost',    # dont change
        'user': 'root',         # change user
        'password': '',         # put password
        'database': 'data1'     # database name
    }
    try:
        db_conn = mysql.connector.connect(**db_config)
        if db_conn.is_connected():
            query = f"SELECT No, Date, Type, `Vin No.`, `Seq No.`, Colour, TIME, `Straight Bracket`, `No Washer`, Status FROM {table_name}"
            conditions = []
            params = []
            if type:
                conditions.append("Type = %s")
                params.append(type)
            if vin:
                conditions.append("`Vin No.` = %s")
                params.append(vin)
            if sequence_number:
                conditions.append("`Seq No.` = %s")
                params.append(sequence_number)
            if colour and colour != 'All':
                conditions.append("Colour = %s")
                params.append(colour)
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            cursor = db_conn.cursor()
            cursor.execute(query, params)
            df = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])
            cursor.close()
            db_conn.close()
            return df
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
        return pd.DataFrame()

with st.sidebar:
    # Sidebar for user inputs to query the database
    st.header("Data Parameters")
    st.subheader("Insert for Data Query")
    detections = ['All', 'Image', 'Bulk Image', 'Video', 'Capture', 'Live']
    selected_detection = st.selectbox('Detection Methods', detections)
    detection_type = {'All': None, 'Image': 'Image', 'Bulk Image': 'Bulk Image', 'Video': 'Video',
                      'Capture': 'Capture', 'Live': 'Live'}.get(selected_detection)
    type = st.text_input('Type')
    vehicle_identification_number = st.text_input('Vehicle Identification Number')
    sequence_number = st.text_input('Sequence Number')
    colour = ['All', 'Red', 'Blue', 'Silver', 'White', 'Black']
    selected_colour = st.selectbox('Vehicle Colour', colour)

st.title("Historical Data")
clm1, clm2 = st.columns([0.5,0.35])

with clm1:
    st.subheader("Bracket & Washer")
    st.image("images/demo4.jpg", width=350)

data={}

data_image = fetch_data("data_image", vehicle_identification_number, sequence_number, selected_colour, type)
data_bulk_image = fetch_data("data_bulk_image", vehicle_identification_number, sequence_number, selected_colour, type)
data_video = fetch_data("data_video", vehicle_identification_number, sequence_number, selected_colour, type)
data_capture = fetch_data("data_capture", vehicle_identification_number, sequence_number, selected_colour, type)
data_live = fetch_data("data_live", vehicle_identification_number, sequence_number, selected_colour, type)

if selected_detection == "All":
    # Create column 1 for data and column 2 for pie chart
    st.header("Image Detection Data")
    c1, c2 = st.columns([0.7,0.35])
    st.header("Bulk Image Detection Data")
    co1, co2 = st.columns([0.7,0.35])
    st.header("Video Detection Data")
    col1, col2 = st.columns([0.7,0.35])
    st.header("Capture Detection Data")
    colum1, colum2 = st.columns([0.7, 0.35])
    st.header("Live Detection Data")
    column1, column2 = st.columns([0.7,0.35])

    ##############################     Data Image Object Detection     ##############################
    with c1:
        st.subheader('Queried Data')
        if not data_image.empty:
            st.dataframe(data_image)
        else:
            st.write("No data available based on the input parameters.")

    # Pie chart section for 'Status' distribution
    with c2:
        if not data_image.empty and 'Status' in data_image.columns and 'Date' in data_image.columns:
            # Parse the date column to extract months
            data_image['Month'] = pd.to_datetime(data_image['Date']).dt.strftime('%Y-%m')
            # Aggregate the data to count statuses by month
            status_counts_by_month = data_image.groupby(['Month', 'Status']).size().unstack(fill_value=0)
            # Plot the data as a bar chart
            fig, ax = plt.subplots()
            status_counts_by_month.plot(kind='bar', ax=ax)
            ax.set_ylabel('Count')
            ax.set_xlabel('Month')
            ax.set_title('Status Distribution by Month')
            ax.legend(title='Status')
            # Set yaxis whole number
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            st.subheader('Status Distribution by Month')
            st.pyplot(fig)
        else:
            st.write("Data is empty or required columns are missing for the bar chart.")
    ##############################     (END) Data Image Object Detection (END)      ##############################

    ##############################     Data Bulk Image Object Detection     ##############################
    with co1:
        st.subheader('Queried Data')
        if not data_bulk_image.empty:
            st.dataframe(data_bulk_image)
        else:
            st.write("No data available based on the input parameters.")

    # Pie chart section for 'Status' distribution
    with co2:
        if not data_bulk_image.empty and 'Status' in data_bulk_image.columns and 'Date' in data_bulk_image.columns:
            # Parse the date column to extract months
            data_bulk_image['Month'] = pd.to_datetime(data_bulk_image['Date']).dt.strftime('%Y-%m')

            # Aggregate the data to count statuses by month
            status_counts_by_month = data_bulk_image.groupby(['Month', 'Status']).size().unstack(fill_value=0)

            # Plot the data as a bar chart
            fig, ax = plt.subplots()
            status_counts_by_month.plot(kind='bar', ax=ax)
            ax.set_ylabel('Count')
            ax.set_xlabel('Month')
            ax.set_title('Status Distribution by Month')
            ax.legend(title='Status')

            # Set yaxis whole number
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

            st.subheader('Status Distribution by Month')
            st.pyplot(fig)
        else:
            st.write("Data is empty or required columns are missing for the bar chart.")
    ##############################     (END) Data Bulk Image Object Detection (END)      ##############################

    ##############################     Data Video Object Detection     ##############################
    with col1:
        st.subheader('Queried Data')
        if not data_video.empty:
            st.dataframe(data_video)
        else:
            st.write("No data available based on the input parameters.")

    # Pie chart section for 'Status' distribution
    with col2:
        if not data_video.empty and 'Status' in data_video.columns and 'Date' in data_video.columns:
            # Parse the date column to extract months
            data_video['Month'] = pd.to_datetime(data_video['Date']).dt.strftime('%Y-%m')

            # Aggregate the data to count statuses by month
            status_counts_by_month = data_video.groupby(['Month', 'Status']).size().unstack(fill_value=0)

            # Plot the data as a bar chart
            fig, ax = plt.subplots()
            status_counts_by_month.plot(kind='bar', ax=ax)
            ax.set_ylabel('Count')
            ax.set_xlabel('Month')
            ax.set_title('Status Distribution by Month')
            ax.legend(title='Status')

            # Set yaxis whole number
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

            st.subheader('Status Distribution by Month')
            st.pyplot(fig)
        else:
            st.write("Data is empty or required columns are missing for the bar chart.")
    ##############################     (END) Data Video Object Detection (END)      ##############################

    ##############################     Data Capture Object Detection     ##############################
    with colum1:
        st.subheader('Queried Data')
        if not data_capture.empty:
            st.dataframe(data_capture)
        else:
            st.write("No data available based on the input parameters.")

    # Pie chart section for 'Status' distribution
    with colum2:
        if not data_capture.empty and 'Status' in data_capture.columns and 'Date' in data_capture.columns:
            # Parse the date column to extract months
            data_capture['Month'] = pd.to_datetime(data_capture['Date']).dt.strftime('%Y-%m')

            # Aggregate the data to count statuses by month
            status_counts_by_month = data_capture.groupby(['Month', 'Status']).size().unstack(fill_value=0)

            # Plot the data as a bar chart
            fig, ax = plt.subplots()
            status_counts_by_month.plot(kind='bar', ax=ax)
            ax.set_ylabel('Count')
            ax.set_xlabel('Month')
            ax.set_title('Status Distribution by Month')
            ax.legend(title='Status')

            # Set yaxis whole number
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

            st.subheader('Status Distribution by Month')
            st.pyplot(fig)
        else:
            st.write("Data is empty or required columns are missing for the bar chart.")
    ##############################     (END) Data Capture Object Detection (END)      ##############################

    ##############################     Live Object Detection     ##############################
    with column1:
        st.subheader('Queried Data')
        if not data_live.empty:
            st.dataframe(data_live)
        else:
            st.write("No data available based on the input parameters.")

    # Pie chart section for 'Status' distribution
    with column2:
        if not data_live.empty and 'Status' in data_live.columns and 'Date' in data_live.columns:
            # Parse the date column to extract months
            data_live['Month'] = pd.to_datetime(data_live['Date']).dt.strftime('%Y-%m')

            # Aggregate the data to count statuses by month
            status_counts_by_month = data_live.groupby(['Month', 'Status']).size().unstack(fill_value=0)

            # Plot the data as a bar chart
            fig, ax = plt.subplots()
            status_counts_by_month.plot(kind='bar', ax=ax)
            ax.set_ylabel('Count')
            ax.set_xlabel('Month')
            ax.set_title('Status Distribution by Month')
            ax.legend(title='Status')

            # Set yaxis whole number
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

            st.subheader('Status Distribution by Month')
            st.pyplot(fig)
        else:
            st.write("Data is empty or required columns are missing for the bar chart.")
    ##############################     (END) Live Object Detection (END)     ##############################

else:
    data[selected_detection] = fetch_data(f"data_{selected_detection.lower().replace(' ', '_')}",
                                          vehicle_identification_number, sequence_number, selected_colour, type)
    for detection, df in data.items():
        st.header(f"{detection} Detection Data")
        c1, c2 = st.columns([0.7, 0.35])

        with c1:
            st.subheader('Queried Data')
            if not df.empty:
                st.dataframe(df)
            else:
                st.write("No data available based on the input parameters.")

        with c2:
            if not df.empty and 'Status' in df.columns and 'Date' in df.columns:
                # Parse the date column to extract months
                df['Month'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m')

                # Aggregate the data to count statuses by month
                status_counts_by_month = df.groupby(['Month', 'Status']).size().unstack(fill_value=0)

                # Plot the data as a bar chart
                fig, ax = plt.subplots()
                status_counts_by_month.plot(kind='bar', ax=ax)
                ax.set_ylabel('Count')
                ax.set_xlabel('Month')
                ax.set_title('Status Distribution by Month')
                ax.legend(title='Status')

                # Set yaxis whole number
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))

                st.subheader('Status Distribution by Month')
                st.pyplot(fig)
            else:
                st.write("Data is empty or required columns are missing for the bar chart.")

# First, combine the data from all tables into a single DataFrame
combined_data = pd.concat([data_image, data_bulk_image, data_video, data_capture, data_live], ignore_index=True)

# Parse the date column to extract months
combined_data['Month'] = pd.to_datetime(combined_data['Date']).dt.strftime('%Y-%m')

# Aggregate the data to count statuses by month
status_counts_by_month = combined_data.groupby(['Month', 'Status']).size().unstack(fill_value=0)

with clm2:
    # Plot the data as a bar chart
    fig, ax = plt.subplots()
    status_counts_by_month.plot(kind='bar', ax=ax)
    ax.set_ylabel('Count')
    ax.set_xlabel('Month')
    ax.set_title('Combination Status Distribution by Month')
    ax.legend(title='Status')

    # Set yaxis whole number
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    st.subheader('Status Distribution by Month')
    st.pyplot(fig)