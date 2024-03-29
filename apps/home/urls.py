# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path, include
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('appointments',        views.show_table, {'page_type': 'APPOINTMENTS'},    name='appointments'),
    path('hospitals',           views.show_table, {'page_type': 'HOSPITALS'},       name='hospitals'),
    path('healthcare-services', views.show_table, {'page_type': 'HEALTHCARE_SERVICES'},   name='healthcare-services'),
    path('practitioners',       views.show_table, {'page_type': 'PRACTITIONERS'},   name='practitioners'),
    path('patients',            views.show_table, {'page_type': 'PATIENTS'},        name='patients'),
    path('observations',        views.show_table, {'page_type': 'OBSERVATIONS'},      name='observations'),
    path('reports/<int:report_no>/',    views.show_report,          name='reports'),
    path('smart-app-register/',         views.register_smart_app,   name='register_smart_app'),
    path('launch-smart-app/',           views.launch_smart_app,     name='launch-smart-app'),

    # Add row
    path('add-appointment',     views.add_edit_appointment,  name='add-appointment'),
    # load appointments from Synthea generated Patient JSON file
    path('load-appointments',   views.load_appointments,  name='load-appointments'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
