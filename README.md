# 🌿 Plant Disease Recognition System

An AI-powered **plant disease detection web application** built with **Streamlit**, **TensorFlow (Keras)**, and **FPDF**.
This system allows farmers, researchers, and agriculture enthusiasts to **upload or capture leaf images**, detect plant diseases using a trained CNN model, and **download detailed PDF reports**.
It also keeps a **prediction history** and includes a **feedback submission feature**.

---

## 📌 Features

* **AI Disease Detection** – Detects plant diseases from leaf images using a deep learning model.
* **Image Input Options** – Upload from your device or capture directly using your camera.
* **Detailed Disease Information** – Displays symptoms, causes, treatment, and prevention steps.
* **Instant PDF Reports** – Generates downloadable reports for offline use.
* **Prediction History** – Stores and retrieves past diagnoses with report downloads.
* **Excel Export** – Export your full history as an Excel file.
* **Feedback Submission** – Send feedback via Gmail directly from the app.
* **Custom UI Theme** – Modern green-themed responsive design.

---

## 📂 Project Structure

```
.
├── trained_model.h5                  # Trained Keras model
├── full_plant_disease_info.txt        # Disease details text file
├── prediction_history.json            # JSON file for saving history
├── pdf/                               # Generated PDF reports
├── img/                               # UI images (e.g., midimage.png)
├── main.py                             # Main Streamlit app script
└── README.md                          # Project documentation
```

---

## 🛠️ Technologies Used

* **Python 3.9+**
* **Streamlit** – Web app framework
* **TensorFlow / Keras** – Deep learning model
* **NumPy** – Numerical processing
* **Pandas** – Data manipulation & history export
* **FPDF** – PDF generation
* **OpenCV (optional)** – Image preprocessing (if extended)
* **Matplotlib (optional)** – For future data visualizations

---

## ⚙️ Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/plant-disease-recognition.git
   cd plant-disease-recognition
   ```

2. **Create and Activate Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate     # For Linux/Mac
   venv\Scripts\activate        # For Windows
   ```

3. **Install Required Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Add Model & Assets**

   * Place your **`trained_model.h5`** in the root directory.
   * Add **`full_plant_disease_info.txt`** with all disease descriptions.
   * Ensure an `img` folder exists with **`midimage.png`** for the home screen.

---

## 🚀 Running the Application

Run the Streamlit app:

```bash
streamlit run main.py
```

The app will open in your browser at:

```
http://localhost:8501
```

---

## 📖 Usage Guide

### **1. Home Page**

* Overview of the system, stats, and features.
* Button to navigate to **Disease Recognition**.

### **2. Disease Recognition**

* Upload or capture a plant leaf image.
* Click **Predict** to run AI detection.
* View disease details in an expandable section.
* Download the generated **PDF Report**.

### **3. History**

* View previous predictions.
* Search by disease name or date.
* Download previous reports.
* Export all history to **Excel**.
* Clear all history if needed.

### **4. Feedback**

* Enter your name, email, rating, and comments.
* Automatically opens Gmail with pre-filled feedback.

---

## 📑 PDF Report Structure

Each PDF contains:

* Disease name
* Date & time of detection
* Detailed disease description (sanitized for PDF format)

---

## 📊 Model Information

* **Architecture:** CNN (Convolutional Neural Network)
* **Training Dataset:** PlantVillage Dataset (87K+ images, 38+ plant diseases)
* **Input Size:** 128×128 pixels
* **Output:** Disease class index mapped to plant disease name

---

## 📜 Requirements File Example

Create a `requirements.txt` file with:

```
streamlit
tensorflow
numpy
pandas
fpdf
openpyxl
```

---

## 👩‍💻 Author

**Tanisha Thakur**
📧 Email: [tanishaselfthakur@gmail.com](mailto:tanishaselfthakur@gmail.com)
