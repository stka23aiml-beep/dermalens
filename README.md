# DermaLens 🧠🩺

<p align="center">
  <b>Domain-Aware Dermatology Image Enhancement & Validation Framework</b>
</p>

<p align="center">
  Adaptive image restoration • Quality-aware validation • Downstream AI analysis
</p>

---

## ✨ Overview

DermaLens is a **domain-aware dermatology image enhancement and validation framework** designed to improve degraded skin images before downstream abnormality analysis.

Real-world dermatology images may be captured using ordinary phone cameras and can contain:

- Low illumination
- Blur
- Motion artifacts
- Sensor noise
- Compression artifacts
- Poor contrast
- Limited image resolution

Instead of applying a fixed preprocessing operation to every image, DermaLens analyzes the input image and generates **multiple enhancement candidates**.

Each candidate is evaluated using image-quality and preservation metrics before the system selects the most suitable result.

The goal is not simply to make an image look sharper.

> **The goal is to make the image clearer while preserving the visual structures and information present in the original image.**

---

## 🚨 Problem

Dermatology images collected outside controlled imaging environments can vary significantly in quality.

A downstream AI model may receive an image that is:

- Too dark
- Blurry
- Noisy
- Low contrast
- Compressed
- Captured at insufficient resolution

Traditional preprocessing pipelines often apply the same transformation regardless of image quality.

Aggressive enhancement can introduce problems such as:

- Artificial textures
- False edges
- Color shifts
- Noise amplification
- Loss of subtle structures
- Over-sharpening

Therefore:

> **Higher numerical sharpness does not necessarily mean a better dermatology image.**

DermaLens treats enhancement as a **validation problem**, rather than a simple image-processing problem.

---

## ✅ Solution

DermaLens uses an adaptive candidate-based enhancement pipeline.

Instead of immediately modifying the uploaded image, the system:

1. Analyzes the original image.
2. Detects relevant quality problems.
3. Generates appropriate enhancement candidates.
4. Measures the effect of each candidate.
5. Rejects candidates that introduce excessive distortion.
6. Selects the best valid candidate.
7. Preserves the original image when no candidate provides a sufficiently safe improvement.
8. Passes the resulting image to downstream abnormality analysis.

---

## ⚙️ System Architecture

```text
                         USER IMAGE
                             │
                             ▼
                  ┌─────────────────────┐
                  │   QUALITY ANALYSIS  │
                  │                     │
                  │ • Brightness        │
                  │ • Sharpness / Blur  │
                  │ • Contrast          │
                  │ • Noise             │
                  └──────────┬──────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │  CANDIDATE GENERATION  │
                 │                        │
                 │ • Brightness correction│
                 │ • Contrast enhancement │
                 │ • Noise reduction      │
                 │ • Super-resolution     │
                 │ • Real-ESRGAN          │
                 │ • EDSR                 │
                 └───────────┬────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   VALIDATION LAYER   │
                  │                      │
                  │ • Quality improvement│
                  │ • Exposure change    │
                  │ • Noise change       │
                  │ • Structural similarity
                  │ • Color shift        │
                  │ • Sharpness change   │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ BEST VALID CANDIDATE │
                  │                      │
                  │ Enhanced image       │
                  │ OR                   │
                  │ Original image       │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ DOWNSTREAM ANALYSIS  │
                  │                      │
                  │ Lesion → ISIC model │
                  │ Wound  → future     │
                  │ Other  → future     │
                  └──────────────────────┘
```

---

## 🧪 How It Works

### 1️⃣ Image Upload

The user uploads a dermatology image.

The application accepts common image formats and sends the image to the FastAPI backend for quality analysis and preprocessing.

The enhancement layer is designed to work with both:

* Curated dermatology datasets such as ISIC
* Real-world images captured using ordinary cameras

The preprocessing system does not assume that every image has the same quality characteristics.

---

### 2️⃣ Quality Analysis

The original image is analyzed before enhancement.

Current measurements include:

#### Brightness

Measures the average illumination level of the image.

Brightness is used to identify images that may require illumination correction.

#### Sharpness

Sharpness is estimated using the **variance of the Laplacian**.

A low Laplacian variance generally indicates a blurry image.

#### Contrast

Contrast measures intensity variation within the image.

Low contrast can indicate weak visual separation between image regions.

#### Noise

Noise characteristics are evaluated during candidate comparison to determine whether an enhancement operation introduces excessive noise.

---

### 3️⃣ Adaptive Candidate Generation

