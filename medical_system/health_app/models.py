"""
Models for Medical Health Detection System
==========================================
Patient -> MedicalReport -> TreatmentPlan
                         -> DietPlan -> DietDay (7 days)
                         -> ReportQRCode
"""

from django.db import models
import uuid


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    name       = models.CharField(max_length=200)
    age        = models.PositiveIntegerField()
    gender     = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone      = models.CharField(max_length=15, blank=True, null=True)
    email      = models.EmailField(blank=True, null=True)
    address    = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (Age: {self.age})"


class MedicalReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('blood', 'Blood Test'), ('urine', 'Urine Test'), ('xray', 'X-Ray'),
        ('mri', 'MRI Scan'), ('ultrasound', 'Ultrasound'),
        ('ecg', 'ECG'), ('general', 'General Checkup'), ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('analyzed', 'Analyzed'),
        ('reviewed', 'Doctor Reviewed'),
    ]
    SEVERITY_CHOICES = [
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')
    ]

    patient            = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reports')
    report_id          = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    report_type        = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='general')
    report_date        = models.DateField()
    report_file        = models.FileField(upload_to='reports/', blank=True, null=True)
    detected_condition = models.CharField(max_length=300, blank=True)
    symptoms           = models.TextField(blank=True)
    severity           = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='low')
    doctor_notes       = models.TextField(blank=True)
    status             = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date']

    def __str__(self):
        return f"[{self.report_type.upper()}] {self.patient.name} - {self.report_date}"


class TreatmentPlan(models.Model):
    report             = models.OneToOneField(MedicalReport, on_delete=models.CASCADE, related_name='treatment')
    medications        = models.TextField(blank=True)
    lifestyle_changes  = models.TextField(blank=True)
    exercises          = models.TextField(blank=True)
    precautions        = models.TextField(blank=True)
    avoid_foods        = models.TextField(blank=True)
    avoid_activities   = models.TextField(blank=True)
    recommended_foods  = models.TextField(blank=True)
    followup_in_days   = models.PositiveIntegerField(default=7)
    additional_notes   = models.TextField(blank=True)
    generated_by_ai    = models.BooleanField(default=True)
    created_at         = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Treatment for {self.report.patient.name}"


class DietPlan(models.Model):
    report      = models.OneToOneField(MedicalReport, on_delete=models.CASCADE, related_name='diet_plan')
    title       = models.CharField(max_length=200, default="7-Day Personalized Diet Plan")
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diet Plan - {self.report.patient.name}"


class DietDay(models.Model):
    DAY_CHOICES = [(i, f'Day {i}') for i in range(1, 8)]

    diet_plan   = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='days')
    day_number  = models.IntegerField(choices=DAY_CHOICES)
    breakfast   = models.TextField()
    mid_morning = models.TextField(blank=True)
    lunch       = models.TextField()
    evening     = models.TextField(blank=True)
    dinner      = models.TextField()
    water_intake= models.CharField(max_length=50, default="8-10 glasses")
    notes       = models.TextField(blank=True)

    class Meta:
        ordering = ['day_number']
        unique_together = ['diet_plan', 'day_number']

    def __str__(self):
        return f"Day {self.day_number} - {self.diet_plan.report.patient.name}"


class ReportQRCode(models.Model):
    report     = models.OneToOneField(MedicalReport, on_delete=models.CASCADE, related_name='qr_code')
    qr_image   = models.ImageField(upload_to='qrcodes/')
    qr_data    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR - {self.report.patient.name}"
