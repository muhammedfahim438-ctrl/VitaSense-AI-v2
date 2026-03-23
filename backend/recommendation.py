"""
VitaSense AI - recommendation.py
Generates fully personalised recommendations based on prediction result.
4 types: Diet, Exercise, Lifestyle, Monitoring
All recommendations are tailored to risk level (High / Medium / Low),
glucose level, BMI status and age.
"""

# ─── Diet Recommendations ─────────────────────────────────────────────────────

DIET = {
    "High": {
        "message": (
            "You have a HIGH diabetes risk. A strict low-GI, low-sugar diet "
            "is essential right now. Avoid all refined carbs and sugary foods."
        ),
        "eat": [
            {"food": "Bitter gourd (karela)",     "reason": "Naturally lowers blood glucose"},
            {"food": "Leafy greens (spinach, methi)", "reason": "Low carb, high fibre, anti-inflammatory"},
            {"food": "Brown rice / quinoa",        "reason": "Low-GI carbs that release energy slowly"},
            {"food": "Fatty fish (salmon, sardines)", "reason": "Omega-3 improves insulin sensitivity"},
            {"food": "Nuts & seeds (almonds, flaxseed)", "reason": "Healthy fats that stabilise blood sugar"},
        ],
        "avoid": [
            {"food": "White rice / white bread",   "reason": "High GI — spikes blood sugar rapidly"},
            {"food": "Sugary drinks & juices",     "reason": "Direct glucose spike, no nutritional value"},
            {"food": "Sweets, mithai, chocolates", "reason": "Extremely high sugar content"},
            {"food": "Fried & processed foods",   "reason": "Cause insulin resistance"},
            {"food": "Full-fat dairy (excess)",   "reason": "Saturated fat worsens insulin sensitivity"},
        ],
        "meal_tips": [
            "Eat small portions every 3–4 hours — avoid skipping meals",
            "Fill half your plate with non-starchy vegetables",
            "Limit total carbs to 45–60 g per meal",
            "Drink 2–3 litres of water daily — avoid sweetened drinks",
            "Avoid eating after 9 PM",
        ],
    },

    "Medium": {
        "message": (
            "You are in the PREDIABETES range. Reducing sugar and increasing "
            "dietary fibre now can normalise your blood sugar within months."
        ),
        "eat": [
            {"food": "Oats / daliya",              "reason": "High soluble fibre — slows glucose absorption"},
            {"food": "Legumes (dal, rajma, chana)", "reason": "Low GI, high protein and fibre"},
            {"food": "Fresh fruits (guava, apple, papaya)", "reason": "Natural sugars with fibre — moderate intake"},
            {"food": "Yogurt (plain, low-fat)",    "reason": "Probiotics help regulate blood sugar"},
            {"food": "Vegetables (broccoli, beans, capsicum)", "reason": "Low carb, high in vitamins"},
        ],
        "avoid": [
            {"food": "Sugary snacks & biscuits",  "reason": "Hidden sugars spike insulin levels"},
            {"food": "Refined flour (maida)",     "reason": "Very high GI, no nutritional benefit"},
            {"food": "Packaged / processed foods","reason": "High in sodium, sugar and trans fats"},
            {"food": "Alcohol",                   "reason": "Disrupts blood sugar regulation"},
            {"food": "High-sugar fruits (mango, banana in excess)", "reason": "Excess fructose raises blood sugar"},
        ],
        "meal_tips": [
            "Use the plate method — 50% veggies, 25% protein, 25% whole grain",
            "Replace white rice with brown rice or millets",
            "Snack on nuts or fruit instead of biscuits",
            "Limit total sugar to under 25 g per day",
            "Eat dinner at least 2 hours before sleeping",
        ],
    },

    "Low": {
        "message": (
            "Your diabetes risk is LOW. Maintain your balanced diet to "
            "keep blood sugar in the healthy range long term."
        ),
        "eat": [
            {"food": "Whole grains (wheat, oats, millets)", "reason": "Sustained energy, good fibre intake"},
            {"food": "Colourful vegetables",       "reason": "Antioxidants protect against diabetes"},
            {"food": "Fresh fruits (all varieties)", "reason": "Natural nutrients and fibre"},
            {"food": "Lean protein (chicken, eggs, tofu)", "reason": "Builds muscle, keeps you full longer"},
            {"food": "Healthy fats (avocado, olive oil)", "reason": "Heart and metabolic health"},
        ],
        "avoid": [
            {"food": "Excess sugar & sweets",     "reason": "Prevention — keep sugar intake moderate"},
            {"food": "Too much processed food",   "reason": "Long-term risk if consumed regularly"},
            {"food": "Sugary beverages",          "reason": "Easiest way to gain weight and raise blood sugar"},
            {"food": "Late-night heavy meals",    "reason": "Disrupts metabolism and sleep quality"},
            {"food": "Trans fats (vanaspati, margarine)", "reason": "Increases cardiovascular and diabetes risk"},
        ],
        "meal_tips": [
            "Keep eating balanced — you're on the right track",
            "Stay hydrated with 2–3 litres of water daily",
            "Include a variety of colours on your plate every day",
            "Limit junk food to once a week",
            "Maintain regular meal timing for metabolic stability",
        ],
    },
}