DermaLens does not blindly apply a single enhancement operation to every image.

Instead, the pipeline generates enhancement candidates according to the detected image characteristics.

Possible enhancement operations include:

#### Brightness Enhancement

Low-light images can undergo adaptive illumination correction using LAB color-space processing and gamma adjustment.

#### Contrast Enhancement

Images with insufficient contrast can undergo controlled contrast enhancement.

#### Noise Reduction

Noise reduction can be applied when image noise is detected.

The resulting candidate is then evaluated to determine whether the reduction in noise comes at the cost of important image structure.

#### Super Resolution

DermaLens supports AI-assisted super-resolution processing.

Current models include:

* **Real-ESRGAN**
* **EDSR**

The pipeline can use adaptive full-resolution processing when CPU constraints make direct EDSR processing impractical for the input image size.

---

### 4️⃣ Candidate Validation

Candidate generation alone is not enough.

Every candidate must be evaluated against the original image.

The validation layer currently considers factors such as:

```text
Quality improvement
Exposure improvement
Sharpness change
Noise change
Structural similarity
Color shift
```

This prevents the system from automatically selecting an image simply because it has a higher numerical sharpness score.

For example:

```text
Candidate A

Sharpness       ↑
Contrast        ↑
Noise           ↑↑
Structure       ↓

→ Rejected
```

while:

```text
Candidate B

Brightness      ↑
Sharpness       ↑
Noise           ≈
Structure       ≈
Color shift     Low

→ Potentially accepted
```

The objective is **controlled improvement**, not maximum enhancement.

---

### 5️⃣ Best Candidate Selection

After candidate validation, DermaLens selects the highest-scoring valid candidate.

If none of the generated candidates satisfies the validation criteria, the original image is preserved.

```text
Enhanced candidates
        │
        ▼
Validation checks
        │
        ├── Valid candidate → Select best candidate
        │
        └── No valid candidate
                    │
                    ▼
             Preserve original
```

This creates a safety-oriented fallback mechanism.

The system therefore does not force an enhancement onto an image when the enhancement cannot demonstrate sufficient benefit.

---

### 6️⃣ Downstream AI Validation

After preprocessing, DermaLens can evaluate the resulting image using a dermatology classifier.

The current implementation uses a **ResNet18-based dermatology model**.

The model can be evaluated on both the original and enhanced images.

```text
Original Image
      │
      ▼
ResNet18
      │
      ▼
Prediction + Confidence


Enhanced Image
      │
      ▼
ResNet18
      │
      ▼
Prediction + Confidence
```

The system can then compare the resulting confidence values.

Example:

```text
Original Confidence  → 0.80
Enhanced Confidence  → 0.83

Confidence Delta      → +0.03
```

Model confidence is treated as a **downstream validation signal**, not as the sole definition of image quality.

A higher confidence score does not automatically mean that an enhancement is clinically correct.

---

## 🧠 Core Design Principle

DermaLens is built around the following principle:

> **Image enhancement should improve usability without unnecessarily changing the underlying visual information.**

A visually sharper image can still be worse if it introduces:

* Artificial patterns
* False lesion boundaries
* Incorrect pigmentation
* Synthetic textures
* Excessive noise
* Significant color distortion

Therefore:

```text
Higher Sharpness
        ≠
Better Dermatology Image
```

Similarly:

```text
Higher Model Confidence
        ≠
Clinical Correctness
```

DermaLens therefore evaluates enhancement using multiple signals rather than relying on a single metric.

---

## 🚀 Features

* 📸 Dermatology image upload
* 🔍 Automatic image-quality analysis
* 🌙 Low-light detection and correction
* 🌫️ Blur detection
* 🎚️ Contrast analysis
* 🧹 Noise analysis
* 🤖 Adaptive enhancement candidates
* 🧠 Real-ESRGAN super resolution
* 🧠 EDSR super resolution
* 🛡️ Enhancement validation
* 📊 Before/after quality comparison
* 🧩 Structural preservation checks
* 🎨 Color-shift monitoring
* 🔄 Original-image safety fallback
* 🧠 ResNet18 downstream confidence evaluation
* ⚡ FastAPI backend
* 🎨 React + Vite frontend
* ✨ Animated AI processing interface
* 📱 Responsive web interface

---

## 🛠️ Tech Stack

