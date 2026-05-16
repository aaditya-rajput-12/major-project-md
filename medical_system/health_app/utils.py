"""
Utility functions for Medical Health Detection System
=====================================================
- generate_qr_code()      : creates QR image for a report
- get_ai_treatment()      : calls Claude API for treatment suggestions
- parse_ai_response()     : parses AI JSON response into model fields
"""

import qrcode
import io
import json
import os
import urllib.request
import urllib.error
from django.core.files.base import ContentFile
from django.conf import settings


# ─── QR CODE GENERATOR ──────────────────────────────────────────
def generate_qr_code(report, base_url="http://127.0.0.1:8000"):
    """
    Generate a QR code image for a medical report.
    The QR encodes the URL to view that report.
    Returns a ReportQRCode instance (saved).
    """
    from .models import ReportQRCode

    # Build the URL that QR will encode
    qr_url = f"{base_url}/report/{report.report_id}/"

    # Create QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1a3a5c", back_color="white")

    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Delete old QR if exists
    ReportQRCode.objects.filter(report=report).delete()

    # Save new QR
    qr_obj = ReportQRCode(report=report, qr_data=qr_url)
    filename = f"qr_{report.report_id}.png"
    qr_obj.qr_image.save(filename, ContentFile(buffer.read()), save=True)

    return qr_obj


# ─── AI TREATMENT GENERATOR ─────────────────────────────────────
def get_ai_treatment(report):
    """
    Call Claude API to generate treatment plan + diet plan.
    Returns a dict with keys: treatment, diet
    Falls back to a default template if API key is missing.
    """
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')

    if not api_key:
        # Return default template if no API key set
        return _default_treatment_template(report)

    prompt = f"""
You are a medical AI assistant. Based on the following patient report, generate:
1. A detailed treatment plan
2. A 7-day diet plan where EACH DAY has COMPLETELY DIFFERENT meals (different breakfast, lunch, and dinner every day — no repetition across days)

Patient Information:
- Name: {report.patient.name}
- Age: {report.patient.age}
- Gender: {report.patient.get_gender_display()}
- Condition: {report.detected_condition}
- Symptoms: {report.symptoms}
- Report Type: {report.get_report_type_display()}
- Severity: {report.get_severity_display()}
- Doctor Notes: {report.doctor_notes}

IMPORTANT DIET RULES:
- Every day must have a unique breakfast, lunch, and dinner.
- Vary protein sources, grains, and vegetables across days.
- Tailor all meals specifically for someone with {report.detected_condition}.
- Include day-specific notes explaining why those foods help the condition.

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{{
  "treatment": {{
    "medications": "list medicines here",
    "lifestyle_changes": "list lifestyle changes",
    "exercises": "recommended exercises",
    "precautions": "important precautions",
    "avoid_foods": "foods to strictly avoid",
    "avoid_activities": "activities to avoid",
    "recommended_foods": "foods that help recovery",
    "followup_in_days": 7,
    "additional_notes": "any extra important notes"
  }},
  "diet": {{
    "title": "7-Day Diet Plan for {report.detected_condition}",
    "description": "brief description tailored to the condition",
    "days": [
      {{
        "day_number": 1,
        "breakfast": "UNIQUE breakfast for day 1",
        "mid_morning": "snack",
        "lunch": "UNIQUE lunch for day 1",
        "evening": "evening snack",
        "dinner": "UNIQUE dinner for day 1",
        "water_intake": "amount",
        "notes": "why these specific foods help {report.detected_condition} today"
      }}
    ]
  }}
}}
Include all 7 days. Every day must have different meals. Be specific and medically appropriate for {report.detected_condition}.
"""

    try:
        import json as json_lib
        payload = json_lib.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 3000,
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json_lib.loads(response.read().decode('utf-8'))
            text = data['content'][0]['text']
            # Strip markdown code fences if present
            text = text.strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1].rsplit('```', 1)[0]
            return json_lib.loads(text)

    except Exception as e:
        print(f"AI API Error: {e}")
        return _default_treatment_template(report)


