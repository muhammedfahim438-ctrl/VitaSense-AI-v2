"""
VitaSense AI - chatbot_model.py
Rule-based AI chatbot covering 20 diabetes topics.
Detects topic from user message using keywords and returns
a detailed educational response. Always advises consulting a doctor.
"""

import re

# ─── 20 Topic Knowledge Base ──────────────────────────────────────────────────

TOPICS = {

    "what_is_diabetes": {
        "keywords": ["what is diabetes", "define diabetes", "diabetes meaning",
                     "what is diabetic", "explain diabetes", "about diabetes"],
        "title": "What is Diabetes?",
        "response": (
            "Diabetes is a chronic condition where the body cannot properly regulate "
            "blood sugar (glucose) levels.\n\n"
            "There are 3 main types:\n"
            "• Type 1 Diabetes — The immune system attacks insulin-producing cells. "
            "The body makes little or no insulin. Usually diagnosed in children or young adults.\n"
            "• Type 2 Diabetes — The body doesn't use insulin effectively (insulin resistance). "
            "This is the most common type, often linked to lifestyle factors.\n"
            "• Gestational Diabetes — Occurs during pregnancy and usually resolves after delivery, "
            "but increases future Type 2 risk.\n\n"
            "Normal blood sugar: 70–99 mg/dL (fasting)\n"
            "Prediabetes: 100–125 mg/dL\n"
            "Diabetes: 126 mg/dL or above (fasting, confirmed on two tests)\n\n"
            "⚕️ Always consult a qualified doctor for diagnosis and treatment."
        ),
    },

    "symptoms": {
        "keywords": ["symptoms", "signs of diabetes", "diabetes signs", "symptom",
                     "how do i know", "how to know if diabetic", "warning signs"],
        "title": "Symptoms of Diabetes",
        "response": (
            "Common symptoms of diabetes include:\n\n"
            "Early symptoms:\n"
            "• Frequent urination (especially at night)\n"
            "• Excessive thirst and dry mouth\n"
            "• Unexplained weight loss\n"
            "• Increased hunger even after eating\n"
            "• Blurred vision\n"
            "• Fatigue and weakness\n\n"
            "Additional symptoms in Type 2:\n"
            "• Slow-healing wounds or cuts\n"
            "• Frequent infections (skin, gum, bladder)\n"
            "• Tingling or numbness in hands and feet\n"
            "• Dark patches on skin (acanthosis nigricans)\n\n"
            "⚠️ Many people with Type 2 diabetes have NO symptoms initially — "
            "regular screening is important.\n\n"
            "⚕️ See a doctor immediately if you experience multiple symptoms."
        ),
    },

    "normal_blood_sugar": {
        "keywords": ["normal blood sugar", "normal glucose", "blood sugar level",
                     "glucose level", "blood sugar range", "what is normal sugar"],
        "title": "Normal Blood Sugar Levels",
        "response": (
            "Blood sugar reference ranges:\n\n"
            "Fasting Blood Sugar (FBS) — tested after 8 hours of fasting:\n"
            "• Normal       : 70 – 99 mg/dL\n"
            "• Prediabetes  : 100 – 125 mg/dL\n"
            "• Diabetes     : 126 mg/dL or above\n\n"
            "Post-meal Blood Sugar (2 hours after eating):\n"
            "• Normal       : Less than 140 mg/dL\n"
            "• Prediabetes  : 140 – 199 mg/dL\n"
            "• Diabetes     : 200 mg/dL or above\n\n"
            "Random Blood Sugar (any time):\n"
            "• Diabetes     : 200 mg/dL or above with symptoms\n\n"
            "For diabetics, target ranges (as per doctor's advice):\n"
            "• Before meals : 80 – 130 mg/dL\n"
            "• After meals  : Less than 180 mg/dL\n\n"
            "⚕️ Your doctor will set personalised targets based on your condition."
        ),
    },

    "hba1c": {
        "keywords": ["hba1c", "a1c", "glycated", "haemoglobin", "hemoglobin a1c",
                     "3 month sugar", "average blood sugar", "hba1c test"],
        "title": "HbA1c — 3-Month Blood Sugar Average",
        "response": (
            "HbA1c (Glycated Haemoglobin) measures your average blood sugar "
            "over the past 2–3 months. It is one of the most important diabetes tests.\n\n"
            "HbA1c reference ranges:\n"
            "• Normal       : Below 5.7%\n"
            "• Prediabetes  : 5.7% – 6.4%\n"
            "• Diabetes     : 6.5% or above\n\n"
            "For people already diagnosed with diabetes:\n"
            "• Well controlled  : Below 7.0%\n"
            "• Needs attention  : 7.0% – 8.0%\n"
            "• Poor control     : Above 8.0%\n\n"
            "Why it matters:\n"
            "• A single blood test can be affected by a recent meal or illness.\n"
            "• HbA1c gives a true average — it cannot be 'cheated' with one day of good diet.\n\n"
            "How often to test:\n"
            "• Diabetics       : Every 3 months\n"
            "• Prediabetics    : Every 6 months\n"
            "• Normal risk     : Once a year\n\n"
            "⚕️ Ask your doctor to include HbA1c in your next blood test."
        ),
    },

    "diet_advice": {
        "keywords": ["diet", "food for diabetes", "what to eat", "diabetic diet",
                     "diet plan", "eating", "nutrition", "meal plan", "what should i eat"],
        "title": "Diabetes Diet Advice",
        "response": (
            "A diabetes-friendly diet focuses on controlling blood sugar spikes.\n\n"
            "Best foods to eat:\n"
            "• Non-starchy vegetables — spinach, broccoli, beans, capsicum\n"
            "• Whole grains — brown rice, oats, millets, quinoa\n"
            "• Legumes — dal, rajma, chana (high fibre, low GI)\n"
            "• Lean protein — eggs, fish, chicken, tofu, paneer\n"
            "• Healthy fats — almonds, walnuts, flaxseed, olive oil\n"
            "• Low-sugar fruits — guava, apple, papaya, berries\n\n"
            "Key principles:\n"
            "• Eat small meals every 3–4 hours\n"
            "• Never skip meals — it causes blood sugar swings\n"
            "• Fill half your plate with vegetables\n"
            "• Limit carbs to 45–60 g per meal\n"
            "• Drink 2–3 litres of water daily\n"
            "• Avoid eating after 9 PM\n\n"
            "⚕️ A registered dietitian can create a personalised meal plan for you."
        ),
    },

    "foods_to_avoid": {
        "keywords": ["avoid", "foods to avoid", "what not to eat", "bad food",
                     "foods bad for diabetes", "sugar foods", "unhealthy food"],
        "title": "Foods to Avoid with Diabetes",
        "response": (
            "These foods can cause dangerous blood sugar spikes and should be "
            "avoided or strictly limited:\n\n"
            "Avoid completely:\n"
            "• Sugary drinks — soft drinks, fruit juices, energy drinks, sweetened tea/coffee\n"
            "• White sugar, jaggery (in large amounts), honey\n"
            "• Sweets — mithai, chocolates, ice cream, cakes, biscuits\n"
            "• Refined flour (maida) — white bread, naan, puri, pasta\n"
            "• Fried foods — samosa, pakora, chips, fried snacks\n\n"
            "Limit significantly:\n"
            "• White rice — switch to brown rice or millet\n"
            "• Potatoes — baked occasionally is better than fried\n"
            "• Full-fat dairy in excess\n"
            "• High-sugar fruits — banana, mango, grapes in large portions\n"
            "• Alcohol — disrupts blood sugar regulation\n"
            "• Packaged and processed foods — hidden sugars and trans fats\n\n"
            "⚕️ Your doctor or dietitian will advise on quantities based on your glucose levels."
        ),
    },

    "exercise": {
        "keywords": ["exercise", "workout", "physical activity", "walk", "jogging",
                     "gym", "yoga", "sport", "fitness", "active"],
        "title": "Exercise and Diabetes",
        "response": (
            "Exercise is one of the most effective ways to control blood sugar naturally.\n\n"
            "How exercise helps:\n"
            "• Muscles use glucose for energy during exercise — lowers blood sugar directly\n"
            "• Improves insulin sensitivity for up to 24–48 hours after exercise\n"
            "• Helps with weight management\n"
            "• Reduces cardiovascular risk (major complication of diabetes)\n\n"
            "Recommended exercise:\n"
            "• Brisk walking — 30–45 minutes daily (most effective and easy to start)\n"
            "• Cycling or swimming — 30 minutes, 3–5 days per week\n"
            "• Strength training — 2–3 days per week to build glucose-absorbing muscle\n"
            "• Yoga — daily, reduces cortisol which raises blood sugar\n\n"
            "Important tips:\n"
            "• Exercise 30–60 minutes after a meal for best blood sugar reduction\n"
            "• Carry a snack in case of low blood sugar during exercise\n"
            "• Stay hydrated — drink water before, during and after exercise\n"
            "• Start slowly and gradually increase intensity\n\n"
            "⚕️ Consult your doctor before starting a new exercise routine."
        ),
    },

    "causes": {
        "keywords": ["cause", "causes of diabetes", "why diabetes", "reason for diabetes",
                     "risk factors", "who gets diabetes", "what causes diabetes"],
        "title": "Causes and Risk Factors of Diabetes",
        "response": (
            "Type 1 Diabetes causes:\n"
            "• Autoimmune reaction — body attacks its own insulin-producing cells\n"
            "• Genetic factors\n"
            "• Possibly triggered by viral infections\n\n"
            "Type 2 Diabetes risk factors:\n"
            "• Overweight or obesity (especially belly fat)\n"
            "• Physical inactivity\n"
            "• Unhealthy diet (high sugar, refined carbs, processed food)\n"
            "• Family history of diabetes\n"
            "• Age above 45 years\n"
            "• High blood pressure\n"
            "• High cholesterol or triglycerides\n"
            "• History of gestational diabetes\n"
            "• Polycystic Ovary Syndrome (PCOS)\n"
            "• Stress and poor sleep\n"
            "• Smoking\n\n"
            "The good news:\n"
            "Most Type 2 diabetes risk factors are MODIFIABLE — meaning lifestyle "
            "changes can prevent or delay onset significantly.\n\n"
            "⚕️ Get screened if you have 2 or more risk factors."
        ),
    },

    "complications": {
        "keywords": ["complications", "danger of diabetes", "effects of diabetes",
                     "damage from diabetes", "what happens if diabetic", "long term"],
        "title": "Complications of Diabetes",
        "response": (
            "Uncontrolled diabetes can damage multiple organs over time:\n\n"
            "Short-term complications:\n"
            "• Hypoglycaemia (low blood sugar) — shakiness, sweating, confusion\n"
            "• Hyperglycaemia (high blood sugar) — fatigue, frequent urination, blurred vision\n"
            "• Diabetic ketoacidosis (Type 1) — life-threatening if untreated\n\n"
            "Long-term complications:\n"
            "• Eyes (Diabetic Retinopathy) — can lead to blindness\n"
            "• Kidneys (Diabetic Nephropathy) — can lead to kidney failure\n"
            "• Nerves (Diabetic Neuropathy) — tingling, numbness, pain in feet and hands\n"
            "• Heart disease — 2–4× higher risk of heart attack and stroke\n"
            "• Foot problems — poor healing, infections, risk of amputation\n"
            "• Dental problems — gum disease is more severe in diabetics\n"
            "• Sexual dysfunction\n\n"
            "Prevention:\n"
            "• Keep blood sugar, blood pressure and cholesterol in target range\n"
            "• Regular eye, foot and kidney check-ups\n"
            "• Never miss medications or doctor visits\n\n"
            "⚕️ Regular monitoring and early treatment prevent most complications."
        ),
    },

    "low_sugar_emergency": {
        "keywords": ["low blood sugar", "hypoglycemia", "hypoglycaemia", "sugar low",
                     "sugar drop", "blood sugar too low", "dizzy sugar", "low sugar emergency"],
        "title": "Low Blood Sugar Emergency (Hypoglycaemia)",
        "response": (
            "Hypoglycaemia occurs when blood sugar drops below 70 mg/dL.\n\n"
            "Symptoms:\n"
            "• Sudden shakiness or trembling\n"
            "• Sweating and pale skin\n"
            "• Rapid heartbeat\n"
            "• Dizziness or lightheadedness\n"
            "• Confusion or difficulty concentrating\n"
            "• Irritability or anxiety\n"
            "• Extreme hunger\n"
            "• In severe cases — loss of consciousness\n\n"
            "Immediate action (15-15 Rule):\n"
            "1. Take 15 grams of fast-acting sugar immediately:\n"
            "   • 4–5 glucose tablets, OR\n"
            "   • ½ cup (120 ml) of fruit juice or regular soft drink, OR\n"
            "   • 1 tablespoon of sugar or honey\n"
            "2. Wait 15 minutes and recheck blood sugar\n"
            "3. If still below 70 mg/dL — repeat step 1\n"
            "4. Once blood sugar is above 70 — eat a small snack\n\n"
            "⚠️ If the person is unconscious — CALL EMERGENCY SERVICES IMMEDIATELY.\n"
            "⚕️ Always carry glucose tablets or a sugary snack if you are on diabetes medication."
        ),
    },

    "high_sugar_emergency": {
        "keywords": ["high blood sugar", "hyperglycemia", "hyperglycaemia", "sugar high",
                     "blood sugar too high", "very high glucose", "high sugar emergency"],
        "title": "High Blood Sugar Emergency (Hyperglycaemia)",
        "response": (
            "Hyperglycaemia occurs when blood sugar rises above 180 mg/dL.\n"
            "Values above 300 mg/dL are dangerous and require urgent attention.\n\n"
            "Symptoms:\n"
            "• Frequent urination\n"
            "• Excessive thirst\n"
            "• Blurred vision\n"
            "• Headache\n"
            "• Fatigue and weakness\n"
            "• Nausea or vomiting\n"
            "• Fruity-smelling breath (sign of ketoacidosis — very serious)\n\n"
            "Immediate actions:\n"
            "• Drink plenty of water to help flush excess glucose\n"
            "• Avoid all sugary foods and drinks immediately\n"
            "• Light walking can help lower blood sugar\n"
            "• Check blood sugar every 1–2 hours\n"
            "• Take prescribed medication as directed by your doctor\n\n"
            "⚠️ Go to the emergency room if:\n"
            "• Blood sugar is above 300 mg/dL and not coming down\n"
            "• You have fruity breath, vomiting or confusion\n"
            "• You feel very unwell\n\n"
            "⚕️ Never adjust insulin or medication doses without doctor's guidance."
        ),
    },

    "prevention": {
        "keywords": ["prevent", "prevention", "avoid diabetes", "how to avoid diabetes",
                     "reduce risk", "stop diabetes", "diabetes prevention"],
        "title": "Diabetes Prevention",
        "response": (
            "Type 2 diabetes is largely preventable. Studies show that lifestyle "
            "changes reduce risk by 58%.\n\n"
            "Top prevention strategies:\n\n"
            "1. Maintain a healthy weight\n"
            "   • Losing just 5–7% of body weight significantly cuts diabetes risk\n\n"
            "2. Exercise regularly\n"
            "   • At least 150 minutes of moderate activity per week\n"
            "   • Even a daily 30-minute walk makes a major difference\n\n"
            "3. Eat a healthy diet\n"
            "   • Reduce sugar and refined carbs\n"
            "   • Increase fibre, vegetables and whole grains\n"
            "   • Avoid sugary drinks completely\n\n"
            "4. Don't smoke\n"
            "   • Smoking increases Type 2 diabetes risk by 30–40%\n\n"
            "5. Limit alcohol\n"
            "   • Excess alcohol disrupts blood sugar and causes weight gain\n\n"
            "6. Sleep well\n"
            "   • 7–8 hours per night — poor sleep raises blood sugar\n\n"
            "7. Manage stress\n"
            "   • Chronic stress raises cortisol which elevates blood sugar\n\n"
            "8. Get regular screening\n"
            "   • Especially if you have family history or other risk factors\n\n"
            "⚕️ Your doctor can assess your personal risk and guide prevention."
        ),
    },

    "bmi": {
        "keywords": ["bmi", "body mass index", "weight", "obesity", "overweight",
                     "underweight", "ideal weight", "healthy weight"],
        "title": "BMI and Diabetes Risk",
        "response": (
            "BMI (Body Mass Index) is calculated as weight (kg) ÷ height² (m²).\n\n"
            "BMI categories:\n"
            "• Underweight  : Below 18.5\n"
            "• Normal       : 18.5 – 24.9\n"
            "• Overweight   : 25.0 – 29.9\n"
            "• Obese        : 30.0 and above\n\n"
            "BMI and diabetes risk:\n"
            "• Every 1 unit increase in BMI above 25 raises Type 2 diabetes risk by ~8%\n"
            "• Abdominal (belly) fat is particularly dangerous — waist over 80 cm (women) "
            "or 90 cm (men) increases risk significantly\n"
            "• Losing even 5–10% of body weight improves insulin sensitivity greatly\n\n"
            "How to reach a healthy BMI:\n"
            "• Combine a calorie-controlled balanced diet with regular exercise\n"
            "• Reduce portion sizes — use smaller plates\n"
            "• Increase protein and fibre to feel full longer\n"
            "• Aim for 0.5–1 kg weight loss per week (sustainable pace)\n\n"
            "⚕️ Consult a doctor or dietitian for a safe personalised weight loss plan."
        ),
    },

    "insulin": {
        "keywords": ["insulin", "insulin resistance", "insulin sensitivity",
                     "what is insulin", "insulin injection", "insulin levels"],
        "title": "Insulin and Diabetes",
        "response": (
            "Insulin is a hormone produced by the pancreas that allows cells to "
            "absorb glucose from the blood for energy.\n\n"
            "How it works:\n"
            "• After eating, blood glucose rises\n"
            "• Pancreas releases insulin in response\n"
            "• Insulin unlocks cells to absorb glucose\n"
            "• Blood glucose returns to normal\n\n"
            "Insulin resistance:\n"
            "• Cells stop responding to insulin effectively\n"
            "• Pancreas produces more insulin to compensate\n"
            "• Eventually the pancreas gets exhausted — glucose stays high\n"
            "• This is the core mechanism of Type 2 diabetes\n\n"
            "HOMA-IR (measure of insulin resistance):\n"
            "• Normal    : Below 1.0\n"
            "• Borderline: 1.0 – 1.9\n"
            "• High      : 2.0 and above\n\n"
            "How to improve insulin sensitivity:\n"
            "• Regular exercise (most effective intervention)\n"
            "• Weight loss\n"
            "• Reducing refined carbs and sugar\n"
            "• Getting adequate sleep\n"
            "• Managing stress\n\n"
            "⚕️ Insulin therapy (injections) is prescribed by doctors only when necessary."
        ),
    },

    "stress": {
        "keywords": ["stress", "anxiety", "tension", "mental health", "stress and diabetes",
                     "cortisol", "depression", "emotional", "mental"],
        "title": "Stress and Blood Sugar",
        "response": (
            "Stress has a direct and significant impact on blood sugar levels.\n\n"
            "How stress raises blood sugar:\n"
            "• Stress triggers release of cortisol and adrenaline\n"
            "• These hormones tell the liver to release stored glucose\n"
            "• Blood sugar rises — even without eating\n"
            "• Chronic stress keeps blood sugar elevated for long periods\n\n"
            "Signs of stress-related blood sugar rise:\n"
            "• Blood sugar higher than usual without dietary changes\n"
            "• Fatigue despite normal eating\n"
            "• Difficulty sleeping\n"
            "• Increased cravings for sugary or fatty foods\n\n"
            "Effective stress management strategies:\n"
            "• Deep breathing — 5–10 minutes daily (proven to lower cortisol)\n"
            "• Meditation or mindfulness\n"
            "• Regular physical exercise\n"
            "• Yoga — combines physical activity with breathing\n"
            "• Adequate sleep (7–8 hours)\n"
            "• Social support — talking to family or friends\n"
            "• Limit caffeine and alcohol\n"
            "• Engage in hobbies you enjoy\n\n"
            "⚕️ If stress or anxiety is severe, please consult a mental health professional."
        ),
    },

    "water_intake": {
        "keywords": ["water", "hydration", "drink water", "water intake",
                     "how much water", "dehydration", "fluids"],
        "title": "Water Intake and Diabetes",
        "response": (
            "Staying well hydrated is especially important for people with diabetes.\n\n"
            "How water helps:\n"
            "• Helps kidneys flush excess glucose through urine\n"
            "• Prevents dehydration (high blood sugar draws water from cells)\n"
            "• Reduces hunger and prevents overeating\n"
            "• Helps maintain healthy blood pressure\n\n"
            "Recommended daily water intake:\n"
            "• Normal / Low risk  : 2.0 – 2.5 litres per day\n"
            "• Prediabetes        : 2.5 – 3.0 litres per day\n"
            "• High risk / Diabetic: 3.0+ litres per day\n"
            "• Increase intake when exercising or in hot weather\n\n"
            "Best drinks for diabetics:\n"
            "• Plain water — the best choice always\n"
            "• Unsweetened herbal tea or green tea\n"
            "• Black coffee (without sugar) — in moderation\n"
            "• Coconut water — occasionally (natural electrolytes)\n\n"
            "Drinks to avoid:\n"
            "• Soft drinks and sodas\n"
            "• Fruit juices (even 'natural')\n"
            "• Sweetened tea, coffee or milk drinks\n"
            "• Energy drinks\n"
            "• Alcohol\n\n"
            "⚕️ If you have kidney disease, consult your doctor about fluid intake."
        ),
    },

    "sleep": {
        "keywords": ["sleep", "rest", "insomnia", "sleep deprivation", "tired",
                     "sleeping", "sleep and diabetes", "night", "fatigue"],
        "title": "Sleep and Diabetes",
        "response": (
            "Sleep and blood sugar are deeply connected. Poor sleep is a "
            "significant and often overlooked diabetes risk factor.\n\n"
            "How poor sleep affects blood sugar:\n"
            "• Even one night of poor sleep increases insulin resistance\n"
            "• Sleep deprivation raises cortisol — which raises blood glucose\n"
            "• Poor sleep increases hunger hormones (ghrelin) causing cravings\n"
            "• Less than 6 hours/night raises Type 2 diabetes risk by 28%\n\n"
            "Recommended sleep:\n"
            "• Adults        : 7–8 hours per night\n"
            "• Diabetics     : Consistent sleep schedule is critical\n\n"
            "Tips for better sleep:\n"
            "• Sleep and wake at the same time every day\n"
            "• Avoid screens (phone, TV) for 1 hour before bed\n"
            "• Keep your bedroom cool, dark and quiet\n"
            "• Avoid heavy meals within 2 hours of bedtime\n"
            "• Avoid caffeine after 3 PM\n"
            "• Light exercise during the day improves sleep quality at night\n"
            "• Practice relaxation or deep breathing before sleep\n\n"
            "⚕️ If you have sleep apnoea, treatment greatly improves blood sugar control."
        ),
    },

    "foot_care": {
        "keywords": ["foot", "feet", "foot care", "diabetic foot", "foot pain",
                     "foot ulcer", "neuropathy", "feet numbness"],
        "title": "Foot Care for Diabetics",
        "response": (
            "Diabetes can damage nerves and blood vessels in the feet, making "
            "foot care a critical daily practice.\n\n"
            "Why foot care matters:\n"
            "• Diabetic neuropathy reduces sensation — injuries go unnoticed\n"
            "• Poor circulation slows healing — small wounds become serious\n"
            "• Infections can spread rapidly in diabetics\n"
            "• Severe cases can lead to amputation if untreated\n\n"
            "Daily foot care routine:\n"
            "• Inspect both feet every day — look for cuts, blisters, redness or swelling\n"
            "• Wash feet with warm (not hot) water and mild soap\n"
            "• Dry thoroughly — especially between toes\n"
            "• Apply moisturiser on the top and bottom (not between toes)\n"
            "• Trim toenails straight across — not too short\n"
            "• Never walk barefoot — indoors or outdoors\n"
            "• Wear well-fitting, comfortable footwear\n"
            "• Change socks daily — choose soft, breathable cotton\n\n"
            "See a doctor immediately if you notice:\n"
            "• Any wound that is not healing\n"
            "• Redness, warmth or swelling\n"
            "• Numbness or severe pain\n\n"
            "⚕️ Have your feet examined by a doctor at every diabetes check-up."
        ),
    },

    "pregnancy": {
        "keywords": ["pregnancy", "pregnant", "gestational diabetes", "diabetes in pregnancy",
                     "blood sugar pregnancy", "baby and diabetes"],
        "title": "Diabetes and Pregnancy",
        "response": (
            "Gestational diabetes (GDM) is diabetes that develops during pregnancy. "
            "It affects 2–10% of pregnancies.\n\n"
            "When it occurs:\n"
            "• Usually develops in the 2nd or 3rd trimester\n"
            "• Hormones from the placenta block insulin action\n"
            "• Blood sugar rises if the pancreas cannot compensate\n\n"
            "Who is at risk:\n"
            "• Overweight or obese\n"
            "• Family history of diabetes\n"
            "• Previous gestational diabetes\n"
            "• Age above 25\n"
            "• PCOS\n\n"
            "Risks if uncontrolled:\n"
            "• For baby — large birth weight, early birth, low blood sugar at birth\n"
            "• For mother — increased risk of Type 2 diabetes later in life\n\n"
            "Management:\n"
            "• Regular blood sugar monitoring\n"
            "• Dietary changes — reduce sugar and refined carbs\n"
            "• Safe exercise as recommended by your doctor\n"
            "• Insulin therapy if needed (safe during pregnancy)\n\n"
            "After delivery:\n"
            "• Blood sugar usually returns to normal\n"
            "• Test for Type 2 diabetes 6–12 weeks after delivery\n\n"
            "⚕️ All pregnant women should be screened for gestational diabetes. "
            "Consult your obstetrician and endocrinologist."
        ),
    },

    "blood_sugar_monitoring": {
        "keywords": ["monitor", "monitoring", "check sugar", "test blood sugar",
                     "glucometer", "blood sugar test", "how to check", "when to check"],
        "title": "Blood Sugar Monitoring",
        "response": (
            "Regular blood sugar monitoring helps you understand how food, "
            "exercise and medication affect your levels.\n\n"
            "Types of blood sugar tests:\n"
            "• Fasting Blood Sugar (FBS) — done after 8 hours of fasting\n"
            "• Post-Prandial Blood Sugar (PPBS) — done 2 hours after a meal\n"
            "• Random Blood Sugar — done any time\n"
            "• HbA1c — lab test showing 3-month average\n\n"
            "How often to check (at home glucometer):\n"
            "• High risk / Diabetic  : Daily — before breakfast and 2 hours after dinner\n"
            "• Prediabetes           : 2–3 times per week\n"
            "• Low risk              : Monthly as a preventive check\n\n"
            "Using a glucometer correctly:\n"
            "1. Wash and dry hands thoroughly\n"
            "2. Insert a test strip into the glucometer\n"
            "3. Prick the side of a fingertip with the lancet\n"
            "4. Touch the blood drop to the test strip\n"
            "5. Read the result in seconds\n"
            "6. Record the reading in a diary or app\n\n"
            "Target ranges:\n"
            "• Fasting         : 80 – 130 mg/dL\n"
            "• After meals     : Less than 180 mg/dL\n\n"
            "⚕️ Share your blood sugar log with your doctor at every visit."
        ),
    },
}

