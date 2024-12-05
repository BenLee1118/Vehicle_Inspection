import os
import re
import zipfile
import tempfile
import requests
import pandas as pd
from PIL import Image
import streamlit as st
from io import BytesIO
from ultralytics import YOLO
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import mysql.connector
from mysql.connector import Error

# Specified Model Path
model_path = "weights/best.pt"

# Loading of Trained YOLOv9 Model
try:
    model = YOLO(model_path)
except Exception as ex:
    st.error(f"Unable to load YOLO model. Check Model Path: {model_path}")
    st.error(ex)

# Page Layout Setting
st.set_page_config(
    page_title="Image Capture Object Detection",
    page_icon='📸',
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to fetch data from MySQL database
def fetch_data(vin, sequence_number, colour, type):
    db_config = {
        'host': 'localhost',    # dont change
        'user': 'root',         # change user
        'password': '',         # put password
        'database': 'data1'     # database name
    }
    try:
        db_conn = mysql.connector.connect(**db_config)
        if db_conn.is_connected():
            # Change query "data_image" to your table name
            query = "SELECT No, Date, Type, `Vin No.`, `Seq No.`, Colour, TIME, `Straight Bracket`, `No Washer`, Status FROM data_capture"
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

# Function to insert data to MySQL database
def insert_data(type, vin, seq_no, colour, bracket, washer, status):
    db_config = {
        'host': 'localhost',    # dont change
        'user': 'root',         # change user
        'password': '',         # put password
        'database': 'data1'     # database name
    }
    try:
        # with mysql.connector.connect(**db_config) as db_conn:
        db_conn = mysql.connector.connect(**db_config)
        if db_conn.is_connected():
            query = """
                    INSERT INTO data_capture (Type, `Vin No.`, `Seq No.`, Colour, `Straight Bracket`, `No Washer`, Status, `Date`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
            values = (type, vin, seq_no, colour, bracket, washer, status, datetime.now())
            cursor = db_conn.cursor()
            cursor.execute(query, values)
            db_conn.commit()
            st.success("Data inserted successfully!")
            cursor.close()
            db_conn.close()
    except Error as e:
        st.error(f"Error connecting to the database: {e}")

# Function to fetch and return the image
def fetch_image(url):
    try:
        response = requests.get(url, timeout=5)  # Add a timeout to avoid hanging requests
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return Image.open(BytesIO(response.content))
    except requests.exceptions.Timeout:
        st.error(f"Request to {url} timed out.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"Failed to connect to {url}. Please check the IP address format.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}. Make sure Raspberry is Turned On and Check IP Address Number")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return None

def display_detection_results(image, col, cam_results):
    res = model.predict(image, conf=confidence)
    boxes = res[0].boxes
    res_plotted = res[0].plot()[:, :, ::-1]
    with col:
        st.image(res_plotted, caption='Detection Results', use_column_width=True)
        detected_classes = [(model.names[int(c)], conf) for r in res for c, conf in zip(r.boxes.cls, r.boxes.conf)]
        st.subheader(cam_results)
        st.write("Detected Classes with Confidence Scores:")
        for cls, conf in detected_classes:
            st.info(f"{cls}: {conf:.2f}")

        # Check conditions for OK or NOT OK
        detected_classes_set = set(cls for cls, _ in detected_classes)
        # classy = set(["straight bracket", "no washer friction"])  # Method 1 test the below statement
        # classy= {"straight bracket", "no washer friction"}        # Method 2 test the below statement

        if "crooked bracket" in detected_classes_set or "washer friction" in detected_classes_set:
            st.error("  NOT OK", icon="🚨")
        elif detected_classes_set == {"straight bracket", "no washer friction"}:
            st.success("    OK", icon="✅")
        else:
            st.warning("Unknown", icon="⚠️")

with st.sidebar:
    st.header("Insert IP Addresses")
    # Model Confidence Option
    confidence = float(st.slider("Set Confidence Level", 25, 100, 40)) / 100
    # Input for the first and second camera IP address
    ip_address1 = st.text_input("Enter the IP address for Camera 1 (e.g., 192.168.1.4)")
    # Input for the second camera IP address
    ip_address2 = st.text_input("Enter the IP address for Camera 2 (e.g., 192.168.1.5)")

# Title of the app
st.title("Image Capture Object Detection")
column1, column2 = st.columns([0.7,0.35])
st.markdown("---")

# If both IP addresses are provided
if ip_address1 and ip_address2:
    # Construct the URLs using the input IP addresses
    image_url1 = f"http://{ip_address1}/picture/1/current/"
    image_url2 = f"http://{ip_address2}/picture/1/current/"

    # Fetch the images
    image1 = fetch_image(image_url1)
    image2 = fetch_image(image_url2)

    # Display the images if they were successfully fetched
    if image1 and image2:
        st.sidebar.write("Links are Correct")
        if st.sidebar.button("Capture Images"):
            col1, col2 = st.columns(2)
            with col1:
                st.image(image1, caption=f'Camera 1 Image from {ip_address1}', use_column_width=True)
            with col2:
                st.image(image2, caption=f'Camera 2 Image from {ip_address2}', use_column_width=True)

        detect_button = st.sidebar.button("Detect Images")
        colu1, colu2 = st.columns(2)
        cam_results1 = "Camera 1 Results"
        cam_results2 = "Camera 2 Results"
        with colu1:
            st.header("Camera 1 View")
        with colu2:
            st.header("Camera 2 View")

        if detect_button:
            display_detection_results(image1, colu1, cam_results1)
            display_detection_results(image2, colu2, cam_results2)
    else:
        st.sidebar.write("Images not found, refer to the error")

with st.sidebar:
    # Sidebar for user inputs to query the database
    st.sidebar.markdown("---")
    st.header("Data Parameters")
    st.subheader("Insert for Data Query")
    type = st.text_input('Type')
    vehicle_identification_number = st.text_input('Vehicle Identification Number')
    sequence_number = st.text_input('Sequence Number')
    colour = ['All', 'Red', 'Blue', 'Silver', 'White', 'Black']
    selected_colour = st.selectbox('Vehicle Colour', colour)

    st.subheader("Insert Data into Database")
    with st.form(key='insert form'):
        type_input = st.text_input('Type (Insert)')
        vin_input = st.text_input('Vehicle Identification Number (Insert)')
        seq_no_input = st.text_input('Sequence Number (Insert)')
        colour_input = st.selectbox('Vehicle Colour (Insert)', ['Red', 'Blue', 'Silver', 'White', 'Black'])
        bracket_input = st.text_input('Straight Bracket')
        washer_input = st.text_input('No Washer')
        status_input = st.selectbox('Status', ['ok', 'not ok'])

        submit_button = st.form_submit_button('Submit')
        if submit_button:
            insert_data(type_input, vin_input, seq_no_input, colour_input, bracket_input, washer_input, status_input)

# Fetch data based on inputs
data = fetch_data(vehicle_identification_number, sequence_number, selected_colour, type)

# Creating two columns on the main page
col1, col2 = st.columns(2)

# Display the fetched data
with column1:
    st.subheader('Queried Data')
    if not data.empty:
        st.dataframe(data)
    else:
        st.write("No data available based on the input parameters.")

# Pie chart section for 'Status' distribution
with column2:
    if not data.empty and 'Status' in data.columns and 'Date' in data.columns:
        # Parse the date column to extract months
        data['Month'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m')

        # Aggregate the data to count statuses by month
        status_counts_by_month = data.groupby(['Month', 'Status']).size().unstack(fill_value=0)

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