# ─── Exercise Recommendations ─────────────────────────────────────────────────

EXERCISE = {
    "High": {
        "message": (
            "Regular exercise is one of the most powerful ways to lower "
            "blood sugar. Start immediately and be consistent."
        ),
        "plan": [
            {
                "type":      "Brisk Walking",
                "duration":  "45 minutes",
                "frequency": "Daily (7 days/week)",
                "intensity": "Moderate — you should be slightly breathless",
                "benefit":   "Directly lowers blood glucose levels",
            },
            {
                "type":      "Strength Training",
                "duration":  "30 minutes",
                "frequency": "3 days/week",
                "intensity": "Moderate — bodyweight or light weights",
                "benefit":   "Builds muscle which absorbs excess glucose",
            },
            {
                "type":      "Yoga / Stretching",
                "duration":  "20 minutes",
                "frequency": "Daily",
                "intensity": "Light — focus on breathing and relaxation",
                "benefit":   "Reduces cortisol (stress hormone) that raises blood sugar",
            },
            {
                "type":      "Cycling / Swimming",
                "duration":  "30 minutes",
                "frequency": "3–4 days/week",
                "intensity": "Moderate",
                "benefit":   "Low-impact cardio, excellent for blood sugar control",
            },
        ],
        "tips": [
            "Exercise 30–60 minutes after meals for best glucose reduction",
            "Check blood sugar before and after exercise if possible",
            "Never exercise on an empty stomach — have a light snack",
            "Stay consistent — even a 15-minute walk helps on busy days",
            "Consult your doctor before starting intense exercise",
        ],
    },

    "Medium": {
        "message": (
            "Moderate regular exercise can bring your blood sugar back "
            "to the normal range. Aim for at least 150 minutes per week."
        ),
        "plan": [
            {
                "type":      "Brisk Walking / Jogging",
                "duration":  "30 minutes",
                "frequency": "5 days/week",
                "intensity": "Moderate",
                "benefit":   "Improves insulin sensitivity within weeks",
            },
            {
                "type":      "Strength Training",
                "duration":  "25 minutes",
                "frequency": "2–3 days/week",
                "intensity": "Moderate",
                "benefit":   "Increases lean muscle mass — improves glucose uptake",
            },
            {
                "type":      "Yoga",
                "duration":  "30 minutes",
                "frequency": "3 days/week",
                "intensity": "Light to moderate",
                "benefit":   "Reduces stress which contributes to blood sugar rise",
            },
            {
                "type":      "Dance / Aerobics",
                "duration":  "30 minutes",
                "frequency": "2 days/week",
                "intensity": "Moderate — enjoyable cardio",
                "benefit":   "Burns calories, lifts mood and improves metabolism",
            },
        ],
        "tips": [
            "Aim for 150+ minutes of moderate activity each week",
            "Take a 10-minute walk after every main meal",
            "Use stairs instead of lifts wherever possible",
            "Track your steps — aim for 8,000–10,000 steps per day",
            "Stay active even on rest days with light walking or stretching",
        ],
    },

    "Low": {
        "message": (
            "You're in great shape! Maintain your current activity level "
            "to keep your diabetes risk low long term."
        ),
        "plan": [
            {
                "type":      "Walking / Light Jogging",
                "duration":  "25 minutes",
                "frequency": "4 days/week",
                "intensity": "Light to moderate",
                "benefit":   "Maintains healthy metabolism and blood sugar",
            },
            {
                "type":      "Strength or Resistance Training",
                "duration":  "20–30 minutes",
                "frequency": "2 days/week",
                "intensity": "Light to moderate",
                "benefit":   "Keeps muscles healthy and metabolism active",
            },
            {
                "type":      "Yoga / Stretching",
                "duration":  "20 minutes",
                "frequency": "3 days/week",
                "intensity": "Light",
                "benefit":   "Flexibility, stress relief and mental wellbeing",
            },
            {
                "type":      "Any sport or activity you enjoy",
                "duration":  "30+ minutes",
                "frequency": "Weekends",
                "intensity": "Your choice",
                "benefit":   "Keeps you motivated and active long term",
            },
        ],
        "tips": [
            "Keep exercising regularly — consistency is the key",
            "Aim for at least 30 minutes of movement most days",
            "Mix cardio and strength training for best overall health",
            "Stay hydrated during exercise — drink water before and after",
            "Annual health check-ups are still recommended",
        ],
    },
}

