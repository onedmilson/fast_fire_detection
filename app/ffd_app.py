import streamlit as st
import cv2
from PIL import Image
import numpy as np
from ultralytics import YOLO
import os

# Load model
model = YOLO("../models/best.pt")

st.title("🔥 Fast Fire Detection App")

option = st.radio("Choose input type:", ("Image", "Webcam"))

if option == "Image":
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
       
        temp_image_path = "temp_image.jpg"
        with open(temp_image_path, "wb") as f:
            f.write(uploaded_image.read())

        st.image(temp_image_path, caption="Uploaded Image", use_container_width=True)

        # Prediction
        results = model.predict(source=temp_image_path, imgsz=640, conf=0.6)
        res_img = results[0].plot()

        st.image(res_img, caption="Prediction", use_container_width=True)

        if len(results[0].boxes) > 0:
            conf = results[0].boxes.conf[0].item()
            st.error(f"🔥 Fire detected! Confidence: {conf:.2f}")
        else:
            st.success("✅ No fire detected.")

        os.remove(temp_image_path)

elif option == "Webcam":
    st.warning("Click 'Start Webcam' to detect fire in real-time. Click 'Stop Webcam' to stop.")

    if "webcam_running" not in st.session_state:
        st.session_state.webcam_running = False

    col1, col2 = st.columns(2)
    with col1:
        start = st.button("Start Webcam", key="start_btn")
    with col2:
        stop = st.button("Stop Webcam", key="stop_btn")

    if start:
        st.session_state.webcam_running = True
    if stop:
        st.session_state.webcam_running = False

    if st.session_state.webcam_running:
        try:
            cap = cv2.VideoCapture(0)
            stframe = st.empty()

            while st.session_state.webcam_running:
                ret, frame = cap.read()
                if not ret:
                    break

                results = model.predict(source=frame, imgsz=640, conf=0.6)
                res_frame = results[0].plot()

                stframe.image(res_frame, channels="BGR", use_container_width=True)

                if not st.session_state.webcam_running:
                    break

            cap.release()
            cv2.destroyAllWindows()
            stframe.empty()

        except Exception as e:
            st.error(f"An error occurred: {e}")
