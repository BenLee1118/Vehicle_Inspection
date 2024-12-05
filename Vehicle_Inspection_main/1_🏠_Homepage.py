import streamlit as st

st.set_page_config(
    page_title = "Home",
    page_icon = '🏡️',
    layout = "wide",
    initial_sidebar_state = "expanded"
)

st.sidebar.success("Select a page above.")

st.image("images/logo.png", width=150)
st.title("Project Explanation")

c1, c2 = st.columns([0.3, 0.5])
st.markdown("---")
col1, col2, col3 = st.columns([0.5, 0.3, 0.3])
st.markdown("---")
colu1, colu2, colu3 = st.columns([0.3, 0.3, 0.5])
st.markdown("---")
colum1, colum2 = st.columns([0.5, 0.3])
st.markdown("---")

with c1:
    st.image("images/model.jpg", width=500)
with c2:
    st.header("Enhanced Inspection System")
    st.subheader("Deep Learning for Anomaly Detection of Underbody Vehicles")
    proj_exp = "This project is developed to undergo car inspection with the help of Artificial Intelligence which" \
               "is YOLOv9 from Ultralytics. With the help of AI, detection process becomes more easier and " \
               "convinient. The AI will automatically help us to scan the image/video input from camera then process " \
               "it and displayed out a detected result for us to see."
    page_exp = "There are total of six pages including the homepage. The Data Collection page will allowed you to " \
               "access and inspect all the data from different detection categories. The Image Object Detection page " \
               "allows you to upload one image and detect it. The Bulk Image Object Detection page allows you to " \
               "upload a folder of images and detect all. The Video Object Detection page allows you to upload a " \
               "video and detects the video. The Live Object Detection allows you to stream through your webcam or " \
               "wireless camera to do live detection."
    st.write(proj_exp)
    st.write(page_exp)

with col1:
    st.header("Detection")
    st.subheader("Bracket & Washer")
    detect_exp = "The system developed is used to detect the bracket and washer on the exhaust mounting underneath the" \
                 " vehicle. There will be a total of four classes which are 'Straight Bracket', 'Crooked Bracket', " \
                 "'Washer Friction' and 'No Washer Friction'."
    st.write(detect_exp)
with col2:
    st.image("images/demo4.jpg", width=300)
with col3:
    st.image("images/demo5.jpg", width=300)

with colu1:
    st.image("images/demo6.png", width=300)
with colu2:
    st.image("images/demo7.png", width=300)
with colu3:
    st.header("Equipments")
    equip_exp = "This project used Nvidia Jetson Orin Nano to run all the detection process and display the results " \
                "out on a website. The camera used is the Raspberry Pi NoIR Camera with the help of " \
                "Raspberry Pi Zero WH to setup the camera properly, the connection between the Pi Zero WH with the " \
                "Jetson Orin Nano is through wireless connection which is throught a local webserver."
    st.write(equip_exp)

with colum1:
    st.header("Software Stack")
    software_exp = "To developed this system, there are several software stacks that we used to help us to build this" \
                   " model system. Ultralytics is the one that provide us YOLOv9 model to train with our datasets. " \
                   "MotionEyes and Raspberry helped us to setup the NoIR camera along with Pi Zero WH. PyCharm is " \
                   "the platform where we use python to train our YOLOv9 model and design our webpage. MySQL is the" \
                   " database where we store all the collected data. Streamlit is the web server where we can do " \
                   "all the object detection and insert or display all the data collected."
    st.write(software_exp)
with colum2:
    st.image("images/demo8.png", width=500)