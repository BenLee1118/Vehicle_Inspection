import os
import zipfile
import tempfile
import pandas as pd
from PIL import Image
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
    page_title="Bulk Image Object Detection",
    page_icon='🖼️',
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
            # Change query "data_bulk_image" to your table name
            query = "SELECT No, Date, Type, `Vin No.`, `Seq No.`, Colour, TIME, `Straight Bracket`, `No Washer`, Status FROM data_bulk_image"
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
                    INSERT INTO data_bulk_image (Type, `Vin No.`, `Seq No.`, Colour, `Straight Bracket`, `No Washer`, Status, `Date`)
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
    st.header("Upload Your Image")
    source_imgs = st.file_uploader("Choose an Image...", type=("jpg", "jpeg", "png", 'bmp', 'webp'), accept_multiple_files=True)
    DEMO1_PATH = 'images/demo1.jpg'
    DEMO2_PATH = 'images/demo2.jpg'
    DEMO3_PATH = 'images/demo3.jpg'
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
st.title("Image Object Detection")
st.write("Choose your image and set the confidence level. Finally, click detect image.")

# List to store many paths of detected images
detected_image_paths = []

# Fetch data based on inputs
data = fetch_data(vehicle_identification_number, sequence_number, selected_colour, type)

# Create column 1 for data and column 2 for pie chart
column1, column2 = st.columns([0.7,0.35])
st.markdown("---")

# Creating 1 column for detect image button and 1 column for download zip
c1, c2 = st.columns(2)

# Creating 1 column for ori image and 1 column for detected image
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


# Column 1 for uploading demo images or uploaded images
with col1:
    if not source_imgs:
        demo_image1 = Image.open(DEMO1_PATH)
        demo_image2 = Image.open(DEMO2_PATH)
        demo_image3 = Image.open(DEMO3_PATH)
        st.image(DEMO1_PATH, caption="Demo Image", width = 400)
        st.image(DEMO2_PATH, caption="Demo Image", width=400)
        st.image(DEMO3_PATH, caption="Demo Image", width=400)
        demo_file_paths = [DEMO1_PATH, DEMO2_PATH, DEMO3_PATH]
    else:
        for source_img in source_imgs:
            uploaded_image = Image.open(source_img)
            st.image(uploaded_image, caption="Image Uploaded", width = 400)

# Put detect image button at c1
with c1:
    st.write("Detect all the images")
    detect_button = st.button('Detect Image')

# Do object Detection on demo images or uploaded images and display them one by one at column 2.
# Create temp path of each image and add them into one file paths for zip download
if detect_button:
    for source_img in source_imgs:
        uploaded_image = Image.open(source_img)
        res = model.predict(uploaded_image, conf = confidence)
        boxes = res[0].boxes
        res_plotted = res[0].plot()[:, :, ::-1]
        with col2:
            st.image(res_plotted, caption = 'Image Detected Results', width = 400)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file_path = temp_file.name
                Image.fromarray(res_plotted).save(temp_file_path)
                detected_image_paths.append(temp_file_path)
    if not source_imgs:
        res1 = model.predict(demo_image1, conf=confidence)
        res2 = model.predict(demo_image2, conf=confidence)
        res3 = model.predict(demo_image3, conf=confidence)
        boxes1 = res1[0].boxes
        boxes2 = res2[0].boxes
        boxes3 = res3[0].boxes
        res_plotted1 = res1[0].plot()[:, :, ::-1]
        res_plotted2 = res2[0].plot()[:, :, ::-1]
        res_plotted3 = res3[0].plot()[:, :, ::-1]
        with col2:
            st.image(res_plotted1, caption='Demo Detected Results', width = 400)
            st.image(res_plotted2, caption='Demo Detected Results', width=400)
            st.image(res_plotted3, caption='Demo Detected Results', width=400)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file1, \
                tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file2, \
                tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file3:
            temp_file_path1 = temp_file1.name
            temp_file_path2 = temp_file2.name
            temp_file_path3 = temp_file3.name
            Image.fromarray(res_plotted1).save(temp_file_path1)
            Image.fromarray(res_plotted2).save(temp_file_path2)
            Image.fromarray(res_plotted3).save(temp_file_path3)
            detected_image_paths.extend([temp_file_path1, temp_file_path2, temp_file_path3])

# If there is a detection of paths and after the detection and display finish,
# it will allow us to download the zip file with the button appear.
if detected_image_paths:
    with c2:
        st.write("Download all detected results")
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_path = os.path.join(temp_dir, "detected_images.zip")
            with zipfile.ZipFile(zip_file_path, "w") as zipf:
                for img_path in detected_image_paths:
                    zipf.write(img_path, os.path.basename(img_path))
                    os.unlink(img_path)  # Delete the temporary file
            with open(zip_file_path, "rb") as file:
                st.download_button(
                    label="Download Results",
                    data=file,
                    file_name="detected_images.zip",
                    mime="application/zip"
                )

