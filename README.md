# DermaLens 🧠🩺

<p align="center">
  <b>Domain-Aware Dermatology Image Enhancement & Validation Framework</b>
</p>

<p align="center">
  Selective preprocessing • AI confidence validation • Dermatology-focused image enhancement
</p>

---

## ✨ Overview

DermaLens is a **domain-aware dermatology image enhancement and validation framework** designed to improve image quality **without compromising downstream AI reliability**.

Unlike traditional preprocessing pipelines that blindly enhance every image, DermaLens applies **selective enhancement only when necessary** and validates whether the enhancement actually improves model confidence.

The system combines:

* 🔍 OpenCV-based image quality analysis
* 🤖 ResNet18-based confidence evaluation
* 📊 Validation-aware preprocessing logic

to study the relationship between **perceptual image enhancement** and **AI prediction reliability** in dermatology workflows.

---
<img width="1897" height="968" alt="image" src="https://github.com/user-attachments/assets/77e140fe-3885-42f4-b0d8-146cf0534069" />



# 🚨 Problem

Dermatology images captured in real-world telemedicine environments are often:

* blurry
* poorly illuminated
* noisy

Conventional enhancement pipelines apply aggressive preprocessing without validating whether the enhancement improves downstream AI performance.

This can:

* distort lesion textures
* alter color distributions
* reduce model reliability

---

# ✅ Solution

DermaLens introduces a **validation-aware preprocessing pipeline** that:

* analyzes image quality before enhancement
* applies minimal corrective enhancement only when required
* evaluates enhancement impact using a dermatology classifier
* compares model confidence before and after preprocessing

This ensures that enhancement improves **measurable AI reliability**, not just visual appearance.

---

# ⚙️ Pipeline

```text
Input Image
      ↓
Quality Analysis
(Sharpness • Brightness)
      ↓
Selective Enhancement
(if required)
      ↓
Dermatology Classifier
(ResNet18)
      ↓
Confidence Comparison
(Before vs After)
```

---

# 🧪 How It Works

### 1️⃣ User Upload

User uploads a dermatology image.

### 2️⃣ Quality Analysis

The system computes:

* sharpness (blur detection)
* brightness level
* contrast metrics

### 3️⃣ Adaptive Enhancement

Based on image quality:

* mild brightness correction OR
* light sharpening OR
* no enhancement

is selectively applied.

### 4️⃣ Model Evaluation

The system runs the dermatology classifier on:

* original image
* enhanced image

### 5️⃣ Confidence Validation

Confidence scores are compared to evaluate whether enhancement improved AI reliability.

### 6️⃣ Output

The frontend displays:

* enhanced image
* quality metrics
* enhancement mode
* confidence impact assessment

---

# 🧠 Key Insight

Higher image sharpness or visual quality does **not necessarily improve downstream AI performance**.

DermaLens demonstrates that aggressive enhancement can artificially inflate quality metrics while degrading clinically relevant information and reducing model confidence.

The framework therefore treats preprocessing as a **validated decision process** rather than a purely visual enhancement step.

---

# 🚀 Features

* 📸 Image upload and preview
* 🔍 Selective enhancement (non-destructive)
* 📊 Quality metrics

  * Sharpness
  * Contrast
  * Brightness
* 🧠 Blur & brightness-based decision logic
* 🤖 Model-based confidence validation
* ⚡ FastAPI backend
* 🎨 React + Vite frontend
* 🧪 Real-time preprocessing evaluation

---

# 🛠️ Tech Stack

| Layer            | Technologies              |
| ---------------- | ------------------------- |
| Frontend         | React, Vite, Tailwind CSS |
| Backend          | FastAPI (Python)          |
| Image Processing | OpenCV                    |
| Machine Learning | PyTorch, ResNet18         |
| Communication    | Axios                     |

---

# 📂 Project Structure

```text
backend/
│
├── app/
│   ├── ml/
│   │   ├── enhancement.py
│   │   ├── quality_analyzer.py
│   │   ├── evaluate_derm.py
│   │   ├── train_derm.py
│   │   └── derm_model.py
│   │
│   └── routes/
│       └── upload.py
│
frontend/
│
└── dermalens/
    └── src/
```

---

# ⚡ How to Run

## Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r ../requirements.txt

python -m uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend/dermalens

npm install

npm run dev
```

---

# 📈 Evaluation

The system evaluates preprocessing using:

* model confidence before enhancement
* model confidence after enhancement
* confidence delta comparison

### Example

```text
Original Confidence   → 0.80
Enhanced Confidence  → 0.83

Δ Confidence         → +0.03
Status               → Improvement
```

---

# 📌 Current Status

* ✔ Full adaptive preprocessing pipeline implemented
* ✔ Dermatology model training completed
* ✔ Enhancement logic stabilized
* ✔ Quality analysis integrated
* ✔ Confidence evaluation implemented
* ✔ Modern frontend dashboard completed

---

# ⚠️ Limitations

* Conservative enhancement produces modest improvements
* No paired real-world degraded dermatology dataset
* Potential distribution mismatch between training and real-world images
* Traditional sharpness metrics may overestimate enhancement quality

---

# 🔮 Future Improvements

* U-Net / GAN-based learned enhancement
* Adaptive threshold optimization
* Larger dermatology datasets
* Grad-CAM explainability
* Mobile deployment
* Telemedicine integration
* Real-time clinical validation

---

#  Author

### Stuti Katiyar ❤️
