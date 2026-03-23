# 🩺 VitaSense AI — Diabetes Prediction & Management Platform

<div align="center">

![VitaSense AI](https://img.shields.io/badge/VitaSense-AI-0EA5E9?style=for-the-badge&logo=python&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

**98.2% Accuracy · ROC-AUC 0.9975 · 5,000 Patient Records · 16 AI Features**

[Features](#-features) · [Demo](#-demo) · [Installation](#-installation) · [API](#-api-endpoints) · [Tech Stack](#-tech-stack) · [Model](#-ai-model)

</div>

---

## 📌 Overview

**VitaSense AI** is an intelligent, web-based diabetes prediction and management platform. It uses a **Voting Ensemble** of Random Forest and Gradient Boosting to predict diabetes risk from basic medical parameters — and returns a complete personalised action plan covering diet, exercise, lifestyle and monitoring.

> ⚕️ **Disclaimer:** This application is for **educational and screening purposes only**. It is not a medical diagnosis. Always consult a qualified doctor.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🤖 **AI Risk Prediction** | Voting Ensemble (RF + GB) · Exact risk % (0–100) · 98.2% accuracy |
| 📊 **Confidence Score** | Evaluates data quality and consistency · Unique transparency feature |
| 🥗 **Diet Recommendations** | 5 foods to eat + 5 to avoid with medical reasons · Personalised by risk level |
| 🏃 **Exercise Plans** | Duration, frequency and intensity tailored to your exact risk |
| 💡 **Lifestyle Guidance** | Sleep, stress, water intake, smoking and alcohol advice |
| 📋 **Monitoring Schedule** | How often to check blood sugar, HbA1c and doctor visit frequency |
| 💬 **Diabetes Chatbot** | 20 educational topics · Keyword-based with curated medical responses |
| 📊 **Reference Ranges** | Age-group specific normal values for all 8 parameters |
| 📈 **Analytics Dashboard** | Prediction history, risk distribution, health score trends |
| 🗄️ **Dataset Viewer** | Full 5,000-record training dataset with search, filter and CSV export |

---

## 🖥️ Demo

### Prediction Flow
```
User enters glucose, BP, BMI, DPF, age
         ↓
Optional fields (pregnancies, skin thickness, insulin) auto-imputed if blank
         ↓
16 features engineered (including HOMA-IR insulin resistance)
         ↓
Voting Ensemble predicts risk probability
         ↓
Full result: risk %, HbA1c estimate, health score, % breakdown
         ↓
Personalised diet + exercise + lifestyle + monitoring plan
```

### Sample Result
```json
{
  "prediction": "Diabetic",
  "risk_percentage": 73.4,
  "risk_level": "High",
  "urgency_level": "See Doctor Now",
  "health_metrics": {
    "hba1c_estimate": 7.6,
    "bmi_status": "Obese",
    "health_score": 34
  },
  "percentage_breakdown": {
    "glucose_contribution": 82.0,
    "bmi_contribution": 71.0,
    "age_contribution": 62.0
  }
}
```

---

## 🗂️ Project Structure

```
VitaSense-AI-v2/
│
├── vitasense.html              # Complete frontend (CSS + HTML + JS)
│
└── backend/
    ├── app.py                  # Flask server · CORS · Port 5000
    ├── models.py               # SQLite DB setup · 2 tables
    ├── ai_model.py             # Loads pkl files · Runs prediction
    ├── recommendation.py       # Diet · Exercise · Lifestyle · Monitoring data
    ├── chatbot_model.py        # 20-topic keyword chatbot
    ├── train_model.py          # Dataset generator + model training
    │
    ├── routes/
    │   ├── __init__.py
    │   ├── predict.py          # POST /predict · GET /dataset · GET /dashboard/stats
    │   └── chatbot.py          # POST /chat · GET /chat/topics
    │
    └── models/                 # Auto-created after running train_model.py
        ├── vitasense_model.pkl
        ├── vitasense_scaler.pkl
        ├── vitasense_imputer.pkl
        └── vitasense_medians.pkl
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.8+
- VS Code with **Live Server** extension installed

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/VitaSense-AI-v2.git
cd VitaSense-AI-v2
```

### Step 2 — Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install flask flask-cors scikit-learn numpy pandas
```

### Step 4 — Train the model (run once only)
```bash
cd backend
python train_model.py
```

Expected output:
```
============================================================
  VitaSense AI — Model Training
============================================================
[1/5] Generating dataset (5000 records, 16 features)...
[2/5] Optional-field medians...
[3/5] Imputing + scaling...
[4/5] Training Voting Ensemble (RF + GB)...
[5/5] Evaluating model...
  Accuracy  : 98.2%
  ROC-AUC   : 0.9975
  ✓ Model   → backend/models/vitasense_model.pkl
  Training complete!
============================================================
```

### Step 5 — Start the backend server
```bash
python app.py
```

Server starts at `http://localhost:5000`

### Step 6 — Open the frontend
Right-click `vitasense.html` in VS Code → **Open with Live Server**

Navigate to `http://127.0.0.1:5500/vitasense.html`

---

## 🔌 API Endpoints

Base URL: `http://localhost:5000`

### Prediction

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/predict` | Run AI prediction · Accepts JSON or form-data |
| `GET` | `/predictions/history` | Last N predictions · `?limit=20` |
| `GET` | `/dashboard/stats` | Aggregated stats for Dashboard charts |
| `GET` | `/dataset` | All 5,000 training records for Dataset tab |

#### POST `/predict` — Request Body
```json
{
  "glucose": 148,
  "blood_pressure": 85,
  "bmi": 33.6,
  "dpf": 0.627,
  "age": 50,
  "pregnancies": 3,
  "skin_thickness": 35,
  "insulin": 80
}
```
> `pregnancies`, `skin_thickness` and `insulin` are optional — omit them and the model auto-imputes using training medians.

### Chatbot

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Send a message · Get educational response |
| `GET` | `/chat/topics` | All 20 topic titles for quick-reply buttons |
| `GET` | `/chat/history` | Last N messages · `?limit=50` |

### Health Check

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Server health check · Lists all endpoints |

---

## 🤖 AI Model

### Architecture
```
Input (5–8 params) → Feature Engineering (16 features) → Imputer → Scaler
        ↓
  ┌─────────────┐     ┌──────────────────┐
  │Random Forest│     │Gradient Boosting │
  │  300 trees  │  +  │   300 trees      │
  │  (bagging)  │     │  (sequential)    │
  └──────┬──────┘     └────────┬─────────┘
         │                     │
         └─────── Soft Vote ───┘
                     ↓
              Risk % (0–100)
```

### Model Parameters

**Random Forest**
```python
RandomForestClassifier(
    n_estimators=300, max_depth=10,
    min_samples_split=4, min_samples_leaf=2,
    max_features="sqrt", class_weight="balanced",
    random_state=42, n_jobs=-1
)
```

**Gradient Boosting**
```python
GradientBoostingClassifier(
    n_estimators=300, learning_rate=0.05,
    max_depth=5, subsample=0.8,
    min_samples_split=4, random_state=42
)
```

### Performance

| Metric | Value |
|---|---|
| Accuracy | **98.2%** |
| ROC-AUC | **0.9975** |
| Cross-validation | 5-fold stratified |
| Train/Test split | 80% / 20% stratified |

### 8 Input Parameters

| Parameter | Type | Range |
|---|---|---|
| Glucose | Required | 50–400 mg/dL |
| Blood Pressure | Required | 40–160 mmHg |
| BMI | Required | 10–70 kg/m² |
| Diabetes Pedigree Function | Required | 0.05–3.0 |
| Age | Required | 1 month–120 years |
| Pregnancies | Optional | 0–20 |
| Skin Thickness | Optional | 0–100 mm |
| Insulin | Optional | 0–900 µU/mL |

### 8 Engineered Features

| Feature | Formula | Medical Meaning |
|---|---|---|
| HOMA-IR | (Insulin × Glucose) / 405 | Insulin resistance biomarker |
| Glucose-BMI Ratio | Glucose ÷ BMI | Compound risk factor |
| Age-BMI Interaction | (Age × BMI) / 100 | Age-compounded obesity risk |
| Glucose-Age Ratio | Glucose ÷ Age | Age-adjusted glucose significance |
| BMI Category | 0–3 ordinal | Underweight/Normal/Overweight/Obese |
| Glucose Category | 0–2 ordinal | Normal/Prediabetes/High |
| BP Category | 0–2 ordinal | Normal/Elevated/High |
| Age Category | 0–3 ordinal | Under 30 / 30–45 / 45–60 / Over 60 |

---

## 🗃️ Database

SQLite database (`vitasense.db`) with 2 tables:

**`predictions`** — stores every prediction with all inputs, outputs, % breakdowns, urgency and recommendation message

**`chat_history`** — stores every chatbot conversation with detected topic and timestamp

---

## 💬 Chatbot Topics (20)

What is diabetes · Symptoms · Normal blood sugar · HbA1c · Diet advice · Foods to avoid · Exercise · Causes · Complications · Low blood sugar emergency · High blood sugar emergency · Prevention · BMI · Insulin · Stress · Water intake · Sleep · Foot care · Pregnancy · Blood sugar monitoring

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask, Flask-CORS |
| ML | Scikit-learn, NumPy, Pandas, Pickle |
| Database | SQLite3 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js 4.4.0 |
| Fonts | Outfit, Plus Jakarta Sans (Google Fonts) |
| Dev Tools | VS Code, Live Server extension |

---

## 📦 Dependencies

```
flask
flask-cors
scikit-learn
numpy
pandas
```

Install all with:
```bash
pip install flask flask-cors scikit-learn numpy pandas
```

---

## 🔒 Safety & Ethics

- ✅ Never suggests medicines or drug dosages
- ✅ Every result includes a medical disclaimer
- ✅ Chatbot always ends responses with "consult a doctor"
- ✅ All predictions labelled as educational screening only
- ✅ No user registration or personal data collection
- ✅ Infants (age < 1 year) always receive "See Doctor Now" urgency

---

## 🗺️ Future Scope

- [ ] Mobile app (React Native) for Android and iOS
- [ ] Tamil, Hindi, Telugu language support
- [ ] Hospital EMR system integration via REST API
- [ ] Retrain on real anonymised clinical data
- [ ] Wearable device integration for real-time glucose
- [ ] Doctor dashboard portal for patient monitoring
- [ ] LLM-powered chatbot with safety guardrails

---

## 📁 Build Order

If building from scratch, create files in this order:

```
1. train_model.py      → python train_model.py (run once)
2. models.py
3. ai_model.py
4. recommendation.py
5. chatbot_model.py
6. routes/predict.py
7. routes/chatbot.py
8. app.py              → python app.py
9. vitasense.html      → Open with Live Server
```

---

## 👥 Team — Catalyst Crew

**Hackathon Team · Nehru Arts and Science College, Coimbatore**

| # | Name | Role | GitHub |
|---|---|---|---|
| 1 | **Muhammed Fahim M** | Project Lead · ML Engineer | [![GitHub](https://img.shields.io/badge/GitHub-muhammedfahim438--ctrl-181717?style=flat&logo=github)](https://github.com/muhammedfahim438-ctrl) |
| 2 | **Shain Shafi H** | Backend Developer · API Engineer | [![GitHub](https://img.shields.io/badge/GitHub-Shahinshafi1717-181717?style=flat&logo=github)](https://github.com/Shahinshafi1717) |
| 3 | **Vijay K** | Frontend Developer · UI Designer | — |
| 4 | **Sreekuttan S** | Data Engineer · Model Validation | [![GitHub](https://img.shields.io/badge/GitHub-Sreekuttan33714-181717?style=flat&logo=github)](https://github.com/Sreekuttan33714) |

> Built with ❤️ for the hackathon · **VitaSense AI v2.0**

---

## 👨‍💻 Author

**VitaSense AI v2.0**
Built by Team Catalyst Crew — Nehru Arts and Science College, Coimbatore

---

## 📄 License

This project is for educational purposes. All medical predictions are informational only and not a substitute for professional medical advice.

---

<div align="center">
  <strong>VitaSense AI</strong> · Accuracy: 98.2% · ROC-AUC: 0.9975
  <br/>
  <em>Early awareness is the most powerful medicine we have.</em>
</div>
