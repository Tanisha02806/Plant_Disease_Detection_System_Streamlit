from multiprocessing import reduction
import streamlit as st
import tensorflow as tf
import numpy as np
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import io
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import hashlib
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from fpdf import FPDF

st.set_page_config(layout="wide")

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["plant_disease_app"]
users_collection = db["users"]
history_collection = db["historyTracker"]

# --- Password Hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# --- Signup ---
def signup(username, password, first_name, last_name, phone_number):
    if users_collection.find_one({"username": username}):
        return False, "Username already exists."

    hashed_pw = hash_password(password)
    user_document = {
        "username": username,
        "password": hashed_pw,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "registration_date": datetime.datetime.utcnow()
    }
    users_collection.insert_one(user_document)
    return True, "Account created successfully!"

# --- Login ---
def login(username, password):
    user = users_collection.find_one({"username": username})
    if not user:
        return False, "User not found. Please sign up first."
    if verify_password(password, user["password"]):
        return True, user
    return False, "Incorrect password."

# --- Auth Interface ---
def auth_interface():
    # Session state defaults
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # Already logged in
    if st.session_state.logged_in:
        return True

    # UI Styling
    with st.container():
        st.markdown(
            "<h2 style='text-align: center;'>Welcome to FloraScan</h2>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='max-width: 500px; margin: auto;'>", unsafe_allow_html=True)

        option = st.radio("Choose Option", ["Login", "Sign Up"])

        if option == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                success, result = login(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = result["username"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result)

        elif option == "Sign Up":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            phone_number = st.text_input("Phone Number")

            if st.button("Sign Up"):
                if not (username and password and first_name and last_name and phone_number):
                    st.warning("Please fill in all fields.")
                else:
                    success, msg = signup(username, password, first_name, last_name, phone_number)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)

    return False  # Not logged in

#Saving prediction data to MongoDB
def history_tracking(username, predicted_disease, description, treatment, health_percentage, severity):
    history_collection.insert_one({
        "username": username,
        "disease": predicted_disease,
        "timestamp": datetime.now(),
        "description": description,
        "treatment": treatment,
        "health_percentage": round(health_percentage, 2),
        "severity": severity
    })