def _default_treatment_template(report):
    """Fallback treatment template when API is not configured."""
    condition = report.detected_condition or "the detected condition"

    # 7 fully unique days — different breakfast, lunch, dinner every day
    unique_days = [
        {
            "day_number": 1,
            "breakfast": "Oatmeal porridge with sliced banana + warm lemon water",
            "mid_morning": "A handful of soaked almonds (5-6) + 1 glass water",
            "lunch": "Brown rice + moong dal + steamed broccoli + cucumber salad",
            "evening": "Herbal green tea + 2 whole wheat crackers",
            "dinner": "Vegetable khichdi (rice + lentils + vegetables) + buttermilk",
            "water_intake": "8-10 glasses",
            "notes": "Day 1: Start light. Focus on hydration and rest."
        },
        {
            "day_number": 2,
            "breakfast": "2 whole wheat rotis + low-fat paneer bhurji + 1 glass warm milk",
            "mid_morning": "1 medium apple or pear",
            "lunch": "Multigrain roti (2) + palak dal + mixed vegetable sabzi + salad",
            "evening": "Coconut water + roasted chana (small bowl)",
            "dinner": "Vegetable daliya (broken wheat) + low-fat curd",
            "water_intake": "8-10 glasses",
            "notes": "Day 2: Increase fibre intake. Avoid skipping meals."
        },
        {
            "day_number": 3,
            "breakfast": "Poha (beaten rice) with vegetables + 1 glass buttermilk",
            "mid_morning": "Seasonal fruit salad (papaya / guava / watermelon)",
            "lunch": "Brown rice + rajma (kidney beans) + steamed carrots + salad",
            "evening": "Herbal tulsi-ginger tea + handful of walnuts",
            "dinner": "2 jowar rotis + lauki (bottle gourd) sabzi + low-fat curd",
            "water_intake": "8-10 glasses",
            "notes": "Day 3: Focus on antioxidant-rich foods today."
        },
        {
            "day_number": 4,
            "breakfast": "Idli (3) + sambar + mint chutney + warm water",
            "mid_morning": "Pomegranate seeds or 1 orange",
            "lunch": "Quinoa or brown rice + chana dal + bhindi sabzi + tomato-onion salad",
            "evening": "Chamomile tea + 2 dates",
            "dinner": "Moong dal soup + 2 whole wheat rotis + stir-fried spinach",
            "water_intake": "8-10 glasses",
            "notes": "Day 4: Include probiotic-rich foods like curd to support gut health."
        },
        {
            "day_number": 5,
            "breakfast": "Vegetable upma + 1 boiled egg (optional) + 1 glass coconut water",
            "mid_morning": "Mixed nuts (almonds, cashews, pistachios) — small handful",
            "lunch": "Millet roti (2) + toor dal + baingan sabzi + cucumber raita",
            "evening": "Lemon ginger tea + roasted makhana (fox nuts)",
            "dinner": "Pumpkin soup + 2 multigrain rotis + sautéed vegetables",
            "water_intake": "8-10 glasses",
            "notes": "Day 5: Millets provide extra minerals and slow-release energy."
        },
        {
            "day_number": 6,
            "breakfast": "Besan chilla (2) with tomato-coriander chutney + 1 glass warm milk",
            "mid_morning": "1 bowl of mixed fresh fruits",
            "lunch": "Brown rice + masoor dal + methi sabzi + carrot-beet salad",
            "evening": "Turmeric milk (haldi doodh) + 1 banana",
            "dinner": "Vegetable daliya khichdi + low-fat curd + steamed beans",
            "water_intake": "8-10 glasses",
            "notes": "Day 6: Turmeric has anti-inflammatory benefits — include it in cooking."
        },
        {
            "day_number": 7,
            "breakfast": "Sprouts salad + 1 glass fresh orange juice (no sugar)",
            "mid_morning": "Seasonal fruit + 4-5 soaked walnuts",
            "lunch": "Brown rice + sambar + mixed vegetable curry + salad",
            "evening": "Herbal tea + 2 whole wheat biscuits",
            "dinner": "Light vegetable soup + 2 jowar rotis + stir-fried cabbage-carrot",
            "water_intake": "8-10 glasses",
            "notes": "Day 7: Reflect on the week. Continue healthy habits into next week."
        },
    ]

    return {
        "treatment": {
            "medications": f"Consult your doctor for medications specific to {condition}.",
            "lifestyle_changes": "Maintain a regular sleep schedule (7-8 hrs). Reduce stress with meditation. Stay well hydrated throughout the day.",
            "exercises": "Light walking 30 minutes daily. Yoga or gentle stretching in the morning. Avoid strenuous activity until reviewed by doctor.",
            "precautions": "Monitor symptoms daily. Avoid self-medication. Follow doctor advice strictly. Attend scheduled follow-up.",
            "avoid_foods": "Processed/packaged foods, excess sugar and sweets, fried foods, alcohol, tobacco/smoking, excess salt.",
            "avoid_activities": "Heavy lifting, intense workouts, staying up past midnight, excessive screen time.",
            "recommended_foods": "Fresh fruits, leafy green vegetables, whole grains (brown rice, millets), lentils, low-fat dairy, plenty of water.",
            "followup_in_days": 7,
            "additional_notes": "Please consult with your healthcare provider for personalized medical advice. This plan is a general wellness guide only."
        },
        "diet": {
            "title": f"7-Day Personalized Diet Plan for {condition}",
            "description": (
                f"A structured 7-day diet plan tailored for {condition}. "
                "Every day features a different, balanced menu to ensure variety, "
                "complete nutrition, and sustained motivation."
            ),
            "days": unique_days
        }
    }


