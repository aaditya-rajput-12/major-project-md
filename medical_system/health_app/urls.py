"""
URL Configuration for health_app
=================================
All URL patterns for the medical system.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Patient URLs
    path('patients/',               views.patient_list,   name='patient_list'),
    path('patients/add/',           views.patient_add,    name='patient_add'),
    path('patients/<int:pk>/',      views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit,   name='patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),

    # Report URLs
    path('patients/<int:patient_pk>/reports/add/', views.report_add, name='report_add'),
    path('report/<uuid:report_id>/',               views.report_detail,  name='report_detail'),
    path('report/<uuid:report_id>/edit/',          views.report_edit,    name='report_edit'),
    path('report/<uuid:report_id>/analyze/',       views.report_analyze, name='report_analyze'),
    path('report/<uuid:report_id>/delete/',        views.report_delete,  name='report_delete'),
]
