"""
Views for Medical Health Detection System
==========================================
- dashboard         : home page with stats
- patient_list      : all patients
- patient_add       : add new patient
- patient_detail    : one patient's profile + all reports
- report_add        : add new report for patient
- report_detail     : view report + treatment + diet + QR
- report_analyze    : trigger AI analysis
- report_delete     : delete a report
- patient_delete    : delete a patient
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Patient, MedicalReport, TreatmentPlan, DietPlan, DietDay, ReportQRCode
from .forms import PatientForm, MedicalReportForm
from .utils import generate_qr_code, get_ai_treatment, detect_disease_from_text


# ─── DASHBOARD ──────────────────────────────────────────────────
def dashboard(request):
    """Home dashboard with quick stats."""
    context = {
        'total_patients':  Patient.objects.count(),
        'total_reports':   MedicalReport.objects.count(),
        'pending_reports': MedicalReport.objects.filter(status='pending').count(),
        'analyzed':        MedicalReport.objects.filter(status='analyzed').count(),
        'recent_reports':  MedicalReport.objects.select_related('patient').order_by('-created_at')[:5],
        'recent_patients': Patient.objects.order_by('-created_at')[:5],
    }
    return render(request, 'health_app/dashboard.html', context)


# ─── PATIENT VIEWS ──────────────────────────────────────────────
def patient_list(request):
    """List all patients with search."""
    query = request.GET.get('q', '')
    patients = Patient.objects.all()
    if query:
        patients = patients.filter(name__icontains=query)
    return render(request, 'health_app/patient_list.html', {
        'patients': patients,
        'query': query
    })


def patient_add(request):
    """Add a new patient."""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Patient '{patient.name}' added successfully!")
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm()
    return render(request, 'health_app/patient_form.html', {'form': form, 'title': 'Add New Patient'})


def patient_edit(request, pk):
    """Edit existing patient."""
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient updated!")
            return redirect('patient_detail', pk=pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'health_app/patient_form.html', {'form': form, 'title': 'Edit Patient', 'patient': patient})


def patient_detail(request, pk):
    """Patient profile with all reports."""
    patient = get_object_or_404(Patient, pk=pk)
    reports = patient.reports.all().order_by('-report_date')
    return render(request, 'health_app/patient_detail.html', {
        'patient': patient,
        'reports': reports,
    })


def patient_delete(request, pk):
    """Delete a patient (and all their reports)."""
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        name = patient.name
        patient.delete()
        messages.success(request, f"Patient '{name}' deleted.")
        return redirect('patient_list')
    return render(request, 'health_app/confirm_delete.html', {'object': patient, 'type': 'Patient'})


# ─── REPORT VIEWS ───────────────────────────────────────────────
def report_add(request, patient_pk):
    """Add a new medical report for a patient."""
    patient = get_object_or_404(Patient, pk=patient_pk)
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.patient = patient
            report.detected_condition = detect_disease_from_text(report.symptoms or '')
            report.save()
            # Auto-generate QR code for this report
            try:
                generate_qr_code(report)
            except Exception as e:
                messages.warning(request, f"Report saved but QR generation failed: {e}")
            messages.success(request, "Report added! Click 'Analyze with AI' to generate treatment plan.")
            return redirect('report_detail', report_id=report.report_id)
    else:
        form = MedicalReportForm(initial={'report_date': timezone.now().date()})
    return render(request, 'health_app/report_form.html', {
        'form': form,
        'patient': patient,
        'title': 'Add Medical Report'
    })


def report_detail(request, report_id):
    """View a single report with treatment plan, diet, and QR code."""
    report = get_object_or_404(MedicalReport, report_id=report_id)
    treatment = getattr(report, 'treatment', None)
    diet_plan = getattr(report, 'diet_plan', None)
    qr_code = getattr(report, 'qr_code', None)
    diet_days = diet_plan.days.all() if diet_plan else []
    return render(request, 'health_app/report_detail.html', {
        'report': report,
        'treatment': treatment,
        'diet_plan': diet_plan,
        'diet_days': diet_days,
        'qr_code': qr_code,
    })


def report_analyze(request, report_id):
    """Trigger AI analysis for a report (POST only)."""
    report = get_object_or_404(MedicalReport, report_id=report_id)
    if request.method == 'POST':
        try:
            ai_data = get_ai_treatment(report)

            # Save Treatment Plan
            TreatmentPlan.objects.filter(report=report).delete()
            t = ai_data.get('treatment', {})
            TreatmentPlan.objects.create(
                report=report,
                medications=t.get('medications', ''),
                lifestyle_changes=t.get('lifestyle_changes', ''),
                exercises=t.get('exercises', ''),
                precautions=t.get('precautions', ''),
                avoid_foods=t.get('avoid_foods', ''),
                avoid_activities=t.get('avoid_activities', ''),
                recommended_foods=t.get('recommended_foods', ''),
                followup_in_days=t.get('followup_in_days', 7),
                additional_notes=t.get('additional_notes', ''),
                generated_by_ai=True
            )

            # Save Diet Plan
            DietPlan.objects.filter(report=report).delete()
            d = ai_data.get('diet', {})
            diet_plan = DietPlan.objects.create(
                report=report,
                title=d.get('title', '7-Day Diet Plan'),
                description=d.get('description', '')
            )
            for day_data in d.get('days', []):
                DietDay.objects.create(
                    diet_plan=diet_plan,
                    day_number=day_data.get('day_number', 1),
                    breakfast=day_data.get('breakfast', ''),
                    mid_morning=day_data.get('mid_morning', ''),
                    lunch=day_data.get('lunch', ''),
                    evening=day_data.get('evening', ''),
                    dinner=day_data.get('dinner', ''),
                    water_intake=day_data.get('water_intake', '8-10 glasses'),
                    notes=day_data.get('notes', '')
                )

            # Regenerate QR
            generate_qr_code(report)

            # Update status
            report.status = 'analyzed'
            report.save()

            messages.success(request, "AI Analysis complete! Treatment plan and diet plan generated.")
        except Exception as e:
            messages.error(request, f"Analysis failed: {str(e)}")

    return redirect('report_detail', report_id=report_id)


def report_edit(request, report_id):
    """Edit a medical report."""
    report = get_object_or_404(MedicalReport, report_id=report_id)
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            updated_report = form.save(commit=False)
            # Re-run disease detection whenever symptoms are updated
            updated_report.detected_condition = detect_disease_from_text(
                updated_report.symptoms or ''
            )
            updated_report.save()
            messages.success(request, "Report updated!")
            return redirect('report_detail', report_id=report_id)
    else:
        form = MedicalReportForm(instance=report)
    return render(request, 'health_app/report_form.html', {
        'form': form,
        'patient': report.patient,
        'title': 'Edit Report'
    })


def report_delete(request, report_id):
    """Delete a report."""
    report = get_object_or_404(MedicalReport, report_id=report_id)
    patient_pk = report.patient.pk
    if request.method == 'POST':
        report.delete()
        messages.success(request, "Report deleted.")
        return redirect('patient_detail', pk=patient_pk)
    return render(request, 'health_app/confirm_delete.html', {'object': report, 'type': 'Report'})
