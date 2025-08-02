import streamlit as st
import tensorflow as tf
import numpy as np
from fpdf import FPDF
import base64
import datetime
import re
import os
import json
import pandas as pd
from datetime import datetime

HISTORY_FILE = "prediction_history.json"

# ⛑️ Sanitize text for PDF
def remove_unicode(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# 🧠 Model prediction
def model_prediction(test_image):
    model = tf.keras.models.load_model('trained_model.h5')
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=(128, 128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    prediction = model.predict(input_arr)
    return np.argmax(prediction)

# 📄 Get disease info
def get_disease_info(disease_name):
    try:
        with open("full_plant_disease_info.txt", "r", encoding="utf-8") as file:
            content = file.read()
            diseases = content.split("=" * 70)
            for disease in diseases:
                if disease_name.strip() in disease:
                    return disease.strip()
    except Exception as e:
        return f"Error loading disease information: {e}"
    return "Disease information not found."

# 📄 PDF Generator
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font("Arial", size=12)

def generate_pdf(disease_name, disease_details):
    pdf = PDF()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Plant Disease Prediction Report", ln=True, align="C")

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Disease: {disease_name}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", '', 11)
    clean_text = remove_unicode(disease_details)
    for line in clean_text.split("\n"):
        pdf.multi_cell(0, 8, line)

    pdf_dir = "pdf"
    os.makedirs(pdf_dir, exist_ok=True)
    
    #save in pdf folder
    pdf_path = os.path.join(pdf_dir, f"{disease_name.replace(' ', '_')}_report.pdf")
    pdf.output(pdf_path)
    return pdf_path

# 📁 History management
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(disease_name, pdf_path):
    history = load_history()
    entry = {
        "disease_name": disease_name,
        "pdf_path": pdf_path,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Home"
    
#  Sidebar
st.sidebar.title("Dashboard")
st.session_state.app_mode = st.sidebar.selectbox(
    "Select Page", ["Home", "About", "Disease Recognition", "History", "Profile"],
    index=["Home", "About", "Disease Recognition", "History", "Profile"].index(st.session_state.app_mode)
)
app_mode = st.session_state.app_mode

# 🏠 Home
if app_mode == "Home":
    st.set_page_config(page_title="Plant Disease Recognition", layout="wide")

    # 🌿 Custom green-themed style
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
        }
        .metric-label, .stMarkdown {
            font-family: "Segoe UI", sans-serif;
        }
        .metric-box {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 0.75rem;
            text-align: center;
            box-shadow: 2px 2px 10px rgba(0, 100, 0, 0.1);
            border: 2px solid #c8e6c9;
            font-family: 'Segoe UI', sans-serif;
        }
        .highlight-box {
            background-color: #f0fff0;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #d0e9d0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            color: #2e7d32;
        }
        .testimonial {
            background-color: #fff8e1;
            padding: 1rem;
            border-left: 4px solid #ffb300;
            margin-bottom: 1rem;
            font-style: italic;
            color: #BDB76B;
        }
        </style>
    """, unsafe_allow_html=True)

    # 🌾 Hero Section
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("img/midimage.png", width=300)

    st.markdown("""
    <h2 style='text-align: center; color: #2e7d32;'>Welcome to the <i>Plant Disease Recognition System</i> </h2>
    <p style='text-align: center;'>Empowering farmers and researchers with fast, AI-powered plant disease diagnosis and actionable insights.</p>
    """, unsafe_allow_html=True)

    # 📊 Stats
    history = load_history()
    total_predictions = len(history)
    most_common = pd.DataFrame(history)['disease_name'].mode()[0] if history else "N/A"

    st.markdown("### 📈 System Usage Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Predictions Made", total_predictions)
    with col2:
        st.metric("🧬 Most Common Disease", most_common)
    with col3:
        st.metric("📄 Reports Generated", total_predictions)

    st.markdown("---")

    # 🚀 Features
    st.subheader("🚜 Why Farmers & Researchers Use Our System")
    feat1, feat2, feat3, feat4 = st.columns(4)
    with feat1:
        st.success("🤖 AI Disease Detection")
    with feat2:
        st.success("📊 87K+ Image Training")
    with feat3:
        st.success("📄 Instant PDF Reports")
    with feat4:
        st.success("🌱 38+ Crop Diseases")

    st.markdown("---")

    # 📸 How It Works
    st.subheader("📸 How It Works")
    st.markdown("""
    <div class='highlight-box'>
    
    - Upload a clear leaf image of the affected plant.
    
    - AI analyzes the image using deep learning.
    
    - Get diagnosis including symptoms, causes, treatment & prevention.
    
    - Download PDF report to save, print, or share.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 💬 Testimonials
    st.subheader("💬 What People Are Saying")
    st.markdown("""
    <div class='testimonial'>
        "This system helped me identify a disease in my tomato plants within minutes!"  
        – 🌱 Happy Farmer
    </div>
    <div class='testimonial'>
        "The PDF report was a game changer for my research."  
        – 🔬 Plant Scientist
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 🚀 CTA Button
    st.markdown("### 👇 Ready to diagnose your plant?")
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🔍 Start Diagnosis"):
            st.session_state.app_mode = "Disease Recognition"
            st.rerun()

    # 📬 Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; font-size: 0.9rem; color: gray;'>
        📬 Contact: <a href='mailto:chakudi@example.com'>chakudi@example.com</a>  
        • <a href='https://github.com/' target='_blank'>GitHub</a>  
        • <a href='https://linkedin.com/' target='_blank'>LinkedIn</a>
    </div>
    """, unsafe_allow_html=True)



# ℹ️ About
elif app_mode == "About":
    st.header("About")
    st.markdown("""
    ### Dataset Summary
    Trained on 87,000+ RGB images across 38 disease classes using offline augmentation.

    - **Train Set:** 70,295 images  
    - **Validation Set:** 17,572 images  
    - **Test Set:** 33 images
""")

# 🔍 Disease Recognition
elif app_mode == "Disease Recognition":
    st.header("🌿 Disease Recognition")

    # 🌱 Green Theme CSS
    st.markdown("""
        <style>
        .predict-box {
            background-color: #ffffff;
            border-left: 5px solid #66bb6a;
            padding: 1.5rem;
            margin-top: 1rem;
            border-radius: 10px;
            box-shadow: 1px 1px 8px rgba(0, 100, 0, 0.08);
            font-family: 'Segoe UI', sans-serif;
            color: #2e7d32;
        }
        .result-header {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1b5e20;
            margin-bottom: 0.75rem;
        }
        .result-disease {
            font-size: 1.8rem;
            font-weight: bold;
            color: #388e3c;
        }
        .streamlit-expanderHeader {
            font-size: 1.1rem !important;
            color: #2e7d32 !important;
            font-weight: 600 !important;
        }
        .download-btn button {
            background-color: #66bb6a;
            color: white;
            border: none;
            font-weight: bold;
        }
        .download-btn button:hover {
            background-color: #558b2f;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    # 🌿 Upload or Capture Image
    st.subheader("📤 Upload or 📷 Capture a Plant Leaf Image")
    # 📁 Upload section
    test_image = st.file_uploader("Upload an Image (JPG/PNG)", type=["jpg", "jpeg", "png"])

    # 📷 Camera section (shown after upload for optional capture)
    camera_input = st.camera_input("Or Capture Image with Camera")

    # Decide which image to use (priority to uploaded image)
    final_image = test_image if test_image is not None else camera_input

    # Show Image
    if st.button("🖼️ Show Image") and final_image:
        st.image(final_image, width=300, caption="Selected/Captured Leaf Image")

    # Predict Button
    if st.button("🔬 Predict"):
        if final_image is not None:
            with st.spinner("🔎 Analyzing image..."):
                result_index = model_prediction(final_image)

                class_name = [
                    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
                    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
                    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
                    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot',
                    'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
                    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
                    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
                    'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
                    'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
                    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight',
                    'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
                    'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
                    'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
                ]

                predicted_disease = class_name[result_index]

                # 🌱 Prediction Box
                st.markdown(f"""
                    <div class="predict-box">
                        <div class="result-header">Prediction:</div>
                        <div class="result-disease">{predicted_disease}</div>
                    </div>
                """, unsafe_allow_html=True)

                # 🧬 Disease Info
                disease_details = get_disease_info(predicted_disease)
                with st.expander("🧾 View Detailed Disease Information", expanded=True):
                    st.markdown(disease_details.replace("\n", "  \n"))

                # 📄 PDF Generation
                pdf_path = generate_pdf(predicted_disease, disease_details)
                save_history(predicted_disease, pdf_path)

                # 📥 Styled Download Button
                with open(pdf_path, "rb") as f:
                    st.markdown("<div class='download-btn'>", unsafe_allow_html=True)
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=f,
                        file_name=f"{predicted_disease}_report.pdf",
                        mime="application/pdf"
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please upload or capture an image before predicting.")


# 📜 History Page
elif app_mode == "History":
    st.header("🕓 Prediction History")
    
    #clear button at the top-right
    colA, colB = st.columns([6, 1])
    with colB:
        if st.button("Clear History"):
            clear_history()
            st.rerun()
            
    history = load_history()
    if not history:
        st.info("No prediction history found.")
    else:
        df = pd.DataFrame(history)
        for i, row in df.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(f"**{row['disease_name']}**")
            col2.write(row["date"])
            if os.path.exists(row["pdf_path"]):
                with open(row["pdf_path"], "rb") as f:
                    col3.download_button(
                        label="📄 Download Report",
                        data=f,
                        file_name=os.path.basename(row["pdf_path"]),
                        mime="application/pdf",
                        key=f"download_{i}"
                    )
            else:
                col3.error("PDF not found")

# Profile Page
elif app_mode == "Profile":
    st.header("👤 Profile")

    # Left: Profile image | Right: Profile info
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("img/default_pfp.jpg", width=150, caption="Your Profile", use_container_width=False)

    with col2:
        st.subheader("Chakudi")  # Replace with dynamic username if available
        st.markdown("""
        - **Email:** chakudi@example.com  
        - **Role:** Engineering Student  
        - **Institution:** Example Institute of Technology  
        - **Account Created:** August 2025  
        """)
        st.success("✅ Profile details loaded successfully")

    st.markdown("---")

    st.subheader("Account Settings")
    st.info("Feature under development — profile editing and security settings coming soon!")

    # Optional: layout for future editable fields
    # st.text_input("Name", value="Chakudi", disabled=True)
    # st.text_input("Email", value="chakudi@example.com", disabled=True)
    # st.text_input("Institution", value="Example Institute", disabled=True)
    # st.text_input("Role", value="Engineering Student", disabled=True)