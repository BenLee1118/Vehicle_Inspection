import cv2
import pandas as pd
import streamlit as st
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
    page_title = "Live Object Detection",
    page_icon = '️🎥',
    layout = "wide",
    initial_sidebar_state = "expanded"
)

# Function for drawing frame purposes
def draw_boxes(frame, boxes, threshold):
    # Implementation to draw bounding boxes on the image
    return frame

# Function for WebCam and SiteCam1 to detect
def detect_objects(image):
    # Detection implementation using YOLO model
    detections = model(image, conf = confidence)
    # Format detections if necessary
    return detections

# Function for SiteCam2 to detect
def detect_objects2(image):
    # Detection implementation using YOLO model
    detections2 = model(image, conf = confidence)
    # Format detections if necessary
    return detections2

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
            # Change query "data_live" to your table name
            query = "SELECT No, Date, Type, `Vin No.`, `Seq No.`, Colour, TIME, `Straight Bracket`, `No Washer`, Status FROM data_live"
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
            # Change the name in the query below ("data_live"
            query = """
                    INSERT INTO data_live (Type, `Vin No.`, `Seq No.`, Colour, `Straight Bracket`, `No Washer`, Status, `Date`)
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

# Create Side Bar
with st.sidebar:
    st.header("Stream Configurations")
    confidence = float(st.slider("Set Confidence Level", 25, 100, 40)) / 100  # Model Confidence Option

    # Sidebar for user inputs to query the database
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

# Main Page
st.title("Live Object Detection")

# Fetch data based on inputs
data = fetch_data(vehicle_identification_number, sequence_number, selected_colour, type)

column1, column2 = st.columns([0.7,0.35])
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

# Create two tabs for Webcam and SiteCam
tab1, tab2 = st.tabs(["WebCam", "SiteCam"])

# Tab 1 for Webcam
with tab1:
    column1, column2 = st.columns([4, 4])
    with column1:
        st.header("WebCam Stream")
        webcam_switch = st.toggle("Start/Stop Detection")
        webcam = cv2.VideoCapture(0)
        display_webcam = st.empty()
        if webcam_switch:
            st.write("Camera On")
            webcam_OnOff = True
        else:
            st.write("Camera Off")
            webcam_OnOff = False
        while webcam_OnOff:
            ret, img = webcam.read()
            if ret:
                detections = detect_objects(img)
                res_plotted = detections[0].plot()
                output_frame = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
                display_webcam.image(res_plotted, channels="BGR", use_column_width=True)

# Tab 2 for SiteCam 1 and SiteCam 2
with tab2:
    placeholder = st.columns(2)
    st.header("SiteCam Stream")
    sitecam_switch = st.toggle("Start/Stop Detection All SiteCam")
    sitecam_1 = cv2.VideoCapture("http://192.168.1.158:8081") # Site Cam 1http://192.168.1.137:8081
    sitecam_2 = cv2.VideoCapture("http://192.168.1.152:8081")  # SiteCam 2 http://192.168.1.125:8081
    col1 = placeholder[0].empty()
    col2 = placeholder[1].empty()
    if sitecam_switch:
        st.write("SiteCam On")
        sitecam_OnOff = True
    else:
        st.write("SiteCam Off")
        sitecam_OnOff = False
    while sitecam_OnOff:
        ret1, img1 = sitecam_1.read()
        ret2, img2 = sitecam_2.read()
        if ret1 | ret2:
            detections = detect_objects(img1)
            detections2 = detect_objects2(img2)
            res_plotted1 = detections[0].plot()
            res_plotted2 = detections2[0].plot()
            output_frame1 = cv2.cvtColor(res_plotted1, cv2.COLOR_BGR2RGB)
            output_frame2 = cv2.cvtColor(res_plotted2, cv2.COLOR_BGR2RGB)
            col1.image(res_plotted1, channels="BGR", use_column_width=True)
            col2.image(res_plotted2, channels="BGR", use_column_width=True)