"""
Forms for Medical Health Detection System
==========================================
PatientForm      : Add/Edit patient
MedicalReportForm: Add/Edit report
"""

from django import forms
from .models import Patient, MedicalReport


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'phone', 'email', 'address']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full name'}),
            'age':     forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Age'}),
            'gender':  forms.Select(attrs={'class': 'form-input'}),
            'phone':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
            'email':   forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Address'}),
        }


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = [
            'report_type', 'report_date', 'report_file',
            'detected_condition', 'symptoms', 'severity',
            'doctor_notes', 'status'
        ]
        widgets = {
            'report_type':        forms.Select(attrs={'class': 'form-input'}),
            'report_date':        forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'report_file':        forms.FileInput(attrs={'class': 'form-input'}),
            'detected_condition': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Type 2 Diabetes'}),
            'symptoms':           forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'List symptoms...'}),
            'severity':           forms.Select(attrs={'class': 'form-input'}),
            'doctor_notes':       forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': "Doctor's notes..."}),
            'status':             forms.Select(attrs={'class': 'form-input'}),
        }
