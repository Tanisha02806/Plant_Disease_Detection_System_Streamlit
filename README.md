# 🌿 FloraScan

FloraScan is an intelligent plant health detection platform that enables users to upload or capture images of their plants to assess their condition. Leveraging advanced AI technology, the system analyzes the image in real time to detect signs of disease or confirm plant health. With a focus on early diagnosis and prevention, FloraScan empowers users to protect, treat, and care for their plants more effectively.

---

## 📌 Features

- 🌱 Detects diseases in major crops using image classification
- 🧠 Trained on a custom dataset with TensorFlow
- 📷 Preprocessed images using OpenCV
- 🌐 Interactive web UI with Streamlit
- 📊 Model evaluation metrics included
- 🧪 Tested with real-world images for accuracy

---

## 🖼️ Dataset

- Source: Custom collected dataset
- Number of Classes: 38
- Format: JPG/PNG images
- Preprocessing: Resizing, normalization, augmentation using OpenCV

---

## 🧠 Model Training

- Framework: TensorFlow / Keras
- Architecture: CNN (Convolutional Neural Network)
- Loss Function: `categorical_crossentropy`
- Optimizer: `adam`
- Epochs: *e.g., 30*
- Accuracy Achieved: *e.g., 92% on validation data*

---

## 🛠️ Tech Stack

| Component      | Technology        |
|----------------|-------------------|
| Image Processing | OpenCV            |
| Model Training   | TensorFlow / Keras|
| Web App          | Streamlit         |
| Language         | Python            |

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/YourUsername/Plant-Disease-Detection-System.git
cd Plant-Disease-Detection-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit App
```bash
streamlit run main.py
```

---

## 🖼️ How It Works

- Upload an image of the crop leaf.
- The app preprocesses it using OpenCV.
- The trained CNN model predicts the disease.
- The result and confidence score are displayed.

---

## 📁 Project Structure
```bash
Copy code
├── dataset/
│   └── [train, test folders]
├── model/
│   └── plant_disease_model.h5
├── app.py
├── utils.py
├── requirements.txt
├── README.md
```

---
