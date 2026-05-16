from django.contrib import admin
from .models import Patient, MedicalReport, TreatmentPlan, DietPlan, DietDay, ReportQRCode

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'gender', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']

@admin.register(MedicalReport)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['patient', 'report_type', 'report_date', 'detected_condition', 'severity', 'status']
    list_filter = ['report_type', 'severity', 'status']
    search_fields = ['patient__name', 'detected_condition']

@admin.register(TreatmentPlan)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['report', 'followup_in_days', 'generated_by_ai', 'created_at']

class DietDayInline(admin.TabularInline):
    model = DietDay
    extra = 0

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['report', 'title', 'created_at']
    inlines = [DietDayInline]

@admin.register(ReportQRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['report', 'created_at']