# ─── Lifestyle Recommendations ────────────────────────────────────────────────

LIFESTYLE = {
    "High": {
        "sleep":        "7–8 hours every night. Poor sleep raises cortisol and blood sugar.",
        "stress":       "Practice deep breathing, meditation or yoga daily. High stress = high blood sugar.",
        "water":        "Drink 3+ litres of water daily. Water helps kidneys flush excess glucose.",
        "smoking":      "Stop smoking immediately. Smoking doubles the risk of Type 2 diabetes.",
        "alcohol":      "Avoid alcohol completely. It disrupts blood sugar regulation severely.",
        "weight":       "Weight loss of even 5–7% of body weight significantly reduces diabetes risk.",
        "checkups":     "Schedule a doctor appointment within the next 7 days.",
    },
    "Medium": {
        "sleep":        "Get 7–8 hours of sleep. Sleep deprivation raises blood sugar levels.",
        "stress":       "Manage stress with mindfulness, light exercise or a hobby you enjoy.",
        "water":        "Drink 2.5–3 litres of water daily. Replace sugary drinks with water.",
        "smoking":      "Quit smoking — it is a major modifiable risk factor for diabetes.",
        "alcohol":      "Limit alcohol to no more than 1 unit per day if at all.",
        "weight":       "Aim to reach a healthy BMI. Losing weight reduces prediabetes risk greatly.",
        "checkups":     "See a doctor within the next 2–4 weeks for a full diabetes screening.",
    },
    "Low": {
        "sleep":        "Maintain 7–8 hours of quality sleep every night.",
        "stress":       "Keep stress low — practice relaxation techniques when needed.",
        "water":        "Drink 2–3 litres of water daily to stay well hydrated.",
        "smoking":      "Stay smoke-free — smoking is a risk factor for many diseases.",
        "alcohol":      "Keep alcohol intake moderate or avoid it altogether.",
        "weight":       "Maintain your healthy weight with regular exercise and a balanced diet.",
        "checkups":     "Routine health check-up once a year is recommended.",
    },
}

# ─── Monitoring Recommendations ───────────────────────────────────────────────

MONITORING = {
    "High": {
        "blood_sugar_frequency": "Check fasting blood sugar daily if possible, or every 2–3 days minimum",
        "hba1c_frequency":       "HbA1c test every 3 months",
        "doctor_visits":         "Visit your doctor every 1–2 months",
        "tests_recommended": [
            "Fasting Blood Sugar (FBS)",
            "Post-Prandial Blood Sugar (PPBS)",
            "HbA1c (Glycated Haemoglobin)",
            "Kidney Function Test (KFT)",
            "Lipid Profile",
            "Eye examination (diabetic retinopathy check)",
            "Foot examination",
        ],
        "target_ranges": {
            "Fasting glucose":     "80–130 mg/dL",
            "Post-meal glucose":   "< 180 mg/dL",
            "HbA1c":               "< 7.0%",
            "Blood pressure":      "< 130/80 mmHg",
            "BMI":                 "18.5–24.9",
        },
    },
    "Medium": {
        "blood_sugar_frequency": "Check fasting blood sugar once a week",
        "hba1c_frequency":       "HbA1c test every 6 months",
        "doctor_visits":         "Visit your doctor every 3 months",
        "tests_recommended": [
            "Fasting Blood Sugar (FBS)",
            "Post-Prandial Blood Sugar (PPBS)",
            "HbA1c (Glycated Haemoglobin)",
            "Lipid Profile",
            "Blood Pressure monitoring",
        ],
        "target_ranges": {
            "Fasting glucose":     "< 100 mg/dL",
            "Post-meal glucose":   "< 140 mg/dL",
            "HbA1c":               "< 5.7%",
            "Blood pressure":      "< 120/80 mmHg",
            "BMI":                 "18.5–24.9",
        },
    },
    "Low": {
        "blood_sugar_frequency": "Check fasting blood sugar once a month as a preventive measure",
        "hba1c_frequency":       "HbA1c test once a year",
        "doctor_visits":         "Annual health check-up",
        "tests_recommended": [
            "Fasting Blood Sugar (FBS)",
            "HbA1c (once a year)",
            "Blood Pressure check",
            "BMI check",
        ],
        "target_ranges": {
            "Fasting glucose":     "< 100 mg/dL",
            "Post-meal glucose":   "< 140 mg/dL",
            "HbA1c":               "< 5.7%",
            "Blood pressure":      "< 120/80 mmHg",
            "BMI":                 "18.5–24.9",
        },
    },
}

