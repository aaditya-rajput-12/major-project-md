# 🏥 Medical Health Detection System
### Django + Python + HTML/CSS/JS

A complete medical health detection system where you can manage patients, upload reports,
get AI-powered treatment plans, 7-day diet plans, and auto-generated QR codes per report.

---

## 📁 Project Structure

```
medical_system/
├── medical_system/         ← Django project settings
│   ├── settings.py         ← ⚙️  All settings (DB, API keys, etc.)
│   └── urls.py             ← Main URL router
│
├── health_app/             ← Main application
│   ├── models.py           ← 📦 All database models
│   ├── views.py            ← 🔧 All page logic
│   ├── forms.py            ← 📝 Forms (Patient, Report)
│   ├── urls.py             ← 🔗 All URLs
│   ├── utils.py            ← 🛠️  QR generator + AI helper
│   ├── admin.py            ← 🔑 Admin panel config
│   │
│   └── templates/health_app/
│       ├── base.html           ← Layout + sidebar
│       ├── dashboard.html      ← Home dashboard
│       ├── patient_list.html   ← All patients
│       ├── patient_form.html   ← Add/Edit patient
│       ├── patient_detail.html ← Patient profile
│       ├── report_form.html    ← Add/Edit report
│       ├── report_detail.html  ← Report + Treatment + Diet + QR
│       └── confirm_delete.html ← Delete confirmation
│
├── media/                  ← Uploaded files (reports, QR codes)
├── db.sqlite3              ← Database (auto-created)
└── manage.py               ← Django CLI
```

---

## 🚀 How to Run

### 1. Install requirements
```bash
pip install django qrcode pillow
```

### 2. Run migrations
```bash
python manage.py migrate
```

### 3. Create admin user
```bash
python manage.py createsuperuser
```

### 4. Start server
```bash
python manage.py runserver
```

### 5. Open browser
```
http://127.0.0.1:8000/
```

---

## 🤖 Enable AI Treatment Generation

Set your Anthropic API key as an environment variable:

**Windows:**
```cmd
set ANTHROPIC_API_KEY=your_key_here
python manage.py runserver
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY=your_key_here
python manage.py runserver
```

Without the key, the system uses a built-in default template.
Get key from: https://console.anthropic.com

---

## 🔑 Admin Panel
```
URL:      http://127.0.0.1:8000/admin/
Username: admin
Password: admin123
```

---

## ✏️ How to Customize

### Change colors (CSS variables in base.html):
```css
:root {
    --primary:  #0f4c81;   ← Main blue color
    --accent:   #00b894;   ← Green buttons
    --danger:   #d63031;   ← Red/delete buttons
    --bg:       #f0f4f8;   ← Page background
}
```

### Add a new field to Patient:
1. Open `health_app/models.py`
2. Add field to `Patient` class
3. Open `health_app/forms.py`, add to `PatientForm.Meta.fields`
4. Run: `python manage.py makemigrations && python manage.py migrate`

### Add a new report type:
1. Open `health_app/models.py`
2. Add to `MedicalReport.REPORT_TYPE_CHOICES`
3. Run migrations

### Change AI model or prompt:
1. Open `health_app/utils.py`
2. Edit `get_ai_treatment()` function

---

## 📊 Features

| Feature              | Description                                      |
|----------------------|--------------------------------------------------|
| Patient Management   | Add, edit, delete patients with full info        |
| Medical Reports      | Upload reports (PDF/images), detect conditions   |
| AI Treatment Plans   | Auto-generated via Claude AI                     |
| 7-Day Diet Plan      | Personalized diet based on condition             |
| QR Code per Report   | Every report gets a unique scannable QR code     |
| Severity Levels      | Low / Medium / High / Critical                   |
| Admin Panel          | Full Django admin for power users                |