# ─── Fallback response ────────────────────────────────────────────────────────

FALLBACK = (
    "I'm sorry, I didn't quite understand your question. "
    "I can help you with these diabetes topics:\n\n"
    "• What is diabetes\n"
    "• Symptoms of diabetes\n"
    "• Normal blood sugar levels\n"
    "• HbA1c test\n"
    "• Diet advice for diabetes\n"
    "• Foods to avoid\n"
    "• Exercise recommendations\n"
    "• Causes and risk factors\n"
    "• Complications of diabetes\n"
    "• Low blood sugar emergency\n"
    "• High blood sugar emergency\n"
    "• Diabetes prevention\n"
    "• BMI and diabetes\n"
    "• Insulin and insulin resistance\n"
    "• Stress and blood sugar\n"
    "• Water intake\n"
    "• Sleep and diabetes\n"
    "• Foot care\n"
    "• Diabetes in pregnancy\n"
    "• Blood sugar monitoring\n\n"
    "Please try asking about one of these topics.\n"
    "⚕️ Always consult a qualified doctor for medical advice."
)

# ─── Topic detection ──────────────────────────────────────────────────────────

def detect_topic(user_message: str) -> str | None:
    """Returns the matched topic key or None if no match found."""
    msg = user_message.lower().strip()
    msg = re.sub(r"[^\w\s]", " ", msg)   # remove punctuation

    for topic_key, topic_data in TOPICS.items():
        for kw in topic_data["keywords"]:
            if kw in msg:
                return topic_key

    # Second pass — single keyword match (less strict)
    single_kw_map = {
        "diabetes": "what_is_diabetes",
        "sugar":    "normal_blood_sugar",
        "glucose":  "normal_blood_sugar",
        "diet":     "diet_advice",
        "eat":      "diet_advice",
        "food":     "diet_advice",
        "exercise": "exercise",
        "walk":     "exercise",
        "insulin":  "insulin",
        "bmi":      "bmi",
        "weight":   "bmi",
        "sleep":    "sleep",
        "stress":   "stress",
        "water":    "water_intake",
        "foot":     "foot_care",
        "prevent":  "prevention",
        "symptom":  "symptoms",
        "hba1c":    "hba1c",
        "a1c":      "hba1c",
        "pregnant": "pregnancy",
        "monitor":  "blood_sugar_monitoring",
    }
    for word, topic_key in single_kw_map.items():
        if word in msg.split():
            return topic_key

    return None


def get_response(user_message: str) -> dict:
    """
    Main chatbot function.
    Returns dict with topic, title and response text.
    """
    topic_key = detect_topic(user_message)

    if topic_key and topic_key in TOPICS:
        topic = TOPICS[topic_key]
        return {
            "topic":    topic_key,
            "title":    topic["title"],
            "response": topic["response"],
            "found":    True,
        }

    return {
        "topic":    "unknown",
        "title":    "Topic not found",
        "response": FALLBACK,
        "found":    False,
    }


# ─── Quick self-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_messages = [
        "What is diabetes?",
        "What are the symptoms?",
        "What should I eat?",
        "How much water should I drink?",
        "Tell me about HbA1c",
        "What is a random question about nothing",
    ]
    for msg in test_messages:
        r = get_response(msg)
        print(f"\n{'─'*50}")
        print(f"  User : {msg}")
        print(f"  Topic: {r['topic']}")
        print(f"  Title: {r['title']}")
        print(f"  Reply: {r['response'][:80]}...")