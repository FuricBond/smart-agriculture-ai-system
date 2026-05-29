<div align="center">

  <h1>🌾 Smart Agriculture AI System</h1>
  <h3>AI-Based Crop Health & Yield Prediction with Advisory Support</h3>
  <p>An intelligent, ML-powered platform that empowers farmers with data-driven agronomic decisions — from disease diagnosis to harvest forecasting.</p>

  <br/>

  <!-- Tech Stack Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" alt="Node.js" />
    <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch" />
    <img src="https://img.shields.io/badge/XGBoost-FF6600?style=for-the-badge&logo=xgboost&logoColor=white" alt="XGBoost" />
    <img src="https://img.shields.io/badge/Gemini_AI-1A73E8?style=for-the-badge&logo=google&logoColor=white" alt="Gemini AI" />
  </p>

  <!-- Status Badges -->
  <p>
    <img src="https://img.shields.io/badge/status-active-brightgreen?style=flat-square" alt="Status" />
    <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License" />
    <img src="https://img.shields.io/badge/platform-web-lightgrey?style=flat-square" alt="Platform" />
  </p>

</div>

---

## 📖 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [System Architecture](#️-system-architecture)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Datasets](#️-datasets)
- [Installation & Setup](#-installation--setup)
- [How to Use](#️-how-to-use)
- [Team Contributions](#-team-contributions)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## 🌐 Project Overview

The **Smart Agriculture AI System** is a full-stack, AI-powered platform designed to modernize farming practices through data intelligence. By integrating deep learning, ensemble machine learning, and generative AI, the system helps farmers make precision-driven agronomic decisions.

**Core problem this solves:** Farmers lack timely, affordable access to agronomic expertise. Late disease diagnosis, wrong crop selection, and yield uncertainty lead to massive losses. This system provides an on-demand AI advisor that processes soil data, leaf images, and historical climate records to deliver actionable recommendations in real time.

**What makes it unique:**
- End-to-end pipeline from raw farm data → AI inference → generative advisory
- Three independent ML models (Vision CNN, Ensemble Classifier, XGBoost Regressor) unified under a single API
- Augmented with **Google Gemini LLM** for human-readable, context-aware farming advice
- A sleek, production-quality React dashboard with multi-language support

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔬 **AI Disease Detection** | Upload a leaf image → EfficientNet CNN identifies crop disease with Grad-CAM heatmap explanations |
| 🌱 **Crop Recommendation** | Input soil (N, P, K, pH) & climate data → Soft-voting ensemble recommends the top 3 crops |
| 🧠 **Gemini Advisory** | Google Gemini LLM generates fertilizer dosing, biological prevention, and irrigation advice |
| 💬 **Farm AI Chatbot** | Conversational assistant powered by Gemini for open-ended farming Q&A |
| 📈 **Yield Forecasting** | Input area, crop, & year → XGBoost regression predicts harvest density (hg/ha) |
| 🛡️ **Confidence Guards** | AI flags low-confidence predictions to prevent risky agronomic decisions |
| 🌍 **Multi-Language UI** | Frontend supports internationalization (i18n) via react-i18next |
| 📊 **Interactive Charts** | Recharts-powered visualizations of yield trends and recommendation scores |

---

## 🏗️ System Architecture

The application follows a clean, decoupled full-stack architecture designed for high performance and scalability:

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (:3000)                    │
│      (Dashboard UI, Multi-Language, Interactive Charts)     │
└──────────────────────────┬──────────────────────────────────┘
                           │ 
                           │ HTTP / REST (JSON & FormData)
                           │ 
┌──────────────────────────▼──────────────────────────────────┐
│               Python FastAPI ML Server (:8000)               │
│      (Model Inference, Gemini Integration, Validation)       │
├─────────────────┬─────────────────────┬─────────────────────┤
│ Disease Engine  │   Crop Engine        │   Yield Engine      │
│ (EfficientNet)  │ (Voting Ensemble)    │ (XGBoost Regressor) │
└─────────────────┴─────────────────────┴─────────────────────┘
```

**Data Flow:**
1. User inputs farm data (leaf image / soil values / area details) via the **React Dashboard**
2. The dashboard makes direct REST API requests to the **FastAPI ML Server**
3. The server validates incoming payloads and routes requests to the appropriate engine in `smart_system/`
4. Core machine learning predictions are augmented with **Google Gemini LLM** advisory recommendations
5. The unified JSON response (with Grad-CAM heatmaps, top recommendations, and risks) is returned and rendered on the dashboard


---

## 📂 Project Structure

```text
CropProject/
│
├── ai_api/                     # 🐍 Python FastAPI ML inference server
│   ├── api.py                  #    Main FastAPI application & all endpoints
│   ├── smart_system/           #    Embedded ML engines (symlinked/shared)
│   └── .env                    #    API keys (Gemini, etc.) — not committed
│
├── smart_system/               # 🧠 Core AI orchestration & inference engines
│   ├── disease_engine.py       #    EfficientNet image classification
│   ├── crop_engine.py          #    Soil & climate ensemble predictor
│   ├── yield_engine.py         #    XGBoost regression forecaster
│   ├── ensemble_engine.py      #    Unified multi-model prediction pipeline
│   ├── gemini_advisor.py       #    Google Gemini LLM advisory integration
│   ├── farm_ai_assistant.py    #    Conversational chatbot handler
│   ├── recommendations.py      #    Rule-based agronomic advisory logic
│   ├── risk_analysis.py        #    Risk scoring & confidence evaluation
│   ├── smart_predict.py        #    End-to-end prediction orchestration
│   ├── report.py               #    Report generation utilities
│   ├── evaluation.py           #    Model evaluation & metrics
│   ├── config.py               #    Global system configuration
│   └── logger.py               #    Structured runtime logging
│
├── disease_model/              # 🦠 Disease detection training pipeline (PyTorch)
│   ├── data/                   #    Raw image datasets (PlantVillage, etc.)
│   ├── data_prep/              #    Preprocessing & augmentation scripts
│   ├── models/                 #    Saved model weights (.pt files)
│   ├── scripts/                #    Training, evaluation, Grad-CAM scripts
│   └── reports/                #    Training metrics & confusion matrices
│
├── crop_model/                 # 🌿 Crop recommendation training pipeline (Scikit-Learn)
│   ├── data/                   #    Soil & climate CSV datasets
│   ├── data_prep/              #    Feature engineering & normalization
│   ├── models/                 #    Saved ensemble model artifacts (.pkl)
│   ├── scripts/                #    Training, tuning & validation scripts
│   └── reports/                #    Classification reports & metrics
│
├── yield_model/                # 📊 Yield forecasting training pipeline (XGBoost)
│   ├── data/                   #    Historical yield & climate datasets
│   ├── data_prep/              #    Label encoding & data cleaning
│   ├── models/                 #    Saved XGBoost model & encoders
│   ├── scripts/                #    Training, cross-validation scripts
│   └── reports/                #    Regression plots, R² / MAE metrics
│
├── frontend/                   # ⚛️  React.js web dashboard
│   ├── src/                    #    Components, pages, hooks, i18n
│   ├── public/                 #    Static assets
│   ├── tailwind.config.js      #    Tailwind CSS configuration
│   └── package.json            #    Frontend dependencies
│
├── documentation/              # 📄 Academic & technical documentation
│   ├── ABOUT.md                #    Detailed project goals, architecture & ML details
│   └── WORKING_OF_THE_PROJECT.md #  Detailed technical explanation of system pipeline
├── logs/                       # 🪵 Runtime system logs
├── reports/                    # 📑 Generated analytical reports
├── requirements.txt            # Python dependency manifest
└── .gitignore
```

---

## 💻 Tech Stack

### 🖥️ Frontend
| Technology | Version | Purpose |
|---|---|---|
| React.js | 19 | Component-based UI framework |
| Tailwind CSS | 3.4 | Utility-first styling |
| Framer Motion | 12 | Animations & micro-interactions |
| Recharts | 3.7 | Interactive data visualization |
| React Router DOM | 7 | Client-side routing |
| i18next / react-i18next | — | Multi-language internationalization |
| Lucide React | — | Icon system |
| Axios | — | HTTP client |

### 🤖 AI / Machine Learning (FastAPI Backend)
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core language |
| FastAPI | ≥ 0.115 | High-performance ML API server |
| Uvicorn | ≥ 0.30 | ASGI server |
| PyTorch / Torchvision | ≥ 2.3 | Deep learning (disease CNN) |
| Scikit-Learn | ≥ 1.5 | Ensemble modeling (crop recommendation) |
| XGBoost | ≥ 2.0 | Gradient boosting (yield regression) |
| LightGBM | ≥ 4.3 | Gradient boosting (ensemble member) |
| Google Generative AI | ≥ 1.0 | Gemini LLM integration |
| OpenAI CLIP | — | Visual-semantic features |
| FAISS | ≥ 1.7 | Similarity search |
| OpenCV | ≥ 4.8 | Image preprocessing |
| Pandas / NumPy | — | Data manipulation |


---

## 🗄️ Datasets

Download the training datasets and place them in the correct directories before running training scripts.

| Module | Dataset | Target Directory |
|---|---|---|
| 🦠 Disease Detection | [PlantVillage Dataset ↗](https://drive.google.com/drive/folders/1hMRYfnG-9OKpa8tB_zbzO9Gw2qUYJ8D2?usp=sharing) | `disease_model/data/` |
| 🌿 Crop Recommendation | [Crop Recommendation Dataset ↗](https://drive.google.com/drive/folders/11-Ld88jJMRRGzNd9bw24utOg51v1GLcc?usp=sharing) | `crop_model/data/` |
| 📊 Yield Prediction | [Crop Yield Dataset ↗](https://drive.google.com/drive/folders/1SkMuOc498OXxruQy3_EaJsDZy60JF3th?usp=sharing) | `yield_model/data/` |

> **Note:** Pre-trained model weights are stored in each module's `models/` directory. If weights are present, you can skip training and run inference directly.

---

## 🚀 Installation & Setup

### Prerequisites
- **Python** 3.10 or higher
- **Node.js** 18 or higher
- **npm** 8 or higher
- A **Google Gemini API key** ([Get one here](https://aistudio.google.com/app/apikey))

---

### Step 1 — Clone the Repository
```bash
git clone https://github.com/FuricBond/smart-agriculture-ai-system.git
cd smart-agriculture-ai-system
```

---

### Step 2 — Configure Environment Variables
Create a `.env` file inside the `ai_api/` directory:
```bash
# ai_api/.env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

---

### Step 3 — Start the Python FastAPI ML Server

> Ensure Python 3.10+ is installed. Using a virtual environment is strongly recommended.

```bash
# Create and activate virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install all Python dependencies
pip install -r requirements.txt

# Launch the FastAPI server
cd ai_api
uvicorn api:app --reload --port 8000
```
✅ The AI API will be live at **`http://localhost:8000`**  
📖 Interactive API docs available at **`http://localhost:8000/docs`**

---

### Step 4 — Start the React Frontend Dashboard
```bash
# Open a new terminal at project root
cd frontend
npm install
npm start
```
✅ The dashboard will open automatically at **`http://localhost:3000`**


---

## 🛠️ How to Use

### 1. 🔬 Diagnose a Crop Disease
Navigate to the **Diagnostics Hub** tab.
- Upload a clear, well-lit photo of a crop leaf.
- The AI processes the image through the EfficientNet CNN.
- View the identified disease (or "Healthy" confirmation), confidence score, and treatment recommendations.
- A Grad-CAM attention heatmap shows which leaf regions influenced the diagnosis.

### 2. 🌱 Get a Crop Recommendation
Navigate to the **Crop Matrix** tab.
- Enter your soil test values: **Nitrogen (N), Phosphorus (P), Potassium (K), pH**, rainfall, temperature, and humidity.
- The ensemble model (Random Forest + XGBoost + LightGBM) recommends the **top 3 most suitable crops**.
- Gemini AI provides tailored fertilizer and cultivation advice for each recommended crop.

### 3. 📈 Forecast Your Harvest Yield
Navigate to the **Yield Intelligence** tab.
- Select your **geographic area**, **target crop**, and **planting year**.
- The XGBoost regressor predicts the expected **harvest density (hg/ha)**.
- View interactive historical yield trend charts and AI advice to maximize output.

### 4. 💬 Chat with the Farm AI Assistant
Navigate to the **AI Assistant** tab.
- Ask any farming-related question in natural language (e.g., *"What fertilizer should I use for rice in sandy soil?"*).
- The chatbot is powered by Google Gemini and is trained to respond with agronomic expertise.

---

## 🔌 API Endpoints Reference

The FastAPI server provides several production-grade endpoints for prediction, chat, and utility functions:

### 1. 🏥 System Health check
- **Endpoint:** `GET /health`
- **Description:** Verifies running state and loading status of all models.
- **Response:**
  ```json
  {
    "status": "running",
    "disease_model": true,
    "ensemble_models": true,
    "crop_model": true,
    "yield_model": true,
    "timestamp": "2026-05-29T16:17:55"
  }
  ```

### 2. 🔬 Disease Diagnosis (Ensemble + Grad-CAM)
- **Endpoint:** `POST /detect-disease`
- **Request Type:** `multipart/form-data`
- **Payload:** File input named `file` (image).
- **Description:** Diagnoses plant leaf diseases using a soft-voting ensemble (EfficientNet-B0, ResNet-50, EfficientNet-B1) and overlays a Grad-CAM attention heatmap.

### 3. 🌱 Crop Recommendation
- **Endpoint:** `POST /predict-crop`
- **Request Type:** `application/json`
- **Payload:**
  ```json
  {
    "Nitrogen": 90.0,
    "Phosphorus": 42.0,
    "Potassium": 43.0,
    "Temperature": 20.87,
    "Humidity": 82.00,
    "pH": 6.5,
    "Rainfall": 202.93
  }
  ```
- **Description:** Recommends the top 3 most suitable crops based on soil nutrients and climate conditions.

### 4. 📈 Yield Prediction & Intelligence
- **Endpoint:** `POST /predict-yield-v2/full`
- **Request Type:** `application/json`
- **Payload:**
  ```json
  {
    "crop": "Rice",
    "state": "Uttar Pradesh",
    "season": "Kharif",
    "year": 2024
  }
  ```
- **Description:** Predicts expected crop yield in hg/ha and returns a Gemini-generated risk assessment and agricultural suggestions.

### 5. 💬 Farm AI Assistant
- **Endpoint:** `POST /farm-assistant`
- **Request Type:** `application/json`
- **Payload:**
  ```json
  {
    "question": "What is the best fertilizer timing for wheat?"
  }
  ```
- **Description:** Real-time conversational AI chatbot expert for agronomy and crop management queries.

### 6. 📊 Yield Trends
- **Endpoint:** `POST /yield-trends`
- **Request Type:** `application/json`
- **Payload:**
  ```json
  {
    "Area": "India",
    "Crop": "Wheat"
  }
  ```
- **Description:** Returns historical yield records to plot trends on the frontend dashboard.

---

## 👨‍💻 Team Contributions


This project was developed collaboratively by a five-member team, with each member owning one complete module from data preparation through integration.

| # | Role | Module | Key Responsibilities |
|---|---|---|---|
| 1 | **Deep Learning & Diagnostics Lead** | Disease Detection | EfficientNet CNN training, data augmentation pipeline, Grad-CAM integration, model evaluation |
| 2 | **Predictive Soil Modeling & Feature Engineer** | Crop Recommendation | 21-feature engineering pipeline, soft-voting ensemble (RF + XGBoost + LightGBM), input validation guards |
| 3 | **Yield Forecasting & Analytics Lead** | Yield Prediction | Historical data aggregation, XGBoost regressor, 5-fold CV, R²/MAE/RMSE reporting & visual charts |
| 4 | **Backend Systems & API Architect** | Backend API | FastAPI server, RESTful endpoints, Node.js proxy, Gemini integration, full pipeline orchestration |
| 5 | **Frontend Developer & UI/UX Designer** | Dashboard UI | React dashboard, Tailwind CSS, Recharts visualizations, i18n support, API integration |

> Each member contributed equally to the final integrated system through parallel development of independent, interconnected modules.

---

## 🔮 Future Improvements

- [ ] **🛰️ Satellite Data Integration** — Auto-map farm areas to pull real-time NDVI and soil moisture data
- [ ] **⛅ Live Weather API** — Connect to OpenWeatherMap to auto-fill climatic inputs for predictions
- [ ] **📱 Mobile App** — React Native port for in-field use on smartphones
- [ ] **📡 IoT Sensor Integration** — Consume live telemetry from on-farm NPK and moisture sensors
- [ ] **🗺️ Farm Mapping** — Geospatial visualization of field health zones and yield maps
- [ ] **🔐 User Authentication** — Farmer profile system with historical record tracking

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <p>Built with ❤️ for the future of farming.</p>
  <p><i>Smart Agriculture AI System — Empowering farmers with the power of artificial intelligence.</i></p>
</div>