| Layer             | Technologies                             |
| ----------------- | ---------------------------------------- |
| Frontend          | React, Vite, Tailwind CSS, Framer Motion |
| Backend           | FastAPI, Python                          |
| Image Processing  | OpenCV, NumPy                            |
| Machine Learning  | PyTorch                                  |
| Dermatology Model | ResNet18                                 |
| Super Resolution  | Real-ESRGAN, EDSR                        |
| API Communication | Fetch / Axios                            |

---

## 📂 Project Structure

```text
dermalens/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── ml/
│   │   │   ├── degrade.py
│   │   │   ├── derm_model.py
│   │   │   ├── enhancement.py
│   │   │   ├── evaluate.py
│   │   │   ├── evaluate_derm.py
│   │   │   ├── generate_comparison_figure.py
│   │   │   ├── inference.py
│   │   │   ├── make_bad_images.py
│   │   │   ├── metrics.py
│   │   │   ├── pipeline.py
│   │   │   ├── prepare_data.py
│   │   │   ├── quality_analyzer.py
│   │   │   ├── superres_enhancer.py
│   │   │   ├── train_derm.py
│   │   │   │
│   │   │   ├── models/
│   │   │   │   └── isic_resnet18.pth
│   │   │   │
│   │   │   ├── realesrgan_weights/
│   │   │   │   └── realesr-general-x4v3.pth
│   │   │   │
│   │   │   └── weights/
│   │   │       └── EDSR_x2.pb
│   │   │
│   │   └── routes/
│   │       └── upload.py
│   │
│   ├── requirements.txt
│   └── test_realesrgan.py
│
└── frontend/
    │
    └── dermalens/
        │
        ├── src/
        │   ├── api/
        │   │   └── api.js
        │   │
        │   ├── assets/
        │   │   ├── hero.png
        │   │   ├── react.svg
        │   │   └── vite.svg
        │   │
        │   ├── components/
        │   │   ├── AIOrb.jsx
        │   │   ├── AIProcessing.jsx
        │   │   ├── BackgroundGlow.jsx
        │   │   ├── HeroSection.jsx
        │   │   ├── MetricsCard.jsx
        │   │   ├── Navbar.jsx
        │   │   ├── ResultSection.jsx
        │   │   ├── UploadBox.jsx
        │   │   └── UploadSection.jsx
        │   │
        │   ├── pages/
        │   │   └── Home.jsx
        │   │
        │   ├── App.css
        │   ├── App.jsx
        │   ├── index.css
        │   └── main.jsx
        │
        ├── package.json
        └── vite.config.js
```

---

## ⚡ How to Run

### Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS / GitHub Codespaces

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

---

### Frontend

Navigate to the frontend:

```bash
cd frontend/dermalens
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The Vite development server will start on the configured development port.

---

## 📊 Evaluation

DermaLens evaluates enhancement using multiple image-level signals.

### Image Quality

* Brightness
* Sharpness
* Contrast
* Noise
* Overall quality score

### Preservation

* Structural similarity
* Color shift
* Exposure change
* Noise change

### Downstream AI Evaluation

* Prediction before enhancement
* Prediction after enhancement
* Confidence before enhancement
* Confidence after enhancement
* Confidence delta

---

## 🧪 Example Evaluation

An example low-quality input may produce results such as:

```text
Original
────────────────────────────

Brightness       → 58.32
Sharpness        → 4.74
Contrast         → 6.89


Selected Candidate
────────────────────────────

Brightness       → 87.64
Sharpness        → 8.54
Contrast         → 8.28
Structure        → 0.995
```

The system can then evaluate the downstream model:

```text
Confidence Before → 0.768
Confidence After  → 0.794

Δ Confidence      → +0.026
```

The exact values depend on the uploaded image.

---

## 🔬 Validation Philosophy

DermaLens deliberately avoids treating a single metric as the ground truth.

For example, a candidate may produce:

```text
Sharpness ↑↑
```

but simultaneously:

```text
Noise ↑↑
Color Shift ↑
Structure Similarity ↓
```

Such a candidate should not automatically be considered better.

The framework therefore attempts to balance:

```text
Image Quality
      +
Information Preservation
      +
Downstream Model Behavior
```

rather than optimizing only for visual sharpness.

---

## 🩺 Future Abnormality Analysis

The long-term architecture separates **image preparation** from **abnormality analysis**.

The enhancement layer can prepare an image without needing to know which abnormality is present.

The downstream analysis layer can then route the image to an appropriate specialized model.

```text
                         Skin Image
                             │
                             ▼
                    ┌─────────────────┐
                    │    DermaLens    │
                    │ Enhancement +   │
                    │   Validation    │
                    └────────┬────────┘
                             │
                             ▼
                    Abnormality Analysis
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
           Lesion          Wound          Other
              │              │              │
              ▼              ▼              ▼
         ISIC Model      Future Model    Future Model