def set_bg_image(image_path):
    with open(image_path, "rb") as img_file:
        b64_img = base64.b64encode(img_file.read()).decode()
        
    page_bg_img = f"""
    <style>

    .stApp{{
        background-image: linear-gradient(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.6)),url("data:image/jpg;base64,{b64_img}");
        background-size: cover;
    }}           
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_bg_image("img/background.jpg")

logged_in = auth_interface()
# Main App Starts After Auth
if logged_in:
    # Description dictionary
    disease_descriptions = {
        "Apple___Apple_scab": "Apple scab is a fungal disease that causes dark, scabby lesions on leaves and fruit.",
        "Apple___Black_rot": "Black rot is a fungal disease affecting apples. It causes leaf spots and fruit decay.",
        "Apple___Cedar_apple_rust": "Cedar apple rust is a fungal disease that causes yellow-orange spots on apple leaves and fruit.",
        "Apple___healthy": "The apple plant appears healthy with no signs of disease.",
        "Blueberry___healthy": "The blueberry plant shows no visible disease symptoms.",
        "Cherry_(including_sour)___Powdery_mildew": "Powdery mildew in cherry plants causes white, powdery fungal growth on leaves and stems.",
        "Cherry_(including_sour)___healthy": "The cherry plant appears healthy with no visible disease signs.",
        "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Gray leaf spot in corn is caused by a fungus and results in elongated, gray to tan lesions on leaves.",
        "Corn_(maize)___Common_rust_": "Common rust in corn is a fungal disease. It causes reddish-brown pustules on leaves.",
        "Corn_(maize)___Northern_Leaf_Blight": "Northern leaf blight in corn causes long, gray-green or tan lesions on the leaves.",
        "Corn_(maize)___healthy": "The corn plant appears healthy and unaffected by disease.",
        "Grape___Black_rot": "Black rot in grapes is a fungal disease causing black spots on leaves, shoots, and fruit.",
        "Grape___Esca_(Black_Measles)": "Esca, or black measles, is a grapevine disease that causes dark streaks in wood and spots on leaves and fruit.",
        "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Isariopsis leaf spot causes dark lesions on grape leaves, reducing photosynthetic ability.",
        "Grape___healthy": "The grape plant shows no visible symptoms of disease.",
        "Orange___Haunglongbing_(Citrus_greening)": "Huanglongbing, or citrus greening, is a bacterial disease that causes yellowing of leaves and misshapen, bitter fruit.",
        "Peach___Bacterial_spot": "Bacterial spot in peaches causes dark, sunken spots on leaves, fruit, and twigs.",
        "Peach___healthy": "The peach plant is healthy with no signs of disease.",
        "Pepper,_bell___Bacterial_spot": "Bacterial spot in bell peppers causes water-soaked lesions on leaves and fruits that turn dark and scabby.",
        "Pepper,_bell___healthy": "The bell pepper plant is healthy and shows no disease symptoms.",
        "Potato___Early_blight": "Early blight in potatoes is a fungal disease causing concentric ring patterns on leaves and stems.",
        "Potato___Late_blight": "Late blight is a severe disease of potatoes that causes dark blotches on leaves and rot on tubers.",
        "Potato___healthy": "The potato plant is healthy with no visible signs of disease.",
        "Raspberry___healthy": "The raspberry plant shows no disease symptoms and appears healthy.",
        "Soybean___healthy": "The soybean plant appears free from any disease symptoms.",
        "Squash___Powdery_mildew": "Powdery mildew in squash causes white, powdery spots on leaves and stems, reducing plant vigor.",
        "Strawberry___Leaf_scorch": "Leaf scorch in strawberries causes browning and drying of leaf edges and tips due to fungal infection.",
        "Strawberry___healthy": "The strawberry plant is healthy with no signs of disease.",
        "Tomato___Bacterial_spot": "Bacterial spot in tomatoes causes small, dark spots on leaves and fruits, leading to defoliation and blemishes.",
        "Tomato___Early_blight": "Early blight in tomatoes is a fungal disease with concentric rings on older leaves and fruit drop.",
        "Tomato___Late_blight": "Late blight causes dark, greasy-looking spots on tomato leaves, stems, and fruit.",
        "Tomato___Leaf_Mold": "Leaf mold in tomatoes is caused by fungus. Yellow spots and mold growth appear on leaves.",
        "Tomato___Septoria_leaf_spot": "Septoria leaf spot causes small, circular spots with dark borders on lower leaves of tomato plants.",
        "Tomato___Spider_mites Two-spotted_spider_mite": "Spider mites cause yellowing and speckling on tomato leaves due to feeding damage.",
        "Tomato___Target_Spot": "Target spot in tomatoes causes dark, concentric lesions on leaves and fruits due to fungal infection.",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "TYLCV causes yellowing and upward curling of leaves, stunted growth, and reduced fruit yield.",
        "Tomato___Tomato_mosaic_virus": "Tomato mosaic virus causes mottled, discolored leaves and distorted fruit.",
        "Tomato___healthy": "The tomato plant is healthy with no visible signs of disease."
    }
    def get_description(disease_name):
        return disease_descriptions.get(disease_name, "No description available for this disease.")




    def model_prediction(image_file):
        model = tf.keras.models.load_model("trained_model.h5")
        image = tf.keras.preprocessing.image.load_img(image_file, target_size=(128, 128))
        input_arr = tf.keras.preprocessing.image.img_to_array(image)
        input_arr = np.expand_dims(input_arr, axis=0)
        prediction = model.predict(input_arr)
        result_index = np.argmax(prediction)
        confidence = float(np.max(prediction)) * 100
        return result_index, confidence

    def get_description(disease_name):
        return disease_descriptions.get(disease_name, "No description available for this disease.")

    def create_download_link(disease_name, description, image_file, health_percentage, treatment, severity, filename="diagnosis.pdf"):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.setFillColor(HexColor("#f0fff0"))
        c.rect(0, 0, width, height, fill=1)
        c.setFillColor(HexColor("#006400"))
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 100, "PLANT DISEASE DIAGNOSIS REPORT")
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 140, description)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 180, disease_name)
        image = ImageReader(image_file)
        img_width, img_height = image.getSize()
        aspect = img_height / img_width
        new_width = width * 0.6
        new_height = new_width * aspect
        x = (width - new_width) / 2
        y = height - 350 - new_height
        c.drawImage(image, x, y, width=new_width, height=new_height)
        c.save()
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📄 Download PDF Report</a>'
        return href

    #List of treatments 
    treatments = {
        "Apple___Apple_scab": "Prune infected leaves and apply fungicide such as captan or myclobutanil.",
        "Apple___Black_rot": "Remove mummified fruit and infected limbs. Use fungicides like thiophanate-methyl.",
        "Apple___Cedar_apple_rust": "Remove nearby cedar trees if possible and apply preventive fungicides.",
        "Apple___healthy": "No treatment needed. Maintain regular monitoring and proper nutrition.",
        
        "Blueberry___healthy": "No treatment needed. Ensure proper drainage and routine inspection.",
        
        "Cherry_(including_sour)___Powdery_mildew": "Apply sulfur or potassium bicarbonate spray and improve air circulation.",
        "Cherry_(including_sour)___healthy": "No treatment required. Maintain proper pruning and watering.",
        
        "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Use resistant hybrids and apply fungicide like azoxystrobin at early symptoms.",
        "Corn_(maize)___Common_rust_": "Use resistant varieties and fungicides like propiconazole.",
        "Corn_(maize)___Northern_Leaf_Blight": "Use resistant hybrids and apply fungicide early in disease development.",
        "Corn_(maize)___healthy": "No treatment required. Maintain spacing and rotation practices.",
        
        "Grape___Black_rot": "Prune infected parts and apply fungicides like mancozeb or myclobutanil.",
        "Grape___Esca_(Black_Measles)": "Remove affected vines and avoid mechanical injuries. No known effective fungicide.",
        "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Improve air flow and apply fungicides like trifloxystrobin.",
        "Grape___healthy": "No treatment needed. Continue regular monitoring and pruning.",
        
        "Orange___Haunglongbing_(Citrus_greening)": "Remove infected trees and control psyllid vectors using insecticides.",
        
        "Peach___Bacterial_spot": "Use resistant varieties, copper-based sprays, and remove infected fruit.",
        "Peach___healthy": "No treatment required. Maintain good sanitation and irrigation practices.",
        
        "Pepper,_bell___Bacterial_spot": "Apply copper-based bactericides and avoid overhead watering.",
        "Pepper,_bell___healthy": "No treatment needed. Maintain proper soil health and pest control.",
        
        "Potato___Early_blight": "Apply fungicides such as chlorothalonil or mancozeb and rotate crops.",
        "Potato___Late_blight": "Use resistant varieties and apply fungicides like metalaxyl.",
        "Potato___healthy": "No treatment required. Monitor soil moisture and nutrients.",
        
        "Raspberry___healthy": "No treatment needed. Ensure proper pruning and spacing.",
        
        "Soybean___healthy": "No treatment required. Rotate crops and monitor soil nutrients.",
        
        "Squash___Powdery_mildew": "Use sulfur sprays or neem oil and plant resistant varieties.",
        
        "Strawberry___Leaf_scorch": "Remove infected leaves and apply fungicides like captan or myclobutanil.",
        "Strawberry___healthy": "No treatment needed. Maintain dry foliage and avoid overcrowding.",
        
        "Tomato___Bacterial_spot": "Use copper-based sprays and avoid overhead irrigation.",
        "Tomato___Early_blight": "Apply fungicides such as chlorothalonil and remove infected leaves.",
        "Tomato___Late_blight": "Use resistant varieties and apply fungicides like mancozeb or metalaxyl.",
        "Tomato___Leaf_Mold": "Improve air circulation and use fungicides like chlorothalonil.",
        "Tomato___Septoria_leaf_spot": "Remove infected foliage and apply fungicides regularly.",
        "Tomato___Spider_mites Two-spotted_spider_mite": "Spray insecticidal soap or neem oil and maintain humidity.",
        "Tomato___Target_Spot": "Use copper-based fungicides and ensure good field sanitation.",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Control whitefly populations and remove infected plants.",
        "Tomato___Tomato_mosaic_virus": "Destroy infected plants and disinfect tools; no chemical control available.",
        "Tomato___healthy": "No treatment needed. Continue good growing practices.",
    }
    def get_treatment_suggestion(disease):
        return treatments.get(disease, "No treatment suggestion available for this disease.")

    def get_severity(confidence):
        if confidence >= 85:
            return "Severe"
        elif confidence >= 60:
            return "Moderate"
        else:
            return "Mild"
    
    with st.sidebar:
        col1, col2 = st.columns([2, 5])  # Adjust column ratio as needed

        with col1:
            st.image("img/logo.png", width=40)  # Your logo

        with col2:
            st.markdown("<h3 style='font-size: 30px; margin-top: 1px; color: green;'>FloraScan</h3>", unsafe_allow_html=True)

    st.sidebar.markdown(
        "<h1 style='font-size: 36px; color: green; font-family:Arial;'>Dashboard</h1>",
        unsafe_allow_html=True
    )
    app_mode = st.sidebar.radio("", ["Home", "Profile", "Disease Recognition", "History"])
    st.markdown("""
        <style>
        /* Sidebar container styling */
        [data-testid="stSidebar"] {
            color: #1b5e20;
            padding: 2rem;
            font-family: 'Poppins', sans-serif;
            border-right: 2px solid #a5d6a7;
            font-size: 36px;
        }

        /* Sidebar headings */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #2e7d32;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        /* Radio buttons group style */
        div[role="radiogroup"] label {
            font-size: 100px;
            font-weight: 500;
            color: #2e7d32;
            margin-bottom: 0.5rem;
            padding: 1px 1px;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        </style>
    """, unsafe_allow_html=True)


    if app_mode == "Home":
        # Center the image using columns
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.write("")

        with col2:
            st.image("img/home.png", width=500)

        with col3:
            st.write("")

        st.markdown("""
        <style>
            .florascan-container {
                font-family: 'Segoe UI', sans-serif;
                color: #2d3436;
                padding: 0 20px;
                line-height: 1.7;
                background: transparent;
                border: none;
                box-shadow: none;
            }
            .florascan-container p {
                font-size: 18px;
            }
            .florascan-container h3 {
                color: #27ae60;
                font-size: 30px;
                margin-bottom: 10px;
            }
            .florascan-container h4 {
                color: #27ae60;
                font-size: 30px;
                margin-top: 20px;
            }
            .florascan-container ul {
                padding-left: 1.5em;
                font-size: 18px;
            }
            .florascan-container li {
                margin-bottom: 10px;
                font-size: 18px;
            }
        </style>

        <div class="florascan-container">
            <h3>Welcome to FloraScan!</h3>
            <p>
                <strong>FloraScan</strong> is an intelligent plant health detection platform that enables users to upload or capture images of their plants to assess their condition. Leveraging advanced AI technology, the system analyzes the image in real time to detect signs of disease or confirm plant health. With a focus on early diagnosis and prevention, FloraScan empowers users to protect, treat, and care for their plants more effectively.
            </p>
            <h4>How It Works</h4>
            <ul>
                <li><strong>Upload Image:</strong> Go to the <em>Disease Recognition</em> page and upload an image of a plant with suspected diseases.</li>
                <li><strong>Analysis:</strong> Our system processes the image using advanced algorithms to identify potential diseases.</li>
                <li><strong>Results:</strong> View the results and recommendations for further action.</li>
            </ul>
            <h4>Why Choose Us?</h4>
            <ul>
                <li><strong>Accuracy:</strong> Utilizes state-of-the-art machine learning for precise detection.</li>
                <li><strong>User-Friendly:</strong> Simple, intuitive interface for all experience levels.</li>
                <li><strong>Fast and Efficient:</strong> Get results in seconds for timely action.</li>
            </ul>
            <h4>About Us</h4>
            <p>
                This project is developed by engineering students passionate about leveraging technology to support sustainable agriculture. Our goal is to provide farmers, agronomists, and enthusiasts with a reliable tool to detect plant diseases early, reduce crop losses, and enhance decision-making. We combine deep learning with an intuitive interface to make plant health monitoring accessible, accurate, and efficient.
            </p>
        </div>
        """, unsafe_allow_html=True)


        # Add Footer
        st.markdown("""
        <style>
        .footer {
            background-color: #ffffff;
            padding: 20px 10px;
            color: green;
            font-size: 18px;
            text-align: center;
            width: 100%;
            margin-top: 30px;
        }
        .footer a {
            color: light green;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        </style>
        <hr style="border: 0.5px solid #ccc" />
        <div class="footer">
            <strong>FloraScan</strong> | Helping you grow healthier plants<br>
            Contact us: <a href="mailto:tanishaselfthakur@gmail.com">tanishaselfthakur@gmail.com</a> | Website: <a href="#" target="_blank">#</a><br>
            © 2025 FloraScan. All rights reserved.
        </div>
        """, unsafe_allow_html=True)


    elif app_mode == "Profile":

        username = st.session_state.get("username")

        if not username:
            st.warning("You must be logged in to view your profile.")
        else:
            if "edit_mode" not in st.session_state:
                st.session_state.edit_mode = False

            user_data = users_collection.find_one({"username": username})

            if not user_data:
                st.error("User profile not found in the database.")
            else:
                from datetime import datetime

                reg_date = user_data.get("registration_date")
                formatted_date = reg_date.strftime("%d %B %Y, %I:%M %p") if isinstance(reg_date, datetime) else "Unknown"

                # Modal Style (inject only once)
                st.markdown("""
                    <style>
                    .modal-container {
                        position: fixed;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        background: white;
                        padding: 25px;
                        border-radius: 10px;
                        width: 350px;
                        z-index: 999;
                        box-shadow: 0 0 20px rgba(0,0,0,0.3);
                    }
                    </style>
                """, unsafe_allow_html=True)

                if not st.session_state.edit_mode:
                    # Title row: Left = User Profile, Right = Profile Picture
                    col_left, col_right = st.columns([1, 1], gap="medium")

                    with col_left:
                        st.subheader("User Profile")
                        st.markdown(f"- **Username:** `{username}`")
                        st.markdown(f"- **First Name:** {user_data.get('first_name', 'N/A')}")
                        st.markdown(f"- **Last Name:** {user_data.get('last_name', 'N/A')}")
                        st.markdown(f"- **Phone Number:** {user_data.get('phone_number', 'N/A')}")
                        st.markdown(f"- **Registered On:** {formatted_date}")

                        col1, col2 = st.columns(2)
                        if col1.button("Edit Profile"):
                            st.session_state.edit_mode = True

                        if col2.button("Logout"):
                            for key in list(st.session_state.keys()):
                                del st.session_state[key]
                            st.success("You have been logged out.")
                            st.rerun()

                    with col_right:
                        st.subheader("Profile Picture")

                        profile_pic_path = user_data.get("profile_picture_path", None)
                        if profile_pic_path:
                            st.image(profile_pic_path, width=150, caption="Your Avatar")
                        else:
                            st.image("img/default_pfp.jpg", width=150, caption="No Avatar")

                        uploaded_file = st.file_uploader(
                            label="",
                            type=["png", "jpg", "jpeg"],
                            label_visibility="collapsed"
                        )

                        if st.button("📷 Upload Photo"):
                            if uploaded_file is not None:
                                import os
                                os.makedirs("uploads", exist_ok=True)
                                image_path = f"uploads/{username}_avatar.png"
                                with open(image_path, "wb") as f:
                                    f.write(uploaded_file.read())

                                users_collection.update_one(
                                    {"username": username},
                                    {"$set": {"profile_picture_path": image_path}}
                                )
                                st.success("Profile picture updated successfully.")
                                st.rerun()
                            else:
                                st.warning("Please select a file before uploading.")



                # Edit Mode (Modal)
                else:

                    with st.form("edit_profile_form"):
                        st.subheader("Edit Profile")

                        first_name = st.text_input("First Name", value=user_data.get("first_name", ""))
                        last_name = st.text_input("Last Name", value=user_data.get("last_name", ""))
                        phone_number = st.text_input("Phone Number", value=user_data.get("phone_number", ""))

                        col1, col2 = st.columns(2)
                        submitted = col1.form_submit_button("Save")
                        cancelled = col2.form_submit_button("Cancel")

                        if submitted:
                            users_collection.update_one(
                                {"username": username},
                                {
                                    "$set": {
                                        "first_name": first_name,
                                        "last_name": last_name,
                                        "phone_number": phone_number,
                                    }
                                }
                            )
                            st.session_state.edit_mode = False
                            st.success("Profile updated successfully.")
                            st.rerun()

                        elif cancelled:
                            st.session_state.edit_mode = False
                            st.info("Edit cancelled.")
                            st.rerun()

                    st.markdown('</div>', unsafe_allow_html=True)


    elif app_mode == "Disease Recognition":
        st.header("Disease Recognition")
        
        #File upload and camera input options
        uploaded_file = st.file_uploader("Choose an Image:", type=["jpg", "jpeg", "png"])
        st.write("OR")
        camera_image = st.camera_input("Take a Picture")
        
        #Decide which image to use (uploaded or camera)
        input_image = uploaded_file if uploaded_file is not None else camera_image
        

        if input_image is not None:
            if st.button("Show Image"):
                st.image(input_image, use_column_width=True)

            if st.button("Predict"):
                with st.spinner("Please wait.."):
                    st.write("Our Prediction")
                    result_index, confidence = model_prediction(input_image)
                    class_names = [ 'Apple___Apple_scab',
                                    'Apple___Black_rot',
                                    'Apple___Cedar_apple_rust',
                                    'Apple___healthy',
                                    'Blueberry___healthy',
                                    'Cherry_(including_sour)___Powdery_mildew',
                                    'Cherry_(including_sour)___healthy',
                                    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                                    'Corn_(maize)___Common_rust_',
                                    'Corn_(maize)___Northern_Leaf_Blight',
                                    'Corn_(maize)___healthy',
                                    'Grape___Black_rot',
                                    'Grape___Esca_(Black_Measles)',
                                    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                                    'Grape___healthy',
                                    'Orange___Haunglongbing_(Citrus_greening)',
                                    'Peach___Bacterial_spot',
                                    'Peach___healthy',
                                    'Pepper,_bell___Bacterial_spot',
                                    'Pepper,_bell___healthy',
                                    'Potato___Early_blight',
                                    'Potato___Late_blight',
                                    'Potato___healthy',
                                    'Raspberry___healthy',
                                    'Soybean___healthy',
                                    'Squash___Powdery_mildew',
                                    'Strawberry___Leaf_scorch',
                                    'Strawberry___healthy',
                                    'Tomato___Bacterial_spot',
                                    'Tomato___Early_blight',
                                    'Tomato___Late_blight',
                                    'Tomato___Leaf_Mold',
                                    'Tomato___Septoria_leaf_spot',
                                    'Tomato___Spider_mites Two-spotted_spider_mite',
                                    'Tomato___Target_Spot',
                                    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                                    'Tomato___Tomato_mosaic_virus',
                                    'Tomato___healthy' ]  
                    disease = class_names[result_index]
                    description = get_description(disease)
                    treatment = get_treatment_suggestion(disease)
                    health_percentage = 100 - confidence
                    severity = get_severity(confidence)
                    
                    st.success(f"Model predicts: **{disease}** with confidence {confidence:.2f}%")
                    st.info(f"Estimated Plant Health: **{health_percentage:.2f}%**")
                    
                    #Treatment suggestion section
                    st.subheader("Basic treatment suggestion")
                    st.write(treatment)
                    
                    st.warning(f"Estimated Disease Severity: **{severity}**")
                    if severity == "Severe":
                        st.error(" Severe infection detected. Immediate action recommended.")   
                    elif severity == "Moderate":
                        st.warning("Moderate symptoms present. Begin treatment soon.")
                    else:
                        st.info("Mild symptoms. Monitor and apply light treatment if needed.")
                    
                    # Call history tracker
                    history_tracking(st.session_state.username, disease, description, treatment, health_percentage, severity)
                    
                    #Resize and display image
                    image = Image.open(input_image)
                    max_width = 600
                    if image.width > max_width:
                        aspect_ratio = image.height / image.width
                        new_height = int(aspect_ratio * max_width)
                        image = image.resize((max_width, new_height))
                    st.image(image, caption="Captured/Uploaded Image", use_container_width=False, channels="RGB")
                    
                    #PDF download link
                    pdf_link = create_download_link(disease, description, input_image, health_percentage, treatment, severity)
                    st.markdown(pdf_link, unsafe_allow_html=True)
                    
                    
    elif app_mode == "History":
        st.markdown("""
        <style>
            /* Remove Streamlit horizontal scrollbars */
            .stDataFrame div[role="grid"] {
                overflow-x: hidden !important;
            }

            /* Expand column widths for better visibility */
            .stDataFrame td, .stDataFrame th {
                min-width: 120px;
                word-wrap: break-word;
                white-space: normal;
            }
        </style>
        """, unsafe_allow_html=True)
        st.header("Prediction History")
        

        def generate_pdf(dataframe):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Prediction History Report", ln=True, align='C')
            pdf.ln(10)

            pdf.set_font("Arial", size=10)

            for idx, row in dataframe.iterrows():
                pdf.cell(200, 8, txt=f"#{row['S.No']} | Disease: {row['Predicted Disease']}", ln=True)
                pdf.multi_cell(0, 6, txt=f"Description: {row['Description']}", border=0)
                pdf.multi_cell(0, 6, txt=f"Treatment: {row['Treatment']}", border=0)
                pdf.cell(200, 6, txt=f"Health %: {row['Health %']}    Severity: {row['Severity']}", ln=True)
                pdf.ln(5)

            # Get PDF as byte string and return as BytesIO
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            buffer = BytesIO(pdf_bytes)
            return buffer


        def display_history(username):
            entries = history_collection.find({"username": username}).sort("timestamp", -1)

            history_data = []
            for i, entry in enumerate(entries, start=1):
                ts = entry.get("timestamp")
                formatted_time = ts.strftime("%d %B %Y, %I:%M %p") if isinstance(ts, datetime) else "Unknown"

                history_data.append({
                    "S.No": i,
                    "Predicted Disease": entry.get("disease", "Unknown"),
                    "Description": entry.get("description", "Not Available"),
                    "Treatment": entry.get("treatment", "Not Available"),
                    "Health %": entry.get("health_percentage", "N/A"),
                    "Severity": entry.get("severity", "N/A")
                })

            if history_data:

                # Convert to DataFrame without index column
                df = pd.DataFrame(history_data).reset_index(drop=True)

                # Conditional styling function
                def style_func(val, col_name):
                    if col_name == "Health %":
                        if isinstance(val, (int, float)):
                            if val >= 80:
                                return "background-color: #d4edda;"  # green
                            elif val >= 50:
                                return "background-color: #fff3cd;"  # yellow
                            else:
                                return "background-color: #f8d7da;"  # red
                    elif col_name == "Severity":
                        severity_colors = {
                            "Low": "#d4edda",
                            "Moderate": "#fff3cd",
                            "High": "#f8d7da"
                        }
                        return f"background-color: {severity_colors.get(val, '#ffffff')}"
                    return ""

                styled_df = df.style.applymap(lambda val: style_func(val, "Health %"), subset=["Health %"])\
                                    .applymap(lambda val: style_func(val, "Severity"), subset=["Severity"])

                    # 🔽 Add this to hide the toolbar
                st.markdown("""
                    <style>
                        .stDataFrame div[data-testid="stDataFrameToolbar"] {
                            display: none !important;
                        }
                    </style>
                """, unsafe_allow_html=True)

                # Hide index here
                st.dataframe(styled_df, use_container_width=True, hide_index=True)

                # PDF download button
                pdf_data = generate_pdf(df)
                st.download_button(
                    label="Download as PDF",
                    data=pdf_data,
                    file_name="prediction_history.pdf",
                    mime="application/pdf"
                )
            else:
                st.info("No prediction history found.")

        display_history(st.session_state.username)