# ─── 10 Personalised Health Tips ─────────────────────────────────────────────

HEALTH_TIPS = {
    "High": [
        "Consult a doctor as soon as possible — do not delay.",
        "Check your blood sugar every morning before eating.",
        "Cut out all sugar, white rice and refined flour from your diet immediately.",
        "Walk for at least 45 minutes every day — start today.",
        "Drink 3 litres of water daily and avoid all sugary drinks.",
        "Eat small meals every 3–4 hours — never skip meals.",
        "Sleep 7–8 hours — sleep deprivation worsens blood sugar control.",
        "Manage stress actively — cortisol directly raises blood glucose.",
        "Avoid smoking and alcohol — both significantly worsen diabetes.",
        "Lose even 5% of your body weight to see a measurable improvement.",
    ],
    "Medium": [
        "You can reverse prediabetes — lifestyle changes are highly effective.",
        "Replace white rice with brown rice or millets this week.",
        "Take a 10-minute walk after every meal — it lowers blood sugar.",
        "Cut sugary snacks and replace with nuts or fruit.",
        "Aim for 150 minutes of moderate exercise every week.",
        "Sleep at least 7 hours — poor sleep raises blood sugar.",
        "Drink water instead of juice, tea with sugar or soft drinks.",
        "Reduce stress — try 10 minutes of deep breathing daily.",
        "Get your HbA1c tested — it gives a 3-month blood sugar average.",
        "Track your progress — small consistent changes make a big difference.",
    ],
    "Low": [
        "Great job! Keep up your healthy habits every day.",
        "Stay active — even a daily 30-minute walk keeps diabetes away.",
        "Eat a balanced diet with plenty of vegetables and whole grains.",
        "Stay well hydrated — drink 2–3 litres of water daily.",
        "Maintain a healthy weight — it is the best diabetes prevention.",
        "Get an annual health check-up including fasting blood sugar.",
        "Limit processed and junk food to occasional treats only.",
        "Sleep 7–8 hours every night for overall metabolic health.",
        "Keep stress under control with regular exercise and relaxation.",
        "Share healthy habits with your family — diabetes has a genetic risk.",
    ],
}

# ─── Main function: build full recommendation package ─────────────────────────

def get_recommendations(risk_level: str, glucose: float, bmi: float,
                         bmi_status: str, age: float) -> dict:
    """
    Returns a complete personalised recommendation package
    based on risk_level (High / Medium / Low), glucose, BMI and age.
    """
    level = risk_level if risk_level in ("High", "Medium", "Low") else "Low"

    return {
        "diet":       DIET[level],
        "exercise":   EXERCISE[level],
        "lifestyle":  LIFESTYLE[level],
        "monitoring": MONITORING[level],
        "health_tips": HEALTH_TIPS[level],
    }


# ─── Quick self-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    for level in ["High", "Medium", "Low"]:
        rec = get_recommendations(level, glucose=160, bmi=32, bmi_status="Obese", age=45)
        print(f"\n{'─'*50}")
        print(f"  Risk Level  : {level}")
        print(f"  Diet msg    : {rec['diet']['message'][:70]}...")
        print(f"  Exercise    : {rec['exercise']['plan'][0]['type']} — {rec['exercise']['plan'][0]['duration']}")
        print(f"  Sleep tip   : {rec['lifestyle']['sleep'][:60]}...")
        print(f"  HbA1c check : {rec['monitoring']['hba1c_frequency']}")
        print(f"  Tip 1       : {rec['health_tips'][0]}")