def detect_disease_from_text(symptoms):
    """
    Detect likely disease from symptoms text.
    Returns the best matching disease name or 'General Illness'.
    """
    text = symptoms.lower()

    disease_map = {
        # Metabolic / Endocrine
        'Diabetes (Type 2)': [
            'sugar', 'glucose', 'frequent urination', 'diabetes', 'hba1c',
            'polydipsia', 'polyuria', 'insulin', 'fasting glucose', 'blood sugar high',
            'excessive thirst', 'blurred vision', 'slow healing wound',
        ],
        'Hypothyroidism': [
            'tsh', 'thyroid', 'weight gain', 'fatigue', 'hypothyroid',
            'cold intolerance', 'constipation', 'dry skin', 'hair loss', 't3', 't4',
        ],
        'Hyperthyroidism': [
            'hyperthyroid', 'weight loss', 'rapid heartbeat', 'tremors',
            'sweating', 'anxiety', 'heat intolerance', 'goiter',
        ],
        'Obesity': [
            'obese', 'obesity', 'bmi high', 'overweight', 'body mass index',
        ],

        # Cardiovascular
        'Hypertension': [
            'high bp', 'hypertension', 'high blood pressure', 'systolic',
            'diastolic', 'bp 140', 'bp 150', 'bp 160', 'headache', 'dizziness',
        ],
        'Heart Disease': [
            'chest pain', 'ecg', 'angina', 'coronary', 'cardiac', 'heart attack',
            'myocardial', 'palpitations', 'shortness of breath on exertion',
            'cholesterol', 'triglycerides',
        ],
        'Anemia': [
            'anemia', 'weakness', 'hemoglobin', 'hgb low', 'iron', 'pale',
            'pallor', 'fatigue', 'low rbc', 'ferritin', 'breathlessness',
        ],

        # Respiratory
        'Asthma': [
            'asthma', 'wheezing', 'breathlessness', 'inhaler', 'bronchospasm',
            'coughing at night', 'chest tightness',
        ],
        'Tuberculosis (TB)': [
            'tb', 'tuberculosis', 'night sweats', 'blood in sputum',
            'chronic cough', 'afb', 'sputum positive',
        ],
        'Pneumonia': [
            'pneumonia', 'lung infection', 'chest x-ray', 'consolidation',
            'productive cough', 'high fever cough',
        ],
        'COPD': [
            'copd', 'chronic obstructive', 'emphysema', 'chronic bronchitis',
            'smoking', 'persistent cough', 'mucus',
        ],

        # Gastrointestinal
        'Gastritis / GERD': [
            'gastritis', 'acid reflux', 'gerd', 'heartburn', 'acidity',
            'stomach pain', 'nausea', 'vomiting', 'epigastric', 'indigestion',
        ],
        'Irritable Bowel Syndrome': [
            'ibs', 'irritable bowel', 'bloating', 'abdominal cramps',
            'diarrhea', 'constipation alternating',
        ],
        'Liver Disease': [
            'liver', 'jaundice', 'hepatitis', 'sgpt', 'sgot', 'bilirubin',
            'cirrhosis', 'fatty liver', 'yellow eyes', 'yellow skin',
        ],
        'Kidney Disease': [
            'kidney', 'renal', 'creatinine', 'urea', 'dialysis', 'ckd',
            'nephrotic', 'nephritis', 'edema feet', 'protein in urine',
        ],

        # Infectious
        'Dengue Fever': [
            'dengue', 'platelet low', 'thrombocytopenia', 'rash', 'joint pain',
            'high fever sudden', 'retro-orbital pain',
        ],
        'Malaria': [
            'malaria', 'chills', 'plasmodium', 'cyclic fever', 'antimalarial',
            'mosquito bite', 'splenomegaly',
        ],
        'Typhoid': [
            'typhoid', 'enteric fever', 'widal', 'rose spots', 'abdominal pain fever',
            'salmonella',
        ],
        'COVID-19': [
            'covid', 'coronavirus', 'loss of taste', 'loss of smell', 'sars-cov',
            'rt-pcr positive', 'oxygen low', 'covid positive',
        ],
        'Viral Fever': [
            'viral fever', 'flu', 'influenza', 'fever cold', 'body ache fever',
            'runny nose', 'sore throat', 'temperature high',
        ],
        'Urinary Tract Infection': [
            'uti', 'urinary tract', 'burning urination', 'dysuria', 'frequent urination',
            'urine culture', 'e coli urine',
        ],

        # Neurological / Mental Health
        'Migraine': [
            'migraine', 'severe headache', 'throbbing headache', 'light sensitivity',
            'nausea headache', 'one sided headache',
        ],
        'Depression / Anxiety': [
            'depression', 'anxiety', 'stress', 'insomnia', 'sleep disorder',
            'mood swings', 'panic attack', 'mental health',
        ],

        # Musculoskeletal
        'Arthritis': [
            'arthritis', 'joint pain', 'rheumatoid', 'osteoarthritis', 'gout',
            'swollen joints', 'stiffness',
        ],
        'Osteoporosis': [
            'osteoporosis', 'bone density', 'fracture risk', 'calcium deficiency',
            'dexa', 'low bone mass',
        ],

        # Skin
        'Dermatitis / Eczema': [
            'eczema', 'dermatitis', 'itching', 'skin rash', 'dry itchy skin',
            'allergy rash',
        ],
        'Psoriasis': [
            'psoriasis', 'scaly skin', 'plaque skin', 'silver scales',
        ],
    }

    # Score each disease by how many keywords match
    scores = {}
    for disease, keywords in disease_map.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[disease] = score

    if scores:
        # Return the disease with the highest keyword match score
        return max(scores, key=scores.get)

    return 'General Illness'