```

This architecture allows the preprocessing framework to remain independent from individual abnormality classifiers.

---

## ⚠️ Limitations

DermaLens is currently a **research and prototype framework**, not a clinically validated diagnostic system.

Important limitations include:

* No paired real-world degraded/clean dermatology dataset
* Potential distribution mismatch between curated datasets and real-world phone-camera images
* Traditional image-quality metrics may not perfectly represent perceptual or clinical quality
* Super-resolution models may introduce synthetic details
* Model confidence is not equivalent to clinical correctness
* Current downstream classification coverage is limited
* Wound/cut abnormality analysis is not yet integrated
* No clinical expert validation has been performed
* No prospective clinical evaluation has been performed

Therefore, DermaLens should **not be used as a standalone diagnostic system**.

---

## 🔮 Future Improvements

### Enhancement

* Learned image-quality assessment
* Domain-specific enhancement models
* Improved motion-blur restoration
* Compression-artifact correction
* Better low-light restoration
* Adaptive enhancement threshold optimization
* Paired dermatology degradation datasets
* Domain-specific super-resolution models

### Evaluation

Planned evaluation metrics include:

* PSNR
* SSIM
* LPIPS
* Perceptual quality evaluation
* Human expert evaluation
* Cross-camera robustness testing
* Cross-lighting-condition evaluation

PSNR and SSIM are particularly useful when paired reference images are available.

For unpaired real-world images, perceptual and preservation-based evaluation will be more appropriate.

### Explainability

* Grad-CAM
* Lesion localization
* Abnormality-region highlighting
* Model uncertainty visualization
* Enhancement-region visualization

### Abnormality Analysis

* Specialized lesion classification
* Wound/cut classification
* Other skin abnormality models
* Multi-model routing
* Abnormality localization

### Deployment

* Mobile inference
* Edge deployment
* Telemedicine integration
* Real-time camera processing
* Lightweight model optimization

---

## 🎯 Project Goal

DermaLens investigates a fundamental problem in medical AI:

> **Can degraded medical images be improved before AI analysis without introducing changes that make the image less trustworthy?**

Instead of treating preprocessing as a fixed sequence of filters, DermaLens treats it as a **decision-making and validation layer between image acquisition and downstream AI analysis**.

```text
              IMAGE ACQUISITION
                     │
                     ▼
             ┌───────────────┐
             │   DermaLens   │
             │               │
             │ Quality       │
             │ Analysis      │
             │      ↓        │
             │ Enhancement   │
             │      ↓        │
             │ Validation    │
             └───────┬───────┘
                     │
                     ▼
             ABNORMALITY ANALYSIS
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        Lesion      Wound      Other
```

---

## 📌 Current Status

### Implemented

* ✔ Image upload and preprocessing API
* ✔ Image-quality analysis
* ✔ Brightness analysis and correction
* ✔ Blur/sharpness detection
* ✔ Contrast analysis
* ✔ Noise analysis
* ✔ Adaptive enhancement pipeline
* ✔ Candidate generation
* ✔ Candidate validation
* ✔ Quality-based candidate selection
* ✔ Original-image safety fallback
* ✔ ResNet18 dermatology model
* ✔ Real-ESRGAN integration
* ✔ EDSR integration
* ✔ Downstream confidence comparison
* ✔ Enhancement acceptance/rejection logic
* ✔ FastAPI backend
* ✔ React + Vite frontend
* ✔ Animated AI processing interface
* ✔ Before/after result interface
* ✔ Enhancement metrics display
* ✔ Model weights integrated into the project

### In Progress

* 🚧 Improved result visualization
* 🚧 Image quality analysis panel
* 🚧 Compare / zoom interaction
* 🚧 Quality-change visualization
* 🚧 Downstream abnormality analysis workflow

### Planned

* 🔮 PSNR / SSIM evaluation
* 🔮 LPIPS evaluation
* 🔮 Wound/cut analysis
* 🔮 Additional abnormality models
* 🔮 Grad-CAM explainability
* 🔮 Real-world dataset evaluation
* 🔮 Clinical expert evaluation
* 🔮 Mobile / edge deployment

---

## 👩‍💻 Author

### Stuti Katiyar

Engineering • AI/ML • Computer Vision

---

<p align="center">
  <b>DermaLens — Enhance carefully. Validate before trusting.</b>
</p>